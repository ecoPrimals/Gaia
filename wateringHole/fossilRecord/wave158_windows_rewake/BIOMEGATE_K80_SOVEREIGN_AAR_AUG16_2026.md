# biomeGate K80 Sovereign Track AAR — Aug 16, 2026 (PM)

**Date:** Aug 16, 2026 12:30–13:15 UTC-4 | **Wave:** 157k | **Team:** biomeGate hotSpring sub-team
**Gate:** biomeGate (Threadripper 3970X, 128GB, RTX 5060 + Titan V + 2× K80)
**Status:** K80 sovereign path opened and advanced three stages. One hard lockup, self-inflicted, now guarded in code.

Third AAR of the day. Follows `BIOMEGATE_DRM_HOTADD_ROOT_CAUSE_AAR_AUG16_2026.md`
(session kills) and `BIOMEGATE_MEASUREMENT_TRUTH_AAR_AUG16_2026.md` (measurement
bugs). This one covers the K80 track and a lockup I caused.

> **Correction, same day (evening).** The `pgraph_reset` line celebrated below
> as *"PGRAPH ungated, no vendor code"* was a bug, not a milestone. It clocked
> PGRAPH before devinit on a generation where devinit *is* the power sequencer,
> against a mask that deliberately excluded GR. Stages recorded after it were
> measured on a dying die.
>
> The wedge blamed here on "PMC_ENABLE sequencing" was also wrong. The real
> cause was a PROM read writing `0x1854` through a PRI-faulted PBUS ring.
>
> See `BIOMEGATE_K80_WEDGE_AAR_AUG16_2026.md`. Read this document for the
> sentinel and lockup findings, which stand; treat its K80 stage results as
> superseded.

---

## Summary

The K80 was previously blocked at `seeder_bind`: nouveau has no GK210 entry, so
it refused the card. The planned fix was to patch nouveau's chipset dispatch
table.

That turned out to be the wrong problem to solve. **The K80 does not need
nouveau at all.** Kepler has unsigned falcons and no ACR/WPR chain, and
`sovereign.init` already encodes a Kepler path — `BootStrategy::NoAcr`, direct
PIO falcon upload. Going direct got further in one attempt than the nouveau
route had in total:

```
[ok     ] identity_probe    raw=0x0f22d0a1 chip=0x0f2      <- toadStool knows GK210
[ok     ] pmc_enable        before=0xc0002020
[ok     ] pgraph_reset      pmc=0xc0002020 -> 0xc0003020   <- PGRAPH ungated, no vendor code
[ok     ] boot_state_probe  cold (pmc=0xc0003020)
[failed ] memory_training   <- the live edge
```

toadStool's own identity probe recognises GK210 where nouveau does not. The
"unknown chipset" wall was nouveau's, not the hardware's, and it is no longer
on the critical path.

**The GK210 dispatch-table patch is withdrawn.** It would have bought a seeder
we do not need.

---

## What Was Actually Blocking the K80

### 1. Cold memory training was skipped unconditionally

`sovereign.init` hardcoded `opts.skip_cold_memory_training = true`, overriding
the caller. The reasoning was sound for the card it was written against: HBM2 is
trained by on-die sequencers during power-on, and cannot be driven from software
afterwards. That is the standing Tier 3 wall on GV100.

It was applied to every GPU. A GDDR5 K80 was told

```
cold GPU: HBM2 training requires power-on reset
```

and halted — a card with no HBM anywhere on it, refused on HBM's behalf.

The distinction matters because GDDR is trained by the VBIOS devinit script,
which is ordinary register programming that can be replayed. On Kepler, devinit
*is* the power sequencer.

Every generation profile already carried a `memory_type`. Nothing needed to be
discovered, only consulted:

```rust
let mem = profile_for_sm(sm).memory_type;
opts.skip_cold_memory_training = mem.requires_power_on_reset_to_train();
```

The skip message now names the memory type it is actually talking about.

**A GDDR5 cold-training path already existed in the tree**, complete with its
own error variants (`Gddr5PraminDeadAfterDevinit`,
`Gddr5PraminDeadDevinitSkipped`) and a comment describing the exact
`0xbad0fb0*` PRAMIN signature a cold K80 returns. It had simply never been
reachable. The hardcoded skip stood in front of it.

### 2. The fifth sentinel-as-data bug, and it was load-bearing

With training reachable, it failed:

```
DEVINIT not needed per register but PRAMIN is dead
```

Which is a contradiction stated plainly, and the cause was familiar:

```rust
let r = |reg| bar0.read_u32(reg).unwrap_or(0xDEAD_DEAD);
let devinit_reg = r(DEVINIT_STATUS);
let needs_post = (devinit_reg & 2) == 0;
```

Bit 1 means POST complete. `0xFFFFFFFF` has bit 1 set. So a device that is not
answering reports **"devinit already complete"**, and the one operation that
would have brought it up is declined on the strength of a register that was
never read.

Measured directly:

| GPU | boot0 | DEVINIT_STATUS | verdict |
|-----|-------|----------------|---------|
| Titan V | `0x140000a1` | `0x00000002` | real — POST genuinely done |
| K80 | `0xffffffff` | `0xffffffff` | sentinel — read as POST done |

This is the fifth instance of the pattern `RegisterRead` was introduced for this
morning, and the first where the wrong answer was *blocking* rather than merely
cosmetic. The type existed; this call site predated its application and had not
been swept.

`DevinitStatus` now carries `readable`, an unreadable register can never report
POST-complete, and `execute_devinit_with_diagnostics` returns
`StatusUnreadable` instead of a quiet `Ok(false)`.

The payoff was immediate. The honest error localised the real problem on the
next run:

```
devinit status unreadable (reg=0xffffffff) — device is not answering
```

while `identity_probe` had just read `boot0` fine and `pmc_enable` fine. Not a
dead device — a **specific register that does not decode**, on a device
answering everything else. That is the next question on this track, and it was
invisible while the code was quietly declining to act.

### 3. `sovereign.init` did not wake the device

vfio-pci allows runtime suspend, so an idle GPU drops to D3hot — where the
device factory cannot probe it at all:

```
device 0000:4b:00.0 not available — factory returned None
```

Same root cause as this morning's "Tier 0 cold" misreading, in a different
handler. `power::wake_to_d0` now runs before anything touches BAR0.

---

## The Lockup

**I locked the gate. It needed a hard power cut.**

After a run, both K80 dies stopped answering — BAR0 all-ones, unrecoverable by
power control, with `power_state=D0`, `enable=1` and memory decode on. To
recover them I wrote:

```
echo 1 > /sys/bus/pci/devices/0000:4b:00.0/reset
```

The host froze instantly.

A sysfs reset writes config space. Config access to a device that is not
answering enters the kernel's CRS retry loop, and that loop holds the global
`pci_lock`. Every other PCI operation on the box blocks behind it, the display
GPU's included, so the machine does not report an error — it stops. Both K80
dies sit behind a PLX PEX 8747, so the reset was additionally arbitrated by a
bridge only reachable through the same config space.

The irony is exact: **the reset was an attempt to recover a device whose
unresponsiveness was the very thing that made the reset unsafe.**

This hazard was already known here. It is Exp 229, it is documented in the
`sovereign` CLI's own module docs as the reason that command talks to the daemon
rather than calling the library in-process, and I wrote that paragraph earlier
today. Knowing it was not enough, because nothing in the system was positioned
to object at the moment it mattered.

So it is now code rather than recollection. `vfio::reset_guard` probes BAR0
before permitting a reset and refuses on an unresponsive device, naming both the
mechanism and the remedy:

```
device is not answering (boot0 = bus-failure); a reset would enter CRS retry
holding pci_lock and can hang the host. Recover by reboot instead
```

It also refuses to retry after a reset that leaves the device unresponsive — the
second attempt is the dangerous one.

**The rule: never reset a device that is not answering.** A responsive device
can be reset. An unresponsive one is recovered by reboot, which reinitialises
the bridge hierarchy along with the endpoint. Slower, and the only option that
does not risk the host.

The reboot recovered both dies cleanly (`boot0=0x0f22d0a1`, `pmc=0xc0002020`).

---

## Recovery Was Also Broken

The restore script failed every primal immediately after the reset, at the one
moment it matters most:

```
nohup: failed to run command 'toadstool': No such file or directory
```

It is designed to run as the operator and escalate per-command. Run under
`sudo`, two things break silently: the primals live in the operator's
`~/.local/bin`, absent from root's PATH, and `RUNTIME_DIR` resolves to
`/run/user/0`. Both surface only as `FAILED`.

Then the root-owned `/tmp/*.log` files from that attempt made the *next*,
correct run fail too — permission denied, still reported as `FAILED`.

Fixed: the script re-execs as `SUDO_USER` rather than aborting, ensures
`~/.local/bin` is on PATH, logs to a per-user state directory that cannot be
poisoned by ownership, and prints the first lines of a failing primal's log
instead of only the word `FAILED`.

Full restore now verified: six primals up, FLR/SBR suppression active, four GPUs
Alive.

---

## Current K80 Position

| Stage | State |
|-------|-------|
| identity_probe | GK210 recognised, `chip=0x0f2` |
| pmc_enable | reads clean, `0xc0002020` |
| pgraph_reset | **PGRAPH ungated sovereignly**, `-> 0xc0003020` |
| boot_state_probe | cold, correctly |
| memory_training | live edge — devinit status register does not decode |

Three stages further than the nouveau route reached, with no vendor code
involved at any point.

Two open questions, in order:

1. ~~**`DEVINIT_STATUS` at `0x2240c` does not decode on GK210.**~~
   **RETRACTED, same day.** Measured against a live die, `0x2240c` decodes
   correctly on GK210 and reads `0x00000000` on both dies — bit 1 clear,
   `needs_post = true`, exactly right. The Titan V reads `0x00000002`. Stable
   across repeated reads on all three GPUs.

   The all-ones came from the **wedged die**, not a wrong offset. I read one
   dead register on a dead device and inferred a generation-specific offset bug
   from it, which is the same mistake this AAR is otherwise about: treating a
   sentinel as information. The register map needs no change.

   What this retraction leaves behind is a sharper problem — see item 2, which
   is now the only blocker on this track.

2. **The dies wedge after a run. This is the blocker.** Both went to all-ones
   following `pgraph_reset` + `pmc_rollback`, and did not recover from power
   control — `power_state=D0`, `enable=1`, memory decode on, and still nothing
   answering. Only a reboot brought them back.

   With item 1 retracted, this is the whole K80 problem. Every downstream
   symptom today, including the "unreadable devinit status" that sent me chasing
   a register map, was this wedge seen from a different angle.

   `GenerationProfile` already carries `power_safety: PowerSafetyProfile` and
   Kepler is set to `PRE_FIRMWARE`, so the concept exists; whether the
   `pgraph_reset` write path honours it is the open question. Next attempt goes
   with the reset guard in place and a reboot budgeted as recovery.

---

## Method Note

This morning's note was: *when a measurement agrees with your expectation, that
is not evidence it was taken.* Today's addition is narrower.

Both of the day's genuine blockers were **assumptions from one GPU applied to
all of them** — HBM2's power-on-reset requirement imposed on GDDR5, and a Volta
register offset assumed present on Kepler. Neither was a mistake when written.
Both became wrong the moment a second architecture arrived, and neither
announced the transition.

The generation profile is the right home for this and already exists. The
failure mode is not missing infrastructure but code that predates it and was
never swept in.

---

## Next

| # | Item | Status |
|---|------|--------|
| 1 | ~~`DEVINIT_STATUS` offset into `GenerationProfile`~~ | **RETRACTED** — `0x2240c` is correct on GK210; the all-ones was the wedged die |
| 2 | Kepler PMC_ENABLE sequencing — dies wedge after `pgraph_reset` | **OPEN — now the sole K80 blocker** |
| 3 | Sweep remaining raw `read_u32().unwrap_or(...)` decision sites | OPEN |
| 4 | GK210 nouveau dispatch patch | **WITHDRAWN** — sovereign path does not need a seeder |
| 5 | FECS liveness on Volta — the standing Tier 2 wall | OPEN |
| 6 | `SA_SIGINFO` signal provenance; handoff critical section | PENDING |

Both cards remain targets. QCD is a target; sovereign deployment is the goal.
