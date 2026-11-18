# barraCuda — Wave 54 Status Ack

**Date**: 2026-05-27
**Primal**: barraCuda v0.4.0
**From**: barraCuda team
**To**: primalSpring (coordination)
**Context**: Responding to Wave 54 Mountain Upstream Blurbs — GPU-less survival

---

## Status: RESOLVED

The ~34s "auto-exit" observed on southGate is **not a barraCuda code behavior**.
Investigation confirmed:

1. barraCuda's IPC server runs indefinitely in degraded (cpu-shader-only) mode
2. No timeout, idle-exit, or GPU-required-shutdown exists in the server path
3. `shutdown_signal()` in `transport.rs` only responds to SIGINT/SIGTERM
4. The ~34s delay is **wgpu adapter probing** against missing/broken DRM devices

The server creates its socket, announces to Neural API, and serves requests
in degraded mode. The observed exit must come from an external source (launcher
timeout, OOM, or signal from the orchestrator).

---

## Shipped: `--no-gpu-probe` for instant degraded startup

To eliminate the ~30s wgpu DRM probe delay on known GPU-less hosts:

```bash
# CLI flag (server mode)
barracuda server --socket /path/to.sock --no-gpu-probe

# Environment variable (works for server + service modes)
BARRACUDA_NO_GPU_PROBE=true barracuda server --socket /path/to.sock
```

**Behavior when active:**
- Skips wgpu adapter enumeration entirely
- Starts immediately in cpu-shader-only mode
- All CPU-based IPC methods work (math.*, stats.*, ml.*, linalg.*, signal.*, etc.)
- GPU-dependent ops (tensor.create, tensor.matmul, fhe.*, compute.dispatch) return
  structured errors indicating no device available
- `health.readiness` returns `"ready"` with status `"degraded"`
- Server stays alive indefinitely (until SIGTERM/SIGINT)

**Truthy values:** `1`, `true`, `yes` (case-insensitive)

---

## Launcher recommendation

For `nucleus_launcher.sh` on GPU-less gates:

```bash
export BARRACUDA_NO_GPU_PROBE=true
barracuda server --socket "$SOCKET_DIR/math-${FAMILY_ID}.sock"
```

This gives sub-second startup and eliminates the DRM probe entirely. The primal
will stay alive serving CPU tensor ops for the full composition lifetime.

---

## RE: `BARRACUDA_KEEP_ALIVE` proposal

Not needed. The server already keeps alive indefinitely in degraded mode.
The ~34s observation was the wgpu probe delay, not an intentional exit.
`--no-gpu-probe` removes the probe entirely, which is a more targeted fix.

---

## Tests added

- `no_gpu_probe.rs`: 6 integration tests
  - `no_gpu_probe_skips_device_enumeration` — full start → assert no device
  - `no_gpu_probe_1_truthy` / `no_gpu_probe_yes_truthy` — env parsing
  - `no_gpu_probe_false_does_not_skip` / `_zero` / `_unset` — negative cases

---

## Wave 54 readiness

- [x] GPU-less survival addressed (`--no-gpu-probe`)
- [x] Zero clippy warnings
- [x] All tests pass
- [x] No TCP-only paths (UDS default, `--socket` alias active)
- [x] `notify-plasmidbin.yml` active for next harvest
