# biomeOS Wave 86 — NUCLEUS Federation Profile Fix (v4.09)

**Date**: June 6, 2026
**Gate**: southGate (ironGate)
**Cascade**: primalSpring → eastGate → southGate
**Severity**: P1 BLOCKER RESOLVED

---

## P1 BLOCKER: Songbird Federation Env Passthrough

### Root Cause

`config/nucleus_launch_profiles.toml` songbird profile had no env_vars section.
When `biomeos nucleus start` launched songbird, it received only `--socket` (UDS
path) and capability-resolved security sockets. Without `SONGBIRD_FEDERATION_PORT`
and `SONGBIRD_PEERS`, songbird started in standalone UDS mode — no federation TCP
listener, invisible to other gates.

strandGate attempted `mesh.init` → eastGate → CONNECTION REFUSED on `:7700`.

### Fix Applied

```toml
[profiles.songbird.env_vars]
SONGBIRD_FEDERATION_PORT = "$SONGBIRD_FEDERATION_PORT"
SONGBIRD_PEERS = "$SONGBIRD_PEERS"
SONGBIRD_NODE_ID = "$node_id"
```

The `$UPPER_CASE` convention means "passthrough from parent process environment"
(resolved via `std::env::var`). If the var is unset in the parent, it is silently
skipped — songbird falls back to standalone mode gracefully.

`$node_id` uses the existing literal substitution (from `--node-id` CLI arg).

### Code Change: `build_primal_command_with()`

Enhanced the env_vars resolution loop:
- `$UPPER_CASE` (all-caps + underscores after `$`) → read from parent env
- `$family_id` / `$node_id` → literal substitution from config (existing behavior)
- Unset parent env vars → `continue` (no env set on child)

### P1: `--family-id` Flag Verification

Confirmed the `pass_family_id_flag = false` logic is correctly implemented.
The code (lines 243-249 of `nucleus.rs`) reads the profile's flag and only passes
`--family-id` as a CLI arg when `true`. Songbird's profile explicitly sets `false`.
The cascade's observation may have been from a stale binary build.

Test `test_build_primal_command_songbird` now explicitly asserts `--family-id`
is NOT present in songbird's arg list.

---

## Validation (operator action required on eastGate)

After deploying v4.09:

```bash
export FAMILY_SEED=$(cat ~/.family.seed)
export SONGBIRD_FEDERATION_PORT=7700
export SONGBIRD_PEERS="strand-gate@192.168.1.132:7700"
biomeos nucleus start --node-id east-gate --family-id eastgate --mode tower
```

Expected:
- `ss -tlnp | grep 7700` → songbird LISTENING
- `discovery.peers` → `peer_count >= 1` when strandGate is online

---

## Test Results

- **495 tests passed** (biomeos-unibin), 0 failures
- `cargo clippy --workspace --lib` — zero warnings
- `cargo check` — clean

## Files Changed

| File | Change |
|------|--------|
| `config/nucleus_launch_profiles.toml` | Added `[profiles.songbird.env_vars]` with federation passthrough |
| `crates/biomeos/src/modes/nucleus.rs` | Enhanced env_vars resolution for `$UPPER_CASE` parent env inheritance |
| `crates/biomeos/src/modes/nucleus_tests.rs` | Expanded songbird test: federation env + `--family-id` absence assertion |
| `CHANGELOG.md` | v4.09 entry |
| `CURRENT_STATUS.md` | Updated to v4.09 |
| `START_HERE.md` | Updated to v4.09 |

## Upstream Coordination

- **eastGate operator**: Deploy v4.09 binary, then start NUCLEUS with federation env vars set
- **strandGate**: Ready and waiting — once eastGate NUCLEUS is live, mesh proof completes
- **primalSpring**: P1 BLOCKER resolved. Mesh proof is one `biomeos nucleus start` away.
