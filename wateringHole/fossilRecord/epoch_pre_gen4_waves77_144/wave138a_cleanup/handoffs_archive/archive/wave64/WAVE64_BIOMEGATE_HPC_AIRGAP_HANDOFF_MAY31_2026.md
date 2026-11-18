# Wave 64 Handoff: biomeGate — HPC / Air-Gap Validation

**From**: eastGate (overwatch)
**To**: biomeGate / hotSpring team
**Date**: May 31, 2026
**Context**: biomeGate SSH key registered on Forgejo (ID: 8, fingerprint SHA256:uqeeNUOkfospwVNJTZ+2Kdo9VwJUOhm8hhXDN5xKirk). K-Derm diderm relay live. biomeGate's async hardware cadence serves as the air-gap validation loop for temporal sync tolerance.

---

## Wave 64 Assignments

### 1. Songbird federation restart (independent, priority)

This unblocks everything else:
```bash
# In your shell profile or systemd service:
export SONGBIRD_FEDERATION_PORT=7700
export SONGBIRD_PEERS="192.168.1.144:7700"  # eastGate
```

- Restart Songbird with federation enabled
- Verify peer count > 0 (`songbird mesh.status` or equivalent)
- Once federated, biomeGate joins the 4-gate LAN mesh

### 2. Temporal sync validation (after federation)

```bash
cd infra/wateringHole && git pull forgejo main
cascade-pull.sh --mode check --source temporal
cascade-pull.sh --mode pull --source temporal
```

- Validate all repos reach temporal leader position
- Your async cadence (push after long compute runs) tests the system's tolerance for delayed pushes — same pattern as an air-gapped gate
- Report any fast-forward failures or divergences

### 3. hotSpring IPC rewiring — Tier 2-to-3 (independent)

Adopt `primal-proof` feature for hotSpring's NUCLEUS integration:
- Move from library calls to IPC channels
- Follow `PRIMAL_PROOF_IPC_MAPPING.md` patterns
- Local science work, no eastGate code dependency

### 4. Push toadStool + hotSpring to Forgejo (after sync)

```bash
cd primals/toadStool && git push forgejo main
cd springs/hotSpring && git push forgejo main
```

The K-Derm relay chain propagates to GitHub automatically. You don't need to push to `origin` anymore.

---

## Air-Gap Validation Role

Your async hardware cadence (HBM2 GPU compute, toadStool diesel engine experiments) naturally creates multi-day gaps between pushes. This validates:
- Temporal sync absorbs arbitrary drift without manual intervention
- K-Derm relay chain fires correctly on stale-then-fresh push patterns
- No divergence accumulates during gaps

If temporal sync breaks after a long gap, that's a bug we want to catch here first — before air-gapped field deployments depend on it.

---

## Sync First

```bash
cd infra/wateringHole && git pull forgejo main
cd gardens && git clone ssh://git@git.primals.eco:2222/sporeGarden/cellMembrane.git
cd cellMembrane/crates/membrane-shadow && cargo build --release --bin membrane
cp target/release/membrane ~/.local/bin/
membrane manifest.info  # verify topology: diderm with roles
```

---

## Wave 65 Preview

- Ionic GPU lease prototype (GAP-HS-005): `crypto.sign_contract` for cross-family metered GPU scheduling
- Cross-gate dispatch validation: toadStool yield-to-owner + compute dispatch from strandGate to biomeGate GPU
- Songbird mesh participation in `capability.call` tests

## Wave 66 Target

- Multi-provider peptidoglycan (Hetzner/Vultr node for quorum sensing validation)
- strandGate science routing: Dual EPYC bio/chem science → biomeGate GPU dispatch
- Full distributed compute mesh operational

---

*biomeGate at Wave 64. Forgejo key registered. Focus: federation restart + temporal sync validation + air-gap loop.*
