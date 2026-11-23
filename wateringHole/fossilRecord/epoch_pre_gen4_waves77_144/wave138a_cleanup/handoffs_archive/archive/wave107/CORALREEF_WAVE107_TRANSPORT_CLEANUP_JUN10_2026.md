# coralReef — Wave 107 Handoff: Transport Evolution + Socket Cleanup + Deep Debt

**Date**: June 10, 2026  
**Primal**: coralReef  
**Gate**: strandGate  
**Wave**: 107  
**Tests**: 3304 passing, 0 failed  
**Clippy**: Zero warnings (pedantic + nursery)

---

## Summary

Waves 79–107 delivered five evolution milestones for coralReef:

1. **Headless fix** (Wave 79): VPS deployment regression resolved — `default-members` excludes `tools/amd-isa-gen` from production builds
2. **capabilities.list** (Wave 99): IPC compliance 12/12 — added plural alias, fixed 3-tier socket resolution
3. **Transport evolution** (Wave 100): sourDough `TRANSPORT_ENDPOINT` injection — local wire-compatible type, 19 tests
4. **Deep debt** (Wave 101): `main.rs` extraction → `server_lifecycle.rs`, named constants, naga hoisted to workspace deps
5. **Socket cleanup** (Wave 107): Zero `/tmp` in production — `ProtectSystem=strict` unblocked

---

## Key Changes

### Wave 107: PRIMAL-SOCKET-CLEANUP

| File | Change |
|------|--------|
| `ipc/mod.rs` | `default_tarpc_bind()` fallback → `config::socket_base_dir()` |
| `ipc/unix_jsonrpc.rs` | `unix_socket_path_for_base()` fallback → `config::socket_base_dir()` |

Zero `/tmp` artifacts. All paths use 3-tier: `$BIOMEOS_SOCKET_DIR` → `$XDG_RUNTIME_DIR/biomeos` → `/run/biomeos`.

### Wave 101: Deep Debt

| File | Change |
|------|--------|
| `server_lifecycle.rs` | **NEW** — extracted from `main.rs`: discovery file, PID file, shutdown signal |
| `main.rs` | 827 → 704 lines |
| `newline_jsonrpc.rs` | Named `TCP_PEEK_TIMEOUT` constant |
| `ecosystem.rs` | Named `DEFAULT_HEARTBEAT_INTERVAL_SECS`, cost/latency constants |
| `service/compile.rs` | Named `PCI_VENDOR_NVIDIA`, `PCI_VENDOR_AMD`, `INTEL_DEFAULT_WAVE_SIZE` |
| `Cargo.toml` (workspace) | `naga = "28"` in `[workspace.dependencies]` |

### Wave 100: Transport Evolution

| File | Change |
|------|--------|
| `ipc/transport.rs` | **NEW** — `TransportEndpoint` (Uds/Tcp/MeshRelay), `ResolvedBind`, `resolve_bind()` |
| `main.rs` | `cmd_server` uses `resolve_bind()` for dynamic transport |
| `env_keys.rs` | Added `TRANSPORT_ENDPOINT` constant |

sourDough wire-compatible. Zero new external deps. Reference implementation for ecosystem.

### Wave 99: capabilities.list

| File | Change |
|------|--------|
| `ipc/newline_jsonrpc.rs` | Added `"capabilities.list"` dispatch alias |
| `config.rs` | Added to `SERVED_METHODS` |
| `capability_registry.toml` | Added alias metadata |

IPC compliance: 12/12 PASS (was 11/12).

### Wave 79: Headless Fix

| File | Change |
|------|--------|
| `Cargo.toml` (workspace) | `default-members` excludes `tools/amd-isa-gen` |
| `ipc/btsp.rs` | Flaky test isolation via `discover_security_socket_in_dir()` |

---

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 3304 |
| Clippy warnings | 0 |
| Unsafe blocks | 0 (all crates `#![forbid(unsafe_code)]`) |
| Production files >800L | 0 |
| TODO/FIXME/HACK | 0 |
| C/FFI deps | 0 |
| `/tmp` usage | 0 |

---

## Resolved FRAGOs

| FRAGO | Wave | Resolution |
|-------|------|------------|
| `wave79-coralreef-headless-fix` | 79 | default-members excludes tools from builds |
| `wave82-coralreef-registry-parity` | 82 | capability_registry.toml confirmed present |
| `wave99-coralreef-capabilities-list` | 99 | Plural alias + dispatch tests |
| `wave100-coralreef-transport-evolution` | 100 | TRANSPORT_ENDPOINT injection |
| `wave107-coralreef-socket-cleanup` | 107 | /tmp fallback eliminated |

---

## Upstream Gaps for primalSpring

### RESOLVED (previously tracked)

- `capability_registry.toml` — created Wave 78, expanded Wave 99
- `capabilities.list` method — added Wave 99
- `TRANSPORT_ENDPOINT` — adopted Wave 100 (reference implementation)
- `/tmp` socket fallback — eliminated Wave 107

### NO REMAINING GAPS

coralReef has zero known parity gaps. All P0/P1/P2 items from Wave 78–102 blurbs are resolved.

---

## Depot Status

The running VPS binary is stale (pre-Wave 99). Depot rebuild needed to pick up:
- `capabilities.list` (Wave 99)
- Transport injection (Wave 100)
- Socket cleanup (Wave 107)

cellMembrane peptidoglycan rebuild will update 11/12 → 12/12 IPC compliance.

---

*coralReef: pure compiler, sovereign compute. The reef grows clean.*
