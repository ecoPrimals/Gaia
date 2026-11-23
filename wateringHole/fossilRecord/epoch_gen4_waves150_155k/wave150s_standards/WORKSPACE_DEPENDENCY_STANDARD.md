# Workspace Dependency Management Standard

**Status**: Active  
**Adopted**: March 30, 2026  
**Authority**: WateringHole Consensus  
**Compliance**: Mandatory for all Rust workspace primals  
**Reference Implementation**: coralReef (March 30, 2026)

---

## Core Principle

**All shared dependency versions live in the workspace root `Cargo.toml`.**

Crate-level `Cargo.toml` files reference them with `{ workspace = true }` and
may add crate-specific features. Per-crate inline version pins are forbidden
for any dependency used by more than one workspace member.

---

## Why

### Single source of truth

When `naga = "28"` appears in four crates, a version bump touches four files
and risks version skew if one is missed. A workspace dependency ensures one
edit, zero drift.

### Faster compilation

Cargo unifies identical dependency versions into a single build unit. Inline
pins that accidentally drift (e.g. `1.1` vs `1.1.4`) produce duplicate
compilations of the same crate with different semver resolutions.

### Cleaner audit

`cargo deny` / `cargo tree` produce cleaner output when every workspace member
resolves to the same version. Duplicate advisories vanish.

### Visible dependency matrix

The workspace `[workspace.dependencies]` section is a single manifest of
everything the primal depends on — a readable compilation and security matrix.

---

## Rules

### 1. Declare in workspace root

Every external dependency used by any member crate **must** appear in
`[workspace.dependencies]` in the root `Cargo.toml`.

```toml
# root Cargo.toml
[workspace.dependencies]
naga = { version = "28", features = ["wgsl-in"] }
```

### 2. Reference from crates

Member crates reference the workspace declaration and may **add** features
(never versions).

```toml
# crates/coral-reef/Cargo.toml
[dependencies]
naga = { workspace = true, features = ["spv-in", "spv-out", "glsl-in"] }
```

Workspace features and crate-level features are merged by Cargo.

### 3. Internal path crates follow the same pattern

Path dependencies within the workspace also belong in
`[workspace.dependencies]` so that member crates use `{ workspace = true }`
consistently.

```toml
# root Cargo.toml
[workspace.dependencies]
coral-driver = { path = "crates/coral-driver" }

# crates/coralreef-core/Cargo.toml
[dependencies]
coral-driver = { workspace = true }
```

Feature activation on path crates uses the same additive pattern:

```toml
coral-driver = { workspace = true, features = ["vfio"] }
```

### 4. Dev-dependencies follow the same rules

Test-only crates (`tempfile`, `criterion`, `trybuild`, etc.) are declared in
`[workspace.dependencies]` and referenced with `{ workspace = true }` in each
crate's `[dev-dependencies]` section.

### 5. Proc-macro crates are not exempt

Proc-macro crates (`syn`, `quote`, `proc-macro2`) follow the same workspace
pattern. Even if only one crate uses them today, centralizing prevents
accidental version drift when a second proc-macro is added.

### 6. Optional/feature-gated dependencies

Optional dependencies are declared normally in the workspace root. The
`optional = true` flag is set at the crate level, not the workspace level.

```toml
# root Cargo.toml
[workspace.dependencies]
cudarc = { version = "0.19", features = ["driver", "cuda-12060"] }

# crates/coral-driver/Cargo.toml
[dependencies]
cudarc = { workspace = true, optional = true }
```

### 7. Version bumps are atomic

When upgrading a dependency, change the version in the workspace root and run
`cargo update -p <crate>`. All members pick up the new version simultaneously.

---

## Exceptions

**Standalone codegen tools** (e.g. `amd-isa-gen`) that are workspace members
for convenience but share zero dependencies with the main crate graph may keep
inline versions for tool-specific crates (e.g. `quick-xml`, `anyhow`) that
would pollute the workspace dependency list. They **should** still use workspace
declarations for any dependency also used by the main crate graph (e.g. `serde`,
`tempfile`).

---

## Validation

```bash
# After consolidation, verify no duplicate versions:
cargo tree --duplicates
# Expected: empty or ecosystem-caused only (not our inline pins)

# Verify clean build:
cargo check --workspace --all-features
cargo clippy --workspace --all-features -- -D warnings
cargo test --workspace
```

---

## Compliance Checklist

- [ ] Every dependency version appears **exactly once** in the root `Cargo.toml`
- [ ] Every member crate uses `{ workspace = true }` for shared dependencies
- [ ] Feature additions at the crate level use `{ workspace = true, features = [...] }`
- [ ] `cargo tree --duplicates` shows no self-inflicted duplicates
- [ ] Version bumps touch only the root `Cargo.toml`

---

## Relationship to ecoBin

Workspace dependency management is a **build hygiene prerequisite** for ecoBin
compliance. A primal cannot reliably prove "zero C dependencies" or pass the
cross-compilation matrix if version skew between members allows a C-linked
version to slip in through one crate while a pure-Rust version is declared in
another.

Centralizing dependencies makes the ecoBin audit command (`cargo tree | grep
-E "(openssl-sys|ring|...)"`) authoritative — if a C crate isn't in the
workspace root, it cannot enter any member.

---

**Standard**: Workspace Dependency Management v1.0.0  
**Adopted**: March 30, 2026  
**Authority**: WateringHole Consensus  
**Status**: Active
