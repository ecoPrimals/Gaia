# SweetGrass — Wave 149b: braid.create/query CONFIRMED

**Date**: Jul 18, 2026  
**Wave**: 149b  
**Version**: v0.7.62  
**Status**: **CONFIRMED** — no code changes required

---

## P1: Confirm `braid.create/query` for esotericWebb

Both methods are registered, implemented, and passing 107 braid-specific tests
(unit + integration + UDS domain + riboCipher autodetect).

### `braid.create`

**Wire name**: `braid.create`  
**Aliases accepted**: `braid.attribution.create`, `attribution.create_braid`,
`provenance.create_braid`, `attribution.braid`

**Required params**:
```json
{
  "data_hash": "sha256:<64-char-hex>",
  "mime_type": "application/json",
  "size": 512
}
```

**Optional params**: `name`, `description`, `tags`, `metadata`, `source_session`,
`source_merkle_root`, `privacy`, `cross_gate`, `source_gate`, `was_generated_by`,
`witness`

**Returns**: Full Braid JSON-LD object with `@id`, `data_hash`, `mime_type`,
`generated_at_time`, `was_attributed_to`, `witness` (if crypto delegate available).

### `braid.query`

**Wire name**: `braid.query`

**Required params**:
```json
{
  "filter": {}
}
```

**Filter fields** (all optional): `data_hash`, `attributed_to`, `braid_type`,
`created_after`, `created_before`

**Optional**: `order` (`"NewestFirst"` | `"OldestFirst"`, default `NewestFirst`)

**Returns**: `{ "braids": [...], "total": N }`

### Transport

Available on:
- HTTP POST `/jsonrpc` (port 8080 default, configurable via `SWEETGRASS_HTTP_PORT`)
- UDS `sweetgrass.sock` with riboCipher `[0xEC, 0x01]` signal prefix
- tarpc (port 9090 default, configurable via `SWEETGRASS_TARPC_ADDRESS`)

### Null Params Handling

Health methods (`health.check`, `health.liveness`, `health.readiness`) accept
`null` params. Domain methods (`braid.create`, `braid.query`) require their
params and return `-32602 Invalid params` on `null`.

---

## P2: GAP-036 Socket Naming Convention — COMPLIANT

- Socket: `$XDG_RUNTIME_DIR/biomeos/sweetgrass.sock`
- Capability symlink: `provenance.sock -> sweetgrass.sock`
- Family-scoped variant: `sweetgrass-{family}.sock`
- Follows 5-tier resolution: `SWEETGRASS_SOCKET` → `BIOMEOS_SOCKET_DIR` →
  `XDG_RUNTIME_DIR/biomeos/` → `biomeos-{USER}/` → `{temp_dir}/biomeos/`

---

## P2: GAP-038 Stale UDS Socket Cleanup — COMPLIANT

- **On bind**: removes stale socket file before `UnixListener::bind`
  (tested: `test_uds_stale_socket_file_removed_before_bind`)
- **On shutdown**: `cleanup_socket_at()` removes socket + PID file + capability symlink
- **PID files**: written alongside socket (`sweetgrass.pid`) enabling `kill(pid, 0)` checks
- **Capability symlinks**: cleaned alongside socket on graceful shutdown

---

## Phase 2 TransportEndpoint — Already SHIPPED

Shipped at commit `7596df1` (Wave 142b). Prior handoff fossilized in Wave 143b.
No remaining transport work. All `#[cfg(unix)]` removed from probe/dispatch paths.

---

## Verification

```
cargo test --all-features -p sweet-grass-service -- braid    107 pass
cargo test --all-features --test integration -- braid          4 pass (E2E)
cargo clippy --all-features --all-targets -- -D warnings       0 warnings
cargo check --target x86_64-pc-windows-gnu                     0 warnings
```
