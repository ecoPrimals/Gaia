# Squirrel Wave 82c — UDS Health Probe Fix

**Date**: June 6, 2026
**From**: squirrel (eastGate)
**Wave**: 82c
**Priority**: P1 (was blocking VPS health monitoring)

## Problem

"Socket connects but `health.liveness` returns empty on UDS."

On VPS with `FAMILY_ID` set (production mode), plain JSON-RPC health
probes over UDS received no response. TCP probes worked fine.

## Root Cause

When `FAMILY_ID` is set, the BTSP Phase 2 auto-detect logic in
`maybe_handshake()` reads the first line to determine if the client is
initiating a BTSP handshake or sending plain JSON-RPC.

For plain JSON-RPC (e.g. `health.liveness`):
1. `maybe_handshake()` consumed the entire first line
2. Detected it wasn't a BTSP ClientHello
3. Returned `Err(BtspError::PlainJsonRpc { first_line })`
4. The accept loop treated ALL errors identically: `return;` (drop connection)

The request bytes were consumed but never processed — client sees empty/EOF.

TCP was unaffected because the TCP accept loop does NOT run `maybe_handshake()`.

## Fix

Commit `5172ef50`: Handle `BtspError::PlainJsonRpc` as a recoverable case
(PG-14 auto-detect fallback). The consumed `first_line` is re-injected into
`handle_jsonrpc_with_first_line()` so the request is processed and a
response is sent.

Also extracted `handle_uds_connection()` helper to DRY both UDS accept loops
and resolve a `too_many_lines` clippy warning.

## Verification

```bash
# Production mode (FAMILY_ID set):
SQUIRREL_FAMILY_ID=ecoPrimal squirrel server --socket /tmp/test.sock

# Health probe now returns proper response:
echo '{"jsonrpc":"2.0","method":"health.liveness","params":{},"id":1}' | \
  socat - UNIX-CONNECT:/tmp/test.sock
# → {"jsonrpc":"2.0","result":{"alive":true,"status":"alive",...},"id":1}
```

## Impact

- Unblocks VPS health monitoring for squirrel in BTSP-guarded mode
- All plain JSON-RPC methods (health, identity, capabilities) now work
  over UDS regardless of FAMILY_ID setting
- BTSP-authenticated connections continue to work as before
- TCP path unchanged (never ran handshake)

## Tests

- 7,098 passed / 0 failed
- 0 clippy warnings
- Verified with `SQUIRREL_FAMILY_ID=ecoPrimal` active
