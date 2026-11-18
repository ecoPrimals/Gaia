# barraCuda — FRAGO Response: Sovereign Compute Cascade

**Date**: 2026-06-01  
**In Response To**: `FRAGO_BARRACUDA_SOVEREIGN_COMPUTE_CASCADE_JUN01_2026.md`  
**From**: barraCuda team (strandGate)  
**To**: hotSpring (biomeGate), primalSpring (eastGate)  
**Commits**: `5c70da46`, `ccb5d752`

---

## P1: RESOLVED — Wire contract clarified and evolved

### What changed

`compute.dispatch.submit` now has two distinct modes:

**Mode 1 — Shader binary dispatch** (when `binary_b64` present):
1. Resolves toadStool via Songbird `DISCOVERY_SOCKET` → `ipc.resolve`
2. If toadStool found: forwards full request (binary_b64, input, shader_info, bindings, bdf)
3. If toadStool unavailable: falls back to tensor passthrough with explicit diagnostics

**Mode 2 — Tensor passthrough** (no `binary_b64`):
- Unchanged behavior: uploads input.data to GPU, reads back, stores as job

### Response contract update

All responses now include `"routed": bool`:
- `"routed": true` → workload was forwarded to toadStool for shader execution
- `"routed": false` → handled locally (tensor passthrough or fallback)

When falling back with a binary present, response includes:
```json
{
  "job_id": "job-...",
  "status": "completed",
  "routed": false,
  "note": "binary_b64 present but toadStool unavailable — tensor passthrough used"
}
```

### Ownership clarity

| Method | Owner | Purpose |
|--------|-------|---------|
| `compute.dispatch` (ops) | barraCuda | Named tensor ops (zeros, ones, read) |
| `compute.dispatch.submit` | barraCuda → toadStool | Shader execution (routes to toadStool when available) |
| `compute.dispatch.capabilities` | barraCuda | GPU/CPU capability reporting |
| `compute.dispatch.result` | barraCuda | Job result retrieval |

---

## P2: RESOLVED — Cross-gate capability routing implemented

`try_forward_to_toadstool()` resolves toadStool via:
```
DISCOVERY_SOCKET → ipc.resolve { capability: "compute.dispatch.submit" }
  → toadStool UDS path
  → forward full JSON-RPC request
  → return result
```

`primal.capabilities` now advertises `consumed_capabilities` including
`"compute.dispatch.submit"` — making the toadStool dependency explicit
in the capability graph.

---

## Deployment Note (circular symlinks)

Acknowledged. Not blocking evolution. Socket symlink management in
`IpcServer::create_legacy_symlink` is idempotent (removes before creating).
Will investigate if the NUCLEUS composition context creates a different
symlink ordering issue.

---

## Test Coverage

10 dispatch pipeline tests pass:
- `capabilities_returns_cpu_capabilities_without_gpu`
- `capabilities_includes_primal_and_version`
- `submit_missing_input_returns_invalid_params`
- `submit_empty_data_returns_failed_status`
- `submit_valid_returns_job_id_cpu_fallback`
- `submit_then_retrieve_result`
- `submit_with_binary_and_no_toadstool_falls_back` ← new
- `result_missing_job_id_returns_invalid_params`
- `result_unknown_job_id_returns_not_found`
- `full_pipeline_roundtrip`

---

## What hotSpring Can Expect Now

1. Send `compute.dispatch.submit` with `binary_b64` — barraCuda will route to toadStool if available
2. Check `"routed"` field to know if shader executed or tensor-passthrough was used
3. If `"routed": false` + binary was sent → toadStool not in NUCLEUS composition
4. `compute.dispatch.capabilities` accurately reports what hardware is available

---

*Wave 67 FRAGO complete. Wire contract clarified. Capability routing live.*
