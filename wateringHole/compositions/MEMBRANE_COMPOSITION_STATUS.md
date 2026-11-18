<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Membrane Composition Status — golgi

**Wave**: 178b | **Date**: 2026-10-17
**Node**: golgi (DigitalOcean, 2GB RAM, 1 vCPU, no GPU)
**Composition**: Tower Atomic + Nest Atomic + Node Atomic (headless) + biomeOS Neural API

---

## Live Composition

| Primal | Domain | Socket | Port | Status | systemd |
|--------|--------|--------|------|--------|---------|
| bearDog | crypto | crypto.sock + 5 symlinks | — | 🟢 alive | enabled |
| songBird | network | network.sock | 7700 + 7780 | 🟢 alive | enabled |
| skunkBat | security | security.sock | 9750 | 🟢 alive | enabled |
| nestGate | storage | — | 9870 | 🟢 ok | enabled |
| rhizoCrypt | dag | dag.sock | — | 🟢 alive v0.14.17 | enabled |
| loamSpine | permanence | ledger.sock + permanence.sock | — | 🟢 alive (55 caps) | enabled |
| sweetGrass | provenance | provenance.sock | 9850 | 🟢 healthy (8 braids) | enabled |
| toadStool | compute | compute.sock (riboCipher) | — | 🟢 alive (headless) | enabled |
| barraCuda | math | math.sock | — | 🟢 alive (cpu-shader) | enabled |
| biomeOS | orchestration | neural-api-default.sock | — | 🟢 1053 caps / 57 primals | enabled |
| petalTongue | visualization | petaltongue.sock + visualization.sock | 8090 | 🟢 neural_api: true | enabled |
| swarmVine | gossip | swarmvine.sock | 7800 | 🟢 alive | enabled |

**Infrastructure**: caddy (PID stable, 34h+), opsonize-rs (2d+), skunky-ingest (9h+)

---

## Atomic Composition Verification

### Tower Atomic ✅

BearDog (crypto) → SongBird (transport) → SkunkBat (defense)

All three alive on UDS. Tier 3 discovery (UDS filesystem convention).
No BTSP family seed on membrane — `--btsp-optional` mode.

### Nest Atomic ✅

NestGate (storage) + rhizoCrypt (ephemeral DAG) + LoamSpine (permanent
ledger) + SweetGrass (attribution). Full Memory & Attribution Stack:

```
Application requests
      ↓
sweetGrass (query + attribution)
      ↓
LoamSpine (selective permanence, 55 capabilities)
      ↓
rhizoCrypt (working memory, BLAKE3 DAG)
```

8 PROV-O braids registered: vcs, squirrel, scan-sweep-sort, tuebor,
campfire, epitope, human, mesh.

### Node Atomic ✅ (headless)

ToadStool in `--headless` mode (no GPU/NPU probes, pure-compute IPC).
Capabilities: `compute`, `cpu`, `orchestration`. Enforces riboCipher
transport signal (`0xEC 0x01` prefix).

BarraCuda in cpu-shader mode. Domain: math — fleet bingo maze math,
immunity/opsonization algebra. NOT a GPU primal.

### biomeOS Neural API ✅

Auto-discovered 1,053 capabilities from 57 primal entries by scanning
`/run/user/0/biomeos/*.sock`. Bootstrap mode (no Tower Atomic BTSP).
Background discovery sweep every 30s. Stale-registration prune every 60s.

### petalTongue Universal UI ✅

Dual-port mode: HTTP `:8090` (web UI + API) + IPC (petaltongue.sock).
WebSocket bridge at `/ws`. Connected to Neural API via family ID bridge
symlink. Reports `neural_api: true` and 57 primals in topology.

---

## Resource Usage

| Metric | Value |
|--------|-------|
| Processes | 18 (12 primals + 3 infra + biomeOS + 2 cron) |
| Memory | 827MB / 2GB (42%) |
| Sockets | 24 biomeos + 8 ecosystem + 3 membrane = 35 |
| systemd units | 13 enabled |
| Public domains | 21 (via Caddy) |
| Uptime | 22 weeks |

---

## Build Artifacts

All binaries built on eastgate (i9-14900K) with `cargo build --release`
(LTO), then scp'd to golgi.

| Binary | Size | Build notes |
|--------|------|-------------|
| tower | 5.4M | `-p biomeos-core` |
| biomeos | 22M | `-p biomeos-unibin`, needs `RUST_MIN_STACK=33554432` |
| toadstool | 13.3M | `-p toadstool` (crates/cli) |

---

## Known Constraints

1. **No GPU**: toadStool headless, barraCuda cpu-shader only. No coralReef.
2. **No family seed**: BTSP optional. biomeOS in bootstrap mode.
3. **Memory ceiling ~850MB**: skunky-ingest is largest variable consumer.
4. **golgi /opt/forgejo/data/ — 1.2GB**: Safe to delete after Oct 18.
5. **WireGuard tunnel**: If WG drops, eastgate→golgi publish flow breaks.
6. **Family ID mismatch**: petalTongue uses `nat0`, biomeOS uses `default`.
   Bridged with symlink. Will align when family seed is deployed.
