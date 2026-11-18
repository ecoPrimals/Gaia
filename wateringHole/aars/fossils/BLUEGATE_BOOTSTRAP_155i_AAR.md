# blueGate Bootstrap AAR — Wave 155i

**Date**: Jul 29, 2026 12:24 EDT | **Wave**: 155i | **From**: blueGate
**Gate**: blueGate | **OS**: Windows 10.0.26200 | **Blurb version**: Wave 155i team startup blurb

---

## WHAT WORKED

1. **HTTPS zero-config clone** — All 40 repos cloned from `https://git.primals.eco/` with zero auth, zero config.
2. **Forgejo org mapping** — Three-org mapping (ecoPrimals/sporeGarden/syntheticChemistry) worked perfectly.
3. **Depot Windows genomeBins** — All 14 primal `.exe` binaries at `https://depot.primals.eco/primals/x86_64-pc-windows-gnu/`. Tower Atomic trio: beardog.exe 10MB, songbird.exe 23MB, skunkbat.exe 2.5MB.
4. **Workspace structure** — Canonical layout clean and unambiguous.
5. **Blurb phasing** — Four-phase flow well-sequenced. Phase 0+1 fully automatable.
6. **winget toolchain** — Git 2.55.0.3, Rust 1.97.1, WireGuard 1.1 all clean via winget.

## WHAT DIDN'T WORK (Windows-specific)

1. **benchScale colon-in-filename (BLOCKER)** — 6 files in `benchScale/tower_shadow/` have IP:port colons (`10_13_37_2:7700`). NTFS prohibits `:`. Creates 12 permanent dirty entries. **Fix**: rename upstream (`:` → `_`).
2. **fossilRecord deep archive paths** — Exceeded 260-char MAX_PATH. Resolved with `git config --global core.longpaths true`. **Blurb gap**: should mention this for Windows.
3. **Git not pre-installed** — Blurb assumes git available. Windows needs explicit install step.
4. **git-credential-manager blocking** — Hangs in non-interactive sessions. Fixed with `GIT_TERMINAL_PROMPT=0` + `GCM_INTERACTIVE=never`.
5. **LongPathsEnabled registry** — OS-level default is 0. Needs admin: `Set-ItemProperty -Path "HKLM:\...\FileSystem" -Name "LongPathsEnabled" -Value 1`.

## BLURB EVOLUTION NEEDED

- A: Windows Phase 0+1 section (PowerShell, git install, longpaths, GCM)
- B: benchScale filename fix (upstream rename)
- C: sporePrint is empty repo — note in blurb
- D: springs/helixVision layout error — it's gardens/helixVision
- E: Windows genomeBins ARE available — update blurb note

## REGISTRATION NEEDED

WireGuard: `sJKbtjyHFXFPnHnzePuK9jX/6QBHyWKC2KimRJb6RlE=` → golgiBody peer (10.13.37.12/32)
SSH: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINlBX3vvJWHySRLf6d901D4UGw7PRmLMcUb3xJJmnybd blueGate@primals.eco` → Forgejo wateringHole write

## STATUS

| Item | Status |
|------|--------|
| Repos | **40/40** cloned, **38/40** clean |
| Tower binaries | **Downloaded + verified** |
| WireGuard | Installed, keys generated — **awaiting peer registration** |
| SSH | Key generated — **awaiting Forgejo registration** |
| Rust | 1.97.1 stable |
| Git | 2.55.0.3, core.longpaths=true |

---

*blueGate — Wave 155i. 40/40 repos synced. Tower Atomic genomeBins verified.
WireGuard + SSH keys generated. Awaiting eastGate peer + key registration.*
