# River Delta — Wave 50: Post-Primordial Absorption + Covalent HPC

**From**: primalSpring (coordinator)
**To**: All delta springs
**Date**: May 25, 2026
**Wave**: 50

---

## Context

NUCLEUS is 12/12 ALIVE on eastGate (plasmidBin musl binaries). All 13 primals
at zero debt. Peer seeding (`SONGBIRD_PEERS`) shipped. 4 gates operational with
Songbird TCP :7700 federation. The primals on the mountain have cleared — now
the river delta catches up and begins evolving toward covalent HPC.

---

## Ecosystem-wide mandates

### 1. Post-primordial: zero `target/release/` for NUCLEUS primal binaries

All primal binaries come from `plasmidBin` only. No `target/release/<primal>`
fallbacks in composition or launcher scripts. Spring cell binaries (your own
`target/release/<spring_unibin>`) are fine — this applies only to NUCLEUS
primals (beardog, songbird, toadstool, nestgate, squirrel, barracuda,
coralreef, rhizocrypt, loamspine, sweetgrass, petaltongue, biomeos, skunkbat).

**How to check**: `grep -rn 'target/release' tools/ scripts/ | grep -v '#'`
— any hits for primal names must be removed and replaced with `find_binary`
from plasmidBin or env-based discovery.

### 2. NUCLEUS sharing on your gate

Each spring should be able to start NUCLEUS on its gate and validate basic
composition. Use primalSpring's `tools/nucleus_launcher.sh` or the Rust
`nucleus_launcher` binary (both in plasmidBin).

```bash
# From your spring root:
SONGBIRD_FEDERATION_PORT=7700 \
  bash ../primalSpring/tools/nucleus_launcher.sh start

# Verify:
bash ../primalSpring/tools/nucleus_launcher.sh status
# → 12/12 ALIVE
```

### 3. Begin covalent HPC evolution

Once NUCLEUS is alive on your gate, seed Songbird peers to mesh with other
gates on the LAN:

```bash
# Set peer addresses for cross-gate discovery
export SONGBIRD_PEERS="192.168.1.144:7700,192.168.1.238:7700"

# Or via RPC after startup:
echo '{"jsonrpc":"2.0","method":"mesh.init","params":{"bootstrap_peers":["192.168.1.144:7700"]},"id":1}' \
  | socat - UNIX-CONNECT:/run/user/$(id -u)/biomeos/songbird-nucleus01.sock
```

Cross-gate `capability.call` is the target — your spring's composition graphs
should be able to call capabilities on remote gates via Songbird mesh routing.

---

## Per-spring guidance

### airSpring (eastGate) — Wave 49 DONE

Gate: eastGate (i9-12900, RTX 4070 + Akida, 32GB)
Status: Post-primordial confirmed. 12/12 NUCLEUS.

**Wave 50**:
- [ ] Validate cross-gate `capability.call` from eastGate → ironGate (co-resident with primalSpring)
- [ ] Begin neuromorphic composition: explore `toadstool.compute` dispatch to Akida via barraCuda WGSL bridge
- [ ] Seed `SONGBIRD_PEERS` with ironGate address in your gate startup

### groundSpring (eastGate) — Wave 49 DONE

Gate: eastGate (co-resident with airSpring, primalSpring)
Status: Post-primordial confirmed. V146.

**Wave 50**:
- [ ] Validate degradation behavior scenarios against live NUCLEUS (NestGate IPC)
- [ ] Begin cross-gate data dependency staging — `nest.sync` graph from biomeOS for backup to ironGate

### healthSpring (ironGate) — Wave 49 DONE

Gate: ironGate (i9-14900K, RTX 5070, 96GB)
Status: Post-primordial confirmed. V65a. 57 scenarios.

**Wave 50**:
- [ ] Launch NUCLEUS on ironGate if not already running
- [ ] Validate dual-tower composition against live NUCLEUS (7/7 Tower A claims)
- [ ] Seed `SONGBIRD_PEERS` with eastGate address
- [ ] Begin covalent health monitoring: cross-gate `health.liveness` sweep via mesh

### ludoSpring (ironGate) — Wave 49 DONE

Gate: ironGate (co-resident with healthSpring)
Status: Post-primordial confirmed. 11/11 NUCLEUS PASS.

**Wave 50**:
- [ ] Validate proto-nucleate graph against live NUCLEUS on ironGate
- [ ] GAP-01 coralReef shader: test `shader.compile_wgsl` call against live barraCuda/coralReef
- [ ] Begin cross-gate game state sync: explore `nest.sync` for persistent game state on remote NestGate

### neuralSpring (southGate) — Wave 49 DONE (1 fix needed)

Gate: southGate (5800X3D, RTX 4060 + 3090s, 128GB)
Status: Post-primordial claimed, but **`composition_nucleus.sh` line 396 still
hardcodes `primals/petalTongue/target/release/petaltongue`**. Must fix.

**Wave 50**:
- [ ] **FIX**: Remove `target/release/petaltongue` hardcode in `tools/composition_nucleus.sh:396` — use `find_binary petaltongue` only
- [ ] Launch NUCLEUS on southGate
- [ ] Seed `SONGBIRD_PEERS` — note: southGate (192.168.4.x) is on a different subnet than eastGate/ironGate (192.168.1.x). Cross-subnet mesh requires router config or TURN relay via cellMembrane
- [ ] Begin agentic covalent: explore `science.*` method dispatch across gates for distributed experiment execution

### wetSpring (southGate) — Wave 49 DONE

Gate: southGate (co-resident with neuralSpring)
Status: Post-primordial confirmed. V186. 1,962+ tests.

**Wave 50**:
- [ ] Validate breseq pipeline against live NUCLEUS on southGate
- [ ] WS-2 cross-spring data exchange: test `nest.sync` live orchestration with loamSpine on remote gate
- [ ] WS-11 variant caller parity: run Tenaillon batch 0 re-measurement against covalent compute (toadStool on remote gate)
- [ ] Same subnet caveat as neuralSpring — document cross-subnet workaround if needed

### hotSpring (biomeGate) — Wave 48 (behind)

Gate: biomeGate (Threadripper 3970X, 256GB)
Status: **Not post-primordial**. Still on Wave 48. Active experiment cluster (Exp 219-222).

**Wave 50**:
- [ ] Absorb post-primordial mandate: remove `target/release/toadstool` fallback in `scripts/boot/install-glowplug.sh`
- [ ] Confirm plasmidBin-only binary sourcing in all active launchers
- [ ] Launch NUCLEUS on biomeGate — this gate has 256GB RAM and Threadripper, ideal for HPC composition
- [ ] Begin sovereign GPU compute: explore `toadstool.compute` + barraCuda dispatch for CAZyme FEL workloads via NUCLEUS composition instead of direct binary calls

---

## Covalent HPC target state

```
eastGate ←→ ironGate ←→ southGate ←→ biomeGate
   │              │            │            │
airSpring    healthSpring  neuralSpring  hotSpring
groundSpring ludoSpring    wetSpring
primalSpring
```

Each gate runs NUCLEUS (12/12 primals). Songbird TCP :7700 federates them.
Springs compose capabilities across gates via `capability.call` through the
mesh. HPC workloads (GPU compute, bioinformatics, neuromorphic) flow to the
gate with the right hardware. This is covalent HPC — shared compute through
the NUCLEUS bond.

**Next milestone**: 2+ gates meshed with live `discovery.peers` returning
peer count > 0. Then cross-gate `capability.call` smoke test via primalSpring
`s_covalent_mesh` scenario.

---

## How to respond

1. Fix any remaining `target/release/` primal hardcodes
2. Confirm NUCLEUS 12/12 ALIVE on your gate
3. Seed `SONGBIRD_PEERS` with at least one other gate
4. Report back: `<spring> Wave 50: NUCLEUS <count>/12 on <gate>, peers seeded, covalent ready`
