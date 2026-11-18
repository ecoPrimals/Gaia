# ToadStool — Wave 155k Legacy Symlink Fix

**Date**: Jul 30, 2026 | **Session**: S348 | **Gate**: strandGate | **Priority**: P2 resolved
**Wave**: 155k | **Divergence**: "toadStool tarpc-only (no JSON-RPC health endpoint)" on westGate

---

## Summary

Fixed root cause of P2 divergence: legacy symlink `toadstool.sock` was pointing at
`compute-tarpc.sock` (binary tarpc protocol) instead of `compute.sock` (JSON-RPC primary).

Any biomeOS or legacy caller probing `toadstool.sock` would receive tarpc binary frames
instead of JSON-RPC responses, appearing as if toadStool had no JSON-RPC health endpoint.

## Root Cause

In `crates/server/src/unibin/mod.rs`, the symlink creation code used `&tarpc_socket_path`
as the symlink target instead of `&jsonrpc_socket`. The doc comment correctly documented
`toadstool.sock → compute.sock`, but the code did the opposite.

## Fix

One file, 7 insertions / 6 deletions:
- Symlink target: `&tarpc_socket_path` → `&jsonrpc_socket`
- Parent dir derivation: from `tarpc_socket_path` → from `jsonrpc_socket`
- Self-link guard: compare against `jsonrpc_socket` instead of `tarpc_socket_path`

## Verification

| Gate | Status |
|------|--------|
| `cargo clippy -p toadstool-server --all-targets -D warnings` | 0 warnings |
| `cargo test -p toadstool-server --lib` | 1,128 passed, 0 failed |

## Upstream Notes

### westGate
- After redeploying toadStool with this fix, `toadstool.sock` will correctly route to
  JSON-RPC `compute.sock`. biomeOS health probes via the legacy socket will work.

### All gates
- Gates using `compute.sock` directly (the recommended path) were never affected.
- Only callers using the legacy `toadstool.sock` symlink experienced the issue.

---

*Wave 155k P2 resolved. Legacy symlink now correctly points at JSON-RPC primary.*
