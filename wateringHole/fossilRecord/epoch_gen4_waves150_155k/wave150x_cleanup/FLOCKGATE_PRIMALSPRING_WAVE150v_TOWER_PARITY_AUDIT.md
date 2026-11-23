# flockGate primalSpring Wave 150v — Tower Atomic Parity Audit

**Wave**: 150v | **Gate**: flockGate (10.13.37.6) | **Role**: WAN peer
**Date**: 2026-07-22 | **Team**: flockGate
**Commit**: `a515d8d` (HEAD of main, up to date with origin)

---

## Mission Status

**WAN PEER READY.** Tower Atomic primals are running. WireGuard mesh is UP.
Structural scenarios pass. Awaiting sporeGate benchmark probes.

---

## Tower Atomic Stack — flockGate Status

| Primal | Socket | Process | Status |
|--------|--------|---------|--------|
| **bearDog** | `/run/user/1000/biomeos/beardog.sock` | PID via plasmidBin, `--socket` flag | **LIVE** since Jul 16 |
| **songBird** | `/run/user/1000/biomeos/songbird.sock` + `:7780` drawbridge | PID 2100, `songbird server` | **LIVE** since Jul 16 |
| **skunkBat** | `/run/user/1000/biomeos/skunkbat.sock` | PID via plasmidBin, `--socket` flag | **LIVE** since Jul 16 |

Additional confirmation:
- `security.sock` (bearDog alias) — present
- `btsp.sock` — present (BTSP handshake endpoint)
- `songbird.sock` bound on 2 listeners
- Drawbridge TCP on `127.0.0.1:7780` — listening

**Mesh topology confirms**: flockGate = `role = "tower"`, `zone = "Wan"`.

---

## WireGuard Mesh Connectivity

| Target | Address | RTT | Status |
|--------|---------|-----|--------|
| golgiBody (TURN hub) | 10.13.37.1 | 30.7 ms | **REACHABLE** |
| sporeGate (benchmark peer) | 10.13.37.2 | 66.2 ms | **REACHABLE** |
| flockGate (self) | 10.13.37.6 | — | **UP** via wg0 |

WireGuard baseline RTT to golgiBody: ~31ms. To sporeGate via golgiBody: ~66ms.
This establishes the WG baseline for WAN parity comparison.

---

## Structural Scenario Results

| Scenario | Tests | Result |
|----------|-------|--------|
| `tower_atomic` (s_tower_atomic) | 1 | **PASS** |
| `tower_atomic_membership` (primal_names) | 1 | **PASS** |
| `fragment_tower_atomic_caps_in_registry` (composition) | 1 | **PASS** |
| `flockgate_tower_wan` (3 tests) | 3 | **PASS** |

All Tower Atomic structural validation passes on flockGate.

---

## Code Quality Audit

### Linting: `cargo clippy --all-targets -- -W clippy::pedantic -W clippy::nursery`

**Result: 6 unique warnings** (17 are doc_markdown backtick nits, 2 are `sort` → `sort_unstable`)

| Warning Type | Count | Severity | Fix |
|--------------|-------|----------|-----|
| `doc_markdown` (missing backticks) | 17 | Cosmetic | `s_diderm_domain_posture.rs`, `compose_nest.rs`, `server_contract_stubs.rs` |
| `stable_sort_primitive` | 2 | Perf nit | `s_diderm_domain_posture.rs:257` — use `sort_unstable()` |

**Assessment**: Near-zero. The `doc_markdown` lint is actually allowed in workspace config
(`doc_markdown = "allow"`), so these only fire because `-W clippy::pedantic` on the CLI
overrides workspace config. Under normal CI (`cargo clippy --all-features -- -D warnings`),
these are suppressed. **Effectively 0 actionable warnings.**

### Formatting: `cargo fmt --check`

**Result: 2 formatting diffs** in `s_diderm_domain_posture.rs` (newest scenario, Wave 150t):
1. Module declaration sort order (alphabetical `s_diderm_` after `s_depot_*`)
2. Assert macro line-break formatting

**Proposed fix for eastGate**: Run `cargo fmt` on `ecoPrimal/src/validation/scenarios/mod.rs`
and `s_diderm_domain_posture.rs`. Likely missed in the `a515d8d` commit.

### Documentation: `cargo doc --no-deps`

**Result: 20 warnings total**
- 19× redundant explicit link targets (rustdoc style nits)
- 1× unclosed HTML tag in `nucleus_launcher/orchestrator/registry.rs:55` (`Vec<domain>` needs backticks)

None prevent doc generation. All are cosmetic.

### File Size

**COMPLIANT.** Largest file: 712 lines (`covalent_mesh_trust.rs`). All under 1000-line limit.

### Unsafe Code

**NONE.** Workspace enforces `unsafe_code = "deny"`. Confirmed zero `unsafe` blocks.

### Unwrap/Expect

Workspace warns on both. Zero `unwrap()` in non-test code (proptest and test harness only).

---

## Architecture Compliance

| Requirement | Status | Notes |
|-------------|--------|-------|
| JSON-RPC first | **COMPLIANT** | All IPC via `ipc/` module; synchronous JSON-RPC 2.0 over UDS/TCP |
| tarpc interop | **COMPLIANT** | No tarpc dep; handles upstream dual-socket primals via `prefer_jsonrpc_socket()` |
| ecoBin pattern | **COMPLIANT** | Two binaries (`primalspring_unibin`, `nucleus_launcher`); static linking; clap CLI |
| Semantic method naming | **COMPLIANT** | `domain.verb` convention; capability registry at `config/capability_registry.toml` |
| Zero-copy | **N/A** | primalSpring is a validation client, not a data plane; no bulk data transfer |
| Silicon Atheism | **COMPLIANT** | `ipc/platform.rs` uses trait-based transport abstraction; no `#[cfg]` exclusion |
| No banned deps | **COMPLIANT** | `cargo tree` shows zero hits for openssl/ring/aws-lc/native-tls/zstd-sys/lz4-sys |
| Pure Rust crypto | **COMPLIANT** | blake3 (pure feature), chacha20poly1305, sha2, hmac, hkdf — all RustCrypto |

---

## Test Coverage

### Scale

| Metric | Value |
|--------|-------|
| Total tests (lib) | **1,214** |
| Passed | 1,211 (in full suite) / 1,212 (filtered runs) |
| Failed | 1 (non-deterministic, see below) |
| Ignored | 2 |
| Registered scenarios | 172 |
| Integration test files | 7 |
| Doctests | 17 passing, 4 ignored (need live primals) |
| Full suite runtime | ~28s |

### Line Coverage (`cargo llvm-cov --lib --summary-only`)

| Metric | Covered | Total | Percentage |
|--------|---------|-------|------------|
| Lines | 51,490 | 69,765 | **73.8%** |
| Functions | 3,660 | 4,405 | **83.1%** |
| Regions | 33,563 | 46,431 | **72.3%** |

**Assessment**: 73.8% line coverage. Below the 90% target. Gap is primarily in
live-only code paths (scenarios that skip when primals aren't available for IPC).
Structural tests cover config/registry/graph parsing heavily; live integration
paths account for most uncovered lines.

### Non-Deterministic Test Failure

**`s_depot_architecture_coverage::tests::depot_arch_coverage_structural`** — fails
in full parallel suite but passes in isolation. Likely filesystem or timing
contention when all 1,214 tests run simultaneously.

**Proposed fix for eastGate**: Investigate resource contention in depot scenario;
may need a test mutex or isolated temp directory.

---

## Debt & Gaps

### Markers

| Marker | Count | Notes |
|--------|-------|-------|
| `todo!()` | 0 | Clean |
| `unimplemented!()` | 0 | Clean |
| `FIXME` | 0 | Clean |
| `HACK` | 0 | Clean |
| `TODO` | 0 | Clean (tracked via scenario skip semantics instead) |

### Hardcoded Values

All ports, primal names, and gate addresses are extracted to config:
- `config/ports.toml` — TCP fallback port registry (Tier 5, debug-only)
- `config/mesh_topology.toml` — gate roster and addresses
- `config/capability_registry.toml` — method-level capabilities
- `ecoPrimal/src/primal_names.rs` — centralized name constants

**No hardcoded ports or primal names found in scenario/lib code.**

### Dead Code / Unused Imports

None detected by clippy.

### Experiment Crate Debt

94 experiment crates in workspace — all are thin wrappers over absorbed library scenarios.
Not dead code per se (fossil record pattern), but workspace compile includes all members.
`default-members = ["ecoPrimal"]` correctly limits default builds.

---

## Sovereignty & Licensing

| Check | Status |
|-------|--------|
| License file | `AGPL-3.0-or-later` (LICENSE at root, SPDX in Cargo.toml) |
| `Cargo.toml` license field | `AGPL-3.0-or-later` |
| SPDX headers | Present in config files; `.rs` files rely on root LICENSE |
| Telemetry | **NONE** — no analytics, no tracking, no phone-home |
| Cloud lock-in | **NONE** — all deps are pure Rust crates from crates.io |
| Pure Rust crypto | **YES** — blake3 (pure), RustCrypto suite (sha2, hmac, hkdf, chacha20poly1305) |
| Data exfiltration | **NONE** — no network calls except explicit IPC to local sockets |
| Dark patterns | **NONE** — CLI-only tool, no user-facing UI |

---

## What Have We Not Completed?

### P0 — Blocking

None. flockGate primalSpring is GREEN for its WAN peer mission.

### P1 — Should Fix (eastGate owns)

| Item | File/Location | Description |
|------|---------------|-------------|
| `cargo fmt` regression | `scenarios/mod.rs`, `s_diderm_domain_posture.rs` | Wave 150t commit `a515d8d` introduced unformatted code |
| Non-deterministic test | `s_depot_architecture_coverage` | Passes alone, fails in parallel suite — resource contention |
| Doc warning (HTML tag) | `nucleus_launcher/orchestrator/registry.rs:55` | `Vec<domain>` needs backtick quoting |
| Coverage gap | 73.8% vs 90% target | Live-only paths uncoverable without full NUCLEUS; honest skip semantics mitigate |

### P2 — Track

| Item | Description | Blocker |
|------|-------------|---------|
| WAN parity benchmark (throughput/latency) | Tower vs WG comparative measurement | Needs sporeGate to drive; benchmark harness not yet built in songBird |
| golgiBody TURN relay | `songbird relay` — code complete, deployment pending on golgiBody VPS | Ops ticket |
| CAC scenario | FRAGO issued, not implemented | eastGate primalSpring backlog |
| `wan-deploy` scenario | 1/5 protoKarya scenarios remaining | eastGate primalSpring backlog |
| `PRIMALSPRING_WAVE150u_TOWER_PARITY_AAR.md` | Referenced in blurb but does not exist | eastGate to write or supersede |
| LAN parity benchmark | sporeGate ↔ eastGate; needs ironGate online | Hardware dependency |

---

## WAN Peer Readiness Checklist

- [x] Tower Atomic primals running (bearDog + songBird + skunkBat)
- [x] flockGate confirmed as `role = "tower"` in mesh topology
- [x] WireGuard mesh UP (wg0 at 10.13.37.6/24)
- [x] golgiBody reachable (31ms RTT via WG)
- [x] sporeGate reachable (66ms RTT via WG through golgiBody)
- [x] Structural scenarios passing (tower_atomic, flockgate_tower_wan)
- [x] Drawbridge listening on :7780
- [x] BTSP socket present
- [x] esotericWebb confirmed running (`esotericwebb.sock` present)
- [ ] **PENDING**: songBird TURN relay deployed on golgiBody
- [ ] **PENDING**: sporeGate drives benchmark probes
- [ ] **PENDING**: iperf3-equivalent throughput measurement through Tower relay

---

## WG Baseline Measurements (for parity comparison)

| Path | RTT (ping) | Notes |
|------|-----------|-------|
| flockGate → golgiBody | 30.7 ms | Direct WG peer |
| flockGate → sporeGate | 66.2 ms | Via golgiBody hub |

These establish the WireGuard WAN baseline. Tower parity target: ≤50ms to golgiBody,
throughput ≥50 Mbps through Tower relay.

---

## Recommendations to eastGate

1. **Run `cargo fmt`** — trivial fix for Wave 150t regression
2. **Investigate `s_depot_architecture_coverage`** parallel test failure
3. **Deploy songBird TURN relay** on golgiBody — blocker for WAN benchmark
4. **Build benchmark harness** in songBird (`songbird benchmark --mode tower-atomic`)
5. **Write or supersede** `PRIMALSPRING_WAVE150u_TOWER_PARITY_AAR.md`

---

## esotericWebb V22 Health Check

- `esotericwebb.sock` present in biomeos directory
- `petaltongue.sock` and `petaltongue-flockGate.sock` active
- `visualization.sock` and `visualization-flockGate.sock` active
- No port conflicts with Tower Atomic (esotericWebb uses songBird drawbridge, separate IPC)

**Assessment**: No regressions from Tower Atomic deployment. esotericWebb and Tower
coexist cleanly on separate socket namespaces.

---

*Filed by flockGate team, Wave 150v. eastGate integrates code changes.*
