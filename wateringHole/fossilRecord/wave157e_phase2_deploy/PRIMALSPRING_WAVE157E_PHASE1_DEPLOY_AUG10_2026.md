# primalSpring — Wave 157e Phase 1 Divergence Examination

**Date**: Aug 10, 2026 (morning session)
**Team**: primalSpring code team (eastGate)
**Wave**: 157e
**Context**: Full depot refresh and Phase 1 divergence checks per blurb deployment plan

## Summary

eastGate Phase 1 deploy **COMPLETE**. 14/14 primals active, 1.0ms dispatch mean,
7/7 capability domains route. All blurb divergence checks pass.

## Deployment

- Full depot rsync from sporeGate: **17 binaries** (187 MB) + BLAKE3SUMS (18 entries)
- All 13 standard primals + nestGate restarted with fresh binaries
- `LimitNOFILE=65536` on `membrane-nucleus@.service` template (P1 fix fleet-wide)
- biomeOS running `neural-api --btsp-optional --graphs-dir primalSpring/runtime_graphs`
- swarmVine configured with `SWARMVINE_SKUNKBAT_SOCK` for vine-bat hook

## Phase 1 Divergence Results

| Check | Result | Detail |
|-------|--------|--------|
| **Primals alive** | **14/14** | All health sockets responding |
| **Primal announcements** | **27+** | Full NUCLEUS + capability aliases |
| **Dispatch latency** | **1.0ms mean** | 3.7ms max (10/10 succeed) |
| **crypto→bearDog** | **PASS** | 1ms |
| **crypto.sign_ed25519** | **PASS** | Actual signing (not health stub) |
| **dag→rhizoCrypt** | **PASS** | 1ms |
| **braid→sweetGrass** | **PASS** | 1ms (riboCipher auto-route) |
| **ml→barraCuda** | **PASS** | 1ms |
| **visualization→petalTongue** | **PASS** | 1ms |
| **gossip→swarmVine** | **PASS** | 2ms |
| **songBird Tier 2 (0xED)** | **PASS** | riboCipher Tier 2 framing accepted |
| **toadStool silicon.registry** | **PASS** | SiliconRegistry struct returned |
| **nestGate content.stat** | **PASS** | Method wired (responds to calls) |
| **swarmVine gossip table** | **PASS** | Active, 0 cross-gate peers (LAN) |
| **vine-bat pre-accept** | **PASS** | 8/8 checks, verdict=allow |
| **BLAKE3SUMS** | **PASS** | 18 entries |

### Binary Sizes (depot)

| Binary | Size | Notes |
|--------|------|-------|
| biomeOS | 17 MB | TOML fix + gossip table + FD self-heal |
| songBird | 19 MB | Tier 2 + transport convergence |
| petalTongue | 35 MB | WebGL bridge + FD self-heal |
| toadStool | 13 MB | S374 silicon registry + Tokio debt |
| cellMembrane | 17 MB | G69 Phase 2 |
| barraCuda | 9 MB | Zero-panic + Silicon Fold |
| coralReef | 9 MB | GEMM Phase 2 |
| nestGate | 9 MB | content.ingest + content.stat |
| squirrel | 9 MB | Updated |
| bearDog | 9 MB | RiboCipherHandler Tier 2 |
| sweetGrass | 9 MB | Updated |
| rhizoCrypt | 8 MB | Updated |
| skunkBat | 3 MB | vine-bat pre-accept |
| swarmVine | 3 MB | Phase 4 + vine-bat hook |
| loamSpine | 5 MB | Updated |
| sourdough | 3 MB | G68 validator |

### Notes

- bearDog's new binary separates health (`beardog-health.sock`) from main RPC
  (`beardog.sock` — plain JSON-RPC). The `RiboCipherHandler` handles Tier 2
  encode/decode on the health socket.
- toadStool `compute.silicon.registry` returns a populated struct but coralReef
  IPC fails (expected — no GPU on eastGate). Silicon validation deferred to strandGate.
- nestGate was inactive (no systemd enable) — started manually for this deploy.
  Should be enabled permanently: `systemctl --user enable membrane-nucleus@nestgate.service`
- Cross-gate peers = 0 (eastGate is on LAN, other gates not currently reachable via WireGuard)

## Cascade Status

- primalSpring: `161ef98d` → HEAD (updated)
- wateringHole: synced
- biomeOS: `2fae9144` (gossip table + registry translations)
- barraCuda: `e5d44c4f` (+3177 lines — Silicon Fold, Node Atomic IPC)
- coralReef: `3c17d77` (+5945 lines — GEMM Phase 2, deep debt splits)
- toadStool: `28f674048` (S374 silicon registry, Tokio deep debt)
- nestGate: `4cafa535` (content.ingest + content.stat handlers)
- All other primals: synced

## eastGate Ready for Phase 2 Fleet Deploy

Phase 1 divergence examination CLEAR. eastGate is running the full 157e payload.
Recommending Phase 2 fleet deploy proceed when sporeGate confirms depot rebuild.
