# rhizoCrypt — Wave 43: Neural API `primal.announce`

**Date**: 2026-05-23
**Sprint**: S70 (Wave 43 adoption)
**Status**: Complete — merged, 1,646 tests passing

## Summary

Implemented outbound `primal.announce` JSON-RPC call to biomeOS Neural API
per `WAVE42_NEURAL_API_DEPLOYMENT_GUIDE.md` wire schema.

## What Was Done

### 1. Announce Payload (`niche.rs`)

`announce_payload(socket_path, pid)` builds the full Wire Schema payload:

- `primal`: `"rhizocrypt"`
- `capabilities`: `["dag", "integrity", "merkle"]`
- `methods`: all 32+ registered methods from `CAPABILITIES`
- `semantic_mappings`: all `provenance.*` → `dag.*` aliases from `PROVENANCE_ALIASES`
- `signal_tiers`: `["nest"]`
- `cost_hints`: `{ dag: 10.0, integrity: 5.0, merkle: 8.0 }`
- `latency_estimates`: `{ dag: 15, integrity: 5, merkle: 10 }`
- `version`: crate version
- `pid`: process ID (optional)
- `attestation`: null (bearDog attestation not yet adopted)

### 2. Socket Discovery (`lib.rs`)

`discover_neural_api_socket()` implements tiered lookup:

1. `$NEURAL_API_SOCKET` (env override)
2. `$XDG_RUNTIME_DIR/biomeos/neural-api-{family}.sock`
3. `/tmp/biomeos/neural-api-{family}.sock`

Where `{family}` = `$ECOPRIMALS_FAMILY_ID` (default: `ecoPrimal`).

### 3. Outbound Call (`lib.rs`)

`announce_to_biomeos(socket_path)` sends newline-delimited JSON-RPC to the
discovered biomeOS socket. Called in `run_server_with_ready()` immediately
after `publish_capability_manifest()`. Non-fatal — if biomeOS is unavailable,
rhizoCrypt logs at debug level and continues in standalone mode.

### 4. Tests

4 new tests in `niche_tests.rs`:
- `announce_payload_has_required_fields` — validates all required fields present
- `announce_payload_has_cost_and_latency_hints` — validates cost/latency maps
- `announce_payload_includes_semantic_mappings` — validates provenance alias mappings
- `announce_payload_pid_optional` — validates pid=null when not provided

## Wave 22 Checklist Impact

`primal.announce` was one of 2 remaining FAIL items in the stadial checklist
(the other being `btsp.capabilities`). Now PASS.

## Validation

After biomeOS is running with v3.69+ persistent weights:

```bash
echo '{"jsonrpc":"2.0","method":"neural_api.routing_weights","params":{},"id":1}' | \
  socat - UNIX-CONNECT:$XDG_RUNTIME_DIR/biomeos/neural-api-ecoPrimal.sock
```

Should show rhizoCrypt as a provider for `dag.*`, `integrity.*`, `merkle.*`
capability calls with non-default routing affinity.

## Files Changed

| File | Change |
|------|--------|
| `crates/rhizo-crypt-core/src/niche.rs` | `announce_payload()`, `semantic_mapping_object()` |
| `crates/rhizo-crypt-core/src/niche_tests.rs` | 4 announce payload tests |
| `crates/rhizocrypt-service/src/lib.rs` | `announce_to_biomeos()`, `discover_neural_api_socket()`, `send_jsonrpc_uds()` |
| `CHANGELOG.md` | Wave 43 entry |
| `README.md` | Neural API section in Composition Readiness |
| `capability_registry.toml` | Neural API announce documentation |
| `sporeprint/validation-summary.md` | Updated test/line counts, added Neural API transport |
| `CONTEXT.md` | Updated test/line counts |
