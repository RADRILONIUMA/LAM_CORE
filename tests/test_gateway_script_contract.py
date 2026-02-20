from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_gateway_script_has_core_commands():
    script = (REPO_ROOT / "scripts" / "gateway_io.sh").read_text(encoding="utf-8")
    assert "verify_github" in script
    assert "verify_onedrive" in script
    assert "verify_gworkspace" in script
    assert "do_export" in script
    assert "do_import" in script
    assert "Usage: $0 [verify|export|import <archive>]" in script
