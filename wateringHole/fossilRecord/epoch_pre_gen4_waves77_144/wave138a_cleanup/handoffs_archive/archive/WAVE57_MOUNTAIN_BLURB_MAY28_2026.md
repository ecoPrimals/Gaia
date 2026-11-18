# Wave 57 Mountain Blurb — Upstream Primals

**Date:** May 28, 2026 (updated)
**From:** primalSpring coordination
**To:** All 13 primal teams (upstream mountain)

---

## State of the Mountain

primalSpring is clean. Wave 57 completed the final local debt sweep: main.rs
split into 3 focused modules, all env vars centralized, zero production
unwraps/unsafe/todo, zero clippy suppressions without reason, all doctests fixed.
797 lib tests, 56 scenarios, zero clippy warnings.

**primalSpring coordination pushed env var centralization to 8 primals this wave.**
This eliminates hardcoded `std::env::var("LITERAL")` across the mountain, matching
the `env_keys.rs` pattern established in primalSpring.

---

## What We Pushed (8 primals, committed & pushed)

| Primal | Constants | Files | Pattern | Tests |
|--------|-----------|-------|---------|-------|
| **sourDough** | 3 keys | 7 files | new `env_keys.rs` + scaffold template | 185 pass |
| **sweetGrass** | 3 keys | 3 files | extended `primal_names::env_vars` | 878+ pass |
| **skunkBat** | 18 keys | 15 files | new `env_keys.rs` | 376 pass |
| **rhizoCrypt** | 22 keys | 10 files | completed `safe_env` migration | 883+ pass |
| **loamSpine** | 30+ keys | 13 files | completed `env_resolution` + facades | all pass |
| **petalTongue** | 60 keys | 17 files | new `constants/env_vars.rs` | 1583+ pass |
| **coralReef** | 22 keys | 16 files | new `env_keys.rs` + 3 clippy fixes | all pass |
| **barraCuda** | 30 keys | 15 files | new `env_keys.rs` (core + device) | 3867 pass |

**Total: ~188 env var constants centralized across 96 files in 8 primals.**

---

## Remaining Per-Primal Action Items

### biomeOS — **CRITICAL PATH**
- NC-1 COMPLETE code-side. **Action: deploy v3.81 to cellMembrane VPS via plasmidBin**
- Once live: hotSpring column U pass becomes unblocked (first spring emission)
- `biomeos deploy graphs/cells/hotspring_cell.toml` — test on live VPS

### bearDog — **NEEDS TEAM** (env epic)
- ~550 env var sites across 130 files — multi-crate migration
- `zero_hardcoding.rs` exists but literals remain widespread
- **Action**: enforce `zero_hardcoding.rs` philosophy, track as env migration epic
- NC-3.5 sporePrint: `auth.issue_session` scope expansion needed

### songbird — **NEEDS TEAM** (env + clippy)
- ~70 env sites across 35 files — `songbird-process-env` crate exists but not fully adopted
- ~180 `#[allow(clippy::` in test modules (batch `expect` migration)
- **Action**: adopt `songbird-process-env` everywhere; batch clippy expect migration

### squirrel — **NEEDS TEAM** (SDK config sprawl)
- ~250 env sites across 90 files — SDK `infrastructure/config.rs` is the hotspot
- 3 `#[allow(clippy::` in prod-adjacent code
- **Action**: extract shared env constants from SDK config layer

### toadStool — **NEEDS TEAM** (domain complexity)
- ~200 env sites, `env_overrides.rs` (70+ literals in one file) needs split
- ~17 `#[allow(clippy::` + extensive VFIO unsafe (domain-required)
- **Action**: split `env_overrides.rs` into domain modules; `unused_async` quick fix

### lithoSpore
- NC-5 **UNBLOCKED** — NC-1.4 resolved, `--from-dir` emission path shipped
- **Action**: prepare for first live postPrimordial emission once 2 springs pass column U

---

## Canonical Health Method

**`health.liveness`** is the canonical health method across all primals.
All 13 primals implement it. Certification Layer 2 uses `health.liveness`.

---

## Niche Climate Summary

```
NC-1  postPrimordial Spore Gateway    COMPLETE     Deploy v3.81 → first emission
NC-2  Multi-Gate NUCLEUS Mesh          IN PROGRESS  Songbird GAP-17/18 partial
NC-3  cellMembrane Sovereignty         CONSUMED     VPS standard absorbed
NC-4  Spring NUCLEUS Depth             ADVANCING    --uds-only across all deploy tooling
NC-5  lithoSpore postPrimordial        UNBLOCKED    Waiting on 2 spring emissions
```

**Critical path**: biomeOS v3.81 on VPS → hotSpring column U → groundSpring column U → NC-5 → stadial.

---

*Wave 57. 8 primals pushed upstream. Mountain converging. Deploy the ecosystem.*
