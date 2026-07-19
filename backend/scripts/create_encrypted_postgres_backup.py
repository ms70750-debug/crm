import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable
from urllib.parse import parse_qsl, unquote, urlsplit

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import create_engine, text

BACKUP_FORMAT_VERSION = "postgres-logical-fernet-v1"
DEFAULT_OUTPUT_DIR = Path("backup-artifact")
CRM_DUMP_SCHEMAS = ("public",)
MANAGED_SUPABASE_SCHEMAS = ("auth", "storage", "vault", "realtime", "extensions")
LATEST_MIGRATION_QUERY = """
SELECT version
FROM schema_migrations
ORDER BY applied_at DESC, version DESC
LIMIT 1
"""
TABLE_COUNT_QUERY = """
SELECT COUNT(*)
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_type = 'BASE TABLE'
"""
EXTENSION_METADATA_QUERY = """
SELECT e.extname, e.extversion, n.nspname AS schema_name
FROM pg_extension e
JOIN pg_namespace n ON n.oid = e.extnamespace
ORDER BY e.extname
"""
PG_DUMP_TIMEOUT_SECONDS = 120
MINIMUM_DUMP_FREE_SPACE_BYTES = 32 * 1024 * 1024
SAFE_ERROR_CATEGORIES = {
    "PG_DUMP_NOT_FOUND",
    "PG_DUMP_VERSION_MISMATCH",
    "DNS_FAILED",
    "SSL_FAILED",
    "CONNECTION_FAILED",
    "AUTHENTICATION_FAILED",
    "PERMISSION_DENIED",
    "INVALID_ARGUMENT",
    "OUTPUT_FILE_ERROR",
    "DISK_SPACE_LOW",
    "TIMEOUT",
    "DATABASE_DUMP_ERROR",
    "SCHEMA_PERMISSION_DENIED",
    "TABLE_PERMISSION_DENIED",
    "SEQUENCE_PERMISSION_DENIED",
    "MANAGED_SCHEMA_ERROR",
    "MANAGED_EXTENSION_ERROR",
    "INVALID_DATABASE_OBJECT",
    "ENCRYPTION_FAILED",
    "DRIVER_NOT_AVAILABLE",
    "UNKNOWN_SAFE_ERROR",
}

DIAGNOSTIC_CODES = {
    "PG_DUMP_NOT_FOUND": "PGDUMP_NOT_FOUND",
    "PG_DUMP_VERSION_MISMATCH": "PGDUMP_VERSION_MISMATCH",
    "DNS_FAILED": "PGDUMP_DNS_FAILED",
    "SSL_FAILED": "PGDUMP_SSL_FAILED",
    "CONNECTION_FAILED": "PGDUMP_CONNECTION_FAILED",
    "AUTHENTICATION_FAILED": "PGDUMP_AUTHENTICATION_FAILED",
    "PERMISSION_DENIED": "PGDUMP_PERMISSION_DENIED",
    "INVALID_ARGUMENT": "PGDUMP_INVALID_ARGUMENT",
    "OUTPUT_FILE_ERROR": "PGDUMP_OUTPUT_FILE_ERROR",
    "DISK_SPACE_LOW": "PGDUMP_DISK_SPACE_LOW",
    "TIMEOUT": "PGDUMP_TIMEOUT",
    "DATABASE_DUMP_ERROR": "PGDUMP_DATABASE_DUMP_ERROR",
    "SCHEMA_PERMISSION_DENIED": "PGDUMP_SCHEMA_PERMISSION_DENIED",
    "TABLE_PERMISSION_DENIED": "PGDUMP_TABLE_PERMISSION_DENIED",
    "SEQUENCE_PERMISSION_DENIED": "PGDUMP_SEQUENCE_PERMISSION_DENIED",
    "MANAGED_SCHEMA_ERROR": "PGDUMP_MANAGED_SCHEMA_ERROR",
    "MANAGED_EXTENSION_ERROR": "PGDUMP_MANAGED_EXTENSION_ERROR",
    "INVALID_DATABASE_OBJECT": "PGDUMP_INVALID_DATABASE_OBJECT",
    "DRIVER_NOT_AVAILABLE": "PGDUMP_DRIVER_NOT_AVAILABLE",
    "ENCRYPTION_FAILED": "BACKUP_ENCRYPTION_FAILED",
    "UNKNOWN_SAFE_ERROR": "PGDUMP_UNKNOWN_SAFE_ERROR",
}


@dataclass(frozen=True)
class BackupResult:
    encrypted_backup: Path
    manifest: Path
    checksums: Path
    plaintext_removed: bool
    manifest_data: dict


@dataclass(frozen=True)
class SafePgDumpError(RuntimeError):
    category: str
    step: str
    exit_code: int | None = None
    pg_dump_version: str = "unknown"
    recommendation: str = "Revise a configuracao segura do workflow e tente novamente."
    binary_found: bool | None = None
    output_created: bool | None = None
    output_nonempty: bool | None = None
    encryption_started: bool = False
    upload_started: bool = False
    sqlstate: str = "indisponivel"
    object_type: str = "indisponivel"
    schema: str = "indisponivel"
    error_class: str = "indisponivel"

    @property
    def diagnostic_code(self) -> str:
        return DIAGNOSTIC_CODES.get(self.category, DIAGNOSTIC_CODES["UNKNOWN_SAFE_ERROR"])

    def __str__(self) -> str:
        exit_code = "n/a" if self.exit_code is None else str(self.exit_code)
        binary_found = "desconhecido" if self.binary_found is None else ("sim" if self.binary_found else "nao")
        output_created = "desconhecido" if self.output_created is None else ("sim" if self.output_created else "nao")
        output_nonempty = "desconhecido" if self.output_nonempty is None else ("sim" if self.output_nonempty else "nao")
        return (
            f"BACKUP_DIAGNOSTIC_CODE={self.diagnostic_code}; categoria={self.category}; "
            f"etapa={self.step}; exit_code={exit_code}; pg_dump_version={self.pg_dump_version}; "
            f"pg_dump_encontrado={binary_found}; arquivo_saida_criado={output_created}; "
            f"arquivo_saida_nao_vazio={output_nonempty}; "
            f"criptografia_iniciada={'sim' if self.encryption_started else 'nao'}; "
            f"upload_iniciado={'sim' if self.upload_started else 'nao'}; "
            f"sqlstate={self.sqlstate}; tipo_objeto={self.object_type}; "
            f"schema={self.schema}; classe_erro={self.error_class}; "
            f"recomendacao={self.recommendation}"
        )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_fernet_key(env: dict[str, str] | None = None) -> bytes:
    source = env if env is not None else os.environ
    key = source.get("BACKUP_ENCRYPTION_KEY", "").strip()
    if not key:
        raise RuntimeError("BACKUP_ENCRYPTION_KEY ausente.")
    try:
        Fernet(key.encode("utf-8"))
    except (ValueError, InvalidToken) as exc:
        raise RuntimeError("BACKUP_ENCRYPTION_KEY invalida.") from exc
    return key.encode("utf-8")


def get_database_url(env: dict[str, str] | None = None) -> str:
    source = env if env is not None else os.environ
    database_url = (
        source.get("DIRECT_URL")
        or source.get("POSTGRES_DIRECT_URL")
        or source.get("SUPABASE_DIRECT_URL")
        or ""
    ).strip()
    if not database_url:
        raise RuntimeError("URL do banco ausente.")
    if "[YOUR-PASSWORD]" in database_url:
        raise RuntimeError("URL do banco ainda contem placeholder.")
    return database_url


def sqlalchemy_database_url(database_url: str) -> str:
    if database_url.startswith("postgresql+psycopg://"):
        return database_url
    if database_url.startswith("postgresql://"):
        return "postgresql+psycopg://" + database_url.removeprefix("postgresql://")
    if database_url.startswith("postgres://"):
        return "postgresql+psycopg://" + database_url.removeprefix("postgres://")
    return database_url


def postgres_client_database_url(database_url: str) -> str:
    if database_url.startswith("postgresql+psycopg://"):
        return "postgresql://" + database_url.removeprefix("postgresql+psycopg://")
    if database_url.startswith("postgresql+psycopg2://"):
        return "postgresql://" + database_url.removeprefix("postgresql+psycopg2://")
    if database_url.startswith("postgres://"):
        return "postgresql://" + database_url.removeprefix("postgres://")
    return database_url


def postgres_client_environment(database_url: str, base_env: dict[str, str] | None = None) -> dict[str, str]:
    native_url = postgres_client_database_url(database_url)
    parsed = urlsplit(native_url)
    if parsed.scheme not in {"postgresql", "postgres"} or not parsed.hostname:
        raise SafePgDumpError(
            "INVALID_ARGUMENT",
            step="client-env",
            pg_dump_version=pg_dump_version(),
            recommendation=safe_recommendation("INVALID_ARGUMENT"),
            binary_found=True,
        )
    database = unquote(parsed.path.lstrip("/"))
    if not database:
        raise SafePgDumpError(
            "INVALID_ARGUMENT",
            step="client-env",
            pg_dump_version=pg_dump_version(),
            recommendation=safe_recommendation("INVALID_ARGUMENT"),
            binary_found=True,
        )
    env = (base_env or os.environ).copy()
    env["PGHOST"] = parsed.hostname
    env["PGPORT"] = str(parsed.port or 5432)
    env["PGUSER"] = unquote(parsed.username or "")
    if parsed.password is not None:
        env["PGPASSWORD"] = unquote(parsed.password)
    env["PGDATABASE"] = database
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if query.get("sslmode"):
        env["PGSSLMODE"] = query["sslmode"]
    return env


def safe_completed_process(args: list[str], env: dict[str, str] | None = None, timeout: int = 15) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(args, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env, timeout=timeout)
    except FileNotFoundError as exc:
        raise SafePgDumpError("PG_DUMP_NOT_FOUND", step=args[0]) from exc
    except subprocess.TimeoutExpired as exc:
        raise SafePgDumpError("TIMEOUT", step=args[0]) from exc


def pg_dump_binary() -> str:
    return os.environ.get("PG_DUMP_BIN", "pg_dump")


def pg_dump_version() -> str:
    try:
        result = safe_completed_process([pg_dump_binary(), "--version"], timeout=10)
    except SafePgDumpError:
        return "not_found"
    output = (result.stdout or result.stderr or "").strip()
    return output or "unknown"


def pg_dump_major(version_text: str) -> int | None:
    for token in version_text.replace("(", " ").replace(")", " ").split():
        numeric = token.split(".")[0]
        if numeric.isdigit():
            return int(numeric)
    return None


def sanitize_identifier(identifier: str | None) -> str:
    if not identifier:
        return "indisponivel"
    cleaned = identifier.strip().strip('"').strip("'").lower()
    if cleaned in {*CRM_DUMP_SCHEMAS, *MANAGED_SUPABASE_SCHEMAS}:
        return cleaned
    if cleaned.replace("_", "").isalnum() and len(cleaned) <= 63:
        return "identificador_sanitizado"
    return "indisponivel"


def safe_pg_dump_details(stderr: str) -> dict[str, str]:
    normalized = stderr.lower()
    sqlstate = "indisponivel"
    for token in normalized.replace("(", " ").replace(")", " ").replace(":", " ").split():
        if len(token) == 5 and token.isalnum() and any(char.isdigit() for char in token):
            sqlstate = token.upper()
            break

    schema = "indisponivel"
    for marker in ("schema ", "schema \""):
        if marker in normalized:
            candidate = normalized.split(marker, 1)[1].split()[0]
            schema = sanitize_identifier(candidate)
            break

    object_type = "indisponivel"
    if "permission denied for schema" in normalized:
        object_type = "schema"
    elif "permission denied for table" in normalized:
        object_type = "table"
    elif "permission denied for sequence" in normalized:
        object_type = "sequence"
    elif "extension" in normalized:
        object_type = "extension"
    elif "function" in normalized:
        object_type = "function"
    elif "trigger" in normalized:
        object_type = "trigger"

    error_class = "database_dump_error"
    if "permission denied" in normalized:
        error_class = "permission_denied"
    elif "does not exist" in normalized or "could not find" in normalized or "invalid" in normalized:
        error_class = "invalid_object"
    elif "timeout" in normalized or "timed out" in normalized:
        error_class = "timeout"
    elif "extension" in normalized:
        error_class = "managed_extension"

    return {
        "sqlstate": sqlstate,
        "object_type": object_type,
        "schema": schema,
        "error_class": error_class,
    }


def safe_server_major(database_url: str) -> int | None:
    try:
        engine = create_engine(sqlalchemy_database_url(database_url))
        with engine.connect() as conn:
            version_num = conn.execute(text("SHOW server_version_num")).scalar()
    except ModuleNotFoundError as exc:
        raise SafePgDumpError(
            "DRIVER_NOT_AVAILABLE",
            step="preflight",
            pg_dump_version=pg_dump_version(),
            recommendation=safe_recommendation("DRIVER_NOT_AVAILABLE"),
        ) from exc
    except Exception as exc:
        category = classify_pg_dump_error(str(exc), None)
        raise SafePgDumpError(
            category,
            step="preflight",
            pg_dump_version=pg_dump_version(),
            recommendation=safe_recommendation(category),
        ) from exc
    if not version_num:
        return None
    return int(str(version_num)) // 10000


def classify_pg_dump_error(stderr: str, exit_code: int | None) -> str:
    normalized = stderr.lower()
    details = safe_pg_dump_details(stderr)
    if "server version" in normalized and "pg_dump version" in normalized:
        return "PG_DUMP_VERSION_MISMATCH"
    if "could not translate host name" in normalized or "temporary failure in name resolution" in normalized:
        return "DNS_FAILED"
    if "ssl" in normalized and (
        "certificate" in normalized
        or "tls" in normalized
        or "sslmode" in normalized
        or "ssl error" in normalized
        or "server does not support ssl" in normalized
    ):
        return "SSL_FAILED"
    if "authentication failed" in normalized or "password authentication failed" in normalized:
        return "AUTHENTICATION_FAILED"
    if "permission denied for schema" in normalized:
        if details["schema"] in MANAGED_SUPABASE_SCHEMAS:
            return "MANAGED_SCHEMA_ERROR"
        return "SCHEMA_PERMISSION_DENIED"
    if "permission denied for table" in normalized:
        return "TABLE_PERMISSION_DENIED"
    if "permission denied for sequence" in normalized:
        return "SEQUENCE_PERMISSION_DENIED"
    if "permission denied" in normalized or "must be owner" in normalized or "permission for" in normalized:
        return "PERMISSION_DENIED"
    if "could not translate host name" in normalized or "could not connect" in normalized or "connection refused" in normalized:
        return "CONNECTION_FAILED"
    if "unrecognized option" in normalized or "invalid option" in normalized or "too many command-line arguments" in normalized:
        return "INVALID_ARGUMENT"
    output_error_markers = (
        "could not open output file",
        "could not open file",
        "could not create file",
        "could not write to output file",
        "error opening output file",
        "is a directory",
    )
    if any(marker in normalized for marker in output_error_markers):
        return "OUTPUT_FILE_ERROR"
    if "extension" in normalized and details["schema"] in MANAGED_SUPABASE_SCHEMAS:
        return "MANAGED_EXTENSION_ERROR"
    if "does not exist" in normalized or "could not find" in normalized or "invalid" in normalized:
        return "INVALID_DATABASE_OBJECT"
    if exit_code:
        return "DATABASE_DUMP_ERROR"
    return "UNKNOWN_SAFE_ERROR"


def safe_recommendation(category: str) -> str:
    return {
        "PG_DUMP_NOT_FOUND": "Instale o cliente PostgreSQL antes do backup.",
        "PG_DUMP_VERSION_MISMATCH": "Use pg_dump com versao principal igual ou superior ao servidor.",
        "DNS_FAILED": "Confira resolucao DNS e rede sem expor host ou URL.",
        "SSL_FAILED": "Confira requisitos de SSL sem expor parametros ou host.",
        "CONNECTION_FAILED": "Confira rede, allowlist e disponibilidade do banco sem expor a URL.",
        "AUTHENTICATION_FAILED": "Revise o secret SUPABASE_DIRECT_URL sem copiar o valor para logs.",
        "PERMISSION_DENIED": "Revise permissoes do usuario de backup sem ampliar acesso do frontend.",
        "INVALID_ARGUMENT": "Revise argumentos seguros do pg_dump.",
        "OUTPUT_FILE_ERROR": "Revise diretorio temporario e permissoes de escrita do runner.",
        "DISK_SPACE_LOW": "Libere espaco no runner antes de gerar novo dump.",
        "TIMEOUT": "Tente novamente e avalie tamanho do banco ou timeout operacional.",
        "DATABASE_DUMP_ERROR": "Revise objetos e extensoes do banco com logs sanitizados.",
        "SCHEMA_PERMISSION_DENIED": "Revise permissao de USAGE no schema do CRM ou limite o dump ao schema exportavel.",
        "TABLE_PERMISSION_DENIED": "Revise permissao SELECT da tabela essencial do CRM sem ampliar acesso do frontend.",
        "SEQUENCE_PERMISSION_DENIED": "Revise permissao USAGE/SELECT em sequencias do CRM.",
        "MANAGED_SCHEMA_ERROR": "Exporte explicitamente apenas schemas do CRM e deixe schemas gerenciados para o provedor.",
        "MANAGED_EXTENSION_ERROR": "Documente a extensao gerenciada no manifesto e nao exporte objetos internos do provedor.",
        "INVALID_DATABASE_OBJECT": "Revise objeto invalido ou referencia quebrada com diagnostico sanitizado.",
        "DRIVER_NOT_AVAILABLE": "Use o driver psycopg 3 ja previsto no projeto para conexoes SQLAlchemy.",
        "ENCRYPTION_FAILED": "Revise a etapa de criptografia com dados ficticios antes de nova tentativa.",
    }.get(category, "Revise a falha com logs sanitizados e sem secrets.")


def output_status(path: Path) -> tuple[bool, bool]:
    if not path.exists() or path.is_dir():
        return False, False
    return True, path.stat().st_size > 0


def prepare_dump_path(dump_path: Path) -> Path:
    absolute_dump_path = dump_path.resolve()
    if absolute_dump_path.exists() and absolute_dump_path.is_dir():
        raise SafePgDumpError(
            "OUTPUT_FILE_ERROR",
            step="prepare-output",
            pg_dump_version=pg_dump_version(),
            recommendation=safe_recommendation("OUTPUT_FILE_ERROR"),
            binary_found=True,
            output_created=False,
            output_nonempty=False,
        )
    try:
        absolute_dump_path.parent.mkdir(parents=True, exist_ok=True)
        if not absolute_dump_path.parent.is_dir():
            raise OSError("output parent is not a directory")
        probe_path = absolute_dump_path.parent / f".{absolute_dump_path.name}.write-test"
        probe_path.write_bytes(b"ok")
        probe_path.unlink(missing_ok=True)
    except OSError as exc:
        raise SafePgDumpError(
            "OUTPUT_FILE_ERROR",
            step="prepare-output",
            pg_dump_version=pg_dump_version(),
            recommendation=safe_recommendation("OUTPUT_FILE_ERROR"),
            binary_found=True,
            output_created=False,
            output_nonempty=False,
        ) from exc

    try:
        free_bytes = shutil.disk_usage(absolute_dump_path.parent).free
    except OSError as exc:
        raise SafePgDumpError(
            "OUTPUT_FILE_ERROR",
            step="prepare-output",
            pg_dump_version=pg_dump_version(),
            recommendation=safe_recommendation("OUTPUT_FILE_ERROR"),
            binary_found=True,
            output_created=False,
            output_nonempty=False,
        ) from exc
    if free_bytes < MINIMUM_DUMP_FREE_SPACE_BYTES:
        raise SafePgDumpError(
            "DISK_SPACE_LOW",
            step="prepare-output",
            pg_dump_version=pg_dump_version(),
            recommendation=safe_recommendation("DISK_SPACE_LOW"),
            binary_found=True,
            output_created=False,
            output_nonempty=False,
        )
    return absolute_dump_path


def collect_metadata(database_url: str) -> dict:
    try:
        engine = create_engine(sqlalchemy_database_url(database_url))
        with engine.connect() as conn:
            latest_migration = conn.execute(text(LATEST_MIGRATION_QUERY)).scalar()
            table_count = conn.execute(text(TABLE_COUNT_QUERY)).scalar()
            server_major = safe_server_major(database_url)
            extensions = [
                {
                    "name": row[0],
                    "version": row[1],
                    "schema": sanitize_identifier(row[2]),
                    "managed_by_provider": sanitize_identifier(row[2]) in MANAGED_SUPABASE_SCHEMAS,
                }
                for row in conn.execute(text(EXTENSION_METADATA_QUERY)).fetchall()
            ]
    except SafePgDumpError:
        raise
    except Exception as exc:
        category = classify_pg_dump_error(str(exc), None)
        raise SafePgDumpError(
            category,
            step="metadata",
            pg_dump_version=pg_dump_version(),
            recommendation=safe_recommendation(category),
        ) from exc
    return {
        "latest_migration": latest_migration or "unknown",
        "table_count": int(table_count or 0),
        "server_major": server_major,
        "extensions": extensions,
    }


def run_pg_dump(database_url: str, dump_path: Path, timeout: int = PG_DUMP_TIMEOUT_SECONDS) -> None:
    dump_path = prepare_dump_path(dump_path)
    command = [
        pg_dump_binary(),
        "--format=custom",
        "--no-owner",
        "--no-privileges",
        "--schema",
        CRM_DUMP_SCHEMAS[0],
        "--file",
        str(dump_path),
    ]
    process_env = postgres_client_environment(database_url)
    command.extend(["--dbname", process_env["PGDATABASE"]])
    try:
        result = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=process_env,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise SafePgDumpError(
            "PG_DUMP_NOT_FOUND",
            step="pg_dump",
            pg_dump_version="not_found",
            recommendation=safe_recommendation("PG_DUMP_NOT_FOUND"),
            binary_found=False,
            output_created=False,
            output_nonempty=False,
        ) from exc
    except subprocess.TimeoutExpired as exc:
        output_created, output_nonempty = output_status(dump_path)
        raise SafePgDumpError(
            "TIMEOUT",
            step="pg_dump",
            pg_dump_version=pg_dump_version(),
            recommendation=safe_recommendation("TIMEOUT"),
            binary_found=True,
            output_created=output_created,
            output_nonempty=output_nonempty,
        ) from exc
    if result.returncode != 0:
        stderr = result.stderr or ""
        category = classify_pg_dump_error(stderr, result.returncode)
        details = safe_pg_dump_details(stderr)
        output_created, output_nonempty = output_status(dump_path)
        raise SafePgDumpError(
            category,
            step="pg_dump",
            exit_code=result.returncode,
            pg_dump_version=pg_dump_version(),
            recommendation=safe_recommendation(category),
            binary_found=True,
            output_created=output_created,
            output_nonempty=output_nonempty,
            sqlstate=details["sqlstate"],
            object_type=details["object_type"],
            schema=details["schema"],
            error_class=details["error_class"],
        )
    output_created, output_nonempty = output_status(dump_path)
    if not output_created or not output_nonempty:
        raise SafePgDumpError(
            "OUTPUT_FILE_ERROR",
            step="validate-output",
            pg_dump_version=pg_dump_version(),
            recommendation=safe_recommendation("OUTPUT_FILE_ERROR"),
            binary_found=True,
            output_created=output_created,
            output_nonempty=output_nonempty,
        )


def backup_preflight(database_url: str) -> dict:
    version = pg_dump_version()
    dump_major = pg_dump_major(version)
    server_major = safe_server_major(database_url)
    compatible = bool(dump_major and server_major and dump_major >= server_major)
    return {
        "pg_dump_installed": version != "not_found",
        "pg_dump_major": dump_major,
        "server_major": server_major,
        "compatible": compatible,
    }


def encrypt_file(source: Path, target: Path, key: bytes) -> None:
    encrypted = Fernet(key).encrypt(source.read_bytes())
    target.write_bytes(encrypted)


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def create_encrypted_backup(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    env: dict[str, str] | None = None,
    dump_runner: Callable[[str, Path], None] = run_pg_dump,
    metadata_loader: Callable[[str], dict] = collect_metadata,
    preflight_loader: Callable[[str], dict] = backup_preflight,
) -> BackupResult:
    database_url = get_database_url(env)
    key = load_fernet_key(env)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="crm-backup-") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        plaintext_dump = temp_dir / f"crm-{timestamp}.dump"
        encrypted_backup = output_dir / f"crm-{timestamp}.dump.enc"
        manifest_path = output_dir / f"crm-{timestamp}.manifest.json"
        checksums_path = output_dir / f"crm-{timestamp}.sha256"

        try:
            preflight = preflight_loader(database_url)
            if not preflight["pg_dump_installed"]:
                raise SafePgDumpError(
                    "PG_DUMP_NOT_FOUND",
                    step="preflight",
                    pg_dump_version="not_found",
                    recommendation=safe_recommendation("PG_DUMP_NOT_FOUND"),
                )
            if not preflight["compatible"]:
                raise SafePgDumpError(
                    "PG_DUMP_VERSION_MISMATCH",
                    step="preflight",
                    pg_dump_version=str(preflight["pg_dump_major"] or "unknown"),
                    recommendation=safe_recommendation("PG_DUMP_VERSION_MISMATCH"),
                )
            dump_runner(database_url, plaintext_dump)
            if not plaintext_dump.exists() or plaintext_dump.stat().st_size == 0:
                raise SafePgDumpError(
                    "OUTPUT_FILE_ERROR",
                    step="validate-output",
                    pg_dump_version=pg_dump_version(),
                    recommendation=safe_recommendation("OUTPUT_FILE_ERROR"),
                    binary_found=True,
                    output_created=plaintext_dump.exists(),
                    output_nonempty=plaintext_dump.exists() and plaintext_dump.stat().st_size > 0,
                )

            metadata = metadata_loader(database_url)
            plaintext_checksum = sha256_file(plaintext_dump)
            plaintext_size = plaintext_dump.stat().st_size
            try:
                encrypt_file(plaintext_dump, encrypted_backup, key)
            except Exception as exc:
                output_created, output_nonempty = output_status(plaintext_dump)
                raise SafePgDumpError(
                    "ENCRYPTION_FAILED",
                    step="encrypt",
                    pg_dump_version=str(preflight.get("pg_dump_major") or "unknown"),
                    recommendation=safe_recommendation("ENCRYPTION_FAILED"),
                    binary_found=bool(preflight.get("pg_dump_installed")),
                    output_created=output_created,
                    output_nonempty=output_nonempty,
                    encryption_started=True,
                ) from exc
            encrypted_checksum = sha256_file(encrypted_backup)

            manifest = {
                "created_at": datetime.now(UTC).isoformat(),
                "format_version": BACKUP_FORMAT_VERSION,
                "encrypted_backup": encrypted_backup.name,
                "plaintext_size_bytes": plaintext_size,
                "encrypted_size_bytes": encrypted_backup.stat().st_size,
                "plaintext_sha256": plaintext_checksum,
                "encrypted_sha256": encrypted_checksum,
                "latest_migration": metadata.get("latest_migration", "unknown"),
                "table_count": int(metadata.get("table_count", 0)),
                "server_major": metadata.get("server_major"),
                "pg_dump_major": preflight.get("pg_dump_major"),
                "dump_schemas": list(CRM_DUMP_SCHEMAS),
                "managed_schemas_excluded": list(MANAGED_SUPABASE_SCHEMAS),
                "extensions": metadata.get("extensions", []),
                "restore_notes": [
                    "Dump contem objetos e dados do schema public do CRM.",
                    "Schemas gerenciados do Supabase devem ser recriados pelo provedor.",
                    "Validar restauracao em PostgreSQL isolado antes de qualquer uso real.",
                ],
                "storage_provider": "not_configured",
                "contains_credentials": False,
                "contains_customer_content": False,
            }
            write_json(manifest_path, manifest)
            checksums_path.write_text(
                f"{encrypted_checksum}  {encrypted_backup.name}\n"
                f"{sha256_file(manifest_path)}  {manifest_path.name}\n",
                encoding="utf-8",
            )
        finally:
            if plaintext_dump.exists():
                plaintext_dump.unlink()

        return BackupResult(
            encrypted_backup=encrypted_backup,
            manifest=manifest_path,
            checksums=checksums_path,
            plaintext_removed=not plaintext_dump.exists(),
            manifest_data=manifest,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cria backup PostgreSQL criptografado sem expor credenciais.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = create_encrypted_backup(args.output_dir)
    print("Backup criptografado criado com seguranca.")
    print(f"Manifesto: {result.manifest.name}")
    print(f"Arquivo criptografado: {result.encrypted_backup.name}")
    print("Dump aberto removido: sim")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERRO SEGURO: {exc}", file=sys.stderr)
        raise SystemExit(1)
