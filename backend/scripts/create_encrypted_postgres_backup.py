import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import create_engine, text

BACKUP_FORMAT_VERSION = "postgres-logical-fernet-v1"
DEFAULT_OUTPUT_DIR = Path("backup-artifact")
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
PG_DUMP_TIMEOUT_SECONDS = 120
SAFE_ERROR_CATEGORIES = {
    "PG_DUMP_NOT_FOUND",
    "PG_DUMP_VERSION_MISMATCH",
    "CONNECTION_FAILED",
    "AUTHENTICATION_FAILED",
    "PERMISSION_DENIED",
    "INVALID_ARGUMENT",
    "OUTPUT_FILE_ERROR",
    "TIMEOUT",
    "DATABASE_DUMP_ERROR",
    "UNKNOWN_SAFE_ERROR",
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

    def __str__(self) -> str:
        exit_code = "n/a" if self.exit_code is None else str(self.exit_code)
        return (
            f"{self.category}: etapa={self.step}; exit_code={exit_code}; "
            f"pg_dump_version={self.pg_dump_version}; recomendacao={self.recommendation}"
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


def safe_completed_process(args: list[str], env: dict[str, str] | None = None, timeout: int = 15) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(args, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env, timeout=timeout)
    except FileNotFoundError as exc:
        raise SafePgDumpError("PG_DUMP_NOT_FOUND", step=args[0]) from exc
    except subprocess.TimeoutExpired as exc:
        raise SafePgDumpError("TIMEOUT", step=args[0]) from exc


def pg_dump_version() -> str:
    try:
        result = safe_completed_process(["pg_dump", "--version"], timeout=10)
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


def safe_server_major(database_url: str) -> int | None:
    engine = create_engine(database_url)
    with engine.connect() as conn:
        version_num = conn.execute(text("SHOW server_version_num")).scalar()
    if not version_num:
        return None
    return int(str(version_num)) // 10000


def classify_pg_dump_error(stderr: str, exit_code: int | None) -> str:
    normalized = stderr.lower()
    if "server version" in normalized and "pg_dump version" in normalized:
        return "PG_DUMP_VERSION_MISMATCH"
    if "authentication failed" in normalized or "password authentication failed" in normalized:
        return "AUTHENTICATION_FAILED"
    if "permission denied" in normalized or "must be owner" in normalized or "permission for" in normalized:
        return "PERMISSION_DENIED"
    if "could not translate host name" in normalized or "could not connect" in normalized or "connection refused" in normalized:
        return "CONNECTION_FAILED"
    if "unrecognized option" in normalized or "invalid option" in normalized or "too many command-line arguments" in normalized:
        return "INVALID_ARGUMENT"
    if "could not open output file" in normalized or "no such file or directory" in normalized or "is a directory" in normalized:
        return "OUTPUT_FILE_ERROR"
    if exit_code:
        return "DATABASE_DUMP_ERROR"
    return "UNKNOWN_SAFE_ERROR"


def safe_recommendation(category: str) -> str:
    return {
        "PG_DUMP_NOT_FOUND": "Instale o cliente PostgreSQL antes do backup.",
        "PG_DUMP_VERSION_MISMATCH": "Use pg_dump com versao principal igual ou superior ao servidor.",
        "CONNECTION_FAILED": "Confira rede, allowlist e disponibilidade do banco sem expor a URL.",
        "AUTHENTICATION_FAILED": "Revise o secret SUPABASE_DIRECT_URL sem copiar o valor para logs.",
        "PERMISSION_DENIED": "Revise permissoes do usuario de backup sem ampliar acesso do frontend.",
        "INVALID_ARGUMENT": "Revise argumentos seguros do pg_dump.",
        "OUTPUT_FILE_ERROR": "Revise diretorio temporario e permissoes de escrita do runner.",
        "TIMEOUT": "Tente novamente e avalie tamanho do banco ou timeout operacional.",
        "DATABASE_DUMP_ERROR": "Revise objetos e extensoes do banco com logs sanitizados.",
    }.get(category, "Revise a falha com logs sanitizados e sem secrets.")


def collect_metadata(database_url: str) -> dict:
    engine = create_engine(database_url)
    with engine.connect() as conn:
        latest_migration = conn.execute(text(LATEST_MIGRATION_QUERY)).scalar()
        table_count = conn.execute(text(TABLE_COUNT_QUERY)).scalar()
        server_major = safe_server_major(database_url)
    return {
        "latest_migration": latest_migration or "unknown",
        "table_count": int(table_count or 0),
        "server_major": server_major,
    }


def run_pg_dump(database_url: str, dump_path: Path, timeout: int = PG_DUMP_TIMEOUT_SECONDS) -> None:
    if dump_path.exists() and dump_path.is_dir():
        raise SafePgDumpError(
            "OUTPUT_FILE_ERROR",
            step="pg_dump",
            pg_dump_version=pg_dump_version(),
            recommendation=safe_recommendation("OUTPUT_FILE_ERROR"),
        )
    dump_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "pg_dump",
        "--format=custom",
        "--no-owner",
        "--no-acl",
        "--file",
        str(dump_path),
    ]
    process_env = os.environ.copy()
    process_env["PGDATABASE"] = database_url
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
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise SafePgDumpError(
            "TIMEOUT",
            step="pg_dump",
            pg_dump_version=pg_dump_version(),
            recommendation=safe_recommendation("TIMEOUT"),
        ) from exc
    if result.returncode != 0:
        category = classify_pg_dump_error(result.stderr or "", result.returncode)
        raise SafePgDumpError(
            category,
            step="pg_dump",
            exit_code=result.returncode,
            pg_dump_version=pg_dump_version(),
            recommendation=safe_recommendation(category),
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
                )

            metadata = metadata_loader(database_url)
            plaintext_checksum = sha256_file(plaintext_dump)
            plaintext_size = plaintext_dump.stat().st_size
            encrypt_file(plaintext_dump, encrypted_backup, key)
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
