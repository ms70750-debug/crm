from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LOGIN_PAGE = ROOT / "frontend" / "src" / "pages" / "Login.tsx"
LAYOUT_COMPONENT = ROOT / "frontend" / "src" / "components" / "Layout.tsx"


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
