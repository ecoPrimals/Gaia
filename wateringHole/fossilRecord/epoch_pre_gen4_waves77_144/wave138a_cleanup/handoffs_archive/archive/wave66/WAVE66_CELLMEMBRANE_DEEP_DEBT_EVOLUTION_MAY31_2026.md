# WAVE66 cellMembrane Deep Debt Evolution — May 31 2026

**From:** ironGate (cellMembrane team)
**Date:** 2026-05-31
**Wave:** 66
**Scope:** membrane-shadow deep debt sprint + K-Derm relay Rust evolution

---

## Summary

Wave 66 eliminates external tool dependencies, removes dead code, and
completes the K-Derm relay evolution from bash to Rust.

## Deliverables

### K-Derm Relay Chain — bash → Rust (Wave 65 FRAGO)

New `relay.rs` module (265L) in membrane-shadow:
- `relay::mediate()` — pull from Forgejo (metallic bond inward)
- `relay::ship_extracellular()` — push to GitHub via SSH to golgiBody-ext
- `relay::run()` — full 3-stage chain exposed as `membrane relay.run <repo_path>`

Replaces: `pepti-sync-relay.sh` (95L), `ext-github-push.sh` (91L)
Integrates: `impulse-relay-hook.sh` (52L) → wired via impulse::sense()
Keeps bash: `golgi-post-receive-relay.sh` (36L) — Forgejo hook constraint

### External Dependencies Eliminated

| Was (shell-out) | Now (pure Rust) | Module |
|-----------------|-----------------|--------|
| `socat` → UDS JSON-RPC | `std::os::unix::net::UnixStream` | impulse.rs |
| `curl` → HTTP download | `reqwest` (already a dep) | plasmid.rs |
| `b3sum` → BLAKE3 checksum | `blake3` crate in-process | plasmid.rs |
| `extract_json_field` hack | `serde_json` deserialization | plasmid.rs |

### Dead Code Removed

- `signal.rs` (deprecated Wave 63, slated for Wave 66 removal) — deleted
- `signal.*` CLI dispatch aliases — removed
- `neural-bridge` feature gate — removed (tokio/net always available)
- `forgejo_sync.sh` (246L) — superseded by `membrane temporal.cascade`
- `forgejo_pull_mirror.sh` (196L) — superseded by `membrane mirror.sync-all`

### Hardcoded Values Parameterized

| Was | Now | File |
|-----|-----|------|
| `/opt/ecoPrimals` in remote SSH script | `config.ecoprimals_root` | relay.rs |
| `ssh://git@git.primals.eco:2222/...` | `manifest.forgejo_clone_url()` | temporal.rs |

### Code Quality

- `FetchSource::from_str()` inherent → `impl FromStr` (proper trait)
- `is_none_or`, `is_ok_and`, `let-else` patterns applied
- 8 new impulse unit tests (discovery, expiry, ack, sense)
- `clippy::pedantic` warnings reduced (123 → 105, all new code zero-warning)

## Metrics

| Metric | Before (Wave 65) | After (Wave 66) |
|--------|-------------------|------------------|
| Tests | 191 | 204 |
| External tool deps | socat, curl, b3sum | 0 |
| Bash scripts in garden | 2 (442L) | 0 |
| Dead code (signal.rs) | 20L + dispatch shim | Removed |
| Clippy warnings (new code) | N/A | 0 |

## Impulse Acknowledged

`2026-05-31T20-45-eastGate-cellmembrane-k-derm-relay-evolution-bash-rust`

Note: relay.rs implemented, impulse acked with implementation note.

## Upstream Gaps for primalSpring

1. `nucleus_launcher` binary not in plasmidBin releases (deploy `--uds-only` blocked)
2. biomeOS v3.84 `graph.execute` not implemented (spring overlay gated)
3. CI sovereignty (S4): still GitHub Actions — Forgejo CI runner not deployed

## For golgi-post-receive-relay.sh

Once `membrane` binary is deployed to VPS, update the hook to call
`membrane relay.run` instead of the bash script chain. The Rust binary
handles all three stages internally.
