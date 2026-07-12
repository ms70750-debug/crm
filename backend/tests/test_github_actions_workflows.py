from pathlib import Path


WORKFLOWS_DIR = Path(__file__).resolve().parents[2] / ".github" / "workflows"
DRY_RUN_WORKFLOW_PATH = WORKFLOWS_DIR / "supabase-migrations-dry-run.yml"
APPLY_WORKFLOW_PATH = WORKFLOWS_DIR / "supabase-migrations-apply.yml"
SINGLE_APPLY_WORKFLOW_PATH = WORKFLOWS_DIR / "supabase-migration-single-apply.yml"
READONLY_AUDIT_WORKFLOW_PATH = WORKFLOWS_DIR / "supabase-readonly-audit.yml"


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


def test_supabase_single_apply_workflow_exists_and_is_manual_only() -> None:
    content = SINGLE_APPLY_WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "name: Supabase Migration Single Apply" in content
    assert "workflow_dispatch:" in content
    assert "pull_request:" not in content
    assert "\npush:" not in content
    assert "contents: read" in content
    assert "concurrency:" in content
    assert "timeout-minutes: 10" in content


def test_supabase_single_apply_workflow_has_closed_migration_options() -> None:
    content = SINGLE_APPLY_WORKFLOW_PATH.read_text(encoding="utf-8")

    for migration in (
        "2026_07_01_000_postgres_bootstrap_schema.sql",
        "2026_07_02_postgres_preparacao.sql",
        "2026_07_12_auth_sessions.sql",
        "2026_07_12_real_data_readiness.sql",
    ):
        assert migration in content
    assert "APLICAR-MIGRATION" in content
    assert "expected_previous_migration" in content


def test_supabase_single_apply_workflow_uses_secret_without_printing_it() -> None:
    content = SINGLE_APPLY_WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "SUPABASE_DIRECT_URL" in content
    assert "DIRECT_URL: ${{ secrets.SUPABASE_DIRECT_URL }}" in content
    assert "::add-mask::${DIRECT_URL}" in content
    assert "printenv" not in content
    assert "env |" not in content
    assert "echo ${DIRECT_URL}" not in content
    assert "echo $DIRECT_URL" not in content
    assert "postgresql://" not in content
    assert "postgres://" not in content


def test_supabase_single_apply_workflow_runs_transaction_test_before_apply() -> None:
    content = SINGLE_APPLY_WORKFLOW_PATH.read_text(encoding="utf-8")

    transaction_test_index = content.index("--transaction-test")
    apply_index = content.rindex("Apply selected migration only")
    assert transaction_test_index < apply_index
    assert content.count("apply_single_postgres_migration.py") == 2


def test_supabase_readonly_audit_workflow_is_manual_readonly_and_safe() -> None:
    content = READONLY_AUDIT_WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "name: Supabase Readonly Audit" in content
    assert "workflow_dispatch:" in content
    assert "\npush:" not in content
    assert "pull_request:" not in content
    assert "schedule:" not in content
    assert "contents: read" in content
    assert "timeout-minutes: 10" in content
    assert "concurrency:" in content
    assert "SUPABASE_DIRECT_URL" in content
    assert "::add-mask::${DIRECT_URL}" in content
    assert "upload-artifact" in content
    assert "supabase-readonly-audit" in content


def test_supabase_readonly_audit_workflow_does_not_expose_connection_string() -> None:
    content = READONLY_AUDIT_WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "printenv" not in content
    assert "env |" not in content
    assert "echo ${DIRECT_URL}" not in content
    assert "echo $DIRECT_URL" not in content
    assert "postgresql://" not in content
    assert "postgres://" not in content
