# Wave 58b — Remaining Work to Stadial Entry (updated)

**Date:** May 28, 2026 (updated after ecosystem-wide pull)
**From:** primalSpring coordination
**To:** All teams

---

## Ecosystem State

The mountain responded. After our Wave 58 blurbs, 4 of 4 Tier 2 primals
shipped env var work: bearDog created `env_keys.rs` (290 constants),
songbird fully adopted `songbird-process-env` (48 sites + 146 expect
migrations), squirrel centralized 316 constants, biomeOS shipped `env_config`
(90+ literals). projectFOUNDATION elevated to full Rust (5 crates).
lithoSpore retired dead code and created `env_vars.rs`. Fresh ecoBins
harvested. Env var centralization is now **complete or in progress across
all 13 primals**.

---

## What's Done (no further action needed)

| Item | Owner | Wave |
|------|-------|------|
| NC-1 code: `biomeos-pseudospore` + emit materialization | biomeOS | 57 |
| biomeOS env centralization: `env_config` module (90+ literals) | biomeOS | 58b |
| VPS deployment standard: `--uds-only`, TransportMode, spring overlays | cellMembrane | 56 |
| cellMembrane deep debt: 95.8% coverage, typed errors, licensing | cellMembrane | 57 |
| Deploy scripts: all 13 primal `--uds-only` + socket health | projectNUCLEUS | 58 |
| projectNUCLEUS: async-correct, wire-native discovery, 166 tests | projectNUCLEUS | 58 |
| projectFOUNDATION: Rust elevation Phase B (5 crates) | projectFOUNDATION | 58b |
| lithoSpore: dead code retired, `env_vars.rs`, NC-5 preparation | lithoSpore | 58b |
| Env var centralization (8 primals pushed by primalSpring) | primalSpring coord | 57b |
| bearDog: `env_keys.rs` (290 constants), orphan purge (21 files) | bearDog | 117b |
| songbird: `songbird-process-env` full adoption, 146 `#[expect` | songbird | 58 |
| squirrel: 316 env constants, self-identity eliminated, 5,417L purge | squirrel | 58 |
| primalSpring local debt: zero `#[allow]` → `#[expect]`, dispatch telemetry persistence | primalSpring | 58b |
| Port SSOT reconciliation | cellMembrane + primalSpring | 56 |
| Wire-native newline JSON-RPC discovery | projectNUCLEUS | 58 |

---

## What Remains — Ordered by Critical Path

### P0: Live Deployment (blocks everything)

| Action | Owner | Blocker |
|--------|-------|---------|
| Deploy biomeOS v3.84 to VPS via plasmidBin | cellMembrane + ops | None — fresh ecoBin harvested |
| Test `biomeos deploy graphs/cells/hotspring_cell.toml` on VPS | cellMembrane + hotSpring | biomeOS on VPS |

### P1: First Spring Emissions (blocks NC-5 + stadial)

| Action | Owner | Blocker |
|--------|-------|---------|
| hotSpring column U pass (first emission) | hotSpring + biomeOS | P0 |
| groundSpring column U pass (second emission) | groundSpring + biomeOS | P0 |

### P2: Gate Stabilization (blocks stadial NC-2/NC-4)

| Action | Owner | Blocker |
|--------|-------|---------|
| southGate 13/13 health (currently 7/13) | wetSpring/neuralSpring ops | Songbird peers config |
| biomeGate 13/13 primals (currently 9/13) | hotSpring ops | Primal binaries |

### P3: Sovereignty Completion (progressive, not blocking)

| Action | Owner | Blocker |
|--------|-------|---------|
| NS registrar cutover (NC-3.3) | cellMembrane + registrar | External |
| Forgejo releases (NC-3.4) | cellMembrane + plasmidBin | Forgejo config |
| sporePrint living content (NC-3.5) | cellMembrane + petalTongue | BearDog `auth.issue_session` scope |

### P4: Remaining Primal Env Debt (reduced — most resolved this wave)

| Primal | Status | Remaining |
|--------|--------|-----------|
| ~~bearDog~~ | **RESOLVED** Wave 117b | `env_keys.rs` (290 constants). Residual: PRIMAL_CONTRACTS method catalog stale. |
| ~~songbird~~ | **RESOLVED** Wave 58 | `songbird-process-env` fully adopted. Zero hardcoded env in prod. |
| squirrel | **IN PROGRESS** | 316 constants built, ~93 files still have raw `std::env::var`. SDK config layer next. |
| toadStool | **PENDING** | ~200 env sites. `env_overrides.rs` split needed. VFIO domain complexity. |

### P4b: Remaining Primal Clippy Debt (reduced)

| Primal | Status | Notes |
|--------|--------|-------|
| ~~songbird~~ | **RESOLVED** Wave 58 | 146 `#[expect` migrations complete. |
| toadStool | **PENDING** | ~17 `#[allow(clippy::` + `unused_async` |
| ~~squirrel~~ | **RESOLVED** Wave 58 | Covered in deep debt session. |

---

## Stadial Entry Criteria

```
NC-1: 2+ springs pass column U        → GATED on P0/P1
NC-2: 3+ gates meshed                  → GATED on P2
NC-4: all 4 named gates healthy        → GATED on P2
NC-3: partial satisfaction sufficient   → ADVANCING
NC-5: progressive after NC-1 live      → UNBLOCKED
```

**Critical path unchanged**: P0 (deploy v3.84) → P1 (2 emissions) → stadial candidate.

**P4 env debt is nearly eliminated.** Only squirrel (in progress) and toadStool
(pending) remain. 11 of 13 primals have fully centralized env vars.

---

*Wave 58b. Mountain responded. Deploy the ecosystem.*
