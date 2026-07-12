from scripts import audit_supabase_permissions as audit


def _table(name: str, grants: dict[str, list[str]] | None = None, rls_enabled: bool = False):
    return {
        "name": name,
        "owner": "postgres",
        "rls_enabled": rls_enabled,
        "rls_forced": False,
        "policies": [],
        "grants": grants or {"public": [], "PUBLIC": [], "anon": [], "authenticated": [], "service_role": [], "postgres": []},
        "security_definer_functions": [],
    }


def test_detects_anon_select_as_critical() -> None:
    table = _table("clientes", {"public": [], "PUBLIC": [], "anon": ["SELECT"], "authenticated": [], "service_role": [], "postgres": []})

    status, reasons = audit.classify_table(table)

    assert status == "CRITICO"
    assert any("anon" in reason for reason in reasons)


def test_detects_anon_write_as_critical() -> None:
    table = _table("clientes", {"public": [], "PUBLIC": [], "anon": ["INSERT"], "authenticated": [], "service_role": [], "postgres": []})

    status, reasons = audit.classify_table(table)

    assert status == "CRITICO"
    assert any("anon" in reason for reason in reasons)


def test_detects_public_grant_as_critical() -> None:
    table = _table("leads", {"public": ["SELECT"], "PUBLIC": [], "anon": [], "authenticated": [], "service_role": [], "postgres": []})

    status, reasons = audit.classify_table(table)

    assert status == "CRITICO"
    assert any("public" in reason for reason in reasons)


def test_detects_table_without_rls_as_attention_for_backend_only() -> None:
    status, reasons = audit.classify_table(_table("schema_migrations"))

    assert status == "ATENCAO"
    assert any("RLS desativado" in reason for reason in reasons)


def test_classifies_backend_only_without_direct_public_access() -> None:
    table = _table(
        "clientes",
        {"public": [], "PUBLIC": [], "anon": [], "authenticated": [], "service_role": ["SELECT"], "postgres": ["SELECT", "INSERT"]},
        rls_enabled=True,
    )

    status, reasons = audit.classify_table(table)

    assert status == "SEGURO"
    assert "Sem grants diretos perigosos identificados" in reasons


def test_recommends_backend_only_when_frontend_does_not_use_supabase() -> None:
    assert audit.recommend_strategy([]) == "A) BACKEND-ONLY"


def test_recommends_rls_when_frontend_uses_supabase_directly() -> None:
    assert audit.recommend_strategy([], frontend_uses_supabase=True) == "B) RLS OBRIGATORIO"


def test_safe_error_and_report_mask_sensitive_values() -> None:
    rendered = audit.render_report(
        {
            "generated_at": "2026-07-12T00:00:00+00:00",
            "roles": [],
            "grants": [{"grantee": "anon", "table_name": "clientes", "privilege_type": "SELECT"}],
            "routine_privileges": [],
            "policies": [],
            "security_definer_functions": [],
            "tables": [
                {
                    **_table("clientes", {"public": [], "PUBLIC": [], "anon": ["SELECT"], "authenticated": [], "service_role": [], "postgres": []}),
                    "classification": "CRITICO",
                    "reasons": ["admin@demo.com postgresql://user:secret@host:5432/db 123.456.789-09"],
                }
            ],
        }
    )

    assert "admin@demo.com" not in rendered
    assert "secret@host" not in rendered
    assert "123.456.789-09" not in rendered

