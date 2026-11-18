# FRAGO: aarch64 Cross-Compile Blocker — bearDog C-Dependency

**Date**: 2026-06-09
**From**: cellMembrane / ironGate
**To**: bearDog team, primalSpring overwatch
**Priority**: P1 for cross-arch deployment
**Type**: Upstream blocker — C-dependency elimination needed

---

## Context

cellMembrane attempted a full aarch64-unknown-linux-musl cross-compile sweep for the
Pixel 8 / GrapheneOS deployment target. Results:

| Primal | aarch64 Status | Notes |
|--------|---------------|-------|
| songbird | **BUILT** | 20,231KB — clean cross-compile |
| skunkbat | **BUILT** | Previously validated |
| sourdough | **BUILT** | Previously validated |
| beardog | **FAILED** | `aws-lc` C linker errors |
| biomeos | Pending | Blocked on beardog (security provider) |
| remaining 8 | Pending | In queue after beardog |

## The Blocker

bearDog links `aws-lc-rs` (AWS Libcrypto) which contains C code compiled via `cc` crate.
When targeting `aarch64-unknown-linux-musl`, the linker fails:

```
dsa.c:(.text.aws_lc_0_41_0_dsa_internal_paramgen+0x1c0): undefined reference to `__memcpy_chk`
collect2: error: ld returned 1 exit status
```

`__memcpy_chk` is a glibc fortification symbol not available in musl. The C code assumes
glibc even when targeting musl.

## The Central Dogma

**Rust compiler is our DNA synthase.** All primal code flows through the central dogma:

```
Source (Rust) → Compiler (rustc) → Binary (static musl)
```

C dependencies break this dogma — they introduce external linkage requirements,
platform-specific build failures, and non-reproducible compilation. Every primal that
achieved clean aarch64 cross-compile did so by eliminating C deps entirely.

## Required Action (bearDog)

Replace `aws-lc-rs` with a pure-Rust cryptography stack:

| C Dependency | Pure-Rust Replacement | Crate |
|-------------|----------------------|-------|
| `aws-lc-rs` (TLS) | `rustls` + `ring` (or `rustls-post-quantum`) | `rustls` |
| `aws-lc-rs` (X25519) | `x25519-dalek` | `curve25519-dalek` |
| `aws-lc-rs` (AES-GCM) | `aes-gcm` | `RustCrypto` |
| `aws-lc-rs` (SHA) | `sha2` / `blake3` | `RustCrypto` / `blake3` |
| `aws-lc-rs` (HMAC) | `hmac` | `RustCrypto` |
| `aws-lc-rs` (RSA) | `rsa` | `RustCrypto` |
| `aws-lc-rs` (ECDSA) | `p256` / `k256` | `RustCrypto` |

If `ring` is used (which contains some C/asm), ensure `ring` 0.17+ with the
`--target aarch64-unknown-linux-musl` musl build path is validated. Alternatively,
fully pure-Rust via `rustls` + `aws-lc-rs` feature flags that disable C code, OR
switch to `rustls` with `ring` backend which has musl support.

**Simplest path**: Check if `aws-lc-rs` has a `--cfg` or feature flag for
musl-compatible builds. If not, switch TLS provider to `rustls` with
`ring` or `aws-lc-rs` FIPS-less mode.

## Validation

Once C deps are eliminated, bearDog should pass:

```bash
cargo build --release --target aarch64-unknown-linux-musl
file target/aarch64-unknown-linux-musl/release/beardog
# Expected: ELF 64-bit LSB executable, ARM aarch64, statically linked
```

## Impact

bearDog is the security provider — every primal depends on it for crypto operations.
Until bearDog cross-compiles cleanly, no full NUCLEUS can run on aarch64 targets
(Pixel 8, ARM servers, future ARM VPS).

## cellMembrane Status

- `plasmid.harvest --target aarch64-unknown-linux-musl` pipeline is operational
- songbird, skunkbat, sourdough confirmed building for aarch64
- Depot staging at `infra/plasmidBin/primals/aarch64-unknown-linux-musl/`
- Will sweep remaining primals once beardog unblocks

---

*Filed by cellMembrane automated frago — Wave 103*
