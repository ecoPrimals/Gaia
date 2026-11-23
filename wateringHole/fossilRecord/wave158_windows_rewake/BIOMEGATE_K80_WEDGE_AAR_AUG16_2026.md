# biomeGate K80 Wedge Hunt AAR — Aug 16, 2026 (Evening)

**Date:** Aug 16, 2026 17:00–18:05 UTC-4 | **Wave:** 157k | **Team:** biomeGate hotSpring sub-team
**Gate:** biomeGate (Threadripper 3970X, 128GB, RTX 5060 + Titan V + 2× K80)
**Status:** Four bugs found and fixed, K80 VBIOS obtained for the first time, blocker advanced two stages. Five die-wedges spent getting there. Host never went down.

Fourth AAR of the day. Follows `BIOMEGATE_K80_SOVEREIGN_AAR_AUG16_2026.md`, which
this one partly corrects.

---

## Summary

The previous AAR recorded this as a success line:

```
[ok] pgraph_reset  pmc=0xc0002020 -> 0xc0003020   <- PGRAPH ungated, no vendor code
```

That line was the first of the bugs. It reads as progress — an engine ungated,
no vendor driver involved — and it was in fact clocking PGRAPH before its power
rails existed. Everything downstream of it in that AAR was measured on a dying
die.

Four bugs, all the same shape: **acting on data we could not validate.**

| # | Bug | Consequence |
|---|-----|-------------|
| 1 | `pgraph_reset` ignored `PowerSafetyProfile` | Clocked PGRAPH pre-devinit on a generation where devinit *is* the power sequencer |
| 2 | `pramin_sentinel_test` used as a *test* | Wrote `0xCAFEBEEF` into untrained GDDR5 to find out whether GDDR5 worked |
| 3 | PROM read through a PRI-faulted PBUS ring | Wrote `0x1854` in a ring answering `0xbad0011f`. **This was the actual killer.** |
| 4 | Interpreter executed a 76%-unknown parse | 196 register writes decoded from garbage |

Net: the K80 now reads its own VBIOS off the die with no vendor code, and the
blocker has moved from "cannot start" to "Kepler opcode coverage".

Commits: `1d07d198c`, `20821be8a`, `e068a860b`. 780 tests pass, 25 of them new,
each pinned to a register value measured on live silicon.

---

## Bug 1 — `pgraph_reset` ignored the power profile

`pmc_enable` applies Kepler's `PMC_MASK_CONSERVATIVE` (`0xC000_2030`). That mask
deliberately excludes GR, and the profile says why in its own comment:

> `full_enable_after_devinit: false` — *"False for Kepler/Maxwell where devinit
> IS the power sequencer."*

The very next stage set bit 12 anyway:

```
pmc_enable      mask=0xc0002030            <- GR deliberately excluded
pgraph_reset    0xc0002020 -> 0xc0003020   <- GR enabled regardless
memory_training                            <- devinit had not run yet
```

The profile was in scope at the call site. It simply was not passed.
`pgraph_engine_reset(bar0)` took no profile argument, so there was nothing to
consult, and the caller three lines above had it in a local named `power`.

**Fix.** The function now takes the profile and an explicit `DevinitState`, and
defers when GR is absent from the pre-devinit mask. A bare `bool` was rejected
for the second parameter — at the call site `true` does not say which way round
it is. Its PMC writes also go through the fork-isolated path, rather than bare
`write_u32` with the result discarded, on the one register where the codebase
already knew better (`pmc_enable_full` had used isolation all along).

**Verified on hardware:**

```
[ok] pgraph_reset  deferred: GR not in pre-devinit mask (0xc0002030); devinit is
                   the power sequencer on this generation, so PGRAPH stays gated
                   until it has run. pmc=0xc0002020 unchanged
```

---

## Bug 2 — probing VRAM to find out whether VRAM works

`gddr5_training` opened by calling `pramin_sentinel_test` to decide whether
memory needed training. Despite the name, that function is not a read. It steers
`BAR0_WINDOW` and **writes** `0xCAFEBEEF` into video memory.

On a cold K80 that is a store into GDDR5 with no configured timings, through a
window register that lives in a PRI-faulted ring.

This is the same circularity as `vfio::reset_guard` from the earlier AAR:
resetting an unresponsive device to make it respond. You cannot probe VRAM to
learn whether VRAM works.

**Fix.** Consult `DEVINIT_STATUS` first — it *does* answer on a cold die
(`0x00000000` on both K80s, `0x00000002` on a POSTed Titan V) — and touch the
aperture only once memory is known to be up.

**A second copy existed.** `check_vram_via_pramin` in
`vfio/channel/devinit/pmu/mod.rs` does the same thing with `0xCAFE_DEAD`. Every
guard added to the first copy did nothing for it. It is now guarded on BAR0
liveness, and both functions carry a `# Destructive` doc section, because the
names do not warn anybody.

---

## Bug 3 — the actual killer

After bugs 1 and 2 were fixed and *verified working*, the dies still wedged.

That is the part worth recording. Both guards demonstrably held —
`pgraph_reset` logged `pmc unchanged`, the PRAMIN entry guard logged the skip —
and the die died anyway. Each time this read as "the fix did not work," when it
actually meant "there is another one."

`FalconDiagnostic::probe` reads the VBIOS to build its report:

```rust
let prom_enable_reg = r(PROM_ENABLE_REG);                              // 0x1854
let _ = bar0.write_u32(PROM_ENABLE_REG, prom_enable_reg & !1);         // un-shadow
let prom_signature = r(PROM_BASE);                                     // 0x300000
let _ = bar0.write_u32(PROM_ENABLE_REG, prom_enable_reg);              // restore
```

`0x1854` is a **PBUS** register. On a cold Kepler the entire PBUS ring answers
`0xbad0011f`. Measured on the die immediately before a run:

```
boot0=0x0f22d0a1  pbus_1854=0xbad0011f  pmc=0xc0002020  devinit=0x00000000
```

Writing into a faulted ring and then reading a 1MB aperture behind it takes BAR0
to all-ones until reboot. This ran unconditionally on every cold bring-up.

**Fix.** Classify `0x1854` before touching it.

**Result — the die survived, reproducible ×4:**

```
[ok    ] pgraph_reset     deferred: GR not in pre-devinit mask ...
[failed] memory_training  no VBIOS source available
boot0=0x0f22d0a1  pmc=0xc0002020   ALIVE
```

First K80 sovereign init that does not destroy the die.

### A misleading error message cost a die

The early return in `gddr5_training` reused `Gddr5PraminDeadDevinitSkipped`,
whose text reads *"DEVINIT not needed per register but PRAMIN is dead."* The new
guard path deliberately never probes PRAMIN — but it reported that it had, and
found it dead. It was indistinguishable from the pre-existing failure, so a
working guard looked like a failed one and the search went elsewhere.

Split into `Gddr5DevinitDeclinedWhilePostNeeded`, which says what actually
happened: the two readings disagree, so memory state is unknown and PRAMIN was
deliberately not touched.

**An error variant reused for a second meaning is a lie the next reader has no
way to detect.**

---

## The find: PROM decodes cold, without the write

With PROM correctly off-limits the run failed with `no VBIOS source available`.
Checking the alternatives:

- **PCI expansion ROM BAR:** config offset `0x30` reads `0x00000000` — unimplemented.
- **ACPI `_ROM`:** absent.
- **PRAMIN VBIOS shadow:** requires a POST that has not happened.

PROM was the only source, and it sat behind the ring we had just agreed not to
touch. So, read-only probe, no writes anywhere:

```
PROM[0x300000] = 0xeb7baa55   signature 0xAA55? True
PROM[0x300004] = 0x3034374b
boot0          = 0x0f22d0a1   (alive)
```

**The aperture already decodes.** Un-shadowing via `0x1854` is an optimization,
not a precondition. The write that cost three dies was never needed for the read
it was meant to enable.

Both PROM paths now skip only the *write* when the ring is faulted, and read
regardless. Reads of a faulted ring are benign — we had been doing them all day.

This is the first VBIOS the K80 has ever handed us, off its own die, with no
vendor driver in the path.

---

## Bug 4 — executing a parse that did not parse

With the VBIOS in hand the interpreter ran, and wedged the die:

```
VBIOS interpreter total  scripts=6 ops=1044 writes=196 unknown=796 delays_ms=10000.3
VBIOS: stream desynced (100 unknown opcodes) — terminating script
VBIOS interpreter fallback result  writes=196 vram="still dead"
```

**796 of 1044 opcodes unknown — 76%.**

That is not "Kepler has unimplemented opcodes." That is not parsing the script.
Each bad decode advances the offset by the wrong stride, so everything after it
is read at the wrong boundary and the stream never recovers. Most likely a wrong
script-table offset.

It issued **196 register writes** decoded from that garbage.

A desync detector existed — it fires at 100 unknowns — but it fires *after*, by
which time the writes have landed. Detection downstream of the side effect is
not a guard.

**Fix.** `writes_armed: bool` on the interpreter, gated at the single
`bar0_wr32` choke point. Each script is walked once with writes disarmed; a
script missing more than 25% of its opcodes is refused rather than executed.

Kepler opcode coverage is the real fix and remains open. This only ensures a
parser that does not understand its input cannot drive hardware.

---

## Also fixed: write-before-check in the PRI path

Enabling `needs_cg_sweep` for Kepler required hardening the stage first.

`cg_sweep` phase 1 checks `is_pri_fault(old)` before writing. **Phases 2 and 3
wrote first and checked afterwards** — and those phases are the FBPAs and LTCs,
which on a cold Kepler front untrained memory and are precisely the domains
answering `0xbad0*`. The check was backwards in the worst possible place.

`pri_bus_recover` acknowledged the ringmaster by writing back the value it had
just read, gated on `rm_intr != 0`. A fault pattern is very much non-zero, so on
a faulted ring it wrote `0xbad0011f` into the ringmaster's control register and
then issued `ENUMERATE` on top of it. Same pattern in
`PriBusMonitor::attempt_recovery`.

All now classify before writing.

`NvKeplerStrategy::needs_cg_sweep()` flipped `false` → `true`. It had been
`false`, so `pri_bus_recover` **never ran on Kepler at all**.

**Verified on hardware:**

```
[ok] cg_sweep      3 changed, 18 faulted [PTHERM master gate: 0x22722444->0x00000000, ...]
[ok] pri_recovery  2 alive, 11 faulted, recovered=true
                   die ALIVE
```

Real state change (PTHERM clock gating genuinely cleared), 18 faulted domains
correctly skipped, die survived.

---

## Negative results worth keeping

- **PRI recovery does not clear the PBUS fault.** `recovered=true`, and
  `0x1854` still read `0xbad0011f` afterwards. That ring is unpowered, not
  merely holding stale faults. Ack-and-enumerate is the wrong tool.
- **`PMC_ENABLE` writes do not fully stick when cold.** Mask `0xc0002030`
  written, `0xc0002020` read back — bit 4 never takes. Unexplained; may be the
  same unpowered-domain story.
- **The K80 has no expansion ROM BAR and no ACPI `_ROM`.** PROM is the only
  VBIOS source on this card. Any future "just read the ROM from sysfs" plan is
  dead on arrival.
- **A wedged die is refused at the factory**, before any guard runs, because
  identity probe sees all-ones. Guards cannot be regression-tested on a corpse.

---

## Method note

Five dies were wedged across the session. Every one was a **GPU** loss, never a
host loss: no `pci_lock`, no hung tasks, `toadstool` responsive throughout. That
is `vfio::reset_guard` from the previous AAR doing its job — the Exp 229 class of
failure did not recur even once while we were actively wedging hardware.

Two process notes:

1. **Guards were validated on the wedged die first where possible**, since
   all-ones is exactly the input they must refuse. This is free — the die is
   already lost — and it caught that the factory rejects wedged devices before
   guards are reached.

2. **The release binary was nearly tested without the fix in it.** After the
   `Ok(false)` guard was written, only `cargo build -p toadstool-cylinder`
   (debug) had run; `~/.local/bin/toadstool` was still the previous release. Had
   that gone unnoticed, a working fix would have been recorded as a failure and
   abandoned. Check binary timestamps against commit times before hardware runs.

---

## Current K80 position

```
[ok    ] identity_probe   raw=0x0f22d0a1 chip=0x0f2
[ok    ] pmc_enable       before=0xc0002020 after=0xc0002020 mask=0xc0002030
[ok    ] pgraph_reset     deferred (GR not in pre-devinit mask)
[ok    ] cg_sweep         3 changed, 18 faulted
[ok    ] pri_recovery     2 alive, 11 faulted
[ok    ] boot_state_probe cold
[failed] memory_training  <- VBIOS read OK; interpreter cannot parse the scripts
[ok    ] pmc_rollback
```

Both dies wedged at time of writing (by the interpreter, before the guard
existed). Reboot recovers them; they come back cold and healthy at
`boot0=0x0f22d0a1 pmc=0xc0002020 devinit=0x00000000`.

The live edge moved from `memory_training: no VBIOS source` to
`memory_training: cannot decode the scripts inside the VBIOS we now hold`.

---

## Next

1. **Kepler VBIOS opcode coverage.** 76% unknown says wrong parse, not missing
   opcodes. Start with the script-table offset resolution against
   `nvkm/subdev/bios/init.c`, then the per-opcode strides for
   `BiosGeneration::Kepler`. Read-only work — the ROM is already dumped and can
   be parsed offline against a known-good decode without any hardware.
2. **Dump the K80 VBIOS to a file** now that PROM reads. Offline parsing costs
   no dies, and `best_vbios` already has a file source.
3. **Why does `PMC_ENABLE` bit 4 not stick when cold?** May be the same
   unpowered-domain question as PBUS.
4. **Sweep for further destructive probes named as tests.** Two copies of the
   PRAMIN write existed; a third would not be surprising. Grep for `write` under
   functions named `*_test`, `check_*`, `probe_*`.

---

## The pattern

Every bug this session, and every bug in the previous two AARs, is one thing:

> **Acting on data we could not validate.**

- Reading a sentinel as a value (`0xFFFFFFFF` as "POST complete")
- Probing VRAM to see whether VRAM works
- Writing a fault pattern back as an acknowledgement
- Executing opcodes from a parse that did not parse

The `RegisterRead` abstraction made the first unrepresentable. The rest were the
same idea wearing different clothes, in code that predates it. The remedy is not
more guards bolted on individually — it is that **an operation that requires a
subsystem to be healthy must ask whether it is healthy, and the asking must not
require the same subsystem.**

`DEVINIT_STATUS` answers when PBUS does not. PROM decodes when `0x1854` does not.
Those are the load-bearing facts of the day, and both were found by reading
before writing.
