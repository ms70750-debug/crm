import logging
import os

logger = logging.getLogger("bbb-consig.environment")

PRODUCTION_ENV_VALUES = {"production", "prod", "render"}
DEMO_AUTH_SECRET = "bbb-consig-crm-demo-secret"
PLACEHOLDER_AUTH_SECRET = "troque-este-valor-em-ambiente-seguro"


def is_production_environment() -> bool:
    return os.environ.get("APP_ENV", "local").strip().lower() in PRODUCTION_ENV_VALUES


def validate_environment() -> None:
    if not is_production_environment():
        return

    errors: list[str] = []
    auth_secret = os.environ.get("BBB_AUTH_SECRET", "")
    cors_origins = os.environ.get("CORS_ORIGINS", "")
    database_url = os.environ.get("DATABASE_URL", "")
    evolution_mode = os.environ.get("EVOLUTION_API_MODE", "")

    if not auth_secret or auth_secret in {DEMO_AUTH_SECRET, PLACEHOLDER_AUTH_SECRET}:
        errors.append("BBB_AUTH_SECRET ausente ou inseguro")
    if not cors_origins or "SEU-FRONTEND" in cors_origins:
        errors.append("CORS_ORIGINS ausente ou com placeholder")
    if not database_url:
        errors.append("DATABASE_URL ausente")
    if evolution_mode != "simulation":
        errors.append("EVOLUTION_API_MODE deve permanecer como simulation nesta fase")

    if not errors:
        logger.info("Ambiente de producao controlada validado sem expor segredos.")
        return

    for error in errors:
        logger.error("Configuracao de ambiente invalida: %s", error)
    raise RuntimeError("Variaveis obrigatorias ausentes ou inseguras para producao controlada.")
