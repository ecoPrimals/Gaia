# Pure Rust Crypto Purity Standard

**Status**: ECOSYSTEM STANDARD v1.0  
**Adopted**: Jun 9, 2026  
**Authority**: WateringHole Consensus (BearDog → primalSpring review)  
**Compliance**: Mandatory for primals handling cryptographic operations  
**Reference Implementation**: BearDog v0.9.0 Wave 145  
**Reinforces**: ecoBin Architecture Standard v3.0

---

## Rationale

C-linked crypto libraries (`aws-lc-rs`, `ring`, `openssl`, `boring`) create:
- Cross-compilation blockers (musl, ARM, WASM targets)
- Supply chain audit surface (C code is invisible to `cargo audit`)
- Build toolchain dependencies (`cc`, `cmake`, `bindgen`)
- Platform-specific build failures

The Rust ecosystem now has mature, audited Pure Rust alternatives for every standard cryptographic operation. This standard codifies enforcement.

---

## Standard Declaration

### S1: Zero C-Crypto Dependencies

Every primal that performs cryptographic operations MUST have zero C-linked crypto crates in its resolved dependency graph.

**Verification**:
```bash
cargo deny check bans
# Expected: 0 DENIED entries
```

### S2: `deny.toml` Ban List

Every primal MUST include a `deny.toml` that explicitly bans C-crypto crates. Minimum ban list:

```toml
[[bans.deny]]
wrappers = []
name = "aws-lc-rs"

[[bans.deny]]
wrappers = []
name = "aws-lc-sys"

[[bans.deny]]
wrappers = []
name = "ring"

[[bans.deny]]
wrappers = []
name = "openssl"

[[bans.deny]]
wrappers = []
name = "openssl-sys"

[[bans.deny]]
wrappers = []
name = "boring"

[[bans.deny]]
wrappers = []
name = "boring-sys"

[[bans.deny]]
wrappers = []
name = "native-tls"

[[bans.deny]]
wrappers = []
name = "security-framework-sys"

[[bans.deny]]
wrappers = []
name = "schannel"
```

The full 19-crate ban list is maintained in BearDog's `deny.toml` as the reference.

### S3: Approved Pure Rust Alternatives

| Operation | C Library (BANNED) | Pure Rust Alternative |
|-----------|-------------------|----------------------|
| TLS `CryptoProvider` | `aws-lc-rs`, `ring` | `rustls-rustcrypto` |
| X.509 CSR generation | `rcgen` (when C-linked) | `p256` + `x509-cert` |
| AEAD encryption | `ring::aead` | `aes-gcm`, `chacha20poly1305` |
| Signatures | `ring::signature` | `ed25519-dalek`, `p256`, `p384`, `rsa` |
| Hashing | `ring::digest` | `sha2`, `sha3`, `blake3` |
| Key exchange | `ring::agreement` | `x25519-dalek`, `p256` |
| KDF | `ring::hkdf` | `hkdf`, `pbkdf2`, `argon2`, `scrypt` |
| Random | `ring::rand` | `rand`, `rand_core` (OS-backed) |

### S4: `cc` Crate Exception

The `cc` crate is allowed ONLY as a transitive dependency of `blake3` when blake3 uses its `pure` Rust feature (which disables C assembly). All other `cc` usage must be explicitly justified.

```toml
[[bans.deny]]
wrappers = ["blake3"]
name = "cc"
```

### S5: Build Tool Bans

C build toolchain crates MUST be banned:

```toml
[[bans.deny]]
wrappers = []
name = "bindgen"

[[bans.deny]]
wrappers = []
name = "cmake"
```

---

## Validation Pattern

### CI Gate

Add to CI pipeline:

```bash
cargo deny check bans 2>&1 | grep -c "DENIED"
# MUST be 0
```

### Local Development

```bash
# One-time setup
cargo install cargo-deny

# Validate purity
cargo deny check bans
cargo deny check advisories
cargo deny check licenses
cargo deny check sources
```

### Primal Adoption Checklist

1. Copy ban list from BearDog `deny.toml` to primal's `deny.toml`
2. Run `cargo deny check bans` — fix any violations
3. Replace C-crypto imports with Pure Rust alternatives per S3 table
4. Verify `cargo check` still passes
5. Run full test suite
6. Update primal docs to reflect Pure Rust status

---

## Wider Rust Ecosystem Value

This standard and its reference implementation (BearDog) demonstrate a validated, production-tested path for any Rust project to eliminate C-crypto dependencies. The pattern is:

1. **Declare** — Ban list in `deny.toml` makes the policy machine-readable
2. **Enforce** — `cargo deny check` runs in CI as a gate
3. **Consolidate** — Single canonical wrapper struct for consistent API across the codebase
4. **Verify** — All 4 `cargo deny` checks pass (advisories, bans, licenses, sources)

Projects outside ecoPrimals can adopt this pattern by:
- Using the S3 alternatives table for migration planning
- Copying the `deny.toml` ban list
- Using `rustls-rustcrypto` as their TLS `CryptoProvider`

---

## Ecosystem Adoption Status

| Primal | Status | Notes |
|--------|--------|-------|
| BearDog | COMPLIANT | Reference implementation, Wave 145 |
| Others | PENDING AUDIT | primalSpring to coordinate |

---

## References

- BearDog `deny.toml`: canonical ban list with documented rationale
- ecoBin Architecture Standard v3.0: zero C-dependency mandate
- RustCrypto organization: https://github.com/RustCrypto
- `rustls-rustcrypto`: https://github.com/RustCrypto/rustls-rustcrypto
