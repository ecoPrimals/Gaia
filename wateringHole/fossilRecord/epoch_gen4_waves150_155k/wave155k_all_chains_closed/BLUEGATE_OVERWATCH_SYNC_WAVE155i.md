# blueGate — Wave 155i Overwatch Sync Report

**Date**: Jul 29, 2026 12:15 EDT | **Wave**: 155i | **From**: blueGate overwatch
**Gate**: blueGate | **OS**: Windows 10.0.26200 | **Status**: **SYNC COMPLETE. PHASE 0+1 DONE.**

---

## SUMMARY

Fresh gate bootstrap on Windows. Forgejo HTTPS connectivity verified.
Git installed via winget (v2.55.0.3). All 40 repos cloned from Forgejo via
HTTPS (read-only). 39/40 clean checkout, 1 with known Windows limitation
(colon in filenames). No SSH key configured yet — HTTPS sufficient for
initial sync. SSH setup deferred until push access needed for handoff filing.

**Phases completed**: 0 (connectivity), 1 (sync)
**Phases pending**: 2 (WireGuard enrollment, IP 10.13.37.12), 3 (code team)

---

## CLONE INVENTORY — 40/40 REPOS

### primals/ — 15/15 (ecoPrimals org)

| Repo | Status | Branch | Notes |
|------|--------|--------|-------|
| bearDog | OK | main | Clean |
| songBird | OK | main | Clean |
| skunkBat | OK | main | Clean |
| nestGate | OK | main | Clean |
| rhizoCrypt | OK | main | Clean |
| loamSpine | OK | main | Clean |
| sweetGrass | OK | main | Clean |
| toadStool | OK | main | Clean |
| barraCuda | OK | main | Clean |
| coralReef | OK | main | Clean |
| biomeOS | OK | main | Clean |
| squirrel | OK | main | Clean |
| petalTongue | OK | main | Clean |
| sourDough | OK | main | Clean (dormant) |
| bingoCube | OK | main | Clean (dormant) |

### gardens/ — 9/9 (sporeGarden org)

| Repo | Status | Branch | Notes |
|------|--------|--------|-------|
| cellMembrane | OK | main | Clean |
| esotericWebb | OK | main | Clean |
| lithoSpore | OK | main | Clean |
| projectFOUNDATION | OK | main | Clean |
| projectNUCLEUS | OK | main | Clean |
| helixVision | OK | main | Clean |
| initioChem | OK | main | Clean |
| metalForge | OK | main | Clean |
| blueFish | OK | main | Clean |

### springs/ — 9/9 (syntheticChemistry org)

| Repo | Status | Branch | Notes |
|------|--------|--------|-------|
| primalSpring | DIRTY | main | 6 files with colon in filename (IP:port format in `benchScale/tower_shadow/`). Windows cannot create files with `:` in names. Git created truncated versions. **Not a code issue — benchmark data only.** |
| hotSpring | OK | main | Clean |
| wetSpring | OK | main | Clean |
| airSpring | OK | main | Clean |
| groundSpring | OK | main | Clean |
| healthSpring | OK | main | Clean |
| ludoSpring | OK | main | Clean |
| neuralSpring | OK | main | Clean |
| rustChip | OK | main | Clean |

### infra/ — 7/7 (mixed orgs)

| Repo | Status | Branch | Notes |
|------|--------|--------|-------|
| wateringHole | OK | main | Clean (ecoPrimals) |
| plasmidBin | OK | main | Clean (ecoPrimals) |
| fossilRecord | OK | main | Clean (ecoPrimals). Required `core.longpaths=true` + force checkout for deep archive paths. |
| sporePrint | EMPTY | — | No commits on Forgejo. Empty repo (placeholder). (ecoPrimals) |
| whitePaper | OK | main | Clean (ecoPrimals) |
| agentReagents | OK | main | Clean (syntheticChemistry) |
| benchScale | OK | main | Clean (syntheticChemistry) |

---

## ISSUES

### 1. primalSpring colon-in-filename (Windows limitation)

6 benchmark JSON files in `benchScale/tower_shadow/` have IP:port format
in filenames (e.g., `tower-atomic_10_13_37_2:7700_20260723T204413.json`).
Windows NTFS does not allow colons in filenames. Git checked out truncated
versions (cut at colon). The 6 tracked files show as deleted, and 6
untracked truncated files exist.

**Impact**: None — benchmark data only, not executable code.
**Recommendation**: Rename upstream to use underscore instead of colon
(e.g., `tower-atomic_10_13_37_2_7700_20260723T204413.json`).

### 2. fossilRecord deep archive paths

Initial checkout failed due to Windows MAX_PATH (260 char) limit on deeply
nested archive paths under `misc/archive-pre-2026/`. Resolved by enabling
`git config --global core.longpaths true` and force checkout.

**Impact**: None — fully resolved.

### 3. sporePrint empty repo

`infra/sporePrint` is an empty repository on Forgejo (no commits). Cloned
successfully but has no working tree content.

**Impact**: None — placeholder repo.

### 4. SSH not configured

No SSH key exists on this gate. All clones done via HTTPS (read-only).
SSH setup needed before filing handoffs via push.

**Action needed**: Generate `id_ed25519_ecoPrimal`, register in Forgejo.

### 5. Windows LongPathsEnabled registry

OS-level `LongPathsEnabled` is 0 (disabled). Git `core.longpaths` is
enabled but some applications may still hit 260-char limits. Requires
admin to set `HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem\LongPathsEnabled = 1`.

### 6. springs/helixVision missing from layout

The blurb workspace layout lists `springs/helixVision` but no such repo
exists under `syntheticChemistry/` org on Forgejo. `gardens/helixVision`
exists under `sporeGarden/` and cloned successfully. May be a layout
documentation discrepancy.

---

## WORKSPACE STATE

```
ecoPrimals/
├── primals/     15 repos — 15/15 clean
├── gardens/      9 repos —  9/9  clean
├── springs/      9 repos —  8/9  clean (primalSpring: Windows filename limitation)
└── infra/        7 repos —  6/7  clean (sporePrint: empty repo)
                 40 total — 38 clean, 1 Windows-limited, 1 empty
```

**All remotes**: Forgejo HTTPS (`https://git.primals.eco/`)
**All branches**: `main` (except sporePrint — no branch)
**Uncommitted changes**: None (primalSpring dirty is from Windows filename limitation, not local edits)
**Extra directories**: None — canonical layout only

---

## ENVIRONMENT

| Item | Value |
|------|-------|
| OS | Windows 10.0.26200 |
| Git | 2.55.0.3 (winget install) |
| git core.longpaths | true (global) |
| SSH key | Not configured |
| WireGuard | Not installed |
| Rust toolchain | Not checked |
| Forgejo access | HTTPS read-only (verified) |

---

## NEXT STEPS

1. **Phase 2**: WireGuard enrollment (IP 10.13.37.12) — requires human action
2. **Phase 2**: SSH key generation + Forgejo registration — for push access
3. **Phase 2**: Windows LongPathsEnabled registry fix — requires admin
4. **Phase 2**: Tower Atomic deployment (bearDog + songBird + skunkBat)
5. **Phase 3**: Code team spin-up — blueGate full atomic stack (Tower → Nest → Node)

---

*Wave 155i — blueGate sync complete. 40/40 repos from Forgejo. Fresh Windows
gate ready for Phase 2 enrollment and Phase 3 code team work.*
