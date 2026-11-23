# cellMembrane — Pipeline Evolution: Runner Redundancy, Forgejo Actions, Build Inversion

**From**: primalSpring (upstream)
**To**: cellMembrane team (ironGate)
**Date**: May 26, 2026
**Wave**: 52
**Priority**: High — single-runner SPOF, sovereignty evolution
**Status**: Wave 52a shipped by primalSpring; cellMembrane owns 52b/53/54

---

## Context

primalSpring has shipped Wave 52a pipeline correctness improvements to `plasmidBin`:

- `plasmidbin build --commit <SHA>` — reproducible builds pinned to dispatch SHA
- `plasmidbin harvest --version-tag <tag>` — auto-updates `manifest.toml` latest field after harvest, closing the stale re-dispatch loop
- `auto-harvest.yml` wires dispatch SHA through to `--commit` and resolves upstream version tags for manifest updates
- biomeOS asset naming mismatch resolved (id-based fallback in `fetch.rs`)

These changes land on `main` at `d41913b` and are live for all future harvest runs.

## What cellMembrane Owns Next

### Wave 52b: Runner Redundancy (immediate)

| Item | Detail |
|------|--------|
| **2nd self-hosted runner** | Deploy on eastGate (or southGate) labeled `self-hosted, linux, x86_64, eastgate` |
| **Toolchain** | Rust stable + `x86_64-unknown-linux-musl` target (mirrors ironGate) |
| **Lockout prevention** | If ironGate goes down, eastGate picks up — eliminates single-runner SPOF |
| **Tracking** | Already in `GLACIAL_SHIFT_TRACKER.md` |

This is the most urgent item. The current ironGate runner is a SPOF for all harvest builds.

### Wave 53: Forgejo Actions — Shadow CI (cellMembrane + primalSpring)

| Item | Detail |
|------|--------|
| **Deploy Forgejo Actions runner** | Co-located on ironGate with Forgejo instance |
| **Port `validate.yml`** | Already marketplace-free, straightforward Forgejo Actions port |
| **Shadow mode** | Run both GitHub Actions + Forgejo Actions `plasmidbin validate` and compare results |
| **`sources.toml` `forge` field** | Add Forgejo clone URL per primal as fallback source |
| **`plasmidbin build --forge-url`** | Try Forgejo clone first, GitHub fallback |

### Wave 54: Build Inversion — Inner Membrane Primary (horizon)

| Item | Detail |
|------|--------|
| **Forgejo becomes CI dispatch plane** | `notify-plasmidbin.yml` equivalent fires on Forgejo push hooks |
| **Build on LAN, push UP** | After build + harvest: `git push forgejo`, `git push github`, `gh release upload` |
| **Private repos** | No PAT needed — bearDog + skunkBat already timer-synced to Forgejo |
| **`deploy_membrane.sh`** | Fetch switches to Forgejo releases (or NestGate) with GitHub Releases fallback |

This is the "push UP to GitHub" inversion: builds happen on inner membrane, results push outward.

## Key Facts for cellMembrane

- **25 repos** already timer-synced from GitHub to Forgejo on ironGate (6 via timer)
- **bearDog + skunkBat** are private repos, already synced — inner membrane builds eliminate PAT dependency
- **`manifest.toml` `mirror_url`** field is already reserved for NestGate depot (Wave 55+)
- **Node.js 20 deprecation** warning active on GitHub Actions — migrate to v5 action versions or set `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24` before June 2

## Requested Actions

- [ ] Provision 2nd self-hosted runner on eastGate with `self-hosted, linux, x86_64, eastgate` labels
- [ ] Evaluate Forgejo Actions runner deployment on ironGate
- [ ] Port `validate.yml` to Forgejo Actions as shadow CI proof-of-concept
- [ ] Add `deploy_membrane.sh` Forgejo/NestGate fallback fetch path
- [ ] Update `GLACIAL_SHIFT_TRACKER.md` with Wave 52b/53 progress
