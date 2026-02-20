from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_boundary_contract_sections_present():
    text = (REPO_ROOT / "CORE_BOUNDARY_CONTRACT.md").read_text(encoding="utf-8")
    assert "# CORE Boundary Contract" in text
    assert "## Modules" in text
    assert "## Allowed Dependencies" in text
    assert "## Gate" in text


def test_boundary_modules_declared():
    text = (REPO_ROOT / "CORE_BOUNDARY_CONTRACT.md").read_text(encoding="utf-8")
    assert "core-governance" in text
    assert "core-runtime" in text
    assert "core-integration" in text
    assert "Reverse dependencies are disallowed." in text
