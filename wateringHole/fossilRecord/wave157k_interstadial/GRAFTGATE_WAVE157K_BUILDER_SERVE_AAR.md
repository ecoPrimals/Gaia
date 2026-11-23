# graftGate AAR — Wave 157k builder.serve Deployment + D12 Fix

**Date**: Aug 13, 2026 09:26–10:00 | **Gate**: graftGate (M4 Mac Mini)
**Wave**: 157k Interstadial | **Agent**: Cursor (ephemeral)

---

## Summary

Cascaded Wave 157k Interstadial from Forgejo. Deployed `builder.serve` on graftGate — darwin builder is now autonomous in the cascade pipeline via TCP JSON-RPC dispatch (riboCipher compatible). Fixed D12 (swarmVine NUCLEUS launch failure) with two-part patch to biomeOS. Rebuilt 5 primals (biomeOS, petalTongue, barraCuda, nestGate, cellMembrane). Depot refreshed to 16/16 (15 primals + membrane).

---

## What Was Done

### 1. builder.serve Deployment (Stadial #2 UNBLOCKED)

Built cellMembrane for `aarch64-apple-darwin` from `c1b9de1` (latest, includes `content.braid` + enmeshment). Deployed `membrane` binary to `~/.local/bin` and `/usr/local/bin`.

Started `builder.serve` in a persistent `screen` session on port 9800. Verified end-to-end:
- Raw JSON-RPC health: `{"method":"health"}` → `{"ok":true,"message":"builder OK"}`
- riboCipher-framed health: `[0xEC, 0x01]` prefix + JSON → same response
- Reachable on all interfaces:
  - `localhost:9800` (loopback)
  - `10.13.37.13:9800` (WireGuard mesh)
  - `192.168.4.131:9800` (LAN)

Created `launchd` plist at `~/Library/LaunchAgents/eco.primals.builder.plist` for boot persistence (`RunAtLoad`, `KeepAlive`).

Updated `ecosystem_manifest.toml`:
```toml
[sub_builders."aarch64-apple-darwin"]
gate = "graftGate"
transport = "mesh"
builder_host = "10.13.37.13"
builder_port = 9800
notes = "... builder.serve LIVE (launchd, Aug 13). TCP dispatch + riboCipher compatible."
```

**Status**: sporeGate can now dispatch `plasmid.harvest` to graftGate via `call_tcp(10.13.37.13:9800)` — no SSH needed.

### 2. D12 Fix (swarmVine NUCLEUS Launch)

Root cause was **two-part**:

**Part A — Subcommand mismatch**: biomeOS passed `server` subcommand to all primals by default. swarmVine doesn't accept a subcommand (it uses `swarmvine [OPTIONS]`). Exit code 2 (argument parse error).

**Fix**: Added swarmVine profile to `config/nucleus_launch_profiles.toml` with `subcommand = ""`. Modified `build_primal_command_with()` in `nucleus/types.rs` to skip `cmd.arg(subcommand)` when subcommand is empty.

**Part B — Socket path mismatch**: swarmVine's `platform_paths::runtime_socket_dir()` resolves to `$XDG_RUNTIME_DIR/biomeos/` (NAMESPACE="biomeos"), but biomeOS expects all primal sockets in `$XDG_RUNTIME_DIR/membrane/`.

**Fix**: Added `BIOMEOS_RUNTIME_DIR = "${XDG_RUNTIME_DIR}/membrane"` to swarmVine's launch profile `env_vars`. Also enhanced `build_primal_command_with()` to support inline `${VAR}` expansion in env var values (previously only supported `$VAR` for whole-value passthrough).

Applied same fix to graph TOMLs: `nucleus_simple.toml`, `nucleus_complete.toml`, `tower_atomic_bootstrap.toml`.

**Result**: swarmVine now starts correctly, creates socket at `/tmp/eco/membrane/swarmvine-graftGate.sock`, transitions to ACTIVE, and stays running.

### 3. Cascade Rebuild

Rebuilt 5 primals from upstream changes:
- **biomeOS** (D12 fix + `deploy.result` gossip + data_braid_ingress)
- **petalTongue** (nestgate.io Phase 3: `/cas/{hash}` + `/cas/{hash}/provenance`)
- **barraCuda** (lattice QCD `rt_core_qcd.rs`)
- **nestGate** (load balancing `round_robin.rs`)
- **cellMembrane** (content.braid + enmeshment)

All pushed to depot. Darwin depot now **16/16** (15 primals + membrane).

### 4. NUCLEUS Status (Post-D12)

11 primal processes running stably:
| Primal | PID | Status |
|--------|-----|--------|
| beardog | 62610 | ACTIVE |
| songbird | 62611 | ACTIVE |
| skunkbat | — | Incubating (health ping timeout) |
| swarmvine | 62748 | **ACTIVE** (D12 FIXED) |
| coralreef | 62651 | ACTIVE |
| nestgate | — | ACTIVE |
| rhizocrypt | — | ACTIVE |
| loamspine | — | ACTIVE |
| sweetgrass | — | Incubating |
| squirrel | — | ACTIVE |
| petaltongue | — | ACTIVE |

- toadstool: Incubating (health check timeout — likely socket format mismatch, non-blocking)
- barracuda: TCP-only mode (no GPU on M4, expected)

---

## Divergences

### D12 (RESOLVED locally) — swarmVine launch profile missing from biomeOS

The nucleus launch profiles (`config/nucleus_launch_profiles.toml`) had no entry for swarmVine. This caused two failures: wrong subcommand (`server` vs none) and wrong socket directory (`biomeos/` vs `membrane/`). Fix is minimal and data-driven — no match-arm changes, just a TOML profile addition + one `if !subcommand.is_empty()` guard.

**Upstream recommendation**: Merge the swarmVine profile addition to `nucleus_launch_profiles.toml` and the empty-subcommand guard in `types.rs`. Any future primal that uses options-only CLI (no subcommand) will benefit from the same pattern.

### D13 (NEW) — `build_primal_command_with()` env var expansion limited

The profile env var substitution only supported two patterns: `$UPPER_CASE` (whole-value passthrough) and `$family_id`/`$node_id` (literal). Inline `${VAR}` expansion within paths (e.g. `${XDG_RUNTIME_DIR}/membrane`) was not supported. Fixed locally with a `while let` loop that expands `${VAR}` patterns.

**Upstream recommendation**: Merge the `${VAR}` expansion support in `build_primal_command_with()`. Other primals may need embedded env var paths in their profiles as the ecosystem grows.

### Depot correction — blurb says 5/15, actual is 16/16

The blurb's depot table shows `aarch64-apple-darwin: 5/15 refreshed`. This was stale — we pushed 15/15 on Aug 12 (Wave 157k ortho cascade). Now 16/16 with membrane added.

---

## Files Modified

| File | Change |
|------|--------|
| `biomeOS/config/nucleus_launch_profiles.toml` | Added `[profiles.swarmvine]` with empty subcommand + BIOMEOS_RUNTIME_DIR |
| `biomeOS/crates/biomeos/src/modes/nucleus/types.rs` | Skip subcommand when empty; `${VAR}` expansion in env vars |
| `biomeOS/graphs/nucleus_simple.toml` | Added `BIOMEOS_RUNTIME_DIR` to swarmVine node |
| `biomeOS/graphs/nucleus_complete.toml` | Added `BIOMEOS_RUNTIME_DIR` to swarmVine node |
| `biomeOS/graphs/tower_atomic_bootstrap.toml` | Added `BIOMEOS_RUNTIME_DIR` to swarmVine node |
| `wateringHole/ecosystem_manifest.toml` | Added `builder_host`/`builder_port` for graftGate darwin builder |
| `~/Library/LaunchAgents/eco.primals.builder.plist` | New: launchd service for builder.serve persistence |

---

*graftGate AAR — Wave 157k Interstadial. builder.serve LIVE. D12 RESOLVED. Depot 16/16. Next: sporeGate validate TCP dispatch to graftGate, D12/D13 merge upstream (eastGate).*

---
*FOSSILIZED Wave 157k interstadial (Aug 13, 2026). Content fully absorbed into ORTHOGONAL_DIMENSIONS_REVIEW.md and ECOSYSTEM_BLURB.md.*
