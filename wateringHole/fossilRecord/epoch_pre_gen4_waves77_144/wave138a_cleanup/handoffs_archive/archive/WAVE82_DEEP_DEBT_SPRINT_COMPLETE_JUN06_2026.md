# Wave 82: Deep Debt Evolution Sprint — Complete

**Date**: 2026-06-06
**Author**: eastGate overwatch
**Sprint**: primalSpring Deep Debt Evolution (16 tasks, all complete)
**Test count**: 929 (up from 893)

---

## Sprint Results

All 16 tasks from the Deep Debt Evolution Sprint are complete. primalSpring
is now fully TOML-driven, type-safe, and shell-free for all core business
logic.

| Track | Tasks | Status |
|-------|-------|--------|
| 1. Type-safe dispatch | t1a, t1b, t1c, t1d | COMPLETE |
| 2. Shell absorption | t2a, t2b | COMPLETE |
| 3. TOML-driven config | t3a, t3b, t3c, t3d | COMPLETE |
| 4. Code quality | t4a, t4b, t4c | COMPLETE |
| 5. Pipeline & coverage | t5a, t5b, t5c | COMPLETE |

### Key deliverables

- **Zero string dispatch** — all method routing derived from `capability_registry.toml`
- **Zero hardcoded metadata** — ports, bind flags, VPS IPs, env keys all from TOML
- **Real health checks** — `health.drain` (AtomicU64 in-flight) and `health.readiness` (capability discovery)
- **Shell scripts deprecated** — `nucleus_composition_lib.sh` and `nucleus_crypto_bootstrap.sh` have comprehensive Rust replacement guides
- **Pure-Rust crypto bootstrap** — `certification/crypto_bootstrap.rs` provides three-tier HMAC-SHA256 key derivation
- **36 new tests** — env_keys, validation helpers, neural dispatch metrics, crypto bootstrap
- **Deploy pipeline hardened** — multi-binary workspace overrides, Rust self-refresh module with BLAKE3 verification
- **ureq pinned** — `=3.3.0`, `ring` wrapper-allowed in deny.toml for cross-membrane only

---

## plasmidBin Ownership Model

Formalized ownership for long-term binary distribution:

### cellMembrane team — owns binary distribution *evolution*

plasmidBin is a membrane artifact. cellMembrane owns:

- **plasmidBin CLI evolution** — `harvest`, `sync`, `fetch`, `verify`, `validate` subcommands
- **VPS deployment scripts** — `deploy_membrane.sh`, self-refresh orchestration
- **Source priority logic** — GitHub ↔ Forgejo ↔ VPS binary routing
- **Provenance chain** — checksums.toml, manifest.toml, BLAKE3 verification
- **Forgejo release publishing** — inner membrane binary distribution
- **GitHub release mirroring** — outer membrane binary distribution

### projectNUCLEUS — owns deployment *consumption* (long-term)

NUCLEUS consumes plasmidBin binaries to compose atomics:

- **nucleus_launcher** — which binaries to start, startup ordering, health sweep
- **CompositionContext** — capability requirements, liveness validation
- **Deploy graphs** — TOML compositions defining what gets deployed
- **Gate-level automation** — self-refresh *policy* (when to refresh, rollback)
- **Composition health** — verifying deployed NUCLEUS is healthy

### primalSpring — retains the *library surface*

primalSpring keeps the shared infrastructure but doesn't own execution:

- `deploy/self_refresh.rs` — Rust library for binary fetching (used by consumers)
- `config/capability_registry.toml` — canonical capability routing
- Deploy graph definitions and structural validation
- Certification and validation frameworks

### Handoff chain

```
primalSpring (evolution team)
  → defines capability requirements, deploy graphs, validation
  → hands off binary distribution concerns to ↓

cellMembrane (membrane team)
  → owns plasmidBin CLI evolution
  → owns VPS deployment scripts and self-refresh
  → owns source priority (GitHub ↔ Forgejo ↔ VPS)
  → owns provenance chain (checksums, manifest, BLAKE3)
  → hands off runtime deployment orchestration to ↓

projectNUCLEUS (long-term deployment owner)
  → owns nucleus_launcher, startup sequencing
  → owns composition validation
  → owns gate-level deployment automation
  → consumes plasmidBin as a dependency
```

---

## Remaining Work (primalSpring-specific)

| Item | Priority | Owner | Notes |
|------|----------|-------|-------|
| toadStool `--headless` regression | P0 | toadStool team | Blocks 13/13 ALIVE → mesh.init |
| Songbird test coverage (73% → 90%) | P2 | Songbird team | Coverage sprint, not blocking mesh |
| 3 springs missing `domain_profile.toml` | P2 | spring owners | hotSpring, ludoSpring, neuralSpring |
| `deploy_membrane.sh refresh` validation | P1 | cellMembrane | Full pipeline proof on VPS |

### What primalSpring does NOT need to do

- plasmidBin CLI changes → cellMembrane
- VPS binary management → cellMembrane
- Gate deployment automation → projectNUCLEUS
- Individual primal fixes → respective primal teams

---

## For the Record

929 tests. Zero clippy warnings. Zero C deps (default build). All 16 deep
debt tasks delivered. Shell scripts deprecated with comprehensive Rust
replacement guides. The codebase is now HPC mesh-ready.

---

## tideGlass Seeded (Post-Stadial Bloom Target)

[protoKarya/tideGlass](https://github.com/protoKarya/tideGlass) — first
gen5-native product. GPS sovereign rebuild (Bin Chen Lab, Cell 2026) for
NF drug repurposing. Assigned by Andrea Gonzales.

**Why this matters for deployment**: tideGlass is the first consumer that
will exercise the full NUCLEUS composition stack for external science
production. The Python validation phase (Phases 0-2) needs:

- **nestGate** — content-addressed data fetch (LINCS L1000, ChEMBL, ZINC)
- **provenance trio** — data braid chains for sovereign compute validation
- **barraCuda** — 3 WGSL shaders (RGES batch scoring, MCTS rollout, fingerprints)
- **toadStool** — GPU streaming for RCL training

This is why the deployment pipeline matters NOW — when Phase 3 (Rust
rebuild) starts, the primals must be NUCLEUS-composable. The deep debt
sprint cleaned primalSpring's side. cellMembrane and projectNUCLEUS
own the deployment path that makes this possible.

**Timeline**: Post-stadial bloom. Phase 0 (archaeology) begins now.
Full NUCLEUS lithoSpore (Phase 4) is a 12+ week horizon.

---

## ecoPrimals Workspace Dewired (NestGate Legacy Cleanup)

`/home/eastgate/Development/ecoPrimals/` was historically a NestGate clone
(NestGate was the first ecoPrimal). Over time the workspace grew to hold
all primals, springs, gardens, and infra as gitignored sibling directories.
This created:

1. **Submodule coupling** — `infra/wateringHole` was tracked as a NestGate
   submodule. Every wateringHole update required syncing with NestGate upstream.
2. **Push conflicts** — NestGate upstream (ironGate team) evolved independently.
   Pushing the submodule pointer caused rebase conflicts with ZFS restructuring.
3. **Identity confusion** — directory named `ecoPrimals/` but git identity was
   `ecoPrimals/nestGate.git`.

**Resolution (Wave 82)**:
- Root `.git` removed (backed to `/tmp/nestgate_root_git_backup_20260606`)
- Root NestGate source files removed (duplicates of `primals/nestGate/`)
- `infra/wateringHole` is now a plain independent clone (always was, just
  also had a submodule pointer in the root git)
- `primals/nestGate/` is the canonical NestGate clone (session 95b, ahead)
- All 39 ecosystem repos verified with correct independent remotes

**Manual cleanup needed**:
- `sudo rm -rf /home/eastgate/Development/ecoPrimals/wetSpring` — root-owned
  empty directory (orphan, real wetSpring is at `springs/wetSpring/`)
- `/tmp/nestgate_root_git_backup_20260606/` can be deleted after verification

**Impact on ironGate team**: NestGate no longer needs wateringHole as a
submodule. If their repo still references it, they should remove the
`.gitmodules` entry and the `infra/wateringHole` submodule tracking.

*"Sixteen tasks. Nine hundred twenty-nine tests. Zero string dispatch. The mountain is clean. The first lens is being ground. And the fossil wire is cut."*
