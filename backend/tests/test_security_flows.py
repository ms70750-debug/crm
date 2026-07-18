import base64
from datetime import datetime, timedelta
import json
from time import time_ns

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.config.environment import validate_environment
from app.database.init_db import init_db
from app.database.session import SessionLocal
from app.main import app
from app.models import AuditLog, AuthSession, Client, Consent, Simulation
from app.services.privacy import is_valid_cpf


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_rate_limits():
    from app.services.security import _rate_buckets

    _rate_buckets.clear()
    yield
    _rate_buckets.clear()


def test_production_environment_rejects_insecure_required_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("BBB_AUTH_SECRET", "bbb-consig-crm-demo-secret")
    monkeypatch.setenv("CORS_ORIGINS", "https://SEU-FRONTEND.vercel.app")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./app.db")
    monkeypatch.setenv("EVOLUTION_API_MODE", "simulation")

    with pytest.raises(RuntimeError):
        validate_environment()


def test_production_environment_rejects_missing_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("BBB_AUTH_SECRET", "segredo-demo-forte-para-pytest")
    monkeypatch.setenv("CORS_ORIGINS", "https://crm-sepia-beta.vercel.app")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("EVOLUTION_API_MODE", "simulation")
    monkeypatch.setenv("REAL_DATA_MODE", "false")

    with pytest.raises(RuntimeError):
        validate_environment()


def test_production_sqlite_is_allowed_only_for_controlled_mvp(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("BBB_AUTH_SECRET", "segredo-demo-forte-para-pytest")
    monkeypatch.setenv("CORS_ORIGINS", "https://crm-sepia-beta.vercel.app")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./app.db")
    monkeypatch.setenv("EVOLUTION_API_MODE", "simulation")
    monkeypatch.setenv("REAL_DATA_MODE", "false")

    validate_environment()


def test_real_data_mode_rejects_sqlite(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("BBB_AUTH_SECRET", "segredo-demo-forte-para-pytest")
    monkeypatch.setenv("CORS_ORIGINS", "https://crm-sepia-beta.vercel.app")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./app.db")
    monkeypatch.setenv("EVOLUTION_API_MODE", "simulation")
    monkeypatch.setenv("REAL_DATA_MODE", "true")

    with pytest.raises(RuntimeError):
        validate_environment()


def test_real_data_mode_with_postgresql_still_requires_future_controls(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("BBB_AUTH_SECRET", "segredo-demo-forte-para-pytest")
    monkeypatch.setenv("CORS_ORIGINS", "https://crm-sepia-beta.vercel.app")
    monkeypatch.setenv("DATABASE_URL", "postgresql://host.local:5432/bbb")
    monkeypatch.setenv("EVOLUTION_API_MODE", "simulation")
    monkeypatch.setenv("REAL_DATA_MODE", "true")

    with pytest.raises(RuntimeError):
        validate_environment()


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


def _token_payload(token: str) -> dict:
    raw = token.split(".", 1)[0]
    return json.loads(base64.urlsafe_b64decode(raw.encode()).decode())


def _fictitious_cpf(prefix: str = "39") -> str:
    base = f"{prefix}{str(time_ns())[-9:]}"[:11]
    for digit in "0123456789":
        candidate = f"{base[:-1]}{digit}"
        if not is_valid_cpf(candidate):
            return candidate
    return "00000000000"


def test_login_rejects_invalid_password() -> None:
    init_db()
    response = client.post("/auth/login", json={"email": "admin@bbbconsig.demo", "password": "senha-errada"})
    assert response.status_code == 401


def test_healthz_reports_safe_database_and_version_metadata() -> None:
    init_db()
    response = client.get("/healthz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
    assert body["version"]
    assert "DATABASE_URL" not in response.text
    assert "postgresql://" not in response.text


def test_global_rate_limit_blocks_excessive_requests() -> None:
    init_db()
    responses = [client.get("/auth/me") for _ in range(301)]
    assert responses[-1].status_code == 429


def test_login_rate_limit_blocks_repeated_attempts() -> None:
    init_db()
    suffix = str(time_ns())[-9:]
    email = f"rate-limit-{suffix}@demo.local"
    responses = [
        client.post("/auth/login", json={"email": email, "password": "senha-errada"})
        for _ in range(11)
    ]
    assert responses[-1].status_code == 429


def test_demo_login_is_limited_to_demo_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    init_db()
    monkeypatch.setenv("APP_MODE", "demo")
    monkeypatch.setenv("PUBLIC_DEMO_LOGIN_ENABLED", "true")
    allowed = client.post("/auth/demo-login", json={"role": "admin"})
    assert allowed.status_code == 200

    client.cookies.clear()
    monkeypatch.setenv("APP_MODE", "demo")
    monkeypatch.setenv("PUBLIC_DEMO_LOGIN_ENABLED", "false")
    blocked_by_default = client.post("/auth/demo-login", json={"role": "admin"})
    assert blocked_by_default.status_code == 403

    client.cookies.clear()
    monkeypatch.setenv("APP_MODE", "internal")
    monkeypatch.setenv("PUBLIC_DEMO_LOGIN_ENABLED", "true")
    blocked = client.post("/auth/demo-login", json={"role": "admin"})
    assert blocked.status_code == 403
    monkeypatch.setenv("APP_MODE", "demo")


def test_auth_me_and_route_protection() -> None:
    login = _login("admin@bbbconsig.demo", "BbbConsig@2026")
    assert "password" not in str(login).lower()
    assert "hash" not in str(login).lower()
    headers = {"Authorization": f"Bearer {login['access_token']}"}

    me = client.get("/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["role"] == "admin"
    assert "password_hash" not in me.text
    assert client.cookies.get("bbb_consig_session") is not None

    client.cookies.clear()
    blocked = client.get("/dashboard/resumo")
    assert blocked.status_code == 401

    dashboard = client.get("/dashboard/resumo", headers=headers)
    assert dashboard.status_code == 200
    assert "cards" in dashboard.json()

    cookie_login = _login("admin@bbbconsig.demo", "BbbConsig@2026")
    assert cookie_login["user"]["role"] == "admin"
    cookie_dashboard = client.get("/dashboard/resumo")
    assert cookie_dashboard.status_code == 200
    logout = client.post("/auth/logout")
    assert logout.status_code == 200
    assert client.get("/dashboard/resumo").status_code == 401


def test_login_creates_server_side_session_and_does_not_store_full_token() -> None:
    login = _login("admin@bbbconsig.demo", "BbbConsig@2026")
    token = login["access_token"]
    payload = _token_payload(token)
    assert payload["sid"]

    with SessionLocal() as db:
        session = db.scalar(select(AuthSession).where(AuthSession.user_id == login["user"]["id"]).order_by(AuthSession.id.desc()))
        assert session is not None
        assert session.revoked_at is None
        assert session.expires_at > datetime.utcnow()
        assert token not in str(session.__dict__)
        assert payload["sid"] not in str(session.__dict__)

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_logout_revokes_server_side_session_and_blocks_copied_bearer_token() -> None:
    login = _login("admin@bbbconsig.demo", "BbbConsig@2026")
    token = login["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/auth/me", headers=headers).status_code == 200

    logout = client.post("/auth/logout", headers=headers)
    assert logout.status_code == 200
    assert client.cookies.get("bbb_consig_session") is None
    assert client.get("/auth/me", headers=headers).status_code == 401

    with SessionLocal() as db:
        session = db.scalar(select(AuthSession).where(AuthSession.user_id == login["user"]["id"]).order_by(AuthSession.id.desc()))
        assert session is not None
        assert session.revoked_at is not None
        assert session.revocation_reason == "logout"


def test_expired_or_missing_server_side_session_fails() -> None:
    expired_login = _login("admin@bbbconsig.demo", "BbbConsig@2026")
    expired_token = expired_login["access_token"]
    with SessionLocal() as db:
        session = db.scalar(select(AuthSession).where(AuthSession.user_id == expired_login["user"]["id"]).order_by(AuthSession.id.desc()))
        assert session is not None
        session.expires_at = datetime.utcnow() - timedelta(seconds=1)
        db.commit()
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {expired_token}"}).status_code == 401

    missing_login = _login("admin@bbbconsig.demo", "BbbConsig@2026")
    missing_token = missing_login["access_token"]
    with SessionLocal() as db:
        session = db.scalar(select(AuthSession).where(AuthSession.user_id == missing_login["user"]["id"]).order_by(AuthSession.id.desc()))
        assert session is not None
        db.delete(session)
        db.commit()
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {missing_token}"}).status_code == 401


def test_revoked_session_does_not_affect_another_valid_session_for_same_user() -> None:
    first = _login("admin@bbbconsig.demo", "BbbConsig@2026")
    first_headers = {"Authorization": f"Bearer {first['access_token']}"}
    second = _login("admin@bbbconsig.demo", "BbbConsig@2026")
    second_headers = {"Authorization": f"Bearer {second['access_token']}"}

    assert client.post("/auth/logout", headers=first_headers).status_code == 200
    assert client.get("/auth/me", headers=first_headers).status_code == 401
    assert client.get("/auth/me", headers=second_headers).status_code == 200


def test_demo_mode_blocks_valid_cpf_and_allows_fictitious_cpf(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_MODE", "demo")
    token = _token()
    headers = {"Authorization": f"Bearer {token}"}
    suffix = str(time_ns())[-9:]

    blocked = client.post(
        "/clientes",
        headers=headers,
        json={
            "nome": f"CPF Real Bloqueado {suffix}",
            "cpf": "529.982.247-25",
            "telefone": f"1198{suffix}",
            "email": f"blocked{suffix}@demo.local",
            "convenio": "INSS",
        },
    )
    assert blocked.status_code == 400
    assert "Ambiente de demonstracao" in blocked.text

    allowed = client.post(
        "/clientes",
        headers=headers,
        json={
            "nome": f"CPF Ficticio Permitido {suffix}",
            "cpf": _fictitious_cpf(),
            "telefone": f"1197{suffix}",
            "email": f"allowed{suffix}@demo.local",
            "convenio": "INSS",
        },
    )
    assert allowed.status_code == 201

    simulation_blocked = client.get("/consultas/inss/52998224725", headers=headers)
    assert simulation_blocked.status_code == 400


def test_whatsapp_status_is_simulated() -> None:
    token = _token()
    response = client.get("/whatsapp/status", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "simulation"
    assert body["real_send_enabled"] is False


def test_partner_permissions_are_limited() -> None:
    admin = _login("admin@bbbconsig.demo", "BbbConsig@2026")
    admin_headers = {"Authorization": f"Bearer {admin['access_token']}"}
    suffix = str(time_ns())[-9:]
    raw_cpf = _fictitious_cpf("41")
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
    cpf = _fictitious_cpf()
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
    assert consent.json()["terms_version"] == "minuta-lgpd-v1"

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
    assert simulation.json()["snapshot"]["rule_version"] == "demo-v1"

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
        stored_consent = db.scalar(select(Consent).where(Consent.customer_id == body["id"]).order_by(Consent.id.desc()))
        assert stored_consent is not None
        assert stored_consent.terms_version == "minuta-lgpd-v1"
        stored_simulation = db.scalar(select(Simulation).where(Simulation.cpf_masked == simulation.json()["cpf"]).order_by(Simulation.id.desc()))
        assert stored_simulation is not None
        assert stored_simulation.rule_version == "demo-v1"
        assert stored_simulation.created_by_user_id is not None
