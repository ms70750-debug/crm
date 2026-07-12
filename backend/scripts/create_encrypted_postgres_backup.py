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


@dataclass(frozen=True)
class BackupResult:
    encrypted_backup: Path
    manifest: Path
    checksums: Path
    plaintext_removed: bool
    manifest_data: dict


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


def collect_metadata(database_url: str) -> dict:
    engine = create_engine(database_url)
    with engine.connect() as conn:
        latest_migration = conn.execute(text(LATEST_MIGRATION_QUERY)).scalar()
        table_count = conn.execute(text(TABLE_COUNT_QUERY)).scalar()
    return {
        "latest_migration": latest_migration or "unknown",
        "table_count": int(table_count or 0),
    }


def run_pg_dump(database_url: str, dump_path: Path) -> None:
    command = [
        "pg_dump",
        "--format=custom",
        "--no-owner",
        "--no-acl",
        "--file",
        str(dump_path),
        database_url,
    ]
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except FileNotFoundError as exc:
        raise RuntimeError("pg_dump nao encontrado no ambiente.") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("pg_dump falhou. Credenciais e detalhes foram ocultados.") from exc


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
            dump_runner(database_url, plaintext_dump)
            if not plaintext_dump.exists() or plaintext_dump.stat().st_size == 0:
                raise RuntimeError("Dump aberto nao foi criado corretamente.")

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
