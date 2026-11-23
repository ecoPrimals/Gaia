# Secrets and Seeds Standard

**Version:** 1.0.0  
**Date:** March 31, 2026  
**Status:** Active  

---

## Core Principle

**No static secrets in repositories.** Seeds, keys, tokens, and credentials are generated at runtime or build time — never committed to source. A published binary carries its own lineage seed derived during build, validated via guideStone, and traceable without exposing the generation material.

---

## Definitions

| Term | Meaning |
|------|---------|
| **Secret** | Any value whose exposure compromises security: private keys, API tokens, passwords, PEM material |
| **Seed** | A cryptographic or identity-bearing value used to derive keys, generate configurations, or establish lineage |
| **Lineage seed** | A build-time or init-time seed embedded in a binary or artifact that proves provenance without revealing generation material |
| **Tutorial seed** | A well-known, documented seed used in examples, showcases, and tests — clearly marked as non-production |

---

## Repository Rules

### MUST NOT commit

- Private keys (PEM, PKCS8, JWK private material)
- API keys or tokens (sk-ant, sk-proj, Bearer tokens with real values)
- Passwords or passphrases
- .env files with real credentials
- Family seeds, mito seeds, or any production identity material
- SSH keys, TLS certificates with private keys
- Cloud credentials (AWS, GCP, Cloudflare tokens)

### MUST commit (when applicable)

- Public keys and certificates (without private counterparts)
- Example/template configurations with placeholder values
- Tutorial seeds clearly marked `# TUTORIAL ONLY — DO NOT USE IN PRODUCTION`
- `.env.example` files with placeholder structure

### MAY commit

- Test fixtures using well-known constants (e.g. all-zeros, RFC test vectors)
- Demo keys generated specifically for showcase — documented as compromised-by-design

---

## Seed Generation Patterns

### Init-time (primal first run)

When a primal starts for the first time, it generates its identity material:

```rust
// Pattern: generate on first run, persist to runtime directory
let seed_path = runtime_dir.join("identity.seed");
if !seed_path.exists() {
    let seed = generate_cryptographic_seed();
    write_atomic(&seed_path, &seed)?;
}
```

Runtime directories: `$XDG_RUNTIME_DIR/<primal>/`, `~/.local/share/<primal>/`, or operator-configured path. Never under the source tree.

### Build-time (lineage embedding)

Released binaries carry a lineage seed derived during build:

```rust
// build.rs pattern
let build_seed = derive_lineage_seed(
    env!("CARGO_PKG_VERSION"),
    &git_commit_hash(),
    &build_timestamp(),
);
println!("cargo:rustc-env=LINEAGE_SEED={}", build_seed);
```

The lineage seed is:
- **Deterministic** given the same source + version + commit
- **Verifiable** via guideStone (the binary can prove its lineage)
- **Non-secret** — it proves provenance, not access

### Tutorial seeds (showcase / testing)

Primals should ship tutorial configurations that generate fresh seeds on first use:

```bash
# Good: generate at init
./primal init --tutorial

# Bad: static seed in repo
echo "seed=0xdeadbeef" > config.toml && git add config.toml
```

Tutorial mode should:
1. Generate ephemeral keys/seeds
2. Log that tutorial mode is active
3. Refuse to connect to production infrastructure
4. Self-document the generated material's location

---

## Binary Distribution (genomeBin / plasmidBin)

### Lineage validation chain

```
Source (git commit) → Build (lineage seed derived) → Binary (seed embedded)
                                                        ↓
                                                   guideStone validates
                                                        ↓
                                                   rhizoCrypt records DAG
                                                        ↓
                                                   loamSpine issues certificate
                                                        ↓
                                                   sweetGrass traces provenance
```

### What a released binary contains

- Embedded lineage seed (build-derived, non-secret)
- Version string and commit hash
- guideStone validation checksums for its own outputs
- Capability declarations (primalSpring)

### What a released binary does NOT contain

- Build-machine paths (see Build Cleanliness below)
- Private keys or signing material
- Network credentials or tokens
- User-specific configuration

---

## Build Cleanliness

### Problem

Rust binaries compiled in development environments embed host-specific paths through:
- Panic messages (`/home/username/...` in panic file paths)
- Debug info (DWARF sections)
- Procedural macro expansions
- Build script output

### Requirements for public binaries

1. **Strip debug info:** `strip = true` in `[profile.release]`
2. **Remap path prefix:** `rustflags = ["--remap-path-prefix=/home/builder=build"]` in `.cargo/config.toml`
3. **Verify with strings:** `strings binary | grep -i '/home/'` should return nothing
4. **CI builds preferred:** Build in ephemeral containers where host paths are generic

### .cargo/config.toml pattern for clean builds

```toml
[build]
rustflags = [
    "--remap-path-prefix", "/home/builder=build",
    "--remap-path-prefix", "/rustc/=rustc/",
]

[profile.release]
strip = true
lto = true
```

### Verification checklist

- [ ] `strings <binary> | grep '/home/'` returns empty
- [ ] `strings <binary> | grep 'eastgate\|strandgate\|southgate\|westgate\|northgate\|biomegate'` returns empty
- [ ] `strings <binary> | grep '192\.168\.'` returns empty (unless intentional LAN default)
- [ ] Binary size is reasonable for release profile (strip + LTO)

---

## Pre-Push Audit Patterns

Before making any repository public or pushing to public remotes:

```bash
# Current tree — no secrets
rg -g '!target/' -g '!.git/' 'BEGIN PRIVATE KEY|BEGIN RSA|sk-ant|sk-proj' .

# Current tree — no personal paths
rg -g '!target/' -g '!.git/' '/path/to/home|/path/to/home|/path/to/home|/path/to/home|/path/to/home|/path/to/home' .

# Git history — identity check (should be ecoPrimal <ecoPrimal@pm.me> only for ecoPrimals org)
git log --all --format='%an <%ae>' | sort -u
git log --all --format='%cn <%ce>' | sort -u

# Git history — secrets in any commit
git log --all --oneline -S "BEGIN PRIVATE KEY" -- | head -5
git log --all --oneline -S "sk-ant" -- | head -5

# Git history — personal paths in any commit
git log --all --oneline -S "/path/to/home" -- | head -5
git log --all --oneline -S "/path/to/home" -- | head -5
```

### Remediation tools

- **Current tree:** `sed`, `rg --replace`, manual edits
- **Git history:** `git filter-repo --blob-callback` for content, `git filter-repo --mailmap` for identities
- **Binary artifacts:** Rebuild from clean environment with path remapping

---

## Publication Identity Standard

### ecoPrimals organization repositories

- **Author/committer:** `ecoPrimal <ecoPrimal@pm.me>`
- **No machine-specific identities** in git metadata (no `user@hostname`, no ISP domains)
- **wateringHole exception:** Historical handoffs and fossilRecord may retain development-era identities as geological record; root standards documents must use canonical identity

### syntheticChemistry organization repositories

- Personal attribution acceptable — these are science-facing
- Author may use personal name where appropriate for academic context

### sporeGarden organization repositories

- Follow ecoPrimals identity standard

---

## Version History

| Version | Date | Notes |
|---------|------|-------|
| 1.0.0 | 2026-03-31 | Initial standard after Provenance Trio public release audit |
