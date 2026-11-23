# sweetGrass v0.7.47 — Wave 78: AppState Env Snapshots

**Date**: June 4, 2026
**Gate**: strandGate
**Version**: v0.7.47
**Tests**: 1,623 (all passing, 0 clippy warnings)
**LOC**: 60,624

## Summary

Eliminated all hot-path `env::var` reads from BTSP handshakes and braid
creation. Security socket, family seed, BTSP requirement, and JSON-LD
vocabulary URIs are now snapshotted into `AppState` at startup, ensuring
zero env syscalls per-request.

## Changes

### BTSP Environment Snapshot (P0)

- `security_socket_path: PathBuf` — snapshotted from
  `SECURITY_PROVIDER_SOCKET` / `BIOMEOS_SOCKET_DIR` / XDG fallback chain
- `family_seed_b64: Option<String>` — snapshotted from `FAMILY_SEED` /
  `BEARDOG_FAMILY_SEED`
- UDS and TCP listeners use `perform_server_handshake_with()` with
  `state.security_socket_path` instead of resolving per-handshake
- `resolve_security_socket_from_env()` and `resolve_family_seed_from_env()`
  renamed to public for startup snapshot use; runtime callers use snapshot

### BraidContext Environment Snapshot (P0)

- `ecop_vocab_uri: String` — snapshotted from `ECOP_VOCAB_URI`
- `ecop_base_uri: String` — snapshotted from `ECOP_BASE_URI`
- `BraidContext::with_uris()` — DI-friendly constructor from pre-resolved URIs
- `BraidBuilder::context()` — fluent setter to skip `BraidContext::default()`

### Listener Snapshot Consistency (P1)

- `uds.rs` and `tcp_jsonrpc.rs` use `state.btsp_required` instead of
  re-calling `is_btsp_required()` at listener start
- `AppState::new_memory()` now snapshots `btsp_required` like other
  constructors (fixed integration test hang)

### trust.event Behavioral Tests (P1)

5 new behavioral tests for `trust.event`:
- Key exchange weaving with delegation assertion
- Mesh join without delegation
- Gateway witness from base64 signature
- Deterministic content hash seed
- Roundtrip via `braid.get` with full assertion

## Metrics Delta

| Metric | v0.7.46 | v0.7.47 | Delta |
|--------|---------|---------|-------|
| Tests | 1,607 | 1,623 | +16 |
| LOC | 60,377 | 60,624 | +247 |
| Source files | 209 | 209 | 0 |
| Methods | 40 | 40 | 0 |

## Forward Targets

- **PROV-O export env read** — `prov_o_context()` in `sweet-grass-query` still
  calls `ecop_vocab_uri()` directly; thread URI through `QueryEngine` or accept
  `&AppState`
- **`BraidFactory` integration** — wire `AppState.ecop_vocab_uri` /
  `ecop_base_uri` into factory to use `BraidContext::with_uris()` on every
  `create_braid` call
- **`auth.check` completion** — wiring `BearDog` token verification (JH-11)
  blocks on `BearDog` IPC availability
- **btsp/server.rs (766L), btsp/transport.rs (763L)** — approaching 800-line
  threshold; candidate for test extraction if they grow
