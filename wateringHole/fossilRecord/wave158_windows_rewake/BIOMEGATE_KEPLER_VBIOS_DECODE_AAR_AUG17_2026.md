# biomeGate Kepler VBIOS Decode AAR — Aug 17, 2026 (Midday)

**Date:** Aug 17, 2026 11:57–13:10 UTC-4 | **Wave:** 157k | **Team:** biomeGate hotSpring sub-team
**Gate:** biomeGate (Threadripper 3970X, 128GB, RTX 5060 + Titan V + 2× K80)
**Status:** Kepler VBIOS blocker resolved. Boot scripts decode at **0% unknown opcodes**, down from 76%, yielding 303 register writes. Found entirely offline. **No hardware touched beyond a read-only ROM dump; nothing executed on a die.**

Sixth AAR of the cycle. First one where the process review of the morning
directly produced the afternoon's result.

---

## Summary

The morning's process review closed with a prediction: *the next wave should be
judged on whether it moves the VBIOS parse, not on how much more instrument debt
it finds.* It also named the most under-exploited technique available —
`ScriptBus`, the trait that lets the interpreter run with no GPU present.

Both held. The blocker fell in about an hour, offline, and the fix is two
payload-length bugs of the same species.

| Configuration | Unknown opcodes |
|---------------|-----------------|
| group count 4 (fallback), `0x8F` 6-byte header | **76%** — the failure as reported from hardware |
| group count 8 (correct), `0x8F` 6-byte header | 40% |
| group count 8, `0x8F` 7-byte header | **0%** — 2 of 381 |

---

## Getting the artifact

Everything downstream needed a ROM on disk. Both K80 dies came back from the
Aug 17 reboot `Responding` and unbound, which is the safest state this hardware
has been in for days: no driver to fight, memory decode already enabled, D0.

Read-only `mmap` of `resource0` at `BAR0 + 0x300000`, 128 KiB:

```
first word: 0xeb7baa55     AA55 signature present
rom size:   123 blocks = 62,976 bytes
PCIR:       10de:102d, image length 62,976
```

`0xeb7baa55` matches the value recorded on Aug 16 exactly, confirming both the
PROM aperture and that reading it cold still needs no un-shadowing write. Both
dies were verified `Responding` afterward, and the second die dumped identically.

**This was the whole hardware interaction.** One read. Everything after it is a
file.

---

## Bug 1 — the group count came from the wrong structure

Opcodes `0x87`, `0x88`, `0x8A` and `0x8F` carry one `u32` per RAM-restrict
group. The group count therefore sets their length, and a wrong count desyncs
the walk permanently: every byte after the first such opcode is read at the
wrong boundary.

Ours dereferenced BIT 'M' `data[0:2]` as a pointer to the rammap table, then
read `+4` of whatever it landed on:

```rust
let tbl_ptr = u16::from_le_bytes([rom[m_off], rom[m_off + 1]]) as usize;
let snr = rom[tbl_ptr + 4] as usize;
if snr > 0 && snr <= 16 { return snr; }
```

The count is not behind a pointer. It is a field of the 'M' entry itself, at a
version-dependent offset (nouveau `nvbios_ramcfg_count`):

| BIT 'M' version | Requires | Count at |
|-----------------|----------|----------|
| 1 | `length >= 5` | `offset + 2` |
| 2 | `length >= 3` | `offset + 0` |

The K80's 'M' entry is version 2, 17 bytes, and its data begins `08 5b 4e a7 …`
— so the count is **8**. The bogus pointer path produced **58**, which failed
the `<= 16` bound and **fell through to a default of 4**.

That fallback is why the failure looked like broad opcode ignorance rather than
an obviously wrong number: 4 is plausible, so nothing downstream complained.

Note the near-miss. `08 5b` little-endian is `0x5b08`; the correct answer was
the low byte of the pointer the code built out of it.

---

## Bug 2 — `0x8F` had the wrong header shape

Fixing the count took 76% → 40%. Better, still not a decode.

nouveau's `init_ram_restrict_zm_reg_group`:

```c
u32 addr = nvbios_rd32(bios, offset + 1);
u8  incr = nvbios_rd08(bios, offset + 5);   /* address stride */
u8   num = nvbios_rd08(bios, offset + 6);   /* group count    */
init->offset += 7;
```

Ours used a **6-byte** header and read the count from **`+5`** — which is the
address stride, not a count — then advanced registers by a fixed 4 instead of by
`incr`.

On the K80's first group (`8f 50 00 11 00 04 01 …`: addr `0x00110050`, incr 4,
num 1) that consumed `6 + 4×8×4 = 134` bytes where the opcode occupies
`7 + 1×8×4 = 39`. The walk resumed 95 bytes into the payload.

With the header corrected: **0% unknown, 2 residual opcodes out of 381.**

---

## Validating that it is a decode and not a coincidence

A clean opcode histogram is necessary and not sufficient — a wrong-but-
self-consistent parse can also look tidy. Three checks:

**Volume.** 303 register writes from 381 opcodes. A parse that terminates early
produces a clean percentage and almost nothing else.

**Targets.** Where the writes land is the strongest signal, because it is
independent of the parser:

| Domain | Writes | What it is |
|--------|--------|-----------|
| `0x11e000` | 194 | memory partition |
| `0x10f000` | 14 | **PFB — framebuffer** |
| `0x137000` | 10 | **PTRIM — clock tree** |
| `0x00e000` | 11 | GPIO / thermal |
| `0x61c000` | 5 | **PDISP — display** |
| `0x022000` | 4 | PMC |

That is the shape of a memory-and-clock bring-up. Garbage decoded from the wrong
byte boundary does not land preferentially in the framebuffer and clock trees.
The test now asserts on the domains, not just the counts.

**No regression.** Titan V decodes unchanged; all 794 cylinder tests pass.

### Residual

Two unknowns remain — one `0x00` at `0x9345` after a `0x96` (`I2C_LONG_IF`), one
`0x0D` at `0xb84e` after a `0x4D` (`ZM_I2C_BYTE`). Both are length errors in
opcodes that do nothing under VFIO. Worth fixing for correctness; not blocking.

---

## The test was holding the bug in place

The existing coverage for `ram_restrict_group_count` was:

```rust
// M data[0:2] = pointer to rammap table
rom[m_data_off..m_data_off + 2].copy_from_slice(&(tbl_off as u16).to_le_bytes());
// Rammap table header: snr at offset +4
rom[tbl_off + 4] = count;
assert_eq!(ram_restrict_group_count(&rom), 8);
```

It built a ROM *in the shape the buggy reader expected*, then asserted the
reader found what had been planted for it. It passed, permanently, and could
never have failed — the fixture and the implementation shared the same
misunderstanding.

This is worse than no test. It converted an untested assumption into a green
check, and any future reader correcting the formula would have seen a passing
test break and assumed they were wrong.

**A synthetic fixture built from your own reading of a format tests self-
consistency, not correctness.** The replacements pin the real bytes from the
K80's BIT 'M' entry, so they are wrong only if the hardware is.

---

## Method note

The morning review called `ScriptBus` "the single largest multiplier found so
far and under-applied." Quantifying that from this session:

| | Before | Today |
|---|--------|-------|
| Iteration | one per reboot, a die at risk each time | sub-second, in a unit test |
| Cost of a wrong guess | possible dead die | a failed assert |
| Hardware needed | a live K80 | one read-only dump |

Five dies were spent on the previous stage of this problem. This stage cost
zero, and the diagnostic loop that found bug 2 — change a length, re-measure the
unknown rate — ran perhaps twenty times.

Second: **a Python model beside the Rust.** The two disagreed (15% vs 40%) after
bug 1, and the disagreement *was* the signal that located bug 2. A single
implementation would have shown 40% with nothing to compare it against, which
reads as "more unknown opcodes to implement" rather than "one length is wrong."
Two independent decoders of the same bytes is the software form of the
pair-your-sources rule that fixed GPU liveness detection yesterday.

---

## Current position

- Kepler boot scripts decode at 0% unknown, producing 303 writes.
- The interpreter's `writes_armed` guard will now **permit** these scripts,
  having refused them since Aug 16.
- Both K80 dies alive, unbound, `Responding`.
- ROM dumps archived under `wateringHole/experiments/vbios/`. Test fixtures are
  gitignored — vendor firmware is not committed; the test skips without them.

### Commits

| Commit | Subject |
|--------|---------|
| `6dcf4107e` | `ci: make the build reproducible — pin toolchain, track lockfile, gate test compilation` |
| `36a595b4c` | `fix(vbios): decode Kepler boot scripts — 76% unknown opcodes to 0%` |

---

## Next, and a warning about it

The obvious next step is to run the decoded script on a die. **That is the
single most dangerous thing this gate can currently do**, and it should not be
done casually:

1. 303 writes into the framebuffer and clock trees of a cold GPU is exactly the
   class of operation that cost five dies. The parse being correct raises the
   odds it works; it does not make it safe.
2. Both dies are currently healthy. A reboot recovers a wedge, so the risk is
   time, not hardware — but only while that remains true.
3. Recommended shape: **dry-run first** — arm the interpreter but route writes
   to a recording bus on live hardware, dump the intended sequence, and inspect
   it before letting a single write reach BAR0. The infrastructure for this
   already exists; it is what found the bug.

Prerequisites before any of that:
- Fix the two residual opcode lengths (`0x96`, `0x4D`).
- Confirm the strap read at `0x100000` returns something sane on a cold die —
  the group index comes from it, so a garbage strap selects the wrong values out
  of every group even with a perfect parse. **This is untested and is a
  sentinel-as-data risk of exactly the kind that has cost this project six
  times.**

---

## The pattern

Yesterday: *a component that reports on the system must not depend on a part of
the system it is reporting about.*

Today, the same rule aimed at test fixtures. **A test that builds its input from
the implementation's understanding of a format cannot detect that the
understanding is wrong.** It is a mirror, and it reports the reader's own
assumptions back as a passing check.

The corrective is the one the hardware side already learned: measure against
something you did not author. The replacement tests use the K80's actual bytes.
They can be wrong about the world, but they cannot silently agree with us about
it.
