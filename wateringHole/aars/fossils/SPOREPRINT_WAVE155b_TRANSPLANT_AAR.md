# sporePrint AAR — Wave 155b Transplant

**Date**: 2026-07-27 | **Wave**: 155b | **Gate**: eastGate
**Scope**: sporePrint content alignment with ecosystem Wave 155b

---

## Mission

Update sporePrint to reflect the Wave 155b ecosystem state: tracks converged,
genomeBin cross-platform distribution, BTSP 13/13, autonomous enrollment (F10),
7 gates online + 5 HW ready, and updated primal test counts.

---

## Actions Taken

### 1. Entity registry (config.toml)

Updated 7 entities and totals:

| Entity | Old Tests | New Tests | Key Description Updates |
|--------|-----------|-----------|------------------------|
| bearDog | 13,973 | 11,993 | FIDO2 + beacon + HSM agnostic, BTSP 13/13, Chimera beardog-core |
| songBird | 14,332 | 10,335 | universal-ipc, mesh.gate_enroll, BTSP ClientHello |
| nestGate | 11,474 | 9,617 | BTSP ClientHello, cross-platform CAS (Windows/ZFS) |
| toadStool | 21,108 | 17,614 | (unchanged description) |
| petalTongue | 5,773 | 5,812 | WASM/WebGL shipped, BTSP ClientHello |
| cellMembrane | 1,043 | 1,043 | gate.bootstrap (genomeBin), nucleus.rs cross-platform, Platform::detect() |
| Tower Atomic | — | — | BTSP 13/13, autonomous enrollment (F10), genomeBin 5 targets, glacial goals |

**Totals**: primal_tests 82,124, spring_tests 11,576, total 93,700.

### 2. Content pages (10 files)

| File | Key Updates |
|------|------------|
| tower_atomic.md | Cross-platform IPC, BTSP 13/13, genomeBin target matrix, glacial goals G1/G2/G5, autonomous enrollment pipeline |
| living-systems.md | 7 online + 5 HW ready gate table with platforms |
| MESH_TOPOLOGY.md | Full 14-gate inventory, autonomous enrollment flow, physical topology |
| NUCLEUS_ARCHITECTURE.md | BTSP 13/13, genomeBin, glacial goals |
| CONTEXT.md | Wave 155b header, 10 fossilized dimensions, tracks converged |
| llms.txt | Updated metrics, gate counts, glacial goals |
| products/_index.md | Tower: 7 gates, BTSP 13/13, genomeBin |
| architecture/_index.md | Updated Tower/CI/Mesh descriptions |
| README.md | 313 pages |

---

## Metrics

| Metric | Before (151c) | After (155b) |
|--------|--------------|--------------|
| Total tests | 104,989 | 93,700 |
| Gates online | 7 | 7 (unchanged but list refined) |
| Gates HW ready | — | 5 (strandGate, westGate, blueGate, swiftGate, southGate) |
| BTSP coverage | "strict mode" | 13/13 |
| Fossilized dims | unspecified | 10 |
| genomeBin targets | unspecified | 5 |
| Glacial goals | — | G1-G9 documented |
| spore-validate | 0 errors | 0 errors |

---

## Divergences Found

### Test count gap

The blurb states `primal_tests = 75,199` total, but we only received
individual counts for 5 of 15 primals. The remaining 10 primals still
carry their Wave 151b counts in config.toml. Our actual entity sum
is 82,124 (not 75,199). A full `spore-validate refresh` from source
repos is needed to get accurate per-entity counts for all primals.

**Recommendation**: Run `spore-validate refresh` on eastGate against
all primal repos to get authoritative per-entity test counts matching
the blurb's 75,199 total.

### Missing content

- **rustChip**: Entity in registry but no content page tags it (spring hub page needed when content is ready)
- **genomeBin**: No dedicated page yet — concept is documented inline in tower_atomic.md and MESH_TOPOLOGY.md

### Zola warnings (pre-existing)

4 lab validation summaries missing weight frontmatter (biomeos, groundspring,
healthspring, airspring). Not blocking, generates Zola warnings.

---

## Upstream Tasks

| Task | Team | Priority |
|------|------|----------|
| Full `spore-validate refresh` from source repos | eastGate / sporePrint | P1 |
| rustChip spring hub page | rustChip | P3 |
| Weight frontmatter for 4 validation summaries | sporePrint | P3 |

---

*Wave 155b transplant: 10 files, 154 insertions, 106 deletions.
genomeBin, BTSP 13/13, autonomous enrollment, 12 gates (7+5).
Tracks converged. 0 errors.*
