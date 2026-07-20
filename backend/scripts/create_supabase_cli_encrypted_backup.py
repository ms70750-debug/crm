import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.database_target_guard import guard_if_required  # noqa: E402

BACKUP_FORMAT_VERSION = "supabase-cli-logical-fernet-v1"
DEFAULT_OUTPUT_DIR = Path("backup-artifact")
INCLUDED_SCHEMAS = ("public",)
INTERNAL_SCHEMAS_FILTERED = ("auth", "storage", "vault", "realtime", "extensions")
INTERNAL_FILES = ("roles.sql", "schema.sql", "data.sql", "manifest.json", "checksums.txt")
SUPABASE_CLI_VERSION = "2.109.1"
RETENTION_DAYS = 1

DIAGNOSTIC_CODES = {
    "CLI_NOT_FOUND": "SUPABASE_CLI_NOT_FOUND",
    "ROLES_DUMP_FAILED": "SUPABASE_ROLES_DUMP_FAILED",
    "SCHEMA_DUMP_FAILED": "SUPABASE_SCHEMA_DUMP_FAILED",
    "DATA_DUMP_FAILED": "SUPABASE_DATA_DUMP_FAILED",
    "BACKUP_EMPTY": "SUPABASE_BACKUP_EMPTY",
    "PACKAGE_FAILED": "SUPABASE_PACKAGE_FAILED",
    "ENCRYPTION_FAILED": "BACKUP_ENCRYPTION_FAILED",
    "CHECKSUM_FAILED": "BACKUP_CHECKSUM_FAILED",
    "UPLOAD_FAILED": "BACKUP_UPLOAD_FAILED",
    "UNKNOWN_SAFE_ERROR": "SUPABASE_BACKUP_UNKNOWN_SAFE_ERROR",
}


@dataclass(frozen=True)
class BackupResult:
    encrypted_backup: Path
    manifest: Path
    checksum: Path
    plaintext_removed: bool
    manifest_data: dict


@dataclass
class SafeSupabaseBackupError(RuntimeError):
    category: str
    step: str
    exit_code: int | None = None
    cli_version: str = "unknown"
    completed_steps: tuple[str, ...] = ()

    @property
    def diagnostic_code(self) -> str:
        return DIAGNOSTIC_CODES.get(self.category, DIAGNOSTIC_CODES["UNKNOWN_SAFE_ERROR"])

    def __str__(self) -> str:
        exit_code = "n/a" if self.exit_code is None else str(self.exit_code)
        completed = ",".join(self.completed_steps) if self.completed_steps else "nenhuma"
        return (
            f"BACKUP_DIAGNOSTIC_CODE={self.diagnostic_code}; categoria={self.category}; "
            f"etapa={self.step}; exit_code={exit_code}; supabase_cli_version={self.cli_version}; "
            f"etapas_concluidas={completed}; stderr_bruto=oculto; segredos_expostos=nao"
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
    database_url = (source.get("SUPABASE_DIRECT_URL") or source.get("DIRECT_URL") or "").strip()
    if not database_url:
        raise RuntimeError("SUPABASE_DIRECT_URL ausente.")
    if "[YOUR-PASSWORD]" in database_url:
        raise RuntimeError("SUPABASE_DIRECT_URL ainda contem placeholder.")
    guard_if_required(database_url, source)
    return database_url


def supabase_command() -> str:
    return os.environ.get("SUPABASE_CLI", "supabase")


def safe_completed_process(args: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["SUPABASE_TELEMETRY_DISABLED"] = "1"
    return subprocess.run(args, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env, timeout=timeout)


def supabase_cli_version() -> str:
    command = supabase_command()
    if shutil.which(command) is None:
        return "not_found"
    try:
        result = safe_completed_process([command, "--version"], timeout=30)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return "not_found"
    output = (result.stdout or result.stderr or "").strip()
    return output.splitlines()[-1] if output else "unknown"


def run_supabase_dump(step: str, output_path: Path, flags: list[str], database_url: str, completed_steps: list[str]) -> None:
    command = supabase_command()
    if shutil.which(command) is None:
        raise SafeSupabaseBackupError("CLI_NOT_FOUND", step=step, cli_version="not_found", completed_steps=tuple(completed_steps))

    args = [command, "db", "dump", "--db-url", database_url, "-f", str(output_path), *flags]
    try:
        result = safe_completed_process(args, timeout=300)
    except FileNotFoundError as exc:
        raise SafeSupabaseBackupError("CLI_NOT_FOUND", step=step, cli_version="not_found", completed_steps=tuple(completed_steps)) from exc
    except subprocess.TimeoutExpired as exc:
        raise SafeSupabaseBackupError(step_category(step), step=step, cli_version=supabase_cli_version(), completed_steps=tuple(completed_steps)) from exc

    if result.returncode != 0:
        raise SafeSupabaseBackupError(
            step_category(step),
            step=step,
            exit_code=result.returncode,
            cli_version=supabase_cli_version(),
            completed_steps=tuple(completed_steps),
        )
    if not output_path.exists() or output_path.stat().st_size == 0:
        raise SafeSupabaseBackupError("BACKUP_EMPTY", step=step, cli_version=supabase_cli_version(), completed_steps=tuple(completed_steps))
    completed_steps.append(step)


def step_category(step: str) -> str:
    return {
        "roles": "ROLES_DUMP_FAILED",
        "schema": "SCHEMA_DUMP_FAILED",
        "data": "DATA_DUMP_FAILED",
    }.get(step, "UNKNOWN_SAFE_ERROR")


def latest_postgres_migration() -> str:
    migrations = sorted(Path("backend/migrations/postgres").glob("*.sql"))
    return migrations[-1].name if migrations else "unknown"


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def encrypt_file(source: Path, target: Path, key: bytes) -> None:
    target.write_bytes(Fernet(key).encrypt(source.read_bytes()))


def create_package(package_path: Path, source_dir: Path) -> None:
    required = [source_dir / name for name in INTERNAL_FILES]
    if any(not path.exists() or path.stat().st_size == 0 for path in required):
        raise SafeSupabaseBackupError("PACKAGE_FAILED", step="package")
    with tarfile.open(package_path, "w") as archive:
        for path in required:
            archive.add(path, arcname=path.name)
    if not package_path.exists() or package_path.stat().st_size == 0:
        raise SafeSupabaseBackupError("PACKAGE_FAILED", step="package")


def create_supabase_cli_backup(output_dir: Path = DEFAULT_OUTPUT_DIR, env: dict[str, str] | None = None) -> BackupResult:
    database_url = get_database_url(env)
    key = load_fernet_key(env)
    output_dir.mkdir(parents=True, exist_ok=True)
    completed_steps: list[str] = []

    with tempfile.TemporaryDirectory(prefix="crm-supabase-cli-backup-") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        roles_path = temp_dir / "roles.sql"
        schema_path = temp_dir / "schema.sql"
        data_path = temp_dir / "data.sql"
        internal_manifest_path = temp_dir / "manifest.json"
        internal_checksums_path = temp_dir / "checksums.txt"
        package_path = temp_dir / "crm-supabase-backup.tar"

        encrypted_backup = output_dir / "crm-supabase-backup.tar.enc"
        external_manifest_path = output_dir / "crm-supabase-backup.manifest.json"
        external_checksum_path = output_dir / "crm-supabase-backup.sha256"

        cli_version = supabase_cli_version()
        if cli_version == "not_found":
            raise SafeSupabaseBackupError("CLI_NOT_FOUND", step="preflight", cli_version="not_found")

        run_supabase_dump("roles", roles_path, ["--role-only"], database_url, completed_steps)
        run_supabase_dump("schema", schema_path, ["--schema", INCLUDED_SCHEMAS[0]], database_url, completed_steps)
        run_supabase_dump("data", data_path, ["--schema", INCLUDED_SCHEMAS[0], "--use-copy", "--data-only"], database_url, completed_steps)

        internal_checksums = {
            "roles.sql": sha256_file(roles_path),
            "schema.sql": sha256_file(schema_path),
            "data.sql": sha256_file(data_path),
        }
        internal_manifest = safe_manifest(cli_version, completed_steps, {
            "roles.sql": roles_path.stat().st_size,
            "schema.sql": schema_path.stat().st_size,
            "data.sql": data_path.stat().st_size,
        })
        write_json(internal_manifest_path, internal_manifest)
        internal_checksums["manifest.json"] = sha256_file(internal_manifest_path)
        internal_checksums_path.write_text(
            "".join(f"{digest}  {name}\n" for name, digest in sorted(internal_checksums.items())),
            encoding="utf-8",
        )

        try:
            create_package(package_path, temp_dir)
        except SafeSupabaseBackupError:
            raise
        except Exception as exc:
            raise SafeSupabaseBackupError("PACKAGE_FAILED", step="package", cli_version=cli_version, completed_steps=tuple(completed_steps)) from exc

        try:
            encrypt_file(package_path, encrypted_backup, key)
        except Exception as exc:
            raise SafeSupabaseBackupError("ENCRYPTION_FAILED", step="encrypt", cli_version=cli_version, completed_steps=tuple(completed_steps)) from exc
        if not encrypted_backup.exists() or encrypted_backup.stat().st_size == 0:
            raise SafeSupabaseBackupError("ENCRYPTION_FAILED", step="encrypt", cli_version=cli_version, completed_steps=tuple(completed_steps))

        try:
            encrypted_checksum = sha256_file(encrypted_backup)
            external_manifest = dict(internal_manifest)
            external_manifest["encrypted_backup"] = encrypted_backup.name
            external_manifest["encrypted_size_bytes"] = encrypted_backup.stat().st_size
            external_manifest["encrypted_sha256"] = encrypted_checksum
            write_json(external_manifest_path, external_manifest)
            external_checksum_path.write_text(f"{encrypted_checksum}  {encrypted_backup.name}\n", encoding="utf-8")
        except Exception as exc:
            raise SafeSupabaseBackupError("CHECKSUM_FAILED", step="checksum", cli_version=cli_version, completed_steps=tuple(completed_steps)) from exc

    return BackupResult(
        encrypted_backup=encrypted_backup,
        manifest=external_manifest_path,
        checksum=external_checksum_path,
        plaintext_removed=True,
        manifest_data=external_manifest,
    )


def safe_manifest(cli_version: str, completed_steps: list[str], internal_sizes: dict[str, int]) -> dict:
    return {
        "created_at": datetime.now(UTC).isoformat(),
        "commit": os.environ.get("GITHUB_SHA", "local"),
        "format_version": BACKUP_FORMAT_VERSION,
        "method": "supabase-cli",
        "supabase_cli_version": cli_version,
        "schemas_included": list(INCLUDED_SCHEMAS),
        "internal_schemas_filtered": list(INTERNAL_SCHEMAS_FILTERED),
        "steps_completed": list(completed_steps),
        "internal_files": list(INTERNAL_FILES),
        "internal_sizes_bytes": internal_sizes,
        "encryption": "fernet",
        "checksum": "sha256",
        "latest_migration": latest_postgres_migration(),
        "retention_days": RETENTION_DAYS,
        "restore_order": ["roles.sql", "schema.sql", "data.sql"],
        "restore_instruction": "Decrypt in a temporary directory, validate internal checksums, restore roles, schema, then data with ON_ERROR_STOP.",
        "contains_credentials": False,
        "contains_customer_content": False,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cria backup Supabase CLI criptografado sem expor credenciais.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = create_supabase_cli_backup(args.output_dir)
    print("Backup Supabase CLI criptografado criado com seguranca.")
    print(f"Manifesto: {result.manifest.name}")
    print(f"Arquivo criptografado: {result.encrypted_backup.name}")
    print("Arquivos SQL abertos removidos: sim")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERRO SEGURO: {exc}", file=sys.stderr)
        raise SystemExit(1)
