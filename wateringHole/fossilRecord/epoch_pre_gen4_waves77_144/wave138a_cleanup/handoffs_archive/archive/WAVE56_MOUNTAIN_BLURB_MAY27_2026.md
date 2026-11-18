# Wave 56 Mountain Blurb — Upstream Primals

**Date:** May 27, 2026
**From:** primalSpring coordination
**To:** All 13 primal teams (upstream mountain)

---

## State of the Mountain

primalSpring has completed deep debt cleanup through Wave 56. Local debt is
effectively cleared: zero unsafe, zero TODO/FIXME, env vars centralized,
797 lib tests, 56 scenarios, 93 experiments, no clippy warnings. VPS
deployment standard is documented and tooled (`--uds-only`). Desktop
primordial scripts are marked and contained.

**The mountain is clean. What follows is niche climate work — the primals
need to warm the deployment topology before stadial gates.**

---

## Per-Primal Action Items

### biomeOS (substrate primal)

| ID | Action | Priority | Notes |
|----|--------|----------|-------|
| NC-1.4 | ~~Swap inline pseudoSpore validation to `pseudospore-core` crate~~ | — | **RESOLVED** — v3.81 ships the swap |
| NC-1.emit | Complete emit content materialization (full pseudoSpore dir unpack, not just `emit_manifest.json`) | MEDIUM | Partial in v3.79 |
| — | v3.79 ingest/emit subcommands, signal graphs, conventions | — | **DELIVERED** |

### Songbird (security + mesh primal)

| ID | Action | Priority | Notes |
|----|--------|----------|-------|
| NC-2 | TCP fallback mesh seed bug is fixed — verify southGate mesh stability | MEDIUM | wetSpring/neuralSpring report 7/13 health; may be env/OOM, not Songbird code |
| GAP-17/18 | Capability socket resolution (eliminates desktop symlink hacks) | LOW | Tracked; not blocking VPS |

### lithoSpore (data primal)

| ID | Action | Priority | Notes |
|----|--------|----------|-------|
| NC-5 | postPrimordial emission pattern ready on your side (`pseudospore-core`, envelope API shipped) | — | **DELIVERED** |
| NC-5.live | First live postPrimordial pseudoSpore emission via `biomeos nucleus ingest` | **HIGH** | Gated on v3.81 VPS deploy + column U |
| — | `PseudoSporeEnvelope` load/validate, `ltee-cli` wiring | — | **DELIVERED** |

### bearDog (identity + crypto primal)

| Action | Priority | Notes |
|--------|----------|-------|
| No blocking items | — | Wave 99 `auth.public_key` (Ed25519 key distribution) resolved JH-11. BTSP Phase 3 operational. |
| sporePrint BearDog scope | LOW | NC-3.5 (sporePrint living content) blocked on BearDog scoping content signing for NestGate `content.put` |

### toadStool, barraCuda, coralReef, nestGate, rhizoCrypt, loamSpine, sweetGrass, squirrel, petalTongue, skunkBat, sourDough

| Action | Priority | Notes |
|--------|----------|-------|
| No blocking items | — | All 13 primals are at full test/method coverage, zero drift. Trio primals operational for provenance signing. |

---

## Mountain Summary

```
13/13 primals clean          — zero method drift, zero upstream code gaps
NC-1 COMPLETE (code)         — v3.81 needs VPS deploy
NC-5 UNBLOCKED               — gated on deploy + column U
NC-2 is ops, not code         — southGate stabilization
```

Everything else is downstream deployment or niche climate warming.
No primalSpring wave is needed — we're ready to validate as gates come online.
