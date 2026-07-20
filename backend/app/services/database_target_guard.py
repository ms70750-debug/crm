import hmac
import hashlib
from dataclasses import dataclass
from urllib.parse import parse_qs, urlsplit


APPROVED_MESSAGE = "destino aprovado"
DIVERGENT_MESSAGE = "destino divergente"
EXPECTED_FINGERPRINT_ENV = "EXPECTED_DATABASE_TARGET_FINGERPRINT"
GUARD_REQUIRED_ENV = "DATABASE_TARGET_GUARD_REQUIRED"
SAFE_POSTGRES_SCHEMES = {"postgres", "postgresql", "postgresql+psycopg"}
UNSAFE_SSLMODES = {"disable", "allow"}
DEFAULT_POSTGRES_PORT = 5432


class DatabaseTargetGuardError(RuntimeError):
    pass


@dataclass(frozen=True)
class NormalizedDatabaseTarget:
    scheme: str
    username: str
    hostname: str
    port: int
    database: str
    sslmode: str
    environment: str

    def canonical_payload(self) -> str:
        return "|".join(
            [
                f"scheme={self.scheme}",
                f"user={self.username}",
                f"host={self.hostname}",
                f"port={self.port}",
                f"database={self.database}",
                f"sslmode={self.sslmode}",
                f"environment={self.environment}",
            ]
        )


def guard_required(env: dict[str, str]) -> bool:
    return env.get(GUARD_REQUIRED_ENV, "").strip().lower() in {"1", "true", "yes", "sim", "ok"}


def normalize_database_target(database_url: str, *, environment: str = "production") -> NormalizedDatabaseTarget:
    if not database_url:
        raise DatabaseTargetGuardError(DIVERGENT_MESSAGE)
    try:
        parsed = urlsplit(database_url)
        port = parsed.port or DEFAULT_POSTGRES_PORT
    except ValueError as exc:
        raise DatabaseTargetGuardError(DIVERGENT_MESSAGE) from exc

    scheme = parsed.scheme.strip().lower()
    if scheme not in SAFE_POSTGRES_SCHEMES:
        raise DatabaseTargetGuardError(DIVERGENT_MESSAGE)
    hostname = (parsed.hostname or "").strip().lower()
    database = parsed.path.lstrip("/").strip()
    username = (parsed.username or "").strip().lower()
    if not hostname or not database or not username:
        raise DatabaseTargetGuardError(DIVERGENT_MESSAGE)

    sslmode = (parse_qs(parsed.query).get("sslmode", ["require"])[0] or "require").strip().lower()
    if sslmode in UNSAFE_SSLMODES:
        raise DatabaseTargetGuardError(DIVERGENT_MESSAGE)

    return NormalizedDatabaseTarget(
        scheme="postgresql",
        username=username,
        hostname=hostname,
        port=port,
        database=database,
        sslmode=sslmode,
        environment=environment.strip().lower() or "production",
    )


def calculate_database_target_fingerprint(database_url: str, *, environment: str = "production") -> str:
    target = normalize_database_target(database_url, environment=environment)
    return hashlib.sha256(target.canonical_payload().encode("utf-8")).hexdigest()


def validate_database_target(
    database_url: str,
    expected_fingerprint: str,
    *,
    environment: str = "production",
) -> None:
    expected = (expected_fingerprint or "").strip().lower()
    if len(expected) != 64 or any(char not in "0123456789abcdef" for char in expected):
        raise DatabaseTargetGuardError(DIVERGENT_MESSAGE)
    actual = calculate_database_target_fingerprint(database_url, environment=environment)
    if not hmac.compare_digest(actual, expected):
        raise DatabaseTargetGuardError(DIVERGENT_MESSAGE)


def guard_if_required(
    database_url: str,
    env: dict[str, str],
    *,
    environment: str = "production",
) -> None:
    if not guard_required(env):
        return
    validate_database_target(
        database_url,
        env.get(EXPECTED_FINGERPRINT_ENV, ""),
        environment=env.get("APP_ENV", environment),
    )
