# primalSpring Wave 150v — sporeGate Tower Atomic Parity Audit

**Date**: 2026-07-22 | **Wave**: 150v | **Gate**: sporeGate (10.13.37.2)
**Role**: Backbone LAN peer — benchmark runner (NOT code evolver)
**Version**: primalSpring v0.9.42 | **Commit**: `1ab0bfea` (Tower Atomic parity scenario)

---

## Mission Status

| Step | Status | Detail |
|------|--------|--------|
| 1. Audit dimensions | **COMPLETE** | All 5 dimensions assessed — report below |
| 2. Review convergence brief | **COMPLETE** | `TOWER_ATOMIC_CONVERGENCE.md` (songBird) reviewed |
| 3. Verify Tower primals | **COMPLETE** | 3/3 LIVE on sporeGate (bearDog, songBird, skunkBat) |
| 4. Structural scenario | **COMPLETE** | `tower-atomic-parity` 21/21 GREEN |
| 5. WAN parity benchmark | **BLOCKED** | Needs TURN relay on golgiBody + benchmark harness |
| 6. LAN parity benchmark | **DEFERRED** | ironGate offline |

---

## 1. Code Quality

| Check | Result | Detail |
|-------|--------|--------|
| `cargo clippy --all-targets` | **0 warnings** | pedantic + nursery via `[workspace.lints.clippy]` |
| `cargo fmt --check` | **CLEAN** | No formatting violations |
| `cargo doc --no-deps` | **20 warnings** | 19 `doc_markdown` false positives (ecosystem terms) + 1 unclosed HTML tag |
| `unsafe` code | **ZERO** | `#![forbid(unsafe_code)]` on lib.rs root; only doc mentions |
| File sizes | **ALL <1000L** | Max: 712 lines (`covalent_mesh_trust.rs`). 299 files, avg 287 lines |
| TODO/FIXME/HACK | **ZERO** | No markers in any source file |
| `.unwrap()` in prod code | **ZERO** | Clippy `unwrap_used = "warn"` passes clean; unwraps confined to `#[cfg(test)]` |
| Dependencies | **LEAN** | 12 direct deps, all Pure Rust (blake3 `pure`, chacha20poly1305, no openssl/ring) |

### Doc Warning Detail (for eastGate — low priority)

19 of 20 are `doc_markdown` on ecosystem terms (BearDog, NestGate, UniBin) already
`allow`-ed in workspace config but re-triggered when `-W clippy::pedantic` is passed
on command line. 1 genuine warning:

- `ecoPrimal/src/bin/nucleus_launcher/orchestrator/registry.rs:55` — unclosed HTML tag
  `Vec<domain>` should be `` `Vec<domain>` ``

**Proposed fix** (for eastGate to ship):

```rust
// Line 55, registry.rs:
// FROM: /// this to build a primal → Vec<domain> mapping for discovery-provider seeding.
// TO:   /// this to build a primal → `Vec<domain>` mapping for discovery-provider seeding.
```

---

## 2. Architecture Compliance

| Standard | Status | Evidence |
|----------|--------|----------|
| JSON-RPC 2.0 + tarpc | **COMPLIANT** | `ipc/protocol.rs` implements JSON-RPC 2.0; `ipc/client.rs` for dispatch |
| ecoBin | **COMPLIANT** | Two binaries: `primalspring_unibin` (CLI) + `nucleus_launcher` (orchestrator) |
| Semantic method naming | **COMPLIANT** | Registry validation (`s_domain_contract_sweep`, `s_skunkbat_method_gate`) |
| Zero-copy | **COMPLIANT** | `Bytes`/`&[u8]` patterns in transport; `zeroize` for secrets |
| Silicon Atheism | **COMPLIANT** | `ipc/platform.rs` trait-based abstraction (no `#[cfg]` exclusion) |
| Single-binary | **COMPLIANT** | `primalspring_unibin` serves CLI + validation; no shared libraries |

---

## 3. Test Coverage

| Metric | Value |
|--------|-------|
| Lib tests | **1,214 passed**, 0 failed, 2 ignored |
| Scenarios | 173 (registered in `scenarios/registry.rs`) |
| Line coverage | **75.63%** (70,195 regions, 53,091 covered) |
| Function coverage | **84.34%** (4,419 functions, 3,727 covered) |
| Branch coverage | **73.95%** (46,692 branches, 34,529 covered) |
| Coverage target gap | **-14.37pp** below 90% target |

### Coverage Analysis

75.63% is respectable for a validation/harness crate — much of the uncovered code
is in Live-tier scenario paths that require running primals (can't execute during
`cargo test --lib`). The structural (Tier::Rust) paths have near-100% coverage.
Files with lowest coverage are scenario files with Live-tier probe branches that
skip when primals aren't running.

### Test Tiers Present

| Tier | Present | Examples |
|------|---------|---------|
| Unit | **YES** | Every module has `#[cfg(test)] mod tests` |
| Integration | **YES** | `tests/compose_*.rs`, `tests/server_*.rs` (5 files) |
| E2E / Scenario | **YES** | 173 scenarios with structural + live tiers |
| Property-based | **YES** | proptest in `ipc/proptest_ipc.rs`, dev-dep `proptest = "1.10.0"` |
| Chaos/fault injection | **PARTIAL** | `s_gate_failure`, `s_chaos_substrate` (experiment) |

---

## 4. Debt & Gaps

### Markers: ZERO

No `todo!()`, `unimplemented!()`, `FIXME`, `HACK`, or `TODO` in any source file.

### Hardcoded Values

IP addresses (`10.13.37.*`) and ports (`:7780`, `:7700`) appear in ~25 scenario
files. These are **validation targets**, not production config — they reference the
mesh topology being validated. All production config comes from `config/mesh_topology.toml`
and `config/capability_registry.toml` via `include_str!`. **No action needed.**

### KNOWN_DEBT (from Wave 150t handoff)

| Scenario | Failures | Reason |
|----------|----------|--------|
| `graphenegate-readiness` | 1 | aarch64 depot directory absent on dev gate |
| `composition-access-control` | 15 | Access layer not yet wired |

**Total known debt**: 2 scenarios, 16 failures — all upstream blockers, not primalSpring code issues.

### Dead Code

None detected. Clippy's dead-code lint passes clean. All modules are `pub mod` from `lib.rs`.

---

## 5. Sovereignty & Licensing

| Check | Status | Evidence |
|-------|--------|---------|
| License header | **AGPL-3.0-or-later** | `Cargo.toml` workspace, `LICENSE` file, SPDX on every `.rs` |
| `#![forbid(unsafe_code)]` | **YES** | lib.rs line 4 |
| No telemetry | **CLEAN** | No analytics, tracking, or phone-home code |
| No cloud lock-in | **CLEAN** | No vendor SDKs, no proprietary dependencies |
| Pure Rust crypto | **YES** | blake3 (pure), chacha20poly1305, hmac, sha2, hkdf, zeroize — all RustCrypto |
| Human dignity | **CLEAN** | No dark patterns, no surveillance, no data exfiltration |
| No openssl/ring | **CLEAN** | Neither in dependency tree |

---

## 6. Tower Atomic Primals — sporeGate Runtime Status

### All 3/3 LIVE

| Primal | PID | Socket | Port | Status |
|--------|-----|--------|------|--------|
| bearDog | 602114, 2031811 | `/run/membrane/beardog.sock`, `/run/membrane/beardog-default.sock` | — | **LIVE** |
| songBird | 3670139 | `/run/membrane/songbird.sock`, `/tmp/songbird.sock` | :7780 (drawbridge), :7700 (federation) | **LIVE** (systemd `songbird-gateway.service`) |
| skunkBat | 868 | `/run/membrane/skunkbat.sock` | — | **LIVE** |

### Deployment Source

All binaries from `~/.local/share/ecoPrimals/plasmidBin/primals/x86_64-unknown-linux-musl/`.

### songBird Configuration

```
songbird server \
  --socket /run/membrane/songbird.sock \
  --security-socket /run/membrane/beardog.sock \
  --bind 0.0.0.0 \
  --federation-port 7700 \
  --pid-dir /run/membrane
```

Drawbridge on `:7780` — accepting HTTP proxy connections.
Federation on `:7700` — inter-gate mesh communication.

---

## 7. Structural Scenario — tower-atomic-parity

**Result**: 21/21 checks GREEN (1 test passed, 0 failed)

| Phase | Checks | Status |
|-------|--------|--------|
| Phase 1: Composition primals (bearDog + songBird + skunkBat) | 5 | GREEN |
| Phase 2: Relay capabilities (BTSP + mesh relay) | 5 | GREEN |
| Phase 3: Benchmark topology (LAN + WAN peers) | 4 | GREEN |
| Phase 4: Parity spec (latency/throughput targets) | 5 | GREEN |
| Phase 5: Credential store (secrets.* integration) | 2 | GREEN |

---

## 8. WAN Baseline Measurements (WireGuard)

These are the WireGuard baselines for the WAN parity benchmark path:

| Metric | Path | Value |
|--------|------|-------|
| RTT to golgiBody | sporeGate (.2) → golgiBody (.1) | **37.8ms avg** (37.1–38.4ms) |
| RTT to flockGate | sporeGate (.2) → golgiBody (.1) → flockGate (.6) | **68.1ms avg** (65.1–69.8ms) |
| WG interface | wg0, port 51821 | Active, recent handshake |
| WG transfer | lifetime | 206.56 MiB rx / 3.61 GiB tx |

**Note**: flockGate TTL=63 (one hop through golgiBody) confirms relay path.

---

## 9. WAN Parity Benchmark — Gap Analysis

### What's Ready

- [x] sporeGate Tower primals: 3/3 LIVE (bearDog, songBird, skunkBat)
- [x] WireGuard connectivity: sporeGate ↔ golgiBody ↔ flockGate verified
- [x] Structural scenario passes: registry has all required capabilities
- [x] WG baseline latency measured: ~38ms to golgiBody, ~68ms to flockGate

### What's BLOCKED

| Blocker | Owner | Priority | Detail |
|---------|-------|----------|--------|
| **TURN relay not deployed on golgiBody** | golgiBody ops | **P0** | songBird's `songbird relay` is CODE COMPLETE but not deployed. Need systemd unit on golgiBody ([RELAY_PUBLIC]). Without this, Tower relay path cannot be tested. |
| **Benchmark harness not implemented** | eastGate primalSpring | **P1** | `songbird benchmark` CLI (proposed in convergence brief) does not exist yet. Need throughput/latency measurement tooling. |
| **flockGate Tower primal status unknown** | flockGate team | **P1** | flockGate shows `role=tower` in topology but we haven't verified songBird is accepting Tower relay connections there. |
| **iperf3-equivalent through Tower stack** | eastGate songBird | **P2** | Need a way to measure raw throughput through the Tower relay, comparable to iperf3 through WireGuard. |

### Proposed Benchmark Execution Plan

```
Phase A: Deploy TURN relay on golgiBody
  1. golgiBody team deploys `songbird relay` systemd unit
  2. Verify relay accepts connections from sporeGate and flockGate
  3. Verify relay routes between peers

Phase B: Measure WireGuard baseline (control)
  1. iperf3 server on flockGate
  2. iperf3 client on sporeGate → golgiBody → flockGate
  3. Record: throughput (Mbps), latency (RTT), jitter

Phase C: Measure Tower relay (experiment)
  1. songbird benchmark or equivalent on sporeGate → Tower relay → flockGate
  2. Record: throughput (Mbps), latency (RTT), connection setup time, reconnect time
  3. Compare Tower vs WireGuard results

Phase D: Report
  1. TOWER_WAN_PARITY_RESULTS.md in wateringHole/handoffs/
  2. Include raw numbers, pass/fail against spec, methodology
```

### Parity Spec (from updated convergence brief — relative targets)

| Metric | WG Baseline (measured) | Tower Target |
|--------|----------------------|--------------|
| WAN RTT (to golgiBody) | **37.8ms** | ≤2x WG = ≤75.6ms |
| WAN RTT (to flockGate) | **68.1ms** | ≤2x WG = ≤136.2ms |
| WAN throughput | TBD (iperf3 needed) | ≥80% of WG |
| Connection setup | ~50ms (WG handshake) | ≤500ms |
| Reconnect | instant (WG stateless) | ≤2s |

---

## 10. Findings for eastGate (Code Changes Needed)

Per convergence rules, sporeGate does NOT modify primalSpring code. These are
proposed fixes for eastGate to integrate:

### P2: Doc Warning Fix

**File**: `ecoPrimal/src/bin/nucleus_launcher/orchestrator/registry.rs`, line 55

```rust
// Current:
/// this to build a primal → Vec<domain> mapping for discovery-provider seeding.
// Proposed:
/// this to build a primal → `Vec<domain>` mapping for discovery-provider seeding.
```

### P2: Coverage Gap — Live-Tier Scenario Paths

Many scenario files have 37–64% coverage because their Live-tier probe branches
are unreachable during `cargo test --lib`. Consider:
1. Mock-backed integration tests for live probe paths
2. Or accept that structural coverage (75.63%) is appropriate for a validation crate

### ~~P3: WAN Latency Observation~~ — RESOLVED

eastGate updated the convergence brief to use relative targets (≥80% of WG throughput,
≤2x WG latency) instead of absolute thresholds. Our measured baselines (37.8ms to
golgiBody, 68.1ms to flockGate) become the WG reference — Tower targets are relative
to these, not fixed numbers. No action needed.

---

## Summary

primalSpring on sporeGate is **audit-clean and structurally ready** for the Tower
Atomic WAN parity benchmark. The codebase is in excellent shape: zero clippy warnings,
zero formatting issues, zero unsafe code, zero TODO markers, all files under 1000 lines,
AGPL-3.0 compliant with Pure Rust crypto throughout.

**The primary blocker is operational**: golgiBody needs the TURN relay deployed, and
the benchmark harness needs implementation by the songBird/eastGate team. Once those
are in place, sporeGate can execute the WAN benchmark immediately — all three Tower
primals are live and the WireGuard baseline is measured.

---

**Filed by**: sporeGate + golgiBody team (Wave 150v)
**Next action**: golgiBody → deploy TURN relay; eastGate → benchmark harness
