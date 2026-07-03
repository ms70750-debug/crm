from pathlib import Path


WORKFLOW_PATH = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "supabase-migrations-dry-run.yml"


def test_supabase_dry_run_workflow_exists_and_is_manual() -> None:
    content = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "name: Supabase Migrations Dry Run" in content
    assert "workflow_dispatch:" in content
    assert "contents: read" in content


def test_supabase_dry_run_workflow_uses_secret_without_apply() -> None:
    content = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "SUPABASE_DIRECT_URL" in content
    assert "DIRECT_URL: ${{ secrets.SUPABASE_DIRECT_URL }}" in content
    assert "python backend/scripts/apply_postgres_migrations.py" in content
    assert "--apply" not in content


def test_supabase_dry_run_workflow_does_not_contain_connection_string() -> None:
    content = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "postgresql://" not in content
    assert "postgres://" not in content
    assert "[YOUR-PASSWORD]" not in content
