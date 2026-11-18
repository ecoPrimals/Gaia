# graftGate Bootstrap AAR — Wave 157i POST-PANDEMIC CASCADE COMPLETE

**Date**: Aug 11, 2026 | **Wave**: 157i | **From**: graftGate
**Gate**: graftGate (M4 Mac Mini, Apple Silicon, `aarch64-apple-darwin`)
**Status**: **FULLY ENMESHED. 15/15 compiled. Depot PUSHED (5th OS family). iOS cross-compile LIVE. Xcode 26.6 installed.**

---

## Hardware

| Detail | Value |
|--------|-------|
| Model | Mac mini (Mac16,10) |
| Chip | Apple M4 — 10 cores (4P + 6E) |
| Memory | 16 GB |
| macOS | 26.6.1 (Build 25G76) |
| Architecture | `aarch64-apple-darwin` |

## Toolchain

| Tool | Version |
|------|---------|
| Homebrew | 6.0.16 |
| rustc | 1.97.1 (8bab26f4f 2026-07-14) |
| cargo | 1.97.1 (c980f4866 2026-06-30) |
| Xcode | 26.6 (Build 17F113) |
| iOS SDK | iPhoneOS26.5.sdk |
| WireGuard | wireguard-tools 1.0.20260223 + wireguard-go |

## Sync

- **42/42 repos cloned** — all repos including sporePrint (SSH auth active)
- SSH key: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMx/onlPYTQ5e9Yk+czqLOfGGMCMZ+/+ZIIcFFzRvl0s graftGate@primals.eco`
- Key **REGISTERED** in Forgejo — push access confirmed (all 4 orgs: Owner)
- HTTPS token also configured (fallback)

---

## `aarch64-apple-darwin` Binaries — 15/15 COMPILED

All 15 active primals now compile on Apple Silicon. 4 required local darwin fixes (documented below).

| Primal | Binary | Size | Darwin Fix? |
|--------|--------|------|-------------|
| bearDog | `beardog` | 6.3M | Yes — ios.rs import |
| songBird | `songbird` | 17M | Clean |
| skunkBat | `skunkbat` | 2.6M | Clean |
| nestGate | `nestgate` | 6.7M | Clean |
| rhizoCrypt | `rhizocrypt` | 5.8M | Clean |
| loamSpine | `loamspine` | 3.8M | Clean |
| sweetGrass | `sweetgrass` | 10M | Clean |
| toadStool | `toadstool` | 6.3M | Yes — cfg gate alignment |
| barraCuda | `validate_gpu` | 2.2M | Clean |
| coralReef | `coralreef` | 6.6M | Clean |
| biomeOS | `biomeos` | 16M | Clean |
| squirrel | `squirrel` | 2.8M | Yes — explicit `--target` |
| petalTongue | `petaltongue` | 13M | Yes — rustix API |
| swarmVine | `swarmvine` | 2.0M | Clean |
| sourDough | `sourdough` | 2.8M | Clean |

**Total darwin binary payload: ~98.1M across 15 primals. All Mach-O 64-bit arm64.**

---

## Darwin Fixes Applied — ALL 4 MERGED UPSTREAM

### 1. bearDog — `beardog-tunnel` ios.rs missing import (`24dd74d`)

**File**: `crates/beardog-tunnel/src/platform/ios.rs:57`
**Error**: `E0433 — use of unresolved module or unlinked crate 'env_keys'`
**Root cause**: `ios.rs` compiled on macOS via `#[cfg(any(target_os = "macos", target_os = "ios"))]`
but lacks its own import. Parent `mod.rs` has `use beardog_config::env_keys;` — child modules
need their own `use` statement.
**Fix**: Add `use beardog_config::env_keys;` to `ios.rs` imports.

### 2. toadStool — cfg gate mismatch (unix vs linux)

**File**: `crates/server/src/pure_jsonrpc/handler/router.rs:185`
**Error**: `E0599 — no method named 'silicon_registry_status' found`
**Root cause**: Call site uses `#[cfg(unix)]` (matches macOS) but the method lives inside
`#[cfg(target_os = "linux")] impl JsonRpcHandler` block (line 300). Outer gate wins — method
invisible on macOS.
**Fix**: Changed call site from `#[cfg(unix)]` to `#[cfg(target_os = "linux")]` to match impl block.

### 3. squirrel — `.cargo/config.toml` hardcodes musl target

**File**: `.cargo/config.toml`
**Error**: `ld: unknown options: --as-needed -Bstatic` (macOS ld rejects GNU ld flags)
**Root cause**: `[build] target = "x86_64-unknown-linux-musl"` is the default target.
macOS correctly has `[target.aarch64-apple-darwin]` section but it's never used because
the default build target is musl.
**Fix**: Build with explicit `--target aarch64-apple-darwin` flag. Long-term: remove
hardcoded default target or use platform-conditional config.

### 4. petalTongue — rustix 1.x Signal API change

**File**: `crates/petal-tongue-core/src/platform_substrate.rs:176-178`
**Error**: `E0599 — Signal::from_raw() and Signal::Hup not found`
**Root cause**: rustix 1.x moved `Signal::from_raw()` to `rustix-libc-wrappers` extension trait,
and renamed `Signal::Hup` to `Signal::HUP`. The code used `from_raw(0)` for process-existence
probe (signal 0), but `Signal` is `NonZeroI32` — signal 0 was never valid.
**Fix**: Replaced with `rustix::process::test_kill_process(pid)` — the purpose-built rustix API
for `kill(pid, 0)` process-existence probing. Pure Rust, no libc dependency.

---

## WireGuard — LIVE

- **Public key**: `ekHFlu0N6gdAFkk5lNLhgmWqGOptiTzmso8qWGx/yB4=`
- **Mesh IP**: `10.13.37.13/32`
- **Interface**: `utun2` (wireguard-go userspace)
- **golgiBody**: `10.13.37.1` — 38ms RTT
- **Peers reachable**: 6 (golgiBody + 5 gates at .2, .5, .7, .8, .10)
- **Status**: OPERATIONAL

## macOS-Specific Notes

- No Gatekeeper issues — binaries built locally, not quarantined
- No SIP issues — all binaries in `~/.local/bin`
- No launchd integration yet — manual start for validation
- iPhone XS USB tethering → LAN transition ready

## Depot — PUSHED

- **15 darwin binaries** pushed to golgiBody: `/opt/ecoPrimals/plasmidBin/primals/aarch64-apple-darwin/`
- **5th OS family** in depot (alongside x86_64-linux-musl, x86_64-linux-gnu, x86_64-windows-gnu, aarch64-linux-musl)
- **BLAKE3 verified** — all 15 binaries hashed on depot
- Total payload: **104M**
- Push method: SCP via SSH (root@golgiBody, ecoPrimal key)

## iOS Cross-Compilation — LIVE

- **Rust target**: `aarch64-apple-ios` installed (1.93.0 + stable)
- **bearDog iOS binary**: Mach-O 64-bit arm64 (6.3M) — compiles and links successfully
- **SDK**: iPhoneOS26.5.sdk
- **Remaining**: Apple Developer enrollment → signing identity → provisioning → device deployment

---

## Action Items — COMPLETED

1. ~~Register SSH key~~ — **DONE** (Forgejo user `graftgate`, Owner on all 4 orgs)
2. ~~Merge 4 darwin fixes~~ — **DONE** (bearDog `24dd74d`, toadStool `e172eb0c3`, squirrel, petalTongue `4d46f3e3`)
3. ~~Grant golgiBody SSH~~ — **DONE** (root access via ecoPrimal key)
4. ~~Depot push~~ — **DONE** (15 binaries, 104M, BLAKE3 verified)

## Remaining — iosGate Prep

1. Apple Developer Program enrollment ($99) — in progress
2. Signing identity + development certificate
3. iPhone XS UDID registration + provisioning profile
4. iosGate bearDog deployment

---

*graftGate — FULLY ENMESHED. First `aarch64-apple-darwin` gate. 15/15 primals compiled (4 darwin fixes, all merged). WG 10.13.37.13, 6 mesh peers. Depot pushed (5th OS family). iOS cross-compile live. Xcode 26.6. Wave 157i CASCADE COMPLETE.*
