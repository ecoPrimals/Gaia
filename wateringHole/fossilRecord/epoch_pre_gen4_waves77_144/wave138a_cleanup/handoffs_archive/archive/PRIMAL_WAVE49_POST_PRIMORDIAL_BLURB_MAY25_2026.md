# Upstream Primal Blurb — Wave 49 Post-Primordial

**Date**: May 25, 2026
**From**: primalSpring (eastGate)
**To**: All 13 upstream primals
**Context**: Post-primordial deployment + covalent mesh evolution

---

## What Happened

primalSpring Wave 49 established **post-primordial deployment** as the
ecosystem standard. All primal binaries now come exclusively from
`plasmidBin`. Direct `cargo install`, `target/release/` paths, and
`which` PATH fallbacks have been cut from all launchers and tools.

4 delta springs confirmed compliance (wetSpring V186, ludoSpring Wave 49,
neuralSpring V174, healthSpring V65a). All cut primordial patterns
independently. 4-gate NUCLEUS operational (eastGate, ironGate, southGate,
biomeGate) with Songbird TCP :7700 federation.

## What This Means for Primals

### 1. plasmidBin Is Your Deployment Channel

Your binary in `plasmidBin` is the one every gate runs. If it's stale,
springs get stale behavior. The CI auto-harvest pipeline
(`notify-plasmidbin.yml` → `auto-harvest.yml`) rebuilds on push to `main`.

**Action**: Verify your `notify-plasmidbin.yml` workflow is in your repo's
`.github/workflows/`. If not, copy from `plasmidBin/templates/`.

### 2. Behavioral Convergence Is Enforced

All 13 primals must accept these CLI flags:
- `--socket <path>` — UDS bind path
- `--port <n>` — TCP fallback (opt-in)
- `--family-id <id>` — family namespace

And respond to:
- `health.liveness` → `{"status":"alive"}`
- `lifecycle.status` → operational state
- SIGTERM/SIGINT → graceful shutdown

**Status**: 13/13 compliant. No action needed unless you've regressed.

### 3. New Launcher Features (Affect Songbird)

**Songbird specifically**: The launcher now:
- Feature-guards `--security-socket` (probes `--help` first; older builds
  get `SONGBIRD_SECURITY_SOCKET` env var instead)
- Passes `--bind 0.0.0.0` when `SONGBIRD_FEDERATION_PORT` is set
- Sends `mesh.init` RPC with `SONGBIRD_PEERS` addresses after startup
- Pre-cleans dead sockets before Phase 0

**Ask for Songbird team**: Ensure `mesh.init` with `bootstrap_peers`
parameter triggers peer connection attempts. This is how cross-gate
discovery bootstraps — without explicit seeding, `discovery.peers`
returns empty even when federation is bound.

### 4. Known Pipeline Debt (Primal Teams)

| Issue | Primal | Ask |
|-------|--------|-----|
| musl binary rejects `--family-id` | petalTongue | Rebuild with current CLI parsing; springs work around via `FAMILY_ID` env |
| `--security-socket` flag rejected | Songbird | Feature exists but plasmidBin binary is pre-flag; rebuild or support env var |
| Tokio runtime-in-runtime panic on health probe | loamSpine | Upstream bug — health probe spawns a second runtime inside an existing one |
| sled DB corruption after unclean shutdown | Songbird | Workaround: clean `~/.local/share/songbird/task_lifecycle*`; consider graceful sled flush |
| Slow startup (>8s) on cold launch | rhizoCrypt, sweetGrass, toadStool | Not blocking, but health probes time out; consider lazy init or faster startup |

### 5. Cross-Gate Mesh Status

```
eastGate  ─── 192.168.1.144:7700  (primalSpring, airSpring, groundSpring)
ironGate  ─── 192.168.1.238:7700  (primalSpring, ludoSpring, healthSpring)
southGate ─── 192.168.4.29:7700   (wetSpring, neuralSpring) ← different subnet
biomeGate ─── [IP]:7700           (hotSpring)
```

Same-subnet gates (eastGate ↔ ironGate) can peer directly with
`SONGBIRD_PEERS`. Cross-subnet (southGate) needs network routing or
cellMembrane TURN relay.

### 6. Cell Binary Pattern (Not Primal Concern)

Springs build their own cell binaries (e.g. `healthspring_primal`).
These are NOT in plasmidBin and NOT your responsibility. Only the 13
NUCLEUS primal binaries go through plasmidBin.

---

## Verification

Primals can verify their plasmidBin build is current:

```bash
# Check your binary exists and is the latest
ls -la infra/plasmidBin/primals/x86_64-unknown-linux-musl/YOUR_PRIMAL

# Verify behavioral convergence (from any spring)
echo '{"jsonrpc":"2.0","method":"health.liveness","id":1}' | \
    socat - UNIX-CONNECT:/run/user/1000/biomeos/YOUR_PRIMAL-nucleus01.sock

# Verify federation (Songbird only)
ss -tlnp | grep 7700
echo '{"jsonrpc":"2.0","method":"discovery.peers","params":{},"id":1}' | \
    socat - UNIX-CONNECT:/run/user/1000/biomeos/songbird-nucleus01.sock
```

## Next Steps

1. Primals with pipeline debt: rebuild and push to `main` to trigger
   plasmidBin auto-harvest
2. Songbird: wire `mesh.init` → peer connection if not already done
3. All: no action needed if your `notify-plasmidbin.yml` is active and
   your binary passes behavioral convergence

---

*The mountain is post-primordial. Binary truth flows through plasmidBin.
Springs validate. Primals serve. The mesh is forming.*
