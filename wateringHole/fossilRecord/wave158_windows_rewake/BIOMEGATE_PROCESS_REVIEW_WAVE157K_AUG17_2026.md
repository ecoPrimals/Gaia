# biomeGate Process Review — Wave 157k

**Date:** Aug 17, 2026 | **Scope:** Aug 13–17, six AARs, one gate
**Team:** biomeGate hotSpring sub-team
**Purpose:** Not a results summary. A review of **how we came to believe things**,
which of those beliefs survived contact with the next wave, and which did not.

Read alongside `SOVEREIGN_GROUND_TRUTH.md`, which holds the current claims. This
document holds the *method* — and its failure modes.

---

## Why this document exists

Six AARs in five days, four of which retract something from an earlier one. That
retraction rate is either a broken process or a working one, and the difference
matters enough to examine directly.

The claim of this review: **it is working, but its yield is falling in a
specific way that predicts the next failure.** Each wave has caught the previous
wave's error. No wave has yet caught its own.

---

## The lineage

Six waves, what each asserted, and what the next one did to it.

| # | Wave | Core assertion | Verdict from later waves |
|---|------|----------------|--------------------------|
| 1 | Dispatch restage (Aug 13) | Lockup vectors mitigated; PRI faults were false positives | **Held.** `0xBADF1020`-as-data named early and correctly |
| 2 | DRM hot-add root cause (Aug 16) | One cause behind three session kills | **Held.** Guards landed; host has not gone down since |
| 3 | Measurement truth (Aug 16) | Titan V Tier 1 confirmed; four measurement bugs | **Held**, and retroactively withdrew the earlier "Tier 2 via catalyst" |
| 4 | K80 sovereign (Aug 16) | `pgraph_reset` a milestone; `DEVINIT_STATUS` a Volta-only offset | **Both retracted same day.** Offset was correct; all-ones was a wedged die |
| 5 | K80 wedge hunt (Aug 16) | Four bugs; wedge is `FalconDiagnostic` writing `0x1854` | **Held.** Cold bring-up survives ×4; dies recovered on reboot |
| 6 | Vendor tool excision (Aug 17) | Detection 1→4 GPUs; "216 tests recovered" | **1→4 verified. Test claim wrong** — see below |

### What wave 6 validated from its predecessors

Three earlier beliefs were tested against new evidence this wave, and all three
survived — which is worth as much as the corrections.

**1. "A wedged die is recoverable by power cycle."** Asserted in waves 4–5 while
sitting on five dead dies, and load-bearing: it is the difference between an
expensive debugging session and destroyed hardware. The Aug 17 reboot recovered
**both** K80 dies to `Responding`. Confirmed.

**2. "Sentinel-as-data is *the* recurring failure mode."** Waves 3–5 named it and
counted six instances. Wave 6 tested it the hard way: I **committed it fresh**,
in the code written to clean up after it, filtering GPUs by a class code read
from live config space so that two wedged dies read `0xffffff` and were reported
as never installed. A pattern that reproduces in a new domain, in the hands of
someone who had just finished writing about it, is not a pattern. It is the
grain of the material.

**3. "Vendor tools are not sovereign."** A definitional claim from wave 3,
initially about drivers. Wave 6 found it had teeth in an unexamined place:
`nvidia-smi` reports only proprietary-driver-bound devices, so detection was
**blind to precisely the sovereign configuration** — unbound Titan V, both
`vfio-pci` K80 dies — and reported that blindness as a successful scan. The
definition predicted a real defect in a layer nobody had pointed it at.

### What earlier waves got wrong, and the shape of it

| Retracted claim | Wave | Why it was believed |
|-----------------|------|--------------------|
| "Tier 2 ACHIEVED via catalyst" | pre-13 | PRI-faulted registers read as live state |
| "`DEVINIT_STATUS` is a Volta-only offset" | 4 | One dead register on one dead device, generalised to an architecture |
| "`pgraph_reset` is a milestone" | 4 | A step completed, mistaken for a step that accomplished something |
| "GK210 nouveau dispatch patch needed" | 4 | Solved a real problem the sovereign path does not have |
| "Wedge is PMC_ENABLE sequencing" | 4 | Plausible mechanism, correct symptom, wrong cause |

Every one is the same error: **an instrument was read without asking whether it
could answer.** On dead silicon every register reads `0xffffff` or `0xbad0____`,
and every one of those is a *refusal*, not a value. Five of five retractions are
this.

---

## Now the same audit, applied to wave 6

The above is easy to write about other people's waves. The test is whether the
method catches its own output. Audited the morning after, against the tree:

### It did not.

Wave 6's headline included **"216 tests recovered across nine files."** Both
numbers are wrong.

| Claim | Reality |
|-------|---------|
| nine files | **21** |
| 216 recovered | **113** run; **510** compile-skip; **623** total |
| "recovered" | 82% of them do not execute |

The 510 sit behind `hardening`, `legacy-cloud`, and `legacy-security`. None is a
default feature. **Nothing in CI or `scripts/` enables any of them.** Those tests
moved from *failing loudly at build time* to *not existing quietly* — which is a
legitimate build fix and is not recovered coverage.

And the number was unsourced. I cannot reconstruct where 216 came from. It
reached `DEBT.md`, `CHANGELOG.md`, the AAR, and the status line inside an hour —
one unverified figure becoming four citations, which is the exact propagation
mechanism `SOVEREIGN_GROUND_TRUTH.md` exists to stop. The doc worked as designed
for hardware claims and was never pointed at process claims.

### Pulling that thread found the real finding

If gated tests never run, what does CI run?

```yaml
- run: cargo test --workspace --lib
```

`--lib` builds and runs unit tests compiled into libraries. It does not touch a
`tests/` directory.

| Target | Test fns | Runs in CI |
|--------|----------|-----------|
| `--lib` unit tests | 8,521 | **yes** |
| `tests/` integration (731 files) | ~13,102 | **no** |

The figure this gate quotes as its quality signal is accurate and is **39% of
the repo's test functions.** The other 61% have no gate asserting they even
compile — which is precisely how 21 files rotted, some referencing APIs that no
longer exist anywhere in the tree.

**The clue was in my hand and I did not read it.** Every rotted file was in
`tests/` — the exact directory `--lib` skips. I fixed twenty-one symptoms
without asking why they shared an address.

One thing this review could **not** settle: `clippy --workspace --all-targets`
*does* build test targets, so CI should have caught the rot. Either CI is not
executing — the workflows are GitHub-format while `origin` is a Forgejo instance
— or it has been red and unattended. Not determinable from the working tree.
Flagged rather than guessed, which is the one part of the method that worked
here.

---

## What the method actually is

Extracted from what produced results rather than from what we intended:

**1. Ask the question the instrument cannot dodge.** The highest-yield move of
the whole wave was `cargo test --workspace --no-run` — asking *do the tests
compile*, separately from *do they pass*. `cargo test` reports a build failure
per crate and moves on; nothing aggregates it. The hardware analogue is asking
`DEVINIT_STATUS` whether it is readable before asking what it says.

**2. Run it and compare against a second source.** All four vendor-tool defects
were found by printing what the code reported next to what `/sys` said. **None**
would have been found by reading the code: it looks reasonable and its tests
passed, because the tests fed it recorded `nvidia-smi` output instead of a
machine.

**3. Pair sources that answer different questions.** The wedged-GPU fix was not
better filtering. Cached sysfs identity answers *who is this* and survives the
device going silent; live config space answers *is it answering now*. Together:
"Tesla K80 at `0000:4b:00.0`, not responding." Either alone gives half an
answer; the class filter over live config space gave none.

**4. Get the hardware out of the loop.** The `ScriptBus` trait let the VBIOS
interpreter run offline and immediately caught a shift-overflow that would have
cost a die. Iteration went from one-per-reboot to one-per-second. This is the
single largest multiplier found so far and it is under-applied.

**5. Write the negative results down.** "0 `unimplemented!` in production", "85
of 85 unsafe blocks documented", "0 files >800L" are results. They stop the next
audit re-deriving alarm from the same grep — the raw counts that triggered this
one ("428 mock hits", "474 unsafe") were almost entirely comments and correctly
gated test code.

### Where the method has a hole

It has no step that turns the instrument on itself. Rules 1–3 are applied to
code, hardware, and other waves' claims. Nothing applies them to **the numbers
in the write-up**, which is why 216 survived into four documents and 8,521 was
quoted without asking what it excluded.

The rule that would have caught both already exists, in this gate's own words:
*a measurement that agrees with expectation is not evidence it was taken.* It
was written about hardware. It is not currently applied to prose.

---

## Are we getting closer?

Yes, and the evidence is specific rather than general — but the ledger has a
debit side.

**Blockers are moving down a real dependency chain**, not sideways:

```
"K80 is dead"
  → wedges during init            (5 dies spent locating this)
  → wedge cause found and fixed   (survives cold bring-up ×4)
  → VBIOS unreadable
  → VBIOS read off PROM           (0xeb7baa55, first time)
  → VBIOS misparsed — 76% unknown opcodes   ← current
```

Each is strictly downstream of the last. Nothing has returned to a previous
rung.

**Cost per rung is falling.** Wave 4 cost five dies and a host lockup. Wave 5
cost zero dies and no lockup, because the guards from wave 4 held. Wave 6 cost
nothing and ran largely offline. Falling cost per advance is the honest signal
that the process compounds.

**Failure modes are being permanently retired**, not just fixed: `reset_guard`
makes the Exp-229 host deadlock unreachable; `RegisterRead` makes sentinel-as-
data a type error at the point of use; `writes_armed` makes executing a desynced
VBIOS parse impossible; the `Send` assertion makes a re-introduced lock-across-
await a compile failure. Each converts a class of mistake into something the
compiler or a guard refuses.

**Against that**: this wave's discoveries were increasingly about *our own
instruments* rather than about the GPU. A floating toolchain pin, a CI job
covering 39% of tests, a test count nobody had checked. None of these bring the
K80 closer to executing a shader. They are the accumulated cost of having
measured carelessly for a while, and paying it down is necessary but is not
progress on the blocker.

The next wave should be judged on whether it moves the VBIOS parse, not on how
much more instrument debt it finds. Finding instrument debt is now easy, which
is exactly why it is a poor proxy for advancement.

---

## Carried forward

**Process changes, ordered by expected yield:**

1. **Audit the write-up as a measurement.** Every number in an AAR gets a
   command that regenerates it, run before the doc is committed. Both of wave
   6's bad numbers would have died in seconds.
2. **Settle whether CI runs.** Unresolved and load-bearing: every quality claim
   in the root docs is downstream of it. Needs checking on golgiBody.
3. **Gate test compilation** — `cargo test --workspace --no-run`. This class of
   rot is silent by construction.
4. **Pin the toolchain explicitly.** A floating `channel = "stable"` makes every
   compiler release an unannounced, unattributed change; it silently falsified a
   "gates green" claim that was true when written.
5. **Extend `ScriptBus`-style offline harnesses** to the remaining hardware
   paths. Best multiplier found; least exploited.

**Open question worth stating plainly.** This gate has now produced six AARs and
zero shaders executed on the sovereign path. Waves 4–6 each ended by advancing a
blocker or removing a class of error, which is real. But "no shader has ever
executed on the sovereign path on any NVIDIA GPU" has been the one-line answer
in `SOVEREIGN_GROUND_TRUTH.md` for the entire wave, and it is still true this
morning.
