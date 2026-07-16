from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LOGIN_PAGE = ROOT / "frontend" / "src" / "pages" / "Login.tsx"
LAYOUT_COMPONENT = ROOT / "frontend" / "src" / "components" / "Layout.tsx"
ADMIN_ACTIVATION_PAGE = ROOT / "frontend" / "src" / "pages" / "AdminActivation.tsx"
APP_ROUTES = ROOT / "frontend" / "src" / "App.tsx"
AUTH_CONTEXT = ROOT / "frontend" / "src" / "auth" / "AuthContext.tsx"
API_LIB = ROOT / "frontend" / "src" / "lib" / "api.ts"


def test_public_login_hides_demo_shortcuts_without_explicit_flag() -> None:
    content = LOGIN_PAGE.read_text(encoding="utf-8")

    assert 'import.meta.env.VITE_DEMO_MODE === "true"' in content
    assert "{demoModeEnabled && (" in content
    assert "Usuarios demo" in content
    assert "Ambiente de demonstracao" in content
    assert 'demoModeEnabled ? "grid gap-5 lg:grid-cols-[1fr_1.1fr]"' in content
    assert "admin@bbbconsig.demo" not in content
    assert "BbbConsig@2026" not in content


def test_layout_hides_demo_badges_without_explicit_flag() -> None:
    content = LAYOUT_COMPONENT.read_text(encoding="utf-8")

    assert 'import.meta.env.VITE_DEMO_MODE === "true"' in content
    assert '{demoModeEnabled && <div className="badge border-lime/30 text-lime">Evolution API em simulacao</div>}' in content
    assert "Ambiente demo: nao insira dados reais" in content


def test_admin_activation_page_removes_token_from_url_and_does_not_store_it() -> None:
    content = ADMIN_ACTIVATION_PAGE.read_text(encoding="utf-8")
    auth_context = AUTH_CONTEXT.read_text(encoding="utf-8")
    routes = APP_ROUTES.read_text(encoding="utf-8")

    assert 'path="/ativar-admin"' in routes
    assert "window.history.replaceState" in content
    assert "localStorage" not in content
    assert "sessionStorage" not in content
    assert "console." not in content
    assert "/auth/admin-bootstrap/validate" in content
    assert "/auth/admin-bootstrap/activate" in auth_context
    assert "X-Admin-Bootstrap-Token" in content
    assert "/validate?token=" not in content


def test_frontend_auth_token_is_memory_only() -> None:
    content = API_LIB.read_text(encoding="utf-8")
    auth_context = AUTH_CONTEXT.read_text(encoding="utf-8")

    assert "let authToken: string | null = null" in content
    assert "authToken = token" in content
    assert "authToken = null" in content
    assert "const tokenAtStart = getAuthToken()" in auth_context
    assert "getAuthToken() === tokenAtStart" in auth_context
    assert content.index("...init") < content.index("headers: {")
    assert "localStorage.setItem" not in content
    assert "sessionStorage" not in content
