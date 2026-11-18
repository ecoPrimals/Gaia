# Wave 64 Handoff: flockGate — sporePrint / WAN Shadow

**From**: eastGate (overwatch)
**To**: flockGate / sporePrint team
**Date**: May 31, 2026
**Context**: K-Derm diderm relay chain validated by flockGate (~3s gate-to-GitHub propagation). flockGate is the WAN shadow validation node and sporePrint product owner.

---

## Wave 64 Assignments

### 1. pseudoSpore gallery Zola template (independent)

Build the gallery template for sporePrint at `/lab/spores/{name}/`:
- Each pseudoSpore gets a page with: domain profile, module list, provenance receipts, lithoSpore download link
- Template reads from `registry.toml` (lithoSpore format) or static TOML per spore
- Currently 1 emitted spore (hotSpring CompChem v1.6.1), healthSpring profile ready
- Target: gallery template renders at least 1 spore page with provenance metadata

This is local Zola dev work — no eastGate dependency. The existing sporePrint site has 143 pages built with Zola on golgiBody-ext.

### 2. Gate bootstrap documentation validation (independent)

flockGate bootstrapped fresh and found real gaps (SSH key registration, Forgejo org paths). Feed back into GATE_SETUP_STANDARD:
- Document any remaining bootstrap friction in an AAR
- Propose fixes to `GATE_SETUP_STANDARD.md` (eastGate will merge)
- Test `bootstrap.sh` end-to-end from clean workspace

### 3. Zola build pipeline on WAN (independent)

Validate the build pipeline works over WAN:
- `zola build` locally on flockGate — confirm 143+ pages render
- Test peptidoglycan-triggered rebuilds: peptidoglycan pulls sporePrint source, builds, rsyncs to golgiBody-ext
- Measure build times and report latency over WAN vs LAN baseline

### 4. Temporal sync sustained measurement (independent)

The ~3s relay propagation was a single test. Run sustained measurement:
- Push 5-10 commits over a day, measure gate-to-GitHub propagation time for each
- Report any failures, retries, or drift
- This validates the relay chain under real WAN usage patterns

---

## Sync First

```bash
cd infra/wateringHole && git pull forgejo main
cd gardens/cellMembrane && git pull forgejo main
# Rebuild membrane
cd gardens/cellMembrane/crates/membrane-shadow && cargo build --release --bin membrane
cp target/release/membrane ~/.local/bin/
```

Push to `forgejo` only.

---

## Wave 65 Preview

- DNS cutover execution: once eastGate points NS records, validate HTTPS on golgiBody-ext via Caddy Let's Encrypt
- Foundation ingestion pipeline: wire `foundation` CLI to ingest pseudoSpores from lithoSpore registry into gallery
- WAN covalent deployment: full gate bootstrap, NUCLEUS Nest Atomic, temporal sync over TURN — glacial criterion #4

## Wave 66 Target

- sporePrint fully sovereign: lab.primals.eco on golgiBody-ext, HTTPS, gallery live with 2+ pseudoSpores
- Context braid template system: `context.weave --template <name>` for recurring patterns

---

*flockGate at Wave 64. WAN relay validated. Focus: gallery template + build pipeline + sustained relay measurement.*
