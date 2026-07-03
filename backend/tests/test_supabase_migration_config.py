import pytest

from app.config.environment import validate_environment
from scripts import apply_postgres_migrations


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


def test_migration_script_masks_direct_url_password() -> None:
    masked_url = apply_postgres_migrations.mask_database_url(
        "postgresql://postgres:senha-super-secreta@aws-0-us-east-1.pooler.supabase.com:5432/postgres"
    )

    assert "senha-super-secreta" not in masked_url
    assert "***" in masked_url


def test_migration_script_dry_run_does_not_print_password(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setenv(
        "DIRECT_URL",
        "postgresql://postgres:senha-super-secreta@aws-0-us-east-1.pooler.supabase.com:5432/postgres",
    )
    monkeypatch.setenv("REAL_DATA_MODE", "false")

    assert apply_postgres_migrations.main([]) == 0
    output = capsys.readouterr().out

    assert "DRY-RUN aplicaria" in output
    assert "senha-super-secreta" not in output


def test_migration_script_blocks_real_data_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "DIRECT_URL",
        "postgresql://postgres:senha-super-secreta@aws-0-us-east-1.pooler.supabase.com:5432/postgres",
    )
    monkeypatch.setenv("REAL_DATA_MODE", "true")

    with pytest.raises(RuntimeError, match="REAL_DATA_MODE=true"):
        apply_postgres_migrations.main([])
