<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Squirrel v0.1.0 — neuralSpring Inference Wiring + NestGate Env Unification

**Date**: May 13, 2026
**Session**: BD
**Audit Source**: primalSpring glacial debt escalation (May 13, 2026)
**Finding**: Meta-tier CLEAN — niche evolution: neuralSpring wiring, NestGate weight storage

## Changes

### 1. Inference UDS Timeout Fix

**Problem**: `send_jsonrpc_public` used a hardcoded 2-second read timeout for
all UDS JSON-RPC calls. LLM inference calls via neuralSpring can take 10-120+
seconds. Every inference call over UDS was racing the timeout.

**Fix**: Added `send_jsonrpc_with_timeout()` in `capabilities/lifecycle.rs` —
a configurable-timeout variant. `RemoteInferenceAdapter` now uses 120s read
timeout for both `inference.complete` and `inference.embed` UDS calls.
Original `send_jsonrpc_public` preserved at 2s for lifecycle heartbeats.

Files:
- `crates/main/src/capabilities/lifecycle.rs` — new `send_jsonrpc_with_timeout`
- `crates/main/src/api/ai/adapters/remote_inference.rs` — switched to 120s timeout

### 2. Inference Endpoint Auto-Discovery

**Problem**: neuralSpring (or any inference primal) had to call
`inference.register_provider` at runtime to be discovered. No env-based
auto-discovery existed for inference endpoints, unlike compute
(`COMPUTE_ENDPOINT`) or storage (`STORAGE_ENDPOINT`).

**Fix**: `AiRouter::new_with_discovery()` now checks `INFERENCE_ENDPOINT` and
`AI_INFERENCE_ENDPOINT` env vars at startup. If set, it auto-registers a
`RemoteInferenceAdapter` with the resolved endpoint (UDS or HTTP).

Files:
- `crates/main/src/api/ai/router.rs` — step 1.7 inference endpoint discovery

### 3. Storage Env Resolution Unification

**Problem**: `DefaultEndpoints::storage_endpoint()` checked
`STORAGE_SERVICE_ENDPOINT` → `NESTGATE_ENDPOINT` but **not**
`STORAGE_ENDPOINT`. `EcosystemConfig` checked `STORAGE_ENDPOINT`.
Operators setting `STORAGE_ENDPOINT` got different behavior depending on
which resolution path was hit.

**Fix**: Added `STORAGE_ENDPOINT` to `DefaultEndpoints` resolution chain:
`STORAGE_SERVICE_ENDPOINT` → `STORAGE_ENDPOINT` → `NESTGATE_ENDPOINT`.

Files:
- `crates/ecosystem-api/src/defaults.rs` — unified env chain

## Quality Gate Results

| Metric | Result |
|--------|--------|
| `cargo fmt --all` | PASS |
| `cargo clippy` (workspace) | ZERO warnings |
| `cargo test --workspace` | 7,209 pass / 0 fail |
| `cargo deny check` | advisories ok, bans ok, licenses ok, sources ok |

## Remaining Niche Evolution (Not Blocking)

- **NestGate weight storage client**: `UniversalStorageClient` scaffold exists
  but is inactive. Full `storage.put`/`get` IPC client and model→CAS
  loader loop are future work.
- **`primal_provider/ai_inference.rs` stub**: Returns canned responses.
  Orthogonal to JSON-RPC `inference.*` path (which routes through AiRouter).
  Low priority cleanup.
- **`jsonrpc_dispatch.rs` drift**: Dead file not `mod`'d. Should be deleted or
  reconciled with `jsonrpc_server.rs` dispatch table. No behavioral impact.
