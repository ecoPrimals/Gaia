# Wave 90: Remaining Mountain Issues — Revalidated

**Date**: 2026-06-07 (updated after Wave 90 cascade + revalidation)  
**From**: eastGate overwatch  
**Goal**: Resolve all remaining deployment/mesh issues so we can move to transport injection evolution

---

## Resolved This Session (Waves 87–90)

| ID | Issue | Owner | Wave |
|----|-------|-------|------|
| CM-TRIGGER-01 | On-demand pipeline trigger | cellMembrane | 87 |
| BIO-SEARCH-01 | Depot-first binary search priority | biomeOS | 88 |
| SB-FEDERATION-01 | Federation TCP listener in server mode | songBird + biomeOS | 89 |
| PostPrimordial audit | Springs 100% plasmidBin-only | overwatch | 87 |
| BARRACUDA-SOCKET-01 | Self-referencing socket symlink | barraCuda | **90 — VALIDATED** |
| BIO-HEALTHRETRY-01 | Health check retry with backoff | biomeOS | **90 — VALIDATED** |

**Pipeline proven end-to-end**: team pushes → cascade → harvest → depot → NUCLEUS → 12/12 ACTIVE → federation :7700 LIVE.

### Wave 90 Revalidation

- Cascade: 38/38 synced, `barraCuda` pulled `126ea3e1` (socket fix), `biomeOS` pulled `7496b398` (v4.12 health retry)
- Both rebuilt and harvested to depot (14 binaries)
- NUCLEUS launch: **12/12 primals resolved from depot, 12/12 transitioned to ACTIVE**
- Barracuda: proper socket file created, `health.liveness` returns `{"status":"alive"}`, RTX 4070 detected
- Songbird: `:7700` LIVE on `*`, `:8091` HTTP API LIVE

---

## Remaining Issues (2)

### 1. BIO-ORPHAN-01 — NUCLEUS Process Lifecycle (P2)

**Owner**: biomeOS team  
**Blocker for**: Clean restart/upgrade cycles (not blocking mesh proof)

NUCLEUS spawns 12 primals, stands up Neural API, enters Coordinated Mode, then **exits**
while child primals continue as orphans. A second `biomeos nucleus start` fails because
old primals still hold ports/sockets.

```
Error: Socket /run/user/1000/biomeos/songbird-8ff3b864a4bc589a.sock did not appear within 10s
```

**Fix options**:
1. NUCLEUS stays alive as supervisor (preferred — enables lifecycle monitoring, health probes, hot-reload)
2. NUCLEUS detects existing primals on startup and reattaches
3. At minimum: clean stale sockets AND check for running primal PIDs before spawning

### 2. 2-Gate Mesh Proof — eastGate ↔ strandGate (P1)

**Owner**: eastGate + strandGate operators  
**Blocker for**: Stadial entry

Both gates now have Songbird :7700 LIVE:
- **eastGate**: `*:7700` confirmed (songBird `0a09354b` + biomeOS v4.12)
- **strandGate**: `*:7700` confirmed (Wave 86)

**Action**: Coordinate with strandGate to run `mesh.init` and verify:
1. `discovery.peers` returns peer_count >= 1
2. `mesh.health_check` shows all_healthy: true
3. Cross-gate `capability.call` smoke test

This is a coordination task, not a code issue.

---

## What's Clear

| Layer | Status |
|-------|--------|
| plasmidBin depot | 14/14 binaries, all current |
| Cascade | 38/38 parity, parallel, freshness auto-publish |
| Pipeline | harvest → refresh → trigger — all proven |
| Springs | 100% postPrimordial (no target/release fallbacks) |
| NUCLEUS binary resolution | 12/12 from depot |
| Primal ACTIVE count | 12/12 (all transitioned) |
| barraCuda socket | Fixed (`126ea3e1`), validated with RTX 4070 |
| biomeOS health retry | Fixed (v4.12 `7496b398`), validated |
| Federation | :7700 LIVE on eastGate `*` + strandGate |
| songBird HTTP | :8091 LIVE |

---

## Path to Transport Injection

Once the 2 remaining issues are addressed:

1. **Fix NUCLEUS lifecycle** (BIO-ORPHAN-01) → clean restart/upgrade cycle
2. **Run 2-gate mesh proof** → validates cross-gate federation
3. **Begin transport injection** (Phase 2 of wave79 FRAGO):
   - songBird: `ipc.resolve` returns structured `TransportEndpoint`
   - All primals: accept injected transport from launcher/Tower
   - biomeOS: graph nodes declare capabilities only, not transport hints
   - sporePrint is first (1/14 — `TransportEndpoint` enum shipped)

---

## Blurbs by Team

### biomeOS Team

1. **(P2) BIO-ORPHAN-01**: NUCLEUS exits after Neural API setup, leaving primals orphaned.
   Second launch fails because old primals hold ports/sockets. NUCLEUS should stay alive
   as supervisor (preferred) or detect/reattach to existing primals on startup.
2. **(DONE)** v4.10: BIO-SEARCH-01. v4.11: SB-FEDERATION-01 bind address. v4.12: health retry.

### songBird Team

1. **(DONE)** SB-FEDERATION-01 resolved (`0a09354b`). Federation :7700 LIVE.
2. **(P2, next)** Begin `ipc.resolve` structured endpoint work (Phase 2 M1 of transport evolution).
   Return `TransportEndpoint { transport: "uds", path: "..." }` instead of raw path strings.

### barraCuda Team — CLEAR

Socket fix (`126ea3e1`) validated. Barracuda starts cleanly via NUCLEUS, responds to
`health.liveness`, GPU detected. No remaining work.

### All Other Teams — NO ACTION

Mountain clear. No upstream work blocking deployment or mesh.

---

*"Six resolved, two remaining. 12/12 primals ACTIVE from depot. Mesh proof is next."*
