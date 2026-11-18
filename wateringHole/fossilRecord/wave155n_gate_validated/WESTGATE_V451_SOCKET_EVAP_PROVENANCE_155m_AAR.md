# AAR: westGate biomeOS v4.51 Redeploy + Socket Evaporation Analysis — Wave 155m

**Date**: Jul 31, 2026 08:45 EDT
**Gate**: westGate
**Wave**: 155m (second redeploy — v4.50 → v4.51)
**Author**: westGate overwatch (AI-assisted)
**Classification**: DISSEMINATE — biomeOS team priority

---

## EXECUTIVE SUMMARY

Deployed biomeOS v4.51 (`999044e7`) to westGate — the 5-tier binary discovery fix. **Capability retention improved significantly**: caps held at 835 for ~2.5 minutes before the wipe cycle (vs instant drop in v4.50). **However, socket evaporation persists** — sockets drop from 31 → 16 within 3 minutes. The binary discovery fix addresses the *symptom* (capability loss) but not the *root cause* (socket file deletion during prune).

Provenance Trio 7/7 continues to pass on every deployment. The chain is resilient.

---

## WHAT WE DID

### Cascade — 6 Repos
| Repo | Commits | Key Changes |
|------|---------|-------------|
| **biomeOS** | +4 | `999044e7`: 5-tier binary search (plasmidBin→~/.local/bin→~/.cargo/bin→$PATH). 14 deps removed. Registry perf |
| **squirrel** | +3 | 7,138 tests, 90.1% coverage, 150+ clippy, universal-constants. Binary: 8.4MB → 4.5MB |
| **cellMembrane** | +4 | Init-scope socket discovery, gate identity consolidation (3→1), plasmid smart split |
| **petalTongue** | +2 | Modern idiom pass, debris audit |
| **sporePrint** | +3 | NUCLEUS milestones, canonical URL, cargo clean 1.3G |
| **wateringHole** | +10 | golgi hook P2 FIXED (3 bugs), sporeGate strategic AAR |

### Binary Updates
| Binary | v4.50 | v4.51 | Delta |
|--------|-------|-------|-------|
| biomeOS | 16,084 KB | 20,342 KB | +4,258 KB (binary discovery code) |
| squirrel | 8,420 KB | 4,464 KB | **-3,956 KB** (deep debt halved binary) |
| membrane | 13,688 KB | 15,993 KB | +2,305 KB |

---

## SOCKET EVAPORATION — DETAILED ANALYSIS

### Timeline (3-minute observation)
```
t=  0s  socks:31  caps:835  mode:Coordinated
t= 15s  socks:31  caps:835  mode:Coordinated
t= 30s  socks:31  caps:835  mode:Coordinated
t= 45s  socks:31  caps:835  mode:Coordinated
t= 60s  socks:20  caps:835  mode:Coordinated  <-- 11 SOCKETS DELETED
t= 75s  socks:20  caps:835  mode:Coordinated
t= 90s  socks:20  caps:835  mode:Coordinated
t=105s  socks:16  caps:835  mode:Coordinated  <-- 4 MORE DELETED
t=120s  socks:16  caps:835  mode:Coordinated
t=135s  socks:16  caps:835  mode:Coordinated
t=150s  socks:16  caps:835  mode:Coordinated
t=165s  socks:16  caps:0    mode:Coordinated  <-- capability wipe finally hits
```

### What v4.51 Improved
- **Capability retention**: Caps held at 835 for ~165 seconds before wipe (v4.50 dropped immediately)
- **3-strike prune threshold**: Working — caps survive multiple prune cycles before wiping
- **Binary discovery**: 5-tier probe resolves binaries from plasmidBin correctly

### What v4.51 Did NOT Fix
- **Socket file deletion**: biomeOS still `unlink()`s socket files belonging to other primals
- **Timing**: First batch (11 sockets) deleted at ~60s, second batch (4 more) at ~105s
- **Process survival**: All 13 services remain `active` with PIDs alive — only the filesystem entries are gone

### Sockets Evaporated
- beardog-westgate-tower-155f.sock
- skunkbat-westgate-tower-155f.sock
- nestgate-westgate-tower-155f.sock
- rhizocrypt-westgate-tower-155f.sock
- loamspine-westgate-tower-155f.sock
- barracuda-westgate-tower-155f.sock
- coralreef-westgate-tower-155f.sock

### Sockets Survived
- songbird-westgate-tower-155f.sock
- sweetgrass-westgate-tower-155f.sock
- toadstool-westgate-tower-155f.sock
- petaltongue-westgate-tower-155f.sock
- squirrel-westgate-tower-155f.sock
- Various alias/secondary sockets

### Root Cause (confirmed across v4.47, v4.50, v4.51)

biomeOS's prune cycle deletes socket **files on disk** when an RPC health ping fails. The processes holding those sockets are still alive — their file descriptors are valid but nobody can connect because the path is gone.

**The fix biomeOS needs**: before calling `unlink()` on a socket file, verify the socket is not held by another process. Options:
1. `fstat()` the socket and check if another PID holds a matching FD
2. Attempt a `connect()` (not an RPC call) — if connect succeeds, the socket is alive
3. Simply **never delete sockets biomeOS didn't create** — track origin in the registry

---

## PROVENANCE 7/7 — CONTINUES PASSING

```
  1. content.put → nestgate           V  BLAKE3 content-addressed
  2. dag.session.create → rhizocrypt  V  Session tracking
  3. dag.event.append → rhizocrypt    V  DataCreate event
  4. dag.merkle.root → rhizocrypt     V  Cryptographic proof
  5. spine.create → loamspine         V  Certificate spine
  6. entry.append → loamspine+bearDog V  Ed25519 signature
  7. braid.create → sweetgrass        V  Attribution braid (JSON-LD)
```

This is the 4th consecutive successful Provenance 7/7 validation across deployments (v4.47, v4.50, v4.51). The chain is resilient — it works with Neural API running or stopped.

---

## METRICS

| Metric | v4.50 | v4.51 | Trend |
|--------|-------|-------|-------|
| Peak capabilities | 835 | **835** | stable |
| Cap retention time | ~60s | **~165s** | **+175%** |
| Socket survival (3 min) | 17/31 | **16/31** | similar |
| Provenance 7/7 | 7/7 | **7/7** | stable |
| CAS objects | 3,254 | **3,256** | +2 |
| ZFS pool | 25.4TB ONLINE | **25.4TB ONLINE** | healthy |
| Services active | 13/13 | **13/13** | stable |

---

## RECOMMENDATION FOR UPSTREAM

### P2 — Socket File Deletion (REOPENED for biomeOS team)

The socket evaporation issue is **not in binary discovery** — it's in the prune/cleanup code path. biomeOS needs to:

1. **Track socket ownership**: maintain a registry of which sockets biomeOS created vs discovered
2. **Never unlink discovered sockets**: if biomeOS didn't `bind()` the socket, it must not `unlink()` it
3. **Verify liveness before pruning**: `connect()` to the socket (no RPC needed) — if it succeeds, the primal is alive
4. **Consider inotify**: instead of scanning and deleting, watch for socket creation/deletion events

### Operational Workaround (westGate)

1. Start all primals in boot order (Tower → Nest → Node → Viz/AI)
2. Build membrane symlinks
3. Start Neural API last
4. If sockets evaporate: stop Neural API, restart affected primals, rebuild symlinks, restart Neural API
5. For Provenance 7/7: can run with Neural API stopped (direct IPC always works)

---

## CONFIGURATION

No changes from previous deployment. All service units, env files, and depot paths unchanged.

---

*westGate Wave 155m v4.51 — Provenance 7/7 passes. Cap retention improved 175% (835 for 165s). Socket evaporation persists (31→16). biomeOS needs to stop deleting sockets it doesn't own. 3,256 CAS on ZFS 25.4TB. gen4 COMPLETE. NUCLEUS IS THE PLATFORM.*
