# Delta Spring Covalent Mesh — Sound Off

**Date**: May 25, 2026
**From**: primalSpring (eastGate)
**To**: All delta spring teams

---

## What happened

Wave 48: the covalent mesh stack is complete. Every piece of software needed
for springs to share NUCLEUS across LAN gates is shipped and tested. We added
a `## Gate Deployment` section to each spring's CONTEXT.md. Four springs
already have operational NUCLEUS on named gates. Four are pending.

## What we need from you

### 1. Sound off: gate + hardware

Update your `## Gate Deployment` section in CONTEXT.md (already templated).
Replace `pending — declare your gate` with your actual gate name. Tell us
what hardware you're on. Example:

```
| **Gate** | strandGate |
| **Hardware** | Dual EPYC 7452 (64c), 256GB ECC |
| **Composition** | Full NUCLEUS |
```

### 2. Start sharing NUCLEUS

If NUCLEUS is already running on your gate, you're done — just enable
Songbird TCP federation so other gates can find you:

```bash
# Bash launcher:
SONGBIRD_FEDERATION_PORT=7700 ./tools/nucleus_launcher.sh start

# Rust launcher (primalSpring ecoPrimal binary):
nucleus_launcher --family-id <your-family> --federation-port 7700
```

If you haven't started NUCLEUS yet, either command works. It starts primals
over UDS on your local machine and opens Songbird TCP on port 7700 for
cross-gate LAN discovery.

### 3. Deploy your cell

```bash
./tools/cell_launcher.sh <yourspring> start
```

This layers your spring on top of the running NUCLEUS using the cell graph
in `plasmidBin/cells/<spring>_cell.toml`.

### 4. Verify you can see other gates

```bash
curl -s -X POST http://127.0.0.1:7700 \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"discovery.peers"}' | jq .result
```

If you see peers from other gates, you're covalently linked.

---

## Complete roster (all 8/8 sounded off — May 25, 2026)

| Spring | Gate | Hardware | Status |
|--------|------|----------|--------|
| primalSpring | eastGate | i9-12900, RTX 4070 + Akida, 32GB | **operational** |
| primalSpring | ironGate | i9-14900K, RTX 5070, 96GB | **operational** |
| airSpring | eastGate | i9-12900, RTX 4070 + Akida, 32GB | **operational** |
| groundSpring | eastGate | i9-12900, RTX 4070 + Akida, 32GB | **operational** |
| ludoSpring | ironGate | i9-14900K, RTX 5070, 96GB | **operational** (12/12 proto-nucleate) |
| healthSpring | ironGate | i9-14900K, RTX 5070, 96GB | **operational** (23 UDS, 4 domain caps) |
| wetSpring | southGate | 5800X3D, RTX 4060 + 3090s, 128GB | **operational** (V185, bonding wired) |
| neuralSpring | southGate | 5800X3D, 128GB DDR4 | **operational** (9/13 UDS, federation live) |
| hotSpring | biomeGate | TR 3970X, RTX 3090 + Titan V, 256GB | **operational** |

**4 gates, 8 springs, all operational.** Songbird TCP :7700 on all gates.

## What's already working

- All 13 primals accept `--socket` + `--port` (behavioral convergence)
- biomeOS v3.75 routes `capability.call` to remote gates via Songbird mesh
- toadStool S274 yields GPU to gate owner when foreground load spikes
- Cell deployment graphs exist for all 8 springs
- Family seed + BTSP bootstrap tooling is ready
- Songbird TCP federation (port 7700) handles cross-gate discovery

## What this enables

Once your gate has NUCLEUS + federation, any spring on any gate can call
any capability on any other gate — transparently. `capability.call` from
wetSpring on southGate can reach hotSpring's physics engine on biomeGate
without either spring knowing the routing details. biomeOS handles it.

When 3+ gates are meshed: `biomeos plasmodium status` shows the collective.

---

**Full details**: `WAVE48_COVALENT_SPRING_MESH_MAY25_2026.md` (same folder)
**Architecture**: `DISTRIBUTED_COVALENT_DEPLOYMENT.md` (wateringHole root)
