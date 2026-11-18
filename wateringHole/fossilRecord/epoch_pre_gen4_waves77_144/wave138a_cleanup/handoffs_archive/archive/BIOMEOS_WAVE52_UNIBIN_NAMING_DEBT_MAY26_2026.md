# biomeOS — UniBin Naming Debt: `biomeos-cli` → `biomeos`

**From**: primalSpring (upstream pipeline)
**To**: biomeOS team
**Date**: May 26, 2026
**Wave**: 52
**Priority**: High — mountain debt, temporally first
**Status**: Requesting rename

---

## Problem

biomeOS ships its binary as `biomeos-cli` (Cargo workspace crate name) instead of `biomeos` (the primal name). This violates the UniBin naming standard:

> "Single binary named after primal (no `-server`, `-client` suffixes)"

The `-cli` suffix caused **three distinct pipeline failures** during Wave 51-52 plasmidBin harvest work:

| Failure | Root Cause | Fix Applied (workaround) |
|---------|-----------|--------------------------|
| `plasmidbin fetch` couldn't find biomeOS release asset | Asset name `biomeos-cli-x86_64-...` didn't match expected `biomeos-x86_64-...` | Added 4-pattern fallback in `fetch.rs` |
| `checksums.toml` orphan entry | Harvest wrote checksums under `biomeos-cli`, manifest uses `biomeos` | Changed harvest to key by source_id |
| Release upload skipped biomeOS | Rename step filtered `biomeos-cli` because it didn't match primal name `biomeos` | Added `binary_name` lookup from `sources.toml` |

Every pipeline layer — fetch, harvest, checksums, rename, upload — needed a workaround for this single naming mismatch. The workarounds are in place, but they add complexity that no other primal requires.

## Why This Matters

- **13 other primals** have `binary_name == source_id` — biomeOS is the only exception
- `sources.toml` needs a `binary_name` override and `build_args` override just for biomeOS
- Every future pipeline feature needs to account for the alias
- Unified naming means `plasmidbin fetch biomeos` just works — no fallback dance

## Requested Change

In the biomeOS workspace, rename the binary crate so the output binary is `biomeos`:

**Option A** (rename crate):
```
crates/biomeos-cli/  →  crates/biomeos/
Cargo.toml: name = "biomeos"
```

**Option B** (keep crate name, override binary):
```toml
# In crates/biomeos-cli/Cargo.toml
[[bin]]
name = "biomeos"
path = "src/main.rs"
```

Either option produces a binary named `biomeos`, which aligns with every other primal and eliminates all the pipeline aliasing.

## After Rename

Once biomeOS ships a release with the renamed binary, primalSpring will:

1. Update `sources.toml` — remove `binary_name` and `build_args` overrides
2. Clean up `checksums.toml` — single `biomeos` entry, no orphan
3. Remove fallback patterns from `fetch.rs` that exist only for this case

## ecoBin Status

biomeOS remains **TRUE ecoBin #5** — this is a naming issue, not a purity or portability issue. The binary is Pure Rust, musl-static, cross-compiles to all Tier 1 targets. Fixing the name makes it UniBin-compliant too.
