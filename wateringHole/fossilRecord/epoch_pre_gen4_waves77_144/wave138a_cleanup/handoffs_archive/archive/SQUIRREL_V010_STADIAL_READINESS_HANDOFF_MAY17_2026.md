<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Squirrel v0.1.0 — Stadial Readiness Hardening

**Date**: May 17, 2026
**Session**: BE
**Audit reference**: Wave 22: Stadial Gate (primalSpring → all primals)

## Context

primalSpring Wave 22 declared Squirrel in the **Low-Debt Group** (structurally clean,
zero blocking gaps). This session self-audited against the **Universal Standards Checklist**
and closed all remaining gaps for stadial readiness.

## Changes

### Gap Closures

1. **`capabilities.list` envelope compliance** — response now includes canonical
   `capabilities` array and `count` field per `CAPABILITY_WIRE_STANDARD`:
   `{ capabilities: [...], count: N, primal: "squirrel", methods: [...], ... }`.
   Existing `methods` field preserved for backward compatibility.

2. **`primal.announce` method** — stadial-standard self-registration alias.
   Dispatches to `handle_announce_capabilities` alongside `capabilities.announce` /
   `capability.announce`. Registered in dispatch table, `capability_registry.toml`,
   `method_gate.rs` (public tier), niche `CAPABILITIES`, cost estimates, and
   operation dependencies.

3. **TCP from env binding** — `run_server` now resolves `SQUIRREL_PORT` /
   `SQUIRREL_SERVER_PORT` from environment when `--port` CLI arg is absent.
   Previously TCP only bound with explicit `--port`, violating the runtime
   checklist item "TCP fallback respects `ports.env` assignment."

4. **Stability tier annotations** — all 38 registered methods in
   `capability_registry.toml` annotated with `stability = "stable"` or `"evolving"`:
   - **stable**: health.*, identity.get, capabilities.*, capability.*, primal.announce,
     system.*, discovery.*, lifecycle.*, ai.* (frozen wire format)
   - **evolving**: inference.*, tool.*, context.*, provider.*, btsp.*, graph.*, signal.*

5. **`signal.plan` registered** — added to `capability_registry.toml`, `COST_ESTIMATES`,
   `operation_dependencies`, and `SEMANTIC_MAPPINGS` (previously in dispatch table
   but missing from these metadata surfaces).

### Documentation

6. **Degradation behavior** — README now includes per-domain degradation table
   (AI, tool, context, capabilities, graph, provider) with severity ratings and
   standalone mode description.

7. **Stadial pairing** — README documents downstream partner integration:
   esotericWebb (agentic AI), projectFOUNDATION (AI-assisted analysis),
   neuralSpring (inference backend), all springs (discovery substrate).

### Debt Cleanup

8. **Clippy fixes**: `PartialEq` without `Eq` on `SignalToolDef`, `SignalPlanStep`,
   `SignalPlanResponse`; redundant clone on `ai_response.provider_id`; let-and-return
   in `parse_signal_plan`; unused `Credentials` import in `tests_registry.rs`.

9. **`cost_estimates_json` refactored** — replaced 38-entry `serde_json::json!` macro
   (hit recursion limit) with programmatic builder from `COST_ESTIMATES` array.

## Universal Standards Checklist Status

| Category | Item | Status |
|----------|------|--------|
| Runtime | Health triad | PASS |
| Runtime | UDS at XDG_RUNTIME_DIR/biomeos/squirrel.sock | PASS |
| Runtime | TCP fallback from env | PASS (fixed this session) |
| Runtime | `server --port` | PASS |
| Runtime | Standalone without FAMILY_ID/NODE_ID | PASS |
| Discovery | `capabilities.list` canonical shape | PASS (fixed this session) |
| Discovery | `identity.get` | PASS |
| Discovery | `primal.announce` | PASS (added this session) |
| Discovery | `{domain}.{operation}` naming | PASS |
| Security | BTSP when FAMILY_ID set | PASS |
| Security | deny.toml bans ring/openssl/aws-lc-sys | PASS |
| Build | edition = "2024" | PASS |
| Build | musl-static | PASS |
| Docs | README version | PASS |
| Docs | CHANGELOG | PASS |
| Docs | CURRENT_STATUS | PASS |
| Composition | Stability tiers | PASS (added this session) |
| Composition | Degradation behavior | PASS (added this session) |
| Composition | Downstream pairing | PASS (added this session) |

## Quality Gates

- `cargo fmt --all`: clean
- `cargo clippy --workspace --all-targets -- -D warnings`: zero warnings
- `cargo test --workspace --lib --tests`: 7,089 passed, 0 failed
- `cargo deny check`: advisories ok, bans ok, licenses ok, sources ok

## Method Count

38 registered methods (up from audit's 20 — includes capabilities accumulated
across sessions AW through BE).

## Version Bump Consideration

Significant evolution since v0.1.0 initial tag:
- MethodGate (JH-0) security layer
- Compute delegation (RemoteComputeProvider)
- neuralSpring inference wiring (120s UDS timeout, endpoint auto-discovery)
- NestGate env unification
- Stadial readiness hardening (this session)
- 38 methods, 7,089 tests

Recommend tagging **v0.2.0** at stadial entry to reflect maturity.
