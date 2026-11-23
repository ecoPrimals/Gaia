# Crash dogfood — blueGate, 2026-11-16 05:57

## What we saw
- Bugcheck 0x1E KMODE_EXCEPTION_NOT_HANDLED, c0000005 (access violation), in the Windows kernel itself:
  `nt!KeContextFromKframes`. No third-party driver on the stack. Process at the time: `rustc.exe`.
- Trigger: a 32-thread Rust test build of biomeOS (sustained full CPU + memory load).
- 1 bugcheck and 3 unclean shutdowns in 30 days. No WHEA hardware errors (consumer DDR5 fails silently).
- Our code cannot cause this: user-mode programs can't bugcheck Windows. Our load exposed it.

## The body
- CPU: Ryzen 9 9950X3D (16C/32T). Board: ASUS ROG STRIX X870E-E GAMING WIFI.
- RAM: 2 × 48 GB G.Skill F5-6400J3239F48G (dual-rank) running EXPO at 6400 (JEDEC default 5600).
- BIOS 1401 (May 2025). Latest is 2503 (Sep 2026, AGESA 1.3.0.1d). BitLocker off on C:, M:, N:.

## What others saw (same CPU, same kit)
- r/overclocking "Having a hard time stabilizing 2x48GB M-Die on 9950x3d": exact same kit and CPU.
  Consensus: 2×48 GB dual-rank at 6400 1:1 is often beyond the memory controller. Owners report stable at
  6200 CL28 or 6000 CL28; one got BSODs at 6200 CL30 during testing.
- Fixes they used: VSOC 1.25–1.30 V; PBO and negative Curve Optimizer OFF while testing memory;
  drop to 6200 or 6000 if 6400 won't hold.
- Phoronix (9950X DDR5 review): compile workloads are what expose unstable memory (GCC segfaults at 8000).
- ASUS BIOS 2103 notes: "additional stability margin during high-frequency DDR5 training" and
  "addresses ... stability issues observed on certain Ryzen 9000 configurations". 2503 adds more.
- ASUS forum: after flashing, re-enter settings by hand; old saved profiles (CMO) can cause hangs.
- 1804 and 2202 cannot be rolled back.

## How to solve it, one change at a time (each followed by the same biomeOS build as the stress test)
1. Flash BIOS 2503 (USB BIOS Flashback; rename A5557.CAP with BIOSRenamer). Re-enter EXPO by hand.
2. If it still crashes: PBO / Curve Optimizer to defaults, VSOC 1.25 V.
3. If it still crashes: memory 6200, then 6000.
Until proven stable, Gaia builds with `cargo -j 8`.
