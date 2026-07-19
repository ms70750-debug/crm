from pathlib import Path
from subprocess import CompletedProcess

import pytest

from backend.scripts import verify_encrypted_backup_restore as restore


def test_pg_restore_uses_configured_absolute_binary(tmp_path: Path, monkeypatch) -> None:
    calls: list[tuple[list[str], dict[str, str] | None]] = []
    configured_binary = "/usr/lib/postgresql/17/bin/pg_restore"
    dump_path = tmp_path / "backup.dump"
    dump_path.write_bytes(b"PGDMP ficticio")

    def fake_run(args, **kwargs):
        calls.append((args, kwargs.get("env")))
        return CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setenv("PG_RESTORE_BIN", configured_binary)
    monkeypatch.setattr(restore.subprocess, "run", fake_run)

    restore.run_pg_restore("postgresql+psycopg://user:pass@example.test:5433/restore_db?sslmode=disable", dump_path)

    command, env = calls[0]
    assert command[0] == configured_binary
    assert "--dbname" in command
    assert command[command.index("--dbname") + 1] == "restore_db"
    assert env is not None
    assert env["PGHOST"] == "example.test"
    assert env["PGPORT"] == "5433"
    assert env["PGUSER"] == "user"
    assert env["PGPASSWORD"] == "pass"
    assert env["PGDATABASE"] == "restore_db"
    assert env["PGSSLMODE"] == "disable"


def test_restore_blocks_external_host_before_drop(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SOURCE_DB", "crm_source_ci")

    with pytest.raises(RuntimeError, match="host do destino nao e local"):
        restore.assert_safe_disposable_restore_target(
            "postgresql+psycopg://user:pass@db.supabase.co:5432/crm_restore_ci?sslmode=require"
        )


def test_restore_blocks_non_synthetic_database_name(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SOURCE_DB", "crm_source_ci")

    with pytest.raises(RuntimeError, match="nome sintetico permitido"):
        restore.assert_safe_disposable_restore_target(
            "postgresql+psycopg://user:pass@127.0.0.1:5432/crm_restore_target?sslmode=disable"
        )


def test_restore_blocks_source_equal_to_target(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SOURCE_DB", "crm_restore_ci")

    with pytest.raises(RuntimeError, match="origem e destino sao iguais"):
        restore.assert_safe_disposable_restore_target(
            "postgresql+psycopg://user:pass@localhost:5432/crm_restore_ci?sslmode=disable"
        )


def test_restore_preparation_drops_public_only_after_guards(monkeypatch: pytest.MonkeyPatch) -> None:
    statements: list[str] = []

    class Result:
        def __init__(self, value):
            self.value = value

        def scalar(self):
            return self.value

        def scalar_one(self):
            return self.value

        def scalars(self):
            return iter(self.value if isinstance(self.value, list) else [])

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return None

        def execute(self, statement, *_args, **_kwargs):
            sql = str(statement)
            statements.append(sql)
            if "current_database()" in sql:
                return Result("crm_restore_ci")
            if "information_schema.tables" in sql:
                return Result([])
            if "pg_namespace" in sql:
                return Result(False)
            return Result(None)

    class FakeEngine:
        @staticmethod
        def begin():
            return FakeConnection()

    monkeypatch.setenv("SOURCE_DB", "crm_source_ci")
    monkeypatch.setattr(restore, "create_engine", lambda _: FakeEngine())

    restore.prepare_disposable_restore_target(
        "postgresql+psycopg://user:pass@127.0.0.1:5432/crm_restore_ci?sslmode=disable"
    )

    assert any("DROP SCHEMA IF EXISTS public CASCADE" in statement for statement in statements)


def test_restore_preparation_blocks_application_tables_before_drop(monkeypatch: pytest.MonkeyPatch) -> None:
    statements: list[str] = []

    class Result:
        def __init__(self, value):
            self.value = value

        def scalar(self):
            return self.value

        def scalar_one(self):
            return self.value

        def scalars(self):
            return iter(self.value if isinstance(self.value, list) else [])

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return None

        def execute(self, statement, *_args, **_kwargs):
            sql = str(statement)
            statements.append(sql)
            if "current_database()" in sql:
                return Result("crm_restore_ci")
            if "information_schema.tables" in sql:
                return Result(["clientes"])
            return Result(None)

    class FakeEngine:
        @staticmethod
        def begin():
            return FakeConnection()

    monkeypatch.setenv("SOURCE_DB", "crm_source_ci")
    monkeypatch.setattr(restore, "create_engine", lambda _: FakeEngine())

    with pytest.raises(RuntimeError, match="ja possui tabelas da aplicacao"):
        restore.prepare_disposable_restore_target(
            "postgresql+psycopg://user:pass@127.0.0.1:5432/crm_restore_ci?sslmode=disable"
        )

    assert not any("DROP SCHEMA IF EXISTS public CASCADE" in statement for statement in statements)


def test_dump_index_confirms_public_schema_without_printing_full_index(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    dump_path = tmp_path / "backup.dump"
    dump_path.write_bytes(b"PGDMP ficticio")

    def fake_run(args, **_kwargs):
        assert args[:2] == ["pg_restore", "--list"]
        return CompletedProcess(
            args=args,
            returncode=0,
            stdout="\n".join(
                [
                    "; archive header",
                    "1; 2615 2200 SCHEMA - public postgres",
                    "2; 1259 12345 TABLE public clientes postgres",
                    "3; 1259 12346 INDEX public clientes_pkey postgres",
                    "4; 2606 12347 CONSTRAINT public clientes clientes_pkey postgres",
                ]
            ),
            stderr="",
        )

    monkeypatch.setattr(restore.subprocess, "run", fake_run)

    summary = restore.inspect_dump_index(dump_path)

    assert summary.public_schema_included is True
    assert summary.total_entries == 4
    assert summary.has_tables is True
    assert summary.has_indexes is True
    assert summary.has_constraints is True
