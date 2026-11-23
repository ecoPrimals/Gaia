# Wave 106 Blurb — Remaining Work by Team

**Date**: 2026-06-10
**From**: eastGate overwatch

**State**: Deterministic deployment is achieved. 3-gate mesh collective LIVE (eastGate↔golgiBody↔ironGate). `gate.bootstrap` goes from zero → fully operational in one command. The pipeline is end-to-end. What follows is the remaining work to reach stadial and autonomous operation.

---

## To: biomeOS — NUCLEUS Supervision (sole P1)

NUCLEUS primals run as bare processes. They die silently with no restart, no detection, no self-repair. This happened 3+ times during Wave 105. Manual operator intervention every time.

**Action** — implement one of:
- `lifecycle.watchdog` — poll `health.liveness` every 30s, restart failures from depot binaries
- systemd user unit generation — `composition.deploy` creates per-primal `.service` files
- `--supervised` mode in `nucleus-deploy` that registers with systemd

**Why P1**: This is the single gap between "deployment works" and "deployment is autonomous." Every other layer is shipped. Once supervision lands, gates self-heal.

**Integration point**: `gate.bootstrap` can install the watchdog as its 7th phase once available.

---

## To: cellMembrane — VPS Depot Rebuild (operational)

All development items are **COMPLETE**. One operational action:

**Action**: Rebuild songbird on peptidoglycan and push to outer membrane depot. The VPS depot still serves songbird v0.2.1 (pre-persistence, pre-federation-port-fix). flockGate's WAN e2e validation is blocked on this — the fetched songbird cannot complete a bidirectional mesh handshake.

**Post-stadial** (from flockGate's guideStone analysis):
- Serve `checksums.toml` from WAN depot endpoint for zero-git verification
- Atomic depot rebuild + checksums.toml publication (currently decoupled)
- `--dry-run` for `gate.bootstrap` (pre-validation without side effects)
- `gate.status` command for already-bootstrapped gates

---

## To: primalSpring — grapheneGate TCP-Only Fallback (4 primals)

9/13 primals running on Pixel 8. 4 exit fatally on UDS bind SELinux denial:

| Primal | Failure | What's Needed |
|--------|---------|---------------|
| coralreef | `EACCES` on UDS bind | TCP-only fallback |
| nestgate | `EACCES` on UDS bind | TCP-only fallback |
| biomeOS | `EACCES` on UDS bind | TCP-only fallback |
| petaltongue | `EACCES` on UDS bind | TCP-only fallback |

**Pattern**: `bind_uds()` → `Err(EACCES)` → `fallback_to_tcp(localhost:PORT)`

The deploy script cannot work around a fatal exit — each primal needs an upstream code change to gracefully degrade. `BIOMEOS_SOCKET_DIR` and `TRANSPORT_ENDPOINT` env vars are already shipped.

---

## To: songBird — Clear (future: mDNS)

Both P1 items shipped (mesh persistence + federation port fix). No blockers for stadial.

**Future**: mDNS/LAN auto-discovery (already wired in discovery layer). Low priority — VPS relay bootstrap is sufficient.

---

## To: flockGate — WAN e2e Completion (blocked on cellMembrane)

4/5 stages PASS. Blocked on stale VPS songbird binary (see cellMembrane action above). Once rebuilt:
1. Re-fetch songbird from VPS
2. Restart songbird with federation
3. Verify bidirectional mesh handshake
4. 5/5 → stadial criterion 4 met

**Post-stadial**: Your guideStone-grade analysis identified 5 evolution gaps — depot integrity chain, deployment manifest, health convergence tolerances, WAN verification gate, depot version tracking. These shape the post-stadial roadmap but don't block entry.

---

## To: all gates — Enrollment Playbook

`gate.bootstrap` or manual procedure in FRAGO (`wave106-cross-topology-validation.toml`).

**DO NOT** `cargo build --release` for deployment. VPS `plasmidBin` is the sole binary authority.

| Gate | Status | Next Action |
|------|--------|-------------|
| eastGate | OPERATIONAL (23 RPC + 3 tarpc) | — |
| golgiBody (VPS) | OPERATIONAL (13/13, mesh hub) | Rebuild songbird in depot |
| ironGate | VALIDATED (3rd mesh node, 12/13) | — |
| strandGate | VALIDATED (LAN re-enrollment) | Power-on when needed |
| flockGate | 4/5 WAN e2e | Awaiting depot rebuild |
| grapheneGate | 9/13 (Pixel 8) | Awaiting TCP-only fallback |
| southGate | Unknown | Power-on + gate.bootstrap |

---

## Ecosystem Snapshot

| Metric | Value |
|--------|-------|
| P1 remaining | **1** — NUCLEUS supervision (biomeOS) |
| P2 remaining | **3** — VPS depot rebuild, grapheneGate 4 primals, flockGate WAN 5/5 |
| Mesh | 3-gate collective (eastGate↔golgiBody↔ironGate) |
| Depot | 13/13 x86_64 verified, 14/14 aarch64 built, 13/13 WAN serving |
| Transport | 11/11 non-exempt complete |
| Cascade | 38/38 clean |
| Deterministic deploy | Codified — gate.bootstrap 6/6 invariants |
| Sovereignty | S1-S3 graduated, S4 ending |

---

## Reference

- `wave106-cross-topology-validation.toml` — active FRAGO
- `AAR_CELLMEMBRANE_WAVE106_DETERMINISTIC_DEPLOYMENT_JUN10_2026.md` — deployment standard
- `wave106-flockgate-wan-deployment-aar.toml` — guideStone-grade WAN analysis
- `GLACIAL_SHIFT_READINESS.md` — ecosystem readiness (Wave 106 final)
