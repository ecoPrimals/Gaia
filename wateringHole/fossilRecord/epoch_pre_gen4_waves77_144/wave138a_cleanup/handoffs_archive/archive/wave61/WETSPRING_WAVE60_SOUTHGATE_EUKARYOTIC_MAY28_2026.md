# wetSpring — Wave 60 southGate Eukaryotic Onboarding

**Date**: 2026-05-28
**From**: wetSpring (southGate)
**To**: primalSpring coordination
**Version**: V189

---

## Status

southGate NUCLEUS: **13/13 processes running**, 11/13 health-responding.
biomeOS auto-discovers 1725 capabilities from 21 primal surfaces.
wetSpring is P1 pattern node — eukaryotic pattern proven internally.

## Blocker: Forgejo SSH Key Registration

southGate cannot push to Forgejo. SSH key not registered.

**Key to register:**
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIHrLVoaIaDaUZVae2UCNhmA8YZ3dVo/FuMOdep+0ZnMV ecoPrimal@github
```

**Title:** `southGate`

We don't have root SSH to VPS ([RELAY_PUBLIC]) or a Forgejo API token.
eastGate operator needs to run:
```bash
FORGEJO_TOKEN=$(ssh root@[RELAY_PUBLIC] 'cat /opt/forgejo/.api_token')
curl -sf -X POST "https://git.primals.eco/api/v1/user/keys" \
  -H "Authorization: token $FORGEJO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"southGate","key":"ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIHrLVoaIaDaUZVae2UCNhmA8YZ3dVo/FuMOdep+0ZnMV ecoPrimal@github"}'
```

## Manifest Issues (ecosystem_manifest.toml)

1. `songbird` repo key → local directory is `primals/songBird/` (capital B).
   Script resolves to `primals/songbird/` which doesn't exist.
2. `nestGate` local_path resolves to workspace root (`.`) instead of
   `primals/nestGate`. Likely missing or wrong `local_path` field.
3. `cellMembrane` — inner-only repo not cloned on southGate.
   Chicken-and-egg: needs Forgejo access to clone, needs to be cloned for
   cascade-pull to include it.

## Launcher Issues (plasmidBin/nucleus_launcher.sh)

- Passes `--socket` to sweetGrass, rhizoCrypt, skunkBat — these binaries
  only accept `--port` (and `--unix` for rhizoCrypt). Requires manual start.
- `fetch.sh` line 350: `local` used outside function body → syntax error
  when fallback path triggers.

## What's Working

- 13/13 NUCLEUS processes with UDS sockets
- biomeOS Neural API: 1725 capabilities / 21 surfaces
- Forgejo remotes configured on 29 repos
- WaterFall 20-repo southGate profile validated (dry-run)
- `GATE_NAME=southGate` in environment (hostname `pop-os` doesn't auto-detect)

```
wetSpring Wave 60: NUCLEUS 13/13 on southGate, eukaryotic pattern proven, Forgejo SSH blocked
```
