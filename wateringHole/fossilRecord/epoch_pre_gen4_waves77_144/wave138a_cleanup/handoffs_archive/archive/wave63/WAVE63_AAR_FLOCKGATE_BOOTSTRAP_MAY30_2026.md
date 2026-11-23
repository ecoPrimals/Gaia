# AAR: flockGate Wave 63 — Bootstrap Deployment Validation

**Date**: May 30, 2026
**From**: sporePrint team (flockGate)
**To**: primalSpring coordination (eastGate), cellMembrane, all gate teams
**Wave**: 63 (WAN Shadow Bootstrap + sporePrint Team Spinup)
**Classification**: Deployment validation — document all friction for handoff refinement

---

## Summary

flockGate bootstrapped successfully from the WAVE63_SPOREPRINT_TEAM_SPINUP handoff.
**38/38 repos at parity, sporePrint builds (144 pages), pseudoSpore gallery feature
implemented.** However, the bootstrap hit multiple friction points that would block a
less experienced operator. This AAR documents each issue with root cause and fix
recommendation so the handoff + tooling can be hardened for future WAN gate spinups.

**Time to parity**: ~20 minutes of active work, ~10 minutes of clone wait
**Total friction events**: 7

---

## What Worked

| Step | Result |
|------|--------|
| `.gate` identity file | Already present, auto-detected correctly |
| Rust toolchain | Already installed (1.92.0) |
| wateringHole clone from GitHub | Clean, 31s |
| `cascade-pull.sh --check` (post-clone) | 38/38 PARITY, clean temporal matrix |
| `zola build` on sporePrint | 144 pages, 882ms, zero errors |
| `spore-validate validate --check` | 63 entities, 0 errors |
| pseudoSpore gallery feature | Template + content + CSS + Rust subcommand, all passing |

---

## Friction Events

### F1: Forgejo SSH Denied (Blocking)

- **Symptom**: `ssh -p 2222 git@git.primals.eco` → `Permission denied (publickey)`
- **Root cause**: flockGate SSH key not registered on golgiBody Forgejo
- **Impact**: No bidirectional sync. Had to fall back to GitHub-only.
- **Resolution**: Key registered (Forgejo ID 7) — Wave 63 immediate action.
- **Hardening**: Prerequisites section added to handoff and GATE_SETUP_STANDARD.

### F2: cascade-pull.sh Uses HTTPS for GitHub Origin (Blocking)

- **Symptom**: HTTPS clone URLs fail for private repos without token
- **Root cause**: `clone_url` Python function generated `https://github.com/` URLs
- **Impact**: Private repos (springs, bearDog, skunkBat) failed to clone.
- **Resolution**: cascade-pull.sh updated to prefer SSH URLs (`git@github.com:`) when
  SSH agent is available. Added `github_ssh` field to `[sync]` manifest section.

### F3: Large Repos Timeout on Full Clone (Blocking)

- **Symptom**: 7 repos hang at "Cloning into..." for >60s
- **Root cause**: Large repos (bearDog 413K LOC, hotSpring 127K LOC) saturate WAN
- **Impact**: Had to manually `--depth 1` all 7.
- **Resolution**: cascade-pull.sh updated with `--shallow` flag and auto-shallow for
  known large repos. GATE_SETUP_STANDARD documents large repos list.

### F4: No flockGate Profile in ecosystem_manifest.toml (Friction)

- **Symptom**: `cascade-pull.sh --gate flockGate` → `unknown gate "flockGate"`
- **Root cause**: Profile missing from manifest
- **Impact**: Had to manually use `--gate eastGate`.
- **Resolution**: `[gates.flockGate]` added to ecosystem_manifest.toml. Error message
  now suggests closest match and fix instructions.

### F5: primals/ Directory Must Pre-Exist (Friction)

- **Symptom**: Root check fails before `--clone-missing` creates dirs
- **Root cause**: Line 46-49 exit check runs before dir creation
- **Impact**: Had to manually `mkdir -p {primals,springs,gardens,infra}`.
- **Resolution**: cascade-pull.sh now creates workspace dirs when `--clone-missing`
  is set, both at root check and after gate profile load.

### F6: Existing Workspace Collisions — Misplaced Repos

- **Symptom**: Stale `songbird/`, `toadstool/` at workspace root
- **Root cause**: Pre-standard layout clones
- **Impact**: Disk waste (~50MB), confusion (cascade-pull correctly ignored them).
- **Resolution**: Documented in handoff pre-bootstrap cleanup section.
  `rm -rf songbird/ toadstool/` at workspace root.

### F7: --source temporal Default When Forgejo Unreachable (Friction)

- **Symptom**: `git fetch --all` hangs on SSH timeout per-repo
- **Root cause**: temporal mode fetches all remotes including unreachable forgejo
- **Impact**: Would cause massive slowdowns with forgejo remotes configured.
- **Resolution**: cascade-pull.sh now pre-flights Forgejo SSH connectivity and skips
  forgejo remote with warning if unreachable.

---

## Fixes Applied (eastGate Response)

| AAR Item | Fix | Status |
|----------|-----|--------|
| F1: Forgejo SSH key | Registered (ID 7) | DONE |
| F2: HTTPS-only GitHub URLs | SSH URL preference + `github_ssh` manifest field | DONE |
| F3: Large repo timeouts | `--shallow` flag + auto-shallow known large repos | DONE |
| F4: Missing gate profile | `[gates.flockGate]` added, better error messages | DONE |
| F5: primals/ pre-check | mkdir when `--clone-missing` set | DONE |
| F6: Stale repos | Documented in handoff cleanup section | DONE |
| F7: Forgejo unreachable hang | Pre-flight SSH check, skip with warning | DONE |
| Handoff prerequisites | Added to GATE_SETUP_STANDARD + sporePrint handoff | DONE |
| Known large repos list | Added to GATE_SETUP_STANDARD + sporePrint handoff | DONE |

---

## Post-Fix Validation (flockGate)

After pulling eastGate fixes, flockGate validated all 7 and reported two additional bugs:

### F8: f-string quoting in bash-embedded Python (line 124)

- **Symptom**: SyntaxError when `--gate unknownName` triggers error path
- **Root cause**: `{", ".join(known)}` inside f-string inside bash `python3 -c "..."` —
  the `"` in `", "` terminates bash's outer double-quoted string
- **Resolution**: Extract join to variable before f-string (`known_str = ', '.join(known)`)

### F9: Temporal summary count mismatch on shallow repos

- **Symptom**: Matrix shows 38/38 PARITY but summary reports "Parity: 0/38"
- **Root cause**: `temporal_check_repo` output can contain extra lines from git fetch
  warnings on shallow repos. `awk '{print $1}'` picks up warning text instead of
  the PARITY/CONVERGE/DIVERGE status keyword.
- **Resolution**: Use `tail -1` to grab only the last line (actual status), redirect
  stderr from `temporal_check_repo` to /dev/null, and use `grep -E` to match known
  status keywords in temporal sync output.

| AAR Item | Fix | Status |
|----------|-----|--------|
| F8: f-string quoting | Extract join to variable | DONE |
| F9: temporal count | tail -1 + stderr redirect + keyword grep | DONE |

---

## Round 2 — Validation Deployment (F10, F11, F12)

### F10: membrane binary in PATH bypasses --clone-missing (Blocking)

- **Symptom**: Cold-start with membrane installed → synced=1 failed=37, no cloning occurs
- **Root cause**: Membrane delegation path exits before bash clone logic runs
- **Resolution**: Clone missing repos via bash BEFORE delegating to membrane binary.
  Clone loop runs first, then membrane handles temporal sync on the now-present repos.

### F11: Forgejo-first clone produces broken remote wiring (Blocking)

- **Symptom**: Both `github` and `forgejo` remotes point to same Forgejo URL
- **Root cause**: `clone_repo()` tried to add `origin` (already exists), then renamed
  the Forgejo-pointing `origin` to `github`, then failed to rename non-existent `forgejo`
- **Resolution**: Simplified to: (1) rename clone's `origin` to `forgejo`, (2) add
  `origin` pointing to GitHub SSH URL. Two operations, correct wiring.

### F12: `auto` clone source prefers Forgejo over WAN (Friction)

- **Symptom**: WAN clones from Forgejo timeout; GitHub CDN is always faster
- **Root cause**: `clone_url` with `auto` source checked Forgejo first
- **Resolution**: Flipped `auto` to prefer GitHub (CDN edge servers) for initial clones,
  Forgejo as fallback. Ongoing temporal sync uses both remotes regardless.

| AAR Item | Fix | Status |
|----------|-----|--------|
| F10: membrane bypasses clone | Clone before membrane delegation | DONE |
| F11: Forgejo-first remote wiring | Simplified rename→add sequence | DONE |
| F12: auto prefers Forgejo for clone | Flipped to GitHub-first for CDN speed | DONE |

---

## Glacial Shift Criterion #4 Evidence

This bootstrap validates WAN gate spinup:
- Remote node (different city, WAN-only) achieved full workspace parity
- `zola build` succeeds on flockGate (content pipeline over WAN)
- `cascade-pull.sh --check` temporal matrix shows all-parity from WAN
- Code changes (pseudoSpore gallery) developed entirely on WAN node
- Forgejo SSH validated (key ID 7, authenticated as golgiAdmin)
- Forgejo bidirectional push verified (3 repos, 3 orgs)
- membrane binary builds and runs on WAN node (14.5s build)
- Cold-start path validated (dirty, clean, reset)

**Remaining for full criterion #4**: Songbird relay validation,
cross-gate `capability.call` over WAN.

---

## Current flockGate State (Round 2)

```
flockGate workspace: ~/Development/ecoPrimals/
├── .gate = "flockGate"
├── primals/    (14 repos, shallow, origin + forgejo remotes)
├── springs/    (8 repos, shallow, origin + forgejo remotes)
├── gardens/    (8 repos, shallow, origin + forgejo remotes)
├── infra/      (8 repos, shallow except wateringHole, origin + forgejo remotes)

Parity: 38/38 repos at PARITY with origin
Forgejo: CONNECTED, push verified
membrane: built and installed at /usr/local/bin/membrane
Dirty workspace preserved at: ~/Development/ecoPrimals.dirty-wave63/
```
