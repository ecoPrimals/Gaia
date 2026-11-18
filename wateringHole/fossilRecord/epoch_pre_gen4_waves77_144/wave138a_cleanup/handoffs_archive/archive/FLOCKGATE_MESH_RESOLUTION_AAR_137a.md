# AAR: FLOCKGATE-MESH Resolution — Wave 137a

**Date**: 2026-07-12 10:30 EDT  
**Author**: flockGate overwatch  
**Wave**: 137a  
**Severity**: P1 → **RESOLVED**  
**Commit**: `f05918a`

---

## Executive Summary

FLOCKGATE-MESH (0 songBird mesh peers from flockGate via WG overlay) has been **root-caused and fixed**. The issue was a port constant mismatch in WireGuard auto-discovery code. songBird now connects to 4 overlay peers immediately on startup.

---

## Root Cause

`parse_wg_conf()` and `parse_wg_dump()` in `crates/songbird-orchestrator/src/mesh_seed.rs` constructed peer addresses using `DEFAULT_HTTP_PORT` (8080) instead of `DEFAULT_MESH_PEER_PORT` (7700):

```rust
// BEFORE (broken):
use songbird_types::defaults::ports::DEFAULT_HTTP_PORT;
let addr = format!("{ip_str}:{DEFAULT_HTTP_PORT}");  // → 10.13.37.x:8080

// AFTER (fixed):
use songbird_types::defaults::ports::DEFAULT_MESH_PEER_PORT;
let addr = format!("{ip_str}:{DEFAULT_MESH_PEER_PORT}");  // → 10.13.37.x:7700
```

Additionally, `~/.config/songbird/mesh-peers.toml` on flockGate had all peers configured on port 8080 (copied from the incorrect code example in doc comments). Updated to 7700.

## Contributing Factor

The `peers.toml` persisted state file (`~/.local/share/songbird/peers.toml`) contained stale LAN addresses (192.168.1.x) from a prior session that are unreachable from flockGate's WG-only network. This took priority over the mesh-peers.toml Tier 3 discovery. Cleaned by removing the stale file and letting the corrected Tier 3 discovery repopulate.

---

## Fix Applied

| Component | Change |
|-----------|--------|
| `mesh_seed.rs` Tier 1 (`parse_wg_dump`) | `DEFAULT_HTTP_PORT` → `DEFAULT_MESH_PEER_PORT` |
| `mesh_seed.rs` Tier 2 (`parse_wg_conf`) | `DEFAULT_HTTP_PORT` → `DEFAULT_MESH_PEER_PORT` |
| `mesh_seed.rs` doc comments | Example ports updated 8080 → 7700 |
| `mesh_seed.rs` tests | 7 assertions updated to expect `:7700` |
| `~/.config/songbird/mesh-peers.toml` | All 4 peers updated to port 7700 |
| `~/.local/share/songbird/peers.toml` | Stale file removed (auto-repopulated on restart) |

---

## Verification

After fix deployment and songBird restart:

```
$ curl -s http://127.0.0.1:7700/jsonrpc -d '{"jsonrpc":"2.0","method":"mesh.peers","params":{},"id":1}'

Total: 4 | Online: 4 | Relays: 0

  golgi        @ wireguard://10.13.37.1:7700 path=overlay  reachable=True
  east-gate    @ wireguard://10.13.37.5:7700 path=overlay  reachable=True
  spore-gate   @ wireguard://10.13.37.2:7700 path=overlay  reachable=True
  iron-gate    @ wireguard://10.13.37.7:7700 path=overlay  reachable=True
```

Full RPC communication verified over WG overlay (identity.get, mesh.status both respond).

---

## Remaining: Bidirectional Discovery

flockGate can now reach all 4 overlay peers, but sporeGate does not yet see flockGate in its peer list. sporeGate's own WG auto-discovery also has the same 8080 bug (`wg-A2fvz3cz @ 10.13.37.0:8080` visible in its mesh.peers output).

**Action needed**: Deploy the updated songBird binary (commit `f05918a`) to sporeGate and eastGate. Once deployed, their Tier 1 (`wg show all dump`) discovery will construct correct `:7700` addresses and bidirectional mesh connectivity will be fully established.

---

## Bonus: FP-API Compatibility Layer

Same commit adds `?url=<encoded_url>` query-string support to the drawbridge external proxy. This enables footPrint's Express-style `fetch('/api/proxy?url=...')` pattern to work through the drawbridge without frontend changes — validated against the same domain allowlist as path-based routing.

---

## Affected Gates

| Gate | Impact | Action |
|------|--------|--------|
| flockGate | Fixed — 4 overlay peers connected | **DONE** |
| sporeGate | Has same 8080 bug in Tier 1 discovery | Deploy `f05918a` binary |
| eastGate | Binary already at HEAD (overwatch) | Verify mesh-peers.toml ports |
| ironGate | LAN mesh (not affected by WG port bug) | No action |
| southGate | LAN mesh (not affected by WG port bug) | No action |

---

## Timeline

- **136b**: Mesh gap surfaced (0 peers from flockGate)
- **137a T+0**: Root cause identified (port constant mismatch)
- **137a T+5min**: Code fix + config fix applied
- **137a T+10min**: Build, deploy, verify (4 overlay peers connected)
- **137a T+15min**: Commit `f05918a` pushed to both remotes
