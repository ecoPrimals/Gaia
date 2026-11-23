# NestGate v0.5.0 — Session 95: Binary UDS Compliance

**Date**: 2026-06-05  
**Wave**: 79  
**Gate**: ironGate  

## P1 Resolved: Native `--socket` on all entry paths

The deployed binary now respects `--socket /run/membrane/nestgate.sock` natively across
all invocation modes. This unblocks the VPS binary refresh for port-free deployment.

### Changes

| Gap | Fix |
|-----|-----|
| `service start` lacked `--socket` | Added `--socket` flag to `ServiceAction::Start`, wired through `ServiceManager::execute` to set `NESTGATE_SOCKET` before startup |
| `IsomorphicIpcServer` fallback ignored `NESTGATE_SOCKET` | `get_socket_path()` now checks `NESTGATE_SOCKET` first, before `XDG_RUNTIME_DIR` or temp dir |
| No CLI tests for socket parsing | 4 new tests: `parse_server_socket_path`, `parse_service_start_socket_path`, `parse_service_start_without_socket`, `service_action_start_holds_socket_path` |

### VPS deployment — all three invocations now work

```bash
# 1. Preferred: service start with explicit socket
nestgate service start --socket /run/membrane/nestgate.sock

# 2. Server mode (already worked)
nestgate server --socket /run/membrane/nestgate.sock

# 3. Environment-only (systemd unit)
Environment=NESTGATE_SOCKET=/run/membrane/nestgate.sock
ExecStart=/path/to/nestgate service start
```

### Socket resolution priority (unchanged)

1. `NESTGATE_SOCKET` env (set by `--socket` flag or systemd unit)
2. `BIOMEOS_SOCKET_DIR` + family filename
3. `XDG_RUNTIME_DIR` + ecosystem dir
4. `std::env::temp_dir()` fallback (last resort)

### Metrics

- 13,039+ total tests, 9,216+ lib tests
- 0 failures, 0 clippy warnings
- nestgate-bin: 135 tests (was 131)
