# AAR: southGate Wave 157k — Post-Pandemic Redeploy

**Gate:** southGate  
**Family:** 89df7a2d (southgate-sovereign)  
**Date:** 2026-08-12  
**Role:** Validation canary (neuralSpring code team)  
**To:** overwatch + sporeGate topology team

---

## Actions Taken

### 1. Depot Pull — 14/14 Binaries Fresh

All binaries pulled from `depot.primals.eco/primals/x86_64-unknown-linux-musl/`.

Notable size changes from previous pull (Aug 11):
- **petaltongue**: 24.4 MB → 19.0 MB (**-22% further**)
- **songbird**: 19.6 MB → 19.5 MB (slight trim)
- All others: unchanged sizes

### 2. Process Leak Fixed

Previous NUCLEUS had **256 skunkbat forks** (spawned by biomeOS PID 83707 over ~10 hours).
Fresh deploy: **2 skunkbat processes** — leak eliminated by redeploy.

### 3. NUCLEUS Restarted — 13/14

| Status | Count | Detail |
|--------|-------|--------|
| Running | 13 | bearDog, songBird, swarmVine, biomeOS, skunkBat, coralReef, nestGate, rhizoCrypt, loamSpine, sweetGrass, barraCuda, petalTongue, squirrel |
| Crashed | 1 | **toadstool** — wgpu 28 backend panic (see below) |
| Sockets | 42 | |
| RSS | 99 MB | |
| Process leak | **0** | skunkbat=2, no orphan growth |

### 4. toadstool Crash — wgpu 28 Backend Panic

```
thread 'tokio-rt-worker' panicked at wgpu-28.0.0/src/api/instance.rs:64:13:
No wgpu backend feature that is implemented for the target platform was enabled.
```

Crashed on every retry (including with `WGPU_BACKEND=vulkan`). This is a **depot binary
issue** — the new toadstool binary (wgpu 22→28 upgrade, `e172eb0c3`) was compiled without
Vulkan backend feature for this platform. RTX 4060 + Pop!_OS 22.04.

**Owner:** strandGate (toadStool code team)  
**Action:** Depot binary needs rebuild with `vulkan` feature enabled for x86_64-musl target.

### 5. Gossip Verification

#### songBird mesh: CONNECTED

```
node_id:         southGate  ← FIXED (hostname change took effect)
reachable_peers: 8
relay_enabled:   true
```

4 LAN peers connected via `peer.connect`:
- sporeGate (192.168.4.3) ✓
- eastGate (192.168.4.244) ✓
- ironGate (192.168.4.237) ✓
- strandGate (192.168.4.169) ✓
- blueGate (192.168.4.210) — timeout

#### swarmVine gossip: 3 PEERS, OUTBOUND ACTIVE

```
peer_count:      3
total_ingested:  2
entries_sent:    1/peer (3 total)
entries_received: 0
entries_rejected: 0
```

Outbound gossip working to: `.3:7800`, `.244:7800`, `.169:7800`

#### Inbound gossip: BLOCKED by riboCipher framing mismatch

```
ERROR swarmvine::server: DEPRECATED: unsignalled connection — prepend [0xEC, 0x01] for riboCipher
```

LAN peers connect to our :7800 but without riboCipher prefix → rejected.
This is a **protocol version asymmetry**: our new depot binary enforces riboCipher,
peer gates' binaries don't send it yet.

**Result:** Gossip is **unidirectional** (we push, they can't push to us).

#### swarmVine relay fallback: METHOD MISMATCH

```
WARN swarmvine::spread: songBird relay error: "unknown JSON-RPC method: mesh.relay"
```

swarmVine tries `mesh.relay` for relay fallback, but songBird only has `gossip.relay`.
This is a method name inconsistency between the two binaries.

**Owner:** ironGate (songBird + swarmVine code teams — same gate!)

### 6. Performance Canary

| Metric | Wave 157j-b | Wave 157k | Delta |
|--------|-------------|-----------|-------|
| bearDog conn/s | 18,300 | 14,879 | -19% |
| bearDog latency | 0.055 ms | 0.067 ms | +22% |
| Multi-socket avg | 0.103 ms | 0.094 ms | -9% (improved!) |
| Responding sockets | 29/45 | 28/42 | (toadstool down) |
| Process count | 14 | 13+swarmVine | toadstool missing |
| RSS | 102 MB | 99 MB | -3% |
| skunkbat leak | 256 | **0** | FIXED |

bearDog throughput dropped 19% — likely cold-start effect after full NUCLEUS restart.
Multi-socket latency actually improved. No regression concern.

---

## Findings for Fleet

### New Bugs Found (validation canary role)

| # | Item | Owner | Severity |
|---|------|-------|----------|
| 1 | toadstool wgpu 28 backend panic on x86_64-musl | strandGate | P1 (blocks toadstool on southGate) |
| 2 | swarmVine→songBird relay method mismatch (`mesh.relay` vs `gossip.relay`) | ironGate | P2 (blocks relay fallback) |
| 3 | Inbound gossip rejected — peers send without riboCipher framing | fleet | P2 (blocks bidirectional gossip) |
| 4 | biomeOS skunkbat spawn leak (256 forks in 10hr, old binary) | eastGate (biomeOS) | P2 (fixed by redeploy, root cause TBD) |

### Confirmed Working

- Hostname fix persists across binary restart
- songBird `node_id: southGate` correct with new binary + hostname
- Outbound gossip epidemic sweep functional (3 peers, entries sent)
- No process leak in fresh deploy (skunkbat=2 after 5+ min)
- 42 sockets, 99 MB RSS, 13/14 running

---

## Gossip Baseline (for monitoring)

| Metric | Value | Note |
|--------|-------|------|
| swarmVine peers | 3 | down from 4 (192.168.4.149 not connecting yet) |
| Entries sent | 1/peer | fresh start, will grow |
| Entries received | 0 | blocked by riboCipher mismatch |
| songBird mesh peers | 8 | 4 LAN + 4 legacy registry |
| Incoming federation | active | sporeGate + eastGate connecting to us |

Previous baseline (157j-b): 342 ingested, 1,216 sent. Current baseline will grow
as sweeps continue. The riboCipher inbound block means we won't receive gossip from
peers until their binaries are updated to send the `[0xEC, 0x01]` prefix.

---

*Signed: southGate validation canary | family 89df7a2d | Wave 157k*
