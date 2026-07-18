from sqlalchemy import select

from app.database.init_db import init_db
from app.database.session import SessionLocal
from app.models import AuditLog
from app.services.auth_email import AuthEmailError, auth_email_health, send_admin_activation_email


def test_auth_email_defaults_to_simulate_without_exposing_link(monkeypatch) -> None:
    monkeypatch.delenv("AUTH_EMAIL_ENABLED", raising=False)
    monkeypatch.delenv("AUTH_EMAIL_MODE", raising=False)
    init_db()
    link = "https://crm-sepia-beta.vercel.app/ativar-admin?token=token-secreto-sintetico"

    with SessionLocal() as db:
        result = send_admin_activation_email(db, to_email="admin@example.test", activation_link=link, expires_minutes=60)
        audit_text = "\n".join(log.metadata_json or "" for log in db.scalars(select(AuditLog)).all())

    assert result.sent is False
    assert result.mode == "simulate"
    assert "token-secreto-sintetico" not in audit_text
    assert link not in audit_text
    assert "admin@example.test" not in audit_text


def test_auth_email_send_mode_requires_secret_and_sender(monkeypatch) -> None:
    monkeypatch.setenv("AUTH_EMAIL_ENABLED", "true")
    monkeypatch.setenv("AUTH_EMAIL_MODE", "send")
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    monkeypatch.delenv("AUTH_EMAIL_FROM", raising=False)
    init_db()

    with SessionLocal() as db:
        try:
            send_admin_activation_email(
                db,
                to_email="admin@example.test",
                activation_link="https://crm-sepia-beta.vercel.app/ativar-admin?token=sintetico",
                expires_minutes=60,
            )
        except AuthEmailError as exc:
            assert "chave" in str(exc) or "Remetente" in str(exc)
        else:
            raise AssertionError("Envio real sem configuracao deveria falhar")


def test_auth_email_health_reports_only_flags(monkeypatch) -> None:
    monkeypatch.setenv("AUTH_EMAIL_ENABLED", "true")
    monkeypatch.setenv("AUTH_EMAIL_MODE", "send")
    monkeypatch.setenv("RESEND_API_KEY", "secret-value-that-must-not-appear")
    monkeypatch.setenv("AUTH_EMAIL_FROM", "CRM <noreply@example.test>")

    health = auth_email_health()

    assert health == {
        "provider": "resend",
        "enabled": True,
        "mode": "send",
        "from_configured": True,
        "secret_configured": True,
    }
