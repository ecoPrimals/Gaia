# AAR — strandGate riboCipher Convergent Evolution (Wave 111, Stream 7)

**Date**: June 13, 2026  
**Gate**: strandGate  
**Primal**: hotSpring (barracuda crate)  
**Wave**: 111  
**Stream**: 7 (riboCipher Transport Signal Convergence)  
**Standard**: `RIBOCIPHER_TRANSPORT_SIGNAL_STANDARD.md`

---

## Summary

hotSpring has shipped riboCipher compliance per the published standard. Server-side
signal detection routes connections deterministically by reading the first byte before
any protocol parsing. Client-side IPC paths prepend `[0xEC, 0x01]` (clear signal,
NDJSON JSON-RPC) before payload.

---

## Changes Shipped

### Server (serve.rs)
- `handle_connection_generic` now reads 1 byte and routes via signal envelope:
  - `0xEC` → read protocol type byte → route (only `0x01` NDJSON supported)
  - `{` or `[` → WARN legacy unsignalled, fallback to NDJSON
  - Other → WARN legacy unsignalled, fallback to NDJSON
- `PrefixedStream` adapter: Zero-copy Read+Write wrapper that re-injects the consumed
  first byte back into the stream for legacy fallback paths.
- `handle_ndjson_loop`: Extracted NDJSON read loop into standalone function.

### Client (outbound IPC)
- `primal_bridge.rs`: `[0xEC, 0x01]` before JSON payload (biomeOS registration, capability calls)
- `fleet_ember.rs`: `[0xEC, 0x01]` before ember.adopt_device and health probes
- `toadstool_report.rs`: `[0xEC, 0x01]` before toadStool JSON-RPC calls
- `bin/_fossilized/node_atomic_gpu_comparison.rs`: `[0xEC, 0x01]` before RPC calls

### Tests
- `ribocipher_clear_signal_routes_ndjson`: Verifies `[0xEC, 0x01]` prefix routes correctly
- `ribocipher_legacy_json_still_works`: Verifies `{` prefix still works (deprecation path)

---

## Compliance Checklist (per standard §Validation)

| # | Criterion | Status |
|---|-----------|--------|
| 1 | Server accept loop checks 0xEC/0xED/0xEE BEFORE peek logic | ✅ |
| 2 | Client connections send appropriate signal prefix | ✅ |
| 3 | Unsignalled connections produce WARN-level log | ✅ |
| 4 | Tests demonstrate correct routing | ✅ (2 tests) |
| 5 | `sourdough validate ribocipher` passes | ⏳ (awaiting sourDough command) |

---

## Test Results

- **627 lib tests pass** (was 625, +2 riboCipher tests)
- **0 clippy warnings** (--lib -D warnings)
- **0 compile errors**

---

## Scope

hotSpring only serves NDJSON JSON-RPC (protocol type `0x01`). It does not serve HTTP,
BTSP, or multi-protocol. This makes the riboCipher implementation straightforward —
a single supported protocol type with legacy fallback for unsignalled connections.

Tier 2 (mito) and Tier 3 (nuclear) are not implemented because hotSpring only receives
local same-gate connections. If cross-gate compute dispatch is later routed directly
(rather than through songBird relay), mito-tier detection would be added.

---

## Next Steps

- None for hotSpring — riboCipher is SHIPPED, pending `sourdough validate` audit
- Upstream: sourDough `validate ribocipher` command needed for formal certification
- The 17 pre-existing validation failures (IPC liveness, SLy4 params, LTEE stochastic,
  tight tolerances, Herman lambda) remain unchanged and are not riboCipher-related

---

## Deprecation Awareness

| Wave | Expected Behavior | hotSpring Status |
|------|-------------------|------------------|
| 111 (now) | WARN on legacy | ✅ SHIPPED |
| 112 | ERROR on legacy | Ready (change WARN → ERROR) |
| 113 | REJECT unsignalled | Ready (add -32002 response) |
| 114 | Remove legacy code | Ready (delete fallback paths) |
