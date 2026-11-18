# lithoSpore Deployment Evolution Handoff — May 18, 2026

**From**: lithoSpore (sporeGarden)
**To**: primalSpring, biomeOS, all spring teams
**Subject**: First live guideStone deployment — patterns for absorption

---

## What Happened

lithoSpore was deployed to 4 USB drives and handed to external scientists
at MSU's Barrick Lab (LTEE, 82,500+ generations). First time a guideStone
artifact crossed institutional boundaries carrying live science.

**Metrics**: 73 science checks, 7 modules, <100ms, 6.3MB musl-static binary,
exFAT cross-platform, 3-zone structure, 10+ validated liveSpore.json entries.

---

## Lessons for Primal Teams

### 1. biomeOS / neuralAPI: Atomic Instantiation Works

The lithoSpore artifact IS an atomic instantiation of the three-tier
pipeline. `bash validate` runs Tier 2 (Rust), attempts Tier 3 (primal
JSON-RPC), and degrades gracefully. The deployment matrix cell
`lithospore-x86-usb-standalone` validated on 4+ machines.

**Request**: When biomeOS supports signal dispatch routing, the Tier 3
composition graph (`graphs/ltee_guidestone.toml`) should collapse to
a single `nest.store` dispatch. The graph is annotated for this transition.

### 2. primalSpring: Deploy Graph Evolution

lithoSpore's deploy graph uses `by_capability` resolution (not primal
names). This works. The pattern should be standardized:

```toml
[[graph.nodes]]
name = "rhizocrypt"
by_capability = "dag"
```

**Request**: Confirm this is the canonical deploy graph pattern for gen4
products that compose primals. lithoSpore, esotericWebb, and future
gardens should use identical graph syntax.

### 3. Provenance Trio: Partial Completion Is Production-Ready

lithoSpore records provenance at whatever depth is available:
- No primals → liveSpore.json only (Tier 2)
- rhizoCrypt available → DAG session created
- Full trio → DAG + spine + braid

The partial completion pattern (try each primal, succeed independently)
is mature and should be documented as ecosystem standard.

### 4. Discovery: Capability Strings Work in the Wild

On the USB, no primals exist. Discovery returns `standalone` immediately.
On a NUCLEUS gate, it would discover via env → UDS → TURN. The four-step
discovery chain (`discovery.rs`) never panics, never blocks, and records
its path in `liveSpore.json`.

**Request**: Confirm discovery priority order and add to primalSpring
standards if not already canonical.

---

## Lessons for Spring Teams

### 5. wetSpring: Braid Handoff Works, Accession Normalization Needed

The sovereign braid (`barrick_2009_sovereign.json`) has real BLAKE3
hashes from 3 hours of GPU computation. lithoSpore validates the braid
metadata. One issue: braid uses `SRP001569` (SRA study), lithoSpore
expects `PRJNA29543` (BioProject). Both are correct references to the
same data.

**Request**: Normalize to BioProject accession in braids (it's the
stable identifier). Or lithoSpore can accept both — needs upstream
decision.

### 6. All Springs: Ferment Transcript Pattern Is Proven

The pattern works in production:
1. Spring computes (wetSpring: 3hr GPU sovereign pipeline)
2. Spring records braid (BLAKE3, wall time, tool version)
3. lithoSpore ingests braid into `provenance/braids/`
4. lithoSpore validates braid metadata against `data.toml`
5. Result appears in `liveSpore.json`

**Standard**: Every spring should produce braids for any computation
whose results feed into a guideStone. The contract is documented in
`LITHOSPORE_FERMENT_TRANSCRIPT_BRAID_HANDOFF_MAY17_2026.md`.

---

## Patterns for NUCLEUS Composition

### 7. The Seed Model

A guideStone USB is a complete NUCLEUS composition in dormant form:
- Validate (Tier 2): proves itself without primals
- Grow (Tier 3): bootstraps full environment with primals
- Four germination paths: source, container, VM, network clone

This is the `projectNUCLEUS` "atomic unit" pattern: the smallest
possible composition that can prove itself and grow into a full system.

### 8. Cross-Platform Shim as Deployment Primitive

The exFAT shim (copy to tmpdir → chmod → execute) should be a standard
pattern in `litho assemble`. Any guideStone that targets USB deployment
needs this automatically. The chassis should generate platform launchers
during assembly.

### 9. MANIFEST.toml as Discovery Substrate

`MANIFEST.toml` at artifact root describes every path and module. AI
agents (Cursor, copilot, future automation) can navigate the artifact
from this single file. This should be a required output of `litho assemble`.

---

## What lithoSpore Needs from Upstream (Updated)

| Need | From | Status |
|------|------|--------|
| Braid accession normalization | wetSpring | Active (SRP→PRJNA decision) |
| Signal dispatch routing | biomeOS | Queued (enables graph collapse) |
| Deploy graph canonicalization | primalSpring | Confirm `by_capability` pattern |
| Discovery priority documentation | primalSpring | Confirm env→UDS→TURN→standalone |
| Multi-node liveSpore federation | primalSpring | Future (merge protocol) |
| aarch64 musl target | sourDough | Future (Apple Silicon) |

---

## Current Test Counts

- lithoSpore: 125 tests, 73 science checks, 7 modules
- Upstream braids: 3 (barrick_2009_breseq, barrick_2009_sovereign, tenaillon_2016_wetspring_tier2)
- Deployment targets validated: ext4 (4 USBs), exFAT (1 USB), container, local

---

*The guideStone crossed the institutional boundary. The patterns are ready
for the next spore instance.*
