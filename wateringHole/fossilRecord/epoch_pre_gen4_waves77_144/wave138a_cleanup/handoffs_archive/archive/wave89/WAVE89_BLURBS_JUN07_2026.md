# Wave 89 Blurbs — Targeted by Team

**Date**: 2026-06-07  
**From**: eastGate overwatch  
**Cascade**: 38/38 parity | Depot: 13/13 current

---

## songBird Team — P1 BLOCKER

**SB-FEDERATION-01: Federation TCP listener does not start in NUCLEUS server mode.**

When NUCLEUS launches songbird via `songbird server --socket <path>`, the UDS IPC is
healthy (`{"status":"alive"}`), and the env vars are correctly passed:

```
SONGBIRD_FEDERATION_PORT=7700
SONGBIRD_PEERS=strand.primals.eco:7700
SONGBIRD_NODE_ID=eastGate
```

However, songbird opens ports 8081 (discovery) and 8091 but **never binds :7700** (or
default :8082). The federation TCP listener is not starting.

strandGate's songbird has :7700 LIVE and accepting — their startup path works.
eastGate's songbird via NUCLEUS does not. The difference may be in how
`start_orchestrator()` wires the federation listener.

**Also**: `SONGBIRD_PRODUCTION_BIND_ADDRESS` defaults to `127.0.0.1`. For cross-gate
federation, this needs to be `0.0.0.0`. biomeOS needs to pass this in the launch
profile, but songbird should also respect `SONGBIRD_FEDERATION_BIND` when set.

**Action**: Ensure the federation TCP listener starts in `server` subcommand mode
when `SONGBIRD_FEDERATION_PORT` is set. This is the sole remaining blocker for the
2-gate mesh proof (strandGate is ready and waiting).

---

## biomeOS Team — P2

**BIO-SEARCH-01: RESOLVED.** v4.10 shipped depot-first search priority. Validated:
all 12 primals resolve from plasmidBin depot. Thank you.

**Remaining**: Add `SONGBIRD_PRODUCTION_BIND_ADDRESS = "0.0.0.0"` to
`[profiles.songbird.env_vars]` in `nucleus_launch_profiles.toml`. This unblocks
cross-gate federation once songBird fixes SB-FEDERATION-01.

**Also**: barracuda fails to create its UDS socket within 10s, causing NUCLEUS to
abort after the 6th primal. Not blocking mesh proof but blocks full 12-primal startup.

---

## cellMembrane Team — CLEAR

**CM-TRIGGER-01: RESOLVED.** `plasmid.trigger` validated from eastGate.  
**CM-VPS-SVC-01: RESOLVED.** Service fix shipped (`e8e19f6`).

No P1/P2 items. P3 remaining: CM-WEBHOOK-01 (Forgejo webhook-driven cascade).

---

## All Other Teams — NO ACTION

Mountain is clear. Springs are 100% postPrimordial compliant.
All gates at cascade parity. No upstream primal work needed.

---

## Critical Path (updated)

| # | Item | Owner | Status |
|---|------|-------|--------|
| 1 | ~~plasmidBin pipeline e2e~~ | cellMembrane | **DONE** |
| 2 | ~~CM-TRIGGER-01~~ | cellMembrane | **DONE** |
| 3 | ~~PostPrimordial audit~~ | overwatch | **DONE** |
| 4 | ~~BIO-SEARCH-01~~ | biomeOS | **DONE** (v4.10) |
| 5 | **SB-FEDERATION-01** | songBird | **P1 BLOCKER** |
| 6 | biomeOS bind address passthrough | biomeOS | P2 (unblocked by #5) |
| 7 | 2-gate mesh proof | eastGate + strandGate | Blocked on #5 |
| 8 | S4 auth gate review | overwatch | ~Jun 9 |
| 9 | westGate enrollment | westGate | Hardware pending |
| 10 | 3-gate mesh proof → stadial | all gates | Blocked on #7 + #9 |

---

*"Twelve primals from depot. One federation port from mesh."*
