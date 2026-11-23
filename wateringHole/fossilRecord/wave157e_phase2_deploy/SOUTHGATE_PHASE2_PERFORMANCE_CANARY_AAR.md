# southGate AAR — Wave 157e Phase 2 Deploy + Performance Canary

**Date**: Aug 10, 2026 | **Wave**: 157e | **Gate**: southGate
**Family**: 89df7a2d (southgate-sovereign) | **From**: eastGate overwatch
**Mission**: Phase 2 binary deploy + Tower-Atomic performance canary baseline

---

## EXECUTIVE SUMMARY

southGate completed Phase 2 deploy: 12/13 binaries updated from golgi depot,
NUCLEUS restarted clean (13/13, 43 sockets, 99 MB), and performance canary
baseline established. **No regressions detected.** Tower-Atomic IPC is stable
at 17,595 conn/s (0.057 ms avg), multi-primal IPC across 28 sockets averages
0.105 ms. GPU healthy.

Process leak recurrence noted (1,801 orphans from 50h session — same coralreef/skunkbat
fork pattern as Wave 157a). Rate: ~36 orphans/hour.

**Canary Verdict: PASS. Phase 2 binaries safe.**

---

## TIMELINE

| Time | Event |
|------|-------|
| 11:32 | Cascade from Forgejo — all repos updated |
| 11:33 | NUCLEUS state: 1,801 processes (leak from 50h session) |
| 11:33 | Mass kill + socket cleanup |
| 11:34 | Depot pull — 12/13 binaries changed |
| 11:34 | Binary deploy to ~/.local/bin/ |
| 11:35 | NUCLEUS restart — 13/13 GREEN first attempt |
| 11:35 | Performance canary: beardog UDS = 17,595 conn/s, 0.057ms |
| 11:35 | Multi-primal IPC: 28 sockets, avg 0.105ms, all responding |
| 11:35 | GPU health: RTX 4060 Vulkan healthy |
| 11:35 | Head + AAR pushed to overwatch |

---

## PERFORMANCE CANARY — BASELINE RESULTS

### Test 1: beardog UDS Burst (1000 connections)
```
Connections: 1000/1000
Rate: 14,747 conn/s
Avg latency: 0.068 ms
```

### Test 2: beardog UDS Sustained (5000 connections)
```
Connections: 5000/5000
Rate: 17,595 conn/s
Avg latency: 0.057 ms
Throughput: 7.5 Mbps (payload)
```

### Test 3: Multi-Primal IPC (28 capability sockets)
```
Socket                          Latency    Status
——————————————————————————————————————————————————
ed25519                         0.052 ms   OK
crypto                          0.057 ms   OK
btsp                            0.061 ms   OK
songbird                        0.065 ms   OK
beardog-health                  0.074 ms   OK
permanence                      0.075 ms   OK
shader                          0.076 ms   OK
x25519                          0.077 ms   OK
rhizocrypt                      0.080 ms   OK
loamspine                       0.081 ms   OK
toadstool                       0.083 ms   OK
biomeos                         0.087 ms   EMPTY (orchestrator ack)
sweetgrass                      0.093 ms   OK
petaltongue                     0.097 ms   OK
network                         0.099 ms   OK
squirrel                        0.107 ms   OK
visualization                   0.112 ms   OK
skunkbat                        0.124 ms   OK
nestgate                        0.130 ms   OK
toadstool-89df7a2d              0.130 ms   OK
ledger                          0.131 ms   OK
beardog-89df7a2d                0.133 ms   OK
dag                             0.138 ms   OK
coralreef                       0.141 ms   OK
petaltongue.negotiate           0.148 ms   EMPTY (handshake ack)
barracuda                       0.155 ms   OK
provenance                      0.156 ms   OK
ai                              0.199 ms   OK
——————————————————————————————————————————————————
Avg: 0.105 ms | Min: 0.052 ms | Max: 0.199 ms
```

### Test 4: GPU Health
```
barraCuda v0.4.0 — HEALTHY
Adapter: NVIDIA GeForce RTX 4060
Backend: Vulkan
```

### Comparison — Wave 157a vs 157e

| Metric | Wave 157a (G68) | Wave 157e (Phase 2) | Delta |
|--------|-----------------|---------------------|-------|
| beardog conn/s | 17,314 | 17,595 | +1.6% |
| beardog avg latency | 0.058 ms | 0.057 ms | -1.7% |
| Multi-primal sockets | 42 total | 43 total | +1 |
| RSS | 96 MB | 99 MB | +3 MB |
| GPU | healthy | healthy | stable |

**Verdict: No regression. Slight improvement in sustained throughput.**

---

## BINARY EVOLUTION (Phase 2 vs Phase 1 G68)

| Primal | Previous | Phase 2 | Delta | Reason |
|--------|----------|---------|-------|--------|
| beardog | 8.68 MB | 8.70 MB | +0.2% | |
| songbird | 19.31 MB | 19.37 MB | +0.3% | riboCipher Tier 2 framing |
| skunkbat | 3.40 MB | 3.43 MB | +0.7% | |
| toadstool | 14.13 MB | 13.00 MB | **-8.0%** | S374 Tokio deep debt cleanup |
| barracuda | 11.90 MB | 9.16 MB | **-23.0%** | Major dead code removal |
| coralreef | 7.87 MB | 9.49 MB | +20.5% | GEMM Phase 2 shader dispatch |
| nestgate | 8.87 MB | 9.54 MB | +7.5% | content.stat + vertebrate self-audit |
| rhizocrypt | (same) | (same) | 0% | |
| loamspine | 5.20 MB | 5.19 MB | -0.2% | |
| sweetgrass | 8.90 MB | 8.92 MB | +0.2% | |
| biomeos | 17.01 MB | 17.06 MB | +0.3% | |
| squirrel | 6.59 MB | 9.02 MB | +36.9% | AI routing expansion |
| petaltongue | 31.37 MB | 35.51 MB | +13.2% | Visualization pipeline |

**Net**: 2 primals shrunk significantly (toadStool -8%, barraCuda -23%),
3 grew for features (coralReef +21%, squirrel +37%, petalTongue +13%).

---

## PROCESS LEAK — RECURRING BUG

| Wave | Uptime | Orphans | Rate |
|------|--------|---------|------|
| 157a | 97h | 3,026 | ~31/hr |
| 157e | 50h | 1,801 | ~36/hr |

**Pattern**: coralreef and skunkbat processes accumulate. Likely fork-based child
processes not being reaped. The G68+ binaries do not appear to have fixed this.

**Recommendation**: P2 bug report for coralreef/skunkbat process hygiene. Workaround:
periodic `pkill -9 -f "plasmidBin/primals"` cron, or systemd-based primal management
with `KillMode=control-group`.

---

## CAPABILITY SOCKET MAP (28 active)

The Phase 2 NUCLEUS exposes 28 capability sockets — up from 42 raw sockets (some
are health/negotiation). The capability surface:

| Domain | Sockets | Primals |
|--------|---------|---------|
| **Security** | ed25519, crypto, btsp, x25519 | beardog |
| **Identity** | beardog-89df7a2d, beardog-health | beardog |
| **Network** | songbird, network | songbird |
| **Compute** | toadstool, toadstool-89df7a2d, shader, coralreef, barracuda | toadstool, coralreef, barracuda |
| **Storage** | nestgate, permanence | nestgate |
| **Provenance** | rhizocrypt, provenance, dag, ledger | rhizocrypt |
| **Data** | loamspine, sweetgrass | loamspine, sweetgrass |
| **Orchestration** | biomeos, squirrel, ai | biomeos, squirrel |
| **Rendering** | petaltongue, visualization, petaltongue.negotiate | petaltongue |
| **Auth** | skunkbat | skunkbat |

---

## STATUS vs BLURB DIRECTIVES

| Directive | Status |
|-----------|--------|
| "Pull from golgi" | **DONE** — 12/13 binaries updated |
| "Validate Tower Atomic baseline" | **DONE** — 17,595 conn/s, 0.057ms, no regression |
| "southGate: PHASE 2 PENDING" | **→ PHASE 2 DEPLOYED** |
| "Performance canary" | **BASELINE ESTABLISHED** |

---

## NEXT STEPS

| Task | Priority | Notes |
|------|----------|-------|
| Process leak P2 | SHOULD | coralreef/skunkbat ~36 orphans/hr |
| Springs activation | READY | Awaiting overwatch directive |
| Braid pen test (local) | CAN | westGate proved 86/87 — can validate same on southGate |
| strandGate pipeline support | CAN | GPU compute available for QCD if needed |
| content.ingest validation | CAN | nestGate 0.5.0 deployed with content.stat |

---

*southGate Wave 157e — Phase 2 DEPLOYED. Performance canary PASS. 13/13 GREEN,
28 capability sockets, 0.057ms IPC, no regressions. GPU healthy. Process leak
noted (~36/hr). K-Derm relay enforced. Ready for work.*
