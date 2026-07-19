import json
from pathlib import Path
from subprocess import CompletedProcess, TimeoutExpired

import pytest
from cryptography.fernet import Fernet

from scripts import create_encrypted_postgres_backup as backup
from scripts import verify_encrypted_backup_restore as restore


WORKFLOWS_DIR = Path(__file__).resolve().parents[2] / ".github" / "workflows"
ENCRYPTED_BACKUP_WORKFLOW_PATH = WORKFLOWS_DIR / "supabase-encrypted-backup.yml"


def _env(key: bytes, database_url: str = "postgresql://user:pass@example.test:5432/db") -> dict[str, str]:
    return {
        "BACKUP_ENCRYPTION_KEY": key.decode("utf-8"),
        "DIRECT_URL": database_url,
    }


def _dump_runner(_: str, dump_path: Path) -> None:
    dump_path.write_bytes(b"PGDMP ficticio sem dados pessoais")


def _metadata_loader(_: str) -> dict:
    return {
        "latest_migration": "2026_07_12_backend_only_permissions.sql",
        "table_count": 13,
        "server_major": 16,
        "extensions": [{"name": "pgcrypto", "version": "1.3", "schema": "extensions", "managed_by_provider": True}],
    }


def _preflight_loader(_: str) -> dict:
    return {
        "pg_dump_installed": True,
        "pg_dump_major": 16,
        "server_major": 16,
        "compatible": True,
    }


def test_create_encrypted_backup_creates_safe_artifacts_and_removes_plaintext(tmp_path: Path) -> None:
    key = Fernet.generate_key()

    result = backup.create_encrypted_backup(
        output_dir=tmp_path,
        env=_env(key),
        dump_runner=_dump_runner,
        metadata_loader=_metadata_loader,
        preflight_loader=_preflight_loader,
    )

    assert result.encrypted_backup.exists()
    assert result.manifest.exists()
    assert result.checksums.exists()
    assert result.plaintext_removed is True
    assert not list(tmp_path.glob("*.dump"))

    manifest = json.loads(result.manifest.read_text(encoding="utf-8"))
    assert manifest["format_version"] == backup.BACKUP_FORMAT_VERSION
    assert manifest["latest_migration"] == "2026_07_12_backend_only_permissions.sql"
    assert manifest["table_count"] == 13
    assert manifest["dump_schemas"] == ["public"]
    assert "auth" in manifest["managed_schemas_excluded"]
    assert manifest["extensions"][0]["name"] == "pgcrypto"
    assert manifest["extensions"][0]["managed_by_provider"] is True
    assert manifest["contains_credentials"] is False
    assert manifest["contains_customer_content"] is False
    assert "postgresql://" not in result.manifest.read_text(encoding="utf-8")
    assert "pass@example" not in result.manifest.read_text(encoding="utf-8")

    decrypted = Fernet(key).decrypt(result.encrypted_backup.read_bytes())
    assert decrypted == b"PGDMP ficticio sem dados pessoais"


def test_create_encrypted_backup_fails_without_key(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="BACKUP_ENCRYPTION_KEY ausente"):
        backup.create_encrypted_backup(
            output_dir=tmp_path,
            env={"DIRECT_URL": "postgresql://user:pass@example.test/db"},
            dump_runner=_dump_runner,
            metadata_loader=_metadata_loader,
            preflight_loader=_preflight_loader,
        )


def test_create_encrypted_backup_fails_with_invalid_key(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="BACKUP_ENCRYPTION_KEY invalida"):
        backup.create_encrypted_backup(
            output_dir=tmp_path,
            env={"DIRECT_URL": "postgresql://user:pass@example.test/db", "BACKUP_ENCRYPTION_KEY": "invalida"},
            dump_runner=_dump_runner,
            metadata_loader=_metadata_loader,
            preflight_loader=_preflight_loader,
        )


def test_create_encrypted_backup_masks_connection_errors(tmp_path: Path) -> None:
    key = Fernet.generate_key()

    def failing_dump(_: str, __: Path) -> None:
        raise RuntimeError("pg_dump falhou. Credenciais e detalhes foram ocultados.")

    with pytest.raises(RuntimeError) as exc:
        backup.create_encrypted_backup(
            output_dir=tmp_path,
            env=_env(key, "postgresql://secret-user:secret-pass@example.test/db"),
            dump_runner=failing_dump,
            metadata_loader=_metadata_loader,
            preflight_loader=_preflight_loader,
        )

    assert "secret-pass" not in str(exc.value)
    assert "example.test" not in str(exc.value)


def test_restore_validates_checksums_and_removes_plaintext(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    key = Fernet.generate_key()
    result = backup.create_encrypted_backup(
        output_dir=tmp_path,
        env=_env(key),
        dump_runner=_dump_runner,
        metadata_loader=_metadata_loader,
        preflight_loader=_preflight_loader,
    )
    monkeypatch.setenv("BACKUP_ENCRYPTION_KEY", key.decode("utf-8"))

    calls: list[str] = []

    def role_preparer(database_url: str) -> None:
        calls.append(f"roles:{database_url}")

    def restore_runner(database_url: str, dump_path: Path) -> None:
        calls.append(f"restore:{database_url}")
        assert dump_path.exists()

    def fake_validate(_: str) -> restore.RestoreVerification:
        return restore.RestoreVerification(
            restored=True,
            plaintext_removed=False,
            table_count=13,
            migration_count=7,
            index_count=41,
            constraint_count=90,
            row_counts={"clientes": 0},
        )

    monkeypatch.setattr(restore, "validate_restore", fake_validate)

    verification = restore.verify_encrypted_backup_restore(
        result.encrypted_backup,
        result.manifest,
        database_url="postgresql://postgres:test@localhost:5432/temp",
        restore_runner=restore_runner,
        role_preparer=role_preparer,
    )

    assert verification.restored is True
    assert verification.plaintext_removed is True
    assert verification.table_count == 13
    assert calls == [
        "roles:postgresql://postgres:test@localhost:5432/temp",
        "restore:postgresql://postgres:test@localhost:5432/temp",
    ]


def test_restore_fails_with_wrong_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = backup.create_encrypted_backup(
        output_dir=tmp_path,
        env=_env(Fernet.generate_key()),
        dump_runner=_dump_runner,
        metadata_loader=_metadata_loader,
        preflight_loader=_preflight_loader,
    )
    monkeypatch.setenv("BACKUP_ENCRYPTION_KEY", Fernet.generate_key().decode("utf-8"))

    with pytest.raises(RuntimeError, match="nao pode ser descriptografado"):
        restore.verify_encrypted_backup_restore(
            result.encrypted_backup,
            result.manifest,
            database_url="postgresql://postgres:test@localhost:5432/temp",
            restore_runner=lambda *_: None,
            role_preparer=lambda *_: None,
        )


def test_restore_fails_with_tampered_checksum(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    key = Fernet.generate_key()
    result = backup.create_encrypted_backup(
        output_dir=tmp_path,
        env=_env(key),
        dump_runner=_dump_runner,
        metadata_loader=_metadata_loader,
        preflight_loader=_preflight_loader,
    )
    monkeypatch.setenv("BACKUP_ENCRYPTION_KEY", key.decode("utf-8"))
    result.encrypted_backup.write_bytes(result.encrypted_backup.read_bytes() + b"adulterado")

    with pytest.raises(RuntimeError, match="Checksum do backup criptografado diverge"):
        restore.verify_encrypted_backup_restore(
            result.encrypted_backup,
            result.manifest,
            database_url="postgresql://postgres:test@localhost:5432/temp",
            restore_runner=lambda *_: None,
            role_preparer=lambda *_: None,
        )


def test_restore_blocks_supabase_direct_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POSTGRES_RESTORE_URL", "postgresql://postgres:test@localhost:5432/temp")
    monkeypatch.setenv("SUPABASE_DIRECT_URL", "postgresql://real-secret.example/db")

    with pytest.raises(RuntimeError, match="SUPABASE_DIRECT_URL nao deve ser usado"):
        restore.get_restore_url()


@pytest.mark.parametrize(
    ("input_url", "expected"),
    [
        ("postgresql://user:pass@example.test/db", "postgresql+psycopg://user:pass@example.test/db"),
        ("postgres://user:pass@example.test/db", "postgresql+psycopg://user:pass@example.test/db"),
        ("postgresql+psycopg://user:pass@example.test/db", "postgresql+psycopg://user:pass@example.test/db"),
    ],
)
def test_sqlalchemy_database_url_uses_psycopg_driver(input_url: str, expected: str) -> None:
    assert backup.sqlalchemy_database_url(input_url) == expected


@pytest.mark.parametrize(
    ("input_url", "expected"),
    [
        ("postgresql+psycopg://user:pass@example.test/db", "postgresql://user:pass@example.test/db"),
        ("postgresql+psycopg2://user:pass@example.test/db", "postgresql://user:pass@example.test/db"),
        ("postgres://user:pass@example.test/db", "postgresql://user:pass@example.test/db"),
        ("postgresql://user:pass@example.test/db", "postgresql://user:pass@example.test/db"),
    ],
)
def test_postgres_client_database_url_uses_native_scheme(input_url: str, expected: str) -> None:
    assert backup.postgres_client_database_url(input_url) == expected


def test_safe_server_major_uses_psycopg_not_psycopg2(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return None

        def execute(self, _):
            class Result:
                @staticmethod
                def scalar():
                    return "160008"

            return Result()

    class FakeEngine:
        @staticmethod
        def connect():
            return FakeConnection()

    def fake_create_engine(url: str):
        calls.append(url)
        return FakeEngine()

    monkeypatch.setattr(backup, "create_engine", fake_create_engine)
    monkeypatch.setattr(backup, "pg_dump_version", lambda: "pg_dump (PostgreSQL) 16.0")

    assert backup.safe_server_major("postgresql://secret-user:secret-pass@example.test/db") == 16
    assert calls == ["postgresql+psycopg://secret-user:secret-pass@example.test/db"]
    assert "psycopg2" not in calls[0]


def test_safe_server_major_masks_invalid_authentication(monkeypatch: pytest.MonkeyPatch) -> None:
    secret_url = "postgresql://secret-user:secret-pass@example.test/db"

    class FakeEngine:
        @staticmethod
        def connect():
            raise RuntimeError(f"password authentication failed for {secret_url}")

    monkeypatch.setattr(backup, "create_engine", lambda _: FakeEngine())
    monkeypatch.setattr(backup, "pg_dump_version", lambda: "pg_dump (PostgreSQL) 16.0")

    with pytest.raises(backup.SafePgDumpError) as exc:
        backup.safe_server_major(secret_url)

    assert exc.value.category == "AUTHENTICATION_FAILED"
    assert "secret-pass" not in str(exc.value)
    assert "example.test" not in str(exc.value)
    assert secret_url not in str(exc.value)


def test_preflight_compatibility_uses_safe_server_major(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(backup, "pg_dump_version", lambda: "pg_dump (PostgreSQL) 17.2")
    monkeypatch.setattr(backup, "safe_server_major", lambda _: 16)

    result = backup.backup_preflight("postgresql://secret-user:secret-pass@example.test/db")

    assert result == {
        "pg_dump_installed": True,
        "pg_dump_major": 17,
        "server_major": 16,
        "compatible": True,
    }


def test_preflight_driver_error_is_safe(monkeypatch: pytest.MonkeyPatch) -> None:
    def missing_driver(_: str):
        raise ModuleNotFoundError("No module named 'psycopg2'")

    monkeypatch.setattr(backup, "create_engine", missing_driver)
    monkeypatch.setattr(backup, "pg_dump_version", lambda: "pg_dump (PostgreSQL) 16.0")

    with pytest.raises(backup.SafePgDumpError) as exc:
        backup.safe_server_major("postgresql://secret-user:secret-pass@example.test/db")

    assert exc.value.category == "DRIVER_NOT_AVAILABLE"
    assert "psycopg2" not in str(exc.value)
    assert "secret-pass" not in str(exc.value)


def test_project_does_not_require_psycopg2_dependency() -> None:
    requirements = Path(__file__).parents[1].joinpath("requirements.txt").read_text(encoding="utf-8")

    assert "psycopg[binary]" in requirements
    assert "psycopg2" not in requirements


def test_pg_dump_command_uses_environment_not_connection_argument(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[list[str], dict[str, str] | None]] = []

    def fake_run(args, **kwargs):
        calls.append((args, kwargs.get("env")))
        Path(args[args.index("--file") + 1]).write_bytes(b"PGDMP ficticio")
        return CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(backup.subprocess, "run", fake_run)
    monkeypatch.setattr(backup, "pg_dump_version", lambda: "pg_dump (PostgreSQL) 16.0")

    backup.run_pg_dump("postgresql://secret-user:secret-pass@example.test/db", tmp_path / "safe.dump")

    command, env = calls[0]
    assert "postgresql://secret-user:secret-pass@example.test/db" not in command
    assert env is not None
    assert env["PGHOST"] == "example.test"
    assert env["PGPORT"] == "5432"
    assert env["PGUSER"] == "secret-user"
    assert env["PGPASSWORD"] == "secret-pass"
    assert env["PGDATABASE"] == "db"
    assert Path(command[command.index("--file") + 1]).is_absolute()
    assert "--schema" in command
    assert command[command.index("--schema") + 1] == "public"
    assert "--dbname" in command
    assert command[command.index("--dbname") + 1] == "db"
    assert "--no-owner" in command
    assert "--no-privileges" in command
    assert "--no-acl" not in command


def test_pg_dump_creates_missing_output_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    output_path = tmp_path / "nested" / "safe.dump"

    def fake_run(args, **_):
        Path(args[args.index("--file") + 1]).write_bytes(b"PGDMP ficticio")
        return CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(backup.subprocess, "run", fake_run)
    monkeypatch.setattr(backup, "pg_dump_version", lambda: "pg_dump (PostgreSQL) 17.0")

    backup.run_pg_dump("postgresql://user:pass@example.test/db", output_path)

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_pg_dump_rejects_invalid_output_parent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    invalid_parent = tmp_path / "not-a-directory"
    invalid_parent.write_text("x", encoding="utf-8")
    monkeypatch.setattr(backup, "pg_dump_version", lambda: "pg_dump (PostgreSQL) 17.0")

    with pytest.raises(backup.SafePgDumpError) as exc:
        backup.run_pg_dump("postgresql://user:pass@example.test/db", invalid_parent / "safe.dump")

    assert exc.value.category == "OUTPUT_FILE_ERROR"
    assert exc.value.diagnostic_code == "PGDUMP_OUTPUT_FILE_ERROR"


def test_pg_dump_rejects_low_disk_space(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    class DiskUsage:
        free = 1

    monkeypatch.setattr(backup.shutil, "disk_usage", lambda _: DiskUsage())
    monkeypatch.setattr(backup, "pg_dump_version", lambda: "pg_dump (PostgreSQL) 17.0")

    with pytest.raises(backup.SafePgDumpError) as exc:
        backup.run_pg_dump("postgresql://user:pass@example.test/db", tmp_path / "safe.dump")

    assert exc.value.category == "DISK_SPACE_LOW"
    assert exc.value.diagnostic_code == "PGDUMP_DISK_SPACE_LOW"


def test_pg_dump_success_with_empty_file_is_output_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(args, **_):
        Path(args[args.index("--file") + 1]).write_bytes(b"")
        return CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(backup.subprocess, "run", fake_run)
    monkeypatch.setattr(backup, "pg_dump_version", lambda: "pg_dump (PostgreSQL) 17.0")

    with pytest.raises(backup.SafePgDumpError) as exc:
        backup.run_pg_dump("postgresql://user:pass@example.test/db", tmp_path / "safe.dump")

    assert exc.value.category == "OUTPUT_FILE_ERROR"
    assert exc.value.output_created is True
    assert exc.value.output_nonempty is False


def test_pg_dump_failure_keeps_database_error_when_empty_file_is_only_a_symptom(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(args, **_):
        Path(args[args.index("--file") + 1]).write_bytes(b"")
        return CompletedProcess(args=args, returncode=1, stdout="", stderr="could not stat file: No such file or directory")

    monkeypatch.setattr(backup.subprocess, "run", fake_run)
    monkeypatch.setattr(backup, "pg_dump_version", lambda: "pg_dump (PostgreSQL) 17.0")

    with pytest.raises(backup.SafePgDumpError) as exc:
        backup.run_pg_dump(
            "postgresql://secret-user:secret-pass@secret-host.internal/db",
            tmp_path / "safe.dump",
        )

    assert exc.value.category == "DATABASE_DUMP_ERROR"
    assert exc.value.diagnostic_code == "PGDUMP_DATABASE_DUMP_ERROR"
    assert exc.value.output_created is True
    assert exc.value.output_nonempty is False
    assert "secret-pass" not in str(exc.value)
    assert "secret-host" not in str(exc.value)


def test_pg_dump_uses_absolute_path_for_relative_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    recorded_output_paths: list[Path] = []

    def fake_run(args, **_):
        output_path = Path(args[args.index("--file") + 1])
        recorded_output_paths.append(output_path)
        output_path.write_bytes(b"PGDMP ficticio")
        return CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(backup.subprocess, "run", fake_run)
    monkeypatch.setattr(backup, "pg_dump_version", lambda: "pg_dump (PostgreSQL) 17.0")

    backup.run_pg_dump("postgresql://user:pass@example.test/db", Path("relative.dump"))

    assert recorded_output_paths == [tmp_path / "relative.dump"]


def test_pg_dump_converts_sqlalchemy_url_for_client_tool(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, str] | None] = []

    def fake_run(args, **kwargs):
        calls.append(kwargs.get("env"))
        Path(args[args.index("--file") + 1]).write_bytes(b"PGDMP ficticio")
        return CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(backup.subprocess, "run", fake_run)
    monkeypatch.setattr(backup, "pg_dump_version", lambda: "pg_dump (PostgreSQL) 17.0")

    backup.run_pg_dump("postgresql+psycopg://user:pass@example.test/db", tmp_path / "safe.dump")

    assert calls[0] is not None
    assert calls[0]["PGHOST"] == "example.test"
    assert calls[0]["PGUSER"] == "user"
    assert calls[0]["PGPASSWORD"] == "pass"
    assert calls[0]["PGDATABASE"] == "db"


def test_pg_dump_client_env_keeps_connection_parts_out_of_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[list[str], dict[str, str] | None]] = []

    def fake_run(args, **kwargs):
        calls.append((args, kwargs.get("env")))
        Path(args[args.index("--file") + 1]).write_bytes(b"PGDMP ficticio")
        return CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(backup.subprocess, "run", fake_run)
    monkeypatch.setattr(backup, "pg_dump_version", lambda: "pg_dump (PostgreSQL) 17.0")

    backup.run_pg_dump(
        "postgresql+psycopg://user:p%40ss@127.0.0.1:5433/crm_restore_source?sslmode=disable",
        tmp_path / "safe.dump",
    )

    command, env = calls[0]
    assert all("postgresql" not in str(part) for part in command)
    assert env is not None
    assert env["PGHOST"] == "127.0.0.1"
    assert env["PGPORT"] == "5433"
    assert env["PGUSER"] == "user"
    assert env["PGPASSWORD"] == "p@ss"
    assert env["PGDATABASE"] == "crm_restore_source"
    assert env["PGSSLMODE"] == "disable"


@pytest.mark.parametrize(
    ("stderr", "expected_category", "expected_code", "expected_type", "expected_schema", "expected_sqlstate"),
    [
        (
            "ERROR: permission denied for schema public SQLSTATE 42501",
            "SCHEMA_PERMISSION_DENIED",
            "PGDUMP_SCHEMA_PERMISSION_DENIED",
            "schema",
            "public",
            "42501",
        ),
        (
            "ERROR: permission denied for schema auth SQLSTATE 42501",
            "MANAGED_SCHEMA_ERROR",
            "PGDUMP_MANAGED_SCHEMA_ERROR",
            "schema",
            "auth",
            "42501",
        ),
        (
            "ERROR: permission denied for table clientes SQLSTATE 42501",
            "TABLE_PERMISSION_DENIED",
            "PGDUMP_TABLE_PERMISSION_DENIED",
            "table",
            "indisponivel",
            "42501",
        ),
        (
            "ERROR: permission denied for sequence clientes_id_seq SQLSTATE 42501",
            "SEQUENCE_PERMISSION_DENIED",
            "PGDUMP_SEQUENCE_PERMISSION_DENIED",
            "sequence",
            "indisponivel",
            "42501",
        ),
        (
            "ERROR: invalid object definition SQLSTATE XX000",
            "INVALID_DATABASE_OBJECT",
            "PGDUMP_INVALID_DATABASE_OBJECT",
            "indisponivel",
            "indisponivel",
            "XX000",
        ),
    ],
)
def test_pg_dump_database_errors_are_sanitized_and_specific(
    stderr: str,
    expected_category: str,
    expected_code: str,
    expected_type: str,
    expected_schema: str,
    expected_sqlstate: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(args, **_):
        Path(args[args.index("--file") + 1]).write_bytes(b"PGDMP parcial")
        return CompletedProcess(
            args=args,
            returncode=1,
            stdout="",
            stderr=f"{stderr} postgresql://secret-user:secret-pass@secret-host.internal/db",
        )

    monkeypatch.setattr(backup.subprocess, "run", fake_run)
    monkeypatch.setattr(backup, "pg_dump_version", lambda: "pg_dump (PostgreSQL) 17.0")

    with pytest.raises(backup.SafePgDumpError) as exc:
        backup.run_pg_dump("postgresql://secret-user:secret-pass@secret-host.internal/db", tmp_path / "safe.dump")

    message = str(exc.value)
    assert exc.value.category == expected_category
    assert exc.value.diagnostic_code == expected_code
    assert exc.value.object_type == expected_type
    assert exc.value.schema == expected_schema
    assert exc.value.sqlstate == expected_sqlstate
    assert exc.value.output_created is True
    assert exc.value.output_nonempty is True
    assert "secret-user" not in message
    assert "secret-pass" not in message
    assert "secret-host" not in message
    assert "postgresql://" not in message


def test_pg_dump_failure_after_writing_partial_dump_blocks_encryption(tmp_path: Path) -> None:
    key = Fernet.generate_key()

    def partial_dump(_: str, __: Path) -> None:
        raise backup.SafePgDumpError(
            "TABLE_PERMISSION_DENIED",
            step="pg_dump",
            exit_code=1,
            pg_dump_version="pg_dump (PostgreSQL) 17.0",
            recommendation=backup.safe_recommendation("TABLE_PERMISSION_DENIED"),
            binary_found=True,
            output_created=True,
            output_nonempty=True,
            sqlstate="42501",
            object_type="table",
            schema="public",
            error_class="permission_denied",
        )

    with pytest.raises(backup.SafePgDumpError) as exc:
        backup.create_encrypted_backup(
            output_dir=tmp_path,
            env=_env(key),
            dump_runner=partial_dump,
            metadata_loader=_metadata_loader,
            preflight_loader=_preflight_loader,
        )

    assert exc.value.category == "TABLE_PERMISSION_DENIED"
    assert not list(tmp_path.glob("*.dump.enc"))
    assert not list(tmp_path.glob("*.manifest.json"))


@pytest.mark.parametrize(
    ("stderr", "expected"),
    [
        ("server version: 17.0; pg_dump version: 16.0", "PG_DUMP_VERSION_MISMATCH"),
        ("could not translate host name \"private-db.example\" to address", "DNS_FAILED"),
        ("SSL error: certificate verify failed", "SSL_FAILED"),
        ("password authentication failed for user", "AUTHENTICATION_FAILED"),
        ("permission denied for table clientes", "TABLE_PERMISSION_DENIED"),
        ("could not connect to server", "CONNECTION_FAILED"),
        ("unrecognized option '--bad'", "INVALID_ARGUMENT"),
        ("could not open output file", "OUTPUT_FILE_ERROR"),
        ("could not stat file: No such file or directory", "DATABASE_DUMP_ERROR"),
        ("some database error", "DATABASE_DUMP_ERROR"),
    ],
)
def test_pg_dump_error_classification(stderr: str, expected: str) -> None:
    assert backup.classify_pg_dump_error(stderr, 1) == expected


def test_pg_dump_timeout_is_safe(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def timeout_run(*_, **__):
        raise TimeoutExpired(cmd="pg_dump", timeout=1)

    monkeypatch.setattr(backup.subprocess, "run", timeout_run)
    monkeypatch.setattr(backup, "pg_dump_version", lambda: "pg_dump (PostgreSQL) 16.0")

    with pytest.raises(backup.SafePgDumpError) as exc:
        backup.run_pg_dump("postgresql://secret-user:secret-pass@example.test/db", tmp_path / "safe.dump", timeout=1)

    assert exc.value.category == "TIMEOUT"
    assert exc.value.diagnostic_code == "PGDUMP_TIMEOUT"
    assert "BACKUP_DIAGNOSTIC_CODE=PGDUMP_TIMEOUT" in str(exc.value)
    assert "secret-pass" not in str(exc.value)
    assert "example.test" not in str(exc.value)


@pytest.mark.parametrize(
    ("stderr", "expected_category", "expected_code"),
    [
        ("could not translate host name \"secret-host.internal\" to address", "DNS_FAILED", "PGDUMP_DNS_FAILED"),
        ("SSL error: certificate verify failed for secret-host.internal", "SSL_FAILED", "PGDUMP_SSL_FAILED"),
        ("password authentication failed for user secret-user", "AUTHENTICATION_FAILED", "PGDUMP_AUTHENTICATION_FAILED"),
        ("permission denied for table clientes", "TABLE_PERMISSION_DENIED", "PGDUMP_TABLE_PERMISSION_DENIED"),
    ],
)
def test_pg_dump_safe_diagnostics_remove_sensitive_details(
    stderr: str,
    expected_category: str,
    expected_code: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(args, **kwargs):
        return CompletedProcess(args=args, returncode=1, stdout="", stderr=stderr)

    secret_url = "postgresql://secret-user:secret-pass@secret-host.internal:5432/db?sslmode=require"
    monkeypatch.setattr(backup.subprocess, "run", fake_run)
    monkeypatch.setattr(backup, "pg_dump_version", lambda: "pg_dump (PostgreSQL) 17.0")

    with pytest.raises(backup.SafePgDumpError) as exc:
        backup.run_pg_dump(secret_url, tmp_path / "safe.dump")

    message = str(exc.value)
    assert exc.value.category == expected_category
    assert exc.value.diagnostic_code == expected_code
    assert f"BACKUP_DIAGNOSTIC_CODE={expected_code}" in message
    assert "secret-user" not in message
    assert "secret-pass" not in message
    assert "secret-host" not in message
    assert "postgresql://" not in message


def test_pg_dump_not_installed_reports_safe_diagnostic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def missing_pg_dump(*_, **__):
        raise FileNotFoundError("pg_dump")

    monkeypatch.setattr(backup.subprocess, "run", missing_pg_dump)

    with pytest.raises(backup.SafePgDumpError) as exc:
        backup.run_pg_dump("postgresql://user:pass@example.test/db", tmp_path / "safe.dump")

    assert exc.value.category == "PG_DUMP_NOT_FOUND"
    assert exc.value.diagnostic_code == "PGDUMP_NOT_FOUND"
    assert "pg_dump_encontrado=nao" in str(exc.value)


def test_empty_pg_dump_output_reports_safe_diagnostic(tmp_path: Path) -> None:
    key = Fernet.generate_key()

    def empty_dump(_: str, dump_path: Path) -> None:
        dump_path.write_bytes(b"")

    with pytest.raises(backup.SafePgDumpError) as exc:
        backup.create_encrypted_backup(
            output_dir=tmp_path,
            env=_env(key),
            dump_runner=empty_dump,
            metadata_loader=_metadata_loader,
            preflight_loader=_preflight_loader,
        )

    assert exc.value.category == "OUTPUT_FILE_ERROR"
    assert exc.value.diagnostic_code == "PGDUMP_OUTPUT_FILE_ERROR"
    assert not list(tmp_path.glob("*.dump"))


def test_encryption_failure_is_safe_and_removes_plaintext(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    key = Fernet.generate_key()

    def fail_encrypt(*_, **__) -> None:
        raise RuntimeError("secret-host secret-user secret-pass")

    monkeypatch.setattr(backup, "encrypt_file", fail_encrypt)

    with pytest.raises(backup.SafePgDumpError) as exc:
        backup.create_encrypted_backup(
            output_dir=tmp_path,
            env=_env(key, "postgresql://secret-user:secret-pass@secret-host.internal/db"),
            dump_runner=_dump_runner,
            metadata_loader=_metadata_loader,
            preflight_loader=_preflight_loader,
        )

    message = str(exc.value)
    assert exc.value.category == "ENCRYPTION_FAILED"
    assert exc.value.diagnostic_code == "BACKUP_ENCRYPTION_FAILED"
    assert "criptografia_iniciada=sim" in message
    assert "secret-host" not in message
    assert "secret-user" not in message
    assert "secret-pass" not in message
    assert not list(tmp_path.glob("*.dump"))


def test_workflow_blocks_invalid_or_empty_artifact_upload() -> None:
    content = ENCRYPTED_BACKUP_WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "Verify artifact contents" in content
    assert "backup-artifact/*.tar.enc" in content
    assert "backup-artifact/*.manifest.json" in content
    assert "backup-artifact/*.sha256" in content
    assert "if-no-files-found: error" in content
    assert "Arquivo aberto nao pode ser publicado como artifact." in content


def test_preflight_version_mismatch_blocks_before_dump(tmp_path: Path) -> None:
    key = Fernet.generate_key()

    with pytest.raises(backup.SafePgDumpError) as exc:
        backup.create_encrypted_backup(
            output_dir=tmp_path,
            env=_env(key),
            dump_runner=_dump_runner,
            metadata_loader=_metadata_loader,
            preflight_loader=lambda _: {
                "pg_dump_installed": True,
                "pg_dump_major": 16,
                "server_major": 17,
                "compatible": False,
            },
        )

    assert exc.value.category == "PG_DUMP_VERSION_MISMATCH"
