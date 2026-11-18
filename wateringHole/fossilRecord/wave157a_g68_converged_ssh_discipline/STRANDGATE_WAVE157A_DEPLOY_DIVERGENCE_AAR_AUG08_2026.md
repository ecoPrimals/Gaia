# AAR: strandGate Wave 157a — Deploy Divergence (RESOLVED)

**Date**: 2026-08-08 09:00→10:00 | **Gate**: strandGate | **Wave**: 157a
**Status**: **RESOLVED** — G68 deployed. 13/13 ALIVE. rsync from golgi `/srv/depot/`.

---

## Problem Statement

strandGate cannot redeploy G68-converged primal binaries from the golgi depot.
sporeGate successfully redeployed (3 cascade cycles, 13/13 ALIVE, S369 deployed).
strandGate is stuck on `v2026.05.30` binaries (June 15 generated, 2+ months stale).

---

## Root Cause

| Component | strandGate | sporeGate |
|---|---|---|
| Depot access | `plasmid.fetch --source github` | Direct filesystem (golgi is co-located) |
| GitHub release | `v2026.05.30` (STALE, assets failing) | N/A — doesn't use GitHub for deploy |
| Forgejo API | `--source forgejo` → "parse: release API parse failed" | N/A |
| Direct SSH to golgi | **NO** (only port 2222 for git) | **YES** (local or SSH shell access) |
| Local build | Possible but not deploy pattern | Not used for deploy either |

**The K-Derm relay chain has a gap**: golgi-ext hasn't pushed a modern release to GitHub,
and strandGate has no alternative path to the golgi musl depot.

---

## What strandGate Has (Forgejo-current)

| Repo | Status | Origin Parity |
|---|---|---|
| hotSpring | `acf63c7` — NPU hw feature enabled | origin=current, github+27 |
| toadStool | `3f75aa5e7` — neuromorphic absorption | origin=current, github+84 |
| whitePaper | `deb41fe` — silicon continuum + upstream merge | origin=current |
| wateringHole | `c331a318` — Wave 157a absorbed | origin=current |

All source is at Forgejo HEAD. The **code** is current. The **deployed binaries** are not.

---

## What Works on strandGate (Local Execution)

Despite the deploy divergence, all local science systems are fully operational:

| System | Status |
|---|---|
| SU(3) thermalization (32⁴) | **COMPLETE** — 36 configs, 4.5 GB, PID exited |
| SU(4) thermalization (16⁴+24⁴) | **RUNNING** — 3/6 done, ETA ~21:00 today |
| NPU hardware (AKD1000) | **LIVE** — 2 µs/sample, 100% accuracy via `npu-hw` feature |
| GPU DF64 compute | **OPERATIONAL** — RTX 3090 + RX 6950 XT |
| MILC interop | **VALIDATED** — bidirectional Δ⟨P⟩ = 3×10⁻⁹ |
| Preprint | **41/42** — science complete, trust surface blocks send |

The divergence is **only** on the primal binary deployment layer, not on science compute.

---

## Resolution Options (for upstream)

### Option A: golgi-ext pushes a modern GitHub release (PREFERRED)

golgi-ext (`outer membrane`) pushes a new tagged release (e.g., `v2026.08.08-g68`) with all
17 musl binaries as assets. strandGate then runs `membrane plasmid.fetch --force` and deploys.

**Owner**: golgi-ext team / overwatch
**Effort**: Minutes (assets already built, need release + upload)

### Option B: Add Forgejo release API support to `membrane plasmid.fetch`

The `--source forgejo` path errors on API parse. Fix the membrane binary to handle
Forgejo's release API format (slightly different from GitHub's).

**Owner**: membrane team (nestGate? loamSpine?)
**Effort**: Small code change in membrane binary

### Option C: Add scp/rsync depot pull path for remote gates

strandGate gets SSH shell access to golgi depot directory and pulls binaries directly:
```
rsync golgi:/srv/depot/musl/ ~/.local/share/ecoPrimals/plasmidBin/primals/x86_64-unknown-linux-musl/
```

**Owner**: golgi/sporeGate ops
**Effort**: SSH key + rsync script

### Option D: strandGate builds from source (NOT deploy pattern)

Build toadStool, primals locally from source. Works but violates the deploy-from-depot
pattern and makes strandGate a special case.

**Owner**: strandGate (local)
**Effort**: ~5-10 min per primal build
**Status**: REJECTED by user — we deploy, not build

---

## Immediate Ask

**To golgi-ext team / overwatch**: Push a modern GitHub release (`v2026.08.08-g68` or
similar) with musl binaries so `membrane plasmid.fetch` resolves for strandGate
(and any other remote gates without direct golgi filesystem access).

**Alternative**: Configure an SSH shell host entry for strandGate → golgi so we can
rsync the depot directly.

---

## What strandGate Continues With (Unblocked)

- SU(4) thermalization (running, ETA tonight)
- NPU experiments (hardware live, `npu-hw` feature wired)
- Preprint updates (silicon continuum integrated)
- petalTongue visualization pipeline (source current)
- Local `cargo run` for all hotSpring binaries (source builds work for science)

The deploy divergence blocks **primal service deployment** (the NUCLEUS mesh) on strandGate,
not science compute. Escalating to overwatch for resolution.

---

## Resolution (10:00)

**Root cause confirmed**: `plasmid.fetch --source forgejo` looks for Forgejo *releases* API,
but the G68 depot is a filesystem at `/srv/depot/primals/x86_64-unknown-linux-musl/` on golgi.
No release object exists — binaries are served via rsync/scp.

**Fix applied**: SSH key to golgi was already configured. Direct rsync from depot:
```
rsync -avz golgi:/srv/depot/primals/x86_64-unknown-linux-musl/ \
  ~/.local/share/ecoPrimals/plasmidBin/primals/x86_64-unknown-linux-musl/
```

Then standard deploy: stop target → replace binaries → start target.

**Result**: 13/13 ALIVE. biomeOS 4.57.0. toadStool 0.2.0. All binaries Aug 8 from golgi depot.

**For future gates**: The `plasmid.fetch --source forgejo` path expects a *Forgejo release*.
The actual depot is filesystem-based at `/srv/depot/`. Remote gates without co-located
access should use `rsync golgi:/srv/depot/...` or the relay chain should wrap this in
`plasmid.fetch --source vps` (which may already exist but needs SSH config).

---

*strandGate AAR — Wave 157a DEPLOY DIVERGENCE → RESOLVED. G68 deployed via rsync from
golgi `/srv/depot/`. 13/13 ALIVE. biomeOS 4.57.0, toadStool 0.2.0. Science systems
unblocked throughout. SU(3) campaign COMPLETE (36 configs). SU(4) in progress. NPU live.*
