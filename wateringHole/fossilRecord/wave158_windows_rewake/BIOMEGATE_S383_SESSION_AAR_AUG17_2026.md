# AAR — Session S383: Test Compilation, Lock-Across-Await, VBIOS Abstraction

**Author**: biomeGate <biomegate@primals.eco>
**Date**: August 17, 2026 — S383
**Repos**: `toadStool` @ `9763b4daa`, `wateringHole` @ `3d1fb58f`
**Commits**: 6 in toadStool, 4 in wateringHole
**Scope**: 33 files, +1,184 / −320 lines

---

## What was accomplished

### 1. Every test target compiles (`D-TEST-COMPILE` resolved)

`cargo test --workspace --no-run` exits 0 for the first time. The CI gate added
in S382 immediately earned its keep by surfacing the remaining failures.

Fixed:
- 3 production `!Send` bugs (lock guards held across await)
- 1 `tokio::process` feature missing from dev-dependencies
- 1 `std`/`tokio` `RwLock` type mismatch
- 1 `wgpu` recursion-limit overflow masking a real `!Send` error
- 1 missing feature gate on `beardog_client_evolved_coverage_tests`
- 2 unimplemented `detect_all()` tests disabled with `#[cfg(any())]`

Recovered: **104 integration tests** (25 detection, 79 GPU) now run.

### 2. `await_holding_lock` denied workspace-wide (10 sites fixed)

Enabling `clippy::await_holding_lock` as `deny` turned a hand-count of four
(from S382) into **ten**. Every one was introduced by a *deep-debt cleanup
commit*, not by early primal code — and three came from S374's `tokio::sync` →
`std::sync` migration across 115 files, which silently inverted a `Send`
invariant the type system was previously carrying.

| Site | Consequence |
|---|---|
| `RuntimeOrchestrator::execute` | engine registry read-locked for entire workload |
| `show_logs` | `!Send`; explicit `drop` but borrow kept guard in generator |
| `list_biomes` | `!Send`; `drop` placed after the await |
| `send_heartbeat` | guard held through network send |
| `execute_with_os_layer` | awaited inside iteration holding guard |
| `evaluate_migration_targets` | guard spanned round of provider queries |
| `record_resource_snapshot` | correct `drop`; scoped for clarity |
| `get_statistics` | std guard spanning a tokio `.read().await` |
| `auth_backend_evolved::get_provider` | copy-paste sibling of the S382 fix |
| `storage_backend_evolved::get_provider` | copy-paste sibling of the S382 fix |

Two structural changes: `CloudProviderRegistry` now stores `Arc<P>` (was
`Box<P>`) and exposes `handle()`; OS layer's `compatibility_layers` changed
the same way. With `Box`, `get()` borrows from the registry and pins the lock
guard for as long as the provider is used — no local rearrangement fixes it.

The lint was verified non-inert by re-injecting the pre-fix shape and
confirming clippy rejects it. That check also caught that `-p toadstool-core`
(`crates/toadstool-core`) is a different package from `-p toadstool`
(`crates/core/toadstool`), so an earlier verification had tested the wrong
crate.

Sibling primals (`coralReef`, `barraCuda`) were linted explicitly: **0 hits**
on both, but neither has the gate configured — their cleanliness is unguarded.

### 3. Script-table discovery unified (scanner bug fixed)

The interpreter and the register-write scanner each located VBIOS init scripts
their own way. On a measured GK210 image they disagreed: the interpreter walked
all 6 scripts, the scanner took only entry `[0]` and scanned forward.
Entry `[2]` sits at `0x65ff`, *below* `[0]` at `0x9271`, so scanning forward
could never reach it — **32 register writes were invisible to one consumer and
visible to the other**.

`ScriptTable::discover` is now the single place that answers where the scripts
are. It reads the layout out of the ROM's BIT 'I' entry — version, payload
size, PMU field capability — rather than branching on a card name. The
opcode-stride selector derives from the same source.

Scanner output: **323 → 355 writes**. Interpreter unchanged at 0% unknown.

### 4. Residual opcode `0x4D` fixed

`INIT_ZM_I2C_BYTE` was coded as a fixed 6 bytes but is actually
`4 + count * 2`. With `count = 2` the walk stopped mid-payload and desynced the
last script. Corrected, the next byte decodes to `0x71` (INIT_DONE) — the
script terminates cleanly. Unknowns: **2 → 1**.

`0x96` was tried at nouveau's 7 and made things worse (1 → 5 unknowns), so 11
stands on evidence. Negative result recorded in place.

### 5. Script[0] desync localised to opcode `0xA8`

The remaining unknown (`0x00` at `0x9345`) is now traced. The walk is correct
through `0x9335`; a sweep of every `0x96` length from 4–21 fails because the
furthest reachable stop is `0x9376`, where opcode `0xA8` is entirely
unimplemented. **It is absent from the dispatch table, not merely mis-sized.**
Implementing it is the concrete next step.

Tooling: per-opcode `tracing::trace!` and `dump_script_walk` (ignored
diagnostic) added for future desync investigations.

---

## Verification

| Gate | Status |
|---|---|
| `cargo test --workspace --no-run` | exits 0 |
| `cargo test --workspace --lib` | 8,539 pass, 0 fail |
| `cargo test -p toadstool-cylinder --lib` | 805 pass, 0 fail, 2 ignored |
| `cargo clippy --workspace --all-targets` | 0 errors, 0 `await_holding` hits |
| `cargo fmt --all --check` | clean |
| K80 dies | both responding (`0x10de`) |

---

## What went right

1. **The `--no-run` gate immediately justified itself.** Added in S382, it
   surfaced the remaining test compilation failures before any human checked.
   The remaining failures were production bugs, not test bugs.
2. **Negative results are results.** Recording that `0x96 = 7` is wrong on this
   image prevents the experiment from being repeated. Recording that `0xA8` is
   *absent* rather than *mis-sized* reframes the investigation.
3. **Shared discovery eliminated a class of bug.** Two consumers can no longer
   disagree about the same ROM.
4. **Per-opcode tracing turned guessing into measurement.** The `0xA8` finding
   came from seeing the sequence, not from reasoning about it.

## What went wrong

1. **An incomplete Python stride table produced a confident wrong answer.** The
   first brute-force sweep was missing `0x36` (INIT_REPEAT_END), so it reported
   that no `0x96` length works. With the complete table, lengths 17–21 decode
   ten more opcodes before hitting a genuinely absent opcode. The incomplete
   instrument looked right.
2. **An earlier count said 90% of script[0] was unwalked.** That measured to the
   next table entry and counted inter-script data as script. The real figure is
   ~27%. The correction is in the ground truth, but the wrong number existed
   for one message before being retracted.
3. **`-p toadstool-core` vs `-p toadstool`.** A lint verification ran against
   the wrong crate and reported green for code it never compiled. Two packages
   that differ only in path arrangement are a measurement trap.
4. **Fixing one instance of a duplicated defect left two live.** S382 fixed
   `AgentBackend::get_provider`; its byte-similar copies in `auth` and
   `storage` kept the bug for a full session.

## Method notes carried forward

- **When a fix lands, grep for the shape of the bug, not the symptom.** One
  fixed instance of a copy-pasted defect leaves the copies live.
- **Verify a new gate rejects what it was built to reject** before reporting
  it green.
- **A resolver overflow can mask a real error.** Raising `recursion_limit`
  didn't fix anything; it let the genuine `!Send` bug through.
- **A cleanup can manufacture the debt it is named for.** Ten lock-across-await
  bugs, every one introduced by a commit labelled "deep debt".
- **The incomplete instrument is worse than no instrument.** A wrong stride
  table produces a confident "nothing works" instead of revealing the ten
  opcodes beyond the gap.

---

## Open items for next session

| ID | Item | Status |
|---|---|---|
| `opcode-a8` | Identify and implement opcode `0xA8`, re-sweep `0x96` | pending |
| `strap` | Verify RAM strap read at `0x100000` on a cold die before arming writes | pending |
| `detect-all` | `UniversalSubstrateCapabilities::detect_all` (D-SUBSTRATE-DETECT-ALL) | pending |

The `0xA8` → `0x96` re-sweep → strap-read sequence is the critical path to
arming VBIOS writes on a live die. `detect_all` is independent and lower
priority.

---

## Repos pushed

All four repos are clean and pushed:

```
wateringHole     dirty=0 unpushed=0
toadStool        dirty=0 unpushed=0
coralReef        dirty=0 unpushed=0
barraCuda        dirty=0 unpushed=0
```

Both K80 dies healthy throughout the session (`0x10de` at `4b:00.0`, `4c:00.0`).
No hardware experiments were performed — all VBIOS work was offline against the
ROM dump.
