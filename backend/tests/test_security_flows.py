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


def _login(email: str, password: str) -> dict:
    init_db()
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()


def test_login_rejects_invalid_password() -> None:
    init_db()
    response = client.post("/auth/login", json={"email": "admin@bbbconsig.demo", "password": "senha-errada"})
    assert response.status_code == 401


def test_auth_me_and_route_protection() -> None:
    login = _login("admin@bbbconsig.demo", "BbbConsig@2026")
    assert "password" not in str(login).lower()
    assert "hash" not in str(login).lower()
    headers = {"Authorization": f"Bearer {login['access_token']}"}

    me = client.get("/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["role"] == "admin"
    assert "password_hash" not in me.text

    blocked = client.get("/dashboard/resumo")
    assert blocked.status_code == 401

    dashboard = client.get("/dashboard/resumo", headers=headers)
    assert dashboard.status_code == 200
    assert "cards" in dashboard.json()


def test_partner_permissions_are_limited() -> None:
    admin = _login("admin@bbbconsig.demo", "BbbConsig@2026")
    admin_headers = {"Authorization": f"Bearer {admin['access_token']}"}
    suffix = str(time_ns())[-9:]
    raw_cpf = f"41{suffix}"
    created = client.post(
        "/leads",
        headers=admin_headers,
        json={
            "nome": f"Lead Parceiro {suffix}",
            "cpf": raw_cpf,
            "telefone": f"1196{suffix}",
            "email": f"parceiro{suffix}@demo.local",
            "origem": "Parceiro",
            "produto_interesse": "INSS",
            "responsavel": "Parceiro Demo",
        },
    )
    assert created.status_code == 201

    login = _login("parceiro@bbbconsig.demo", "Parceiro@2026")
    headers = {"Authorization": f"Bearer {login['access_token']}"}

    dashboard = client.get("/dashboard/resumo", headers=headers)
    assert dashboard.status_code == 200

    leads = client.get("/leads", headers=headers)
    assert leads.status_code == 200
    assert all(item["responsavel"] == "Parceiro Demo" for item in leads.json())
    partner_lead = next(item for item in leads.json() if item["nome"] == f"Lead Parceiro {suffix}")
    assert partner_lead["cpf"].startswith("***.***.")
    assert raw_cpf not in partner_lead["cpf"]

    clients = client.get("/clientes", headers=headers)
    assert clients.status_code == 403

    admin_users = client.get("/auth/users", headers=headers)
    assert admin_users.status_code == 403


def test_internal_profiles_can_view_operational_sensitive_data() -> None:
    credentials = [
        ("admin@bbbconsig.demo", "BbbConsig@2026"),
        ("supervisor@bbbconsig.demo", "Supervisor@2026"),
        ("operador@bbbconsig.demo", "Operador@2026"),
    ]
    for email, password in credentials:
        login = _login(email, password)
        headers = {"Authorization": f"Bearer {login['access_token']}"}
        leads = client.get("/leads", headers=headers)
        clients = client.get("/clientes", headers=headers)
        detail = client.get("/leads/1/detalhe", headers=headers)

        assert leads.status_code == 200
        assert clients.status_code == 200
        assert detail.status_code == 200
        assert leads.json()[0]["cpf"] != "***.***.***-**"
        assert "*" not in leads.json()[0]["cpf"]
        assert "*" not in detail.json()["telefone"]
        assert "*" not in clients.json()[0]["cpf"]


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
    assert body["cpf"] == cpf
    assert body["telefone"] == phone

    blocked = client.post(
        "/whatsapp/simular-envio",
        headers=headers,
        json={"destinatario_tipo": "cliente", "destinatario_id": body["id"], "modelo": "primeiro_contato", "mensagem": "Mensagem ficticia."},
    )
    assert blocked.status_code == 403

    consent = client.post("/consents", headers=headers, json={"customer_id": body["id"], "channel": "whatsapp", "source": "pytest"})
    assert consent.status_code == 201
    assert consent.json()["granted"] is True

    sent = client.post(
        "/whatsapp/simular-envio",
        headers=headers,
        json={"destinatario_tipo": "cliente", "destinatario_id": body["id"], "modelo": "primeiro_contato", "mensagem": "Mensagem ficticia."},
    )
    assert sent.status_code == 201
    assert sent.json()["status"] == "Registrada em simulacao"

    simulation = client.get(f"/consultas/inss/{cpf}", headers=headers)
    assert simulation.status_code == 200
    assert "snapshot" in simulation.json()
    assert "regra_aplicada" in simulation.json()

    deleted = client.delete(f"/clientes/{body['id']}", headers=headers)
    assert deleted.status_code == 200

    listed = client.get("/clientes", headers=headers)
    assert all(item["id"] != body["id"] for item in listed.json())

    with SessionLocal() as db:
        stored = db.get(Client, body["id"])
        assert stored is not None
        assert stored.deleted_at is not None
        audit = db.scalar(select(AuditLog).where(AuditLog.action == "whatsapp_simulation_created").order_by(AuditLog.id.desc()))
        assert audit is not None
        assert cpf not in (audit.metadata_json or "")
