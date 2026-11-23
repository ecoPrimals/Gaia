# swarmVine — Wave 157g MESH ENMESHMENT + SOCKET CONSOLIDATION

**Date**: August 10, 2026
**Wave**: 157g (2 commits: `4cd506a` + `fb0d6be`)
**From**: eastGate overwatch
**Primal**: swarmVine (#16)
**Triggered by**: Wave 157e NUCLEUS COMPOSITION GRAPH overwatch validation

---

## Summary

Two commits addressing three critical overwatch findings (socket discovery
ambiguity, cross-gate gossip unreachable, no gossip injection) plus deep
consolidation of socket directory resolution.

## Commit 1: Mesh enmeshment (`4cd506a`)

### 1. primal.announce disambiguation
`primal.announce` now sends explicit `protocol`, `tarpc_socket`, and
`gossip_port` fields so biomeOS unambiguously discovers the JSON-RPC
socket (not tarpc). Fixes westGate finding where biomeOS connected to
`.tarpc.sock` instead of `.sock`.

### 2. songBird mesh relay fallback
When direct TCP to a gossip peer fails, the epidemic loop falls back to
`relay_via_songbird()` — sends `mesh.relay` through local songBird's
`:7700` mesh transport. Provides cross-gate gossip resilience when TCP
7800 is unreachable.

### 3. endpoint.alive self-injection (ant colony scout)
swarmVine self-injects `endpoint.alive:{gate}` Tower gossip entry on
startup and periodically (every eviction cycle). First primal to inject
gossip — the foundation for the ant colony pattern.

## Commit 2: Socket dir consolidation (`fb0d6be`)

Eliminated **5 duplicated `/tmp` fallback paths** across 3 files:
- `tarpc_server.rs`: inline `XDG→/tmp` → `runtime_socket_dir()`
- `transport.rs`: inline `XDG→/tmp` → `runtime_socket_dir()`
- `tarpc_service.rs`: inline `XDG→/tmp` → `runtime_socket_dir()`
- `announce.rs` (neural-api): removed redundant XDG tier
- `announce.rs` (songBird): removed redundant XDG tier

**After**: `/tmp` appears only in `platform_paths.rs` (single source of truth).
Zero `format!("...biomeos...")` hardcoding remaining anywhere.

Also: `server.rs` replaced `to_value().unwrap_or_default()` with `json!()`.

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 137 |
| Clippy warnings | 0 |
| Fmt violations | 0 |
| TODO/FIXME markers | 0 |
| Unsafe code | 0 |
| `/tmp` outside platform_paths | 0 (was 5) |
| `format!("...biomeos...")` | 0 (was 2) |
| Hardcoded primal names | 0 |
| Source files | 35 (zero debris) |
| Scripts | 0 |
| Archive code | 0 |

## File inventory (35 files, zero debris)

```
19 .rs source (core: 12, server: 7)
 4 .toml (workspace, 2 crate, deny)
 3 .yml (CI workflows)
 3 .md (README, CONVENTIONS, spec)
 1 capability_registry.toml
 1 .lock, 1 LICENSE, 1 .gitignore
```

## Upstream dependencies (for primal teams)

| Team | Need | Status |
|------|------|--------|
| **biomeOS** | Read `protocol`+`tarpc_socket`+`gossip_port` from `primal.announce` | Payload ready |
| **songBird** | Implement `mesh.relay` for gossip transport relay | Request format defined |
| **Gate ops** | Verify TCP 7800 cross-gate reachability | Deployment task |
| **All primals** | Inject domain-specific gossip via `gossip.inject` | API ready, pattern documented |

## Remaining (all external)

- songBird gossip delegation (`mesh.capabilities_announce` → swarmVine)
- tarpc streaming (awaiting upstream tarpc support)
- Test coverage 82% → 90% (needs e2e/integration harness)

---

*Wave 157g — ant colony scout deployed. Relay fallback wired. Announce
payload unambiguous. Socket consolidation: 5 duplicate /tmp fallbacks → 0.
137 tests. Zero debt. Zero debris. Primal #16 clean for upstream audit.*
