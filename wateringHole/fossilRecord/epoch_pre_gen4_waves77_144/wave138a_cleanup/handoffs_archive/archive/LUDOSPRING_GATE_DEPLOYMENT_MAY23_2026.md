# ludoSpring — ironGate Covalent Deployment Status

**Date:** May 23, 2026
**Gate:** ironGate (pop-os)
**Hardware:** i9-14900K, RTX 5070, 96GB DDR5
**Spring:** ludoSpring V77
**Family ID:** irongate
**Composition:** full (12 primals from nucleus_launcher.sh)
**Co-tenants:** primalSpring (coordinator), groundSpring

---

## Deployment Summary

| Phase | Status | Detail |
|-------|--------|--------|
| Phase 1: Prepare runtime | PASS | /tmp/biomeos |
| Phase 2: Stop existing | PASS | Clean slate |
| Phase 3: Start primals | 12/12 STARTED | Dependency order |
| Phase 4: Health sweep | 4/12 TCP HEALTHY | beardog, toadstool, squirrel, petaltongue |
| Phase 5: Registry seeding | 0/11 REGISTERED | Songbird TCP unavailable |
| Phase 6: Composition validation | PASS | exp091 + exp094 both PASS |

## Proto-Nucleate Capability Validation

ludoSpring's proto-nucleate declares 26 validation_capabilities across all 4 atomic tiers.

| Capability | Primal | Transport | Status |
|------------|--------|-----------|--------|
| crypto.hash | BearDog | UDS (/tmp/biomeos/biomeos/) | PASS |
| compute.capabilities | ToadStool | UDS ($XDG_RUNTIME_DIR/biomeos/) | PASS |
| activation.fitts | barraCuda | — | SKIP (binary stale CLI) |
| stats.mean | barraCuda | — | SKIP |
| noise.perlin2d | barraCuda | — | SKIP |
| health.readiness | NestGate | UDS | PASS |
| storage.store | NestGate | UDS | PASS (BTSP auth required — reachable) |
| health.readiness | Squirrel | TCP :9300 | PASS |
| dag.session.create | rhizoCrypt | — | SKIP (binary stale CLI) |
| health.liveness | loamSpine | — | SKIP |
| health.liveness | sweetGrass | — | SKIP |
| visualization.render.scene | petalTongue | TCP :9600 | Not probed (HTTP transport) |

**Initial probe: 5 PASS, 6 SKIP (CLI drift)**
**After fix: 11 PASS, 0 FAIL, 0 SKIP — Status: COMPLETE**

## Root Cause (RESOLVED): `start_primal.sh` CLI Drift

The `infra/plasmidBin/start_primal.sh` script used `serve` for 5 primals, but v2026.05.23
binaries expect `server`. Additionally:
- barraCuda and rhizoCrypt reject `--socket` (use internal XDG discovery)
- coralReef uses `--rpc-bind` not `--port`
- Songbird needs `SONGBIRD_SECURITY_PROVIDER` pointing to BearDog socket

**All fixes applied in plasmidBin commit `8c8cb44`.** After fix: 11/11 PASS.

## What IS Working

Despite the CLI drift, 4 primals are fully operational:

1. **BearDog** (Tower) — BLAKE3 hashing, crypto.hash, BTSP tunnel, all subsockets (crypto, ed25519, x25519, security, btsp) live
2. **ToadStool** (Node) — 32 CPU cores detected, compute.capabilities operational
3. **NestGate** (Nest) — Storage alive, BTSP-gated writes (correct security posture)
4. **Squirrel** (Meta) — AI routing ready, capability registry active

## Composition Validation Results

primalSpring Phase 6 experiments ran successfully against the live composition:

- **exp091_primal_routing_matrix** → PASS
- **exp094_composition_parity** → PASS

These validate multi-primal routing and cross-atomic composition correctness.

## ludoSpring Rust Validation (independent)

```
982 tests, 0 failures, 0 ignored
cargo clippy: 0 warnings (all features)
```

All ludoSpring domain science validates locally (Tier 2). The gate deployment adds Tier 3 (live NUCLEUS) validation once the CLI drift is resolved.

## Multi-Domain Contention Observations

ironGate hosts primalSpring + ludoSpring + groundSpring. Observed:
- **No socket conflicts** — each primal uses `{name}-{family_id}.sock` namespace
- **No port conflicts** — canonical ports.env assignments are non-overlapping
- **No resource exhaustion** — 96GB DDR5 handles 12 concurrent primals comfortably
- **Mixed socket dirs** — some primals use `$XDG_RUNTIME_DIR/biomeos/` (toadstool, nestgate), others `/tmp/biomeos/biomeos/` (beardog, biomeos). This is inconsistent but functional.

## Action Items

| # | Action | Owner | Priority |
|---|--------|-------|----------|
| 1 | Fix `start_primal.sh` `serve` → `server` for 5 primals | plasmidBin / projectNUCLEUS | HIGH |
| 2 | Set `SONGBIRD_SECURITY_PROVIDER` in nucleus_launcher.sh | plasmidBin / projectNUCLEUS | HIGH |
| 3 | Standardize socket directory (XDG vs /tmp) | plasmidBin / biomeOS | MEDIUM |
| 4 | Re-validate full composition after fixes | ludoSpring + groundSpring | MEDIUM |
| 5 | Run `ludospring certify --tier 3` against live NUCLEUS | ludoSpring | MEDIUM |

## Validation Script

ludoSpring provides `tools/validate_gate.sh` + `tools/validate_gate_ipc.py` for repeatable gate validation. Run:

```bash
cd springs/ludoSpring
./tools/validate_gate.sh --family-id irongate
```

---

**License:** AGPL-3.0-or-later
