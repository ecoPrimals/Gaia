# coralReef — DH-1 /tmp Cleanup Complete (May 29, 2026)

**Primal**: coralReef  
**Version**: 0.2.0 — Sprint 13 / Wave 61  
**Commit**: `7e24475`  
**Tests**: 3222 passing, 0 failed  

---

## Summary

All production `/tmp` fallbacks eliminated. Socket resolution now follows the
3-tier pattern established by barraCuda and toadStool:

1. `$BIOMEOS_SOCKET_DIR` — explicit composition launcher override
2. `$XDG_RUNTIME_DIR/biomeos` — Linux/freedesktop (desktop/user systemd)
3. `/run/biomeos` — VPS/system daemon (ProtectSystem=strict safe)

**Zero `std::env::temp_dir()` calls in production code.**

---

## Changes

| File | Before | After |
|------|--------|-------|
| `config.rs` | `temp_dir()` fallback | `/run/biomeos` fallback + new `socket_dir()` helper |
| `ecosystem.rs` | Own XDG→temp resolution | Delegates to `config::socket_dir()` |
| `ipc/unix_jsonrpc.rs` | `runtime_dir.unwrap_or_else(temp_dir)` | Delegates to `config::socket_dir()` |
| `ipc/btsp.rs` | `discovery_dir().unwrap_or_else(\|_\| temp_dir())` | `config::socket_dir()` |
| `ipc/mod.rs` | `discovery_dir().unwrap_or_else(\|_\| temp_dir())` | `config::socket_dir()` |

---

## Verification

```
$ grep -rn "temp_dir()" crates/coralreef-core/src/ | grep -v test
(zero results)
```

Integration tests rewritten to assert:
- Without env → resolves to `/run/biomeos/...`
- With `XDG_RUNTIME_DIR` → uses XDG value
- With empty `XDG_RUNTIME_DIR` → falls to `/run/biomeos`
- With `BIOMEOS_SOCKET_DIR` → takes priority over XDG

---

## Deployment Impact

- Enables `ProtectSystem=strict` in systemd service units
- Compatible with composition launcher (`BIOMEOS_SOCKET_DIR` override)
- No behavioral change on desktop Linux (XDG_RUNTIME_DIR always set by systemd)
- VPS: sockets move from `/tmp/biomeos/` to `/run/biomeos/` (systemd `RuntimeDirectory=biomeos`)
