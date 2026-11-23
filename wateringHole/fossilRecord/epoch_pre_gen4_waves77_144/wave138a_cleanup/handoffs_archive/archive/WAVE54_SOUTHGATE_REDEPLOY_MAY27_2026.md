# Wave 54 — southGate NUCLEUS Redeploy Directive

**Date:** 2026-05-27
**From:** primalSpring (ecosystem validation)
**To:** neuralSpring, wetSpring (southGate co-owners)
**Upstream:** All 4 mountain teams responded to Wave 54 blurbs. Fixes harvested.

---

## Status: READY FOR REDEPLOY

All 7 deployment blockers from the Wave 55 southGate redeploy have been
resolved upstream. Fresh binaries are harvested in plasmidBin. A clean
redeploy should achieve **13/13 started, 12/13 steady** (barracuda GPU-less
auto-exit is environmental, not a bug — see below for keep-alive option).

## What changed since your last deploy

### plasmidBin (bf5c96b → b310310)

| Fix | Commit | Impact |
|-----|--------|--------|
| `fetch.sh` RECENT_TAGS crash | bf5c96b | `fetch.sh --all` no longer crashes under `set -u` |
| skunkBat in launcher STARTUP_ORDER | bf5c96b | skunkBat starts at position 3 (Tower Atomic) |
| `NODE_ID` exported | bf5c96b | BearDog no longer requires manual `NODE_ID` env |
| `NESTGATE_JWT_SECRET` auto-generated | bf5c96b | NestGate JWT secret auto-provisioned if unset |
| petalTongue checksums refreshed | e832f24 | New binary with `--socket` support |
| barraCuda checksums refreshed | 494c1af | New binary with `--no-gpu-probe` |
| Squirrel checksums refreshed | b310310 | New binary with SQ-01 socket fix |

### Primal fixes (all harvested)

| Primal | Issue | Fix | Confidence |
|--------|-------|-----|------------|
| **petalTongue** | Binary rejected `--socket` flag | Global `--socket`/`--port` CLI flags added. Resolution: subcommand > global > env > XDG. Commit `d047dad`. | HIGH — clean implementation, well-documented priority chain |
| **barraCuda** | ~30s startup delay + crash on GPU-less hosts | `--no-gpu-probe` CLI flag and `BARRACUDA_NO_GPU_PROBE` env var. Skips wgpu adapter enumeration, instant degraded startup. 6 new tests. Commit `c55463c3`. | HIGH — targeted fix with proper truthy parsing |
| **ToadStool** | Socket exists, no health response | Early health responder on pre-bound socket. `health.liveness` responds immediately; full handler takes over after executor init (~4-8s). 3 new tests. Commit `3e851517c`. | HIGH — root cause identified (startup timing gap), clean fix |
| **Squirrel** | Socket at unexpected name | SQ-01 filesystem socket now uses `--socket` CLI path instead of re-deriving from env. One-line fix in `jsonrpc_server.rs`. Commit `e14ee9d1`. | HIGH — minimal change, clear root cause |

## Redeploy procedure

### 1. Fetch fresh binaries

```bash
cd $PLASMIBIN_ROOT
git pull
./fetch.sh --all --force
```

This will pull Wave 54 binaries for all primals. `fetch.sh` no longer crashes
on `RECENT_TAGS` (fixed upstream).

### 2. Clean previous NUCLEUS

```bash
pkill -f 'primals/' || true
sleep 2
rm -f ${XDG_RUNTIME_DIR:-/tmp}/biomeos/*.sock
rm -rf ${XDG_RUNTIME_DIR:-/tmp}/biomeos/songbird_sled_*
```

Cleaning sled DB prevents stale peer/registry state from previous deploys.

### 3. Launch NUCLEUS

```bash
./nucleus_launcher.sh \
  --family-id <YOUR_FAMILY_ID> \
  --composition full
```

The launcher now:
- Exports `NODE_ID` automatically (hostname-derived)
- Auto-generates `NESTGATE_JWT_SECRET` if unset
- Starts skunkBat at position 3 (Tower Atomic)
- Passes `--socket` to all primals (including petalTongue)

### 4. Optional: Songbird federation

```bash
export SONGBIRD_FEDERATION_PORT=7700
export SONGBIRD_PEERS=192.168.1.144:7700    # eastGate
./nucleus_launcher.sh \
  --family-id <YOUR_FAMILY_ID> \
  --composition full \
  --peers 192.168.1.144:7700
```

### 5. Optional: barraCuda keep-alive on GPU-less hosts

To keep barraCuda alive for CPU tensor ops instead of auto-exit:

```bash
export BARRACUDA_NO_GPU_PROBE=true
```

Set before launching. This skips the ~30s wgpu probe and keeps the
process alive indefinitely in cpu-shader-only mode.

## Expected results

| Metric | Without GPU keep-alive | With GPU keep-alive |
|--------|----------------------|---------------------|
| Primals started | 13/13 | 13/13 |
| Steady state | 12/13 (barracuda auto-exit) | 13/13 |
| Health responding | 12/13 | 13/13 |
| UDS sockets | 30+ | 30+ |

### Per-primal expected status

| Primal | Expected | Notes |
|--------|----------|-------|
| beardog | ALIVE | Auto-picks NODE_ID from hostname |
| songbird | ALIVE | TCP federation if SONGBIRD_FEDERATION_PORT set |
| skunkbat | ALIVE | Now in launcher (position 3) |
| toadstool | ALIVE | Early health responder responds immediately |
| barracuda | ALIVE or auto-exit | Set BARRACUDA_NO_GPU_PROBE=true for keep-alive |
| coralreef | ALIVE | Unchanged |
| nestgate | ALIVE | JWT auto-generated |
| squirrel | ALIVE | Socket at launcher-specified path (SQ-01 fixed) |
| rhizocrypt | ALIVE | Unchanged |
| loamspine | ALIVE | Tokio crash fixed in v0.9.16 (prior wave) |
| sweetgrass | ALIVE | Unchanged |
| biomeos | ALIVE | Unchanged |
| petaltongue | ALIVE | Now accepts --socket flag |

## Remaining known issues (not blocking)

1. **Songbird `discovery.peers`** returns empty after `mesh.init` (v0.2.1) —
   Songbird team tracking, does not block deployment or health
2. **barracuda GPU-less auto-exit** — environmental, use `BARRACUDA_NO_GPU_PROBE`
   as workaround if CPU tensor ops needed
3. **4 primals not in release** (rhizocrypt, sweetgrass, petaltongue, squirrel
   may use older binaries on some arches) — existing binaries work, next
   full harvest will include all 13

## Validation after deploy

```bash
# Quick health sweep
for p in beardog songbird skunkbat toadstool barracuda coralreef \
         nestgate squirrel rhizocrypt loamspine sweetgrass biomeos petaltongue; do
  SOCK="${XDG_RUNTIME_DIR:-/tmp}/biomeos/${p}-${FAMILY_ID}.sock"
  printf "%-14s " "$p"
  echo '{"jsonrpc":"2.0","method":"health.liveness","id":1}' | \
    timeout 3 socat - "UNIX-CONNECT:$SOCK" 2>/dev/null | head -1 || echo "DOWN"
done
```

Report results back to wateringHole. Target: 12/13 minimum, 13/13 with
`BARRACUDA_NO_GPU_PROBE=true`.
