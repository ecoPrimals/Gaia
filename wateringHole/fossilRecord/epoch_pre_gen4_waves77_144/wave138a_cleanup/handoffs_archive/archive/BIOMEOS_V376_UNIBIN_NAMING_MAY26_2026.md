# biomeOS v3.76 — UniBin Naming: `biomeos-cli` → `biome`

**Date**: May 26, 2026
**Version**: v3.76
**From**: biomeOS
**Scope**: Wave 52 — binary naming alignment for plasmidBin pipeline

---

## Problem

The `biomeos-cli` crate produced a binary named `biomeos-cli`, which the
plasmidBin harvest pipeline misidentified as the main primal binary. This
caused 3 distinct pipeline failures (fetch pattern mismatch, checksums
orphan entry, release upload skip). primalSpring added workarounds but
every future pipeline feature needed to account for the alias.

biomeOS already ships its main binary as `biomeos` from the UniBin crate
(`crates/biomeos/`, package `biomeos-unibin`). The `biomeos-cli` binary
is a supplementary management CLI — not the primal binary.

## Fix

Renamed the CLI binary from `biomeos-cli` to `biome`:

| Change | Before | After |
|--------|--------|-------|
| `crates/biomeos-cli/Cargo.toml` `[[bin]]` name | `biomeos-cli` | `biome` |
| Clap `#[command(name)]` | `biomeos` | `biome` |
| `biomeos-spore` manifest `created_by` | `biomeos-cli v...` | `biomeos v...` |
| Crate name (Rust module) | `biomeos-cli` | `biomeos-cli` (unchanged) |
| UniBin binary (`crates/biomeos/`) | `biomeos` | `biomeos` (unchanged) |

## After This

primalSpring can:
1. Remove `binary_name` and `build_args` overrides from `sources.toml`
2. Clean `checksums.toml` — single `biomeos` entry, no orphan
3. Remove fallback patterns from `fetch.rs` that existed only for this case

## Binary Inventory

| Binary | Source | Purpose | Pipeline artifact? |
|--------|--------|---------|-------------------|
| `biomeos` | `crates/biomeos/` (UniBin) | Primal binary (nucleus, neural-api, deploy, etc.) | YES — the primal |
| `biome` | `crates/biomeos-cli/` | Management CLI helper (spore, chimera, health, etc.) | NO — local dev tool |
| `verify-lineage` | `crates/biomeos-cli/` | Lineage verification | NO — local dev tool |

## State

- **Tests**: 8,026 (0 failures)
- **Clippy**: 0 warnings
- **ecoBin**: TRUE ecoBin #5 — Pure Rust, musl-static, UniBin-compliant

---

*Wave 52. One primal, one binary name. The mountain is tightening.*
