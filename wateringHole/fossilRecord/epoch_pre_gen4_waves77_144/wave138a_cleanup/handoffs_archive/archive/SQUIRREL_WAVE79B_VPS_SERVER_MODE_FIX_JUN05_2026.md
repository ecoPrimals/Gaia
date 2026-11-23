# Squirrel Wave 79b — VPS Server Mode Regression Fix

**Date**: June 5, 2026
**From**: squirrel (eastGate)
**Wave**: 79b
**Priority**: P0 (blocks VPS NUCLEUS refresh)

## Problem

VPS deployment reported `squirrel server` as "unrecognized subcommand". The
deployed binary only had: `text-generation`, `code-generation`,
`multi-model-workflow`, `list-models`, `test-local`, `benchmark`.

## Root Cause

**Wrong binary deployed.** The workspace produces multiple binaries:

| Binary | Crate | Purpose |
|--------|-------|---------|
| `squirrel` | `crates/main` | **Deployable service** — `server`, `client`, `doctor`, `version` |
| `squirrel-cli` | `crates/tools/cli` | Development CLI tool |
| `ai_tools_demo` | `crates/tools/ai-tools` | Demo/example binary |

plasmidBin or `build-primal.sh` picked up `ai_tools_demo` instead of `squirrel`.

## Fix Applied

1. Added `default-run = "squirrel"` to `crates/main/Cargo.toml`
2. Documented correct binary in `CURRENT_STATUS.md`

## Verification

```bash
squirrel server --socket /tmp/test.sock
# Starts UDS JSON-RPC listener, binds at specified path

echo '{"jsonrpc":"2.0","method":"health.check","params":{},"id":1}' | \
  socat - UNIX-CONNECT:/tmp/test.sock
# Returns: {"jsonrpc":"2.0","result":{"alive":true,"status":"alive",...},"id":1}
```

## Socket Naming

Default socket: `$XDG_RUNTIME_DIR/biomeos/squirrel-{FAMILY_ID}.sock`

When `--socket <path>` is provided, uses that path directly. The launcher
should pass: `squirrel server --socket $SOCKET_DIR/squirrel-${FAMILY_ID}.sock`

## Action for cellMembrane / plasmidBin

Ensure `build-primal.sh` builds with:
```bash
cargo build --release -p squirrel --bin squirrel
```

NOT `cargo build --release --workspace` (which produces all binaries).

## Status

**NOT A CODE BUG.** Server mode has been operational since Wave 43. This was
a packaging/deployment error. Commit `5dea2cc6` adds disambiguation.
