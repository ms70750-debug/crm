import os
import tempfile
from pathlib import Path

from sqlalchemy.engine import make_url


class TestDatabaseGuardError(RuntimeError):
    __test__ = False

    pass


FORBIDDEN_HOST_FRAGMENTS = (
    "supabase.co",
    "pooler.supabase.com",
    "onrender.com",
    "vercel.app",
    "render.com",
)
LOCAL_POSTGRES_HOSTS = {"localhost", "127.0.0.1", "::1", "postgres"}
TEST_ENV_VALUES = {"test", "testing", "pytest", "ci"}
PRODUCTION_SECRET_ENV_KEYS = (
    "SUPABASE_DIRECT_URL",
    "DIRECT_URL",
    "POSTGRES_RESTORE_URL",
    "RESEND_API_KEY",
    "EVOLUTION_API_TOKEN",
)


def is_test_environment(env: dict[str, str] | None = None) -> bool:
    source = env or os.environ
    return source.get("APP_ENV", "").strip().lower() in TEST_ENV_VALUES


def _safe_error(message: str) -> TestDatabaseGuardError:
    return TestDatabaseGuardError(f"Banco de teste bloqueado: {message}")


def _contains_forbidden_host(value: str) -> bool:
    lowered = value.lower()
    return any(fragment in lowered for fragment in FORBIDDEN_HOST_FRAGMENTS)


def _run_id(env: dict[str, str]) -> str:
    run_id = env.get("BBB_TEST_RUN_ID", "").strip().lower()
    if len(run_id) < 8:
        raise _safe_error("identificador de execucao ausente")
    return run_id


def _validate_sqlite(database: str | None, run_id: str) -> None:
    if not database:
        raise _safe_error("arquivo SQLite ausente")
    path = Path(database).expanduser().resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    repo_app_db = Path(__file__).resolve().parents[2] / "app.db"
    if path == repo_app_db.resolve():
        raise _safe_error("SQLite persistente do workspace nao autorizado")
    if run_id not in path.as_posix().lower():
        raise _safe_error("SQLite temporario sem identificador da execucao")
    try:
        path.relative_to(temp_root)
    except ValueError as exc:
        raise _safe_error("SQLite de teste deve ficar no diretorio temporario") from exc


def _validate_postgres(host: str | None, database: str | None, run_id: str) -> None:
    normalized_host = (host or "").strip().lower()
    normalized_database = (database or "").strip().lower()
    if not normalized_host or not normalized_database:
        raise _safe_error("PostgreSQL de teste sem host ou banco")
    if _contains_forbidden_host(normalized_host):
        raise _safe_error("host externo proibido")
    if normalized_host not in LOCAL_POSTGRES_HOSTS:
        raise _safe_error("PostgreSQL de teste deve ser local ou service container")
    if not any(marker in normalized_database for marker in ("test", "ci", run_id)):
        raise _safe_error("banco PostgreSQL sem marcador descartavel")
    if normalized_database in {"postgres", "template0", "template1", "crm", "crm_prod"}:
        raise _safe_error("banco PostgreSQL persistente ou administrativo")


def guard_test_database_url(database_url: str, env: dict[str, str] | None = None) -> None:
    source = dict(env or os.environ)
    if not is_test_environment(source):
        return
    if not database_url:
        raise _safe_error("DATABASE_URL ausente")
    run_id = _run_id(source)
    for key in PRODUCTION_SECRET_ENV_KEYS:
        value = source.get(key, "").strip()
        if value:
            raise _safe_error(f"{key} nao deve estar presente em APP_ENV=test")
    if _contains_forbidden_host(database_url):
        raise _safe_error("destino externo proibido")

    try:
        url = make_url(database_url)
    except Exception as exc:
        raise _safe_error("DATABASE_URL invalida") from exc

    drivername = url.drivername.lower()
    if drivername.startswith("sqlite"):
        _validate_sqlite(url.database, run_id)
        return
    if drivername.startswith("postgres"):
        _validate_postgres(url.host, url.database, run_id)
        return
    raise _safe_error("driver nao permitido em testes")
