import json
import os
import tarfile
from pathlib import Path

import pytest
from cryptography.fernet import Fernet

from scripts import create_supabase_cli_encrypted_backup as backup


def _env(key: bytes) -> dict[str, str]:
    return {
        "BACKUP_ENCRYPTION_KEY": key.decode("utf-8"),
        "SUPABASE_DIRECT_URL": "postgresql://secret-user:secret-pass@secret-host.internal:5432/db",
    }


def _install_fake_supabase(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    fake_dir = tmp_path / "bin"
    fake_dir.mkdir()
    py = fake_dir / "fake_supabase.py"
    py.write_text(
        """
import os
import sys
from pathlib import Path

args = sys.argv[1:]
if args == ["--version"]:
    print("2.109.1")
    raise SystemExit(0)

if args[:2] != ["db", "dump"]:
    print("unsupported", file=sys.stderr)
    raise SystemExit(2)

out = Path(args[args.index("-f") + 1])
fail = os.environ.get("FAKE_SUPABASE_FAIL_STEP", "")
empty = os.environ.get("FAKE_SUPABASE_EMPTY_STEP", "")
if "--role-only" in args:
    step = "roles"
elif "--data-only" in args:
    step = "data"
else:
    step = "schema"

if fail == step:
    print("ERROR: failed for postgresql://secret-user:secret-pass@secret-host.internal/db", file=sys.stderr)
    raise SystemExit(1)

out.parent.mkdir(parents=True, exist_ok=True)
if empty == step:
    out.write_text("", encoding="utf-8")
else:
    out.write_text(f"-- {step} SQL ficticio sem dados pessoais\\n", encoding="utf-8")
raise SystemExit(0)
""".strip()
        + "\n",
        encoding="utf-8",
    )
    if os.name == "nt":
        command = fake_dir / "supabase.cmd"
        command.write_text(f'@echo off\npython "{py}" %*\n', encoding="utf-8")
    else:
        command = fake_dir / "supabase"
        command.write_text(f'#!/usr/bin/env sh\npython "{py}" "$@"\n', encoding="utf-8")
        command.chmod(0o755)
    monkeypatch.setenv("PATH", str(fake_dir) + os.pathsep + os.environ.get("PATH", ""))
    monkeypatch.setenv("SUPABASE_CLI", str(command))
    return command


def test_supabase_cli_backup_creates_encrypted_package_and_sanitized_manifest(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fake_supabase(tmp_path, monkeypatch)
    key = Fernet.generate_key()

    result = backup.create_supabase_cli_backup(tmp_path / "artifact", env=_env(key))

    assert result.encrypted_backup.name == "crm-supabase-backup.tar.enc"
    assert result.manifest.name == "crm-supabase-backup.manifest.json"
    assert result.checksum.name == "crm-supabase-backup.sha256"
    assert result.plaintext_removed is True
    assert not list((tmp_path / "artifact").glob("*.sql"))
    assert not list((tmp_path / "artifact").glob("*.tar"))

    manifest_text = result.manifest.read_text(encoding="utf-8")
    manifest = json.loads(manifest_text)
    assert manifest["method"] == "supabase-cli"
    assert manifest["supabase_cli_version"] == "2.109.1"
    assert manifest["schemas_included"] == ["public"]
    assert manifest["steps_completed"] == ["roles", "schema", "data"]
    assert manifest["retention_days"] == 1
    assert manifest["contains_credentials"] is False
    assert "secret-user" not in manifest_text
    assert "secret-pass" not in manifest_text
    assert "secret-host" not in manifest_text
    assert "postgresql://" not in manifest_text

    decrypted_tar = tmp_path / "decrypted.tar"
    decrypted_tar.write_bytes(Fernet(key).decrypt(result.encrypted_backup.read_bytes()))
    with tarfile.open(decrypted_tar) as archive:
        names = sorted(archive.getnames())
    assert names == sorted(backup.INTERNAL_FILES)
    assert "crm-supabase-backup.tar.enc" in result.checksum.read_text(encoding="utf-8")


def test_supabase_cli_missing_reports_safe_code(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PATH", str(tmp_path))

    with pytest.raises(backup.SafeSupabaseBackupError) as exc:
        backup.create_supabase_cli_backup(tmp_path / "artifact", env=_env(Fernet.generate_key()))

    assert exc.value.diagnostic_code == "SUPABASE_CLI_NOT_FOUND"
    assert "secret" not in str(exc.value)


@pytest.mark.parametrize(
    ("step", "code"),
    [
        ("roles", "SUPABASE_ROLES_DUMP_FAILED"),
        ("schema", "SUPABASE_SCHEMA_DUMP_FAILED"),
        ("data", "SUPABASE_DATA_DUMP_FAILED"),
    ],
)
def test_supabase_cli_dump_step_failures_are_safe(step: str, code: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fake_supabase(tmp_path, monkeypatch)
    monkeypatch.setenv("FAKE_SUPABASE_FAIL_STEP", step)

    with pytest.raises(backup.SafeSupabaseBackupError) as exc:
        backup.create_supabase_cli_backup(tmp_path / "artifact", env=_env(Fernet.generate_key()))

    message = str(exc.value)
    assert exc.value.diagnostic_code == code
    assert "postgresql://" not in message
    assert "secret-user" not in message
    assert "secret-pass" not in message
    assert not list((tmp_path / "artifact").glob("*"))


def test_supabase_cli_empty_dump_is_blocked(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fake_supabase(tmp_path, monkeypatch)
    monkeypatch.setenv("FAKE_SUPABASE_EMPTY_STEP", "data")

    with pytest.raises(backup.SafeSupabaseBackupError) as exc:
        backup.create_supabase_cli_backup(tmp_path / "artifact", env=_env(Fernet.generate_key()))

    assert exc.value.diagnostic_code == "SUPABASE_BACKUP_EMPTY"


def test_supabase_cli_incomplete_package_is_blocked(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "roles.sql").write_text("-- roles", encoding="utf-8")

    with pytest.raises(backup.SafeSupabaseBackupError) as exc:
        backup.create_package(tmp_path / "package.tar", source)

    assert exc.value.diagnostic_code == "SUPABASE_PACKAGE_FAILED"


def test_supabase_cli_restore_order_is_roles_schema_data() -> None:
    manifest = backup.safe_manifest("2.109.1", ["roles", "schema", "data"], {"roles.sql": 1, "schema.sql": 1, "data.sql": 1})

    assert manifest["restore_order"] == ["roles.sql", "schema.sql", "data.sql"]
    assert "psycopg2" not in Path(__file__).parents[1].joinpath("requirements.txt").read_text(encoding="utf-8")
