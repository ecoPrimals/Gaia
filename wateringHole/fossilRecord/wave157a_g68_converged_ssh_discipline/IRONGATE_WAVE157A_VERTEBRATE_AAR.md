# ironGate Wave 157a — Vertebrate Evolution AAR

**Date**: 2026-08-09 | **Wave**: 157a | **Gate**: ironGate
**Classification**: G68 redeploy + RPC surface audit evolution

---

## Summary

ironGate cascaded Wave 157a vertebrate evolution blurb, redeployed G68 binaries
(11/13 alive), and evolved `nucleus-deploy verify` with RPC surface audit
capability aligned with the vertebrate self-check mandate.

## Execution

### 1. G68 Binary Redeploy

7 stale binaries (June 21) replaced with G68 depot binaries (Aug 8):
beardog, nestgate, rhizocrypt, loamspine, barracuda, coralreef, toadstool.

**Result**: 11/13 ALIVE, 89 MB total RSS.

**2 blocked**:
- **nestgate** G68 requires `NESTGATE_JWT_SECRET` (added to tower.env). Binary
  exits cleanly after startup under systemd `Type=simple` — primal team issue.
- **toadstool** G68 exits cleanly after binding sockets. Gets "Permission denied"
  on `/run/membrane/` when running as non-root. Works under systemd but async
  runtime completes and process exits with code 0.

### 2. Gate Manifest Update

`irongate.toml` updated to Wave 157a:
- Binary generation: G68
- Primals alive: 11/13
- Added `[p0_blockers]` section documenting all 3 P0s
- Added `[environment]` section for new G68 env requirements

### 3. nucleus-deploy verify --audit-rpc (NEW)

Evolved `nucleus-deploy verify` with vertebrate RPC surface audit:

- **Phase 1**: Probes each primal's `health.liveness` (liveness check)
- **Phase 2**: Sends nonexistent method — detects P0-A health-only stubs
  (proper primals return -32601, stubs return health response for any input)
- **Phase 3**: Validates BTSP gating on protected methods (-32001 rejection)

Extracted per-primal audit into `audit_single_primal` + `audit_unknown_method`
+ `audit_btsp_gating` functions. Added `is_health_stub_response` detection.

**Test coverage**: +1 test (`health_stub_detection`), total 266 workspace tests.
**Clippy**: 0 warnings (pedantic + nursery). **Fmt**: clean.

### 4. P0 Documentation

Updated `specs/EVOLUTION_GAPS.md` with P0 section documenting all three blockers
and their impact on nucleus-deploy validation tooling.

## Files Modified

| File | Change |
|------|--------|
| `deploy/nucleus-deploy/src/verify.rs` | +185 lines: RPC surface audit, stub detection, BTSP audit |
| `deploy/nucleus-deploy/src/main.rs` | Added `--audit-rpc` flag to Verify subcommand |
| `gates/irongate.toml` | Updated to Wave 157a, G68, P0 blockers, environment |
| `specs/EVOLUTION_GAPS.md` | Added P0 blockers section, updated wave stamp and test count |

## Environment Changes on ironGate

| Change | Value |
|--------|-------|
| `NESTGATE_JWT_SECRET` | Generated, added to `/etc/membrane/tower.env` |
| `TOADSTOOL_SECURITY_WARNING_ACKNOWLEDGED` | Set to 1 in tower.env |
| `TOADSTOOL_FAMILY_ID` | Set to `e8b62b6e` in tower.env |
| `BIOMEOS_FAMILY_ID` | Set to `e8b62b6e` in tower.env |

## Primal Team Escalations

| P0 | Owner | Impact |
|----|-------|--------|
| P0-A: bearDog sign stub | bearDog team | All spine commits unsigned. `--audit-rpc` detects. |
| P0-B: nestGate API + startup exit | nestGate team | G68 binary exits after startup. content.ingest missing. |
| P0-C: biomeOS FD leak | biomeOS team | capability.call unusable. Direct UDS works. |
| toadstool G68 startup exit | toadStool team | Binary exits cleanly after socket bind. |

---

*Filed by ironGate code team. Wave 157a vertebrate evolution — G68 redeploy 11/13,
RPC surface audit shipped, 3 P0s documented.*
