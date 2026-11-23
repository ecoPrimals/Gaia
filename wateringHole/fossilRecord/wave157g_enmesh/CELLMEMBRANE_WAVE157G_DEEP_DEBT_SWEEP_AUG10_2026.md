# cellMembrane — Wave 157g Deep Debt Sweep

**Date:** 2026-08-10
**Wave:** 157g (continuation)
**From:** eastGate overwatch
**Scope:** Error handling hardening, module extraction, constant consolidation, NUCLEUS lifecycle extraction

---

## What Was Done

### P1: Silent Error Suppression Fixed

5 `let _ =` on real I/O operations replaced with `if let Err(e)` + tracing:

| File | Operation | Risk mitigated |
|------|-----------|---------------|
| `plasmid/harvest.rs` | `pkill` fallback | Stale processes lingering after NUCLEUS restart |
| `plasmid/harvest.rs` | `archive_superseded_binary` | Depot lineage audit trail silently dropped |
| `gate/nucleus.rs` | PID file write | Bare-process lifecycle impaired if PID missing |
| `plasmid/mod.rs` | `apply_access_async` on socket dir | Socket dir untraversable (0755 requirement) |
| `tower/timer.rs` | `PlatformAccess::Executable` on script | Benchmark script not executable |

### P1: IPC Error Visibility

- `sync_ipc.rs` `ipc_request`/`ipc_request_plain`: 6 `.ok()?` swallowed errors replaced with per-operation `tracing::debug!` (write, shutdown, read each logged)
- `nucleus.rs` CSPRNG failure now logs before returning `None`
- `http_client.rs`: 4 `map_err(|_|` patterns restored to `map_err(|e|` preserving parse/timeout context
- `context.rs` + `impulse/lifecycle.rs`: JoinError panic messages enriched with error detail

### P2: Module Extraction

**health.rs (738L → 519L + 236L):**
- `gate/health.rs` → `gate/health/mod.rs` (orchestrator + mesh probes + primal sweep)
- `gate/health/auxiliary.rs` (depot freshness, VCS parity, rootpulse ledger, TLS cert expiry)

**harvest.rs (788L → 657L + 148L):**
- `install_and_restart()` + `atomic_copy_binaries()` → `plasmid/harvest_install.rs`
- NUCLEUS stop/pkill/copy/restart is a self-contained lifecycle domain

### P2: Constant Consolidation

| Hardcoded | Replaced with |
|-----------|--------------|
| `"/opt/forgejo/data/gitea-repositories"` | `DEFAULT_FORGEJO_DATA_DIR` + suffix |
| `"/proc/sys/kernel/hostname"` | `PROC_HOSTNAME` (gate/mod.rs) |
| `"/etc/hostname"` | `ETC_HOSTNAME` (gate/mod.rs) |
| `"/etc/NetworkManager/conf.d/..."` | Local `const NM_UNMANAGE_CONF` |
| `"cellmembrane"` in `is_post_primordial()` | `MEMBRANE_BINARY` constant |
| `"songBird"` in transport error | Generic "relay primal" |

---

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Files >800L | 1 (harvest.rs 788L) | **0** |
| Files >700L | 3 | **2** (fetch.rs 735L, constants.rs 731L) |
| Clippy warnings | 0 | 0 |
| Tests | 1350+ | 1350+ (all pass) |
| `let _ =` on real I/O | 5 data-loss risk | **0** data-loss risk |
| `.ok()?` silent IPC | 6 | **0** (all logged) |
| `map_err(|_|` discarding errors | 4 HTTP client | **0** |
| Production `unwrap()` | 0 | 0 |
| Unsafe code | 0 (`#![forbid]`) | 0 |

---

## Commits

1. `2486b1a` — `evolve: deep debt sweep — error handling + health module extraction + constant consolidation`
2. `2046756` — `evolve: extract NUCLEUS install lifecycle from harvest.rs`

---

## Upstream Notes

- **All primals**: No API changes. Internal error handling only.
- **Overwatch**: Zero files >800L target achieved across entire codebase.
- **G72 posture**: Tier 1 complete (previous commit). This wave adds error quality depth.
- **Remaining debt**: `fetch.rs` (735L) and `constants.rs` (731L) are natural sizes for their domains — no forced split needed.
