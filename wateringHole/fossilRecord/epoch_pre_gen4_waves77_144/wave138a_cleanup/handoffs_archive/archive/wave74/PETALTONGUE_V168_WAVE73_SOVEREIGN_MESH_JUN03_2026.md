# petalTongue Wave 73 — Sovereign + Mesh + Optimization

**Date**: June 3, 2026
**Version**: v1.6.8 → v1.6.8+ (patch)
**Tests**: 6,209 passed, 0 failed
**Clippy**: 0 warnings (first-party)

## Mission Items Delivered

### P2: Sovereign Rendering Pipeline — VERIFIED CLEAN
Full-repo scan across Rust, HTML, JS, TOML, Markdown, JSON:
- **Zero** hardcoded GitHub Pages domains (`*.github.io`)
- **Zero** `githubusercontent.com` references
- **Zero** CDN script/font dependencies
- **Zero** runtime content-fetch URLs to external hosts
- `web/index.html` uses only relative `/api/` paths
- WASM exports are synchronous and origin-agnostic
- All content paths are env-driven or socket-convention based

**Verdict**: petalTongue is ready for Caddy-served sovereign infrastructure.

### P3: Mesh-Aware Content Routing

`ContentBackendClient` evolved from single-transport (Unix-only) to
multi-transport with discovery fallback:

**New type**: `ContentEndpoint::Unix(PathBuf) | Tcp(String)`

**4-tier resolution chain**:
1. `CONTENT_BACKEND_SOCKET` — explicit Unix socket
2. `CONTENT_BACKEND_ENDPOINT` — explicit TCP `host:port` (cross-gate)
3. `$BIOMEOS_SOCKET_DIR/{provider}-{family}.sock` convention
4. `discovery.query("content")` via DiscoveryServiceClient (mesh fallback)

**New env var**: `CONTENT_BACKEND_ENDPOINT` for cross-gate TCP routing.

**Cross-gate scenario**: User on flockGate sets
`CONTENT_BACKEND_ENDPOINT=eastgate.mesh:9100` (or discovers via mesh) and
petalTongue routes `content.resolve` calls via TCP JSON-RPC to NestGate
on eastGate.

**Files changed**:
- `src/web_mode/content_backend.rs` — full rewrite
- `crates/petal-tongue-core/src/constants/env_vars.rs` — new constant
- `src/web_mode/mod.rs` — async `from_env()` call
- `src/web_mode/tests.rs` — new tests for TCP + discovery endpoints

### P3: WASM Bundle Optimization

**Removed from `petal-tongue-scene`**:
- `toml` dependency (+ transitive `winnow` parser chain)
- `tracing` dependency (zero usage in scene sources)

**Type change**: `PageMeta.extra: HashMap<String, toml::Value>` →
`HashMap<String, serde_json::Value>`. Conversion happens at parse-time
in `content_render/mod.rs` via `serde_json::to_value()`.

**Bonus**: `PageMeta` now derives `Eq` (possible without `toml::Value`
which has floats; `serde_json::Value` implements `Eq`).

**Impact**: Eliminates `toml` + `winnow` + `toml_datetime` + `serde_spanned`
from WASM binary. `tracing` subscriber infrastructure also eliminated.

### P3: Tokio Scope Reduction (Wave 69: 6 crates → Wave 73: 3 more removed)

| Crate | Change | Rationale |
|-------|--------|-----------|
| `petal-tongue-ui-core` | Removed `tokio` from deps | Zero `tokio::` usage in src/ |
| `petal-tongue-headless` | Removed `tokio` + `petal-tongue-discovery` | Zero usage; eliminates transitive ipc/tokio from headless binary |
| `petal-tongue-tui` | Removed `tokio-util` | Zero `tokio_util::` usage in src/ |

**Remaining tokio production consumers** (all fundamental):
- Root binary (runtime, axum, IPC, signals)
- petal-tongue-ipc (async server/client, tarpc)
- petal-tongue-ui (runtime, discovery bridge, async providers)
- petal-tongue-tui (event loop, async state, discovery)
- petal-tongue-discovery (async network I/O, timeouts)
- petal-tongue-api (transport layer)

## Quality Gates
- `cargo fmt --check`: clean
- `cargo clippy --workspace --all-targets`: 0 warnings
- `cargo test --workspace`: 6,209 passed, 0 failed

## For primalSpring Audit
- Verify `CONTENT_BACKEND_ENDPOINT` works with NestGate TCP endpoint
- Coordinate with sporePrint for sovereign content pipeline testing
- WASM bundle size measurement: run `wasm-pack build` + `twiggy` on artifact
