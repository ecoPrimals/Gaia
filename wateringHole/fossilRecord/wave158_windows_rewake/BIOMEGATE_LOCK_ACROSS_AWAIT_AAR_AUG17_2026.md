# AAR — Lock Held Across Await: Ten Sites, One Migration

**Author**: biomeGate <biomegate@primals.eco>
**Date**: August 17, 2026 — S383
**Repos**: `toadStool` @ `31d583170`
**For**: overwatch triage — *modern-systems debt or early-primal pattern for excision?*

---

## Answer to the triage question

**Neither.** This is not a fossil of early primal patterns, and it is not a
consequence of modern async design. Every one of the ten defective sites was
**introduced by a deep-debt cleanup commit**, and three of them by a single
migration whose stated goal was legitimate and whose mechanism was mechanical.

The debt was manufactured by the debt-removal process.

That distinction matters for triage: **excising an "early pattern" would remove
nothing here**, because the pattern predates nothing. The corrective action is
not excision, it is putting a verification gate on migrations that change
semantic invariants.

---

## Provenance — where the ten sites came from

Each defective line was dated with `git log -S` against the introducing commit.

| Site | Introduced by |
|---|---|
| `AgentBackend::get_provider` | **S374** — *Tokio deep debt evolution* |
| `auth_backend_evolved::get_provider` | **S374** — *Tokio deep debt evolution* |
| `storage_backend_evolved::get_provider` | **S374** — *Tokio deep debt evolution* |
| `RuntimeOrchestrator::execute` | S172 — *deep debt evolution plan* |
| `execute_with_os_layer` | *Major technical debt elimination* |
| `evaluate_migration_targets` | *deep-debt third wave — 10 large files split* |

Not one traces to an early primal commit. Every label in that right-hand column
is a cleanup.

## Mechanism — why a correct migration produced incorrect code

S374's own commit message states it plainly:

> `RwLock migration (34+ files: tokio::sync → std::sync). Mutex migration (2 biomeos backends).`

The goal was sound: make `tokio` an optional dependency so the crate compiles
for `wasm32-unknown-unknown` (26/48 crates, up from 13). The execution was a
type substitution across 115 files.

The substitution is not semantics-preserving:

- `tokio::sync::RwLockReadGuard` **is `Send`**, and is *designed* to be held
  across an `.await`.
- `std::sync::RwLockReadGuard` **is not `Send`**. Holding one across an
  `.await` makes the enclosing future `!Send` — it cannot be `tokio::spawn`ed —
  and on a single-threaded executor it can deadlock.

So the pre-migration code was correct, and the same code became incorrect
*without being edited in any way that looks wrong at the diff level*. A reviewer
reading the S374 diff sees `tokio::sync::RwLock` → `std::sync::RwLock` and has
no local signal that an await three lines below now matters.

**This is the general shape worth naming: a mechanical migration that inverts an
invariant the type system was previously carrying for you.** The same migration
also desynchronised the *tests* from the source — the `std`/`tokio` `RwLock`
mismatches fixed in S382 and S383 are the same commit's fallout, surfacing a
year later only because nothing built those test targets.

## Why it stayed invisible

Four independent guards were all disengaged:

1. **`clippy::await_holding_lock` was never enabled.** It would have flagged
   all ten on the day they landed.
2. **`significant_drop_tightening` was explicitly set to `allow`**, annotated
   `# False positives on lock guards`. The adjacent lint family was dismissed
   as noise, which is how the precise one never got considered.
3. **CI runs `cargo test --workspace --lib`.** `--lib` never builds a `tests/`
   directory, so the ~13,102 integration tests that would have tried to
   `tokio::spawn` these futures were never compiled.
4. **Three sites were copy-paste siblings.** S382 fixed
   `AgentBackend::get_provider` and stopped; the identical function had been
   duplicated into the auth and storage backends. Fixing one instance of a
   duplicated defect left two live.

## What was done

`clippy::await_holding_lock` and `await_holding_invalid_type` are now `deny` at
the workspace root. That turned a hand-count of four into ten. All ten are
fixed.

Two fixes were structural rather than local. `CloudProviderRegistry` stored
`Box<P>`, so `get()` borrows from the registry and pins the guard for as long as
the provider is in use — no rearrangement of the await escapes that. It now
stores `Arc<P>` and exposes `handle()`. `os_layer`'s `compatibility_layers` map
changed the same way. One site (`get_statistics`) held a **std** guard across a
**tokio** `.read().await`: two lock families interleaved in one function.

**The lint was verified non-inert before being trusted.** The pre-fix shape was
re-injected into `RuntimeOrchestrator::execute` and clippy confirmed to reject
it. A lint that has never fired is indistinguishable from one that cannot fire.
That check also caught a measurement error of our own: `-p toadstool-core` is
`crates/toadstool-core`, a *different package* from `crates/core/toadstool`
(`-p toadstool`), so an earlier verification run had tested the wrong crate and
reported a green result for code it never compiled.

## Blast radius, measured

| Question | Answer |
|---|---|
| Files touched by the S374 migration | 115 (+812 / −517) |
| Files using `std` locks in `toadStool` today | 149 |
| `await_holding_lock` hits after the fix | 0 (workspace, `--all-targets`) |
| `coralReef` hits | **0** — lint run explicitly, 3 files use std locks |
| `barraCuda` hits | **0** — lint run explicitly, 14 files use std locks |

The defect is **isolated to `toadStool`** and attributable to S374. The siblings
did not undergo the migration and are clean. Neither, however, has the lint
configured, so their cleanliness is currently unguarded rather than enforced.

## Verification

- `cargo clippy --workspace --all-targets` — 0 errors, 0 lock-across-await hits
- `cargo test --workspace --no-run` — exits 0
- 2,121 lib tests pass across the four touched crates
- 30 `workload_migration` integration tests pass
- `cargo fmt --all --check` clean
- Both K80 dies responding after the work (`0x10de` at `4b:00.0`, `4c:00.0`)

---

## Gaps for upstream review

1. **Adopt the lint mesh-wide.** `coralReef` and `barraCuda` measure clean today
   but have no gate holding them there. Two lines in each workspace `Cargo.toml`.
2. **Migrations that change a type's `Send`/`Sync` character need a gate, not a
   review.** The S374 diff was individually unobjectionable at every hunk. A
   lint catches this class; human review of a 115-file type substitution does
   not. Recommend: any commit substituting a synchronisation primitive must land
   with the corresponding lint enabled in the same commit.
3. **`--lib`-only CI is the upstream-wide question.** It is what let this sit
   from S374 to S383. Worth checking whether sibling primals' pipelines have the
   same shape. Tracked in `SOVEREIGN_GROUND_TRUTH.md`.
4. **Duplicated functions need a duplication check.** Three `get_provider`
   implementations were byte-similar. If they had been one generic helper, S382
   would have fixed all three.
5. **"False positive" annotations deserve an expiry.** `significant_drop_tightening
   = "allow" # False positives on lock guards` was, in hindsight, the project
   telling itself that lock-guard lints are noise — immediately before ten real
   lock-guard defects. Suggest such allows carry a date and a re-review trigger.

## Method notes carried forward

- **When a fix lands, grep for the shape of the bug, not just the symptom.**
  One fixed instance of a copy-pasted defect leaves the copies live.
- **Verify a new gate rejects the thing it was built to reject**, before
  reporting it green.
- **A resolver overflow can mask a real error.** The `wgpu` `E0275` in
  `workload_simple_concurrent_tests` looked like the blocker; raising
  `recursion_limit` revealed it had been hiding a genuine `!Send` bug.
- **Two packages that differ only in path arrangement are a measurement trap.**
  `toadstool` vs `toadstool-core` cost one false green.
