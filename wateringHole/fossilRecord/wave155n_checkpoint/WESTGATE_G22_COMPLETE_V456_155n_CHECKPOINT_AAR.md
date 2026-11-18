# AAR: westGate biomeOS v4.56 G22-Complete Deployment — Wave 155n Checkpoint

**Date**: Jul 31, 2026 17:30 EDT
**Gate**: westGate
**Wave**: 155n (checkpoint — clearing for springs+gardens)
**Author**: westGate overwatch (agent-assisted)
**biomeOS**: v4.56.0 (G22 COMPLETE — `b82f0925`)

---

## TL;DR

biomeOS v4.56 G22-complete deployed on westGate. All modes unified — `biomeos api` and
`biomeos neural-api` both launch dual-protocol (HTTP + JSON-RPC). The standalone
`neural-api` mode is deprecated with runtime warning. 13/13 services live, 30/30 sockets
stable over 2 min, 835 capabilities, Provenance 7/7 (8th consecutive pass). ZFS raidz1
50.7 TB pool healthy. cellMembrane J18 gate coupling fix cascaded. sporePrint restructured
for demonstration era. **Zero P0/P1/P2. gen4 COMPLETE.**

---

## What Shipped Upstream (This Cascade)

### biomeOS — G22 COMPLETE (`b82f0925`, `6a698078`, `85e8bdc1`, `bd96dbcd`)

| Commit | Change | Impact |
|--------|--------|--------|
| `b82f0925` | G22 steps 3-5: api+neural-api → dual-protocol in both modes | Springs+gardens can build against any biomeOS entry point |
| `6a698078` | Remove 8 dead deps from tools/ workspace (47 total removed) | Clean dependency tree |
| `85e8bdc1` | cargo deny clean + rustfmt | Zero warnings |
| `bd96dbcd` | v4.56 version bump + G22 convergence handoff | Version reporting correct |

**Key architectural change**: `biomeos api` now launches the Neural API alongside HTTP.
`biomeos neural-api` now launches the HTTP API alongside JSON-RPC. Both entry points
provide both protocols. This is the foundation springs+gardens will build against.

### cellMembrane — J18 Gate Coupling Fix (`882ad09`, `edb7f4d`)

| Commit | Change | Impact |
|--------|--------|--------|
| `882ad09` | J18: `env_or()` migration + gate-name identity bridge | User-space deploy paths resolve correctly (steamGate, southGate). Gate identity file written during bootstrap. |
| `edb7f4d` | TargetArch deprecation + `resolve_xdg_runtime_dir` dedup | Cleaner API, less duplication |

### sporePrint — Demonstration Era (`d66b6b9`, `0236634`)

Site restructured from conceptual to demonstration era: getting-started guide, backstory,
foundation sections, live evidence woven across architecture/science/products. 87 files
changed. sporePrint is now content-ready for `zola build` on golgi VPS.

### wateringHole — 5 New Entries

Fossilization wave: 14 AARs → `fossils/`. Wave 155n checkpoint blurb reshaped for
springs+gardens transition. SporeGate cascade logs absorbed.

---

## Deployment Details

### Binary Update

| Binary | Old Version | New Version | Old Size | New Size |
|--------|-------------|-------------|----------|----------|
| biomeos | 4.55.0 | **4.56.0** | 20,523 KB | 20,551 KB |
| membrane | — | — | 16,072 KB | 16,094 KB |

### NUCLEUS State

| Metric | Value |
|--------|-------|
| Services | **13/13** active |
| Sockets (membrane/) | **30** |
| Sockets (biomeos/) | **6** (stragglers — symlinked to membrane/) |
| Capabilities | **835** |
| biomeOS Mode | COORDINATED |
| Socket stability | **30/30 over 2 min** — zero drift |

### Provenance 7/7 — Pass #8

| Step | Method | Result |
|------|--------|--------|
| 1 | `content.put` (nestGate) | PASS |
| 2 | `content.get` (nestGate) | PASS |
| 3 | `health.check` (rhizoCrypt) | PASS |
| 4 | `spine.create` (loamSpine) | PASS |
| 5 | `crypto.sign_ed25519` (bearDog) | PASS |
| 6 | `braid.create` (sweetGrass) | PASS |
| 7 | `health.check` (sweetGrass) | PASS |

8th consecutive pass across biomeOS v4.50 → v4.51 → v4.55 → v4.56.

### ZFS raidz1 Pool

| Metric | Value |
|--------|-------|
| State | ONLINE, zero errors |
| Usable capacity | **50.7 TB** |
| CAS data | 12.1 MB (4 prefix dirs) |
| L2ARC | 2 TB SSD online |

---

## Convergence Status

### Socket Namespace (G22 Goal)

biomeOS v4.56 G22 unified all internal paths to `membrane/`. On westGate:
- 30/30 sockets in `/run/user/1000/membrane/`
- 6 legacy sockets in `/run/user/1000/biomeos/` (symlinked to membrane/)
- Symlink bridge still needed for stragglers, but count dropped from 31 to 6

This is as converged as it gets without updating all primal binaries themselves.

### Service Unit Status

`neural-api-tower.service` still uses the deprecated `neural-api` subcommand. This works
(deprecated with runtime warning, not removed). Migration to `biomeos api` subcommand is
a non-blocking cleanup for a future wave — the flags differ slightly between modes.

---

## What's Next for westGate

### Immediate (this wave)

1. **AlphaFold ingestion** — 50.7 TB ZFS pool is ready, pipeline is ready. This is the
   first real science workload through NUCLEUS.
2. **Service unit migration** — Optional: switch from `neural-api` to `api` subcommand.

### Springs+Gardens (next wave)

Per the blurb, 4 items must clear before springs+gardens:
1. ~~G22 steps 3-5~~ → **COMPLETE** (this AAR)
2. J12 sub-builder IPC wire → sporeGate + blueGate
3. sporePrint `zola build` → sporeGate
4. J18 gate coupling → **CODE SHIPPED** (`882ad09`), needs gate validation

Then westGate roles in springs+gardens:
- **G7**: AlphaFold ingestion through Nest Atomic CAS on ZFS
- **G18**: squirrel → biomeOS agent dispatch endpoint (once springs exist)
- **Science pipeline**: tideGlass Phase 0 → Nextflow → pseudoSpore → JOSS

---

## Gate Summary

| Gate | biomeOS | NUCLEUS | Provenance | Notes |
|------|---------|---------|------------|-------|
| **westGate** | **v4.56** (G22) | **13/13** | **7/7** (×8) | This AAR. ZFS 50.7 TB. |
| strandGate | v4.51 | 12/12 | — | Needs v4.56 redeploy |
| blueGate | — | 13/13 | 7/7 | Windows. J12 unblocked. |
| sporeGate | v4.56 | 11/11 | — | Depot current. Sovereign CI. |

---

## Observations

1. **G22 unification is clean**: Both modes now launch both protocols. No observable
   regressions. Capabilities, socket stability, and provenance all unaffected.

2. **Socket evaporation is dead**: 8 consecutive checks (v4.55 → v4.56) with zero socket
   drift. The PID ownership guard + dual-protocol health ping is a complete fix.

3. **Symlink bridge shrinking**: From 31 sockets in the first deployment to 6 stragglers.
   Full convergence requires updated primal binaries that natively write to `membrane/`.

4. **neural-api deprecation is safe**: The subcommand still works, just emits a warning.
   No urgency to migrate service units — springs+gardens can start building now.

5. **ZFS raidz1 performing well**: 50.7 TB available, zero errors, 1.56× compression.
   Ready for AlphaFold (~23 TB estimated).

---

*westGate — biomeOS v4.56 G22-complete. 13/13 NUCLEUS. 30/30 sockets. 835 caps.
Provenance 7/7 (×8). ZFS 50.7 TB. ZERO P0/P1/P2. gen4 COMPLETE. Ready for
springs+gardens.*
