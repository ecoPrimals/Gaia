# wetSpring — Wave 157g→157i G72 Compliance + Gossip Injection COMPLETE

**Date**: Aug 11, 2026
**Wave**: 157i — Pandemic Responds
**Primal**: wetSpring
**Gate**: westGate
**From**: overwatch (eastGate)

## G72 Dependency Pandemic — Tier 1 COMPLETE

wetSpring was already G72-lean before this wave:

| Metric | Status | Detail |
|--------|--------|--------|
| **pollster** | REMOVED (V211) | Replaced with tokio `rt` current-thread |
| **tokio features** | MINIMAL | `["rt", "macros"]` — never `["full"]` |
| **HTTP clients** | ZERO | No ureq, no reqwest — routes through `capability.call` |
| **YAML fragmentation** | ZERO | Uses TOML only |
| **env_logger** | ZERO | tracing only |
| **axum** | 0.8 | Aligned with canonical |
| **wgpu** | 28 | Aligned with canonical |
| **thiserror** | 2 | Aligned with canonical |
| **Test deps** | `[dev-dependencies]` | tempfile, temp-env, proptest properly gated |
| **Dead deps** | ZERO | All 320 lockfile crates are transitively necessary |

**bingocube-nautilus path fix**: Corrected stale path reference (`bingoCube/nautilus` → `bingoCube/crates/nautilus`).

## Gossip Injection — WIRED

### Architecture

```text
handle_full_pipeline()              ──→ gossip::emit(PipelineComplete)   ──→ gossip.spread → swarmVine
handle_provenance_complete()        ──→ gossip::emit(ProvenanceWitness)  ──→ gossip.spread → swarmVine
handle_ncbi/chembl/pubchem_fetch()  ──→ gossip::emit(DataIngested)       ──→ gossip.spread → swarmVine
handle_register_table()             ──→ gossip::emit(DataIngested)       ──→ gossip.spread → swarmVine
composition.science_health (pass)   ──→ gossip::emit(ValidationPass)     ──→ gossip.spread → swarmVine
```

### Events

| Event | Domain | Trigger |
|-------|--------|---------|
| `PipelineComplete` | science | Full 16S rRNA pipeline completes |
| `ValidationPass` | science | `composition.science_health` confirms trio + nestGate live |
| `ProvenanceWitness` | provenance | Provenance session committed via trio |
| `DataIngested` | data | NCBI, ChEMBL, PubChem fetch or reference table registration |

### Pattern

Follows rhizoCrypt `GossipEmitter` pattern exactly:
- Discovers `swarmvine` via socket cascade (env → BIOMEOS_SOCKET_DIR → XDG → temp)
- Supports explicit `GOSSIP_RELAY_SOCKET` override
- Non-fatal if unavailable — all `emit()` calls degrade gracefully with `tracing::debug!`
- Fire-and-forget: 200ms timeout, errors never propagated to caller
- Wire format: `gossip.spread` JSON-RPC with `source_primal`, `domain`, `event` payload

### New Files

| File | Lines | Content |
|------|-------|---------|
| `barracuda/src/ipc/gossip.rs` | ~290 | Gossip emitter + event types + 7 tests |

### Modified Files

| File | Change |
|------|--------|
| `barracuda/src/ipc/mod.rs` | Register `gossip` module |
| `barracuda/src/ipc/capability_domains.rs` | Add `gossip.emit` domain (outbound, no methods) |
| `barracuda/src/ipc/handlers/science.rs` | Inject `PipelineComplete` after `handle_full_pipeline`, `DataIngested` after `handle_ncbi_fetch` |
| `barracuda/src/ipc/provenance/mod.rs` | Inject `ProvenanceWitness` after `handle_provenance_complete` |
| `barracuda/src/ipc/handlers/data_fetch.rs` | Inject `DataIngested` after ChEMBL, PubChem, register_table success |
| `barracuda/src/ipc/handlers/mod.rs` | Inject `ValidationPass` after `composition.science_health` passes |
| `barracuda/src/ipc/dispatch.rs` | Update test assertion (22→23 provided capabilities) |
| `barracuda/Cargo.toml` | Fix bingocube-nautilus path |

## Build Gate

```
cargo clippy -p wetspring-barracuda --features "json,ipc,barracuda-lib" -- -D warnings  # CLEAN
cargo clippy -p wetspring-forge -- -D warnings                                           # CLEAN
cargo test -p wetspring-barracuda --features "json,ipc,barracuda-lib" --lib              # 1,840 PASS
cargo test -p wetspring-forge --lib                                                      # 252 PASS
cargo fmt --check                                                                        # CLEAN
```

**Total: 2,092 tests, 0 failures, 0 clippy warnings.**

## Capability Registry Update

- 23 domains (was 22) — added `gossip.emit`
- 47 dispatch methods (unchanged — gossip is outbound-only)
- 4 gossip event types registered

## Status

wetSpring gossip injection is **COMPLETE (4/4)**. All events wired:
- `PipelineComplete` propagates on `science.full_pipeline` completion
- `ProvenanceWitness` propagates on successful `provenance.complete` trio session
- `DataIngested` propagates on NCBI, ChEMBL, PubChem fetch + reference table registration
- `ValidationPass` propagates when `composition.science_health` detects trio + nestGate live

Zero code changes needed at deployment — relay discovered automatically.

## Next (no blockers)

- barraCuda upstream gossip module (`gossip.inject` wire format) complements wetSpring's
  `gossip.spread` — both fire independently, no coordination needed
- Full 16S rRNA pipeline workload (toadStool dispatch integration)
