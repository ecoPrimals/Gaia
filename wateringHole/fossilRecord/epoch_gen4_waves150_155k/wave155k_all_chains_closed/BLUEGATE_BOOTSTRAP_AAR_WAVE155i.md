# blueGate Bootstrap AAR — Wave 155i

**Date**: Jul 29, 2026 12:24 EDT | **Wave**: 155i | **From**: blueGate
**Gate**: blueGate | **OS**: Windows 10.0.26200 | **Blurb version**: Wave 155i team startup blurb

---

## WHAT WORKED

1. **HTTPS zero-config clone** — Exactly as blurb promised. All 40 repos cloned
   from `https://git.primals.eco/` with zero auth, zero config. This is the
   smoothest onramp. Fresh gate → full workspace in one pass.

2. **Forgejo org mapping** — The three-org mapping (ecoPrimals → primals/,
   sporeGarden → gardens/, syntheticChemistry → springs/) worked perfectly.
   Infra mixed-org mapping also correct.

3. **Depot Windows genomeBins** — All 14 primal `.exe` binaries available at
   `https://depot.primals.eco/primals/x86_64-pc-windows-gnu/`. Tower Atomic
   trio downloaded and verified in seconds:
   - `beardog.exe` 0.9.0 (10 MB)
   - `songbird.exe` 0.2.1 (23 MB)
   - `skunkbat.exe` 0.2.18 (2.5 MB)

4. **Workspace structure** — Canonical layout is clean and well-documented.
   No ambiguity about where anything goes.

5. **Blurb phasing** — The four-phase flow (connectivity → sync → enrollment →
   code team) is well-sequenced. Phase 0+1 are fully automatable. Phase 2
   correctly identifies what needs human action.

6. **winget toolchain install** — Git 2.55.0.3, Rust 1.97.1 (stable),
   WireGuard 1.1 all installed cleanly via winget on Windows.

---

## WHAT DIDN'T WORK (Windows-specific)

### 1. primalSpring colon-in-filename (BLOCKER on Windows)

6 files in `benchScale/tower_shadow/` have IP:port colons in filenames:
```
tower-atomic_10_13_37_2:7700_20260723T204413.json
tower-atomic_10_13_37_5:7700_20260723T154353.json
tower-atomic_192_168_4_244:7700_20260723T203912.json
wireguard_10_13_37_2:7700_20260723T204413.json
wireguard_10_13_37_5:7700_20260723T154353.json
wireguard_192_168_4_244:7700_20260723T203912.json
```

Windows NTFS prohibits `:` in filenames. Git creates truncated versions (cut
at colon), leaving 6 deleted tracked files + 6 untracked fragments. Results
in 12 permanent dirty entries in `git status`.

**Fix**: Rename upstream — replace `:` with `_` in these 6 filenames.
Benchmark data only, no code impact.

### 2. fossilRecord deep archive paths (resolved)

Initial checkout failed — paths under `misc/archive-pre-2026/` exceed Windows
260-char MAX_PATH. Resolved by setting `git config --global core.longpaths true`
and force checkout. All 10,905 files checked out successfully.

**Blurb gap**: The blurb doesn't mention `core.longpaths` for Windows gates.
Should be added to Phase 1 Windows instructions.

### 3. Git not pre-installed

The blurb assumes `git` is available. Fresh Windows machines don't have it.
The blurb's bash scripts also assume a Unix shell. Windows gates need
PowerShell equivalents or explicit "install Git first" step.

### 4. git-credential-manager blocking

On initial clone attempts, Git for Windows' built-in credential manager
tried to pop an interactive auth dialog, which hangs in non-interactive
terminals (agent sessions, CI). Fixed by setting:
```
GIT_TERMINAL_PROMPT=0
GCM_INTERACTIVE=never
```
Not needed for public HTTPS repos, but the credential manager doesn't
know that until it tries.

### 5. Windows LongPathsEnabled registry (requires admin)

OS-level `LongPathsEnabled` is 0 by default. Git's `core.longpaths` helps
but some tools may still hit 260-char limits. Requires admin to fix:
```powershell
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1
```

---

## WHAT NEEDS TO EVOLVE IN THE BLURB

### A. Windows-specific Phase 0+1 section

The blurb's Phase 1 scripts are bash. Windows gates need:
- Explicit "install Git" step (winget or manual)
- PowerShell equivalents for clone/sync loops
- `core.longpaths true` as a required git config step
- Note about credential manager blocking in non-interactive sessions

### B. primalSpring filename fix

The 6 colon-in-filename benchmark files should be renamed upstream to use
underscores. This affects any Windows gate (blueGate, swiftGate, northGate).

### C. sporePrint status

`infra/sporePrint` is an empty repo on Forgejo (no commits). The blurb lists
it in the canonical layout but doesn't note it's a placeholder. Minor — just
a documentation note.

### D. springs/helixVision discrepancy

The blurb workspace layout lists `springs/helixVision` but no such repo
exists under `syntheticChemistry/` on Forgejo. `gardens/helixVision` exists
under `sporeGarden/` and cloned fine. Likely a layout doc error — helixVision
appears in both gardens and springs sections.

### E. Blurb could include Windows genomeBin verification

The depot has all 14 Windows `.exe` builds but the blurb only mentions
"build from source if depot lacks Windows bins." Worth noting they're
available — saves 30+ min of compilation.

---

## REGISTRATION NEEDED — KEYS FOR EASTGATE OVERWATCH

### WireGuard public key (for golgiBody peer registration)

```
sJKbtjyHFXFPnHnzePuK9jX/6QBHyWKC2KimRJb6RlE=
```

**Requested peer config on golgiBody:**
```ini
[Peer]
# blueGate
PublicKey = sJKbtjyHFXFPnHnzePuK9jX/6QBHyWKC2KimRJb6RlE=
AllowedIPs = 10.13.37.12/32
PersistentKeepalive = 25
```

### SSH public key (for Forgejo push access — wateringHole handoffs)

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINlBX3vvJWHySRLf6d901D4UGw7PRmLMcUb3xJJmnybd blueGate@primals.eco
```

Register as deploy key on `ecoPrimals/wateringHole` (write access) or as
a user key if blueGate gets a Forgejo account.

---

## BLUEEGATE STATUS AFTER BOOTSTRAP

| Item | Status |
|------|--------|
| Repos cloned | **40/40** from Forgejo HTTPS |
| Repos clean | **38/40** (primalSpring: Windows filename, sporePrint: empty) |
| All on `main` | Yes |
| All remotes Forgejo | Yes (HTTPS) |
| Tower Atomic binaries | **Downloaded + verified** (beardog 0.9.0, songbird 0.2.1, skunkbat 0.2.18) |
| WireGuard | **Installed, keys generated, config written** — awaiting peer registration |
| SSH key | **Generated** — awaiting Forgejo registration |
| Rust toolchain | **1.97.1 stable** (for source builds) |
| Git | **2.55.0.3** with `core.longpaths=true` |
| Windows LongPathsEnabled | 0 (needs admin fix) |

### Once eastGate registers both keys:

1. Activate WireGuard tunnel in GUI → `ping 10.13.37.1`
2. Verify SSH: `ssh -T git@git.primals.eco`
3. Repoint remotes to SSH: `git remote set-url origin ssh://git@git.primals.eco:2222/ecoPrimals/<repo>.git`
4. Start Tower Atomic primals
5. Ready for Phase 3 code team work

---

*blueGate — Wave 155i bootstrap AAR. 40/40 repos synced. Tower Atomic
genomeBins verified. WireGuard + SSH keys generated. Awaiting eastGate
peer + key registration to go live.*
