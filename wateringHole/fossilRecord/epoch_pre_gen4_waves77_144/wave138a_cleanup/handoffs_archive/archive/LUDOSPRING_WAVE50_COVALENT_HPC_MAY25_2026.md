# ludoSpring — Wave 50 Covalent HPC Status

**Date**: May 25, 2026
**Version**: V79
**Gate**: ironGate (i9-14900K, RTX 5070, 96GB DDR5)
**Status**: **operational** — covalent HPC ready

---

## Summary

ludoSpring Wave 50 is complete. Post-primordial mandate absorbed, NUCLEUS live
via primalSpring zero-port launcher, Songbird mesh seeded, and GAP-01 (coralReef
shader compilation) live-validated for the first time.

## Deployment

| Item | Status |
|------|--------|
| NUCLEUS | 12/12 ALIVE (UDS zero-port, primalSpring launcher) |
| Federation | Songbird TCP `0.0.0.0:7700` — LAN reachable at `192.168.1.238` |
| Mesh seeded | `mesh.init` node_id=`irongate`, bootstrap=`192.168.1.144:7700` |
| Cell graph | `plasmidBin/cells/ludospring_cell.toml` (12 nodes, pure composition) |
| Proto-nucleate | 11/11 PASS (UDS-first validation) |
| Post-primordial | Zero `target/release/` primal refs. plasmidBin only. |
| Tests | 982 workspace tests, zero clippy, zero unsafe |

## Wave 50 Deliverables

### GAP-01 coralReef — RESOLVED

`shader.compile.wgsl` live-validated against coralReef on ironGate:
- Fog-of-war compute shader → 688 bytes SPIR-V via UDS
- Method: `shader.compile.wgsl` (not `shader.compile`)
- Socket: `/run/user/1000/biomeos/shader.sock` (capability alias)
- ludoSpring's `try_coralreef_compile()` will auto-use live IPC

### Cross-gate state sync

Composition graph: `graphs/composition/cross_gate_state_sync.toml`
- Pattern: local NestGate → Songbird mesh → remote NestGate
- BTSP auth enforced (NestGate requires authentication)
- Ready to deploy when 2+ gates are meshed

### Post-primordial cuts

- `composition_nucleus.sh`: removed `target/release/` fallback, `which` fallback,
  CamelCase scanning. Errors hard if binary not in plasmidBin.
- `validate_gate_ipc.py`: UDS-first for all probes (zero-port compatible)
- socat dependency eliminated (python3 UDS helper)

## plasmidBin Fixes (committed upstream)

`start_primal.sh` CLI alignment for current binaries:
- barracuda: `--socket` → `--unix`
- rhizocrypt: `--socket` → `--unix`, explicit `--port`
- coralreef: removed `--socket`, uses `--rpc-bind` only
- nestgate: `daemon` → `server --socket-only --family-id`
- nucleus_launcher.sh: `SONGBIRD_FEDERATION_PORT` env plumbed

## Known Pipeline Debt (not ludoSpring)

| Issue | Owner | Impact |
|-------|-------|--------|
| loamSpine Tokio runtime-in-runtime | loamSpine team | Socket shows DOWN, skipped |
| Squirrel needs Ollama | Squirrel/external | Classified as degraded PASS |
| petalTongue stale socket on restart | petalTongue team | `rm` socket before restart |

## Response

**ludoSpring Wave 50: NUCLEUS 12/12 on ironGate, peers seeded, covalent ready.**
