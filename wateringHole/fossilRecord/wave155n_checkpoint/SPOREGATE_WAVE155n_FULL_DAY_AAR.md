# sporeGate Wave 155n — Full Day AAR

**Date**: Jul 31, 2026 17:35 EDT | **From**: sporeGate | **Wave**: 155n
**Posture**: 11/11 HEALTHY | 5 cascades | 46 depot binaries | sporePrint LIVE

---

## Session Overview

5 cascades across 5 hours. Major deployments: biomeOS v4.55 mode gap fix →
biomeOS v4.56 G22 convergence → cellMembrane P2 platform fix → sporePrint
published → GNU depot completed. Gate stable at 11/11 throughout.

| Cascade | Time | Key Delivery |
|---------|------|--------------|
| 1 | 12:34 | biomeOS mode gap fix (652cf8a7) — composition.test_swap E2E VALIDATED |
| 2 | 12:45 | biomeOS v4.55 deployed, mode gap confirmed on neural-api socket |
| 3 | 13:41 | biomeOS v4.56 G22 convergence + cellMembrane P2 platform fix |
| 4 | 14:04 | sporePrint published — 313 pages, demonstration era |
| 5 | 17:16 | GNU depot completed — 5→15 binaries, 46 total across 3 platforms |

---

## What Worked

### 1. Mode Gap Fix (652cf8a7) — VALIDATED

The critical coevolution fix. Neural API now accepts plain JSON-RPC
(`btsp_optional=true`) AND registers `composition.test_swap`. E2E path:

```
cellMembrane validate_with_deps()
  → neural-api socket (plain JSON-RPC)
  → biomeOS composition.test_swap
  → candidate probe + result
```

Proven with live socat tests on sporeGate. This closes G21 (coevolution).

### 2. G22 Convergence Steps 1+2 (v4.56)

biomeOS shipped the first two G22 steps in one wave:
- Step 1: Begin unifying api + neural-api capabilities
- Step 2: Unified socket namespace — all paths use `membrane/`
- 244 capabilities registered (up from 51 in v4.55)
- 47 dead dependencies removed

Backward-compatible: all existing API paths continue working.

### 3. P2 Platform Detection Fix (d7026d7)

cellMembrane `detect_target_triple` now uses `Platform::detect()` at runtime
instead of embedding the build host's target triple. This unblocks J12
(blueGate sub-builder).

### 4. sporePrint Published

22 commits, conceptual era → demonstration era:
- "NUCLEUS Is Running" hero
- Lab | Science | Architecture | Products | Get Started nav
- 47 foundation pages archived
- 4 VALIDATED badges on baseCamp papers
- 313 pages, 23 sections, search index

### 5. GNU Depot Complete

Built 10 missing GNU targets. Depot: 16 musl + 15 gnu + 15 windows = 46 binaries.
This unblocks strandGate (GPU, needs glibc) and steamGate (SteamOS, Arch-based).

---

## Divergences Still Open

### D1: Socket Evaporation on biomeOS Restart — RECURRING

**What happens**: Restarting `membrane-biomeos.service` or `membrane-neural-api.service`
clears primal sockets in `/run/membrane/`. All primal services must be restarted to
regenerate their sockets.

**Evidence**: Cascade 2 — restarted biomeOS services to deploy mode gap fix. 8 primal
sockets disappeared. Required `systemctl restart` of all affected primal services.

**Root cause**: biomeOS's RuntimeDirectory management. The PID ownership guard (v4.55)
prevents biomeOS from deleting sockets *during runtime*, but a full service restart
still clears the RuntimeDirectory.

**Owner**: biomeOS (G22 step 4)
**Resolution path**: G22 step 3 (single-process merge) eliminates the dual-service
restart. G22 step 4 (biomeOS owns `/run/membrane` lifecycle) ensures socket persistence.

### D2: `/run/membrane` Permission Reset — RECURRING

**What happens**: biomeOS resets `/run/membrane` to `0770 root:membrane` on connection.
User-space `membrane gate.status` gets "Permission denied" connecting to neural-api socket.

**Evidence**: Every cascade that restarts biomeOS services. Workaround: `sudo chmod 0777`
on sockets, or run `gate.status` with `sudo`.

**Owner**: biomeOS
**Resolution path**: G22 step 4 — biomeOS should set permissive socket mode (0666 or
0660 with proper group membership) rather than restrictive 0770.

### D3: checksums.toml Format Drift — RECURRING

**What happens**: The `depot.integrity` probe expects section headers like
`[x86_64-unknown-linux-musl]` but manual regeneration has produced wrong formats:
- `[primals/x86_64-unknown-linux-musl]` (path as key — TOML parse error)
- `["primals/x86_64-unknown-linux-musl"]` (quoted path — wrong section name)

**Evidence**: Cascade 2 — two failed `depot.integrity` checks before getting format right.

**Owner**: sporeGate / cellMembrane
**Resolution path**: Codify checksum regeneration in `membrane plasmid.finalize` or a
`depot.seal` command. Currently manual and error-prone.

### D4: Candidate Self-Test Probe Fails — P3

**What happens**: `composition.test_swap` dispatches correctly but the candidate binary
self-test always fails because the candidate can't start in isolation (needs FAMILY_ID,
socket paths, etc.).

**Evidence**: Cascade 2 — `composition.test_swap` for squirrel returns
`{"validated":false,"reason":"Candidate probe failed: composition.self_test call to candidate failed"}`.

**Owner**: biomeOS
**Resolution path**: Either:
- Lightweight version-check probe (don't start candidate, just verify binary version)
- Env passthrough for candidate (FAMILY_ID, socket paths)
- biomeOS "canary" mode for candidate testing

### D5: Sovereign CI Source Tree Divergence — P3

**What happens**: The sovereign CI trigger builds from `/opt/ecoPrimals` (root's source
tree) which can be stale. User's `~/Development` tree has the latest code.

**Evidence**: Previous session — CI trigger built old biomeOS version and overwrote
v4.55 in the depot. Had to manually restore correct binaries.

**Owner**: sporeGate
**Resolution path**: CI trigger needs `git pull` before `cargo build`. Or: CI trigger
should use the same source tree as the user, or a dedicated always-current tree.

### D6: Dual-Service Architecture — Transitional Scaffold

**What happens**: biomeOS runs as two separate systemd services:
- `membrane-biomeos.service` (api mode, riboCipher only)
- `membrane-neural-api.service` (neural-api mode, btsp_optional=true)

This means two sockets (`biomeos.sock`, `neural-api.sock`), two processes,
and restarts affect both independently.

**Evidence**: The entire mode gap saga. The `api` socket rejects plain JSON-RPC.
The `neural-api` socket accepts both but historically lacked some api-mode methods.

**Owner**: biomeOS (G22 step 3)
**Resolution path**: Merge into single process. One socket. One systemd unit. biomeOS
v4.56 steps 1+2 prove this is achievable — 244 capabilities already unified.

### D7: sporePrint Publish Not Automated — P3

**What happens**: Publishing sporePrint requires manual SSH to golgi → `git pull` →
`zola build`. Content can be pushed to Forgejo but the static site won't update.

**Evidence**: Cascade 4 — manual publish worked cleanly but requires human intervention.

**Owner**: sporeGate
**Resolution path**: Forgejo post-receive hook on sporePrint repo → `zola build`.
Same pattern as `30-sovereign-ci` hook for primal repos.

### D8: Neural API Capability Routing Gaps

**What happens**: `membrane gate.status` reports "Capability 'X' not registered" for
several primals (songbird, skunkbat, petaltongue, toadstool, barracuda, coralreef,
beardog) when routing through neural-api. Also "read timeout" for others.

**Evidence**: Every `gate.status` run shows WARN lines. The probes still pass because
they fall back to direct socket checks, but the neural-api routing is incomplete.

**Owner**: biomeOS (G22)
**Resolution path**: G22 convergence — primals need to register their capabilities
with the neural-api coordinator. Currently only biomeOS-native capabilities are registered.

### D9: `nucleus_launcher` GNU Build Missing

**What happens**: `nucleus_launcher` is in the musl depot (16 bins) but not in the
GNU depot (15 bins). It's part of the biomeOS workspace as `biomeos-nucleus` but
doesn't produce a standalone binary from the GNU build.

**Evidence**: Cascade 5 — couldn't find the binary in the biomeOS GNU release dir.

**Owner**: biomeOS / sporeGate
**Resolution path**: Either extract from biomeOS build or create a standalone crate.
Low priority — it's only needed for NUCLEUS bootstrap, and musl works everywhere.

### D10: Zola Warnings — 4 Lab Pages

**What happens**: 4 lab validation summary pages lack `date` or `weight` in a sorted
section, producing build warnings.

**Evidence**: Cascade 4 — `zola build` output.

**Owner**: sporePrint
**Resolution path**: Add `date` or `weight` frontmatter to the 4 pages. Trivial fix.

---

## Convergence Status

### CONVERGED (this session)

| Item | How |
|------|-----|
| Mode gap (G21) | biomeOS 652cf8a7 — btsp_optional=true in neural-api |
| P2 platform detection | cellMembrane d7026d7 — Platform::detect |
| Socket namespace | biomeOS G22 step 2 — all paths use membrane/ |
| GNU depot | sporeGate — 5→15 binaries |
| sporePrint | Published — demonstration era |

### CONVERGING (in progress)

| Item | Owner | Next Step |
|------|-------|-----------|
| G22 single-process merge | biomeOS | Step 3: merge api + neural-api |
| Socket evaporation (D1) | biomeOS | Resolved by G22 step 3+4 |
| Permission reset (D2) | biomeOS | Resolved by G22 step 4 |
| Neural-api routing (D8) | biomeOS | Primal capability registration |
| J12 sub-builder | sporeGate | songBird IPC wire |
| J18 gate coupling | cellMembrane | /etc/environment abstraction |

### NEEDS EVOLUTION (not yet started)

| Item | Owner | What's Needed |
|------|-------|---------------|
| checksums.toml automation (D3) | sporeGate/cellMembrane | `depot.seal` command |
| Candidate self-test (D4) | biomeOS | Lightweight probe or env passthrough |
| CI source tree (D5) | sporeGate | `git pull` in CI trigger |
| sporePrint auto-publish (D7) | sporeGate | Forgejo post-receive hook |
| Zola warnings (D10) | sporePrint | Frontmatter fix (trivial) |

---

## Recommendations to Overwatch

1. **biomeOS G22 step 3 is the critical path.** Single-process merge resolves D1, D2,
   D6, and D8 simultaneously. This should be the biomeOS team's sole focus until shipped.

2. **J12 sub-builder wire is sporeGate's next task.** All blockers are cleared (P2 fix,
   membrane.exe LIVE). Need songBird IPC message format for build dispatch.

3. **sporePrint auto-publish (D7) is a quick win.** Same hook pattern as sovereign CI.
   Can be wired in one session.

4. **checksums.toml and CI source tree (D3, D5) are operational debt.** Not blocking
   anything but cause manual rework on every depot rebuild. Should be codified before
   the springs+gardens phase creates more build frequency.

5. **southGate validation is the best proof of the deployment story.** An off-mesh gate
   deploying from public depot with its own genetic lineage proves the entire
   architecture works for external users.

---

## Score

| Dimension | Status |
|-----------|--------|
| Gate health | **11/11 HEALTHY** — stable all day |
| Depot | **46 binaries** — 16 musl + 15 gnu + 15 windows |
| biomeOS | **v4.56** — G22 convergence, 244 caps |
| cellMembrane | **d7026d7** — P2 FIXED, registry hardened |
| sporePrint | **LIVE** — 313 pages, demonstration era |
| Coevolution (G21) | **COMPLETE** |
| G22 convergence | **40%** — steps 1+2 done, 3-5 remain |
| Jelly strings | **9/11 KILLED** — J12 UNBLOCKED, J18 open |
| Open divergences | **10** (2 recurring, 4 P3, 4 need evolution) |

---

*sporeGate 155n full day AAR — 5 cascades, 46 depot binaries, biomeOS v4.56,
sporePrint LIVE. 10 divergences documented: D1-D2 resolve with G22, D3-D5-D7
are sporeGate operational debt, D4-D6-D8 resolve with biomeOS single-process
merge. Recommendation: G22 step 3 is the critical path for springs+gardens.*
