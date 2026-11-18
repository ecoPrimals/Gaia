# petalTongue v1.6.6 — Stadial Gate Readiness

**Date**: May 17, 2026
**Primal**: petalTongue
**Trigger**: Wave 22 stadial gate — universal standards checklist + per-primal items
**Gate**: Low-Debt Group — CLEAN. All checklist items resolved.

## Universal Standards Checklist

### Runtime
- [x] Health triad: `health.liveness`, `health.readiness`, `health.check` — all
      implemented in IPC dispatch + web mode HTTP routes
- [x] UDS socket at `$XDG_RUNTIME_DIR/biomeos/petaltongue.sock`
- [x] TCP fallback: `--port` flag, ecosystem port 9900
- [x] `server` subcommand with `--port` for JSON-RPC
- [x] Standalone startup without `FAMILY_ID`/`NODE_ID`

### Discovery
- [x] `capabilities.list` returns `{ capabilities, count, primal, ... }` — `count`
      field added this session
- [x] `identity.get` returns canonical identity response
- [x] `primal.announce` — dispatch alias for `capability.announce`
- [x] All methods follow `{domain}.{operation}[.{variant}]` naming

### Security
- [x] BTSP handshake mandatory when `FAMILY_ID` is set (non-"default")
- [x] ChaCha20-Poly1305 + HKDF-SHA256 with `btsp-session-v1-*`
- [x] `FAMILY_ID` + `BIOMEOS_INSECURE=1` = refuse to start
- [x] `btsp.capabilities` registered — new method returns cipher suite + status
- [x] Zero metadata leakage (stripped binary in release profile)
- [x] UDS-first default (TCP off unless `--port` explicitly set)
- [x] `deny.toml` bans `ring`, `openssl`, `aws-lc-sys`

### Build / plasmidBin
- [x] `manifest.toml` version 1.6.6 matches workspace
- [x] `checksums.toml` with BLAKE3 hashes — NEW
- [x] `seed_fingerprint` BLAKE3 hash in manifest.toml — NEW
- [x] `notify-plasmidbin.yml` workflow present
- [x] CI green (fmt, clippy, test, doc)
- [x] `edition = "2024"` in workspace Cargo.toml

### Documentation
- [x] README.md version matches manifest (v1.6.6)
- [x] CHANGELOG.md documents recent evolution through May 17, 2026
- [x] CONTEXT.md current — stadial readiness section added

### Composition Readiness
- [x] Stability tiers annotated: all 55 methods classified Stable or Evolving
- [x] Degradation behavior documented (representation layer, not control plane)
- [x] Downstream pairing: esotericWebb, lithoSpore, projectNUCLEUS, wetSpring

## Per-Primal Items (from Wave 22)

- [x] Multiple modes verify health triad: `server` and `live` always start IPC;
      `web` starts IPC with `--ipc`; `ui`/`tui`/`headless`/`status` are
      rendering modes without IPC. Web mode now exposes `/health/liveness` and
      `/health/readiness` HTTP endpoints for deployment probing.
- [x] Platform audio deps documented: graph engine = pure Rust (hound WAV);
      UI = symphonia decode; no system audio playback compiled in; eframe pulls
      windowing deps for `ui` mode only.

## Code Changes

### New Methods
- `btsp.capabilities` — `identity_lifecycle.rs`
- `primal.announce` — dispatch alias in `dispatch.rs`
- `/health/liveness`, `/health/readiness` — `web_mode/mod.rs`

### capabilities.list Enhancement
- Extracted methods to `Vec` for dynamic `count`
- Added `btsp.capabilities`, `primal.announce`, `proprioception.get` to list

### Manifest
- `methods` array expanded from 12 to 55 (full dispatch table)
- Added `seed_fingerprint`
- Health section: `liveness`, `readiness`, `check` fields

### Lint Fixes
Pre-existing clippy lints across 5 crates: `manual_midpoint`, `manual_clamp`,
`cast_sign_loss`, `too_many_lines`, `redundant_closure`, `let_else`,
`long_literal_lacking_separators`, `format_args`, `match_same_arms`,
`const_fn`, `expect_used`.

## Quality Gate
- `cargo fmt --check`: PASS
- `cargo clippy --workspace --all-targets --all-features -- -D warnings`: PASS
- `cargo test --workspace --all-features`: 265+ tests, 0 failures
- `cargo doc --workspace --no-deps --all-features`: PASS

## Stadial Status: READY
