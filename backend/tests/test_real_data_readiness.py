import os
import sqlite3
from pathlib import Path
from time import time_ns

import pytest
from fastapi.testclient import TestClient

from app.config.environment import validate_environment
from app.database.init_db import init_db
from app.database.session import SessionLocal
from app.main import app
from app.models import AuditLog, Client
from app.services.backup import create_sqlite_backup, restore_sqlite_backup
from app.services.data_protection import DataProtectionError, cpf_digest, decrypt_text, encrypt_text, protect_cpf

client = TestClient(app)


@pytest.fixture(autouse=True)
def demo_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("APP_MODE", "demo")
    monkeypatch.setenv("REAL_DATA_MODE", "false")
    yield


def _strong_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BBB_DATA_ENCRYPTION_KEY", "pytest-data-key-with-more-than-32-chars")


def _token() -> str:
    init_db()
    response = client.post("/auth/login", json={"email": "admin@bbbconsig.demo", "password": "BbbConsig@2026"})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_encrypt_decrypt_and_authenticated_tamper_detection(monkeypatch: pytest.MonkeyPatch) -> None:
    _strong_key(monkeypatch)
    encrypted = encrypt_text("cpf-ficticio-000")
    assert encrypted
    assert "cpf-ficticio-000" not in encrypted
    assert decrypt_text(encrypted) == "cpf-ficticio-000"
    with pytest.raises(DataProtectionError):
        decrypt_text(encrypted[:-2] + "AA")


def test_cpf_hash_is_deterministic_and_does_not_expose_cpf(monkeypatch: pytest.MonkeyPatch) -> None:
    _strong_key(monkeypatch)
    first = cpf_digest("000.000.001-91")
    second = cpf_digest("00000000191")
    assert first == second
    assert "00000000191" not in first
    protected = protect_cpf("000.000.001-91")
    assert protected.digest == first
    assert protected.ciphertext


def test_data_protection_fails_safely_without_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BBB_DATA_ENCRYPTION_KEY", raising=False)
    with pytest.raises(DataProtectionError):
        encrypt_text("nao deve criptografar sem chave")


def test_production_mode_blocks_missing_readiness(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("APP_MODE", "production")
    monkeypatch.setenv("BBB_AUTH_SECRET", "segredo-forte-para-pytest-com-mais-de-32")
    monkeypatch.setenv("DATABASE_URL", "postgresql://host.local:5432/bbb")
    _strong_key(monkeypatch)
    for name in ["MIGRATIONS_APPLIED", "BACKUP_CONFIGURED", "CONSENT_REQUIRED", "LOGS_MASKED", "HTTPS_EXPECTED", "CRITICAL_TESTS_APPROVED"]:
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(RuntimeError) as exc:
        validate_environment()
    assert "BACKUP_CONFIGURED" in str(exc.value)
    assert "senha@host" not in str(exc.value)


def test_demo_login_blocked_in_production_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_MODE", "production")
    response = client.post("/auth/demo-login", json={"role": "admin"})
    assert response.status_code == 403


def test_cookie_is_secure_in_production_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    from app.services.security import session_cookie_options

    options = session_cookie_options()
    assert options["httponly"] is True
    assert options["secure"] is True
    assert options["samesite"] == "none"


def test_soft_delete_restore_and_audit_log() -> None:
    token = _token()
    suffix = str(time_ns())[-9:]
    headers = {"Authorization": f"Bearer {token}"}
    created = client.post(
        "/clientes",
        headers=headers,
        json={"nome": f"Cliente Restore {suffix}", "cpf": f"991{suffix}", "telefone": f"1199{suffix}", "email": f"restore{suffix}@demo.local", "convenio": "INSS"},
    )
    assert created.status_code == 201
    client_id = created.json()["id"]
    assert client.delete(f"/clientes/{client_id}", headers=headers).status_code == 200
    assert client.post(f"/clientes/{client_id}/restore", headers=headers).status_code == 200
    with SessionLocal() as db:
        stored = db.get(Client, client_id)
        assert stored is not None
        assert stored.deleted_at is None
        audit = db.query(AuditLog).filter(AuditLog.action == "client_restored").order_by(AuditLog.id.desc()).first()
        assert audit is not None


def test_consent_requires_active_record_and_opt_out_blocks_message() -> None:
    token = _token()
    suffix = str(time_ns())[-9:]
    headers = {"Authorization": f"Bearer {token}"}
    created = client.post(
        "/clientes",
        headers=headers,
        json={"nome": f"Cliente Consent {suffix}", "cpf": f"992{suffix}", "telefone": f"1192{suffix}", "email": f"consent{suffix}@demo.local", "convenio": "INSS"},
    )
    client_id = created.json()["id"]
    consent = client.post("/consents", headers=headers, json={"customer_id": client_id, "channel": "whatsapp", "purpose": "simulacao", "source": "pytest"})
    assert consent.status_code == 201
    assert consent.json()["purpose"] == "simulacao"
    sent = client.post("/whatsapp/simular-envio", headers=headers, json={"destinatario_tipo": "cliente", "destinatario_id": client_id, "modelo": "primeiro_contato", "mensagem": "Mensagem ficticia."})
    assert sent.status_code == 201
    revoked = client.post(f"/consents/{consent.json()['id']}/revoke", headers=headers)
    assert revoked.status_code == 200
    blocked = client.post("/whatsapp/simular-envio", headers=headers, json={"destinatario_tipo": "cliente", "destinatario_id": client_id, "modelo": "primeiro_contato", "mensagem": "Mensagem ficticia."})
    assert blocked.status_code == 403


def _apply_sql_file(db_path: Path, sql_path: Path) -> None:
    statements = [statement.strip() for statement in sql_path.read_text(encoding="utf-8").split(";") if statement.strip()]
    with sqlite3.connect(db_path) as conn:
        for statement in statements:
            conn.execute(statement)


def test_real_data_migration_applies_to_temp_sqlite_and_reverts_from_snapshot(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[2]
    sqlite_migration = root / "backend" / "migrations" / "sqlite" / "2026_07_12_real_data_readiness.sql"
    postgres_migration = root / "backend" / "migrations" / "postgres" / "2026_07_12_real_data_readiness.sql"
    assert sqlite_migration.exists()
    assert postgres_migration.exists()
    assert "backup_audit_logs" in sqlite_migration.read_text(encoding="utf-8")
    assert "IF NOT EXISTS" in postgres_migration.read_text(encoding="utf-8")

    db_path = tmp_path / "migration-demo.sqlite"
    with sqlite3.connect(db_path) as conn:
        for table in ["leads", "clientes", "propostas", "tarefas", "whatsapp_messages", "consents", "simulations"]:
            conn.execute(f"CREATE TABLE {table} (id INTEGER PRIMARY KEY)")
        conn.execute("ALTER TABLE clientes ADD COLUMN deleted_at DATETIME")
    snapshot = tmp_path / "before-migration.sqlite"
    snapshot.write_bytes(db_path.read_bytes())

    _apply_sql_file(db_path, sqlite_migration)
    with sqlite3.connect(db_path) as conn:
        client_columns = {row[1] for row in conn.execute("PRAGMA table_info(clientes)").fetchall()}
        assert {"cpf_hash", "cpf_encrypted", "bank_data_encrypted"}.issubset(client_columns)
        assert conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='backup_audit_logs'").fetchone()

    db_path.write_bytes(snapshot.read_bytes())
    with sqlite3.connect(db_path) as conn:
        reverted_columns = {row[1] for row in conn.execute("PRAGMA table_info(clientes)").fetchall()}
    assert "cpf_hash" not in reverted_columns


def test_auth_session_migration_applies_to_temp_sqlite_and_reverts_from_snapshot(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[2]
    sqlite_migration = root / "backend" / "migrations" / "sqlite" / "2026_07_12_auth_sessions.sql"
    postgres_migration = root / "backend" / "migrations" / "postgres" / "2026_07_12_auth_sessions.sql"
    assert sqlite_migration.exists()
    assert postgres_migration.exists()
    assert "auth_sessions" in sqlite_migration.read_text(encoding="utf-8")
    assert "IF NOT EXISTS" in postgres_migration.read_text(encoding="utf-8")

    db_path = tmp_path / "auth-session-migration-demo.sqlite"
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY)")
    snapshot = tmp_path / "before-auth-session-migration.sqlite"
    snapshot.write_bytes(db_path.read_bytes())

    _apply_sql_file(db_path, sqlite_migration)
    with sqlite3.connect(db_path) as conn:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(auth_sessions)").fetchall()}
        assert {"session_id_hash", "user_id", "expires_at", "revoked_at", "revocation_reason"}.issubset(columns)

    db_path.write_bytes(snapshot.read_bytes())
    with sqlite3.connect(db_path) as conn:
        assert conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_sessions'").fetchone() is None


def test_fictitious_backup_and_restore(tmp_path: Path) -> None:
    source = tmp_path / "demo.sqlite"
    with sqlite3.connect(source) as conn:
        conn.execute("CREATE TABLE demo (id INTEGER PRIMARY KEY, nome TEXT)")
        conn.execute("INSERT INTO demo (nome) VALUES ('ficticio')")
    backup = create_sqlite_backup(source, tmp_path / "backups")
    restored = restore_sqlite_backup(backup, tmp_path / "restore" / "demo-restored.sqlite")
    with sqlite3.connect(restored) as conn:
        row = conn.execute("SELECT nome FROM demo WHERE id=1").fetchone()
    assert row == ("ficticio",)


def test_no_real_secret_patterns_in_current_diff() -> None:
    root = Path(__file__).resolve().parents[2]
    diff_targets = [
        root / ".env.example",
        root / "docs",
        root / "backend" / "app",
        root / "backend" / "migrations",
    ]
    combined = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for target in diff_targets
        for path in ([target] if target.is_file() else target.rglob("*"))
        if path.is_file() and path.suffix in {".md", ".py", ".sql", ".example", ""}
    )
    forbidden_patterns = ["".join(parts) for parts in [("s", "k-"), ("g", "hp_"), ("github", "_pat_"), ("A", "KIA")]]
    for pattern in forbidden_patterns:
        assert pattern not in combined
