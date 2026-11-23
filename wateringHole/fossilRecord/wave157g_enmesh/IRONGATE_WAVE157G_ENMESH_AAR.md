# ironGate Wave 157g — Pipeline Enmesh AAR

**Date**: 2026-08-10 | **Wave**: 157g | **Gate**: ironGate
**Classification**: Composition graph foundation + gossip mesh survey + workload enrichment

---

## Summary

ironGate cascaded Wave 157g ENMESH blurb. Evolved `nucleus-deploy verify` with
biome.yaml manifest validation and RPC surface audit. Created the canonical
`biome-irongate.yaml` composition manifest. Documented gossip mesh reachability.
Enriched 28 workload dispatch TOMLs with `spring` metadata.

## Execution

### 1. Cascade

Pulled latest from Forgejo across key repos:
- **biomeOS**: routing fix (`e1376011` — 1 file, 25 insertions)
- **toadStool**: S375-S379 massive evolution (120 files, manifest convergence,
  WASM 38/48, Tokio blast radius, vestigial segmentation)
- **cellMembrane**: golgi CI post-receive hook (`2430a0b`)
- **coralReef**: dep cleanup (`525855d`)

### 2. ironGate Primal Status

**12/13 ALIVE** — 90 MB total RSS.

| Primal | Status | RSS |
|--------|--------|-----|
| beardog | ALIVE | 8 MB |
| songbird | ALIVE | 16 MB |
| skunkbat | ALIVE | 3 MB |
| biomeos | ALIVE | 15 MB |
| barracuda | ALIVE | 5 MB |
| coralreef | ALIVE | 4 MB |
| loamspine | ALIVE | 4 MB |
| nestgate | ALIVE | 5 MB |
| petaltongue | ALIVE | 8 MB |
| rhizocrypt | ALIVE | 7 MB |
| squirrel | ALIVE | 11 MB |
| sweetgrass | ALIVE | 6 MB |
| **toadstool** | **DEAD** | — |

**toadstool**: Latest 157e depot binary (13.7 MB) exhibits same clean-exit
behavior as previous G68 binary. Starts, binds sockets, hits mDNS multicast
errors on wg0/docker bridge, async runtime completes, exits code 0. Systemd
`Type=simple` reports active but process is gone. Primal team issue.

### 3. nucleus-deploy verify --manifest (NEW)

Created `manifest.rs` module for biome.yaml manifest validation:

- **Schema validation**: api_version, kind, metadata completeness
- **Primal registry cross-check**: every declared primal verified against
  `nucleus-primals` registry
- **Composition kind validation**: Tower/Nest/Node member lists cross-checked
  against registry constants (`COMP_TOWER`, `COMP_NEST`, `COMP_NODE`)
- **Dependency cycle detection**: DFS-based cycle detection on composition
  dependency graphs
- **Federation validation**: peer declarations checked
- **9 unit tests**: YAML parsing, cycle detection, stub detection, schema/primal
  validation

**Result on ironGate**: `29/29 PASS, 0 FAIL, 0 WARN`

### 4. biome-irongate.yaml (NEW)

Created canonical composition manifest for ironGate following toadstool-core v1 schema:

- 13 primals declared with capabilities, dependencies, binary paths
- 3 compositions: `tower-atomic`, `nest-atomic`, `node-atomic`
- Dependency ordering within each composition
- Readiness gates (require_healthy + timeout)
- Federation: 5 peers (sporeGate, blueGate, westGate, southGate, strandGate)
- Resource limits matching ironGate hardware (24 CPU, 96Gi, 1 GPU)

### 5. nucleus-deploy verify --audit-rpc (NEW)

Vertebrate self-audit RPC surface probe:

- **Liveness**: `health.liveness` per primal
- **Unknown method**: `__nonexistent_xyz__` — detects P0-A stub pattern
  (health response for any method)
- **BTSP gating**: domain-specific methods checked for -32001 rejection
- `probe_rpc()` added to `rpc.rs` for audit use

### 6. Gossip Mesh Reachability

| Peer IP | Gate | TCP 7800 |
|---------|------|----------|
| 10.13.37.2 | sporeGate | REACHABLE |
| 10.13.37.5 | eastGate | REACHABLE |
| 10.13.37.10 | strandGate | REACHABLE |
| 10.13.37.1 | golgiBody | UNREACHABLE |
| 10.13.37.11 | westGate | UNREACHABLE |

3/5 peers reachable. Consistent with blurb's "cross-gate gossip peers
unreachable" finding. Requires TCP 7800 firewall rules on unreachable gates.

### 7. Workload Dispatch TOML Enrichment

28 workload TOMLs enriched with `spring` metadata field:
- airspring: 6 files
- groundspring: 1 file
- healthspring: 4 files
- ludospring: 2 files
- neuralspring: 3 files
- wetspring: 12 files

Total: 43 workload TOMLs, all now discoverable by spring name.

## Files Modified

| File | Change |
|------|--------|
| `deploy/nucleus-deploy/Cargo.toml` | Added `serde_yaml` dependency |
| `deploy/nucleus-deploy/src/manifest.rs` | NEW: biome.yaml manifest validator (9 tests) |
| `deploy/nucleus-deploy/src/main.rs` | Added `mod manifest`, `--audit-rpc` and `--manifest` flags |
| `deploy/nucleus-deploy/src/verify.rs` | RPC surface audit + manifest dispatch |
| `deploy/nucleus-deploy/src/rpc.rs` | Added `probe_rpc()` helper |
| `gates/biome-irongate.yaml` | NEW: ironGate composition manifest (v1 schema) |
| `gates/irongate.toml` | Updated to Wave 157g, gossip, enmesh status |
| `specs/EVOLUTION_GAPS.md` | Wave 157g changelog, test count update |
| `workloads/*/*.toml` (28 files) | Added `spring` metadata field |

## Test Results

| Crate | Tests | Result |
|-------|-------|--------|
| darkforest | 149 | PASS |
| tunnelKeeper | 48+1 ignored | PASS |
| nucleus-deploy | 58 (+9 new) | PASS |
| nucleus-primals | 19 | PASS |
| **Total** | **274** | **0 FAIL** |

Clippy: 0 warnings (pedantic + nursery). Fmt: clean.

## Enmesh Status — What projectNUCLEUS Owns

| Item | Status |
|------|--------|
| biome.yaml manifest validation | **SHIPPED** — 29/29 on ironGate |
| RPC surface audit | **SHIPPED** — vertebrate self-check |
| Gossip mesh survey | **DOCUMENTED** — 3/5 peers, 2 firewall fixes needed |
| Workload dispatch enrichment | **DONE** — 43 TOMLs, all spring-tagged |
| toadstool startup | **BLOCKED** — primal team issue |
| sourDough CI | Not projectNUCLEUS — sporeGate + sourDough team |
| songBird MeshRelay | Not projectNUCLEUS — songBird team |
| swarmVine socket fix | Not projectNUCLEUS — biomeOS + gate ops |
| Manifest convergence | toadStool S377 DONE — nucleus-deploy consumes |

## Open Items for Enmesh Phase

1. **TCP 7800 on golgi + westGate**: firewall needs opening for gossip reachability
2. **toadstool startup**: primal team needs to investigate clean-exit behavior
3. **sourDough validate in CI**: sporeGate + sourDough team — 12 validators, none wired
4. **songBird MeshRelay**: relay gossip through :7700 when TCP 7800 fails

---

*Filed by ironGate code team. Wave 157g enmesh — composition graph foundation
shipped (manifest validation 29/29, RPC audit, gossip survey). 274 tests, 0 fail.
12/13 ALIVE, 90 MB. 0 P0, 0 P1, 2 P2.*
