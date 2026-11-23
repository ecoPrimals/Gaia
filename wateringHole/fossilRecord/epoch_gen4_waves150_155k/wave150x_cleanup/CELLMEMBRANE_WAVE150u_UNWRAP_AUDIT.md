# cellMembrane Wave 150u — Unwrap Audit Results

**Date:** 2026-07-22
**Primal:** cellMembrane
**Wave:** 150u
**Author:** cellMembrane team (ironGate)
**Assignment:** #6 — Audit and eliminate production `.unwrap()` calls

---

## Result: 0 Production Unwraps (confirmed)

This is the third verification of the same finding, originally documented in
Wave 150k and Wave 150o. The "456 production unwrap" count from the dimensional
review is a **false positive** caused by the audit methodology.

## Definitive Proof

```
$ cargo clippy --workspace -- -W clippy::unwrap_used
Finished `dev` profile [...] in 19.22s
(exit code 0, zero warnings)
```

`clippy::unwrap_used` is the lint the blurb recommends. It analyzes actual
production code paths and correctly excludes `#[cfg(test)]` module bodies.
**Zero warnings** = zero production unwraps.

## Raw Counts

| Metric | Count |
|--------|-------|
| Total `.unwrap()` in codebase | 551 |
| In `#[cfg(test)]` module bodies | 551 |
| In production code | **0** |
| `.expect()` with invariant comments | 0 |
| `panic!()` in production | 0 |
| `todo!()` in production | 0 |

## Why The Audit Over-Counted

The dimensional review grep methodology:
1. Counts all `.unwrap()` lines in `*.rs` files
2. Subtracts lines containing `#[test]` or `#[cfg(test)]`

This misses the fact that `#[cfg(test)]` is a **module attribute** — it gates
an entire `mod tests { ... }` block (often 50-200 lines). A line like
`serde_json::to_string(&cfg).unwrap()` inside that block has no `#[cfg(test)]`
on the same line, so the grep counts it as "production."

**Fix for audit methodology**: Use `cargo clippy -- -W clippy::unwrap_used`
instead of grep. This is what nestGate, loamSpine, toadStool, and esotericWebb
used to confirm their counts were also false positives.

## Test-Module Annotation Decision

The blurb suggests annotating test unwraps with `#[expect(clippy::unwrap_used)]`.
cellMembrane does **not** enable `clippy::unwrap_used` in its default lint
configuration (pedantic + nursery + specific denies). Adding 551 `#[expect]`
annotations would add noise without value. If the ecosystem adopts
`clippy::unwrap_used` as a workspace-level deny in the future, we'll add
module-level `#[expect]` on the test modules (not per-call), which is ~30
annotations total.

## Health Metrics

- **Tests:** 1,101 (all passing)
- **Clippy:** 0 warnings (pedantic + nursery)
- **Fmt drift:** 0 files
- **Unsafe code:** 0 (`#![forbid(unsafe_code)]` on all crates)

## Prior Documentation

- Wave 150k: Full audit of 551 `.unwrap()` — all test-only
- Wave 150o: Documented as false positive in GLACIAL_SHIFT_TRACKER
- Wave 150t: Reiterated in docs sweep handoff

## For Overwatch

The "456 production unwrap" item for cellMembrane should be marked **RESOLVED
(false positive)** in the dimensional review scorecard. cellMembrane matches
the 0-production-unwrap standard already achieved by nestGate, loamSpine,
toadStool, and esotericWebb.

Recommend updating the audit methodology across the ecosystem to use
`cargo clippy -- -W clippy::unwrap_used` as the canonical unwrap counter.
