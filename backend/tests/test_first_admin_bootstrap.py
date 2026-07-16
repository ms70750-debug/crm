from datetime import datetime, timedelta
from time import time_ns

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.database.init_db import init_db
from app.database.session import SessionLocal
from app.main import app
from app.models import AdminBootstrapToken, AuditLog, User
from app.services.admin_bootstrap import (
    AdminBootstrapBlocked,
    ADMIN_BOOTSTRAP_TTL_MINUTES,
    activate_admin_bootstrap_token,
    create_admin_bootstrap_link,
    token_hash,
)
from app.services.security import hash_password

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_bootstrap_data():
    from app.services.security import _rate_buckets

    init_db()
    _rate_buckets.clear()
    with SessionLocal() as db:
        for token in db.scalars(select(AdminBootstrapToken)).all():
            db.delete(token)
        for user in db.scalars(select(User).where(User.email.like("%@bootstrap.test"))).all():
            db.delete(user)
        db.commit()
    yield
    _rate_buckets.clear()
    with SessionLocal() as db:
        for token in db.scalars(select(AdminBootstrapToken)).all():
            db.delete(token)
        for user in db.scalars(select(User).where(User.email.like("%@bootstrap.test"))).all():
            db.delete(user)
        db.commit()


def _email(label: str) -> str:
    return f"{label}-{time_ns()}@bootstrap.test"


def _strong_password() -> str:
    return "SenhaForte!2026"


def _token_from_link(link: str) -> str:
    return link.split("token=", 1)[1]


def test_create_and_activate_first_real_admin_without_storing_raw_token() -> None:
    email = _email("first")
    with SessionLocal() as db:
        result = create_admin_bootstrap_link(db, email, github_run_id="pytest")
        raw_token = _token_from_link(result.link)
        record = db.scalar(select(AdminBootstrapToken).where(AdminBootstrapToken.email == email))
        assert record is not None
        assert record.token_hash == token_hash(raw_token)
        assert raw_token not in str(record.__dict__)
        assert record.used_at is None
        assert (record.expires_at - datetime.utcnow()) <= timedelta(minutes=ADMIN_BOOTSTRAP_TTL_MINUTES)

        user = activate_admin_bootstrap_token(db, raw_token, _strong_password(), _strong_password())
        assert user.email == email
        assert user.role == "admin"
        assert user.ativo is True
        assert record.used_at is not None

        audit_text = "\n".join(log.metadata_json or "" for log in db.scalars(select(AuditLog)).all())
        assert raw_token not in audit_text
        assert _strong_password() not in audit_text


def test_common_user_is_promoted_only_after_valid_token() -> None:
    email = _email("common")
    with SessionLocal() as db:
        db.add(User(nome="Usuario comum", email=email, password_hash=hash_password("SenhaAntiga!2026"), role="operador", ativo=True))
        db.commit()
        result = create_admin_bootstrap_link(db, email)
        raw_token = _token_from_link(result.link)
        user = activate_admin_bootstrap_token(db, raw_token, _strong_password(), _strong_password())
        assert user.role == "admin"
        assert db.scalar(select(User).where(User.email == email)).id == user.id


def test_same_email_admin_can_receive_recovery_token_without_duplicate() -> None:
    email = _email("admin")
    with SessionLocal() as db:
        db.add(User(nome="Admin real", email=email, password_hash=hash_password("SenhaAntiga!2026"), role="admin", ativo=True))
        db.commit()
        result = create_admin_bootstrap_link(db, email)
        assert result.duplicate_admin is True
        raw_token = _token_from_link(result.link)
        user = activate_admin_bootstrap_token(db, raw_token, _strong_password(), _strong_password())
        assert user.role == "admin"
        assert len(db.scalars(select(User).where(User.email == email)).all()) == 1


def test_other_real_admin_blocks_first_admin_creation() -> None:
    target = _email("target")
    other = _email("other")
    with SessionLocal() as db:
        db.add(User(nome="Outro admin", email=other, password_hash=hash_password("SenhaAdmin!2026"), role="admin", ativo=True))
        db.commit()
        with pytest.raises(AdminBootstrapBlocked):
            create_admin_bootstrap_link(db, target)


def test_invalid_expired_and_used_tokens_are_rejected() -> None:
    email = _email("invalid")
    with SessionLocal() as db:
        result = create_admin_bootstrap_link(db, email)
        raw_token = _token_from_link(result.link)
        assert client.get("/auth/admin-bootstrap/validate", headers={"X-Admin-Bootstrap-Token": "invalido"}).json() == {"valid": False, "expires_at": None}

        record = db.scalar(select(AdminBootstrapToken).where(AdminBootstrapToken.email == email))
        assert record is not None
        record.expires_at = datetime.utcnow() - timedelta(minutes=1)
        db.commit()
        assert client.get("/auth/admin-bootstrap/validate", headers={"X-Admin-Bootstrap-Token": raw_token}).json()["valid"] is False

    email_used = _email("used")
    with SessionLocal() as db:
        result = create_admin_bootstrap_link(db, email_used)
        raw_token = _token_from_link(result.link)
        activate_admin_bootstrap_token(db, raw_token, _strong_password(), _strong_password())
    response = client.post(
        "/auth/admin-bootstrap/activate",
        json={"token": raw_token, "password": _strong_password(), "password_confirmation": _strong_password()},
    )
    assert response.status_code == 400


def test_activation_rejects_weak_or_mismatched_password_and_rate_limits() -> None:
    email = _email("weak")
    with SessionLocal() as db:
        raw_token = _token_from_link(create_admin_bootstrap_link(db, email).link)

    weak = client.post(
        "/auth/admin-bootstrap/activate",
        json={"token": raw_token, "password": "fraca", "password_confirmation": "fraca"},
    )
    assert weak.status_code == 400
    mismatch = client.post(
        "/auth/admin-bootstrap/activate",
        json={"token": raw_token, "password": _strong_password(), "password_confirmation": "OutraSenha!2026"},
    )
    assert mismatch.status_code == 400
    responses = [
        client.post(
            "/auth/admin-bootstrap/activate",
            json={"token": "invalido", "password": _strong_password(), "password_confirmation": _strong_password()},
        )
        for _ in range(6)
    ]
    assert responses[-1].status_code == 429


def test_activation_endpoint_sets_secure_session_and_demo_login_stays_blocked(monkeypatch: pytest.MonkeyPatch) -> None:
    email = _email("endpoint")
    with SessionLocal() as db:
        raw_token = _token_from_link(create_admin_bootstrap_link(db, email).link)
    response = client.post(
        "/auth/admin-bootstrap/activate",
        json={"token": raw_token, "password": _strong_password(), "password_confirmation": _strong_password()},
    )
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "admin"
    assert client.cookies.get("bbb_consig_session") is not None
    monkeypatch.setenv("APP_MODE", "demo")
    monkeypatch.setenv("PUBLIC_DEMO_LOGIN_ENABLED", "false")
    assert client.post("/auth/demo-login", json={"role": "admin"}).status_code == 403
