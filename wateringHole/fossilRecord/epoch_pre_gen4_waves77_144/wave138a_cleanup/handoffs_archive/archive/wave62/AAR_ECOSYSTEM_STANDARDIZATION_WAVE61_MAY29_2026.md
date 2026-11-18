# AAR: Ecosystem Standardization Sprint — Wave 61

**Date**: May 29, 2026
**From**: primalSpring coordination
**To**: all teams, cellMembrane, waterFall
**Wave**: 61 (Temporal Sync → Standardization)

---

## Summary

An ecosystem-wide audit of all 39 repositories revealed systemic standardization debt: duplicate directories, stale branches, inconsistent naming, missing remotes, protocol mismatches, and — most critically — significant friction in the Forgejo membrane for basic operations like creating a new repository. This AAR documents what was found, what was fixed, and what the findings mean for golgiBody and cellMembrane operations going forward.

---

## Trigger

Routine post-evolution sync check revealed toadStool had a stale `mirror` remote pointing to `/tmp/toadstool-mirror.git`. Investigation showed this was not an isolated incident but a pattern of accumulated workspace debris across the ecosystem.

---

## Findings (16 issues across 39 repos)

### Critical: Forgejo Repo Creation Friction

Creating `fossilRecord` on Forgejo exposed a multi-layer access problem:

1. **No local API token** — no `FORGEJO_TOKEN` in env, no `~/.config/forgejo/`, no `tea` CLI
2. **Push-to-create disabled** — `git push forgejo main` returns "Push to create is not enabled for organizations"
3. **No SSH host alias** — `~/.ssh/config` has no entry for the VPS; required `root@git.primals.eco`
4. **Token generation requires VPS shell access** — had to SSH to VPS, `sudo -u git` with full `FORGEJO_WORK_DIR`/`HOME`/`--config` flags to run `forgejo admin user generate-access-token`
5. **Token cleanup impossible via CLI** — the installed Forgejo version has no `delete-access-token` subcommand; must use web UI

**Impact**: Creating a single empty repository required 7 shell commands across 2 machines, knowledge of the Forgejo user (`git`, not `forgejo`), knowledge of the config path (`/opt/forgejo/custom/conf/app.ini`), and knowledge of the work directory (`/opt/forgejo`). This is not sustainable for gen5 collaborator onboarding where we may need to create repos per-collaborator.

### Critical: Root Workspace Remote Misconfiguration

The root ecoPrimals workspace `.git` has remotes pointing to `ecoPrimals/nestGate`. The workspace predates the org structure — it started as a nestGate clone that everything else grew inside of. The root IS nestGate code (Cargo.toml, src/, etc.) with `primals/`, `springs/`, `gardens/`, `infra/` as nested independent repos.

**Resolved**: Root synced to match canonical nestGate (Session 79 → Session 81, fast-forward).

### Duplicate Directories (naming drift)

| Stale | Canonical | Root Cause |
|-------|-----------|-----------|
| `primals/songbird` (lowercase) | `primals/songBird` (camelCase) | phase1 migration used lowercase; canonical evolved to firstLast |
| `gardens/foundation` (lowercase) | `gardens/projectFOUNDATION` | Repo renamed on GitHub/Forgejo; local clone not updated |

**Both had identical commit histories** but pointed to different remote repos. The lowercase copies were older (26-30h behind) and carried 5+ stale branches.

### Stale Branches (archaeological debris)

| Repo | Branches | Age |
|------|----------|-----|
| songbird (lowercase) | 5 branches: `cleanup/*`, `consolidation/*`, `type-unification-*`, `unification/*` | Nov 2025 |
| toadStool | 4 branches: `backup-before-production-*`, `feature/*`, `master-stale-backup`, `parse-error-*` | Aug 2025 |
| root repo | `primalspring-standalone` | unknown |

### master Branch Persistence

| Repo | Location | Status |
|------|----------|--------|
| toadStool | Forgejo `refs/heads/master` | Deleted |
| toadStool | GitHub `origin/HEAD → origin/master` | Fixed (HEAD → main, master already gone) |
| biomeOS | GitHub `refs/heads/master` | Deleted (contained 1 superseded scaffold commit) |

### Remote/Protocol Inconsistencies

| Repo | Issue | Fix |
|------|-------|-----|
| toadStool | `mirror` remote → `/tmp/toadstool-mirror.git` | Removed |
| esotericWebb | origin uses HTTPS not SSH | Switched to `git@github.com:sporeGarden/esotericWebb.git` |
| nestGate | `main` tracks `forgejo/main` not `origin/main` | Fixed |
| songBird | `main` tracks `forgejo/main` not `origin/main` | Fixed |
| 26 repos | `origin/HEAD` not set | Set to `origin/main` |

### Misplaced Repos

| Repo | Was | Now | Reason |
|------|-----|-----|--------|
| bingoCube | `primals/` | `infra/` | Validation tool, not a deployed primal |
| fossilRecord | top-level (no infra/) | `infra/fossilRecord` | Archive repo belongs with infrastructure |

### Missing from Manifest/Infrastructure

| Item | Issue | Fix |
|------|-------|-----|
| fossilRecord | Not in `ecosystem_manifest.toml` | Added as `outer-only` infra |
| fossilRecord | No Forgejo remote | Created repo, pushed |
| songbird key | manifest key was lowercase `[repos.songbird]` | Renamed to `[repos.songBird]` |
| 6 gate profiles | Referenced `"songbird"` | Updated to `"songBird"` |

### Stale Directories (non-repo debris)

| Path | Contents | Action |
|------|----------|--------|
| `springs/primalTools` | Empty (bingoCube had been moved) | Removed |
| `wetSpring/` (top-level) | Root-owned Galaxy container dirs | Removed (`pkexec`) |
| `sporeprint/` (root-level) | Part of nestGate working tree | Left (tracked by root repo) |

---

## Files Modified

- `infra/wateringHole/ecosystem_manifest.toml` — bingoCube reclassified, songBird key fixed, fossilRecord added, gate profiles updated, total_repos 38→39
- `infra/wateringHole/bootstrap.sh` — bingoCube clones to `infra/`, fossilRecord added to clone list

---

## Recommendations

### R1: Forgejo Token Management Standard

The ecosystem needs a documented, repeatable process for Forgejo API operations from gate workstations. Options:

1. **Persistent scoped token** stored in `~/.config/forgejo/token` on eastGate, with read-only + repo-create scope. cellMembrane documents the generation and rotation process.
2. **SSH config entry** for VPS admin access (`Host golgiBody` in `~/.ssh/config`).
3. **Enable push-to-create for ecoPrimals org** on Forgejo, eliminating the API requirement for repo creation entirely.

### R2: Workspace Bootstrap Evolution

`bootstrap.sh` handles phase1/phase2/ecoSprings migration but does not:
- Set `origin/HEAD` after clone
- Verify branch naming (main vs master)
- Add forgejo remote after GitHub clone
- Validate remote protocol (SSH vs HTTPS)

The bootstrap should evolve to run a post-clone standardization pass. Alternatively, waterFall temporal sync (when implemented) should include a lint pass that catches these issues.

### R3: New Repo Onboarding Runbook

Creating a new ecosystem repo currently requires:
1. Create on GitHub (`gh repo create`)
2. SSH to VPS, generate temp token, create on Forgejo via API, revoke token
3. Clone locally, add both remotes, set tracking, set origin/HEAD
4. Add to `ecosystem_manifest.toml`
5. Add to relevant gate profiles
6. Add to `bootstrap.sh` clone list

This should be a single script: `onboard-repo.sh <org> <name> <category>`. plasmidBin already has `onboard-gate-relay.sh` for gate onboarding; this is the repo-level equivalent.

### R4: golgiBody as NUCLEUS — Agentic Control Through Primals

The VPS (golgiBody) is currently a collection of manually configured services — Forgejo, mitoBeacon, DNS, systemd units — accessed through raw SSH and direct database manipulation. This session demonstrated the cost: revoking a single API token required installing sqlite3 on the VPS and querying the database by hand.

golgiBody needs to be a NUCLEUS. Every VPS operation — repo creation, token management, service restarts, DNS updates, certificate rotation, user management — should be:

1. **Agentic** — executable from a gate workstation through capability calls, not SSH sessions. An agent on eastGate should be able to call `capability.call("gate", "repo.create", {org: "ecoPrimals", name: "fossilRecord"})` and have the full pipeline execute: Forgejo API, remote add, initial push, manifest update.

2. **Shadowed through primals** — every VPS operation maps to a primal capability. Forgejo repo management → nestGate `content.*` methods. Token lifecycle → bearDog `auth.token.*` methods. DNS management → songbird `discovery.*` methods. Service health → biomeOS `gate.health.*` methods. The primals become the interface; the VPS services become the implementation.

3. **Recorded in provenance** — every agentic VPS operation produces a rhizoCrypt DAG event and sweetGrass attribution. Who created the repo, when, why, authorized by which token. The same provenance trio that tracks science tracks infrastructure.

This is the cellMembrane's evolution path: from a manually configured VPS to a NUCLEUS gate where the periplasmic surface (Forgejo, DNS, TURN) is controlled through the same capability routing that controls primals on eastGate. The Forgejo API token friction disappears because the agent never touches the API directly — it calls a primal method, and the primal handles the Forgejo interaction through its own authenticated channel.

**Concrete next steps**:
- nestGate `content.repo.create` / `content.repo.list` methods that proxy to the Forgejo API
- bearDog `auth.token.create` / `auth.token.revoke` methods that manage Forgejo tokens through the admin CLI or API
- biomeOS `gate.service.status` / `gate.service.restart` methods that manage systemd units on golgiBody
- cellMembrane evolves from a deploy-script collection to a gate profile with a NUCLEUS manifest

### R5: Periodic Ecosystem Lint

The standardization issues accumulated over months because there was no automated check. A periodic lint (run during cascade-pull or as a Wave checkpoint) should verify:
- All repos have origin + forgejo remotes
- All repos on `main` branch tracking `origin/main`
- No `master` branches on any remote
- `origin/HEAD` set to `origin/main`
- Remote URLs use SSH not HTTPS
- Manifest `local_path` matches actual disk layout
- No duplicate directories (case-insensitive check)
- No stale local branches older than N days

---

## Artifacts

- 16 cleanup actions executed across 39 repos
- `ecosystem_manifest.toml` v2.0.0 updated
- `bootstrap.sh` updated
- fossilRecord created on Forgejo and pushed
- biomeOS `master` branch deleted from GitHub
- toadStool `master` branch deleted from Forgejo
- Temp Forgejo API token `tmp-fossil-create` **pending revocation** at `https://git.primals.eco/-/user/settings/applications`

---

*This AAR feeds directly into two evolution paths. First, the waterFall temporal sync specification (WATERFALL_TEMPORAL_SYNC.md) — the standardization drift documented here is exactly the class of entropy that temporal sync is designed to prevent. Second, the golgiBody-as-NUCLEUS evolution — the Forgejo friction, the SSH-and-sqlite token revocation, the manual service management are all symptoms of the VPS existing outside the primal capability model. When golgiBody is a NUCLEUS, these operations become capability calls. When they are capability calls, they are agentic. When they are agentic, they are recorded in provenance. The membrane becomes sovereign infrastructure, not a box you SSH into.*
