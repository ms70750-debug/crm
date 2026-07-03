from pathlib import Path


WORKFLOWS_DIR = Path(__file__).resolve().parents[2] / ".github" / "workflows"
DRY_RUN_WORKFLOW_PATH = WORKFLOWS_DIR / "supabase-migrations-dry-run.yml"
APPLY_WORKFLOW_PATH = WORKFLOWS_DIR / "supabase-migrations-apply.yml"


def test_supabase_dry_run_workflow_exists_and_is_manual() -> None:
    content = DRY_RUN_WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "name: Supabase Migrations Dry Run" in content
    assert "workflow_dispatch:" in content
    assert "contents: read" in content


def test_supabase_dry_run_workflow_uses_secret_without_apply() -> None:
    content = DRY_RUN_WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "SUPABASE_DIRECT_URL" in content
    assert "DIRECT_URL: ${{ secrets.SUPABASE_DIRECT_URL }}" in content
    assert "python backend/scripts/apply_postgres_migrations.py" in content
    assert "--apply" not in content


def test_supabase_dry_run_workflow_does_not_contain_connection_string() -> None:
    content = DRY_RUN_WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "postgresql://" not in content
    assert "postgres://" not in content
    assert "[YOUR-PASSWORD]" not in content


def test_supabase_apply_workflow_exists_and_is_manual() -> None:
    content = APPLY_WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "name: Supabase Migrations Apply" in content
    assert "workflow_dispatch:" in content
    assert "contents: read" in content


def test_supabase_apply_workflow_requires_confirmation_input() -> None:
    content = APPLY_WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "confirmacao:" in content
    assert "CONFIRMACAO: ${{ github.event.inputs.confirmacao }}" in content
    assert 'if [ "${CONFIRMACAO}" != "APLICAR_MIGRATIONS_SUPABASE" ]; then' in content
    assert "Confirmacao invalida. Nenhuma migration foi aplicada." in content


def test_supabase_apply_workflow_uses_secret_and_apply_flag() -> None:
    content = APPLY_WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "SUPABASE_DIRECT_URL" in content
    assert "DIRECT_URL: ${{ secrets.SUPABASE_DIRECT_URL }}" in content
    assert 'REAL_DATA_MODE: "false"' in content
    assert "python backend/scripts/apply_postgres_migrations.py --apply" in content


def test_supabase_apply_workflow_does_not_print_env_or_connection_string() -> None:
    content = APPLY_WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "printenv" not in content
    assert "env |" not in content
    assert "echo ${DIRECT_URL}" not in content
    assert "echo $DIRECT_URL" not in content
    assert "postgresql://" not in content
    assert "postgres://" not in content
    assert "[YOUR-PASSWORD]" not in content
