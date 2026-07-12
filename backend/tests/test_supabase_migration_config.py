import os
import subprocess
import sys
from pathlib import Path

import pytest

from app.config.environment import validate_environment
from scripts import apply_postgres_migrations

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "apply_postgres_migrations.py"


def test_direct_url_is_not_required_for_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("BBB_AUTH_SECRET", "segredo-demo-forte-para-pytest")
    monkeypatch.setenv("CORS_ORIGINS", "https://crm-sepia-beta.vercel.app")
    monkeypatch.setenv("DATABASE_URL", "postgresql://usuario:senha@aws-0-us-east-1.pooler.supabase.com:6543/postgres")
    monkeypatch.delenv("DIRECT_URL", raising=False)
    monkeypatch.setenv("EVOLUTION_API_MODE", "simulation")
    monkeypatch.setenv("REAL_DATA_MODE", "false")

    validate_environment()


def test_direct_url_is_required_for_postgres_migration_script(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DIRECT_URL", raising=False)
    monkeypatch.setenv("REAL_DATA_MODE", "false")

    with pytest.raises(RuntimeError, match="DIRECT_URL ausente"):
        apply_postgres_migrations.get_direct_url()


def test_migration_script_masks_direct_url_without_user_host_password_or_path() -> None:
    direct_url = "postgresql://postgres:senha-super-secreta@aws-0-us-east-1.pooler.supabase.com:5432/postgres"
    masked_url = apply_postgres_migrations.mask_database_url(
        direct_url
    )

    assert masked_url == "postgresql://[DIRECT_URL_OCULTA]"
    assert "postgresql://" in masked_url
    assert direct_url not in masked_url
    assert "postgres" not in masked_url.removeprefix("postgresql://")
    assert "senha-super-secreta" not in masked_url
    assert "aws-0-us-east-1.pooler.supabase.com" not in masked_url
    assert "5432" not in masked_url


def test_direct_url_placeholder_fails_with_safe_message(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DIRECT_URL", "postgresql://postgres:[YOUR-PASSWORD]@host.supabase.co:5432/postgres")

    with pytest.raises(RuntimeError) as exc:
        apply_postgres_migrations.get_direct_url()

    message = str(exc.value)
    assert "DIRECT_URL ainda contem [YOUR-PASSWORD]" in message
    assert "host.supabase.co" not in message


def test_direct_url_with_brackets_does_not_raise_raw_value_error(monkeypatch: pytest.MonkeyPatch) -> None:
    direct_url = "postgresql://postgres:senha[com-colchete]@host.supabase.co:5432/postgres"
    monkeypatch.setenv("DIRECT_URL", direct_url)

    with pytest.raises(RuntimeError) as exc:
        apply_postgres_migrations.get_direct_url()

    message = str(exc.value)
    assert "DIRECT_URL invalida" in message
    assert "Invalid IPv6 URL" not in message
    assert direct_url not in message
    assert "senha[com-colchete]" not in message


def test_cli_invalid_direct_url_does_not_print_traceback_or_secret() -> None:
    direct_url = "postgresql://postgres:senha[com-colchete]@host.supabase.co:5432/postgres"
    env = os.environ.copy()
    env["DIRECT_URL"] = direct_url
    env["REAL_DATA_MODE"] = "false"

    result = subprocess.run([sys.executable, str(SCRIPT_PATH)], capture_output=True, text=True, env=env, check=False)
    output = f"{result.stdout}\n{result.stderr}"

    assert result.returncode == 1
    assert "ERRO SEGURO" in output
    assert "Traceback" not in output
    assert "Invalid IPv6 URL" not in output
    assert direct_url not in output
    assert "senha[com-colchete]" not in output


def test_invalid_direct_url_is_masked_without_secret() -> None:
    direct_url = "postgresql://postgres:senha[com-colchete]@host.supabase.co:5432/postgres"
    masked_url = apply_postgres_migrations.mask_database_url(direct_url)

    assert masked_url == "<DIRECT_URL invalida ocultada>"
    assert "senha[com-colchete]" not in masked_url


def test_direct_url_invalid_scheme_fails_without_url_or_password(monkeypatch: pytest.MonkeyPatch) -> None:
    direct_url = "mysql://usuario:senha-super-secreta@host.example.com:3306/bbb"
    monkeypatch.setenv("DIRECT_URL", direct_url)

    with pytest.raises(RuntimeError) as exc:
        apply_postgres_migrations.get_direct_url()

    message = str(exc.value)
    assert "DIRECT_URL invalida" in message
    assert direct_url not in message
    assert "senha-super-secreta" not in message


def test_migration_script_dry_run_masks_valid_url(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    direct_url = "postgresql://postgres:senha-super-secreta@aws-0-us-east-1.pooler.supabase.com:5432/postgres"
    monkeypatch.setenv(
        "DIRECT_URL",
        direct_url,
    )
    monkeypatch.setenv("REAL_DATA_MODE", "false")

    assert apply_postgres_migrations.main([]) == 0
    output = capsys.readouterr().out

    assert "DRY-RUN aplicaria" in output
    assert "Validacao offline de schema vazio: OK." in output
    assert "postgresql://[DIRECT_URL_OCULTA]" in output
    assert direct_url not in output
    assert "postgres:senha-super-secreta" not in output
    assert "senha-super-secreta" not in output
    assert "aws-0-us-east-1.pooler.supabase.com" not in output
    assert "5432/postgres" not in output


def test_migration_script_blocks_real_data_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "DIRECT_URL",
        "postgresql://postgres:senha-super-secreta@aws-0-us-east-1.pooler.supabase.com:5432/postgres",
    )
    monkeypatch.setenv("REAL_DATA_MODE", "true")

    with pytest.raises(RuntimeError, match="REAL_DATA_MODE=true"):
        apply_postgres_migrations.main([])


def test_migration_chain_requires_bootstrap_first(tmp_path: Path) -> None:
    migration = tmp_path / "2026_07_02_postgres_preparacao.sql"
    migration.write_text("ALTER TABLE leads ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ;", encoding="utf-8")

    with pytest.raises(RuntimeError, match="Migration bootstrap ausente"):
        apply_postgres_migrations.validate_migration_chain_for_empty_schema([migration])


def test_current_postgres_migration_chain_validates_for_empty_schema() -> None:
    migration_paths = apply_postgres_migrations.load_postgres_migrations()

    apply_postgres_migrations.validate_migration_chain_for_empty_schema(migration_paths)


def test_migration_chain_detects_alter_table_without_base_table(tmp_path: Path) -> None:
    bootstrap = tmp_path / "2026_07_01_000_postgres_bootstrap_schema.sql"
    bootstrap.write_text("CREATE TABLE IF NOT EXISTS clientes (id SERIAL PRIMARY KEY);", encoding="utf-8")
    migration = tmp_path / "2026_07_02_postgres_preparacao.sql"
    migration.write_text("ALTER TABLE leads ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ;", encoding="utf-8")

    with pytest.raises(RuntimeError, match="altera tabela inexistente"):
        apply_postgres_migrations.validate_migration_chain_for_empty_schema([bootstrap, migration])
