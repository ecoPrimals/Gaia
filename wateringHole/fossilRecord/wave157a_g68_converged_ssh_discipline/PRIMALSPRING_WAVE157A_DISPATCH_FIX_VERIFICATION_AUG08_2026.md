# primalSpring — Wave 157a Dispatch Fix Verification

**Date**: Aug 8, 2026 (evening session)
**Team**: primalSpring code team (eastGate)
**Wave**: 157a
**Context**: biomeOS dispatch reorder (`44c40191`) + routing gaps (`6f60cccf`) shipped

## Summary

The biomeOS Neural API dispatch reorder fix has been **verified live on eastGate**.
The 15-second timeout is eliminated. Capability routing and graph execution are
fully operational. A new experiment (exp121) specifically validates the remaining
riboCipher auto-detect gap.

## Results

### N2-N5 Verification (Dispatch Fix Confirmed)

| Experiment | Result | Key Improvement |
|-----------|--------|-----------------|
| exp118: Graph Execution | **14/14 ALL PASS** | Was 6/12 → now 14/14. Graph.list, graph.execute, graph.status all work |
| exp119: PathwayLearner | **12/12 ALL PASS** | 919 exec/s throughput, CV=0.60 timing consistency |
| exp120: Self-Registration | **29/29 ALL PASS** | 34 caps, 58 methods, 11/11 domains resolve |
| exp121: riboCipher Auto-Detect | **32/36 PASS** | Dispatch proven (mean 1.3ms, max 2.5ms). Gap confirmed. |

### Dispatch Reorder Verification

| Metric | Before (Jul 15 binary) | After (44c40191) |
|--------|------------------------|-------------------|
| Mean latency | 15,000ms (timeout) | **1.3ms** |
| Max latency | 15,000ms | **2.5ms** |
| Forwarding success | 0/11 primals | **9/11 primals** |
| Graph execution | 0 (not found) | **55 graphs, 1.2ms/exec** |

### Protocol Classification (exp121 Phase 1+2)

| Primal | Protocol Affinity | Forward via Neural API |
|--------|-------------------|----------------------|
| beardog | Plain only | **PASS** |
| songbird | Dual-lane | **PASS** |
| skunkbat | Dual-lane | **PASS** |
| sweetgrass | **riboCipher ONLY** | FAIL (auto-detect gap) |
| rhizocrypt | Dual-lane | **PASS** |
| loamspine | Dual-lane | **PASS** |
| toadstool | N/A (TARPC) | FAIL (protocol mismatch) |
| coralreef | Dual-lane | **PASS** |
| barracuda | Dual-lane | **PASS** |
| squirrel | Dual-lane | **PASS** |
| petaltongue | Dual-lane | **PASS** |

## What Was Delivered

### exp121: riboCipher Dispatch Auto-Detect (NEW)

A targeted experiment that:
1. Probes each primal directly to classify protocol affinity
2. Tests Neural API `capability.call` forwarding per-primal
3. Measures dispatch timing to prove reorder fix
4. Identifies the riboCipher auto-detect gap

This experiment serves as the **acceptance test** for when biomeOS ships
the auto-detect fix: once sweetGrass accepts forwarded calls, exp121 will
go from 32/36 → 36/36.

### exp118 Fix

Updated to use `health.check` (working method) instead of `sign_ed25519`
(requires beardog-specific operation), and added `"primals"` field check
in `capability.discover` response parsing.

## Remaining Gap: riboCipher Auto-Detect — LOADING PATH BUG **FIXED** (`d1f555e7`)

**Status**: Loading path bug identified AND fixed. Commit `d1f555e7` pushed to
golgiBody. Both the TOML loading path AND capability.call direct dispatch path
now use riboCipher auto-detect.

### Root Cause (verified Aug 8 evening)

The neural-api startup called `load_defaults_for_family()` which went directly
to **compiled defaults** (118 hardcoded translations without `ribocipher` flag).
The TOML-based loading path (`load_defaults_into()` → `load_from_registry_toml()`)
which correctly reads `ribocipher = true` from `config/capability_registry.toml`
was only triggered when NO explicit family_id was provided.

Additionally, the `capability.call` direct dispatch path (for methods not in the
translation registry) used plain forwarding unconditionally, without checking the
domain-level ribocipher flag.

### Fix Applied (`d1f555e7`)

1. **translation_startup.rs**: Changed `load_defaults_for_family()` →
   `load_defaults()` (tries TOML first: 430 entries with ribocipher flags)
2. **mod.rs**: Added `domain_ribocipher` HashMap and `domain_requires_ribocipher()`
   accessor to `CapabilityTranslationRegistry`
3. **toml_loader.rs**: Persists domain-level ribocipher flags into the registry
   during TOML loading (domain + per-capability aliases)
4. **direct.rs**: Checks `domain_requires_ribocipher()` in the `capability.call`
   fallback path and uses `forward_request_ribocipher()` when needed

### Verification

```
capability.call(braid, health.check)      → sweetGrass PASS (riboCipher auto-detect)
capability.call(attribution, health.check) → sweetGrass PASS
capability.call(provenance, health.check)  → sweetGrass PASS
provenance.create_braid (translated)       → sweetGrass PASS (TOML ribocipher flag)
capability.call(crypto, health.check)      → beardog PASS (plain preserved)
```

**Note**: The depot rebuild now WILL enable auto-detect fleet-wide (the loading
path is fixed). Only primal socket stability (Jul 15 binary age) remains as a
blocker for full 11/11 forwarding.

## ADDENDUM: eastGate Depot Deployment (Aug 8 evening)

Rebuilt binaries pulled from sporeGate and deployed to eastGate NUCLEUS:
- biomeOS v4.57.0 (16.9 MB musl) — `biomeos neural-api` mode with LimitNOFILE=65536
- songBird v0.2.1 (19.3 MB musl) — includes swarmVine gossip.inject seam
- cellMembrane (17.0 MB musl) — transport unification
- swarmVine Phase 2 (2.6 MB musl) — epidemic sweep + cross-gate TCP :7800

### Verification Results

| Test | Result |
|------|--------|
| Primals announced | 11/11 |
| Capability routing | 6/7 (sweetGrass socket timeout) |
| riboCipher auto-detect | CONFIRMED (dag→rhizoCrypt 7ms) |
| Dispatch mean | **1.0ms** |
| Dispatch max | **1.1ms** |
| swarmVine via Neural API | PASS (1ms) |
| songBird mesh.health | PASS (2ms) |

### Fleet Status After Deployment

- **eastGate**: 15/15 ALIVE (biomeOS + songBird + swarmVine + 12 primals)
- **sporeGate**: 15/15 ALIVE (depot rebuilt)
- Other gates: awaiting `plasmid.harvest` or rsync of depot binaries

### toadStool Protocol Mismatch

toadStool uses TARPC (not JSON-RPC) on `compute-tarpc.sock`. The Neural API
JSON-RPC forwarding is fundamentally incompatible. This requires either:
- toadStool adds a JSON-RPC shim endpoint, OR
- Neural API adds TARPC forwarding support

This is a longer-term architecture decision, not a P1.

## Test Results

- 1,219 workspace tests pass (3 pre-existing env failures)
- 99 experiments (exp121 added)
- 198 validation scenarios (15 tracks, 3 tiers)
- Zero new regressions

## Infrastructure Notes

- Neural API debug binary (with fix) must be used; depot binary is Jul 15 (pre-fix)
- Graph executor requires `~/graphs` symlink → primalSpring graphs dir
- Primal sockets require services to be running (not just process alive)
- songBird needs stale PID cleanup before restart
- **sweetGrass socket instability**: socket file disappears within 30-60s of service restart
  on the Jul 15 binary. `ss -xlp` shows the abstract socket still bound but filesystem
  entry is gone. Depot rebuild with stable binaries will resolve this.
- **Loading path bug** means depot rebuild alone won't enable auto-detect — code fix needed first

---

## ADDENDUM: Vine-Bat Loop Verification (Aug 9)

Depot binaries synced from sporeGate (biomeOS 16.9 MB, skunkBat 3.3 MB, swarmVine 2.6 MB)
— all include vine-bat hook stack (`df97b25` + `e602e09` + `d1f555e7`).

### Deployment

- `membrane-nucleus@.service` template: `LimitNOFILE=65536` (P1 FIX — all primals)
- `membrane-nucleus@swarmvine.service`: `LimitNOFILE=65536` + `SWARMVINE_SKUNKBAT_SOCK`
- All services restarted, 13/13 active

### Verification Results

| Test | Result |
|------|--------|
| skunkBat `metadata.analyze` (good entry) | **8/8 checks PASS**, verdict `allow` |
| skunkBat `metadata.analyze` (bad key) | verdict `warn`, blocked |
| swarmVine `gossip.inject` | PASS |
| Neural API → `gossip.status` | PASS (routed via capability.call) |
| Primals announced | **29** (full NUCLEUS + aliases) |
| biomeOS FD limit | 65536 |
| swarmVine FD limit | 1048576 |

### P1 Status — eastGate FD Exhaustion: **FIXED**

- `membrane-nucleus@.service` template now includes `LimitNOFILE=65536`
- All dedicated units (biomeOS, swarmVine) also include the limit
- Applied on: **sporeGate, ironGate, eastGate** (3/6)
- Remaining: westGate, strandGate, blueGate, southGate

### Capability Registry Sync

primalSpring `config/capability_registry.toml` synced with biomeOS `2fae9144`:
- Added: `dag.query`, `spine.list`, `spine.status`, `entry.list`, `braid.verify`,
  `content.stat`, `content.ingest`
- All 52 registry routing tests PASS
