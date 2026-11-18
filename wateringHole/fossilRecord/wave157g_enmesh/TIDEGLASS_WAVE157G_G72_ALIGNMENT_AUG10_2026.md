# tideGlass Wave 157g — G72 Dependency Pandemic Alignment

**Date**: Aug 10, 2026 | **Wave**: 157g | **Gate**: westGate
**Author**: tideGlass code team (from overwatch on eastGate)
**Status**: GREEN — 220 tests, zero clippy, 1.9 MB release binary

---

## What Happened

Cascaded from golgiBody Wave 157g blurb. Audited tideGlass against G72
Dependency Pandemic spec (`specs/DEPENDENCY_PANDEMIC_SPEC.md`). Executed
one actionable optimization; confirmed all other G72 items already compliant.

---

## G72 Audit Results

### Already Compliant (no action needed)

| G72 Item | tideGlass Status |
|----------|------------------|
| `tokio ["full"]` | Never used — feature-specific since genesis |
| pollster in GPU springs | Not applicable — no GPU binaries |
| Dead tokio deps | Zero — only `tideglass-bin` uses tokio |
| HTTP client (ureq/reqwest) | Zero — CAS routes through Neural API UDS |
| axum | Zero — pure UDS JSON-RPC, no HTTP server |
| wgpu | Zero — GPU dispatch goes through `capability.call` |
| YAML crates | Zero |
| env_logger | Zero — no logging crate (eprintln-only) |
| chrono | Zero |
| thiserror | v2 (current) |
| Version splits | Zero — all deps at latest |

### Executed

| Change | Before | After | Impact |
|--------|--------|-------|--------|
| `tokio` features | `["rt-multi-thread", "net", "io-util", "macros", "signal"]` | `["rt", "net", "io-util", "macros", "signal"]` | Removes thread pool code. Protist serves sequential science queries — current-thread is correct. |
| Runtime creation | `Runtime::new()` (multi-thread) | `Builder::new_current_thread().enable_all().build()` | Same behavior for sequential UDS dispatch. |

### Dependency Profile

| Metric | Value |
|--------|-------|
| Workspace crates | 9 |
| Direct external deps | 6 (serde, serde_json, thiserror, rand, base64, tokio) |
| Unique transitive deps | 21 (excluding workspace crates) |
| Release binary size | 1.9 MB |
| `#![forbid(unsafe_code)]` | All 9 crates |
| Pure Rust deps | 21/21 (cargo deny: no C FFI) |

tideGlass is the leanest composition in the ecosystem. Born gen5-native — no
Aug 2025 stadial debt to shed.

---

## Doc Reconciliation (this wave)

| File | Change |
|------|--------|
| All docs (8 files) | 519 GB → 3.21 TB / 452 GB CAS pool |
| All docs (4 files) | `neural-api-default.sock` → `neural-api-*.sock` prefix-glob |
| CONTEXT, DATA_ACCESS, MODULE_SPECS | NumPy/pickle → JSON (RESOLVED) |
| scope.toml | "awaiting GPS JSON conversion" → "GPS JSON in CAS" |
| CHANGELOG | G72 tokio trim documented |

---

## Cell Boot Status

tideGlass cell boot on westGate is BLOCKED on depot pull:

| Prereq | Status |
|--------|--------|
| `tideglass_cell.toml` | Ready |
| GPS data in CAS (11 JSON, 103 MB) | Ready |
| `content.query` in tideGlass | Wired |
| `PetalTongueClient` | Activated |
| westGate depot pull (v4.57+) | **PENDING** — westGate needs `depot pull` |
| westGate NUCLEUS restart | **PENDING** — after depot pull |
| `biomeos nucleus attach` | **PENDING** — after NUCLEUS restart |

Once westGate pulls the depot and restarts NUCLEUS, tideGlass cell boot is a
single `biomeos nucleus attach runtime_graphs/tideglass_cell.toml` command.

---

## Gossip Mesh Context

westGate is in the 4-gate gossip mesh (outbound). tideGlass is a protist —
it consumes CAS data via Neural API, it does not inject gossip events. Gossip
integration is not applicable.

Provenance write (per-RGES execution via rhizoCrypt → loamSpine → sweetGrass)
remains a future work item, routed through Neural API `capability.call`.

---

## Upstream Items for Overwatch

1. **westGate depot pull**: tideGlass cell boot blocked. Science springs
   (groundSpring, airSpring) also waiting.
2. **Chen 2017 benchmark**: First E2E science validation (r >= 0.52). Requires
   cell boot + CAS data loaded from GPS JSON.
3. **Provenance write**: Per-RGES execution provenance via Neural API. Requires
   `braid.verify` behavioral tests (sweetGrass P2).
4. **petalTongue co-deployment**: Visualization scenes ready as JSON, forwarding
   wired. Live WebGL render awaits petalTongue on westGate or ironGate.

---

*tideGlass: 9 crates, 220 tests, 17 IPC methods, 21 external deps, 1.9 MB
binary, zero unsafe, zero P0/P1/P2. Gen5-native — already past the stadial.*
