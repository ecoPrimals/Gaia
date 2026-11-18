# biomeGate Measurement Truth AAR — Aug 16, 2026 (PM)

**Date:** Aug 16, 2026 11:00–12:00 UTC-4 | **Wave:** 157k | **Team:** biomeGate hotSpring sub-team
**Gate:** biomeGate (Threadripper 3970X, 128GB, RTX 5060 + Titan V + 2× K80)
**Status:** Titan V Tier 1 CONFIRMED and reproducible. Four measurement bugs fixed. K80 blocked by a missing nouveau device entry.

Companion to `BIOMEGATE_DRM_HOTADD_ROOT_CAUSE_AAR_AUG16_2026.md`, which covers
the session kills. This one covers what we found once the rotation could
actually run to completion.

---

## Summary

With the DRM hot-add hazard closed, Exp R6 completed end to end for the first
time. It immediately reported **"Tier 0: Cold boot"** — which was false. The
GPU was in D3hot, and every BAR0 register read `0xFFFF_FFFF`.

Waking the device first changed the answer completely. The Titan V comes out
of a nouveau warm handoff at **Tier 1 warm infrastructure**: 23 engines
enabled, PRAMIN accessible, reproducible across three consecutive runs.

The pipeline had been measuring a sleeping GPU and reporting the power state
as a hardware verdict.

A first corrected run then over-corrected to **Tier 2 "full shader dispatch"**
while FECS was PRI-faulted. Both errors are the same underlying defect, now
fixed at the type level rather than at the call site.

---

## The Measurement Bugs

### 1. D3hot reads reported as cold

vfio-pci permits runtime suspend, so the GPU drops to D3hot shortly after
bind — precisely when the pipeline measures whether the handoff preserved
state. A D3hot device does not fail BAR0 reads. The bus returns all-ones and
the read *succeeds*.

`0xFFFF_FFFF` has a popcount of 32, which cleared the `< 8` cold gate, so the
classifier proceeded to read every other register (all all-ones) and reasoned
its way to a verdict from nothing:

```
pmc_enable 0xFFFFFFFF  popcount 32   tier "cold"
```

Popcount 32 and "cold" cannot both be true. The pairing was visible in the
output and went unremarked.

**Fix:** `vfio::power::wake_to_d0` before probing, plus `bus_readable` on the
evidence. An unreadable bus now fails the step loudly with the power state
attached instead of presenting a fallback verdict as a measurement.

### 2. Tier 2 granted without FECS

`fecs_pc` was read, stored, and reported — but never consulted in the tier
decision:

```rust
let tier = if gpc_alive && ce_alive && tpc_alive { WarmCompute }
```

GPC and CE both passed only via their fallback scans while their primary
registers were faulted. Three weak signals outvoted the engine that actually
performs dispatch.

**Fix:** Tier 2 requires `fecs_alive`. `TierEvidence` gains the field so the
blocker is named rather than inferred from a lower tier.

### 3. A sleeping GPU declared warm in the RPC handler

```rust
let pmc = bar.read_u32(0x200).unwrap_or(0);
popcount >= 10          // 0xFFFFFFFF -> 32 -> "warm"
```

This suppressed SBR. Worse, on the catalyst path it gated a PRI check whose
`pri_intr != 0` test also saw all-ones — so an unreadable device was scored
degraded and answered with a **spurious bus reset**.

### 4. `warm_probe` thresholds and the catalyst PC range

`live_warm` required `>= 16` engines; all-ones scored 32. `is_catalyst_pc`
tested `fecs_pc >= 0x1000_0000`, which `0xFFFF_FFFF` also satisfies — so an
unreadable FECS looked like a catalyst-warmed one.

---

## The Abstraction

Four instances, one shape: **a sentinel value consumed as a number**. The
third occurrence of a bug is not a bug, it is a design defect.

`nv::pri::is_pri_fault` has encoded these patterns for a long time and is
correct. But it is a free function that callers must remember to invoke, and
a `u32` invites arithmetic — `count_ones()` on a sentinel is silently
meaningless rather than a type error.

`nv::register_read::RegisterRead` removes the invitation. There is no way to
obtain a number without acknowledging the read may not have produced one:

```rust
pub enum RegisterRead { Valid(u32), BusFailure, PriFault(u32), Unread }
```

It also keeps apart two things `is_pri_fault` conflates:

- `0xBADF_5040` on FECS — the device is alive, that engine is gated, other
  registers remain meaningful.
- `0xFFFF_FFFF` on PMC — **nothing** is answering. No register is meaningful,
  and further probing only manufactures more garbage.

Conflating them is how a sleeping GPU was classified as cold rather than as
unmeasured.

Applied to ten sites, found by sweeping for the pattern rather than waiting
for the next incident: `warm_probe`, the `warm_handoff` RPC, `init_volta`,
`open_vfio_fecs_probe`, `driver_probe`, `boot_state`, `preflight`,
`settle_capture`, and both tier classifiers.

---

## Titan V: The Real Result

Three consecutive runs, identical:

```
tier          warm_infrastructure        (Tier 1)
pmc_enable    0x5FECDFF1  (23 engines)
pramin        accessible
tpc_alive     true
fecs_alive    FALSE   fecs_pc = 0xBADF5040   <- blocker
bus_readable  true
```

Handoff steps: preflight → module_prep (6/7 patches) → unbind → seeder_bind →
15s settle → prepare_warm_swap → warm_swap (`warm_preserved=true`) →
tier_classify → module_cleanup. Clean teardown, no oops, no zombie module,
session intact.

**Tier 1 warm infrastructure is achieved and reproducible via nouveau warm
handoff.** Warm state also *persists* on vfio-pci: the GPU still read
`0x5FECDFF1` when re-probed minutes later.

Tier 2 is blocked by the FECS PRI fault, consistent with the known Volta
GPCCS HS fuse lock. Nothing observed today contradicts that wall.

The `gf100_gr_fini` NOP removal is validated: nouveau now unloads cleanly
where it previously page-faulted in `nve0_bo_move_copy`.

---

## K80: Blocked by a Missing Device Entry

The K80 track is a co-equal target, and Kepler's unsigned falcons make it the
natural contrast to Volta's fuse lock. It does not currently get that far.

```
nouveau 0000:4b:00.0: unknown chipset (0f22d0a1)
```

The handoff halted at `seeder_bind` with `driver=none expected=nouveau`, and
rolled back cleanly.

nouveau **matched** the device via its vendor wildcard and read `PMC_BOOT_0`
successfully — so the hardware is alive and answering — then rejected it:

| GPU | boot0 | chipset |
|-----|-------|---------|
| Titan V | `0x140000a1` | `0x140` (GV100) |
| K80 | `0x0f22d0a1` | `0x0f2` (GK210) |

Chipsets present in the shipped module: `gk104`, `gk110`, `gk110b`, `gk208`,
`gk20a`. **`gk210` appears zero times.** GK210 is a Tesla-only part and
nouveau never gained support for it.

This is a software gap, not a hardware wall — the more encouraging of the two
failure modes.

**Path forward:** GK110B is chipset `0xf1` and is fully supported; GK210
(`0xf2`) is a GK110-family variant with a larger register file and cache per
SM. Mapping `0xf2` onto the `gk110b` device implementation is plausible, and
fits the existing injectible-recipe model — the difference is that the patch
targets the chipset dispatch table rather than NOPing teardown functions.

Unverified. The register-file differences may matter for GR init even if the
device probes.

Both K80s are genuinely cold (`0xC0002020`, 4 engines) — a plausible reading,
not a masked one, confirmed against the wake audit.

---

## Also Landed

The `sovereign.*` methods had no CLI and could only be reached by
hand-written socket clients. Every experiment shipped a throwaway harness,
and those harnesses were the least reliable part of the stack: today's
framed requests without the trailing newline the server's `read_line`
requires, and deadlocked — 90 seconds of "GPU hang" that was two processes
waiting on each other.

`toadstool sovereign handoff|status|strategies` now exists. It speaks RPC to
the daemon rather than calling the library in-process, deliberately: the
daemon holds the PCIe bridge keepalive that pins upstream hierarchies during
rotation, which matters most for the K80s behind their PLX switches. The K80
run above was driven entirely through it.

---

## Method Note

Every bug here produced a plausible answer rather than an error. "Tier 0
cold" is what you expect from a failed handoff; "Tier 2 warm compute" is what
you hope for from a good one. Neither prompted a second look, and the one
internally contradictory signal — popcount 32 alongside a cold verdict — sat
in the output unread.

The pattern worth carrying forward: **when a measurement agrees with your
expectation, that is not evidence it was taken.** The contradictions were
visible both times. What was missing was a reason to look.

---

## Next

| # | Item | Status |
|---|------|--------|
| 1 | GK210 chipset entry — map `0xf2` onto `gk110b` | PROPOSED |
| 2 | Re-examine prior "cold" verdicts taken without a wake | OPEN |
| 3 | FECS liveness on Volta — the standing Tier 2 wall | OPEN |
| 4 | Retire the remaining Python harnesses into the CLI | PARTIAL |
| 5 | Signal provenance via `SA_SIGINFO`; handoff critical section | PENDING |

Both cards remain targets. QCD is a target; sovereign deployment is the goal.
