# Wave 58 Mountain Blurb — Upstream Primals

**Date:** May 28, 2026
**From:** primalSpring coordination
**To:** All 13 primal teams (upstream mountain)

---

## State of the Mountain

All code is delivered. primalSpring coordination pushed env var centralization
to 8 primals (Wave 57b), cellMembrane shipped 95.8% coverage with typed errors
(Wave 57), and projectNUCLEUS shipped async-correct discovery with 166 tests
(Wave 58). NC-1 is COMPLETE. The remaining path is live deployment.

---

## What We Pushed (8 primals — already committed)

| Primal | Constants | Files | Tests |
|--------|-----------|-------|-------|
| sourDough | 3 | 7 | 185 |
| sweetGrass | 3 | 3 | 878+ |
| skunkBat | 18 | 15 | 376 |
| rhizoCrypt | 22 | 10 | 883+ |
| loamSpine | 30+ | 13 | all pass |
| petalTongue | 60 | 17 | 1583+ |
| coralReef | 22 | 16 | all pass |
| barraCuda | 30 | 15 | 3867 |

**188 env var constants centralized across 96 files.**
No action needed from these 8 teams — changes are merged.

---

## Remaining Per-Primal Work

### biomeOS — **P0 CRITICAL PATH**
- NC-1 COMPLETE (code). **Deploy v3.84 to VPS** — unblocks all spring emissions.

### bearDog — Tier 2 (team-owned)
- ~550 env sites / 130 files. Enforce `zero_hardcoding.rs` pattern.
- NC-3.5: `auth.issue_session` scope for sporePrint.

### songbird — Tier 2 (team-owned)
- ~70 env sites. Adopt `songbird-process-env` crate fully.
- ~180 test `#[allow(clippy::` → batch `#[expect` migration.

### squirrel — Tier 2 (team-owned)
- ~250 env sites. Extract SDK env constants from `infrastructure/config.rs`.

### toadStool — Tier 2 (team-owned)
- ~200 env sites. Split `env_overrides.rs` (70+ literals) into domain modules.
- ~17 `#[allow(clippy::` fixes + `unused_async` cleanup.

### lithoSpore
- NC-5 UNBLOCKED. Prepare for first live emission after 2 springs pass column U.

---

## Niche Climate

```
NC-1  postPrimordial Spore Gateway    COMPLETE     Code done. Deploy v3.84.
NC-2  Multi-Gate NUCLEUS Mesh          IN PROGRESS  southGate 7/13 → 13/13
NC-3  cellMembrane Sovereignty         CONSUMED     95.8% coverage, typed errors
NC-4  Spring NUCLEUS Depth             ADVANCING    166 tests, wire-native discovery
NC-5  lithoSpore postPrimordial        UNBLOCKED    Waiting on 2 spring emissions
```

**Critical path**: v3.84 on VPS → hotSpring column U → groundSpring → NC-5 → stadial.

---

*Wave 58. Mountain clean. Deploy the ecosystem.*
