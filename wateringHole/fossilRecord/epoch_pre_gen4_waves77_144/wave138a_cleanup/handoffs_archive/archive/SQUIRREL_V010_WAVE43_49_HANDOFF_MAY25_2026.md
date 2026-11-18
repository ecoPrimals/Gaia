# Squirrel v0.1.0 — Waves 43-49 Handoff

**Date:** May 25, 2026
**From:** Squirrel team
**Scope:** Neural API announce, socket targeting, ecosystem tightening
**License:** AGPL-3.0-or-later

---

## Wave 43: Neural API `primal.announce` (May 23)

Added `announce_to_neural_api()` in `capabilities/lifecycle.rs`. On startup,
Squirrel sends `primal.announce` to biomeOS Neural API with full routing metadata:

- `capabilities`: `["inference", "mcp", "coordination"]`
- `signal_tiers`: `["meta"]`
- `cost_hints`: `{ "inference": 50.0, "mcp": 10.0, "coordination": 15.0 }`
- `latency_estimates`: `{ "inference": 500, "mcp": 20, "coordination": 30 }`
- `methods`: all 38 registered methods from `niche.rs`

Graceful degradation: if Neural API absent, announce fails at debug level.

## Wave 44: Neural API Socket Targeting Fix (May 23)

**Bug:** `announce_to_neural_api()` reused `find_biomeos_socket()` which targets
the orchestrator socket (`biomeos.sock`), not the neural-api socket.

**Fix:** Added `resolve_neural_api_socket()` with WAVE42 tiered lookup:
1. `$NEURAL_API_SOCKET`
2. `$XDG_RUNTIME_DIR/biomeos/neural-api-{family}.sock`
3. `$XDG_RUNTIME_DIR/biomeos/neural-api.sock`
4. `/tmp/biomeos/neural-api-{family}.sock`
5. `/tmp/biomeos/neural-api.sock`

Decoupled announce from lifecycle.register — runs independently even when
biomeOS orchestrator is absent.

## Wave 49: Ecosystem Tightening (May 25)

Squirrel was already clean (no showcase, no wateringHole, no deployment debt,
`notify-plasmidbin.yml` active). Additional cleanup performed:

- **Doc unification**: Test count synced to 7,093 across README, CONTEXT,
  CURRENT_STATUS, sporeprint.
- **Build path modernization**: Replaced `./target/release/squirrel` with
  `cargo run -p squirrel --` / `just build-ecobin` in README. Fixed musl
  target path in Docker example.
- **Spec archival**: Moved gen2-era MCP protocol specs, deployment guide,
  testing guide, and security guide to `specs/historical/`. These are
  preserved as fossil record but no longer active.
- **Code nit**: `#[allow(dead_code)]` → `#[cfg_attr(not(test), allow(dead_code))]`
  for `socket_path` field (used in tests, dead in prod builds).

---

## Quality Gates

| Gate | Result |
|------|--------|
| `cargo fmt --all` | PASS |
| `cargo clippy -D warnings` | 0 warnings |
| `cargo test --workspace --lib --tests` | 7,093 pass / 0 fail |
| `cargo deny check` | advisories ok, bans ok, licenses ok, sources ok |

## Commits

- `bfb1e2f5` — primal.announce with Neural API routing metadata (Wave 43)
- `a7753bac` — fix: target neural-api socket for primal.announce (Wave 44)
- (pending) — Wave 49 ecosystem tightening: docs + spec archival
