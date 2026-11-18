<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->

# lithoSpore / pseudoSpore — Pack/Unpack Delivery

**Date**: Jul 17, 2026 11:40 EDT | **Wave**: 147e | **From**: pseudoSpore/lithoSpore on ironGate

---

## Summary

pseudoSpore pack/unpack pipeline shipped. lithoSpore now at **219 tests**
(was 216). Two new CLI subcommands, hardened envelope validation, initioChem
domain profile created. Round-trip integration test passes.

---

## Blurb Status Update (for overwatch)

```
### lithoSpore → CLI tool

| Step | Status | Owner |
|------|--------|-------|
| 1. Silicon Atheism Platform trait | **COMPLETE** (219 tests) | lithoSpore |
| 2. `pseudospore pack` command | **SHIPPED** | lithoSpore |
| 3. `pseudospore unpack` command | **SHIPPED** | lithoSpore |
| 4. initioChem as first consumer | IN PROGRESS (profile created) | initioChem |
| 5. USB round-trip validation | NOT STARTED | lithoSpore + primalSpring |
```

Test health row: `lithoSpore | 219 | 0 | forbidden | 0`

---

## What Shipped

| Item | Detail |
|------|--------|
| `litho pack-pseudospore <dir>` | Directory → `.tar.gz` with present/external split. Excludes large data. |
| `litho unpack-pseudospore <tarball> [--validate]` | `.tar.gz` → directory with optional envelope validation. |
| `create_tarball()` + `extract_tarball()` | `pseudospore-core::tarball` — BLAKE3 hash returned. |
| `write_integrity_manifest()` | Generates `[present]`/`[external]` BLAKE3 manifest. |
| Hardened `PseudoSporeEnvelope::validate()` | Spec VALID tier enforced (items 1-6): type, validation.json, env receipt, checksums verified, ferment transcript, README. |
| `profiles/initiochem-general.toml` | GROMACS / PLUMED / CP2K / ORCA / OpenMM. |
| Round-trip integration test | pack → unpack → load → validate cycle. |

**23 subcommands** (was 21). **219 tests** (was 216). 0 clippy, 0 fmt, 0 doc warnings.

---

## Pipeline (complete)

```
emit-pseudospore → pack-pseudospore → [distribute] → unpack-pseudospore --validate → ingest-pseudospore
```

Ready for initioChem as first external consumer.

---

## initioChem Consumer (SHIPPED)

initioChem is now the **first external pseudoSpore consumer**:
- Added `pseudospore-core` as git dependency from lithoSpore
- 5 CLI subcommands: `status`, `capabilities`, `view`, `validate`, `unpack`
- `view` and `validate` use `PseudoSporeEnvelope` API with spec VALID tier checks
- `unpack` extracts `.tar.gz` tarballs and validates in one step
- 2 tests (envelope load + pack/unpack round-trip), 0 clippy, 0 fmt, 0 doc
- Pushed to `origin main` (`328bc9a`)

Pipeline proven end-to-end:
```
lithoSpore emit → pack → [distribute] → initioChem unpack → validate → view
```

## Blurb Status Update (revised)

```
### lithoSpore → CLI tool

| Step | Status | Owner |
|------|--------|-------|
| 1. Silicon Atheism Platform trait | **COMPLETE** (219 tests) | lithoSpore |
| 2. `pseudospore pack` command | **SHIPPED** | lithoSpore |
| 3. `pseudospore unpack` command | **SHIPPED** | lithoSpore |
| 4. initioChem as first consumer | **SHIPPED** (2 tests) | initioChem |
| 5. USB round-trip validation | NOT STARTED | lithoSpore + primalSpring |
```

## Next Steps

1. USB round-trip validation — primalSpring scenario for pack → USB → unpack → validate cycle
2. Upstream: no blocking needs from lithoSpore on any primal team
