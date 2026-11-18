# cellMembrane — Wave 155i Magic Number Centralization

**Date:** 2026-07-29
**Author:** eastGate overwatch
**Scope:** 15 files, 1,221 tests green, 0 clippy

---

## Overview

Comprehensive sweep replacing scattered magic numbers, hardcoded ports,
domain literals, and inline policy values with centralized named constants
in `constants.rs`. Eliminates 45+ hardcoded values across 15 files.

## New Constants Added to `constants.rs`

### Timeouts & Retries

| Constant | Value | Replaces |
|----------|-------|----------|
| `DEFAULT_JSONRPC_TIMEOUT_SECS` | 3 | `Duration::from_secs(3)` in `jsonrpc.rs` |
| `DEFAULT_PROBE_TIMEOUT_SECS` | 5 | Inline `5` in sovereignty probes |
| `DEFAULT_TCP_PROBE_TIMEOUT_SECS` | 3 | Inline `3` in `tcp_reachable()` |
| `DEFAULT_ENROLL_PHASE_TIMEOUT_SECS` | 30 | Inline `30` in `enroll.rs` |
| `DEFAULT_IPC_WRITE_TIMEOUT_SECS` | 2 | Inline `2` in impulse UDS |
| `DEFAULT_IPC_READ_TIMEOUT_SECS` | 5 | Inline `5` in impulse UDS |
| `DEFAULT_SANDBOX_PROBE_RETRIES` | 5 | Inline `5` in sandbox health |
| `DEFAULT_SANDBOX_PROBE_INTERVAL_MS` | 2000 | Inline `2000` in sandbox health |
| `MESH_SOCKET_WAIT_RETRIES` | 5 | Inline `5` in mesh relay startup |
| `MESH_SOCKET_WAIT_INTERVAL_SECS` | 2 | Inline `2` in mesh relay startup |

### Well-Known Ports

| Constant | Value | Replaces |
|----------|-------|----------|
| `DEFAULT_DNS_PORT` | 53 | Inline `53` in preflight and channels |
| `DEFAULT_HTTP_PORT` | 80 | Inline `80` in channels |

### Systemd Policy

| Constant | Value | Replaces |
|----------|-------|----------|
| `DEFAULT_CASCADE_TIMEOUT_SECS` | 300 | `TimeoutStartSec=300` |
| `DEFAULT_CASCADE_JITTER_SECS` | 60 | `RandomizedDelaySec=60` |
| `DEFAULT_RESTART_DELAY_SECS` | 5 | `RestartSec=5` |
| `DEFAULT_START_LIMIT_INTERVAL_SECS` | 120 | `StartLimitIntervalSec=120` |
| `DEFAULT_START_LIMIT_BURST` | 10 | `StartLimitBurst=10` |

### WireGuard

| Constant | Value | Replaces |
|----------|-------|----------|
| `DEFAULT_WG_PERSISTENT_KEEPALIVE_SECS` | 25 | Inline `25` in wg.rs |

## Hardcode Fixes

| Fix | File |
|-----|------|
| SSH timeout `10` → `SSH_TIMEOUT_U32` (from constant) | `config.rs` |
| SSH timeout `ConnectTimeout=10` → `DEFAULT_SSH_TIMEOUT_SECS` | `enroll.rs` |
| SSH port `"22"` → `DEFAULT_SSH_PORT` const | `enroll.rs` |
| Ping `-W 5` → `DEFAULT_PROBE_TIMEOUT_SECS` | `enroll.rs` |
| `@primals.eco` → `SURFACE_DOMAIN` | `key_portal.rs` |
| `primals.eco` in CLI hint → `SURFACE_DOMAIN` | `cloudflare/mod.rs` |
| `Address = {}/24` → parsed from `self.subnet` CIDR | `wireguard.rs` |
| `default_wg_port() { 51820 }` → `wireguard::DEFAULT_WG_PORT` | `firewall.rs` |
| Channel ports `[53]`, `[3478]`, `[80, 443]` → constants | `channels.rs` |
| Unnecessary `mesh_ip.clone()` → `mesh_ip.as_deref()` | `enroll.rs` |
| WG keepalive `25` → `DEFAULT_WG_PERSISTENT_KEEPALIVE_SECS` | `wg.rs` |

## Upstream Notes

- All timeout/retry values now have a single source of truth in `constants.rs`
- Changing any policy value (e.g., increasing cascade timeout) requires
  editing exactly one line
- WireGuard CIDR is now derived from the manifest subnet rather than
  hardcoded to `/24`
