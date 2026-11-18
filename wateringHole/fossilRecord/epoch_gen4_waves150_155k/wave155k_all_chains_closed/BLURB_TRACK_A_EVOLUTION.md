# Track A: Evolution — Nest Atomic + bearDog Public

> **CONVERGED**: Tracks A and B merged into unified ECOSYSTEM_BLURB.md (Wave 155b).
> This file retained as reference for Nest Atomic + Chimera scope. See ECOSYSTEM_BLURB.md
> for current team assignments and glacial goals (G3, G5, G6).

**Wave**: 155b | **Owner**: eastGate overwatch + flockGate
**Converged with**: Track B (Fleet Convergence) — see ECOSYSTEM_BLURB.md

---

## GOAL

Continue the Wave 151 forward momentum. Evolve the primal composition towards
Nest Atomic, ship bearDog as a public crate, and begin Chimera Phase 0 extraction.
This track is about capability evolution, not fleet operations.

---

## P0 — Nest Atomic Phase 0

The BTSP ClientHello sub-wave (151d) unblocked Nest Atomic. nestGate and
petalTongue both have BTSP outbound, and songBird has full crypto delegation to bearDog.

| # | Task | Owner | Status |
|---|------|-------|--------|
| 1 | Wire `connect_with_btsp` into nestGate priority call sites | nestGate (flockGate) | READY |
| 2 | nestGate CAS integration testing | eastGate + flockGate | READY |
| 3 | Nest Atomic Phase 0 validation — primalSpring scenarios | primalSpring (eastGate) | BLOCKED on 1+2 |
| 4 | nestGate ↔ rhizoCrypt ↔ loamSpine provenance trio signal test | primalSpring | BLOCKED on 1 |

**Validation**: `benchScale` topology `topologies/nucleus/provenance_trio.yaml`
tests the NestGate → rhizoCrypt → loamSpine → sweetGrass signal path.

---

## P0 — bearDog Public Flip

bearDog is at 9/10 readiness for public. Remaining item is a final audit sweep.

| # | Task | Owner | Status |
|---|------|-------|--------|
| 1 | Final security audit sweep (pen test 3 CRITICALs already closed) | bearDog (flockGate) | DONE |
| 2 | Production mock elimination | bearDog (flockGate) | DONE |
| 3 | FIDO2 + iosGate + HSM agnostic | bearDog (flockGate) | DONE |
| 4 | FIDO2 enrollment attestation + beacon proximity proof | bearDog (eastGate) | DONE (Wave 155a) |
| 5 | Flip bearDog repo to public on GitHub + Forgejo | eastGate overwatch | **READY** |

**Dependency**: GitHub SSH key must be registered on eastGate to push public
flip (currently blocked — Forgejo is sovereign, GitHub is mirror).

---

## P1 — Chimera Phase 0

Crypto delegation 6/6 COMPLETE unblocked the shared library extraction.
Tower Atomic proved the composition model. Next step: `libtower.so` extraction.

| # | Task | Owner | Status |
|---|------|-------|--------|
| 1 | Define Chimera boundary — which symbols cross from bearDog + songBird + skunkBat | eastGate | DESIGN |
| 2 | Extract `libtower.so` crate with C FFI | eastGate | BLOCKED on 1 |
| 3 | Tower cutover shadow analysis — shadow data from 3 gates (700+ samples) | eastGate | DATA AVAILABLE |

---

## P1 — Tower Cutover Shadow

Shadow is active on 3 gates with 700+ samples. The 353x LAN / 1.7x WAN
performance data supports cutover, but the chimera extraction must land first
to provide the shared library boundary for non-Rust consumers.

---

## P2 — Publication Pipeline

| # | Task | Owner | Status |
|---|------|-------|--------|
| 1 | crates.io publishing (sovereignty sub-goal, not immediate) | eastGate | DESIGN |
| 2 | JOSS paper — Gonzales NF live system | projectFoundation | STRATEGY DONE |
| 3 | CTF NDU grant alignment | projectFoundation | GLACIAL |
| 4 | sporePrint primal pipeline (replace Zola) | eastGate | DESIGN |

---

## VALIDATION MATRIX

| Test | Topology | What It Proves |
|------|----------|----------------|
| Provenance trio | `nucleus/provenance_trio.yaml` | NestGate → rhizoCrypt → loamSpine signal |
| Tower membrane | `nucleus/tower_membrane.yaml` | bearDog + songBird + skunkBat composition |
| K-Derm layers | `nucleus/kderm_diderm_membrane.yaml` | Membrane model intact |
| Full NUCLEUS | `nucleus/full_nucleus.yaml` | 13 separate containers, 427+ methods |
| Signal graph | `nucleus/ferment_lifecycle.yaml` | Ferment lifecycle signals |

---

*Track A focuses on capability evolution. Track B (fleet convergence) handles
getting the hardware online and testing the postPrimordial deployment system.*
