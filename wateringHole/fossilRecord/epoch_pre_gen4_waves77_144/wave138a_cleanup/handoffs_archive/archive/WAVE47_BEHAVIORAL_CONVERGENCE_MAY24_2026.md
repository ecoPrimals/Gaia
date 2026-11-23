# Wave 47 — Post-Primordial Behavioral Convergence

**Date**: May 24, 2026
**From**: primalSpring v0.9.28 (coordination)
**To**: All primal teams
**Priority**: HIGH — deployment behavior mismatches are now the primary debt

---

## Context

We are post-primordial. All 13 primals are at zero internal debt, 12/12
announcing, 13/13 BTSP Phase 3. Five springs are deploying NUCLEUS
compositions on LAN gates. The remaining friction is **behavioral
divergence** in how primals present their CLI, health endpoints, and socket
interfaces to the deployment system.

`plasmidBin/start_primal.sh` currently maintains per-primal workaround
blocks for CLI differences. This is fragile. We've published
`DEPLOYMENT_BEHAVIOR_STANDARD.md` (primalSpring wateringHole) defining the
target contract. This blurb contains the per-primal action items.

---

## Per-Primal Action Items

### nestgate — 2 items (LOW effort each)

1. **Add `--socket PATH` CLI flag** to the `server`/`daemon` subcommand.
   Currently env-only (`NESTGATE_SOCKET`). The flag should set the same
   internal value. Every other primal with UDS accepts `--socket`.

2. **Normalize `health.liveness` response** to `{"status":"alive"}`.
   Currently returns `{"alive":true}` on some transport paths (missing
   `"status"` field). The health sweep checks `jq -r .status`.

### barraCuda — 1 item (LOW effort)

1. **Alias `--socket` to `--unix`** in clap. barraCuda already supports
   `--unix PATH` for UDS. Adding `--socket` as an alias (or `visible_alias`)
   lets the generic launcher pass `--socket` uniformly.

### rhizoCrypt — 1 item (LOW effort)

1. **Alias `--socket` to `--unix`** in clap. Same pattern as barraCuda.

### coralReef — 2 items (LOW effort each)

1. **Add `--socket PATH` CLI flag** to `server`. Currently auto-resolves
   UDS path from `$XDG_RUNTIME_DIR`. Adding explicit `--socket` lets the
   launcher control placement.

2. **Normalize `health.liveness` response** to `{"status":"alive"}`.
   Currently returns `{"alive":true}` without a `"status"` field.

### skunkBat — 4 items (LOW effort each)

1. **Add `--socket PATH` CLI flag** to `server`. Currently auto-resolves
   from BtspConfig.

2. **Add `lifecycle.status` method**. Only primal missing it. Return
   `{"primal":"skunkbat","version":"<ver>","status":"running"}`.

3. **Handle SIGTERM** (not just SIGINT). Current `tokio::select!` only
   awaits `ctrl_c()`. Add `tokio::signal::unix::signal(SignalKind::terminate())`.

4. **Align default TCP port** to 9750 (code has 9140, `ports.env` has 9750).

### loamSpine — 1 item (HIGH effort, CRITICAL)

1. **Fix Tokio double-runtime crash** on NUCLEUS start. This is the only
   hard blocker — it prevents southGate from running a full composition.
   loamSpine panics when started by `nucleus_launcher.sh` because something
   in its startup path creates a nested Tokio runtime.

### biomeOS — 1 item (LOW effort)

1. **Normalize `health.liveness`** on the `api` UDS socket to return
   `{"status":"alive"}` instead of `{"status":"healthy"}`. The neural-api
   socket already returns `"alive"` — the api socket should match.

### petalTongue — DONE (May 24, 2026)

1. ~~**Add explicit SIGTERM handler**~~ — **DONE** (`src/signal.rs` shared
   module, `shutdown_signal()` for SIGTERM + SIGINT, wired into all 3
   long-running modes via `with_graceful_shutdown` / `tokio::select!` /
   spawned task).
2. **Bonus**: `health.liveness` normalized to `{"status":"alive"}` on both
   HTTP and IPC (removed legacy `"alive":true` field).
3. **Bonus**: Deep debt resolved — web_mode refactored (1136→3 files),
   BTSP BEARDOG overstep removed, NestGate evolved to capability-based
   `content_backend`, Display V1 + provenance trio discovery rewired.

### toadStool — 1 item (LOW effort)

1. **Return instant `health.liveness`** during boot. Currently returns
   `{"status":"starting"}` which fails the `== "alive"` check in health
   sweeps. Consider returning `"alive"` immediately and using a separate
   `health.ready` for boot-complete signaling.

---

## What plasmidBin Fixed

- **skunkBat**: `serve` → `server` subcommand in `start_primal.sh`
- **rhizoCrypt**: `--socket` → `--unix` mapping in launcher (later removed — primal now accepts `--socket`)
- **barraCuda**: `--socket` → `--unix` mapping, proper `--bind` forwarding (later removed — primal now accepts `--socket`)
- **petalTongue**: `--socket` forwarded to `server` mode
- **coralReef**: `CORALREEF_SOCKET` env export for UDS path control (later removed — primal now accepts `--socket`)

## Epilogue — FULLY RESOLVED (May 24, 2026)

**All 13 primals converged.** The workarounds listed above have been **removed**
from `start_primal.sh` — the launcher now passes `--socket` uniformly to all
primals. The `add_standard_flags()` helper replaced per-primal boilerplate.
Net: -20 lines in the launcher, zero behavioral change.

This handoff is **CLOSED**. No remaining action items.

---

## Reference

- Standard: `primalSpring/wateringHole/DEPLOYMENT_BEHAVIOR_STANDARD.md`
- Launcher: `plasmidBin/start_primal.sh` (simplified post-convergence)
- Health sweep: `plasmidBin/nucleus_launcher.sh` Phase 4
- Gate deployment reports: `infra/wateringHole/handoffs/` (May 23 handoffs)
