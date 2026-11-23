# flockGate Wave 150i AAR — Sync Divergence + Depot Gap Report

**Date**: 2026-07-19 | **Wave**: 150i | **From**: flockGate WAN overwatch
**Gate**: flockGate (10.13.37.6) | **Role**: WAN covalent validation

---

## Summary

flockGate is CONVERGED and STABLE. All surfaces LIVE, systemd linger confirmed
(10h+ uptime overnight), ZERO P0/P1 items. However, two upstream deliverables
referenced in the Wave 150i blurb have NOT propagated to shared remotes.

---

## Current State (Verified Jul 19 07:02 EDT)

| Check | Result |
|-------|--------|
| primalSpring suite | 169 scenarios, 1,206 tests, 0 failures |
| WAN surfaces | 5/5 LIVE (footprint 155ms, webb healthy, sporeprint 178ms, live 316ms, git 134ms) |
| esotericWebb | V19.1 LIVE, systemd active 10h+, linger confirmed |
| Mesh | UP, 2 peers registered, handshakes fresh |
| P0/P1 | 0 / 0 |

---

## Sync Divergence — ACTION NEEDED FROM OVERWATCH

### 1. esotericWebb V22 — Source Not on Any Remote

The blurb says "V22 LIVE — SCENE BINDING FIXED" on flockGate. In reality:
- `git fetch origin` → no new commits (HEAD = `08588d5`, V19.1)
- `git fetch forgejo` → no new commits
- V19.1 IS running and healthy at `webb.primals.eco`
- V22 source (scene binding, `visualization.render.scene`) has not been pushed

**Action**: eastGate needs to push V20–V22 commits to origin or forgejo.
flockGate will rebuild and redeploy immediately upon receipt.

### 2. primalSpring CAC Scenario — Not on Origin

The blurb says "primalSpring CAC scenario — IMPLEMENTED (171 scenarios, 15
known-debt, 8a456bf)". In reality:
- `git fetch origin` → no new commits (HEAD = `c677c3c`, 169 scenarios)
- `git fetch forgejo` → 2 commits ahead (Wave 150d/b parallel fixes, NOT the CAC scenario)
- Commit `8a456bf` is not on any remote flockGate can access

**Action**: eastGate needs to push `8a456bf` (or its lineage) to origin.

---

## Depot Architecture Observation

esotericWebb is NOT a genomeBin primal — it's a garden composition. The depot
(`membrane.primals.eco/depot/primals/`) contains only the 16 core binaries:

```
barracuda, beardog, biomeos, coralreef, loamspine, membrane,
nestgate, nucleus_launcher, petaltongue, rhizocrypt, skunkbat,
songbird, sourdough, squirrel, sweetgrass, toadstool
```

esotericWebb is NOT part of the depot pipeline. It runs from `target/release/`
in the source tree on flockGate, managed by systemd user unit. This is correct
architecture — compositions are deployed from source, primals from depot.

**However**: the depot pipeline should ensure ALL genomeBin primals are pushed.
The current 16 binaries per musl arch are correct. The blurb's reference to
"esotericWebb depot binary" appears to be a categorization error — webb is a
composition, not a primal, and doesn't belong in the primal depot.

If overwatch wants composition binaries distributed via depot, a separate
`depot/compositions/` path would be needed. This is a P3 architectural decision.

---

## Remaining Divergence (flockGate Perspective)

| Priority | Item | Owner | Status |
|----------|------|-------|--------|
| — | esotericWebb V22 source push | eastGate | BLOCKED — not on remotes |
| — | primalSpring 8a456bf push | eastGate | BLOCKED — not on remotes |
| P2 | `primals.eco` DNSSEC | ops / Cloudflare | Enable via API |
| P2 | `footprint_composition.toml` URL | cellMembrane | Still path-based |
| P3 | Composition depot path (`depot/compositions/`) | architectural | Not started |

---

## Recommendations for Overwatch

1. **Push V22 to origin** — flockGate will deploy within minutes of landing
2. **Push primalSpring `8a456bf`** — flockGate will rebase and run suite
3. **Clarify depot scope** — genomeBin primals only, or compositions too?
   If compositions: define `depot/compositions/{target}/{name}` layout.
4. **All 16 genomeBin primals ARE in depot** — x86_64-musl and aarch64-musl
   both have 16 binaries. Android (12) and Windows (11) pending re-harvest.

---

*flockGate Wave 150i: STABLE. V19.1 live and healthy. Blocked on upstream
pushing V22 + CAC scenario to shared remotes. Depot observation: esotericWebb
is a composition, not a genomeBin primal — it doesn't belong in the primal
depot pipeline. All 16 actual primals ARE in depot for musl targets.*
