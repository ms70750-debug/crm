import json
from pathlib import Path

import pytest
from cryptography.fernet import Fernet

from scripts import create_encrypted_postgres_backup as backup
from scripts import verify_encrypted_backup_restore as restore


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
        "table_count": 12,
    }


def test_create_encrypted_backup_creates_safe_artifacts_and_removes_plaintext(tmp_path: Path) -> None:
    key = Fernet.generate_key()

    result = backup.create_encrypted_backup(
        output_dir=tmp_path,
        env=_env(key),
        dump_runner=_dump_runner,
        metadata_loader=_metadata_loader,
    )

    assert result.encrypted_backup.exists()
    assert result.manifest.exists()
    assert result.checksums.exists()
    assert result.plaintext_removed is True
    assert not list(tmp_path.glob("*.dump"))

    manifest = json.loads(result.manifest.read_text(encoding="utf-8"))
    assert manifest["format_version"] == backup.BACKUP_FORMAT_VERSION
    assert manifest["latest_migration"] == "2026_07_12_backend_only_permissions.sql"
    assert manifest["table_count"] == 12
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
        )


def test_create_encrypted_backup_fails_with_invalid_key(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="BACKUP_ENCRYPTION_KEY invalida"):
        backup.create_encrypted_backup(
            output_dir=tmp_path,
            env={"DIRECT_URL": "postgresql://user:pass@example.test/db", "BACKUP_ENCRYPTION_KEY": "invalida"},
            dump_runner=_dump_runner,
            metadata_loader=_metadata_loader,
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
            table_count=12,
            migration_count=5,
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
    assert verification.table_count == 12
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
