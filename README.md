# CORE

Governance-oriented core scaffold repository used for protocol, workflow, and system-state contracts.

## Validation
```bash
./.venv/bin/python -m pytest -q
scripts/test_entrypoint.sh --all
```

## Current Strategic Status
- Wave: `SEQ-WAVE-2026-02-17-A`
- Queue order: `#2`
- State: `IN_PROGRESS` (see `ROADMAP.md`)

## AESS Integration
- Autostart hook: `scripts/aess_autostart.sh`
- Optional service hook: `scripts/aess_service_start.sh` (define if runtime service startup is required)
