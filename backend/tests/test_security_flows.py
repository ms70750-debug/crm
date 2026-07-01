from time import time_ns

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.database.init_db import init_db
from app.database.session import SessionLocal
from app.main import app
from app.models import AuditLog, Client


client = TestClient(app)


def _token() -> str:
    init_db()
    response = client.post("/auth/login", json={"email": "admin@bbbconsig.demo", "password": "BbbConsig@2026"})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_login_rejects_invalid_password() -> None:
    init_db()
    response = client.post("/auth/login", json={"email": "admin@bbbconsig.demo", "password": "senha-errada"})
    assert response.status_code == 401


def test_client_consent_whatsapp_simulation_and_soft_delete_flow() -> None:
    token = _token()
    suffix = str(time_ns())[-9:]
    cpf = f"39{suffix}"
    phone = f"1198{suffix}00"
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/clientes",
        headers=headers,
        json={
            "nome": f"Cliente Ficticio {suffix}",
            "cpf": cpf,
            "telefone": phone,
            "email": f"cliente{suffix}@demo.local",
            "convenio": "INSS",
        },
    )
    assert created.status_code == 201
    body = created.json()
    assert body["cpf"].startswith("***.***.")
    assert phone not in body["telefone"]

    blocked = client.post(
        "/whatsapp/simular-envio",
        json={"destinatario_tipo": "cliente", "destinatario_id": body["id"], "modelo": "primeiro_contato", "mensagem": "Mensagem ficticia."},
    )
    assert blocked.status_code == 403

    consent = client.post("/consents", headers=headers, json={"customer_id": body["id"], "channel": "whatsapp", "source": "pytest"})
    assert consent.status_code == 201
    assert consent.json()["granted"] is True

    sent = client.post(
        "/whatsapp/simular-envio",
        json={"destinatario_tipo": "cliente", "destinatario_id": body["id"], "modelo": "primeiro_contato", "mensagem": "Mensagem ficticia."},
    )
    assert sent.status_code == 201
    assert sent.json()["status"] == "Registrada em simulacao"

    simulation = client.get(f"/consultas/inss/{cpf}")
    assert simulation.status_code == 200
    assert "snapshot" in simulation.json()
    assert "regra_aplicada" in simulation.json()

    deleted = client.delete(f"/clientes/{body['id']}", headers=headers)
    assert deleted.status_code == 200

    listed = client.get("/clientes")
    assert all(item["id"] != body["id"] for item in listed.json())

    with SessionLocal() as db:
      stored = db.get(Client, body["id"])
      assert stored is not None
      assert stored.deleted_at is not None
      audit = db.scalar(select(AuditLog).where(AuditLog.action == "whatsapp_simulation_created").order_by(AuditLog.id.desc()))
      assert audit is not None
      assert cpf not in (audit.metadata_json or "")
