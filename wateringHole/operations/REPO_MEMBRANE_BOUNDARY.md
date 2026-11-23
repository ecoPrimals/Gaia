<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Repo Membrane Boundary — Git Host Classification

**Date**: May 17, 2026
**Status**: Active
**Authority**: WateringHole Consensus
**Related**: `SOVEREIGNTY_STANDARDS.md`, `MEMBRANE_CHANNEL_ARCHITECTURE.md`

---

## Purpose

This document classifies every ecoPrimals repository by its membrane
boundary — where it should live (inner membrane only, dual-push, or
outer membrane only) and why. The classification drives push policy,
CI strategy, and contamination prevention.

---

## Membrane Model

| Layer | Git Host | Trust | Sync Direction |
|-------|----------|-------|----------------|
| **Inner membrane** | Forgejo (`git.primals.eco:3000`) | Covalent — full trust, private by default | Direct push to Forgejo only |
| **Trailing mirror** | GitHub primary → Forgejo pulls | Observed primary — Forgejo trails GitHub server-side | GitHub authoritative, Forgejo auto-syncs (8h) |
| **Outer membrane** | GitHub only | Observed — public archive, CDN, Pages | `git push origin` only |

**Note**: The "Dual-push" model was retired May 23, 2026. Dev happens across
multiple gates — per-machine push hooks don't scale. Forgejo now pulls
from GitHub server-side. When covalent gates host Forgejo, we invert.

---

## Repository Classification

### Inner Membrane Only (Forgejo-only)

These repos contain operational data, credentials, or sensitive
infrastructure details that must not exist on external substrate.

| Repo | Org | Content | Rationale |
|------|-----|---------|-----------|
| `cellMembrane` | sporeGarden | VPS deployment, SSH key mgmt, TURN credentials, RustDesk keys | Operational secrets — inner membrane only |
| *(future)* | — | Any new credential/secret/operational repos | Default to inner-only for ops repos |

**Current gap**: `cellMembrane` is currently private on GitHub. It
should be moved to Forgejo-only once Forgejo is operationally primary.
See "Decision: cellMembrane" below.

### Trailing Mirror (GitHub Primary → Forgejo Pulls)

Public code repos where GitHub is operationally primary and Forgejo
trails as an inner membrane mirror (auto-synced every 8h server-side).

**Gardens (sporeGarden org):**

| Repo | GitHub Visibility | Content |
|------|-------------------|---------|
| `projectNUCLEUS` | Public | Sovereignty layer, deployment infrastructure |
| `projectFOUNDATION` | Public | Knowledge layer, thread lineage, validation evidence |
| `lithoSpore` | Public | Verification chassis, USB-deployable validation |
| `esotericWebb` | Public | UI/agentic interaction layer |

**Springs (syntheticChemistry org):**

| Repo | GitHub Visibility | Content |
|------|-------------------|---------|
| `primalSpring` | Public | Coordination spring, composition validation |
| `wetSpring` | Public | Breseq/LTEE science validation |
| `hotSpring` | Public | GPU compute validation |
| `groundSpring` | Public | Geospatial validation |
| `airSpring` | Public | Atmospheric/ADS-B validation |
| `neuralSpring` | Public | Neural/AI validation |
| `ludoSpring` | Public | Game engine validation |
| `healthSpring` | Public | Health/clinical validation |

**Primals (ecoPrimals org):**

| Repo | GitHub Visibility | Content |
|------|-------------------|---------|
| `bearDog` | Public | Security, crypto, BTSP identity |
| `songBird` | Public | Discovery, routing, federation |
| `toadStool` | Public | Compute dispatch |
| `nestGate` | Public | Storage, content serving |
| `squirrel` | Public | AI/MCP orchestration |
| `rhizoCrypt` | Public | Provenance DAG |
| `loamSpine` | Public | Provenance spine |
| `sweetGrass` | Public | Provenance braid |
| `biomeOS` | Public | Orchestration layer |
| `petalTongue` | Public | Storytelling/UI bridge |
| `skunkBat` | Public | Defense/audit |
| `barraCuda` | Public | GPU compute dispatch |
| `coralReef` | Public | Distributed compute mesh |
| `bingoCube` | Public | Validation framework |
| `sourDough` | Public | Starter culture/bootstrap |

**Infrastructure (ecoPrimals org):**

| Repo | GitHub Visibility | Content |
|------|-------------------|---------|
| `plasmidBin` | Public | Binary depot, deploy scripts |
| `wateringHole` | Public | Ecosystem standards/docs |
| `whitePaper` | Public | Research documentation |

### Outer Membrane Only (GitHub-only)

Repos that exist solely for external visibility and don't need
inner membrane presence.

| Repo | Org | Content | Rationale |
|------|-----|---------|-----------|
| `fossilRecord` | ecoPrimals | Archived documentation | Public archive — no development, read-only fossil record |
| `sporePrint` | ecoPrimals | GitHub Pages deployment | Generated site — the deployment target IS GitHub Pages |

---

## Contamination Risk Matrix

| Risk | Vector | Repos Affected | Mitigation |
|------|--------|----------------|------------|
| API keys pushed to GitHub | Accidental `git add` of `.env` files | All primals, especially `squirrel` | `.gitignore` patterns cover `.env`, `*.env`, `.env.*` — verified ecosystem-wide |
| Operational secrets on GitHub | `cellMembrane` is on GitHub (private) | `cellMembrane` | Move to Forgejo-only (pending decision) |
| Local experiments leak to GitHub | Developer pushes WIP with sensitive data | Any repo | Pre-push hook checking for sensitive patterns (future) |
| Forgejo/GitHub divergence | Pull mirror fails or timer stops | All trailing-mirror repos | `forgejo_pull_mirror.sh --status` + `forgejo_sync.sh --status` checks |

### .env Audit Summary (May 17, 2026)

| File | Git-Tracked | Content | Risk |
|------|-------------|---------|------|
| `squirrel/.env` | No (gitignored) | JWT_SECRET | None — local only |
| `squirrel/mcp-config.env` | No (gitignored) | OpenAI/Anthropic/HuggingFace API keys | None — local only |
| `bearDog/production.env` | Yes | Template config (no real secrets) | None — placeholder values |
| `songbird/config/production.env` | No (gitignored) | Template DB URL with placeholder password | None — local only |
| `hotSpring/metalForge/*.env` | Yes | GPU/hardware config | None — no secrets |
| `plasmidBin/ports.env` | Yes | Port assignments | None — no secrets |
| `ecoPrimals/.env.test` | Yes | Test env vars (RUST_LOG, timeouts) | None — no secrets |

---

## Forgejo Operational Status

### Current Reality (May 23, 2026)

Forgejo is the **trailing inner membrane mirror**. GitHub is authoritative.
When covalent gates host Forgejo on sovereign infrastructure, we invert.

- **31/31 trailing-mirror repos** synced to Forgejo (cellMembrane is inner-only)
- All 3 Forgejo orgs populated: sporeGarden (5), ecoPrimals (19), syntheticChemistry (8)
- **25 repos**: Native Forgejo **pull mirrors** from GitHub (auto-sync every 8h, server-side)
- **6 repos**: Regular repos, synced via `forgejo_sync.sh` + systemd timer (8h)
  - Private on GitHub: `bearDog`, `skunkBat`, `whitePaper`
  - Large/clone-timeout: `neuralSpring`, `primalSpring`, `wetSpring`
- **1 repo**: `cellMembrane` — inner-only, direct push (not mirrored from GitHub)
- CI still runs on GitHub Actions (`notify-sporeprint.yml`, etc.)
- Forgejo reachable at `127.0.0.1:3000` (LAN) and `git.primals.eco:3000` (tunnel)

**Why pull, not push?** Dev happens across multiple gates (ironGate, eastGate,
southGate, etc.). Per-machine push hooks don't scale. Server-side pull mirrors
ensure Forgejo stays consistent regardless of which gate pushed to GitHub.

### Sync Tooling

| Tool | Location | Purpose |
|------|----------|---------|
| Native pull mirrors | Forgejo server-side | 25 repos auto-sync from GitHub every 8h |
| `forgejo_sync.sh` | `gardens/cellMembrane/forgejo_sync.sh` | Sync 6 non-mirror repos (fetch origin → push forgejo) |
| `forgejo-sync.timer` | `~/.config/systemd/user/` | Systemd timer fires `forgejo_sync.sh` every 8h |
| `forgejo_pull_mirror.sh` | `gardens/cellMembrane/forgejo_pull_mirror.sh` | Manage native mirrors (migrate, status, trigger sync) |

### Migration Path

1. ~~**GitHub-only development**~~ — completed May 23, 2026
2. ~~**Push-based sync**~~ — replaced May 23, 2026 (doesn't scale to multi-gate)
3. **Current**: Forgejo pulls from GitHub server-side. GitHub remains
   operationally primary for CI and dev. Forgejo is lagging mirror.
4. **Near-term**: Port `notify-sporeprint.yml` to Forgejo Actions,
   validate CI parity. Move 3 private repos to native mirrors with GitHub PAT.
5. **Inversion**: When covalent gates host Forgejo, it becomes primary.
   GitHub becomes the push mirror target.

---

## Decision: cellMembrane Placement

**Context**: `cellMembrane` is the only private repo in the
`sporeGarden` GitHub org. It contains VPS IP addresses, SSH key
management procedures, TURN credential paths, and RustDesk key
material. Its `.gitignore` correctly excludes `.age`, `.pem`, `id_*`,
`.key`, and token files.

**Options**:

1. **Forgejo-only** (recommended): Remove from GitHub entirely. All
   access via Forgejo tunnel. Cleaner sovereignty posture — ops data
   never touches external substrate.

2. **Keep GitHub private**: Convenient for cross-machine pulls without
   tunnel. Relies on GitHub's private repo access controls.

**Recommendation**: Move to Forgejo-only when Forgejo is confirmed
operationally stable (reachable, backups working). Until then, GitHub
private is acceptable as a transitional state.

---

## Push Policy Enforcement

### Automated (current — May 23, 2026)

**Server-side pull mirrors** (25 repos): Forgejo natively pulls from
GitHub every 8h. Zero dev-machine involvement. Triggered via
`POST /api/v1/repos/{owner}/{repo}/mirror-sync` for on-demand sync.

**Systemd timer** (6 non-mirror repos): `forgejo-sync.timer` runs
`forgejo_sync.sh` every 8h on the Forgejo host (ironGate). Fetches
from GitHub origin, pushes to local Forgejo. Independent of which
dev machine pushed to GitHub.

```bash
# Check mirror status (all 31 repos)
FORGEJO_TOKEN=<tok> ./forgejo_pull_mirror.sh --status

# Sync 6 non-mirror repos manually
./forgejo_sync.sh

# Trigger all native mirrors + sync non-mirrors
FORGEJO_TOKEN=<tok> ./forgejo_sync.sh --all

# Force-push diverged repos (after rebase)
./forgejo_sync.sh --force
```

### Inner-only enforcement (future)

A pre-push hook can enforce the membrane boundary for `cellMembrane`:

```bash
# .git/hooks/pre-push (inner-only repos)
remote="$1"
if [[ "$remote" == "origin" ]]; then
  echo "ERROR: This repo is inner-membrane-only. Push to forgejo instead."
  exit 1
fi
```

Post-inversion: Forgejo post-receive hooks auto-mirror to GitHub.

---

## Cross-References

- `SOVEREIGNTY_STANDARDS.md` — Forgejo as Primary Git Host section
- `MEMBRANE_CHANNEL_ARCHITECTURE.md` — Physical channel architecture
- `projectNUCLEUS/deploy/forgejo_mirror.sh` — Legacy setup tooling (creates repos + adds remotes)
- `CELLMEMBRANE_FIELDMOUSE_DEPLOYMENT.md` — fieldMouse VPS specification
- `cellMembrane/README.md` — Operational repo documentation

---

## Changelog

| Date | Change |
|------|--------|
| 2026-05-17 | Initial version — repo membrane boundary classification from infrastructure review |
| 2026-05-23 | Forgejo synced (31/31 repos). Pull-mirror model: 25 native mirrors + 6 timer-synced + 1 inner-only. Cursor hooks removed (wrong model for multi-gate). |
