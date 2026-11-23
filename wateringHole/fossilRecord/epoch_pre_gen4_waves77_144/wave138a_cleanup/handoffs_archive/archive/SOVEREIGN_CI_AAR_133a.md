# Sovereign CI — After Action Review (Wave 133a)

**Gate:** sporeGate | **Date:** 2026-07-06 | **Posture:** LAN+WAN MESHED

## Result

**30/30 ecobins** built, checksummed, and published to pepti warehouse.

- **15/15 x86_64-unknown-linux-musl** (153MB total)
- **15/15 aarch64-unknown-linux-musl** (130MB total)
- `checksums.toml` with SHA-256 for all 30 binaries
- Live at `membrane.primals.eco/depot/{triple}/{binary}`

## Build Failures Encountered (all resolved)

| ID | Primal | Target | Root Cause | Fix Applied |
|----|--------|--------|------------|-------------|
| 1 | biomeOS | both | `--bin biomeos` fails; binary is in non-default package `biomeos-unibin` | Added `--package biomeos-unibin` |
| 2 | skunkBat | both | `--bin skunkbat` fails; binary is in non-default package `skunk-bat-server` | Added `--package skunk-bat-server` |
| 3 | nestGate | aarch64-musl | Project `.cargo/config.toml` requires `ld.lld` linker (not installed) | `apt install lld` on build host |

## Divergences for Upstream Code Teams

### P1 — Breaks cascade pipeline

**CI-DIV-07: temporal.cascade does not commit freshness updates**
- `membrane temporal.cascade` syncs all 17 repos (git pull/push) but does NOT update `[meta].updated` timestamp in `heads/golgi.toml`, and does NOT commit the refreshed file
- Freshness publishing is silently broken — `heads/golgi.toml` was stuck at 2026-07-04 despite repos being current
- **Fix:** Audit `publish_freshness()` in cellMembrane temporal module. After sync, must: (1) re-read HEADs from cloned repos, (2) bump timestamp, (3) `git add` + `commit` + `push` the heads file

### P2 — Breaks CI without manual workarounds

**CI-DIV-01: biomeOS requires --package biomeos-unibin**
- Main binary 'biomeos' is in package 'biomeos-unibin', not in workspace default-members
- `cargo build --bin biomeos` fails without explicit `--package` flag
- **Fix:** Add `biomeos-unibin` to `default-members` in workspace `Cargo.toml`

**CI-DIV-02: skunkBat requires --package skunk-bat-server**
- Main binary 'skunkbat' is in package 'skunk-bat-server', not in workspace default-members
- **Fix:** Add `skunk-bat-server` to `default-members`

**CI-DIV-03: nestGate requires ld.lld (project config diverges from ecosystem)**
- nestGate's `.cargo/config.toml` specifies `linker = "ld.lld"` for aarch64-musl with `link-self-contained=yes`
- All 12 other primals use `aarch64-linux-gnu-gcc` (from global config)
- **Fix:** Converge on single linker strategy ecosystem-wide

**CI-DIV-08: ecosystem_manifest.toml has no type schema validation**
- eastGate pushed `adb_ports` as inline table `{ beardog = 9100, ... }` but membrane parser expects `u16[]`
- Broke `temporal.cascade` on golgi until manually fixed (two attempts)
- **Fix:** Pre-commit hook or CI check to validate manifest against membrane's expected schema

### P3 — Technical debt / convergence opportunities

**CI-DIV-04: 13/14 primals have project-level .cargo/config.toml**
- Config sizes range from 8 lines (rhizoCrypt) to 135 lines (nestGate)
- Creates a matrix of linker/rustflags combinations that CI must navigate
- **Fix:** Standardize a shared template; primals inherit unless they have documented platform needs

**CI-DIV-05: Rust toolchain pinning is inconsistent**
- bearDog: 1.93.0 | songBird: 1.94.0 | nestGate/rhizoCrypt: 1.94.1 | 5 primals: "stable" | 5 primals: no toolchain file
- **Fix:** Single `rust-toolchain.toml` strategy at ecosystem level

**CI-DIV-06: sweetGrass aarch64 binary is larger than x86**
- aarch64-musl: 13.7MB vs x86-musl: 13.6MB (101% ratio)
- All other primals are 75-91% of x86 size on aarch64
- **Fix:** Investigate conditional compilation (`cfg(target_arch)`) in sweetGrass deps

## Golgi VPS Recovery

- Disk was 100% full after `temporal.cascade --clone-missing` cloned 9 repos to a 10GB VPS
- Reclaimed 2.7GB:
  - Converted full clones → shallow (`--depth 1`)
  - Removed legacy `plasmidBin/` (228MB) and `genomeBin/` (108MB)
  - Vacuumed journals (152MB), cleared apt cache (79MB)
- Result: 6.9G / 9.7G (75% usage)
- **Recommendation:** golgi should never hold full source clones. HEAD tracking can use Forgejo API or shallow clones only.

## Convergence Convention (Proposed)

For any primal to be CI-buildable with zero manual intervention:

1. **Binary discoverable from workspace root:** `cargo build --release --target $TRIPLE --bin $PRIMAL_LOWERCASE`
2. **No special linker requirements** beyond what the global `.cargo/config.toml` provides
3. **Toolchain declared** in `rust-toolchain.toml` (can be "stable" — just be explicit)
4. **Binary name = primal name lowercase** with no separators (e.g., `songBird` → `songbird`)

Currently 11/14 primals meet this convention. 3 require workarounds.

## Binary Size Reference

| Binary | x86_64-musl | aarch64-musl | arm/x86 ratio |
|--------|-------------|--------------|---------------|
| petaltongue | 28M | 25M | 90% |
| songbird | 23M | 20M | 90% |
| biomeos | 20M | 18M | 92% |
| sweetgrass | 13M | 14M | 101% |
| toadstool | 13M | 9.7M | 75% |
| beardog | 11M | 8.8M | 80% |
| nestgate | 8.1M | 7.0M | 87% |
| coralreef | 7.7M | 6.8M | 84% |
| rhizocrypt | 7.5M | 6.1M | 81% |
| barracuda | 5.4M | 4.3M | 79% |
| loamspine | 4.5M | 3.8M | 85% |
| squirrel | 4.3M | 3.4M | 78% |
| nucleus_launcher | 4.2M | 3.4M | 81% |
| sourdough | 3.0M | 2.6M | 83% |
| skunkbat | 2.8M | 2.4M | 85% |
| **TOTAL** | **153M** | **130M** | **85%** |
