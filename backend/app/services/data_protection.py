import base64
import hashlib
import hmac
import json
import os
from dataclasses import dataclass

from cryptography.fernet import Fernet, InvalidToken

from app.services.privacy import only_digits

ENVELOPE_VERSION = "bbb:v1"
KEY_ENV = "BBB_DATA_ENCRYPTION_KEY"


class DataProtectionError(RuntimeError):
    pass


@dataclass(frozen=True)
class ProtectedValue:
    ciphertext: str
    digest: str


def _key_from_env() -> bytes:
    value = os.environ.get(KEY_ENV, "").strip()
    if not value or value in {"troque-este-valor", "change-me", "placeholder"}:
        raise DataProtectionError(f"{KEY_ENV} ausente ou insegura")
    try:
        decoded = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
        if len(decoded) >= 32:
            return decoded
    except Exception:
        pass
    if len(value) < 32:
        raise DataProtectionError(f"{KEY_ENV} deve ter pelo menos 32 caracteres")
    return hashlib.sha256(value.encode("utf-8")).digest()


def cpf_digest(cpf: str) -> str:
    key = _key_from_env()
    digits = only_digits(cpf)
    return hmac.new(key, f"cpf:{digits}".encode("utf-8"), hashlib.sha256).hexdigest()


def _fernet() -> Fernet:
    key = base64.urlsafe_b64encode(_key_from_env())
    return Fernet(key)


def encrypt_text(value: str | None) -> str | None:
    if value is None:
        return None
    token = _fernet().encrypt(value.encode("utf-8")).decode("ascii")
    payload = {
        "v": ENVELOPE_VERSION,
        "alg": "fernet",
        "token": token,
    }
    return base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8")).decode("ascii")


def decrypt_text(envelope: str | None) -> str | None:
    if envelope is None:
        return None
    key = _key_from_env()
    try:
        payload = json.loads(base64.urlsafe_b64decode(envelope.encode("ascii")).decode("utf-8"))
        if payload.get("v") != ENVELOPE_VERSION:
            raise DataProtectionError("versao de envelope nao suportada")
        if payload.get("alg") != "fernet":
            raise DataProtectionError("algoritmo de envelope nao suportado")
        token = payload["token"].encode("ascii")
    except Exception as exc:
        raise DataProtectionError("envelope criptografado invalido") from exc
    try:
        return _fernet().decrypt(token).decode("utf-8")
    except InvalidToken as exc:
        raise DataProtectionError("falha de autenticacao do envelope")
    except Exception as exc:
        raise DataProtectionError("envelope criptografado invalido") from exc


def protect_cpf(cpf: str) -> ProtectedValue:
    return ProtectedValue(ciphertext=encrypt_text(cpf) or "", digest=cpf_digest(cpf))


def ensure_protection_key_ready() -> None:
    _key_from_env()
