# Songbird Wave 131 — Deep Debt Evolution: Typed Dispatch + Allocation Elimination

**Date**: July 4, 2026  
**Gate**: flockGate  
**Primal**: songBird v0.2.1-wave131  
**Type**: Deep debt sweep + performance evolution  

---

## Changes

### 1. Hot-Path Allocation Elimination

| Location | Before | After |
|----------|--------|-------|
| `registry.rs` capability lookup | `entry.capabilities.contains(&cap.to_string())` — String alloc per filter | `.iter().any(\|c\| c == cap)` — zero alloc |
| `stun_handler/config.rs` | `SERVERS.clone()` — full `Vec<String>` clone per RPC call | Returns `&'static [String]` — zero alloc |
| `federation.rs` protocol check | `.contains(&String::from("https"))` | `.iter().any(\|p\| p == "https")` |
| `consent/rules.rs` | `.contains(&op.to_string())` | `.iter().any(\|o\| o == op)` |
| `protocol_api.rs` | `.contains(&preferred.to_string())` ×2 | `.iter().any(\|p\| p == preferred)` |

### 2. Typed Exhaustive Dispatch (Legacy String Fallback Eliminated)

New `JsonRpcMethod` variants:
- `GraphMethod::{Validate, CheckAvailability, SuggestAlternatives}`
- `CoordinationMethod::ValidatePattern`
- `LegacyMethod::{DiscoverByFamily, CreateGeneticTunnel, AnnounceCapabilities, DiscoverByCapability, GetServiceHealth}`
- `HttpMethod::{Put, Delete}`

Orchestrator `pure_rust_server/handlers.rs` — the `Err(_) => match normalized { ... }` string-dispatch fallback is **completely eliminated**. All 62+ methods now route through the typed `JsonRpcMethod` enum with exhaustiveness checking.

Also wired into universal-ipc dispatch: `mesh.discover_remotes`, `mesh.mirror`, `mesh.publish` (were declared in the enum but not routed).

### 3. Dependency Diet

`songbird-types` Cargo.toml: `tokio = { features = ["full"] }` → `tokio = { features = ["net", "sync", "time"] }`.

Only 3 features are actually used in the types crate (`TcpStream`, `RwLock`, `timeout`). Since `songbird-types` is a dependency of 20+ downstream crates, this reduces the transitive tokio feature surface across the entire workspace.

### 4. File Refactoring

`mesh_handler/mod.rs` (850L → 697L): Extracted `discovery_federation.rs` (174L) containing `handle_auto_discover`, `handle_discover_remotes`, `handle_mirror`, `handle_publish`. Split by domain cohesion, not arbitrary line count.

---

## Verification

- Zero clippy warnings workspace-wide (`-D warnings --all-targets`)
- 53/53 mesh_handler tests pass
- 94/94 pure_rust_server tests pass
- 585+ songbird-types tests pass
- Zero unsafe blocks, zero production unwrap, zero TODO/FIXME

---

## Upstream Review Targets

1. **Method coverage**: Are there orchestrator methods NOT in `JsonRpcMethod` that other primals call? (All known ones are now typed)
2. **`LegacyMethod` deprecation path**: These flat-namespace names (`discover_by_family`, `create_genetic_tunnel`, etc.) should eventually be migrated to `domain.verb` naming at ecosystem level
3. **`tokio` diet propagation**: Other types/foundation crates in the ecosystem may benefit from the same `"full"` → minimal features pattern

---

## Status

Songbird is **CLEAR** — no sentinel blockers, no code debt above threshold, exhaustive typed dispatch, zero allocation waste in hot paths.
