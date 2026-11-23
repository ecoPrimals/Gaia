# Wave 57 — Ecosystem Convergence Handoff

**Date:** 2026-05-28
**From:** primalSpring coordination (eastGate)
**To:** All teams — primals, springs, cellMembrane, projectNUCLEUS, projectFOUNDATION

---

## Summary

Wave 57 marks ecosystem convergence toward postPrimordial deployment. All teams
have absorbed the VPS deployment standard. NC-1 is COMPLETE (all code delivered).
The remaining path to stadial entry is live deployment and spring emissions.

---

## What primalSpring Shipped (Wave 57)

| Change | Impact |
|--------|--------|
| `main.rs` split → `serve.rs` + `registry_lint.rs` | 804L monolith → 3 focused modules |
| `biomeos.rs` graphs discovery → `env_keys` | Last hardcoded env var eliminated |
| `NeuralBridge::rpc` unreachable → `ProtocolError` | Zero unreachable paths in production |
| `#[allow(clippy::...)]` → `#[expect(...)]` | Zero clippy suppressions without reason |
| Doctest fixes (`CompositionContext::signal`, `dispatch`) | 17/17 doctests pass |
| NC-1 COMPLETE absorption (biomeOS v3.81) | PRIMAL_GAPS + NICHE_CLIMATE updated |
| Downstream absorption (cellMembrane/NUCLEUS/FOUNDATION/lithoSpore) | All 5 teams tracked |

**Test results:** 797 pass / 0 fail / 2 ignored. Zero clippy warnings. Zero unsafe.

---

## Absorbed From Downstream Teams

### cellMembrane (Wave 56)
- `TransportMode` enum (`UdsOnly`, `TcpDefault`, `TcpOptIn`) — typed VPS transport
- `--uds-only` wired into `deploy_membrane.sh` with `nucleus_launcher`
- `spring-overlay` deploy mode: `deploy_membrane.sh spring-overlay root@<ip> --cell hotspring`
- Port SSOT reconciled with primalSpring `tolerances/mod.rs` (5 ports corrected)
- 93/93 tests, 13 new transport tests, zero clippy
- **Ready to deploy spring overlays**

### projectNUCLEUS (Wave 56)
- All 13 primal deploy cases support `--uds-only` with conditional port args
- `socket_health_check()` — UDS socket probe replaces TCP in VPS mode
- Config centralization, hardcoded port elimination, 65 Rust tests
- Cell graphs consumed (6 VPS-ready, 3 desktop-only)

### projectFOUNDATION (Wave 56b)
- Centralized env bootstrap (`deploy/lib/env.sh`) — 6 deploy libs
- Graph-driven health checks (no hardcoded primal names/ports)
- BLAKE3 fail-closed semantics
- CI expansion: `discover_port`, `discover_socket`, `_rpc_uds` mock tests

### lithoSpore (Wave 56)
- `emit-pseudospore --from-dir` — delegation path for re-emission
- 7/7 tier-0 checks passing in CI, parity workflow added
- Typed errors, hardcoding cleanup

### plasmidBin
- Harvests: sourDough + nestGate (May 28), biomeOS + bearDog (May 27)
- Centralized `DEFAULT_REMOTE_DIR` + env-driven paths
- Stale socket dirs cleaned: `/tmp/biomeos` → `/run/membrane`
- `deploy_membrane.sh`: full composition verification (Node + Meta tiers)

---

## Niche Climate Status (Wave 57)

```
NC-1  postPrimordial Spore Gateway    COMPLETE     All code delivered. Live deploy remaining.
NC-2  Multi-Gate NUCLEUS Mesh          IN PROGRESS  GAP-17/18 partially resolved. southGate stabilizing.
NC-3  cellMembrane Sovereignty         CONSUMED     VPS standard absorbed. Forgejo + NS cutover remaining.
NC-4  Spring NUCLEUS Depth             ADVANCING    projectNUCLEUS --uds-only. east/iron OK.
NC-5  lithoSpore postPrimordial        UNBLOCKED    NC-1.4 resolved. --from-dir shipped. Live deploy gated.
```

---

## Confirmed Cross-Team Answers

| Question | From | Answer |
|----------|------|--------|
| Is `health.liveness` the canonical health method? | projectFOUNDATION | **YES** — all primals implement `health.liveness`. primalSpring also aliases `health.check`. Certification Layer 2 uses `health.liveness`. |
| Are ports reconciled? | cellMembrane | **YES** — `ports.env` matches `tolerances/mod.rs` exactly (bearDog 9100, songbird 9200, ... petaltongue 9900). |
| Is NC-1 WIRED or COMPLETE? | projectNUCLEUS (stale) | **COMPLETE** — biomeOS v3.81 shipped `biomeos-pseudospore` + full emit materialization. Update your local NC-1 status. |

---

## Remaining Path to Stadial

| Step | Owner | Blocker |
|------|-------|---------|
| Deploy biomeOS v3.81 to VPS via plasmidBin | cellMembrane + ops | None (code ready) |
| hotSpring column U pass (first spring emission) | hotSpring + biomeOS | biomeOS v3.81 on VPS |
| groundSpring column U pass (second emission) | groundSpring + biomeOS | biomeOS v3.81 on VPS |
| southGate stabilize to 13/13 health | wetSpring/neuralSpring ops | Songbird peer config |
| NS registrar cutover (NC-3.3) | cellMembrane + registrar | External coordination |
| Forgejo releases (NC-3.4) | cellMembrane + plasmidBin | Forgejo instance config |

**Stadial entry**: NC-1 (2+ springs pass column U) + NC-2 (3+ gates) + NC-4 (all 4 gates healthy).

---

*Wave 57. Ecosystem converged. Deploy path clear. All teams aligned.*
