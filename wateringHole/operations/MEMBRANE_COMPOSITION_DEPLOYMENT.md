<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Membrane Composition Deployment — VPS Sovereign Boundary

**Wave**: 178b | **Authority**: wateringHole consensus
**Date**: 2026-10-17
**Status**: Active — validated on golgi (18 processes, 827MB/2GB, 42%)
**Prerequisites**: VPS_ENMESHMENT_STANDARD.md, GATE_NUCLEUS_SYSTEMD_STANDARD.md

---

## Overview

A membrane node is NOT a gate. Gates run full NUCLEUS (13 primals on
desktop hardware with GPUs). A membrane node runs a **composition subset**
appropriate for its role: public-facing relay, content routing, and
ecosystem coordination on constrained hardware (2GB VPS).

This document defines how to deploy and operate a membrane composition,
validated by the golgi deployment (Wave 178b).

---

## Membrane vs Gate

| Property | Gate | Membrane |
|----------|------|----------|
| **Hardware** | Desktop (16–128GB RAM, GPU) | VPS (2–4GB RAM, no GPU) |
| **Composition** | Full NUCLEUS (13 primals) | Tower + Nest + Node (subset) |
| **GPU primals** | coralReef, toadStool (GPU mode) | toadStool (headless), barraCuda (cpu-shader) |
| **Deploy graph** | `nucleus_complete.toml` | `membrane_deploy.toml` |
| **Gate manifest** | Listed in `gate_manifest.toml` | NOT listed — separate topology |
| **biomeOS mode** | `nucleus start` | `neural-api --btsp-optional` |
| **petalTongue** | `live` (desktop + IPC) | `web --ipc` (HTTP + IPC dual-port) |
| **Family seed** | From `plasmidBin seed_workflow.sh` | Not required (standalone mode) |
| **BTSP** | Enforced (covalent family) | Optional (no family seed on VPS) |

---

## Composition Architecture

The membrane runs three atomics plus orchestration:

```
biomeOS Neural API (orchestration substrate)
  │
  ├── Tower Atomic (trust boundary)
  │   ├── bearDog    → crypto.sock, btsp.sock, ed25519.sock, x25519.sock
  │   ├── songBird   → network.sock (TCP :7700 + drawbridge :7780)
  │   └── skunkBat   → security.sock (TCP :9750)
  │
  ├── Nest Atomic (storage + provenance)
  │   ├── nestGate   → TCP :9870 (HTTP/REST)
  │   ├── rhizoCrypt → dag.sock (ephemeral DAG)
  │   ├── loamSpine  → ledger.sock, permanence.sock (permanent)
  │   └── sweetGrass → provenance.sock (TCP :9850, attribution)
  │
  ├── Node Atomic (compute — headless)
  │   ├── toadStool  → compute.sock (riboCipher, headless mode)
  │   └── barraCuda  → math.sock (cpu-shader mode)
  │
  └── Meta
      ├── petalTongue → petaltongue.sock, visualization.sock (TCP :8090)
      └── swarmVine   → swarmvine.sock (TCP :7800, gossip)
```

### Not on membrane

- **coralReef**: Requires GPU for shader compilation
- **squirrel**: Runs as MCP binary, not as NUCLEUS primal on membrane
- **primalSpring**: Validation tool, not continuous process

---

## Socket Mesh Convention

### Directory structure

```
/run/user/0/biomeos/          ← Primal sockets (UDS IPC)
  ├── beardog.sock            ← Primary socket
  ├── crypto.sock             ← Capability symlink → beardog.sock
  ├── btsp.sock               ← Capability symlink
  ├── ed25519.sock            ← Capability symlink
  ├── x25519.sock             ← Capability symlink
  ├── songbird.sock
  ├── network.sock            ← Capability symlink → songbird.sock
  ├── skunkbat.sock
  ├── security.sock           ← Capability symlink → skunkbat.sock
  ├── nestgate.sock
  ├── rhizocrypt.sock
  ├── rhizocrypt.tarpc.sock   ← tarpc transport
  ├── dag.sock                ← Capability symlink → rhizocrypt.sock
  ├── loamspine.sock
  ├── loamspine.tarpc.sock
  ├── ledger.sock             ← Capability symlink → loamspine.sock
  ├── permanence.sock         ← Capability symlink → loamspine.sock
  ├── sweetgrass.sock
  ├── sweetgrass.tarpc.sock
  ├── provenance.sock         ← Capability symlink → sweetgrass.sock
  ├── barracuda.sock
  ├── math.sock               ← Capability symlink → barracuda.sock
  ├── compute.sock            ← toadStool primary
  ├── compute.tarpc.sock
  ├── toadstool.sock          ← Name symlink
  ├── petaltongue.sock
  ├── petaltongue.tarpc.sock
  ├── petaltongue.negotiate.sock  ← G65 BTSP Phase 3
  ├── visualization.sock      ← Capability symlink → petaltongue.sock
  └── swarmvine.sock

/run/user/0/ecosystem/        ← Legacy bearDog sockets (ecosystem convention)
  ├── beardog.sock
  ├── beardog.tarpc.sock
  ├── beardog-health.sock
  ├── btsp.sock
  ├── crypto.sock
  ├── ed25519.sock
  ├── security.sock
  └── x25519.sock

/run/user/0/membrane/         ← biomeOS Neural API sockets
  ├── neural-api-default.sock
  ├── neural-api-default.tarpc.sock
  └── biomeos-api-default.sock
```

### Socket naming rules

1. Primary socket: `/run/user/0/biomeos/<primal-name>.sock`
2. Capability symlinks: `/run/user/0/biomeos/<domain>.sock → <primal>.sock`
3. tarpc transport: `/run/user/0/biomeos/<primal>.tarpc.sock`
4. biomeOS Neural API: `/run/user/0/membrane/neural-api-<family_id>.sock`

### Family ID bridge

petalTongue defaults to family ID `nat0`. biomeOS defaults to `default`.
Bridge with symlink:

```bash
ln -sf /run/user/0/membrane/neural-api-default.sock \
       /run/user/0/biomeos-neural-api-nat0.sock
```

---

## RiboCipher Transport Signal

ToadStool enforces the riboCipher transport signal standard. JSON-RPC
clients MUST prepend `[0xEC, 0x01]` before the JSON payload:

```bash
# Without riboCipher — REJECTED
echo '{"jsonrpc":"2.0","method":"health.liveness","id":1}' | \
  socat - UNIX-CONNECT:/run/user/0/biomeos/compute.sock
# → "Connection rejected: missing riboCipher signal"

# With riboCipher — OK
printf '\xEC\x01{"jsonrpc":"2.0","method":"health.liveness","id":1}\n' | \
  socat - UNIX-CONNECT:/run/user/0/biomeos/compute.sock
# → {"jsonrpc":"2.0","result":{"status":"alive"},"id":1}
```

Protocol type `0x01` = plain JSON-RPC (cleartext). Other primals
(bearDog, rhizoCrypt, loamSpine, etc.) accept plain JSON-RPC without
the riboCipher prefix. The standard is defined in
`protocols/RIBOCIPHER_TRANSPORT_SIGNAL_STANDARD.md`.

---

## Deployment Process

### Phase 1: Build on eastgate

```bash
cd ~/Development/ecoPrimals/primals/<primal>
cargo build --release --bin <binary>
```

Build notes:
- biomeOS requires `RUST_MIN_STACK=33554432` for LTO linking
- Use `-p <package-name>` when workspace has multiple binary crates
- toadStool binary target is in `crates/cli/` (`cargo build --release --bin toadstool`)

### Phase 2: Deploy to golgi

```bash
scp target/release/<binary> golgi:/opt/membrane/<binary>
ssh golgi 'chmod +x /opt/membrane/<binary>'
```

Binary sizes (release, LTO):
| Binary | Size | Package |
|--------|------|---------|
| beardog | 7.3M | beardog |
| songbird | 8.1M | songbird |
| skunkbat | 5.8M | skunkbat-cli |
| nestgate | 6.2M | nestgate |
| rhizocrypt | 5.5M | rhizocrypt |
| loamspine | 5.0M | loamspine |
| sweetgrass | 4.8M | sweetgrass |
| barracuda | 5.3M | barracuda |
| toadstool | 13.3M | toadstool (crates/cli) |
| petaltongue | 12.5M | petaltongue |
| tower | 5.4M | biomeos-core |
| biomeos | 22M | biomeos-unibin |
| swarmvine | 3.2M | swarmvine |

### Phase 3: Start primals (topological order)

```bash
# Phase 1: Tower Atomic
beardog server
songbird server --port 7700
skunkbat server  # or via systemd

# Phase 2: Nest Atomic
nestgate service start --port 9870
rhizocrypt server
loamspine server
sweetgrass server --http-port 9850

# Phase 3: Node Atomic (headless)
TOADSTOOL_SECURITY_WARNING_ACKNOWLEDGED=1 toadstool server --headless
barracuda service

# Phase 4: Orchestration
biomeos neural-api --graphs-dir /opt/membrane/graphs --btsp-optional

# Phase 5: Meta
petaltongue web --port 8090 --docroot /opt/membrane/live-terminal \
  --spa --allowed-origins "*" --cache-ttl 5 --ipc
swarmvine --gate-id golgi
```

### Phase 4: Create systemd units

Every primal gets a systemd unit at `/etc/systemd/system/<primal>.service`:

```ini
[Unit]
Description=<PrimalName> <role description>
After=network.target beardog.service

[Service]
Type=simple
ExecStart=/opt/membrane/<binary> <args>
Restart=on-failure
RestartSec=5
StandardOutput=append:/var/log/membrane/<primal>.log
StandardError=append:/var/log/membrane/<primal>.log

[Install]
WantedBy=multi-user.target
```

Enable all units:
```bash
systemctl daemon-reload
systemctl enable beardog songbird skunkbat nestgate rhizocrypt \
  loamspine sweetgrass barracuda toadstool biomeos petaltongue swarmvine
```

### Phase 5: Wire petalTongue to Neural API

```bash
# Create family ID bridge symlink
ln -sf /run/user/0/membrane/neural-api-default.sock \
       /run/user/0/biomeos-neural-api-nat0.sock

# Restart petalTongue to discover Neural API
systemctl restart petaltongue
```

Verify: `curl http://127.0.0.1:8090/api/status` should show `"neural_api": true`.

---

## Health Verification

### Quick check (all primals)

```bash
# JSON-RPC health on UDS
for sock in crypto dag ledger provenance math security network; do
  echo "$sock: $(echo '{"jsonrpc":"2.0","method":"health.liveness","id":1}' | \
    socat -t1 - UNIX-CONNECT:/run/user/0/biomeos/$sock.sock 2>/dev/null | \
    python3 -c 'import sys,json; print(json.load(sys.stdin)["result"]["status"])' 2>/dev/null || echo 'down')"
done

# toadStool (needs riboCipher)
printf '\xEC\x01{"jsonrpc":"2.0","method":"health.liveness","id":1}\n' | \
  socat -t1 - UNIX-CONNECT:/run/user/0/biomeos/compute.sock

# HTTP health endpoints
curl -s http://127.0.0.1:9850/health   # sweetGrass
curl -s http://127.0.0.1:9870/health   # nestGate
curl -s http://127.0.0.1:8090/api/status  # petalTongue
```

### Composition health methods

Per COMPOSITION_HEALTH_STANDARD.md:

| Method | Stack | Expected on membrane |
|--------|-------|--------------------|
| `composition.tower_health` | bearDog + songBird + skunkBat | Yes |
| `composition.nest_health` | Tower + nestGate + provenance trio | Yes |
| `composition.node_health` | Tower + toadStool + barraCuda | Yes (headless) |

---

## Memory Budget (2GB VPS)

| Component | Typical RSS |
|-----------|------------|
| caddy | ~130MB |
| skunky-ingest | ~200MB |
| opsonize-rs | ~16MB |
| beardog | ~8MB |
| songbird | ~12MB |
| skunkbat | ~12MB |
| nestgate | ~4MB |
| rhizocrypt | ~4MB |
| loamspine | ~4MB |
| sweetgrass | ~4MB |
| barracuda | ~5MB |
| toadstool | ~6MB |
| biomeos | ~12MB |
| petaltongue | ~14MB |
| swarmvine | ~4MB |
| **Total** | **~435MB primal + ~350MB infra ≈ 800MB** |

Ceiling: **~850MB** with all 18 processes. Leaves ~1.1GB for buffer/cache
and OS. Monitor with `free -m`. If memory exceeds 1.5GB, check for
skunky-ingest growth (largest variable consumer).

---

## biomeOS Neural API Auto-Discovery

When `biomeos neural-api` starts, it:

1. Scans `/run/user/0/biomeos/*.sock` for primal sockets
2. Queries each socket for `capabilities.list`
3. Registers all discovered capabilities in the Neural API registry
4. Starts background discovery sweep (every 30s)
5. Starts stale-registration prune sweep (every 60s)
6. Creates socket at `/run/user/0/membrane/neural-api-<family_id>.sock`

On golgi (Wave 178b): **1,053 capabilities from 57 primal entries**
auto-discovered from the socket mesh. No manual registration needed.

The Neural API operates in BOOTSTRAP mode on membrane nodes (no Tower
Atomic BTSP handshake). Use `--btsp-optional` flag.

---

## Caddy Integration

Each primal's public surface gets a Caddy block in `/etc/membrane/Caddyfile`:

```caddy
live.primals.eco {
    import security_headers
    reverse_proxy 127.0.0.1:8090  # petalTongue web
}
```

See `protocols/CADDY_DEPLOY_PROTOCOL.md` for full Caddy configuration.

---

## What Tower Observer Already Does

The existing `tower-observer.sh` cron (runs every 2 minutes) already:
- Polls `health.liveness` on all sockets
- Writes `/opt/ecoPrimals/hud/site/public/tower.json`
- Reports to squirrel via `/run/membrane/squirrel.sock`

This predates the biomeOS Neural API and provides a complementary
health monitoring layer.

---

## References

- `compositions/PRIMAL_REGISTRY.md` — Authoritative primal catalog
- `compositions/COMPOSITION_HEALTH_STANDARD.md` — Health method naming
- `compositions/MEMBRANE_CHANNEL_ARCHITECTURE.md` — Three-channel model
- `operations/GATE_NUCLEUS_SYSTEMD_STANDARD.md` — Gate systemd pattern
- `operations/VPS_ENMESHMENT_STANDARD.md` — Initial VPS setup
- `protocols/RIBOCIPHER_TRANSPORT_SIGNAL_STANDARD.md` — Transport signal
- `specs/TRANSPORT_MATRIX.md` — Per-primal wire protocols
- `projectNUCLEUS/specs/COMPOSITION_CONTRACT.md` — Deploy graph format
- `projectNUCLEUS/specs/EXECUTION_MODEL.md` — Startup ordering
- `projectNUCLEUS/deploy/gate_manifest.toml` — Gate registry (membrane NOT listed)
- `biomeOS/graphs/membrane_deploy.toml` — Membrane deploy graph
