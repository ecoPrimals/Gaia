# southGate AAR — Wave 157a G68 Convergence + SSH Key Discipline

**Date**: Aug 8, 2026 | **Wave**: 157a | **Gate**: southGate
**Family**: 89df7a2d (southgate-sovereign) | **From**: eastGate overwatch
**Mission**: G68-converged binary redeploy + K-Derm SSH key discipline enforcement

---

## EXECUTIVE SUMMARY

southGate completed full G68 convergence: 12/13 binaries updated from golgi depot,
SSH key discipline enforced (33 GitHub remotes removed, SSH config revoked), and
NUCLEUS restarted clean after identifying and killing a 3,026-process orphan leak.
Tower-Atomic benchmark shows 2.6× latency improvement over pre-G68 binaries.

**Result**: 13/13 GREEN. K-Derm relay chain active. Forgejo-only access. GPU healthy.

---

## TIMELINE

| Time | Event |
|------|-------|
| 09:00 | Cascade initiated — all 33 repos fetched from git.primals.eco |
| 09:01 | NUCLEUS state check reveals 3,026 processes (coralreef/skunkbat respawn leak) |
| 09:01 | Mass kill — all orphaned processes terminated, sockets cleaned |
| 09:02 | G68 binaries pulled from depot.primals.eco (12/13 changed) |
| 09:02 | SSH discipline: 33 GitHub remotes removed from all repos |
| 09:02 | SSH config: GitHub Host entries revoked, Forgejo-only retained |
| 09:03 | Binary deployment to ~/.local/bin/ |
| 09:04 | NUCLEUS launch attempt #1: CLI signature mismatch (G68 changes) |
| 09:04 | Discovery: G68 binaries removed --node-id, --socket-dir; added per-primal --socket |
| 09:05 | NUCLEUS launch attempt #2: 11/13 — beardog needs FAMILY_SEED, nestgate needs JWT |
| 09:05 | beardog restarted with FAMILY_SEED env var (production mode) |
| 09:05 | nestgate restarted with NESTGATE_JWT_SECRET (secure random) |
| 09:06 | 13/13 GREEN confirmed. 42 sockets, 96 MB RSS |
| 09:06 | Tower-Atomic benchmark: 17,314 conn/s, 0.058ms latency |
| 09:06 | GPU health check: RTX 4060 healthy, SHADER_F64 native |
| 09:06 | Head file updated, pushed to overwatch (fa9a4971) |

---

## FINDINGS

### 1. Process Leak (Critical — Fixed)

**Symptom**: 3,026 primal processes running (11 GB RSS reported by naive count).
**Root Cause**: coralreef and skunkbat in a respawn loop. Previous NUCLEUS session
(97h uptime, last restarted Aug 4) had accumulated orphaned child processes that
were not properly reaped on shutdown.
**Fix**: Mass `kill -9` + socket cleanup before fresh deploy.
**Prevention**: G68 binaries appear to use single-process model (no fork). Monitor
on next long-running session.

### 2. G68 CLI Migration (Breaking Change — Adapted)

The G68-converged binaries have a new CLI contract. Key differences from v4.56:

| Old (pre-G68) | New (G68) | Rationale |
|---------------|-----------|-----------|
| `--socket-dir /path/` | `--socket /path/primal.sock` | Per-primal explicit path |
| `--node-id southgate` | *(removed)* | No longer CLI arg |
| `--family-id` sufficient | `FAMILY_SEED` env required | Production security enforcement |
| nestgate starts freely | `NESTGATE_JWT_SECRET` required | No insecure defaults |
| beardog creates `beardog.sock` | Creates `beardog-{family_id}.sock` | Multi-family support |

**Impact**: Any existing launcher scripts (nucleus_launcher.sh) will fail on G68
binaries without update. The per-primal --socket flag and env var requirements are
the new guideStone P1/P4 standard.

### 3. SSH Key Discipline (Enforcement Complete)

| Metric | Before | After |
|--------|--------|-------|
| Repos with GitHub remote | 33 | 0 |
| SSH config GitHub entries | 2 (ecoPrimal, DataScienceBioLab) | 0 |
| Access path to GitHub | Direct SSH | K-Derm relay only |
| Forgejo connectivity | LIVE | LIVE (unchanged) |

**Relay chain now active**:
```
southGate → Forgejo (inner/covalent) → pepti (peptidoglycan) → golgi-ext (outer/ionic) → GitHub
```

### 4. Binary Size Changes (G68 vs Previous)

| Primal | Old (bytes) | New (bytes) | Delta |
|--------|-------------|-------------|-------|
| beardog | 8,662,560 | 8,679,104 | +0.2% |
| songbird | 19,162,592 | 19,306,432 | +0.8% |
| skunkbat | 3,077,472 | 3,401,168 | +10.5% |
| toadstool | 12,962,848 | 14,125,904 | +9.0% |
| barracuda | 11,807,040 | 11,897,344 | +0.8% |
| coralreef | 9,283,424 | 7,874,032 | **-15.2%** |
| nestgate | (same) | (same) | 0% |
| rhizocrypt | 7,938,496 | 8,176,480 | +3.0% |
| loamspine | 4,962,720 | 5,196,512 | +4.7% |
| sweetgrass | 8,716,704 | 8,901,376 | +2.1% |
| biomeos | 16,724,672 | 17,012,768 | +1.7% |
| squirrel | 9,023,584 | 6,590,096 | **-27.0%** |
| petaltongue | 34,895,008 | 31,368,688 | **-10.1%** |

Notable: coralReef (-15%), squirrel (-27%), petalTongue (-10%) all **shrunk**.
This aligns with G68 dead code elimination and dependency pruning.

### 5. Performance Improvement (Tower-Atomic)

| Metric | Pre-G68 (Wave 156d) | G68 (Wave 157a) | Improvement |
|--------|---------------------|-----------------|-------------|
| Avg latency | 0.151 ms | 0.058 ms | **2.6×** |
| Conn/sec | ~6,600 | 17,314 | **2.6×** |
| Transport | TCP loopback | UDS (beardog-89df7a2d.sock) | More efficient |

The UDS transport + G68 optimizations deliver a substantial IPC improvement.

---

## NUCLEUS COMPOSITION — G68 STATE

```
13/13 processes | 42 sockets | 96 MB RSS

Tower Atomic:
  beardog    v0.9.0  — HSM + BTSP + BirdSong genetics (FAMILY_SEED production)
  songbird   v0.2.1  — dual-mode TCP+UDS, federation, dark-forest capable
  skunkbat   (G68)   — BTSP enforcement, UDS-only default

Data Primals:
  toadstool  v0.2.0  — family-scoped, headless compute router
  barracuda  v0.4.0  — C2 dual-socket (JSON-RPC + tarpc), no-gpu-probe (musl)
  coralreef  (G68)   — shader dispatch, -15% binary size
  nestgate   (G68)   — UDS-only, JWT secured, storage capability symlink
  rhizocrypt (G68)   — UDS unconditional, provenance authority

Substrate:
  loamspine  (G68)   — tarpc + JSON-RPC dual protocol
  sweetgrass (G68)   — REST + JSON-RPC + tarpc, UDS-first
  biomeos    v4.57.0 — orchestrator, API on UDS
  squirrel   v0.1.0  — AI routing, -27% binary size
  petaltongue (G68)  — IPC server, -10% binary size
```

---

## DATA BRAID LOCATIONS

| Data | Path | Notes |
|------|------|-------|
| **Primal binaries (musl)** | `~/.local/bin/` | 13 primals, G68-converged |
| **Primal binaries (gnu/GPU)** | `~/.local/bin/gnu/barracuda` | Dynamically linked for Vulkan |
| **NUCLEUS sockets** | `/run/user/1000/biomeos/*.sock` | 42 active sockets |
| **beardog audit** | `/tmp/beardog/audit.log` | HSM + BTSP audit trail |
| **Primal logs** | `/tmp/{primal}.log` | Startup + runtime logs |
| **Family seed** | `$FAMILY_SEED` env (sha256 of gate identity) | Not persisted to disk |
| **SSH config** | `~/.ssh/config` | Forgejo-only, GitHub revoked |
| **Head file** | `infra/wateringHole/heads/southGate.toml` | Pushed (fa9a4971) |
| **This AAR** | `infra/wateringHole/fossilRecord/wave157a_g68_converged_ssh_discipline/` | |
| **Source repos** | `/home/southgate/Development/ecoPrimals/` | 33 repos, all at Forgejo HEAD |
| **GPU benchmarks** | `springs/hotSpring/validation/bin/gpu/` | HMC + precision tiers |
| **guideStone data** | `springs/hotSpring/validation/` | 59/59 passed |
| **arXiv data** | `springs/hotSpring/` | Section 3.4 RTX 4060 row |

---

## SECURITY POSTURE

- **FAMILY_SEED**: Production mode enforced. beardog won't start without it.
- **BTSP**: All 13 primals reject unauthenticated JSON-RPC on UDS.
- **JWT**: nestgate requires secure secret (random 48-byte base64 per-boot).
- **SSH**: No GitHub access. K-Derm relay chain only. Forgejo inner membrane.
- **WireGuard**: Still deliberately OFF (validation gate posture).
- **Federation**: songBird rejecting unknown_family peers on LAN.

---

## LESSONS LEARNED

1. **G68 CLI is a breaking change** — Any launcher scripts must be updated. The
   ecosystem moved from "directory-based socket discovery" to "explicit per-primal
   socket paths". This is cleaner but requires migration awareness.

2. **FAMILY_SEED enforcement is good security** — The old --family-id was just a
   label. Now beardog derives actual cryptographic material from the seed, making
   the identity unforgeable.

3. **Process leaks need monitoring** — 3,026 orphans accumulated silently over 97h.
   Consider a cron/systemd watchdog that alerts if primal process count exceeds N.

4. **Binary shrinkage signals maturity** — squirrel -27%, coralReef -15%,
   petalTongue -10% suggests successful dead code elimination in the G68 audit.

5. **UDS > TCP for local IPC** — 2.6× latency improvement moving from TCP loopback
   to UDS. The G68 default of UDS-first is the correct posture.

---

## NEXT STEPS

| Task | Priority | Status |
|------|----------|--------|
| Springs activation (hotSpring QCD viz) | READY | Awaiting overwatch directive |
| footPrint GIS integration | READY | nestGate + petalTongue alive |
| primalSpring Neural API verification | CAN | biomeOS 4.57.0 deployed |
| nucleus_launcher.sh update for G68 CLI | SHOULD | Current script incompatible |
| FAMILY_SEED persistence (.env or systemd) | SHOULD | Currently ephemeral |
| Process watchdog (cron/systemd) | NICE | Prevent future orphan leaks |

---

*southGate Wave 157a — G68 converged, SSH disciplined, K-Derm enforced, 13/13 GREEN,
0.058ms IPC, 96 MB RSS. Validation gate posture maintained. Ready for work.*
