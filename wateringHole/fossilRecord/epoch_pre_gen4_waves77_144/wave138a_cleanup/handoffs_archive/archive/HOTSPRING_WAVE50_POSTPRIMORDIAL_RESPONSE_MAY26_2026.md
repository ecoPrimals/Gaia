# hotSpring Wave 50: postPrimordial + Covalent Ready

**Spring:** hotSpring
**Date:** May 26, 2026
**Wave:** 50 (postPrimordial)
**Gate:** biomeGate (Threadripper 3970X, 256GB, Titan V + RTX 5060)
**Response to:** `DELTA_SPRING_WAVE50_COVALENT_HPC_BLURB_MAY25_2026.md`

---

## Status

```
hotSpring Wave 50: NUCLEUS 6/12 on biomeGate, peers seeded, covalent ready
```

| Requirement | Status |
|-------------|--------|
| `target/release/` primal hardcodes removed | DONE — plasmidBin resolution in `validate-primal-proof.sh` |
| plasmidBin-only binary sourcing | DONE — `find_plasmidbin()` helper, barracuda from depot |
| NUCLEUS operational on biomeGate | DONE — 6 primals responding (beardog, songbird, coralreef, nestgate, toadstool, rhizocrypt) |
| Songbird peers seeded | DONE — `mesh.init` with node_id=biomeGate, bootstrap eastGate |
| Proto-nucleate manifest | DONE — `graphs/downstream/downstream_manifest.toml` |
| Tier 2→3 parity wiring | DONE — `nest-validate parity` invokes plasmidBin barracuda |
| pseudoSpore GuideStone v1.5.0 | DONE — 12/12 audit PASS, BLAKE3 native |
| CompChem pipeline pure Rust | DONE — no Python/bash jelly in active validation |

## What Changed

### postPrimordial Compliance

- `scripts/validate-primal-proof.sh`: Added `find_plasmidbin()` helper. Primary path
  resolves barracuda from `infra/plasmidBin/barracuda/barracuda`. Falls back to local
  workspace only if plasmidBin unavailable. Pre-flight also resolves primalspring from depot.
- `scripts/build-guidestone.sh`: Annotated as artifact PRODUCTION (creates plasmidBin
  contents from source). Not a deployment script — `target/release/` is intentional here.

### NUCLEUS biomeGate

- Family: `hotspring-biome`
- Active primals: beardog (v0.9.0), songbird, coralreef, nestgate, toadstool, rhizocrypt
- 12 UDS sockets operational
- Songbird `mesh.init` completed: node_id=biomeGate, bootstrap_peers=[192.168.1.144:7700]
- Federation port (7700): needs Songbird restart with `SONGBIRD_FEDERATION_PORT=7700`

### Parity Wiring

- `nest-validate parity` subcommand added (pure Rust):
  - Resolves barracuda from plasmidBin (postPrimordial standard)
  - Runs `barracuda validate` for Tier 3 GPU check
  - Runs native `cazyme-fel` Gaussian FES reconstruction for Tier 2 CPU check
  - Graceful degradation when no GPU available (SKIP, not FAIL)
  - Reports cross-tier convergence/divergence status

### CompChem Pipeline (jelly elimination complete)

All validation logic is now pure Rust in `nest-validate`:
- `guidestone validate` — replaces 147 lines of bash (BLAKE3 + science + parity)
- `guidestone finalize` — replaces 135 lines of bash+Python (FES + parity + populate)
- `guidestone refresh` — replaces 44 lines of bash (freshness check)
- `parity` — new: Tier 2→3 convergence via plasmidBin barracuda
- Native FES reconstruction via `cazyme-fel` — no `plumed sum_hills` dependency

## Gaps (Active)

| ID | Description | Severity | Owner |
|----|-------------|----------|-------|
| GAP-HS-111 | barraCuda bonded FF + topology + metadynamics shaders | Medium | hotSpring |
| GAP-HS-113 | Federation port 7700 not bound (needs Songbird restart) | Low | hotSpring |
| GAP-HS-114 | barracuda plasmidBin binary lacks CPU test pool fallback | Low | barraCuda |

## Next

- Restart Songbird with `SONGBIRD_FEDERATION_PORT=7700` for LAN mesh
- Complete ABG FEL refresh simulations (enzyme-bound 2D in progress)
- Run `nest-validate guidestone finalize` to emit v1.6.0 with full parity data
- Begin covalent HPC: `toadstool.compute` dispatch for CAZyme FEL via NUCLEUS

---

*biomeGate is postPrimordial. Binary truth flows through plasmidBin.
Parity wired. Mesh seeded. CompChem pipeline: pure Rust, no jelly.*
