# swarmVine — Wave 157g DEEP DEBT + G72 STADIAL SHIFT

**Date**: August 10, 2026
**Wave**: 157g (Deep Debt + G72 Dependency Pandemic)
**From**: eastGate overwatch
**Primal**: swarmVine (#16)
**Commits**: `7e080d0` (G72 Tier 1 dep trim), `e8c7e44` (deep debt)

---

## Summary

Two-commit deep debt wave: dependency pandemic compliance + idiomatic Rust
evolution. swarmVine is now the lean exemplar across the ecosystem.

## Changes by Category

### External dependency elimination
- **`hostname` crate removed** — replaced with pure Rust `read_system_hostname()`
  that reads `/proc/sys/kernel/hostname` (Linux fast path) or `/etc/hostname`
  (POSIX fallback). Eliminates 3 transitive crates from dep graph.
- **`futures` umbrella → `futures-util`** — only `StreamExt` was used.
  `futures-util` is already transitive via tarpc.
- **Dead `toml` dep removed** — declared in workspace, never imported.

### Safe Rust evolution
- **Bloom filter casts**: `as usize`/`as u64` → `try_from().unwrap_or()`
  throughout `domain_types.rs`. Zero truncation risk on any platform.
- **Clone reduction in gossip ingest**: destructure `GossipEntry` after
  store insertion to avoid cloning `key`, `origin_gate`, `nonce` for
  notification and nonce tracking. Moves owned values instead.

### Constant consolidation (zero hardcoding)
- **`DEFAULT_GOSSIP_PORT`** (7800) — extracted to `env_keys`, eliminates
  3 scattered magic numbers.
- **`resolve_gossip_port()`** — single implementation in `env_keys`,
  eliminates 2 duplicate functions (`spread::gossip_port()` and
  `announce::gossip_port()` both had identical logic).
- **Socket naming constants**: `SWARMVINE_JSONRPC_SOCK`,
  `SWARMVINE_TARPC_SOCK`, `SONGBIRD_SOCK`, `NEURAL_API_SOCK_PREFIX` —
  all socket name string literals now use named constants from `env_keys`.

### Documentation
- `CONVENTIONS.md` updated to reflect pure Rust hostname, socket naming
  constants, `resolve_gossip_port()` as single source of truth.
- `README.md` wave updated to "157g STADIAL SHIFT (G72 clean)".

## Metrics

| Metric | Before (157g mesh) | After (deep debt) |
|--------|--------------------|--------------------|
| Workspace deps | 13 | 11 |
| Core direct deps | 8 (`hostname` included) | 7 |
| Total transitive | 207 | 204 |
| `as` casts in prod | 4 (2× `as usize`, 2× `as u64`) | 0 (`try_from` throughout) |
| Duplicate fn impls | 2 (`gossip_port()` ×2) | 0 |
| Hardcoded socket strings | 3 (`songbird.sock`, `swarmvine.tarpc.sock`, `neural-api-*.sock`) | 0 (all via `env_keys` constants) |
| Magic port numbers | 3 (`7800` literals) | 0 (all via `DEFAULT_GOSSIP_PORT`) |
| Unnecessary clones | 4 (gossip notify + nonce) | 1 (`key` still cloned for notify+debug) |
| Tests | 137 | 137 |
| Clippy warnings | 0 | 0 |
| Unsafe code | 0 | 0 |
| TODO/FIXME markers | 0 | 0 |
| Mocks in production | 0 | 0 |

## Remaining external deps (all justified)

| Dep | Purpose | Notes |
|-----|---------|-------|
| tokio | Async runtime | Specific features, not `["full"]` |
| serde + serde_json | Wire format | Ecosystem standard |
| tarpc + tokio-serde | Binary RPC | G64 Cephalization |
| thiserror | Error types | Zero-cost derive |
| tracing | Structured logging | Ecosystem standard |
| anyhow | Server error handling | Server-only |
| clap | CLI parsing | Server-only |
| futures-util | `StreamExt` | Already transitive via tarpc |
| tracing-subscriber | Log formatting | Server-only |

No further dep reduction possible without removing core functionality.

## Upstream dependencies

- **songBird MeshRelay** — OPEN. Needed for blueGate + southGate gossip.
- **Depot rebuild** — sporeGate scope. Current depot predates gossip binaries.

---

*Deep debt resolved. hostname→pure Rust, safe casts, constant consolidation,
clone reduction. 11 workspace deps. 137 tests. Zero hardcoding. Zero unsafe.
Zero dead deps. swarmVine is G72-clean and the lean exemplar. Primal #16.*
