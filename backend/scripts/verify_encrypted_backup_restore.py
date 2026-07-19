import argparse
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import create_engine, text

try:
    from create_encrypted_postgres_backup import postgres_client_environment, sha256_file
except ModuleNotFoundError:
    from scripts.create_encrypted_postgres_backup import postgres_client_environment, sha256_file

EXPECTED_TABLES = (
    "admin_bootstrap_tokens",
    "audit_logs",
    "auth_sessions",
    "backup_audit_logs",
    "clientes",
    "consents",
    "leads",
    "propostas",
    "schema_migrations",
    "simulations",
    "tarefas",
    "users",
    "whatsapp_messages",
)
DIRECT_ROLES = ("anon", "authenticated")
VALIDATED_PRIVILEGES = ("SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER")


def pg_restore_binary() -> str:
    return os.environ.get("PG_RESTORE_BIN", "pg_restore")


@dataclass(frozen=True)
class RestoreVerification:
    restored: bool
    plaintext_removed: bool
    table_count: int
    migration_count: int
    index_count: int
    constraint_count: int
    row_counts: dict[str, int]


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_fernet_key() -> bytes:
    key = os.environ.get("BACKUP_ENCRYPTION_KEY", "").strip()
    if not key:
        raise RuntimeError("BACKUP_ENCRYPTION_KEY ausente.")
    try:
        Fernet(key.encode("utf-8"))
    except (ValueError, InvalidToken) as exc:
        raise RuntimeError("BACKUP_ENCRYPTION_KEY invalida.") from exc
    return key.encode("utf-8")


def get_restore_url() -> str:
    restore_url = os.environ.get("POSTGRES_RESTORE_URL", "").strip()
    if not restore_url:
        raise RuntimeError("POSTGRES_RESTORE_URL ausente.")
    if os.environ.get("SUPABASE_DIRECT_URL"):
        raise RuntimeError("SUPABASE_DIRECT_URL nao deve ser usado no teste de restore.")
    return restore_url


def decrypt_backup(encrypted_path: Path, target_path: Path, key: bytes) -> None:
    try:
        target_path.write_bytes(Fernet(key).decrypt(encrypted_path.read_bytes()))
    except InvalidToken as exc:
        raise RuntimeError("Backup criptografado nao pode ser descriptografado com a chave fornecida.") from exc


def ensure_validation_roles(database_url: str) -> None:
    engine = create_engine(database_url)
    with engine.begin() as conn:
        for role in ("anon", "authenticated", "service_role", "backend_app"):
            conn.exec_driver_sql(
                f"""
                DO $$
                BEGIN
                  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{role}') THEN
                    CREATE ROLE {role} NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
                  END IF;
                END
                $$;
                """
            )


def run_pg_restore(database_url: str, dump_path: Path) -> None:
    process_env = postgres_client_environment(database_url)
    command = [
        pg_restore_binary(),
        "--exit-on-error",
        "--no-owner",
        "--dbname",
        process_env["PGDATABASE"],
        str(dump_path),
    ]
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=process_env)
    except FileNotFoundError as exc:
        raise RuntimeError("pg_restore nao encontrado no ambiente.") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("pg_restore falhou. Detalhes sensiveis foram ocultados.") from exc


def table_privileges(conn, role: str, table_name: str) -> set[str]:
    rows = conn.execute(
        text(
            """
            SELECT privilege_type
            FROM information_schema.role_table_grants
            WHERE table_schema = 'public'
              AND grantee = :role
              AND table_name = :table_name
            """
        ),
        {"role": role, "table_name": table_name},
    ).scalars()
    return {str(row) for row in rows}


def public_schema_has_access(conn) -> bool:
    acl = conn.execute(
        text("SELECT COALESCE(nspacl::text, '') FROM pg_namespace WHERE nspname = 'public'")
    ).scalar_one()
    entries = acl.strip("{}").split(",") if acl else []
    return any(entry.startswith("=") for entry in entries)


def validate_restore(database_url: str) -> RestoreVerification:
    engine = create_engine(database_url)
    with engine.connect() as conn:
        tables = {
            str(row)
            for row in conn.execute(
                text(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                      AND table_type = 'BASE TABLE'
                    """
                )
            ).scalars()
        }
        missing = set(EXPECTED_TABLES) - tables
        if missing:
            raise RuntimeError(f"Tabelas ausentes no restore: {sorted(missing)}")

        migration_count = int(conn.execute(text("SELECT COUNT(*) FROM schema_migrations")).scalar() or 0)
        if migration_count < 7:
            raise RuntimeError("Restore incompleto: menos de 7 migrations registradas.")

        index_count = int(
            conn.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM pg_indexes
                    WHERE schemaname = 'public'
                    """
                )
            ).scalar()
            or 0
        )
        constraint_count = int(
            conn.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM information_schema.table_constraints
                    WHERE table_schema = 'public'
                    """
                )
            ).scalar()
            or 0
        )
        if index_count <= 0 or constraint_count <= 0:
            raise RuntimeError("Restore incompleto: indices ou constraints ausentes.")

        for table in ("admin_bootstrap_tokens", "auth_sessions", "audit_logs", "consents", "simulations"):
            if table not in tables:
                raise RuntimeError(f"Componente critico ausente: {table}")

        for role in DIRECT_ROLES:
            for table in EXPECTED_TABLES:
                grants = table_privileges(conn, role, table)
                leaked = grants & set(VALIDATED_PRIVILEGES)
                if leaked:
                    raise RuntimeError(f"{role} possui grants indevidos apos restore em {table}.")

        for table in EXPECTED_TABLES:
            grants = table_privileges(conn, "PUBLIC", table) | table_privileges(conn, "public", table)
            if grants:
                raise RuntimeError(f"PUBLIC possui grants indevidos apos restore em {table}.")
        if public_schema_has_access(conn):
            raise RuntimeError("PUBLIC possui acesso indevido ao schema public apos restore.")

        row_counts = {
            table: int(conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar() or 0)
            for table in EXPECTED_TABLES
        }

    return RestoreVerification(
        restored=True,
        plaintext_removed=False,
        table_count=len(tables),
        migration_count=migration_count,
        index_count=index_count,
        constraint_count=constraint_count,
        row_counts=row_counts,
    )


def verify_encrypted_backup_restore(
    encrypted_backup: Path,
    manifest_path: Path,
    database_url: str | None = None,
    restore_runner: Callable[[str, Path], None] = run_pg_restore,
    role_preparer: Callable[[str], None] = ensure_validation_roles,
) -> RestoreVerification:
    manifest = load_manifest(manifest_path)
    expected_checksum = manifest.get("encrypted_sha256")
    if not expected_checksum or sha256_file(encrypted_backup) != expected_checksum:
        raise RuntimeError("Checksum do backup criptografado diverge do manifesto.")

    key = load_fernet_key()
    restore_url = database_url or get_restore_url()

    with tempfile.TemporaryDirectory(prefix="crm-restore-") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        plaintext_dump = temp_dir / "restore.dump"
        try:
            decrypt_backup(encrypted_backup, plaintext_dump, key)
            if sha256_file(plaintext_dump) != manifest.get("plaintext_sha256"):
                raise RuntimeError("Checksum do dump descriptografado diverge do manifesto.")
            role_preparer(restore_url)
            restore_runner(restore_url, plaintext_dump)
            result = validate_restore(restore_url)
        finally:
            if plaintext_dump.exists():
                plaintext_dump.unlink()

        return RestoreVerification(
            restored=result.restored,
            plaintext_removed=not plaintext_dump.exists(),
            table_count=result.table_count,
            migration_count=result.migration_count,
            index_count=result.index_count,
            constraint_count=result.constraint_count,
            row_counts=result.row_counts,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Valida restore de backup PostgreSQL criptografado.")
    parser.add_argument("--backup", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = verify_encrypted_backup_restore(args.backup, args.manifest)
    print("Restore ficticio validado com seguranca.")
    print(f"Tabelas: {result.table_count}")
    print(f"Migrations: {result.migration_count}")
    print(f"Indices: {result.index_count}")
    print(f"Constraints: {result.constraint_count}")
    print("Dump aberto removido: sim")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERRO SEGURO: {exc}", file=sys.stderr)
        raise SystemExit(1)
