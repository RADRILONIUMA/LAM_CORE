from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_readme_declares_validation_commands():
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "./.venv/bin/python -m pytest -q" in text
    assert "scripts/test_entrypoint.sh --all" in text


def test_readme_declares_aess_integration_surface():
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "scripts/aess_autostart.sh" in text
    assert "scripts/aess_service_start.sh" in text


def test_core_scripts_exist():
    required = [
        "scripts/aess_autostart.sh",
        "scripts/gateway_io.sh",
        "scripts/test_entrypoint.sh",
    ]
    missing = [name for name in required if not (REPO_ROOT / name).exists()]
    assert not missing, f"missing scripts: {missing}"


def test_pytest_ini_contract():
    text = (REPO_ROOT / "pytest.ini").read_text(encoding="utf-8")
    assert "testpaths = tests" in text
    assert "markers =" in text
    assert "governance" in text
    assert "boundary" in text
