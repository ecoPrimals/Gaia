# cellMembrane Ecosystem Audit — May 23, 2026

**From**: cellMembrane team (ironGate)
**For**: primalSpring (upstream audit), all primal teams
**Type**: Ecosystem doc sweep + gap report
**Status**: Active — requesting upstream review
**Updated**: May 24, 2026 — Forgejo model change, debris sweep results

---

## Summary

cellMembrane team performed a full ecosystem doc sweep across `infra/wateringHole/`,
`infra/plasmidBin/`, `gardens/cellMembrane/`, and all spring/garden READMEs. Fixed
all Channel 3 / firewall / ownership drift in wateringHole standards. Identified
remaining gaps for upstream teams to triage.

---

## What cellMembrane Fixed (this sweep)

### wateringHole standards (Channel 3 / ownership / firewall corrections)

| Document | Fix |
|----------|-----|
| `MEMBRANE_CHANNEL_ARCHITECTURE.md` | Channel 3 now LIVE (was "CLOSED"), UFW 80/443 open, Tower units Active, evolution path updated |
| `CELLMEMBRANE_FIELDMOUSE_DEPLOYMENT.md` | Firewall table shows 80/443 open, escalation ladder deduped + Phase 1.5 added, ownership updated |
| `SOVEREIGNTY_STANDARDS.md` | Channel 3 status LIVE (was "SHADOW") |
| `GLOSSARY.md` | cellMembrane ownership → cellMembrane team (ironGate), channel status current |
| `GLACIAL_SHIFT_READINESS.md` | Date bumped to May 23, DNS owner → cellMembrane team |

### Stale handoff TODOs

| Document | Fix |
|----------|-----|
| `SONGBIRD_WAVE214_DEEP_DEBT_EVOLUTION_MAY20_2026.md` | Relay deploy TODO marked DONE, S2 shadow status → LIVE |
| `PROJECTNUCLEUS_MEMBRANE_VPS_HANDOFF_MAY14_2026.md` | Supersession banner added (historical snapshot) |

### Stale READMEs

| Document | Fix |
|----------|-----|
| `springs/hotSpring/README.md` | plasmidBin path fixed (`primals/biomeOS/plasmidBin/` → `infra/plasmidBin/`), primalSpring v0.9.25 → v0.9.27 |
| `infra/plasmidBin/README.md` | Missing scripts added (sync.sh, build-primal.sh, cell_launcher.sh, deploy_membrane.sh), method count 445 → 458, Wave 35 → 46 |

### cellMembrane repo (private)

| File | Status |
|------|--------|
| `README.md` | Full rewrite — Channel 3 Surface, Caddy TLS, sporePrint cache, Nest readiness |
| `VPS_STATE.md` | New — live snapshot of all services, ports, filesystem layout |
| `GLACIAL_SHIFT_TRACKER.md` | New — in-repo tracking of 6 stadial entry criteria |
| `RUNBOOKS.md` | New — 9 operational procedures for all channels |
| `IRONGATE_VERIFICATION.md` | Updated — Phase 1 Tower + Channel 3 verification |
| Forgejo remote | Synced — was 1 commit behind, now current |

### Forgejo inner membrane model (May 24 update)

The initial push-based Cursor hook approach (auto-mirror on every `git push`) was
**replaced** with a server-side pull model. Per-machine hooks don't scale across
multiple dev gates (ironGate, eastGate, southGate, etc.).

**New model**:
- 25 repos: Native Forgejo pull mirrors from GitHub (auto-sync every 8h, server-side)
- 6 repos: Timer-synced via `forgejo_sync.sh` + systemd timer (8h interval)
  - Private on GitHub: bearDog, skunkBat, whitePaper
  - Clone-timeout: neuralSpring, primalSpring, wetSpring
- cellMembrane: Inner-only (direct push, not mirrored from GitHub)

**Tooling**: `forgejo_pull_mirror.sh` (manage mirrors), `forgejo_sync.sh` (sync non-mirrors),
`forgejo-sync.timer` (systemd). Cursor hooks removed. `REPO_MEMBRANE_BOUNDARY.md` updated.

**Inversion plan**: When covalent gates host Forgejo on sovereign infrastructure,
Forgejo becomes primary and GitHub becomes the push mirror target.

### Debris sweep (May 24 update)

| Finding | Assessment |
|---------|------------|
| `GLOSSARY.md` header date | Bumped to May 24; stale "dual-push" language corrected to "trailing mirror" |
| `sort-after/` tree (~4 legacy repos) | Pre-ecoPrimals debris; strong archive candidate. Not blocking. |
| `hotSpring/scripts/archive/` (47 scripts) | Explicitly superseded per scripts/README.md — fossil record, not debris |
| `prep_usb_litho.sh` in handoff archive | Misplaced operational script; noted in P2 gaps |
| Duplicate `HOTSPRING_GATE_DEPLOYMENT` handoff | Exists in both `infra/wateringHole/handoffs/` and `springs/hotSpring/wateringHole/handoffs/` — hotSpring owns canonical copy |
| 3 active gate handoffs (ludo, hot, air) | Live gate status — archive after Wave 46 absorption confirmed |
| whitePaper thesis TODOs (3 in ch16) | Content work for wetSpring/thesis team, not operational |
| songBird NFC/IPC platform stubs | Known limitations, documented in crate READMEs |

---

## Gaps for Upstream Teams

### P1 — Requires primal team action

| Gap | Owner | Details |
|-----|-------|---------|
| `deploy_membrane.sh` nest validation doesn't check nest ports | **projectNUCLEUS** | `verify_composition` UFW check only looks for `22\|3478\|21115\|21116\|21117` — nest ports (9500, 9601, 9700, 9850) not included. False "unexpected UFW rules" warning on nest composition. |
| `deploy_membrane.sh` Channel 1 + Channel 3 deploy logic missing | **projectNUCLEUS** | No `deploy_channel_1_dns()` or `deploy_channel_3_surface()` functions exist. Caddy was deployed manually. knot-dns has no deployment path. |
| `capability_registry.toml` version drift | **primalSpring** | wateringHole copy is at meta v0.9.17, ecosystem is at v0.9.27. Sync needed. |
| `hbbs-membrane.service` hardcoded relay IP | **projectNUCLEUS** | Unit file has `-r [RELAY_PUBLIC]` hardcoded — not parameterized by deploy script. |
| nestGate "May 2026 deprecation removal" | **nestGate** | `nestGate/docs/architecture/ARCHITECTURE_OVERVIEW.md` says deprecated modules scheduled for removal May 2026 — due now. |
| nestGate "Next Review: January 20, 2026" | **nestGate** | `COLLABORATIVE_INTELLIGENCE_IMPLEMENTATION.md` — review date 4 months overdue. |

### P2 — Ecosystem-wide doc hygiene (no urgency)

| Gap | Location | Details |
|-----|----------|---------|
| `phase2/biomeOS/` path references | Multiple docs (STANDARDS_AND_EXPECTATIONS, bearDog specs, songBird specs) | Legacy path; biomeOS is at `primals/biomeOS/`. Structural drift, not operational. |
| `infra/benchScale`, `infra/agentReagents` path references | May 11 handoff tree diagrams | Now at `sort-after/`. Historical references in archived handoffs. |
| `GATE_DEPLOYMENT_STANDARD.md` broken link | `STANDARDS_AND_EXPECTATIONS.md` | File not found in wateringHole. Linked but never created. |
| March 2026 "front-loaded meeting" language | healthSpring `EXTENSION_PLAN.md`, `PAPER_REVIEW_QUEUE.md`, `EVOLUTION_MAP.md` | Meeting is past; language still reads as future. |
| `FACULTY_SPRING_PROFILES.md` March 3 coffee meeting | `infra/whitePaper/gen3/data/` | Scheduled date is past. |
| Duplicate `nucleus_launcher.sh` / `cell_launcher.sh` | `primalSpring/tools/` vs `plasmidBin/` | Parallel dev vs deploy copies — drift risk. |
| `prep_usb_litho.sh` misplaced | `wateringHole/handoffs/archive/` | Operational script in handoff archive; has hardcoded `/home/southgate` paths. |
| Duplicate membrane-provenance snapshots | `projectNUCLEUS/validation/archive/membrane-provenance-20260522-*` | Two snapshots 1 minute apart (102425, 102504). |

### P3 — Non-urgent archive hygiene

| Gap | Details |
|-----|---------|
| 148 archived handoffs lack an index | No `HANDOFF_INDEX.md` — discoverability is search-only. |
| ionChannel TODOs in sort-after | 4 TODOs in ionChannel crates (SSH creds, X11 backend, compositor, stream impl). Low priority — sort-after scope. |
| `infra/whitePaper/gen1/Draft/draft.md` | Milestones reference July–December 2025. Pre-current architecture. |
| `sort-after/benchScale/archive/docs-dec-2025/` | December 2025 release docs — archaeological. |

---

## False Positives (Confirmed Not Stale)

| Item | Why it's fine |
|------|---------------|
| neuralSpring session notes (S170–S171) referencing barraCuda v0.3.7 | Fossil record entries — describe state at that session. Current header says v0.4.0/S215. |
| sourDough template TODOs | Scaffold placeholders for new primals — intentional. |
| nestGate vendor `rustls-webpki` TODOs | Upstream vendored code — not ours. |
| `sort-after/` tree generally | Separate incubation; legacy scripts documented. |
| hotSpring `scripts/archive/` (47 .sh + 20 .py) | Explicitly superseded by `toadstool device`; documented in scripts/README.md. |
| Dual `nucleus_launcher.sh` (primalSpring/tools vs plasmidBin) | Dev vs deploy split by design — but drift risk exists. |
| All `**/archive/**`, `**/fossilRecord/**` directories | Explicit retention policy — not debris. |

---

## Tree Cleanliness

The ecoPrimals tree is **remarkably clean**:
- Zero `*.bak`, `*.tmp`, `*.old`, `*.orig`, `*~`, `.DS_Store`, `__pycache__`, `node_modules`
- Zero TODO/FIXME/HACK in production `.rs`/`.py`/`.sh` (outside vendor/templates/sort-after)
- All archive layers are intentional and documented
- No orphaned plasmidBin scripts found

Main debris is local `target/` build artifacts (gitignored) and a few validation log files
under `projectNUCLEUS/validation/archive/`.

---

## Requesting

1. **primalSpring**: Review P1 gaps, triage for Wave 47+
2. **projectNUCLEUS**: Address `deploy_membrane.sh` nest validation gap + Channel 1/3 deploy logic
3. **nestGate**: Review overdue deprecation removal + review date
4. **All primal teams**: Any `phase2/biomeOS/` path references in your docs should point to `primals/biomeOS/`
