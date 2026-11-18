# CATHEDRAL USB Pipeline VM Validation — May 14, 2026

**From**: CATHEDRAL (lithoSpore + Foundation)
**To**: primalSpring / upstream teams
**Date**: May 14, 2026
**Scope**: lithoSpore USB pipeline hardening, VM validation via benchScale + agentReagents

---

## Summary

The lithoSpore USB pipeline has been hardened and validated end-to-end on a
fresh VM. Six of seven LTEE modules pass at Tier 2 with 51/51 checks green.
The benchScale CLI has been wired for libvirt backend support, and
agentReagents has a new lithoSpore validation template.

## What Changed

### lithoSpore (sporeGarden/lithoSpore)

**USB pipeline fixes:**

1. **Binary path resolution** — `litho` CLI now checks `bin/` (USB layout) before
   `target/release/` (dev layout) via `resolve_binary()`.
2. **liveSpore.json path** — Detects USB layout via `.biomeos-spore` marker file.
   Writes to root-level `liveSpore.json` on USB, `artifact/liveSpore.json` in dev.
3. **Expected values staging** — `assemble-usb.sh` step 8 copies `validation/expected/*.json`
   to USB. Was missing entirely.
4. **Data fetching** — Modules 3 (Good 2017) and 4 (Blount 2012) fetched from
   groundSpring V140 control data via `$ECOPRIMALS_ROOT`. All 6 data bundles staged.

**Files modified:**
- `crates/ltee-cli/src/main.rs` — `resolve_binary()`, `resolve_livespore()`, idiomatic `if let`
- `scripts/assemble-usb.sh` — Step 8 (expected values), updated dry-run tree, renumbered to 10 steps

**Validation result (VM):**
- 6/7 modules PASS: fitness (8/8), mutations (7/7), alleles (17/17), citrate (6/6), breseq (8/8), anderson (5/5)
- Module 5 (biobricks) SKIP — upstream DOI pending
- liveSpore.json records different `hostname_hash` from VM, proving geo-delocalization

### benchScale (syntheticChemistry/benchScale)

**CLI wired for libvirt:**
- `--backend libvirt` (or `kvm`) now constructs `LibvirtBackend` instead of always using Docker
- `destroy` auto-detects backend from registry metadata
- Extracted `register_and_report()` helper
- Compiled `--features libvirt` confirmed on ironGate

**Dependency fix:**
- `russh` bumped 0.58 → 0.60, `russh-keys` 0.48 → 0.49 (fixed `rsa` 0.10.0-rc.12 build error)

**Files modified:**
- `Cargo.toml` — russh version bump
- `src/bin/main.rs` — backend dispatch, `register_and_report()`

### agentReagents (syntheticChemistry/agentReagents)

**New template:**
- `templates/lithoSpore-validation.yaml` — minimal Ubuntu 24.04 VM for GuideStone testing
  - 2GB RAM, 2 vCPU, 10GB disk
  - SSH + curl only (validates musl-static binaries need zero dependencies)
  - Validates with `agent-reagents validate`

**Build fix:**
- Regenerated `Cargo.lock` to resolve `der` version conflict from benchScale russh bump

**Files modified:**
- `templates/lithoSpore-validation.yaml` (new)
- `Cargo.lock` (regenerated)
- `README.md` — added lithoSpore-validation to gate templates table

### infra/wateringHole

**This handoff document.**

## Infrastructure Installed on ironGate

- libvirt 8.0.0 + QEMU 6.2.0
- Default virbr0 network (192.168.122.0/24)
- irongate added to `libvirt` + `kvm` groups
- Ubuntu 24.04 cloud image cached at `agentReagents/images/cloud/`

## Debt Audit Results

All three repos scanned for stale TODOs, dead code, debris:
- **lithoSpore**: Clean. No TODOs in Rust code. Python notebook TODOs are valid backlog.
- **benchScale**: Clean. `archive/` contains Dec 2025 docs (fossil record). No active debt.
- **agentReagents**: Clean. `scripts/legacy/` documented as intentional history.

## For Upstream Review

### primalSpring
- All 3 repos ready for audit
- benchScale CLI now supports `--backend libvirt` — primalSpring validation can target real VMs
- lithoSpore USB pipeline produces a self-sufficient artifact that validates on clean systems

### Upstream Primals
- Songbird TURN client library still needed for geo-delocalized Tier 2
- genomeBin packaging for Tier 3 on USB still upstream-blocked
- BearDog FIDO2/CTAP2 for SoloKey witness in `liveSpore.json` still queued

### Evolution Targets (benchScale + agentReagents)
CATHEDRAL now owns these repos. Priority Rust evolution targets:
- `benchScale/scripts/deploy-ecoprimals.sh` → Rust CLI subcommand
- `agentReagents/scripts/` download/setup family → `agent-reagents` subcommands
- Embedded Python in GPU reagent YAMLs → shared Rust or isolated `.py` modules
