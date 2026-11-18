# primalSpring Wave 54 — Mountain Upstream Blurbs

**Date:** 2026-05-27
**From:** primalSpring (ecosystem validation)
**Context:** southGate NUCLEUS redeploy (8/13 health, 5 primals unresponsive)
**Resolved this wave:** plasmidBin fetch.sh crash, skunkBat missing from launcher,
  NODE_ID/NESTGATE_JWT_SECRET env defaults

---

## petalTongue — `--socket` flag support needed

**Status:** DOWN on southGate — binary rejects `--socket` CLI arg
**Impact:** Blocks full NUCLEUS health (12→13) on all gates
**Severity:** BLOCKING Wave 54 deployment

The `nucleus_launcher.sh` passes `--socket <path>` to every primal.
petalTongue's current binary rejects this flag entirely. Two options:

1. **Preferred:** Accept `--socket <path>` to specify UDS listen path
   (matching beardog/songbird/nestgate/loamspine convention)
2. **Minimum:** Accept and ignore `--socket` without erroring, and instead
   discover the socket path from `XDG_RUNTIME_DIR/biomeos/petaltongue-<FAMILY_ID>.sock`

The launcher creates the socket path as:
```
$SOCKET_DIR/petaltongue-${FAMILY_ID}.sock
```

**Ask:** Ship `--socket` support in next plasmidBin harvest.

---

## barraCuda — graceful GPU-less survival

**Status:** CRASH on southGate (wetSpring), auto-exit ~34s on southGate (neuralSpring)
**Impact:** 12/13 steady state on GPU-less gates is acceptable, but crash vs
  graceful exit matters for launcher health reporting
**Severity:** LOW (environmental — GPU required for full function)

neuralSpring confirmed that barracuda starts in degraded mode (cpu-shader
only), announces to Neural API, creates `math-southgate.sock`, then
auto-exits after ~34s. This is not a crash — it's intentional shutdown
when no GPU/DRM is available.

**Ask:** Consider adding `BARRACUDA_KEEP_ALIVE=true` or `--no-gpu-exit=false`
flag so headless/GPU-less compositions can keep barracuda alive for
CPU-only tensor ops. Not blocking — documenting for roadmap.

---

## Squirrel — socket name mismatch

**Status:** DOWN on southGate (wetSpring) — "socket not at expected name"
**Impact:** Blocks `ipc.resolve` for AI/inference capabilities
**Severity:** MEDIUM — blocks `ipc.register` seeding for Squirrel

The launcher expects the socket at:
```
$XDG_RUNTIME_DIR/biomeos/squirrel-${FAMILY_ID}.sock
```

Squirrel may be creating its socket with a different naming convention
(e.g. `ai-*.sock` or `mcp-*.sock`). neuralSpring reports Squirrel as
ALIVE on the same gate with the same binaries, so this may be a
socket path discovery issue rather than a Squirrel bug.

**Ask:** Verify Squirrel's UDS socket name matches `squirrel-<FAMILY_ID>.sock`
or document the actual name so the launcher can discover it. If Squirrel
uses capability-based naming (e.g. `ai-nucleus01.sock`), we can add an
alias mapping in the launcher.

---

## ToadStool — health check unresponsive

**Status:** SOCKET on southGate — socket file exists, no `health.check` response
**Impact:** Blocks compute dispatch capability registration
**Severity:** MEDIUM — ToadStool appears to be running but not responding to
  JSON-RPC health probes

The socket `toadstool-<FAMILY_ID>.sock` exists and has a running process
behind it, but neither `health.check` JSON-RPC nor HTTP `/health` returns
a response. neuralSpring reports ToadStool as ALIVE on the same gate.

Possible causes:
1. health.check method not registered (ToadStool uses `ipc.register` 9-cap
   Node Atomic set but may not expose `health.*` namespace)
2. Socket is listening but not accepting connections yet (startup delay)
3. BTSP handshake required before health responds

**Ask:** Ensure ToadStool responds to `{"jsonrpc":"2.0","method":"health.check","params":{},"id":1}`
on its UDS socket. If BTSP auth is required for health probes, document
the expected handshake so the launcher can perform it.

---

## Already resolved (this wave)

| Issue | Fix | Pushed |
|-------|-----|--------|
| `fetch.sh` RECENT_TAGS unbound variable | String→grep -c count | plasmidBin bf5c96b |
| skunkBat missing from launcher STARTUP_ORDER | Added at position 3 (Tower Atomic) | plasmidBin bf5c96b |
| skunkBat missing from primalSpring launcher | Added Phase 1b block | primalSpring 729550a |
| NODE_ID not exported for BearDog | `export NODE_ID` in launcher | plasmidBin bf5c96b |
| NESTGATE_JWT_SECRET not auto-generated | `openssl rand -base64 48` default | plasmidBin bf5c96b |
| skunkBat capability domains not mapped | Added 8-domain mapping | plasmidBin bf5c96b |

## neuralSpring status (for reference)

neuralSpring V176 on same southGate hardware achieved 13/13 started (12/13
steady — barracuda auto-exit without GPU). Key differences from wetSpring:
- neuralSpring killed stale wetSpring processes before deploy
- neuralSpring cleaned sled DB and sockets before launch
- loamSpine Tokio crash: RESOLVED in v0.9.16
- `discovery.peers` still empty after `mesh.init` (Songbird v0.2.1 known issue)
