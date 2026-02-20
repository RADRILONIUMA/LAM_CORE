# Test Mirror Matrix — CORE_RECLONE_CLEAN (2026-02-17)

## Existing

- Smoke marker.
- Governance artifact/file/header coverage.

## Missing

| Domain | Missing Test | Priority |
|---|---|---|
| Workflow State | Validate `WORKFLOW_SNAPSHOT_STATE.md` against contract fields | P0 |
| System State | Validate `SYSTEM_STATE.md` keys and status value domain | P0 |
| Gateway | Execute dry-run verify of `scripts/gateway_io.sh verify` with mocked env | P1 |
| Drift | Compare protocol sync header version with SoT registry snapshot | P1 |
| Interop | Roundtrip test for export/import package metadata compatibility | P2 |

## Mirror Plan

- Mirror-A: P0 contract/state semantic checks.
- Mirror-B: P1 gateway and drift checks.
- Mirror-C: P2 interop exchange tests with Archivator/System orchestration layer.
