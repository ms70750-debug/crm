import os
from dataclasses import dataclass
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.services.privacy import mask_email
from app.services.security import log_audit

RESEND_API_URL = "https://api.resend.com/emails"
SIMULATE_MODES = {"simulate", "simulado", "simulation", "off", ""}


class AuthEmailError(RuntimeError):
    pass


@dataclass(frozen=True)
class AuthEmailResult:
    sent: bool
    provider: str
    mode: str
    message_id: str | None = None


def auth_email_enabled() -> bool:
    return os.environ.get("AUTH_EMAIL_ENABLED", "false").strip().lower() in {"1", "true", "yes", "sim"}


def auth_email_mode() -> str:
    return os.environ.get("AUTH_EMAIL_MODE", "simulate").strip().lower() or "simulate"


def auth_email_health() -> dict[str, Any]:
    mode = auth_email_mode()
    return {
        "provider": "resend",
        "enabled": auth_email_enabled(),
        "mode": "simulate" if mode in SIMULATE_MODES else "send",
        "from_configured": bool(os.environ.get("AUTH_EMAIL_FROM", "").strip()),
        "secret_configured": bool(os.environ.get("RESEND_API_KEY", "").strip()),
    }


def ensure_auth_email_ready_for_send() -> None:
    if not auth_email_enabled() or auth_email_mode() in SIMULATE_MODES:
        return
    if not os.environ.get("RESEND_API_KEY", "").strip():
        raise AuthEmailError("Provedor transacional sem chave configurada")
    if not os.environ.get("AUTH_EMAIL_FROM", "").strip():
        raise AuthEmailError("Remetente transacional ausente")


def send_admin_activation_email(db: Session, *, to_email: str, activation_link: str, expires_minutes: int) -> AuthEmailResult:
    return _send_auth_email(
        db,
        to_email=to_email,
        subject="Ativacao do CRM BBB CONSIG",
        action="admin_activation_email",
        button_label="Ativar acesso",
        secure_link=activation_link,
        expires_minutes=expires_minutes,
    )


def send_password_recovery_email(db: Session, *, to_email: str, recovery_link: str, expires_minutes: int) -> AuthEmailResult:
    return _send_auth_email(
        db,
        to_email=to_email,
        subject="Recuperacao de senha do CRM BBB CONSIG",
        action="password_recovery_email",
        button_label="Redefinir senha",
        secure_link=recovery_link,
        expires_minutes=expires_minutes,
    )


def _send_auth_email(
    db: Session,
    *,
    to_email: str,
    subject: str,
    action: str,
    button_label: str,
    secure_link: str,
    expires_minutes: int,
) -> AuthEmailResult:
    mode = auth_email_mode()
    if not auth_email_enabled() or mode in SIMULATE_MODES:
        _audit_email(db, action, to_email, sent=False, mode="simulate")
        return AuthEmailResult(sent=False, provider="resend", mode="simulate")

    ensure_auth_email_ready_for_send()
    payload = {
        "from": os.environ["AUTH_EMAIL_FROM"],
        "to": [to_email],
        "subject": subject,
        "html": _email_html(button_label=button_label, secure_link=secure_link, expires_minutes=expires_minutes),
        "text": _email_text(button_label=button_label, secure_link=secure_link, expires_minutes=expires_minutes),
    }
    try:
        response = httpx.post(
            RESEND_API_URL,
            headers={"Authorization": f"Bearer {os.environ['RESEND_API_KEY']}"},
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        _audit_email(db, action, to_email, sent=False, mode="send", error_type=exc.__class__.__name__)
        raise AuthEmailError("Falha no envio transacional") from exc

    message_id = str(response.json().get("id") or "")
    _audit_email(db, action, to_email, sent=True, mode="send", message_id=message_id or None)
    return AuthEmailResult(sent=True, provider="resend", mode="send", message_id=message_id or None)


def _email_html(*, button_label: str, secure_link: str, expires_minutes: int) -> str:
    return (
        "<p>Voce solicitou acesso ao CRM BBB CONSIG.</p>"
        f"<p><a href=\"{secure_link}\">{button_label}</a></p>"
        f"<p>Este link expira em {expires_minutes} minutos e so pode ser usado uma vez.</p>"
        "<p>Se voce nao reconhece esta solicitacao, ignore esta mensagem.</p>"
    )


def _email_text(*, button_label: str, secure_link: str, expires_minutes: int) -> str:
    return (
        "Voce solicitou acesso ao CRM BBB CONSIG.\n"
        f"{button_label}: {secure_link}\n"
        f"Este link expira em {expires_minutes} minutos e so pode ser usado uma vez.\n"
        "Se voce nao reconhece esta solicitacao, ignore esta mensagem."
    )


def _audit_email(
    db: Session,
    action: str,
    to_email: str,
    *,
    sent: bool,
    mode: str,
    message_id: str | None = None,
    error_type: str | None = None,
) -> None:
    metadata = {
        "recipient": mask_email(to_email),
        "provider": "resend",
        "mode": mode,
        "sent": sent,
    }
    if message_id:
        metadata["message_id"] = message_id
    if error_type:
        metadata["error_type"] = error_type
    log_audit(db, action, "auth_email", actor="system", metadata=metadata)
    db.commit()
