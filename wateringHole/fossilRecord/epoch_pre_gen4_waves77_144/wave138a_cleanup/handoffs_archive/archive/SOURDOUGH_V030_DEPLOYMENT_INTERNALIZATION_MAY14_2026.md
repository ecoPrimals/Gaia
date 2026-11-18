# sourDough v0.3.0 — Deployment Internalization Handoff

**Date**: May 14, 2026
**From**: sourDough team
**Context**: First phase of the deployment internalization contract
(primalSpring/docs/SOURDOUGH_DEPLOYMENT_INTERNALIZATION.md)

## What Shipped

### `sourdough sign` (top-level CLI)

Ed25519 detached signatures, wired from the `sourdough-genomebin::signing` module
that was built in v0.2.0 but was not exposed via CLI.

- `sourdough sign <binary>` — signs any file, produces `.sig` sidecar
- `sourdough sign --generate-key` — generates Ed25519 keypair (`signing.key` + `signing.pub`)
- `sourdough sign --key <path>` — uses a custom signing key
- `sourdough verify <binary>` — verifies signature against public key
- `sourdough verify --pub-key <path>` — custom public key path
- `sourdough genomebin sign` now delegates to real signing (was sequoia-openpgp error stub)

Roundtrip verified: generate key → sign binary → verify → tamper → detect invalid.

### `sourdough validate ecobin` evolved

The command now auto-detects path type:

- **File path** (compiled binary): validates static linking (via `file` + `ldd`),
  stripped status, ELF format, size budget (50 MB default)
- **Directory path** (project source): existing behavior — C dependency scan,
  code formatting, clippy lint check

### `sourdough scaffold systemd` (hardened `.service` units)

Generates hardened systemd service units following the ecosystem membrane pattern.

- `sourdough scaffold systemd <primal> --role <role>` — produces `{name}-{role}.service`
- Security hardening: `NoNewPrivileges`, `ProtectSystem=strict`, `ProtectHome`, `PrivateTmp`
- Resource limits: `MemoryMax=128M`, `CPUQuota=50%`
- Socket path: `/run/biomeos/{name}.sock` (ecosystem convention)
- Restart policy: `always`, 5s interval, burst limit

### `sourdough layout` (triple-first validation)

Validates binary directories against the triple-first convention.

- `sourdough layout <dir>` — checks for `{triple}/{name}` structure
- Detects flat binaries that should be under triple directories
- Warns on missing Tier 1 triples (x86_64, aarch64, armv7 musl)
- Validates triple directories are non-empty

### `sourdough validate composition` (composition binary presence)

Validates that all primals in a composition are present as binaries.

- Predefined compositions: tower, node, nest, nucleus, meta, full
- Matches `ports.env` atomic model exactly
- Supports `--triple-first` flag for triple-first layout scanning
- Custom compositions via comma-separated primal list

### Internalization Contract Status

| Pattern | Contract Phase | Status |
|---------|---------------|--------|
| `sourdough sign` | v0.3.0 | **Shipped** |
| `sourdough verify` | v0.3.0 | **Shipped** |
| `sourdough validate ecobin` (binary) | v0.3.0 | **Shipped** |
| `sourdough scaffold systemd` | v0.3.0 | **Shipped** |
| `sourdough layout` | v0.3.0 | **Shipped** |
| `sourdough validate composition` | v0.3.0 | **Shipped** (moved from v0.4.0) |
| `sourdough harvest` | v0.4.0 | Planned |
| `sourdough package` | v0.5.0 | Planned |
| `sourdough deploy` | v0.6.0 | Planned |

### Open Questions (from contract)

1. **Key management**: Should `sourdough sign` use age-encrypted keys or
   integrate with BearDog BTSP credential store? Currently uses plain hex files.
2. **CI ownership**: Does `auto-harvest.yml` call `sourdough harvest` or
   does sourDough provide its own GitHub Action?
3. **Remote deploy transport**: SSH (current) vs BTSP-tunneled commands?

## Quality Gates

- 264 tests passing (0 failures, 0 ignored)
- `cargo clippy --workspace --all-targets` zero warnings
- `cargo deny check` passing
- `cargo doc --workspace --no-deps` zero warnings
- `cargo fmt --all -- --check` clean
