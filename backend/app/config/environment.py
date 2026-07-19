import logging
import os

logger = logging.getLogger("bbb-consig.environment")

PRODUCTION_ENV_VALUES = {"production", "prod", "render"}
DEMO_AUTH_SECRET = "bbb-consig-crm-demo-secret"
PLACEHOLDER_AUTH_SECRET = "troque-este-valor-em-ambiente-seguro"
PENDING_REAL_DATA_CONTROLS = "criptografia em repouso, autenticacao segura, backup/restore, monitoramento e revisao LGPD"
DEMO_MODE_VALUES = {"demo", "demonstracao", "demonstração"}


SIMULATION_MODE_VALUES = {"simulation", "simulate", "simulacao", "simulação"}


def is_production_environment() -> bool:
    return os.environ.get("APP_ENV", "local").strip().lower() in PRODUCTION_ENV_VALUES


def app_mode() -> str:
    return os.environ.get("APP_MODE", "demo").strip().lower() or "demo"


def demo_mode_enabled() -> bool:
    return app_mode() in DEMO_MODE_VALUES


def public_demo_login_enabled() -> bool:
    return os.environ.get("PUBLIC_DEMO_LOGIN_ENABLED", "false").strip().lower() in {"1", "true", "yes", "sim"}


def is_postgresql_url(database_url: str) -> bool:
    return database_url.startswith(("postgres://", "postgresql://", "postgresql+psycopg://", "postgresql+psycopg2://"))


def is_sqlite_url(database_url: str) -> bool:
    return database_url.startswith("sqlite")


def real_data_mode_enabled() -> bool:
    return os.environ.get("REAL_DATA_MODE", "false").strip().lower() in {"1", "true", "yes", "sim"}


def validate_environment() -> None:
    from app.services.readiness import assert_production_ready, production_mode_enabled

    assert_production_ready()
    if production_mode_enabled():
        logger.info("Readiness de producao validado sem expor valores secretos.")
        return

    if not is_production_environment():
        return

    errors: list[str] = []
    auth_secret = os.environ.get("BBB_AUTH_SECRET", "")
    cors_origins = os.environ.get("CORS_ORIGINS", "")
    database_url = os.environ.get("DATABASE_URL", "")
    evolution_mode = os.environ.get("EVOLUTION_API_MODE", "")
    mode = app_mode()
    real_data_mode = real_data_mode_enabled()

    if mode not in DEMO_MODE_VALUES:
        errors.append("APP_MODE deve permanecer como demo nesta fase controlada")
    if not auth_secret or auth_secret in {DEMO_AUTH_SECRET, PLACEHOLDER_AUTH_SECRET}:
        errors.append("BBB_AUTH_SECRET ausente ou inseguro")
    if not cors_origins or "SEU-FRONTEND" in cors_origins:
        errors.append("CORS_ORIGINS ausente ou com placeholder")
    if not database_url:
        errors.append("DATABASE_URL ausente")
    elif not is_postgresql_url(database_url) and (real_data_mode or mode not in DEMO_MODE_VALUES):
        errors.append("APP_ENV=production exige DATABASE_URL PostgreSQL persistente fora do modo demo")
    if evolution_mode not in SIMULATION_MODE_VALUES:
        errors.append("EVOLUTION_API_MODE deve permanecer como simulation/simulate nesta fase")
    if real_data_mode:
        errors.append(f"REAL_DATA_MODE permanece bloqueado ate concluir {PENDING_REAL_DATA_CONTROLS}")

    if not errors:
        logger.info("Ambiente de producao controlada validado sem expor segredos.")
        return

    for error in errors:
        logger.error("Configuracao de ambiente invalida: %s", error)
    raise RuntimeError(
        "Variaveis obrigatorias ausentes ou inseguras para producao controlada: "
        + "; ".join(errors)
    )
