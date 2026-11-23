# Wave 63 — Primal Mountain: Temporal Sync Onboarding

**Date**: May 30, 2026
**From**: primalSpring coordination (eastGate)
**To**: All primal teams across all gates
**Phase**: Mountain CLEAR → temporal sync adoption

---

## Summary

Primal mountain code debt is **zero across all 13 NUCLEUS primals**. 13/14 upstream
Neural API methods shipped. The sole remaining mountain item (SouthGate redeploy) is
an ops task, not code. Wave 62 delivered the waterFall temporal sync — the ecosystem
now has a Rust-native multi-remote DAG sync system. This handoff brings each primal
team onto the temporal sync.

---

## What Changed (Wave 62)

- `cascade-pull.sh --source temporal` is live and delegates to the Rust `membrane` binary
- `ecosystem_manifest.toml` v2.1.0: `default_source = "temporal"`, 5 repos bidirectional
- 5 Forgejo repos converted from pull mirrors to bidirectional push: **biomeOS**, **coralReef**, **sweetGrass**, **squirrel**, **wateringHole**
- Gate identity resolution: `.gate` file + `GATE_NAME` env (no hostname heuristics)
- `membrane` binary: `temporal.check`, `temporal.sync`, `manifest.info`, `identity.resolve`

---

## Per-Gate Actions

### eastGate (squirrel, primalSpring, cellMembrane)

**Status**: Already pushing bidirectional (GitHub + Forgejo). Temporal sync validated.

- [x] Pull updated wateringHole
- [x] `.gate` file exists (`eastGate`)
- [x] `cascade-pull.sh --source temporal` tested
- [ ] Run `temporal.check` across all local repos — verify no divergence

### southGate (biomeOS team)

**Status**: biomeOS Forgejo repo is bidirectional. Gate needs sync tooling.

- [ ] `git pull` wateringHole to get updated `cascade-pull.sh` + manifest
- [ ] Create `.gate` file: `echo "southGate" > /path/to/ecoPrimals/.gate`
- [ ] Set env: `export GATE_NAME=southGate` in shell profile
- [ ] Run: `cascade-pull.sh --mode check --source temporal`
- [ ] If clean, run: `cascade-pull.sh --mode pull --source temporal`
- [ ] Push biomeOS: `git push forgejo main`  (K-Derm relay mirrors to GitHub)
- [ ] **NUCLEUS redeploy**: `plasmidbin fetch --all --force && plasmidbin launch` (pending since Wave 53)
- [ ] Verify: `SONGBIRD_PEERS=192.168.1.144:7700` in environment

### strandGate (coralReef, sweetGrass teams)

**Status**: Both Forgejo repos are bidirectional. Gate needs sync tooling.

- [ ] `git pull` wateringHole
- [ ] Create `.gate` file: `echo "strandGate" > /path/to/ecoPrimals/.gate`
- [ ] Set env: `export GATE_NAME=strandGate`
- [ ] Run: `cascade-pull.sh --mode check --source temporal`
- [ ] Push coralReef: `git push forgejo main`  (K-Derm relay mirrors to GitHub)
- [ ] Push sweetGrass: `git push forgejo main`

### ironGate (agentic dev)

**Status**: Pull-only consumer. No bidirectional repos assigned yet.

- [ ] `git pull` wateringHole
- [ ] Create `.gate` file: `echo "ironGate" > /path/to/ecoPrimals/.gate`
- [ ] Run: `cascade-pull.sh --mode pull --source temporal`
- [ ] Verify all primals at temporal leader position

### biomeGate (hotSpring, HBM2 test bench)

**Status**: Pull-only consumer.

- [ ] `git pull` wateringHole
- [ ] Create `.gate` file: `echo "biomeGate" > /path/to/ecoPrimals/.gate`
- [ ] Run: `cascade-pull.sh --mode pull --source temporal`
- [ ] Restart Songbird with `SONGBIRD_FEDERATION_PORT=7700` + `SONGBIRD_PEERS`

---

## Per-Primal Mountain Status

All clear. No code debt. Summary for each sentinel and NUCLEUS primal:

| Primal | Gate | Status | Wave 62 Note |
|--------|------|--------|--------------|
| **bearDog** | eastGate | CLEAR (14,940+ tests) | UDS-only, ACME daemon operational. S4 auth ready for shadow period. |
| **Songbird** | eastGate | CLEAR (8,070+ tests) | `mesh.init` + `bootstrap_peers` wired. Cross-gate `discovery.peers` needs live test. |
| **toadStool** | eastGate | CLEAR (9,156+ tests) | Zero production panics. 9-cap Node Atomic. |
| **NestGate** | eastGate | CLEAR (v0.5.0 unified) | 83.61% coverage, pushing to 90%. Ready for VPS deploy. |
| **biomeOS** | southGate | CLEAR (v3.88) | Neural API 260+ translations. `spore.instantiate`, `composition.status`. Forgejo **bidirectional**. |
| **coralReef** | strandGate | CLEAR (3,234 tests) | Wave 61 math completeness. Forgejo **bidirectional**. |
| **sweetGrass** | strandGate | CLEAR (v0.7.39) | Wave 63 race conditions fixed. Forgejo **bidirectional**. |
| **squirrel** | eastGate | CLEAR | Multi-MCP coordination. Forgejo **bidirectional**. |
| **barraCuda** | eastGate | CLEAR (4,501+ tests) | 806 WGSL shaders. All IPC handler gaps closed. |
| **rhizoCrypt** | eastGate | CLEAR | DAG engine. Startup latency fixed. |
| **loamSpine** | eastGate | CLEAR (1,528 tests, 90.92%) | Tokio runtime-in-runtime panic remains (upstream, not blocking). |
| **petalTongue** | eastGate | CLEAR | WASM live. `--family-id` accepted. |
| **skunkBat** | eastGate | CLEAR | BLAKE3 fingerprint in manifest. |

---

## Temporal Sync Validation Checklist

After each gate completes the actions above, verify:

```bash
# Check temporal position for all repos on this gate
cascade-pull.sh --mode check --source temporal

# Expected output per repo:
#   REPO: <name>
#     origin: behind=0 ahead=0
#     forgejo: behind=0 ahead=0
#   Classification: CONVERGED
```

Any repo showing `DIVERGE` needs manual investigation — the divergence policy is
`flag` (report, don't auto-merge).

---

## What's Next After Mountain

Mountain is the foundation. Once all gates confirm temporal sync:

1. **cellMembrane** (Phase 2): VPS Nest expansion, sovereign DNS, remaining mirror conversions
2. **Springs** (Phase 3): Proto-nucleate deployment on assigned gates, cross-gate capability routing
3. **Sovereignty** (H2): S4 auth shadow period, formal 7-day cutover for S1-S3

---

## Success Criteria

- [ ] All 5 active gates have `.gate` files
- [ ] All 5 active gates can run `cascade-pull.sh --source temporal` without errors
- [ ] biomeOS, coralReef, sweetGrass pushed bidirectionally from their home gates
- [ ] SouthGate NUCLEUS redeployed (13/13 primals)
- [ ] Zero `DIVERGE` classifications across ecosystem
