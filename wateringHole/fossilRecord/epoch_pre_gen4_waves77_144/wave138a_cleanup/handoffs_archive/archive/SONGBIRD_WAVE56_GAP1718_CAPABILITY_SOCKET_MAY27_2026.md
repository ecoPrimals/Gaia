# Songbird — Wave 56 GAP-17/18 Capability Socket Evolution

**Date**: 2026-05-27  
**From**: Songbird team  
**Version**: v0.2.1  
**Audit item**: GAP-17/18 — Capability socket resolution (desktop symlink evolution)

---

## What Changed

GAP-17/18 tracked the reliance on filesystem symlinks (`network.sock → songbird.sock`)
for capability-domain discovery. This wave centralizes the domain name and documents
the migration path toward runtime `ipc.resolve`.

### Centralized Constants

- `songbird_types::primal_names::CAPABILITY_DOMAIN = "network"` — single source of truth
- `songbird_types::defaults::paths::NETWORK_CAPABILITY_SOCKET_FILENAMES` — capability socket names
- `songbird_types::defaults::paths::network_socket_candidates()` — ordered discovery paths

### Evolved Consumers

- **CLI `status.rs`** — no longer hardcodes `"network.sock"`; checks both primal-named
  and domain sockets via centralized constants
- **`env_config/socket.rs`** — `DOMAIN_SOCKET_STEM` references the centralized constant
  instead of a local `"network"` string literal

### Migration Documentation

All new constants include doc comments directing consumers to prefer
`ipc.resolve({ "capability": "network" })` when a broker connection is available.
The symlink remains for desktop bootstrap (chicken-and-egg: can't resolve via
IPC if you don't know the IPC socket path yet).

---

## Coverage Push: +21 Tests

| Module | Tests | Coverage |
|--------|-------|----------|
| `advanced_cache/helpers.rs` | +17 | `should_evict`, `entry_is_expired`, `estimate_entry_size` — all variants |
| `primal_names.rs` + `paths.rs` | +4 | `CAPABILITY_DOMAIN`, `SELF_NAME`, `network_socket_candidates` |

---

## Also Shipped (Wave 55)

- TCP fallback mesh seed fix (`start_tcp_fallback` now fires `spawn_mesh_seed`)
- `clippy::unnecessary_get_then_check` lint fix

---

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 8,091 lib passed, 0 failures, 23 ignored |
| Clippy | Zero warnings (pedantic + nursery) |
| GAP-17/18 | Constants centralized, migration path documented |
| Deep debt | Zero |

---

## GAP-17/18 Status

**Partially resolved** — constants centralized, CLI evolved, documentation added.
Full resolution (eliminating symlink entirely) requires biomeOS bootstrap resolver
or a well-known broker mechanism for first-hop discovery. The symlink is retained
as a desktop convenience while `ipc.resolve` is the runtime standard.
