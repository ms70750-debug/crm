import base64
import hashlib
import hmac
import json
import os
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Any

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import AuditLog, User
from app.services.privacy import mask_cpf, mask_email, mask_phone

SECRET = os.environ.get("BBB_AUTH_SECRET", "bbb-consig-crm-demo-secret")
TOKEN_TTL_SECONDS = 60 * 60 * 8
_rate_buckets: dict[str, deque[float]] = defaultdict(deque)


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


def create_token(user: User) -> str:
    payload = {"sub": user.id, "email": user.email, "role": user.role, "exp": int(time.time()) + TOKEN_TTL_SECONDS}
    raw = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode()
    signature = hmac.new(SECRET.encode(), raw.encode(), hashlib.sha256).hexdigest()
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


def current_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Autenticacao obrigatoria")
    payload = parse_token(authorization.split(" ", 1)[1])
    user = db.get(User, int(payload["sub"]))
    if not user or not user.ativo:
        raise HTTPException(status_code=401, detail="Usuario invalido")
    return user


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
            created_at=datetime.utcnow(),
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
    return datetime.utcnow() + timedelta(seconds=TOKEN_TTL_SECONDS)
