import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Any

from fastapi import Cookie, Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import AuditLog, AuthSession, User
from app.config.environment import is_production_environment
from app.services.datetime_utc import is_expired, utc_now
from app.services.privacy import mask_cpf, mask_email, mask_phone

SECRET = os.environ.get("BBB_AUTH_SECRET", "bbb-consig-crm-demo-secret")
TOKEN_TTL_SECONDS = 60 * 60 * 8
SESSION_COOKIE_NAME = "bbb_consig_session"
_rate_buckets: dict[str, deque[float]] = defaultdict(deque)
ROLES = ("admin", "supervisor", "operador", "parceiro")
ROLE_LABELS = {
    "admin": "Administrador",
    "supervisor": "Supervisor",
    "operador": "Operador/Vendedor",
    "parceiro": "Parceiro",
}


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or base64.urlsafe_b64encode(os.urandom(16)).decode("ascii")
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 240_000)
    return f"pbkdf2_sha256${salt}${base64.urlsafe_b64encode(digest).decode('ascii')}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, salt, expected = stored.split("$", 2)
    except ValueError:
        return False
    return hmac.compare_digest(hash_password(password, salt), stored)


def _session_id_hash(session_id: str) -> str:
    return hashlib.sha256(session_id.encode("utf-8")).hexdigest()


def create_session_token(db: Session, user: User) -> str:
    session_id = secrets.token_urlsafe(32)
    expires_at = utc_now() + timedelta(seconds=TOKEN_TTL_SECONDS)
    payload = {
        "sub": user.id,
        "email": user.email,
        "role": normalize_role(user.role),
        "sid": session_id,
        "exp": int(expires_at.timestamp()),
    }
    raw = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode()
    signature = hmac.new(SECRET.encode(), raw.encode(), hashlib.sha256).hexdigest()
    db.add(AuthSession(session_id_hash=_session_id_hash(session_id), user_id=user.id, expires_at=expires_at))
    db.flush()
    return f"{raw}.{signature}"


def parse_token(token: str) -> dict[str, Any]:
    try:
        raw, signature = token.split(".", 1)
    except ValueError:
        raise HTTPException(status_code=401, detail="Token invalido")
    expected = hmac.new(SECRET.encode(), raw.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=401, detail="Token invalido")
    payload = json.loads(base64.urlsafe_b64decode(raw.encode()).decode())
    if int(payload.get("exp", 0)) < int(time.time()):
        raise HTTPException(status_code=401, detail="Token expirado")
    return payload


def _active_session_from_payload(db: Session, payload: dict[str, Any]) -> AuthSession:
    session_id = str(payload.get("sid") or "")
    if not session_id:
        raise HTTPException(status_code=401, detail="Sessao invalida")
    session = db.scalar(select(AuthSession).where(AuthSession.session_id_hash == _session_id_hash(session_id)))
    if not session:
        raise HTTPException(status_code=401, detail="Sessao invalida")
    if session.revoked_at is not None:
        raise HTTPException(status_code=401, detail="Sessao revogada")
    try:
        expired = is_expired(session.expires_at)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Sessao invalida") from exc
    if expired:
        raise HTTPException(status_code=401, detail="Sessao expirada")
    if int(payload.get("sub", 0)) != session.user_id:
        raise HTTPException(status_code=401, detail="Sessao invalida")
    return session


def revoke_session_from_payload(db: Session, payload: dict[str, Any], reason: str = "logout") -> None:
    session_id = str(payload.get("sid") or "")
    if not session_id:
        return
    session = db.scalar(select(AuthSession).where(AuthSession.session_id_hash == _session_id_hash(session_id)))
    if session and session.revoked_at is None:
        session.revoked_at = utc_now()
        session.revocation_reason = reason


def current_user(
    request: Request,
    authorization: str | None = Header(default=None),
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
    db: Session = Depends(get_db),
) -> User:
    token = session_token
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
    if not token:
        raise HTTPException(status_code=401, detail="Autenticacao obrigatoria")
    payload = parse_token(token)
    session = _active_session_from_payload(db, payload)
    request.state.auth_payload = payload
    request.state.auth_session_id_hash = session.session_id_hash
    user = db.get(User, int(payload["sub"]))
    if not user or not user.ativo:
        raise HTTPException(status_code=401, detail="Usuario invalido")
    return user


def normalize_role(role: str | None) -> str:
    value = (role or "operador").strip().lower()
    return value if value in ROLES else "operador"


def user_payload(user: User) -> dict[str, Any]:
    return {
        "id": user.id,
        "nome": user.nome,
        "email": user.email,
        "role": normalize_role(user.role),
        "ativo": user.ativo,
        "created_at": user.created_at,
    }


def require_roles(*roles: str):
    allowed = {normalize_role(role) for role in roles}

    def dependency(user: User = Depends(current_user)) -> User:
        if normalize_role(user.role) not in allowed:
            raise HTTPException(status_code=403, detail="Perfil sem permissao para esta acao")
        return user

    return dependency


def is_partner(user: User) -> bool:
    return normalize_role(user.role) == "parceiro"


def can_view_sensitive_data(user: User) -> bool:
    return normalize_role(user.role) in {"admin", "supervisor", "operador"}


def check_rate_limit(key: str, limit: int = 10, window_seconds: int = 60) -> None:
    now = time.time()
    bucket = _rate_buckets[key]
    while bucket and bucket[0] <= now - window_seconds:
        bucket.popleft()
    if len(bucket) >= limit:
        raise HTTPException(status_code=429, detail="Muitas tentativas. Aguarde e tente novamente.")
    bucket.append(now)


def log_audit(db: Session, action: str, entity_type: str, entity_id: int | None = None, actor: str = "system", actor_user_id: int | None = None, metadata: dict[str, Any] | None = None) -> None:
    sanitized = sanitize_metadata(metadata or {})
    db.add(
        AuditLog(
            actor_user_id=actor_user_id,
            actor=actor,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_json=json.dumps(sanitized, ensure_ascii=False),
            created_at=utc_now(),
        )
    )


def sanitize_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    clean: dict[str, Any] = {}
    for key, value in metadata.items():
        lower = key.lower()
        text = str(value) if value is not None else ""
        if "cpf" in lower:
            clean[key] = mask_cpf(text)
        elif "telefone" in lower or "phone" in lower:
            clean[key] = mask_phone(text)
        elif "email" in lower:
            clean[key] = mask_email(text)
        else:
            clean[key] = value
    return clean


def demo_token_expiration() -> datetime:
    return utc_now() + timedelta(seconds=TOKEN_TTL_SECONDS)


def session_cookie_options() -> dict[str, Any]:
    production = is_production_environment()
    return {
        "key": SESSION_COOKIE_NAME,
        "httponly": True,
        "secure": production,
        "samesite": "none" if production else "lax",
        "max_age": TOKEN_TTL_SECONDS,
        "path": "/",
    }
