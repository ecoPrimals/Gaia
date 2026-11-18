# cellMembrane — Reinforcement Checkpoint: All Upstream Debt Clear + K-Derm Interaction Membrane

**From**: primalSpring (upstream)
**To**: cellMembrane team (ironGate)
**Date**: May 26, 2026
**Wave**: 52 (post-pipeline-evolution)
**Priority**: High — window for reinforcement before K-Derm interaction work
**Status**: Upstream debt zero. cellMembrane can fully checkpoint and advance.

---

## Upstream Debt Status: CLEAR

All primal mountain debt, primalSpring debt, and plasmidBin debt is resolved.
cellMembrane has no upstream blockers from the build/deploy pipeline.

| Domain | Status | Evidence |
|--------|--------|----------|
| **plasmidBin validate** | 100/100 pass, 0 fail | sourDough harvest added 2 checks |
| **plasmidBin fetch --all** | 0 failures | Nascent primals (sourDough, esotericWebb, primalSpring) skip gracefully |
| **plasmidBin debt markers** | Zero `TODO`/`FIXME`/`HACK` in Rust crates | Scanned |
| **primalSpring debt markers** | Zero in Rust/shell source | 780 lib pass, 9 live-tier (require NUCLEUS), 2 ignored |
| **biomeOS UniBin naming** | Resolved upstream | `biomeos` primal + `biome` CLI helper, `sources.toml` cleaned |
| **sourDough** | First harvest shipped | 3-arch assets on release, checksums committed |
| **Checksum key drift** | Fixed | `harvest.rs` → `source_id` keys, orphans merged |
| **`gh` CLI hang risk** | Fixed | 15s timeout on `resolve_release_tag` + `resolve_recent_tags` |
| **Manifest staleness** | Fixed | `harvest --version-tag` auto-updates `manifest.toml` latest |
| **Reproducible builds** | Shipped | `build --commit SHA` pins to dispatch commit |

### What this means for cellMembrane

- **Runner builds will not stall** on nascent primals or `gh` auth prompts
- **Self-hosted runner on ironGate** can harvest any primal without naming confusion
- **`plasmidbin validate`** is the canonical health check — 100 checks, all passing
- **2nd runner on eastGate** (Wave 52b) can proceed with confidence in pipeline correctness

---

## Requested: Full Checkpoint

With upstream debt at zero, cellMembrane should reinforce and fully checkpoint
before advancing to K-Derm interaction work. Checkpoint items:

### 1. Validate ironGate self-hosted runner

```bash
cd infra/plasmidBin
git pull
cargo run -p plasmidbin -- validate .    # Expect 100/100
cargo run -p plasmidbin -- fetch --all   # sourDough should download, esotericWebb skips
```

### 2. Pull latest across cellMembrane's repos

```bash
cd gardens/cellMembrane   && git pull
cd infra/plasmidBin        && git pull    # Has fetch resilience + sourDough checksums
cd infra/wateringHole      && git pull    # Has this handoff + Wave 52 pipeline handoff
```

### 3. Run cellMembrane's own test suite

```bash
cd gardens/cellMembrane
cargo test --all           # Expect 80 pass, 0 fail
cargo clippy --all-targets # Expect 0 warnings
```

### 4. Verify VPS diderm topology health

```bash
ssh root@[RELAY_PUBLIC] 'systemctl list-units membrane-*'
# Confirm beardog-membrane, songbird-relay, skunkbat-membrane, hbbs/hbbr active
```

### 5. Update GLACIAL_SHIFT_TRACKER.md

Mark Wave 52 pipeline evolution as received. Note upstream debt zero status.
Confirm 2 direct blockers (Nest expansion, DNS) are still the only cellMembrane-owned blockers.

---

## K-Derm Interaction Membrane Setup

With the checkpoint confirmed, the next evolution is to wire K-Derm topology
awareness into the upstream pipeline — so that primalSpring and plasmidBin
understand the membrane layers they deploy into.

### What we need from cellMembrane

| Item | Detail |
|------|--------|
| **`cellmembrane-types` as dependency** | primalSpring needs `EnvelopeTopology`, `EnvelopeLayer`, `BondType`, `ChannelProtein` types for deploy graph validation. Publish `cellmembrane-types` to the workspace or expose via wateringHole wire contract. |
| **K-Derm layer placement per primal** | Which primals belong at which envelope layer? e.g. BearDog at plasma membrane, Songbird TURN at outer membrane. This mapping drives deploy graph correctness checks. |
| **`membrane.toml` schema contract** | The `topology`, `composition`, `provider` fields that downstream tools should parse. Already in `config.rs` — just needs a wateringHole standard document. |
| **Boundary crossing policy** | Which bond types are valid at each layer boundary? cellMembrane already has `BoundaryPolicy` in `envelope.rs`. Expose the canonical policy set so primalSpring can validate deploy graph `bonding_policy` sections against it. |

### What primalSpring will build (after cellMembrane provides above)

| Item | Detail |
|------|--------|
| **K-Derm-aware deploy graph validation** | New validation tier: check that graph nodes are placed in valid envelope layers per the K-Derm model |
| **`s_kderm_boundary` scenario** | Validation scenario that verifies bonding policies match K-Derm boundary rules |
| **plasmidBin deploy awareness** | `plasmidbin fetch` / `plasmidbin start` can resolve which composition tier maps to which K-Derm topology |
| **benchScale integration** | Leverage `kderm_diderm_membrane.yaml` topology for automated boundary crossing tests |

### Interaction sequence

```
cellMembrane (K-Derm spec + types)
  → wateringHole (wire contract: layer placement, boundary policy)
    → primalSpring (deploy graph validation against K-Derm model)
      → plasmidBin (deploy-time topology awareness)
        → benchScale (automated boundary crossing tests)
```

---

## Glacial Shift Tracker Update

After checkpoint, cellMembrane's remaining path to stadial entry:

| Wave | Owner | Item | Status |
|------|-------|------|--------|
| 52b | cellMembrane | 2nd self-hosted runner on eastGate | PENDING |
| 52c | cellMembrane | **This checkpoint + K-Derm wire contract** | NEW |
| 53 | cellMembrane | Forgejo Actions shadow CI | PENDING |
| 54 | cellMembrane + primalSpring | Build inversion (Forgejo-primary) | HORIZON |
| — | cellMembrane | Blocker 1: Nest expansion on VPS | BLOCKED |
| — | cellMembrane | Blocker 2: DNS → sovereign knot-dns | BLOCKED |

---

## Requested Actions

- [ ] Pull latest plasmidBin, wateringHole, cellMembrane
- [ ] Run `plasmidbin validate` on ironGate — confirm 100/100
- [ ] Run `cargo test --all` in cellMembrane — confirm 80/80
- [ ] Verify VPS diderm services active
- [ ] Update GLACIAL_SHIFT_TRACKER.md with checkpoint status
- [ ] Publish K-Derm wire contract to wateringHole (layer placement, boundary policy, membrane.toml schema)
- [ ] Provision 2nd self-hosted runner on eastGate (Wave 52b carry-forward)
