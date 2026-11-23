# projectNUCLEUS — Atomic Deployment Phase Absorption

**Date**: May 13, 2026
**From**: projectNUCLEUS + lithoSpore/Foundation teams
**Context**: Downstream response to primalSpring L2 Atomic Deployment Directive

---

## Summary

Absorbed the May 13 Atomic Deployment Phase audit from primalSpring. The directive
confirmed 13/13 primals at zero code debt, 8/8 delta springs at zero debt (8,486+ tests),
Tower atomic LIVE, Nest ready, Node in progress. projectNUCLEUS was identified as the
critical path to stadial entry (Pillar 2 shadow runs).

**Resolved in this pass**:

### projectNUCLEUS (17 files changed, 405 insertions)

1. **`composition.deploy.shadow` WIRED**: `shadow_deploy()` in `deploy_graph.sh` —
   dry-run graph validation (binary existence, port conflict detection, dependency
   ordering, toadstool.validate pre-flight on all workloads when toadStool is reachable)

2. **toadstool.validate Tier 2 WIRED**: 12 validation workload TOMLs across all 7
   springs now carry `[output] schema = "toadstool-validate-v1"` + `--format json`:
   - airspring: full-suite, et0-validation
   - groundspring: geochemistry-validation
   - healthspring: pk-validation, biosignal-validation
   - hotspring: ltee-anderson, md-validation
   - neuralspring: ltee-b1-mutation, ml-validation
   - wetspring: ltee-b7-mutation-accumulation, diversity-rust-validation, 16s-rust-validation

3. **DoT parity scenario CREATED**: `dot_sovereign_parity.sh` — DNS-over-TLS vs
   sovereign resolver timing/accuracy comparison (H2-4/H2-17→20). Integrated into
   `shadow_run_orchestrator.sh` as the 4th parity test.

4. **Wire notes absorbed**: bearDog base64 signing param, skunkBat `security.audit_log`
   (not `defense.audit`), NestGate `content.*` vs `storage.*` domain separation, BTSP
   auth pipeline (13/13 primals Ed25519), `composition.deploy.shadow` (biomeOS v3.53).

5. **EVOLUTION_GAPS.md updated**: River delta Push 3 absorbed, interstadial exit score
   advanced (████████░░), 3 new absorption targets closed.

### lithoSpore (9 files changed, 450 insertions)

1. **Modules 3+4 promoted from scaffold**: groundSpring V140 B3 (Good 2017 clonal
   interference) and B4 (Blount 2008/2012 citrate innovation) ingested. Rust crates
   evolved from SKIP scaffold to live validation with real checks.

2. **3 fetch scripts created**: `fetch_good_2017.sh`, `fetch_blount_2012.sh`,
   `fetch_tenaillon_2016.sh` — all with BLAKE3 provenance, gate-agnostic paths.

3. **Module count**: 6/7 live at Tier 2 (modules 1-4, 6-7). Only module 5 (biobricks)
   remains scaffold (DOI pending). ltee-cli dispatches 6 live modules.

### Foundation (4 files changed)

1. **expressions/README.md**: Added threads 9 (Gaming/Creative) and 10 (Provenance/Economics)
   to the active expression table. Fixed thread 6 label (shares MEASUREMENT_SCIENCE.md with 7).

2. **Source TOML consistency**: Set `meta.expression` in `thread09_gaming.toml` and
   `thread10_provenance.toml` (were empty strings).

3. **BioProject reconciliation**: Added PRJNA294072 to `thread05_ltee.toml` Tenaillon entry
   alongside SRP064605 for cross-reference consistency.

### plasmidBin (1 file changed)

1. **Manifest v5.3.0**: barraCuda 0.3.12→0.4.0 (precision.route, 649 tests), primalSpring
   0.9.17→0.9.25 (689 tests, 413-method registry), skunkBat added to tower atomic (Phase 32).

---

## Remaining Critical Path (ops)

| Item | Status | Owner |
|------|--------|-------|
| BearDog TLS shadow run (H2-12) | Scripts staged, needs 7-day execution | ops |
| Songbird NAT VPS relay (H2-14) | Deploy script ready, needs VPS provisioning | ops |
| DoT sovereign DNS (H2-17→20) | Baseline script ready, needs knot-dns on VPS | ops |
| BTSP auth shadow run (H2-01→04) | Ready to build authenticator plugin | dev |
| skunkBat audit forwarding (H3-08) | `security.audit_log` path documented | dev |

---

## Repos Pushed

- `sporeGarden/projectNUCLEUS` → main
- `sporeGarden/lithoSpore` → main
- `sporeGarden/projectFOUNDATION` → main
- `ecoPrimals/plasmidBin` → main
