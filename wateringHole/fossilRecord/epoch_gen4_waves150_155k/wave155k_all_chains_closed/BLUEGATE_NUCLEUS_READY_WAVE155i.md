# blueGate NUCLEUS-READY — 13/13 Primals on Windows

**Date**: Jul 29, 2026 18:55 EDT | **Wave**: 155i | **From**: blueGate
**Status**: **ALL THREE ATOMICS LIVE. 13 primals, 147 MB, TCP-only, Windows 10.0.26200.**

---

## FULL STACK — TOWER + NEST + NODE

| # | Primal | Composition | Version | Port | Health | Transport |
|---|--------|-------------|---------|------|--------|-----------|
| 1 | bearDog | Tower | 0.9.0 | :9100 | `alive` | TCP JSON-RPC |
| 2 | songBird | Tower | 0.2.1 | :9901, :7700 | `healthy` (6,392s up) | TCP IPC + HTTP |
| 3 | skunkBat | Tower | — | — | Running | Process |
| 4 | nestGate | Nest | 0.5.0 | :9200 | `ok` | HTTP (MCP, SSE, WS) |
| 5 | loamSpine | Nest | 0.9.16 | :9201 | `ok` | TCP JSON-RPC |
| 6 | rhizoCrypt | Nest | 0.14.17 | :9202 | `alive` (5,911s up) | TCP JSON-RPC |
| 7 | sweetGrass | Nest | 0.7.61 | :9203, :9213 | `healthy` (5,928s up) | TCP + HTTP |
| 8 | petalTongue | Nest | 1.6.6 | :9204 | Running | tarpc |
| 9 | squirrel | Nest | 0.1.0 | :9205 | `healthy` | TCP JSON-RPC |
| 10 | biomeOS | Nest | 0.1.0 | :9206 | `200 OK` | HTTP |
| 11 | toadStool | Node | 0.2.0 | :9300 | Accepting (riboCipher-gated) | TCP |
| 12 | barraCuda | Node | 0.4.0 | :9301 | `alive` | TCP JSON-RPC |
| 13 | coralReef | Node | 0.2.0 | :9302 | `alive` (37s up) | TCP JSON-RPC |

---

## RESOURCE PROFILE

| Metric | Value |
|--------|-------|
| Total primals | **13** |
| Total memory | **147 MB** |
| Tower footprint | ~36 MB |
| Nest footprint | ~72 MB |
| Node footprint | ~39 MB (toadStool 19, barraCuda 13, coralReef 7) |
| TCP ports | 9100, 9200-9206, 9213, 9300-9302, 7700, 9901 |
| GPU | None (headless/cpu-only mode) |

---

## WHAT WORKS

1. **All 13 primals start and stay alive on Windows** — zero crashes, zero platform gates
   (songBird was built from source; all others from depot)
2. **TCP-only transport works universally** — `PRIMAL_BIND_MODE=tcp_only` is the reliable
   Windows path for all primals
3. **No GPU required** — toadStool `--headless`, barraCuda `--no-gpu-probe`, coralReef
   all run in CPU/shader-only mode. GPU validation happens on strandGate.
4. **Memory efficient** — 147 MB for 13 primals. Windows overhead is minimal.
5. **Long-running stability** — songBird 6,392s, rhizoCrypt 5,911s, sweetGrass 5,928s
   (all >1.5 hours) with no degradation

## OBSERVATIONS

### toadStool riboCipher Gate

toadStool responds to plain JSON-RPC with:
```json
{"error":{"code":-32600,"message":"Connection rejected: missing riboCipher signal. Prepend [0xEC, 0x01]."}}
```

This is the biomeOS riboCipher framing requirement (`[0xEC, 0x01]` prefix on all IPC).
The blurb identifies this as the "graph executor riboCipher fix" — biomeOS needs to
prepend the 2-byte signal when dispatching to primals that enforce it.

**Impact**: toadStool is reachable and responding, but won't process workloads until
the caller uses riboCipher framing. barraCuda and coralReef accept plain JSON-RPC.

### Version Gap: Depot vs. Source

| Primal | Depot Version | Source Version | Gap |
|--------|--------------|----------------|-----|
| sweetGrass | 0.7.61 | 0.8.0 | G3 wiring (LedgerClient) |
| biomeOS | 0.1.0 | 4.45 | Composition broker, BTSP, riboCipher |
| songBird | 0.2.1 | 0.2.1 | **Current** (built from source) |
| nestGate | 0.5.0 | — | Deep debt + CAS ZFS |

For full NUCLEUS orchestration, biomeOS v4.45 is needed (depot has v0.1.0 — very stale).
Building biomeOS from source would give blueGate the composition broker.

---

## COMPARISON TO BLURB NUCLEUS DEFINITION

```
NUCLEUS = Tower + Nest + Node + biomeOS
        = (bearDog + songBird + skunkBat)        ← ✅ 3/3 LIVE
        + (nestGate + rhizoCrypt + loamSpine      ← ✅ 7/7 LIVE
           + sweetGrass + petalTongue + squirrel
           + biomeOS)
        + (toadStool + barraCuda + coralReef)    ← ✅ 3/3 LIVE
```

**blueGate has all 13 NUCLEUS primals running.** What remains for "full NUCLEUS" per
the blurb is:
1. biomeOS v4.45 (composition lifecycle management, not just API)
2. riboCipher framing (toadStool gate)
3. Graph executor (biomeOS orchestrating across compositions)
4. bearDog `crypto.sign_ed25519` (Provenance Trio 7/7)

These are code evolution items, not deployment blockers. The infrastructure proof is done.

---

## NEXT STEPS

1. **Build biomeOS from source** → v4.45 composition broker on blueGate
2. **Sub-builder enrollment** → register blueGate with sporeGate for Windows depot builds
3. **Windows depot rebuild** → publish all 14 `.exe` with Wave 155i source
4. **riboCipher test** → send `[0xEC, 0x01]`-prefixed request to toadStool
5. **NUCLEUS orchestration** → once biomeOS v4.45 is running, test composition lifecycle

---

*blueGate — 13/13 primals, 147 MB, all three atomics proven on Windows.
First Windows gate with full NUCLEUS infrastructure. Pending: biomeOS source
build for composition lifecycle, bearDog crypto for Provenance 7/7.
Infrastructure proof COMPLETE.*
