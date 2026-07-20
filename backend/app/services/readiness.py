import os

from app.config.environment import DEMO_AUTH_SECRET, PLACEHOLDER_AUTH_SECRET, is_postgresql_url
from app.services.data_protection import ensure_protection_key_ready
from app.services.database_target_guard import (
    EXPECTED_FINGERPRINT_ENV,
    DatabaseTargetGuardError,
    validate_database_target,
)

PRODUCTION_MODE_VALUES = {"production", "producao", "real-data"}


def production_mode_enabled() -> bool:
    return os.environ.get("APP_MODE", "demo").strip().lower() in PRODUCTION_MODE_VALUES


def _enabled(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "sim", "ok"}


def check_production_readiness() -> list[str]:
    missing: list[str] = []
    database_url = os.environ.get("DATABASE_URL", "").strip()
    auth_secret = os.environ.get("BBB_AUTH_SECRET", "").strip()

    if not database_url or not is_postgresql_url(database_url):
        missing.append("DATABASE_URL")
    elif production_mode_enabled():
        expected_fingerprint = os.environ.get(EXPECTED_FINGERPRINT_ENV, "").strip()
        if not expected_fingerprint:
            missing.append(EXPECTED_FINGERPRINT_ENV)
        else:
            try:
                validate_database_target(
                    database_url,
                    expected_fingerprint,
                    environment=os.environ.get("APP_ENV", "production"),
                )
            except DatabaseTargetGuardError:
                missing.append("DATABASE_TARGET")
    try:
        ensure_protection_key_ready()
    except Exception:
        missing.append("BBB_DATA_ENCRYPTION_KEY")
    if len(auth_secret) < 32 or auth_secret in {DEMO_AUTH_SECRET, PLACEHOLDER_AUTH_SECRET}:
        missing.append("BBB_AUTH_SECRET")
    for name in [
        "MIGRATIONS_APPLIED",
        "BACKUP_CONFIGURED",
        "CONSENT_REQUIRED",
        "LOGS_MASKED",
        "HTTPS_EXPECTED",
        "CRITICAL_TESTS_APPROVED",
    ]:
        if not _enabled(name):
            missing.append(name)
    return missing


def assert_production_ready() -> None:
    if not production_mode_enabled():
        return
    missing = check_production_readiness()
    if missing:
        names = ", ".join(sorted(set(missing)))
        raise RuntimeError(f"APP_MODE=production bloqueado. Configuracoes pendentes: {names}")
