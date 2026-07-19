from pathlib import Path
from subprocess import CompletedProcess

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
