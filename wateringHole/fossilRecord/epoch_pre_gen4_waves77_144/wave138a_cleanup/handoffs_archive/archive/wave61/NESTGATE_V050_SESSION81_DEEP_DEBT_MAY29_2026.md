# NestGate v0.5.0 — Session 81: Deep Debt Sweep (May 29, 2026)

## Summary

Module split, honest metrics, 501 endpoint evolution, and coverage push.
Follows Session 80 (content federation) in the same day.

## Changes

### P0 — Module split
- `content_federation_handlers.rs` (937L) split into:
  - `content_federation_handlers.rs` (525L) — 4 public handler entry points + blob replication
  - `federation_ops.rs` (430L) — git operations, repo sync, JSON-RPC transport helpers
- Both files well under the 800-line workspace limit

### P1 — Honest metrics
- `ZERO_COST_PLACEHOLDER_REQUESTS_PROCESSED` (fake 1000) → `ZERO_COST_REQUESTS_NOT_TRACKED` (0)
- `ZERO_COST_PLACEHOLDER_AVERAGE_LATENCY_NS` (fake 50,000) → `ZERO_COST_LATENCY_NOT_TRACKED` (0)
- Const-fn stack cannot track runtime state — returning fabricated data was misleading
- Tests updated to assert honest zeroes

### P0 — 501 endpoint evolution
- 8 ZFS REST not-implemented endpoints now return structured JSON:
  - `"code": "NOT_IMPLEMENTED"` for machine-parseable status
  - `"hint"` directing callers to capability-based discovery

### P1 — Coverage push (21 new tests)
- `linux_proc.rs`: 14 tests — memory, CPU, disk, network, uptime, load, kernel, statvfs
- `content_ops.rs`: 7 tests — put/get roundtrip, exists, list, federation error paths

### P2 — Scaffold cleanup
- `discovery/config/network.rs`: removed WILL PROVIDE/PLACEHOLDER comments

### Doc hygiene (Session 81b)
- 9 root docs synchronized to Session 81 (12,500 tests, May 29, 2026)
- CAPABILITY_MAPPINGS.md: content domain expanded from 8 → 12 methods
- Legacy benches archived (9 root `benches/*.rs` files)
- Stale mDNS/Consul discovery docs cleaned

## Verified clean
- `ZfsManager::mock()` already `#[cfg(any(test, feature = "dev-stubs"))]`
- Zero TODO/FIXME/HACK in production code
- Zero `#[allow(...)]` in production code (only `#[expect]` with reasons)
- All external deps pure Rust (no C/FFI)

## Metrics
- **Tests**: 12,500 passing (up from 12,479)
- **Coverage**: 83.61%+ line
- **Clippy**: 0 warnings (workspace, -D warnings)
- **Files > 800L**: 0 in production code (down from 1)

## Remaining debt (downstream audit targets)
- 8 ZFS REST 501 endpoints exist but have no backing implementation
- `specs/` has ~261 unchecked implementation checklist items
- `docs/guides/ENVIRONMENT_VARIABLES.md` still references mDNS discovery backend
- Coverage target 90% not yet reached
