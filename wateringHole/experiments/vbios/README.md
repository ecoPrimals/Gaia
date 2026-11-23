# VBIOS dumps

Working area for offline VBIOS analysis. **The `.rom` files are NVIDIA firmware
and are deliberately not committed** — see `.gitignore` here. This file records
how to regenerate them so the analysis stays reproducible without redistributing
vendor code.

## Why dump at all

Debugging the interpreter against live hardware costs a die per wrong guess and
a reboot per iteration. Against a file it costs a failed assertion. The Kepler
boot-script misparse (76% unknown opcodes → 0%) was found this way in about an
hour, having survived a day of on-hardware work.

## Regenerating

The GPU must be in D0 with memory decode enabled and, ideally, no driver bound.
Both K80 dies satisfy this after a reboot. **The read is non-destructive** —
PROM decodes cold and needs no un-shadowing write; do not write `0x1854` to
"enable" it, which is what wedged a die on Aug 16.

```bash
sudo python3 - <<'PY'
import mmap, os
BDF  = "0000:4b:00.0"      # K80 die 1; 4c:00.0 is die 2
PROM = 0x300000            # NV_PROM aperture in BAR0
SIZE = 0x20000             # 128 KiB covers a 62,976-byte ROM

fd = os.open(f"/sys/bus/pci/devices/{BDF}/resource0", os.O_RDONLY | os.O_SYNC)
m  = mmap.mmap(fd, PROM + SIZE, mmap.MAP_SHARED, mmap.PROT_READ)
data = m[PROM:PROM + SIZE]
m.close(); os.close(fd)

assert data[0] == 0x55 and data[1] == 0xAA, f"no option-ROM signature: {data[:4].hex()}"
open("k80_gk210_4b000_prom.rom", "wb").write(data)
print(f"ok: {data[2] * 512} bytes of ROM in a {len(data)}-byte window")
PY
```

Expected on a K80 (GK210): first word `0xeb7baa55`, size byte 123 (62,976
bytes), PCIR `10de:102d`.

Afterwards, confirm the die still answers — a read should be harmless, and
checking costs nothing:

```bash
sudo python3 -c "print(open('/sys/bus/pci/devices/0000:4b:00.0/config','rb').read(2).hex())"
# expect de10  (0x10de little-endian)
```

## Using a dump as a test fixture

Copy it into toadStool's gitignored fixture directory:

```bash
cp k80_gk210_4b000_prom.rom <toadStool>/testdata/vbios/k80_gk210.rom
cargo test -p toadstool-cylinder --lib kepler_boot_scripts_decode -- --nocapture
```

The test **skips** when the fixture is absent, so a clean checkout still passes.
Expected output:

```
K80: ops=381 unknown=2 (0%) writes=303
```

Known fixture names: `k80_gk210.rom` (GK210), `titanv_gv100.rom` (GV100).

## Reference

`handoffs/BIOMEGATE_KEPLER_VBIOS_DECODE_AAR_AUG17_2026.md` — the two
payload-length bugs, and why the previous unit test could never have caught
them.
