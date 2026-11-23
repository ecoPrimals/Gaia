<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef — Wave 47: Deployment Behavioral Convergence

**Date**: 2026-05-24  
**Author**: coralReef team  
**Audit reference**: Wave 47 — Post-Primordial Behavioral Convergence (primalSpring)  
**Priority**: HIGH — blocks uniform NUCLEUS deployment (workarounds in plasmidBin)

---

## Issues Resolved

### 1. `--socket PATH` CLI flag (was: env-only UDS resolution)

**Problem**: coralReef auto-resolved UDS from `$XDG_RUNTIME_DIR/biomeos/<primal>.sock`.
The generic NUCLEUS launcher passes `--socket` uniformly to all primals.

**Fix**: Added `--socket PATH` argument to the `server` subcommand. When provided,
it overrides both the default XDG-based path and the `tarpc_bind` UDS override logic.
Priority: `--socket` > `--tarpc-bind` unix override > default XDG path.

**Location**: `crates/coralreef-core/src/main.rs` — `Commands::Server { socket }`,
both `cmd_server` function variants updated.

**Test**: `parse_cli_server_socket_override` verifies the flag parses correctly.

### 2. `health.liveness` response normalization

**Problem**: Returned `{"alive":true}` — health sweeps check `jq -r .status`
which returned `null`, failing the `== "alive"` check.

**Fix**: Changed `LivenessResponse` from `{ alive: bool }` to `{ status: String }`
and `handle_health_liveness()` now returns `{"status":"alive"}`.

**Location**: `crates/coralreef-core/src/service/types.rs` (struct),
`crates/coralreef-core/src/service/mod.rs` (handler).

**Tests updated**: 9 test files updated to assert `status == "alive"` instead
of `alive == true`.

## Wire Contract Change (Breaking)

`health.liveness` response is a **wire format change**:

```json
// BEFORE (Wave 43):
{"alive": true}

// AFTER (Wave 47):
{"status": "alive"}
```

Consumers that parse `health.liveness` results need to read `.status` instead
of `.alive`. This aligns coralReef with the ecosystem-wide
`DEPLOYMENT_BEHAVIOR_STANDARD` which mandates `{"status":"alive"}`.

## Validation

```bash
# Test --socket override:
coralreef server --socket /tmp/test-coralreef.sock

# Verify health.liveness response:
echo '{"jsonrpc":"2.0","method":"health.liveness","params":{},"id":1}' | \
  socat - UNIX-CONNECT:/tmp/test-coralreef.sock
# Expected: {"jsonrpc":"2.0","result":{"status":"alive"},"id":1}
```

## Status

- Both Wave 47 items for coralReef: **complete**
- plasmidBin workarounds can be removed for coralReef
- No remaining deployment surface mismatches
