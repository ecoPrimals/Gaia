# blueGate Wave 157k — Blocker #1 RESOLVED

**Date**: Aug 12, 2026 | **Wave**: 157k | **Gate**: blueGate (10.13.37.12 / 192.168.4.212)
**Operator**: blueGate Windows builder | **From**: overwatch (gate-agnostic)
**Status**: **BLOCKER #1 RESOLVED. NUCLEUS 13/13. MESHRELAY LIVE. LAN REACHABLE.**

---

## Summary

Blocker #1 ("blueGate depot pull — .210:7700 timed out") had **two root causes**, both now fixed:

1. **Wrong LAN IP in topology**: `TOPOLOGY_MAP.toml` listed blueGate as `192.168.4.210` — actual IP is **`192.168.4.212`**. Fixed in this commit.
2. **songBird bound to localhost only**: songBird was started with `--bind 127.0.0.1` making it unreachable from LAN. Restarted with `--bind 0.0.0.0` — now listening on all interfaces (LAN + WG + localhost).

After both fixes, blueGate's songBird is reachable at `192.168.4.212:7700` (LAN) and `10.13.37.12:7700` (WireGuard overlay).

---

## What Was Fixed

### Topology Map IP

```diff
- { gate = "blueGate", site = "house2", lan_ip = "192.168.4.210", status = "live" },
+ { gate = "blueGate", site = "house2", lan_ip = "192.168.4.212", status = "live" },
```

### songBird Bind Address

```
BEFORE: songbird server --bind 127.0.0.1 --port 7700  (localhost only)
AFTER:  songbird server --bind 0.0.0.0 --port 7700    (all interfaces)

Listening: 0.0.0.0:7700 (verified: LAN .212:7700 + WG .12:7700 both OPEN)
```

---

## Post-Fix Validation

| Check | Result |
|-------|--------|
| NUCLEUS | 13/13 ALIVE |
| songBird :7700 | 0.0.0.0 LISTENING (LAN + WG + localhost) |
| 192.168.4.212:7700 | REACHABLE (self-test) |
| 10.13.37.12:7700 | REACHABLE (WG self-test) |
| MeshRelay | gossip.inject/spread/subscribe AVAILABLE |
| gossip.inject | OK (origin_gate="blueGate") |
| Mesh peers | 7/7 reachable on WG overlay |
| TCP 7800 gossip | .2 and .5 OPEN |
| builder.serve | :9800 ALIVE |

---

## Remaining Operational Blockers (from blurb)

| # | Item | Status |
|---|------|--------|
| 1 | blueGate depot pull / .210:7700 | **RESOLVED** (IP fix + bind fix) |
| 2 | eastGate NUCLEUS restart + hostname | eastGate (not blueGate) |
| 3 | songBird --node-id flag | songBird team (ironGate) |
| 4 | southGate LAN IP .149 vs .148 | sporeGate topology |
| 5 | biomeGate SSH recovery | biomeGate (eventual) |

---

## Note on Depot songBird

The depot `x86_64-pc-windows-gnu/songbird.exe` (21.5MB) still does NOT contain MeshRelay methods. blueGate continues running the locally-built MeshRelay songBird (17.2MB, commit `9351230d`). This divergence was reported in the previous AAR and needs sporeGate to rebuild the Windows songBird from HEAD.

---

*blueGate 157k: Blocker #1 RESOLVED. LAN IP corrected (.210→.212). songBird rebound to 0.0.0.0:7700. NUCLEUS 13/13. MeshRelay LIVE. 7 mesh peers. Ready for LAN gossip from other gates.*
