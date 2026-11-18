# biomeOS v3.88 — Wave 63 Deep Cleanup

**Date**: May 29, 2026  
**From**: biomeOS team  
**To**: primalSpring coordination  
**Wave**: 63 (PostPrimordial → Glacial Shift)

---

## Scope

JSON parse observability, silent error elimination, env var SSOT expansion, service/core refactor, rootpulse centralization, stale test removal.

---

## Changes

- 4 JSON parse probe sites → `debug!` logging (`cap_probe`, `topology`, `endpoint_probe`, `ai_advisor`)
- 11 HIGH `unwrap_or_default` sites → `warn!`/`debug!` with error context
- BTSP handshake field validation (empty strings → explicit errors)
- Neural API connection serialization failures → `warn!` + JSON-RPC -32603
- Federation discovery/verification: missing result field → `debug!` + graceful degrade
- 3rd TMPDIR regression fixed (`continuous.rs`)
- 18 env var call sites wired to `env_config::vars` constants
- 11 new constants added to `env_config::vars`
- `service/core.rs` split: 795→564L (`status.rs` + `scaling.rs` extracted)
- `ROOTPULSE` added to `primal_names` + display names + `niche.rs` wired
- Hardcoded `"biomeos"` in capability taxonomy → `primal_names::BIOMEOS`
- Root `tests/` directory deleted (75 stale integration tests with disconnected wiremock mocks)
- 3 orphan duplicate test files deleted (`primal_registry_tests.rs`, `node_tests.rs`, `health_tests.rs`)
- 11 unregistered example files deleted (never compiled by Cargo)
- 15 commented-out Cargo.toml dependency lines removed (reqwest, dirs, benchscale, etc.)
- 6 empty `[features]` blocks removed from crate Cargo.tomls
- All root docs synced to v3.88 / 7,983 tests
- `cargo clean` reclaimed 34.5 GiB

---

## Stats

- 7,983 tests, 0 failures, 0 warnings, 0 unsafe blocks
- -2,574 lines in debris cleanup pass

---

## Remaining

- Cross-Gate `graph.execute` Phase B (Wave 65 target)
- Further env var centralization for lower-traffic `BIOMEOS_*` vars

---

## Commits

- `82501658` — JSON parse observability, stale test cleanup, service/core split
- `d8a6039a` — BTSP field validation, silent error logging, env var SSOT expansion
- `cf0f6b57` — HIGH unwrap_or_default elimination, rootpulse primal_names
- `95cd7903` — docs: consolidate v3.88 Wave 63 entry
- `d45e1e0a` — doc sync v3.88, orphan/debris cleanup, Cargo.toml hygiene
