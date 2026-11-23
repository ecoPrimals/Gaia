# AAR: flockGate Wave 63 — Bootstrap Deployment Validation

**Date**: May 30, 2026
**From**: sporePrint team (flockGate)
**To**: primalSpring coordination (eastGate), cellMembrane, all gate teams
**Wave**: 63 (WAN Shadow Bootstrap + sporePrint Team Spinup)
**Classification**: Deployment validation — document all friction for handoff refinement

---

## Summary

flockGate bootstrapped successfully from the WAVE63_SPOREPRINT_TEAM_SPINUP handoff. **38/38 repos at parity, sporePrint builds (144 pages), pseudoSpore gallery feature implemented.** However, the bootstrap hit multiple friction points that would block a less experienced operator. This AAR documents each issue with root cause and fix recommendation so the handoff + tooling can be hardened for future WAN gate spinups.

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

## What Didn't Work — Friction Events

### F1: Forgejo SSH Denied (Blocking)

**Symptom**: `ssh -p 2222 git@git.primals.eco` → `Permission denied (publickey)`

**Root cause**: flockGate's SSH key (`ssh-ed25519 ...IMf+uvSv...ecoPrimal@pm.me`) was never registered on golgiBody Forgejo. The handoff *mentions* this ("ask eastGate to add it via the Forgejo API") but presents it as a parenthetical, not as a prerequisite gate.

**Impact**: Cannot use `--source temporal` or `--source forgejo`. Had to fall back to GitHub-only cloning. No bidirectional sync possible until key is registered.

**Fix for handoff**: Add explicit prerequisite section at top:
```
## Prerequisites (do BEFORE starting)
- [ ] flockGate SSH pubkey registered on golgiBody Forgejo (API: POST /api/v1/user/keys)
- [ ] Verify: ssh -p 2222 git@git.primals.eco → "Hi <user>! ..."
```

**Fix for tooling**: `cascade-pull.sh` should test Forgejo connectivity at the start when `--source temporal` or `--source forgejo` is used, and fail fast with a helpful message instead of hanging.

---

### F2: cascade-pull.sh Uses HTTPS for GitHub Origin (Blocking)

**Symptom**: `cascade-pull.sh --gate eastGate --clone-missing --source origin` → clones fail silently

**Root cause**: The `clone_url` Python function generates `https://github.com/<org>/<repo>.git` for origin source. HTTPS requires a token for private repos. SSH (`git@github.com:<org>/<repo>.git`) works via the registered key, but the script doesn't use it.

**Impact**: cascade-pull couldn't clone private repos (springs, bearDog, skunkBat). Had to write a manual batch clone script using SSH URLs.

**Fix for manifest/tooling**: Add a `github_ssh` field to `[sync]`:
```toml
[sync]
github_ssh = "git@github.com:"
```
And have `clone_url` prefer SSH when the environment has SSH agent loaded:
```python
elif source == 'origin' and gr:
    if ssh_available:
        print(f'git@github.com:{gr}.git')
    else:
        print(f'https://github.com/{gr}.git')
```

---

### F3: Large Repos Timeout on Full Clone (Blocking)

**Symptom**: bearDog, songBird, toadStool, petalTongue, hotSpring, sporePrint, rustChip all hang at "Cloning into..." for >60s, then timeout.

**Root cause**: These repos are large (bearDog 413K LOC/2226 files, hotSpring 127K LOC/2562 files). Full clone over WAN SSH saturates bandwidth or hits GitHub's connection limits.

**Impact**: Had to `--depth 1` all 7. History unavailable without `git fetch --unshallow`.

**Fix for handoff**: Document the known-large repos:
```
## Known Large Repos (shallow clone recommended for WAN)
bearDog, songBird, toadStool, petalTongue, hotSpring, sporePrint, rustChip
```

**Fix for tooling**: `cascade-pull.sh --clone-missing` should accept `--shallow` flag that passes `--depth 1` to git clone. The peptidoglycan deployment already does this (noted in WAVE63_KDERM_DIDERM_DEPLOYMENT: "39 repos cloned (--depth 1 for bloated)").

---

### F4: No flockGate Profile in ecosystem_manifest.toml (Friction)

**Symptom**: `cascade-pull.sh --gate flockGate` → Python errors: `unknown gate "flockGate"`

**Root cause**: The handoff says "flockGate doesn't have its own profile yet — use eastGate's full set." This requires the operator to know to pass `--gate eastGate` instead. The `.gate` file says `flockGate`, the auto-detect resolves to `flockGate`, but the manifest doesn't have it.

**Impact**: Confusing error. Had to read the manifest to understand and use `--gate eastGate`.

**Fix for manifest**: Add flockGate profile (same as eastGate for now):
```toml
[gates.flockGate]
repos = [...]  # same as eastGate
```

---

### F5: primals/ Directory Must Pre-Exist (Friction)

**Symptom**: `cascade-pull.sh` fails with `ERROR: cannot find ecoPrimals root (tried ...)` on fresh workspace.

**Root cause**: Line 46-49 of cascade-pull.sh:
```bash
if [[ ! -d "$ECOPRIMALS_ROOT/primals" ]]; then
    echo "ERROR: cannot find ecoPrimals root..."
    exit 1
fi
```
This check runs before `--clone-missing` has a chance to create the directory.

**Impact**: Had to manually `mkdir -p {primals,springs,gardens,infra}` before running cascade-pull.

**Fix for tooling**: When `--clone-missing` is set, create the directory structure before the check:
```bash
if $CLONE_MISSING; then
    mkdir -p "$ECOPRIMALS_ROOT"/{primals,springs,gardens,infra}
fi
```

---

### F6: Existing Workspace Collisions — Misplaced Repos

**Symptom**: `songbird/` and `toadstool/` exist at workspace root (`~/Development/ecoPrimals/songbird/`, `~/Development/ecoPrimals/toadstool/`), NOT at the standard paths (`primals/songBird/`, `primals/toadStool/`).

**Root cause**: These were cloned before the standard workspace layout was established. They use lowercase naming (`songbird` not `songBird`) and wrong parent directory (root, not `primals/`).

**Impact**: 
- cascade-pull correctly ignored them (checks `primals/songBird/.git` not `songbird/.git`)
- Fresh clones went to the correct paths
- Stale copies remain at root, wasting ~50MB disk and causing confusion

**Disposition**: Should be removed. They are superseded by `primals/songBird/` and `primals/toadStool/`:
```bash
rm -rf ~/Development/ecoPrimals/songbird ~/Development/ecoPrimals/toadstool
```

**Fix for handoff**: Add cleanup step for known stale layouts:
```
## Pre-Bootstrap Cleanup
If this gate previously had repos cloned at non-standard paths, remove them:
  rm -rf ~/Development/ecoPrimals/songbird   # superseded by primals/songBird/
  rm -rf ~/Development/ecoPrimals/toadstool  # superseded by primals/toadStool/
```

**Fix for tooling**: `cascade-pull.sh --check` could scan for repos at non-standard paths and warn.

---

### F7: --source temporal Default When Forgejo Unreachable (Friction)

**Symptom**: The manifest `[sync] default_source = "temporal"` means `cascade-pull.sh` defaults to temporal mode, which fetches ALL remotes including Forgejo. When Forgejo is unreachable, this doesn't fail fast — it hangs on SSH connection attempts per-repo.

**Root cause**: `temporal` mode calls `git fetch --all` which tries every configured remote. With no Forgejo access, each fetch attempt waits for SSH timeout.

**Impact**: Would have caused massive slowdowns if repos already had forgejo remotes configured. Avoided because fresh clones from GitHub only have `origin`.

**Fix for tooling**: `cascade-pull.sh --source temporal` should pre-flight check Forgejo connectivity and skip the forgejo remote if unreachable (with a warning), rather than blocking on every repo.

---

## Recommendations

### For Immediate Action (eastGate)

1. **Register flockGate SSH key on golgiBody Forgejo** — the pubkey is:
   ```
   ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMf+uvSv7msV8Jyo5PnLd6czPDuxiX6DjSMMHTe0ufC3 ecoPrimal@pm.me
   ```
   Via: `curl -X POST https://git.primals.eco/api/v1/user/keys -H "Authorization: token <TOKEN>" -d '{"title":"flockGate","key":"ssh-ed25519 AAAAC3..."}'`

2. **Add `[gates.flockGate]` to ecosystem_manifest.toml** — clone eastGate's repo list for now.

3. **Clean stale repos on flockGate** — `rm -rf songbird/ toadstool/` at workspace root.

### For cascade-pull.sh Hardening

| Issue | Fix | Priority |
|-------|-----|----------|
| HTTPS-only for GitHub | Add SSH URL generation for origin | P0 |
| No `--shallow` flag | Pass `--depth 1` when flag set | P1 |
| `primals/` pre-existence check | Create dirs when `--clone-missing` | P1 |
| Forgejo connectivity pre-flight | Test SSH before per-repo fetch | P2 |
| Unknown gate error message | Suggest closest match or fallback | P3 |

### For Handoff Template

Future gate bootstrap handoffs should include:
1. **Prerequisites checklist** (SSH key registered, Forgejo verified)
2. **Known-large repos** list (for shallow clone decision)
3. **Stale layout cleanup** commands
4. **Explicit fallback path** (not parenthetical)

---

## Current State

```
flockGate workspace: ~/Development/ecoPrimals/
├── .gate = "flockGate"
├── primals/    (14 repos, all shallow)
├── springs/    (8 repos, all shallow)
├── gardens/    (8 repos, all shallow)
├── infra/      (8 repos, wateringHole+plasmidBin+primalSpring full, rest shallow)
├── songbird/   ← STALE, should remove
└── toadstool/  ← STALE, should remove

Parity: 38/38 repos at PARITY with origin (GitHub)
Forgejo: NOT CONNECTED (key not registered)
sporePrint: builds, 144 pages, pseudoSpore gallery implemented
membrane binary: not yet built (requires full clone of cellMembrane — currently shallow)
```

---

---

## Post-Fix Validation (eastGate response actioned)

After eastGate pushed fixes for all 7 friction events:

| Step | Result |
|------|--------|
| `git pull origin main` on wateringHole | Fast-forward, 6 files changed, 340 insertions |
| `ssh -p 2222 git@git.primals.eco` | Authenticated as `golgiAdmin` with key `flockGate` |
| `--gate flockGate` in manifest | Works — 38 repos in profile |
| `--ensure-remotes` | 35 forgejo remotes added (3 already existed) |
| `--check --source temporal` | All 38 show PARITY with origin |

### Additional Bug Found: F8

**F8: f-string quoting in bash-embedded Python (cascade-pull.sh line 124)**

The "suggest closest gate" feature used `{", ".join(known)}` inside an f-string that's embedded in a bash `python3 -c "..."` double-quoted string. The `"` in `", "` terminates bash's outer string, causing a SyntaxError.

**Fix applied locally**: Extract join to a variable (`known_str = ', '.join(known)`) before the f-string.

**F9: Temporal summary count mismatch on shallow repos**

`cascade-pull.sh --check --source temporal` shows all 38 repos as PARITY in the matrix but reports "Parity: 0/38" (or 35/38) in the summary. Root cause: `temporal_check_repo` output contains extra newlines (from Forgejo fetch warnings on shallow repos), which breaks the `awk '{print $1}'` pattern matching in the summary loop.

---

## Glacial Shift Criterion #4 Evidence

This bootstrap validates WAN gate spinup:
- Remote node (different city, WAN-only) achieved full workspace parity
- `zola build` succeeds on flockGate (content pipeline over WAN)
- `cascade-pull.sh --check` temporal matrix shows all-parity from WAN
- Code changes (pseudoSpore gallery) developed entirely on WAN node

**Remaining for full criterion #4**: Songbird relay validation, cross-gate `capability.call` over WAN, temporal sync from Forgejo (requires unshallow).

---

## Current State (Post-Fix)

```
flockGate workspace: ~/Development/ecoPrimals/
├── .gate = "flockGate"
├── primals/    (14 repos, shallow, origin + forgejo remotes)
├── springs/    (8 repos, shallow, origin + forgejo remotes)
├── gardens/    (8 repos, shallow, origin + forgejo remotes)
└── infra/      (8 repos, mixed depth, origin + forgejo remotes)

Parity: 38/38 repos at PARITY with origin
Forgejo: CONNECTED (key ID 7, authenticated as golgiAdmin)
Remotes: origin (GitHub SSH) + forgejo (git.primals.eco:2222) on all 38
sporePrint: builds (144 pages), pseudoSpore gallery implemented
```

### Handoff to eastGate

Two script bugs to merge back (F8 + F9):
- F8: `scripts/cascade-pull.sh` line 124 — f-string quoting fix (applied locally)
- F9: temporal summary count — `awk` parsing broken by extra newlines from shallow fetch

---

## Round 2: Post-F8/F9-Fix Validation

**Date**: May 30, 2026 — 1:00 PM EDT

Pulled `b9fba17` (Fix F8/F9 from flockGate validation). F8/F9 confirmed fixed.

### What Worked (Round 2)

| Step | Result |
|------|--------|
| `git pull origin main` — F8/F9 fixes | Clean fast-forward |
| `--check --source temporal` | **38/38 PARITY** — summary count now matches matrix |
| `--source temporal` (sync) on dirty workspace | 38/38 synced, no errors |
| `--ensure-remotes` idempotency | "Added: 0, Already existed: 38" — correct |
| Forgejo bidirectional push (wateringHole, squirrel, hotSpring) | All "Everything up-to-date" — auth + push works |
| membrane binary build | `cargo build --release` in 14.5s, binary functional |
| `--ensure-remotes` on clean workspace | 38/38 forgejo remotes added, correct org routing |
| `--source temporal` with both remotes active | 38/38 parity, leader selection working |
| Reset test: songBird recovery via temporal | Re-cloned and synced successfully |

---

### F10: membrane binary in PATH short-circuits `--clone-missing` (Blocking)

**Symptom**: On a clean workspace with `membrane` installed at `/usr/local/bin/membrane`, running:
```
cascade-pull.sh --gate flockGate --clone-missing --shallow --source temporal
```
Reports `synced=1 failed=37` with all missing repos as "FAIL not cloned". No cloning occurs.

**Root cause**: `cascade-pull.sh` line 783-789:
```bash
if [[ "$SOURCE" == "temporal" ]]; then
    if [[ -n "$MEMBRANE_BIN" ]]; then
        echo "--- Temporal Sync (Rust membrane) ---"
        ECOPRIMALS_ROOT="$ECOPRIMALS_ROOT" "$MEMBRANE_BIN" temporal.sync "${REPOS[@]}" 2>&1
        exit 0   # ← exits before bash clone logic runs
    fi
```
When membrane binary is detected, the entire temporal path delegates to Rust and then `exit 0`. The `$CLONE_MISSING` flag and all bash clone logic below are never evaluated.

**Impact**: Cold-start on a gate that already has membrane installed is impossible via `--source temporal`. The only workaround is removing membrane from PATH.

**Fix recommendation**: Either:
1. Check `$CLONE_MISSING` before the membrane delegation and clone missing repos first via bash, OR
2. Pass `--clone-missing` to the membrane binary and teach it to clone, OR
3. Don't `exit 0` after membrane — fall through to bash clone logic for missing repos

---

### F11: Forgejo-first clone produces broken remote wiring (Blocking)

**Symptom**: After `--clone-missing --source temporal` (which uses `auto` source for clones → Forgejo first), repos have BOTH `github` and `forgejo` remotes pointing to the **same Forgejo URL**. No actual GitHub remote exists:
```
$ git -C primals/toadStool remote -v
forgejo  ssh://git@git.primals.eco:2222/ecoPrimals/toadStool.git (fetch)
forgejo  ssh://git@git.primals.eco:2222/ecoPrimals/toadStool.git (push)
github   ssh://git@git.primals.eco:2222/ecoPrimals/toadStool.git (fetch)
github   ssh://git@git.primals.eco:2222/ecoPrimals/toadStool.git (push)
```

**Root cause**: `clone_repo()` lines 304-307:
```bash
elif [[ "$clone_url" == *"git.primals.eco"* ]] && [[ -n "$github_url" ]]; then
    git -C "$local_path" remote add origin "$github_url" 2>/dev/null || true      # FAILS: origin already exists
    git -C "$local_path" remote rename origin github 2>/dev/null || true           # Renames Forgejo origin → "github"
    git -C "$local_path" remote rename forgejo origin 2>/dev/null || true          # FAILS: no "forgejo" remote
fi
```
After a Forgejo clone, `origin` = Forgejo URL. Step 1 tries to add `origin` (GitHub) but fails silently (exists). Step 2 renames the Forgejo-pointing `origin` to `github`. Step 3 tries to rename non-existent `forgejo` to `origin`, fails silently.

Result: `github` → Forgejo URL. Then `--ensure-remotes` adds `forgejo` → Forgejo URL. Both are duplicates.

**Impact**:
- `--source origin` recovery completely broken (no `origin` remote exists): 35/38 repos FAILED
- No GitHub fetch possible (github remote URL is actually Forgejo)
- Temporal sync still works because both remotes hit Forgejo (but this masks the bug)

**Fix recommendation**: Replace lines 304-307 with:
```bash
elif [[ "$clone_url" == *"git.primals.eco"* ]] && [[ -n "$github_url" ]]; then
    git -C "$local_path" remote rename origin forgejo 2>/dev/null || true
    git -C "$local_path" remote add origin "$github_url" 2>/dev/null || true
    git -C "$local_path" remote add github "$github_url" 2>/dev/null || true
fi
```
This correctly: (1) renames clone's origin (Forgejo) to `forgejo`, (2) creates `origin` → GitHub, (3) creates `github` → GitHub.

---

### F12: `auto` source prefers Forgejo for clones over WAN (Friction)

**Symptom**: During cold-start, `--clone-missing --source temporal` uses `auto` source for cloning. `auto` prefers Forgejo when `forgejo_repo` is set. For WAN gates, Forgejo clones can timeout (sourDough failed twice before succeeding manually from GitHub in <1s).

**Root cause**: `clone_url` with source `auto`:
```python
elif source == 'auto':
    if fr:
        print(f'{forgejo_ssh}/{fr}.git')  # Forgejo first — slow over WAN
```
Forgejo is a small VPS in nyc1. GitHub has CDN edge servers. For WAN clones, GitHub is always faster.

**Impact**: sourDough timed out twice. Had to manually clone from GitHub to unblock. The remaining 20 repos cloned from Forgejo in 237s total (would have been ~30s from GitHub).

**Fix recommendation**: For `--clone-missing`, `auto` should prefer GitHub (faster CDN) for the initial clone, then add Forgejo as a remote after. The temporal sync can use both remotes for ongoing operations.

---

## Validation Matrix (Round 2)

| Test | Path | Result | Issues |
|------|------|--------|--------|
| Dirty: `--check --source temporal` | Dirty workspace | 38/38 PARITY | None (F8/F9 fixed) |
| Dirty: `--source temporal` sync | Dirty workspace | 38/38 synced | None |
| Dirty: `--ensure-remotes` idempotency | Dirty workspace | 0 added, 38 existed | None |
| Forgejo push (3 repos, 3 orgs) | Dirty workspace | All succeed | None |
| membrane binary build | cellMembrane (full clone) | Success, 14.5s | None |
| Clean: cold-start with membrane in PATH | Fresh workspace | **BLOCKED** | F10 |
| Clean: cold-start without membrane | Fresh workspace | 38/38 (with manual fix for sourDough) | F11, F12 |
| Clean: `--ensure-remotes` | Fresh workspace | 38 added | F11 (wires github → Forgejo) |
| Clean: `--source temporal` both remotes | Fresh workspace | 38/38 parity | Works (masks F11) |
| Reset: delete songBird + `--clone-missing --source origin` | Fresh workspace | **35/38 FAILED** | F11 consequence |
| Reset: delete songBird + `--source temporal` | Fresh workspace | 38/38 recovered | Works (masks F11) |

---

## Current State (Round 2 — Clean Workspace)

```
flockGate workspace: ~/Development/ecoPrimals/
├── .gate = "flockGate"
├── primals/    (14 repos, all shallow)
├── springs/    (8 repos, all shallow)
├── gardens/    (8 repos, all shallow)
├── infra/      (8 repos, all shallow except wateringHole)
└── Dirty workspace preserved at: ~/Development/ecoPrimals.dirty-wave63/

Parity: 38/38 repos at PARITY
Forgejo: CONNECTED, push verified (3 repos, 3 orgs)
Remotes: github + forgejo on all 38 (BUT F11: github URL is wrong on Forgejo-cloned repos)
membrane: built and installed at /usr/local/bin/membrane
```

---

## Priority Fix Order for eastGate

| Priority | Event | Impact | Complexity |
|----------|-------|--------|------------|
| P0 | F11: remote wiring for Forgejo-first clones | Breaks `--source origin`, masks GitHub access | 3 lines |
| P0 | F10: membrane binary bypasses `--clone-missing` | Blocks cold-start when membrane installed | 5-10 lines |
| P1 | F12: `auto` clone source prefers Forgejo over WAN | Slow/timeout clones on WAN gates | 3 lines |

---

## Glacial Shift Criterion #4 Evidence (Updated)

This round validates:
- **Forgejo bidirectional sync from WAN** — push verified to 3 repos across 3 Forgejo orgs
- **membrane binary builds and runs on WAN node** — `membrane --help` functional
- **Temporal sync 38/38 from WAN** — both dirty and clean workspaces
- **Cold-start path validated** — works with workarounds (F10 membrane removed, F11/F12 temporal masks issue)

**Remaining for full criterion #4**: F10/F11 fixes for a fully unassisted cold-start.

---

## Round 3: Post-F10/F11/F12-Fix Validation

**Date**: May 30, 2026 — 3:46 PM EDT

Pulled `8018c9f` (Fix F10/F11/F12 from flockGate round 2). Full clean-room cold-start with membrane binary in PATH.

### Test Conditions

- Workspace **completely nuked** (`rm -rf Development/ecoPrimals`)
- `membrane` binary at `/usr/local/bin/membrane` (in PATH)
- Single-pass cold-start: `.gate` → clone wateringHole → `cascade-pull --clone-missing --shallow --source temporal`

### What Worked (Round 3)

| Step | Result |
|------|--------|
| Clone loop runs BEFORE membrane delegation | **F10 FIXED** — all 37 repos cloned in first pass |
| sourDough clone (previously timed out) | **F12 FIXED** — cloned in normal time (GitHub CDN first) |
| Remote wiring on all repos | **F11 FIXED** — `origin` → GitHub SSH, `forgejo` → Forgejo SSH |
| Membrane temporal sync after clone | 36/38 OK parity, 2 flagged DIVERGE for human review |
| `--check --source temporal` | 36 PARITY, 2 DIVERGE (correctly flagged) |
| Total cold-start time | ~523s (37 shallow clones + temporal sync) |

### Genuine Divergence (Not Script Bugs)

Two repos have legitimate Forgejo/GitHub divergence — Forgejo mirrors are stale:

| Repo | Forgejo vs Origin | Notes |
|------|-------------------|-------|
| gardens/lithoSpore | forgejo(+1,-65) | Forgejo has 1 extra commit, missing 65 from GitHub |
| infra/sporePrint | forgejo(+1,-264) | Forgejo has 1 extra commit, missing 264 from GitHub |

These need Forgejo mirror resync on eastGate — not a cascade-pull issue.

### F13: `--check --source origin` reports false DRIFT (Display Bug)

**Symptom**: `--check --source origin` reports `Drifted: 3` (sourDough, lithoSpore, sporePrint), but all 3 have `HEAD == origin/main` (verified via `git rev-parse`).

**Root cause (sourDough)**: Shallow clone can't compute `git rev-list --count`. Script falls back to `behind=?,ahead=?` and flags as DRIFT even though commits match.

**Root cause (lithoSpore, sporePrint)**: Script reports Forgejo-vs-origin divergence instead of local-vs-origin. Since local HEAD = origin/main, local is at parity with origin — but the cross-remote divergence contaminates the report.

**Impact**: Low — false positives in `--check --source origin`. Functional parity is correct.

**Fix recommendation**:
1. Fast-path: if `HEAD == origin/main`, report `✓` regardless of rev-list results
2. Don't include cross-remote divergence in `--source origin` mode (that's temporal's job)

### Minor: Membrane temporal check has no summary line

The membrane binary's temporal check outputs per-repo status but no "Parity: X / 38" summary. The bash path (without membrane) does output this. Low priority cosmetic issue.

---

## Validation Matrix (Round 3)

| Test | Result | Issues |
|------|--------|--------|
| Cold-start with membrane in PATH | **PASS** — 37 cloned, 36 synced | F10 fixed |
| Remote wiring (toadStool, nestGate, cellMembrane) | **PASS** — origin→GitHub, forgejo→Forgejo | F11 fixed |
| Clone speed (sourDough, all repos) | **PASS** — no timeouts | F12 fixed |
| `--check --source origin` | **35/38** (3 false positives) | F13 (display bug) |
| `--check --source temporal` | **36/38 PARITY**, 2 genuine DIVERGE | Correct behavior |
| Membrane temporal sync | 36 synced, 2 flagged for review | Correct behavior |

---

## Current State (Round 3 — Clean Cold-Start Workspace)

```
flockGate workspace: ~/Development/ecoPrimals/
├── .gate = "flockGate"
├── primals/    (14 repos, all shallow, origin+forgejo wired correctly)
├── springs/    (8 repos, all shallow, origin+forgejo wired correctly)
├── gardens/    (8 repos, all shallow, origin+forgejo wired correctly)
└── infra/      (8 repos, all shallow, origin+forgejo wired correctly)

Parity: 36/38 origin-aligned, 2 genuine diverge (lithoSpore, sporePrint)
Remotes: origin (GitHub SSH) + forgejo (Forgejo SSH) on all 38
membrane: /usr/local/bin/membrane (in PATH, does not block cold-start)
```

---

## Priority Fix Order for eastGate (Round 3)

| Priority | Event | Impact | Complexity |
|----------|-------|--------|------------|
| P2 | F13: false DRIFT in `--check --source origin` | Display-only, no functional impact | ~5 lines |
| P1 | Forgejo mirror resync (lithoSpore, sporePrint) | 2 repos stale on Forgejo | Admin task |
| P3 | Membrane temporal check: add summary line | Cosmetic | 1 line |

---

## Glacial Shift Criterion #4 Evidence (Final)

This round validates the **complete unassisted cold-start path**:
- Brand new gate with only `.gate` file → full 38-repo workspace in single `cascade-pull` invocation
- membrane binary in PATH does NOT block the flow (F10 fixed)
- Remote wiring correct on first try (F11 fixed)
- WAN-safe clone order: GitHub CDN first (F12 fixed)
- Forgejo bidirectional push verified (round 2, still valid)
- Temporal sync identifies genuine divergence and flags for review

**Criterion #4 status**: SATISFIED — WAN gate cold-start is fully automated and functional.

**Only remaining**: Resolve stale Forgejo mirrors (lithoSpore, sporePrint) and fix F13 display bug (low priority).
