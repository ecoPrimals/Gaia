# sporePrint Overwatch AAR — Wave 147c

**Date**: Jul 17, 2026 | **From**: eastGate overwatch (primalSpring perspective)
**Scope**: sporePrint deep debt + thesis metric evolution + primalSpring cleanup

---

## What Happened

Two sporePrint commits and one primalSpring commit, driven by primalSpring
overwatch analysis of validation coverage and content currency.

### Commit 1: `9daf112` — deep debt sweep (spore-validate)

| Dimension | Change |
|---|---|
| Hardcoding → agnostic | `WELL_KNOWN_PEERS` → extensible `peer_hints()` via `SPOREPRINT_EXTRA_PEERS` env |
| Hardcoding → agnostic | Transport error messages decoupled from "NestGate" → transport-agnostic |
| Constants extraction | `certify.rs`: `"1.0.0"` / `"5%/30d"` → `SCHEMA_VERSION` / `DRIFT_TOLERANCE` |
| Dead code → wired | `edges_for_entity()` → isolated node count in graph command |
| Dead code → wired | `is_warning()` → validation display filter |
| Idiomatic Rust | `Duration::as_millis()` replaces manual latency math |
| Doc hygiene | `content-manifest.toml` drift fixed, DNS cutover marked complete, spec wave stamps updated |
| Cleanup | `cargo clean` (1.8GB), `public/` removed |

### Commit 2: `25cab9c` — thesis metric evolution

Evolved hardcoded LOC/test counts in 6 thesis chapters to live `entity_stat()`
and `total_stat()` shortcodes. Numbers now render from `config.toml` entity
registry and stay current via `spore-validate refresh --write`.

| File | Shortcodes Added | What Changed |
|---|---|---|
| `thesis/05_system_architecture.md` | 24 `entity_stat` + 10 `total_stat` | Per-primal table (12 rows), aggregate table (7 rows), prose |
| `thesis/13_quantitative_evidence.md` | 8 `entity_stat` + 3 `total_stat` | Primal specialization prose, ecosystem scale prose |
| `thesis/00_front_matter.md` | 3 `total_stat` | Abstract ecosystem numbers |
| `thesis/01_introduction.md` | 3 `total_stat` | Opening paragraph numbers |
| `thesis/15_discussion.md` | 1 `total_stat` | Test count in AI methodology caveat |
| `thesis/16_conclusion.md` | 4 `total_stat` | Closing paragraph numbers |
| `specs/CONTEXT.md` | — | Companion count ~80 → ~105 |
| `static/llms.txt` | — | Companion count synced |
| `specs/EVOLUTION_QUEUE.md` | — | 2 items checked off, 1 reworded |
| `story/i_dont_know_rust.md` | — | Description test count 114K → 116K |

Historical thesis data points (11,161 checks at March 2026) preserved as
narrative claims — correct practice for temporal arguments.

### Commit 3: `863e28b3` — primalSpring cleanup

Removed stale KNOWN_DEBT comment in `mod.rs:463` referencing
`sporeprint-pure-primal-parity` as Wave 138b debt. Scenario has been
passing since Wave 147b. Only `graphenegate-readiness: 1` remains.

---

## What Went Well

- **primalSpring overwatch surfaced real gaps**: stale thesis numbers, stale
  KNOWN_DEBT comment, understated companion count — all found by systematic
  cross-repo review
- **Shortcode evolution pattern works**: 43 shortcode calls replace 43
  hardcoded numbers. Future `refresh --write` automatically keeps all thesis
  claims current
- **Zero breakage**: Zola builds 302 pages, spore-validate validates clean,
  primalSpring sporePrint tests 4/4 pass

## What Didn't Go Well

- **`membrane temporal.cascade` blocked**: `ecosystem_manifest.toml` has
  `zone = "house1"` for northGate, but cellMembrane's zone enum only allows
  `backbone, house2, garage, wan, unassigned`. Manual push to both remotes
  required as workaround.
- **wateringHole merge conflicts**: Blurb diverged across GitHub/Forgejo
  from concurrent upstream pushes. Required manual conflict resolution.

## Upstream Gaps Identified

| Gap | Owner | Priority |
|-----|-------|----------|
| `zone = "house1"` variant in cellMembrane topology enum | cellMembrane | P1 (blocks cascade) |
| primalSpring scenarios don't invoke `spore-validate` CLI | primalSpring | P2 (semantic depth) |
| primalSpring doesn't validate Zola build output | primalSpring | P2 |
| Freshness head stale in `config/ecosystem/freshness.toml` | primalSpring | LOW |
| SP-3 liveSpore auto-ingest feed | sporePrint CI | LOW |

## Metrics Post-AAR

| Metric | Value |
|--------|-------|
| sporePrint pages | 302 |
| sporePrint entities | 79 |
| spore-validate tests | 289 |
| spore-validate warnings | 0 |
| spore-validate clippy | 0 |
| primalSpring sporePrint tests | 4/4 PASS |
| primalSpring KNOWN_DEBT | 1 (graphenegate only) |
| Thesis shortcode calls | 43 (replacing hardcoded metrics) |

---

*This AAR covers sporePrint commits `9daf112` and `25cab9c`, and
primalSpring commit `863e28b3`. All pushed to GitHub + Forgejo.*
