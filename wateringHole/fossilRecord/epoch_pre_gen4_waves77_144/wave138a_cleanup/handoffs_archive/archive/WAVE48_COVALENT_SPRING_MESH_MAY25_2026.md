# Wave 48 — Covalent Spring Mesh

**Date**: May 25, 2026
**Type**: Deployment — LAN Covalent Linking
**Standard**: DEPLOYMENT_BEHAVIOR_STANDARD v1.0 + DISTRIBUTED_COVALENT_DEPLOYMENT

---

## Summary

All delta springs now declare their gate assignment in their CONTEXT.md
(or README.md). The software stack for covalent mesh linking is complete:
biomeOS v3.75 Songbird mesh dispatch, toadStool S274 yield-to-owner,
Songbird TCP federation, and cell deployment graphs for all 8 springs.

This handoff tells each spring team: **spin up NUCLEUS with Songbird TCP
federation enabled, deploy your cell, and connect over LAN.**

---

## Gate Self-Reports (ALL 8/8 COMPLETE)

| Spring | Gate | NUCLEUS Status | Composition |
|--------|------|----------------|-------------|
| **primalSpring** | eastGate + ironGate | **operational** | Full NUCLEUS (13/13) |
| **wetSpring** | southGate | **operational** | Node Atomic (9/9 validated) |
| **ludoSpring** | ironGate | **operational** | Tower Atomic (11/11 proto-nucleate) |
| **hotSpring** | biomeGate | **operational** | Node Atomic (62/62 validation) |
| **neuralSpring** | southGate | **operational** | Full NUCLEUS |
| **airSpring** | eastGate | **operational** | Full NUCLEUS |
| **groundSpring** | eastGate | **operational** | Full NUCLEUS |
| **healthSpring** | ironGate | **operational** | Nest Atomic |

**8/8 springs sounded off. 4 gates operational.**

---

## Action Items — All Springs

### 1. Declare your gate

If your CONTEXT.md shows `pending — declare your gate`, update it to your
actual gate name. The gate is the machine you're developing and deploying on.

### 2. Ensure NUCLEUS is running with federation

```bash
SONGBIRD_FEDERATION_PORT=7700 ./tools/nucleus_launcher.sh start
```

This starts all 13 primals over UDS and enables Songbird TCP on port 7700
for cross-gate discovery. Without `SONGBIRD_FEDERATION_PORT`, Songbird runs
UDS-only and other gates cannot find you.

### 3. Deploy your cell

```bash
./tools/cell_launcher.sh <yourspring> start
```

This deploys your spring as a biomeOS graph on top of the running NUCLEUS.
Cell deployment graphs are in `plasmidBin/cells/<spring>_cell.toml`.

### 4. Verify LAN mesh discovery

Once 2+ gates have NUCLEUS running with `SONGBIRD_FEDERATION_PORT=7700`,
Songbird discovers peers via TCP on the LAN. Verify:

```bash
# On any gate — should show peers from other gates
curl -s -X POST http://127.0.0.1:7700 \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"discovery.peers"}' | jq
```

### 5. Test cross-gate capability.call

biomeOS v3.75 `try_songbird_mesh_dispatch()` transparently routes requests
to primals on remote gates. Test:

```bash
# From eastGate, call a capability on southGate's wetSpring
curl -s -X POST http://127.0.0.1:7700 \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"capability.call","params":{"method":"science.anderson","gate":"southGate"}}' | jq
```

---

## Mesh Topology

```
LAN Cluster (Cat6 1G)
├── eastGate ── primalSpring + airSpring + groundSpring
├── ironGate ── primalSpring + ludoSpring + healthSpring
├── southGate ── wetSpring + neuralSpring
├── biomeGate ── hotSpring
└── strandGate/northGate/westGate ── hardware ready, not deployed

All gates: NUCLEUS over UDS (composition varies per spring)
Cross-gate: Songbird TCP :7700 federation
Dispatch: biomeOS v3.75 mesh dispatch (capability.call → Songbird)
Yield: toadStool S274 GuestLoadPolicy (yield-to-owner enforced)
```

---

## Prerequisites (all shipped)

| Component | Status |
|-----------|--------|
| Cell deployment graphs | 8/8 springs in `plasmidBin/cells/` |
| `cell_launcher.sh` | Shipped in primalSpring `tools/` |
| `nucleus_launcher.sh` | Shipped with `SONGBIRD_FEDERATION_PORT` support |
| `nucleus_launcher` (Rust) | `--federation-port 7700` CLI flag (Wave 48) |
| biomeOS v3.75 mesh dispatch | `try_songbird_mesh_dispatch()` replaces `relay.allocate` |
| toadStool S274 yield-to-owner | `GuestLoadPolicy` + `YieldStrategy` enforced |
| Songbird TCP federation | Wave 213-214, TCP/WAN fallback |
| 13/13 behavioral convergence | All primals accept `--socket` + `--port` |
| Family seed tooling | `nucleus_crypto_bootstrap.sh` + `gen_seed_fingerprints.sh` |

## What This Enables

- **Local sharing**: Springs on the same gate share a NUCLEUS — zero network hop for intra-gate capability.call
- **LAN covalent**: Springs on different gates route capability.call via Songbird TCP mesh — transparent to the caller
- **Plasmodium collective**: When 3+ gates are meshed, biomeOS recognizes the aggregate as a Plasmodium with combined capabilities
- **Yield-to-owner**: Remote dispatch respects gate owner foreground load via toadStool GuestLoadPolicy

## Next Steps

1. ~~Pending springs declare their gates~~ **DONE** (8/8)
2. ~~All gates start NUCLEUS with `SONGBIRD_FEDERATION_PORT=7700`~~ **DONE** (4 gates broadcasting)
3. **NEXT**: Validate cross-gate `discovery.peers` visibility
4. Run cross-gate `capability.call` smoke test
5. Once 3+ gates are live: `biomeos plasmodium status`

## Deployment Issues (resolved in-flight)

| Issue | Resolution |
|-------|------------|
| `primal.announce` vs `discovery.register` | primalSpring `niche.rs` has auto-fallback. Springs should call `CompositionContext::announce()` which tries `primal.announce` (v3.57+) and falls back to legacy `lifecycle.register` + per-domain `capability.register`. |
| Songbird sled DB corruption after unclean shutdown | Clean `~/.local/share/songbird/task_lifecycle*` and restart. |
| Spring binaries not in plasmidBin 13-primal set | By design. Springs build their own binary from source and symlink into `plasmidBin/primals/`. |
| loamSpine Tokio runtime-in-runtime panic | Upstream loamSpine bug. Does not block mesh — skip loamSpine health probe if needed. |
