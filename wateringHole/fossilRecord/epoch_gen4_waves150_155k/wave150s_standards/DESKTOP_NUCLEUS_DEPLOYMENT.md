# Desktop NUCLEUS Deployment Guide

**Version:** 1.1.0
**Date:** April 28, 2026
**Status:** Active
**Origin:** primalSpring Phase 48 — Desktop Composition (verified live)
**License:** AGPL-3.0-or-later

---

## What Is the Desktop NUCLEUS?

The Desktop NUCLEUS is the **full 13-primal stack** deployed from pre-built
plasmidBin binaries with petalTongue in `live` mode as the desktop UI surface.
It is the standard substrate that springs compose on top of and gardens deploy
for users.

**The NUCLEUS is exactly 13 primals. No spring binaries. No dev artifacts.**

| Atomic | Particle | Primals | Role |
|--------|----------|---------|------|
| **Tower** | electron | BearDog + Songbird + skunkBat | Trust boundary, crypto, discovery, defense |
| **Node** | proton | ToadStool + barraCuda + coralReef | Compute, tensor math, shader compile |
| **Nest** | neutron | NestGate + rhizoCrypt + loamSpine + sweetGrass | Storage, DAG, ledger, attribution |
| **Meta** | cross-atomic | biomeOS + Squirrel + petalTongue | Coordinator, AI, desktop UI |

**What is NOT a primal:**
- `primalspring_primal` — IPC server (JSON-RPC cell membrane)
- `primalspring_unibin` — UniBin: certify/validate/serve/status/version (absorbed guidestone + trio)
- Spring binaries — Rust science validation, not composition nodes

**A spring IS a composition of the 13 primals**, defined by a cell graph.

---

## Quick Start

### Prerequisites

- `infra/plasmidBin` with 13/13 musl-static binaries
- A display server (X11/Wayland) for petalTongue `live` mode

### Deploy

```bash
cd springs/primalSpring

# Option A: Desktop launcher (recommended)
./tools/desktop_nucleus.sh start

# Option B: Composition launcher with full NUCLEUS
PETALTONGUE_LIVE=true ./tools/composition_nucleus.sh start

# Check status
./tools/desktop_nucleus.sh status

# Stop
./tools/desktop_nucleus.sh stop
```

### Verify

```bash
# Health check all 13 primals (IPC liveness probes)
./tools/desktop_nucleus.sh status

# Deep validation (exercises actual capabilities per atomic + crypto tiers)
./tools/desktop_nucleus.sh validate

# Crypto bootstrap (derive and store two-tier purpose keys)
./tools/nucleus_crypto_bootstrap.sh

# Verify crypto keys without re-deriving
./tools/nucleus_crypto_bootstrap.sh --verify-only

# Manual: Test Tower (crypto)
echo '{"jsonrpc":"2.0","method":"crypto.blake3_hash","params":{"data":"hello"},"id":1}' | \
    socat - UNIX-CONNECT:/run/user/$(id -u)/biomeos/beardog-${FAMILY_ID}.sock

# Test Node (compute)
echo '{"jsonrpc":"2.0","method":"compute.capabilities","id":1}' | \
    socat - UNIX-CONNECT:/run/user/$(id -u)/biomeos/toadstool-${FAMILY_ID}.sock

# Test Nest (DAG)
echo '{"jsonrpc":"2.0","method":"dag.session.create","params":{"session_id":"test"},"id":1}' | \
    socat - UNIX-CONNECT:/run/user/$(id -u)/biomeos/rhizocrypt-${FAMILY_ID}.sock

# Test Meta (proprioception)
echo '{"jsonrpc":"2.0","method":"proprioception.get","id":1}' | \
    socat - UNIX-CONNECT:/run/user/$(id -u)/biomeos/petaltongue-${FAMILY_ID}.sock
```

---

## Architecture

### Atomic Structure

The 13 primals compose from three atomics plus a meta tier. Fragment
definitions live in `primalSpring/graphs/fragments/`:

```
NUCLEUS = Tower + Node + Nest
        = (BearDog + Songbird)
        + (ToadStool + barraCuda + coralReef)
        + (NestGate + rhizoCrypt + loamSpine + sweetGrass)

Desktop NUCLEUS = NUCLEUS + Meta
               = 9 domain primals + biomeOS + Squirrel + petalTongue (live)
```

Tower mediates ALL inter-atomic bonding. No cross-gate communication
happens without passing through the electron shell (BearDog + Songbird).

### Deployment Paths

**Primary: composition_nucleus.sh** (shell-managed)
- Starts all 13 primals from plasmidBin in dependency order
- Creates family-namespaced UDS sockets
- Performs health check on each primal
- Creates capability domain symlinks

**Future: biomeOS native** (`biomeos nucleus --mode full`)
- biomeOS coordinator primal manages lifecycle
- Auto-discovery of capabilities
- Health monitoring with 10s interval
- Currently launches 5 core primals; full 13 is roadmap

### Cell Graph

The canonical desktop cell graph is:

```
primalSpring/graphs/cells/nucleus_desktop_cell.toml
```

This graph defines all 13 primals in biomeOS-compatible format with:
- `coordination = "continuous"` (long-running desktop session)
- `security_model = "btsp"` on every node
- `petaltongue` with `mode = "live"`
- `biomeos_neural_api` with `spawn = false` (already running)
- Environment passthrough for `FAMILY_ID`, `BEARDOG_FAMILY_SEED`, etc.

---

## For Springs: Composing on the Desktop NUCLEUS

Springs do NOT launch primals. A spring connects to the running NUCLEUS
via capability sockets and composes through its cell graph.

### Pattern

1. Start the Desktop NUCLEUS: `./tools/desktop_nucleus.sh start`
2. Source the composition library in your domain script
3. Discover capabilities
4. Compose your domain logic using the primals

```bash
#!/usr/bin/env bash
COMPOSITION_NAME="myspring"
REQUIRED_CAPS="visualization tensor"
OPTIONAL_CAPS="dag ledger attribution ai compute shader storage"
source /path/to/primalSpring/tools/nucleus_composition_lib.sh

discover_capabilities

# Push a scene to petalTongue
push_scene '{
    "nodes": [{"id": "main", "type": "text", "content": "My Spring Live"}]
}'

# Use tensor math via barraCuda
send_rpc "$(cap_socket tensor)" "tensor.matmul" '{"lhs_id": "a", "rhs_id": "b"}'

# Record to DAG
dag_append_event "experiment_started" '{"spring": "myspring"}'
```

### Domain Overlay Template

Copy `primalSpring/graphs/cells/nucleus_desktop_overlay_template.toml`
to create your spring's cell graph. Adjust `required = false` for
capabilities your domain doesn't need.

### What Each Capability Gives You

| Capability | Primal | What You Get |
|-----------|--------|-------------|
| `security` | BearDog | Crypto signing, hashing, encryption, keypair generation |
| `discovery` | Songbird | IPC resolution, peer discovery, HTTP requests |
| `compute` | ToadStool | Workload dispatch, execution, resource status |
| `tensor` | barraCuda | Matrix math, stats, noise generation, activation functions |
| `shader` | coralReef | WGSL/SPIRV shader compilation |
| `storage` | NestGate | Content-addressed store/retrieve |
| `dag` | rhizoCrypt | Session DAG, event append, merkle proofs |
| `ledger` | loamSpine | Permanent records, certificates, spine management |
| `attribution` | sweetGrass | Provenance braids, anchoring, verification |
| `ai` | Squirrel | Inference completion, model listing, embedding |
| `visualization` | petalTongue | Scene rendering, interaction polling, proprioception |
| `orchestration` | biomeOS | Graph deployment, capability routing |

---

## For Gardens: Deploying for Users

Gardens (esotericWebb, etc.) are the user-facing products.

1. Fetch binaries from `plasmidBin` (see `PLASMINBIN_DEPOT_PATTERN.md`)
2. Deploy the Desktop NUCLEUS using the cell graph or launcher
3. Compose your garden's UI and logic through the primal capabilities
4. petalTongue `live` mode is your native desktop window

See `GARDEN_COMPOSITION_ONRAMP.md` for the full garden contract.

---

## Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `FAMILY_ID` | No | `nucleus-desktop` | Socket namespace |
| `BEARDOG_FAMILY_SEED` | No | Auto-generated | BTSP crypto seed |
| `FAMILY_SEED` | No | `$BEARDOG_FAMILY_SEED` | rhizoCrypt BTSP seed |
| `NESTGATE_JWT_SECRET` | No | Auto-generated | NestGate auth secret |
| `NODE_ID` | No | `$(hostname)` | Node identifier |
| `BEARDOG_NODE_ID` | No | `$NODE_ID` | BearDog node ID |
| `DISPLAY` | Yes (live) | `:1` | X11/Wayland display for petalTongue |
| `ECOPRIMALS_PLASMID_BIN` | No | Auto-detect | Path to plasmidBin |
| `PETALTONGUE_LIVE` | No | `true` | Enable desktop GUI |

---

## Key Files in primalSpring

| File | Purpose |
|------|---------|
| `graphs/cells/nucleus_desktop_cell.toml` | Canonical 13-primal desktop cell graph |
| `graphs/cells/nucleus_desktop_overlay_template.toml` | Template for spring domain overlays |
| `graphs/cells/cells_manifest.toml` | Index of all deployable cell graphs |
| `graphs/fragments/tower_atomic.toml` | Tower atomic definition (electron) |
| `graphs/fragments/node_atomic.toml` | Node atomic definition (proton) |
| `graphs/fragments/nest_atomic.toml` | Nest atomic definition (neutron) |
| `graphs/fragments/meta_tier.toml` | Meta tier definition (cross-atomic) |
| `graphs/fragments/nucleus.toml` | Full NUCLEUS = tower + node + nest |
| `tools/desktop_nucleus.sh` | Desktop NUCLEUS launcher |
| `tools/composition_nucleus.sh` | Full composition launcher (13 primals) |
| `tools/nucleus_composition_lib.sh` | Reusable composition wiring library |

---

## Related Documents

- `NUCLEUS_TWO_TIER_CRYPTO_MODEL.md` — Two-tier encryption architecture and per-primal evolution
- `LIVE_GUI_COMPOSITION_PATTERN.md` — petalTongue live mode interaction loop
- `DEPLOYMENT_AND_COMPOSITION.md` — Three-layer composition architecture
- `GARDEN_COMPOSITION_ONRAMP.md` — Building gen4 products
- `PRIMAL_SPRING_GARDEN_TAXONOMY.md` — Primal / spring / garden taxonomy
- `PROVENANCE_TRIO_INTEGRATION_GUIDE.md` — DAG + ledger + attribution wiring
- `SPRING_COMPOSITION_PATTERNS.md` — Composition library patterns
- `PLASMINBIN_DEPOT_PATTERN.md` (primalSpring) — Binary depot workflow

---

## plasmidBin Binary Status (April 28, 2026)

All 13 core primals are musl-static x86_64:

```
beardog      — static-pie linked (5.1M)   ✓
songbird     — static-pie linked (7.2M)   ✓
toadstool    — static-pie linked (11M)    ✓
barracuda    — static-pie linked (5.0M)   ✓
coralreef    — static-pie linked (6.5M)   ✓
nestgate     — statically linked  (7.3M)  ✓
rhizocrypt   — static-pie linked (5.7M)   ✓
loamspine    — statically linked  (4.8M)  ✓
sweetgrass   — statically linked  (9.3M)  ✓
squirrel     — static-pie linked (3.4M)   ✓
petaltongue  — static-pie linked (27M)    ✓
biomeos      — statically linked  (13M)   ✓
```

Zero C dependencies. Portable across any x86_64 Linux.

---

## IPC Method Reference

Full method map verified live against Desktop NUCLEUS:

**`springs/primalSpring/docs/NUCLEUS_IPC_METHOD_MAP.md`**

Key discovery methods per primal:
- BearDog: `rpc.methods` (returns all namespaces and methods)
- Songbird: `rpc.discover` (returns flat method list)
- Most others: `primal.capabilities` or `capabilities.list`
- All respond to `health.liveness` with `{"status":"alive"}`
