import hashlib
import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AdminBootstrapToken, User
from app.services.privacy import mask_email
from app.services.security import hash_password, log_audit, normalize_role

ADMIN_BOOTSTRAP_PURPOSE = "first_admin_activation"
ADMIN_BOOTSTRAP_TTL_MINUTES = 60
ACTIVATION_BASE_URL = "https://crm-sepia-beta.vercel.app/ativar-admin"
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class AdminBootstrapError(RuntimeError):
    pass


class AdminBootstrapBlocked(AdminBootstrapError):
    pass


@dataclass(frozen=True)
class BootstrapLink:
    link: str
    expires_at: datetime
    duplicate_admin: bool


def normalize_email(email: str) -> str:
    normalized = (email or "").strip().lower()
    if not EMAIL_PATTERN.match(normalized):
        raise AdminBootstrapError("E-mail invalido")
    return normalized


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def is_demo_email(email: str) -> bool:
    return normalize_email(email).endswith(".demo")


def is_strong_password(password: str) -> bool:
    return (
        len(password) >= 12
        and any(char.islower() for char in password)
        and any(char.isupper() for char in password)
        and any(char.isdigit() for char in password)
        and any(not char.isalnum() for char in password)
    )


def _real_admins(db: Session) -> list[User]:
    users = db.scalars(select(User).where(User.role == "admin", User.ativo.is_(True))).all()
    return [user for user in users if not is_demo_email(user.email)]


def create_admin_bootstrap_link(
    db: Session,
    email: str,
    *,
    activation_base_url: str = ACTIVATION_BASE_URL,
    github_run_id: str | None = None,
    created_by_source: str = "github_actions",
) -> BootstrapLink:
    normalized_email = normalize_email(email)
    admins = _real_admins(db)
    same_email_admin = any(user.email.lower() == normalized_email for user in admins)
    other_admins = [user for user in admins if user.email.lower() != normalized_email]
    if other_admins:
        log_audit(
            db,
            "admin_bootstrap_blocked_existing_admin",
            "admin_bootstrap_token",
            actor="system",
            metadata={"email": normalized_email, "existing_admin": mask_email(other_admins[0].email)},
        )
        db.commit()
        raise AdminBootstrapBlocked("Ja existe administrador real")

    now = datetime.utcnow()
    expires_at = now + timedelta(minutes=ADMIN_BOOTSTRAP_TTL_MINUTES)
    user = db.scalar(select(User).where(User.email == normalized_email))
    for pending in db.scalars(
        select(AdminBootstrapToken).where(
            AdminBootstrapToken.email == normalized_email,
            AdminBootstrapToken.used_at.is_(None),
        )
    ):
        pending.used_at = now
        pending.updated_at = now

    raw_token = secrets.token_urlsafe(48)
    record = AdminBootstrapToken(
        user_id=user.id if user else None,
        email=normalized_email,
        token_hash=token_hash(raw_token),
        purpose=ADMIN_BOOTSTRAP_PURPOSE,
        expires_at=expires_at,
        github_run_id=github_run_id,
        created_by_source=created_by_source,
    )
    db.add(record)
    db.flush()
    log_audit(
        db,
        "admin_bootstrap_created",
        "admin_bootstrap_token",
        record.id,
        actor="system",
        metadata={"email": normalized_email, "expires_minutes": ADMIN_BOOTSTRAP_TTL_MINUTES, "duplicate_admin": same_email_admin},
    )
    db.commit()
    return BootstrapLink(link=f"{activation_base_url}?token={raw_token}", expires_at=expires_at, duplicate_admin=same_email_admin)


def validate_admin_bootstrap_token(db: Session, token: str) -> AdminBootstrapToken:
    if not token or len(token) < 32:
        raise AdminBootstrapError("Token invalido")
    record = db.scalar(select(AdminBootstrapToken).where(AdminBootstrapToken.token_hash == token_hash(token)))
    now = datetime.utcnow()
    if not record or record.used_at is not None or record.expires_at <= now:
        raise AdminBootstrapError("Token invalido")
    return record


def activate_admin_bootstrap_token(db: Session, token: str, password: str, password_confirmation: str) -> User:
    if password != password_confirmation:
        raise AdminBootstrapError("Senha invalida")
    if not is_strong_password(password):
        raise AdminBootstrapError("Senha invalida")
    record = validate_admin_bootstrap_token(db, token)
    normalized_email = normalize_email(record.email)
    now = datetime.utcnow()

    admins = _real_admins(db)
    other_admins = [user for user in admins if user.email.lower() != normalized_email]
    if other_admins:
        log_audit(
            db,
            "admin_bootstrap_activation_blocked_existing_admin",
            "admin_bootstrap_token",
            record.id,
            actor="system",
            metadata={"email": normalized_email, "existing_admin": mask_email(other_admins[0].email)},
        )
        db.commit()
        raise AdminBootstrapBlocked("Ativacao indisponivel")

    user = db.scalar(select(User).where(User.email == normalized_email))
    if user:
        user.role = "admin"
        user.ativo = True
        user.password_hash = hash_password(password)
        user.updated_at = now
    else:
        user = User(nome=normalized_email.split("@", 1)[0], email=normalized_email, password_hash=hash_password(password), role="admin", ativo=True)
        db.add(user)
        db.flush()

    record.user_id = user.id
    record.used_at = now
    record.updated_at = now
    for pending in db.scalars(
        select(AdminBootstrapToken).where(
            AdminBootstrapToken.email == normalized_email,
            AdminBootstrapToken.id != record.id,
            AdminBootstrapToken.used_at.is_(None),
        )
    ):
        pending.used_at = now
        pending.updated_at = now

    log_audit(
        db,
        "admin_bootstrap_activated",
        "user",
        user.id,
        actor=normalized_email,
        actor_user_id=user.id,
        metadata={"email": normalized_email, "role": normalize_role(user.role)},
    )
    db.commit()
    db.refresh(user)
    return user
