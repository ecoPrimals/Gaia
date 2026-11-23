# biomeGate DRM Hot-Add Root Cause AAR — Aug 16, 2026

**Date:** Aug 16, 2026 09:00–10:45 UTC-4 | **Wave:** 157k | **Team:** biomeGate hotSpring sub-team
**Gate:** biomeGate (Threadripper 3970X, 128GB, RTX 5060 + Titan V + 2× K80)
**Status:** ROOT CAUSE FOUND — one cause behind three session kills; guards landed in Rust

---

## Summary

Three consecutive session kills during Titan V warm handoff were diagnosed three
separate times and fixed twice, wrongly. All three had a single root cause:
**nouveau registers a DRM node even under `modeset=2`**, Xorg hot-adds it, and Xorg
calls `abort()` on an internal assertion.

The two earlier diagnoses were not merely incomplete, they were confidently wrong,
and each produced a fix that shipped. This AAR records the false trails as
prominently as the answer, because the failure mode here was diagnostic, not
electrical: every layer reported a plausible local fault, and the pipeline had no
instrument capable of observing the actual mechanism.

Session safety is now encoded in `toadstool-cylinder` as machine-checked preflight
and a live DRM watch, so this specific class cannot recur silently.

---

## The Actual Chain

Times are local. The whole cascade fits in 15 seconds.

| Time | Event |
|------|-------|
| `09:45:56.359` | `finit_module` patched nouveau, `params="modeset=2 runpm=0"` |
| `09:45:56.6` | `[drm] Initialized nouveau 1.4.2 for 0000:21:00.0 on minor 0` — **card0 created** |
| `09:45:57.028` | Xorg udev: `Adding drm device (/dev/dri/card0)` on `pci0000:20/.../0000:21:00.0` |
| `09:45:57.031` | Handoff settle begins (15,000ms) |
| `09:45:57.492` | `modeset(G0): glamor X acceleration enabled on NV140` |
| `09:45:57.494` | `Xorg: dixRegisterPrivateKey: Assertion '!global_keys[type].created' failed` → `abort()` |
| `09:46:12.020` | Session scope teardown SIGTERMs toadStool, **11ms before settle would end** |
| `09:46:12.921` | Graceful shutdown triggers handoff rollback → unbind mid-rotation |
| `09:46:12.9` | `BUG: unable to handle page fault` in `nve0_bo_move_copy` ← `nouveau_ttm_fini` |
| `09:48:50` | Operator logs back in; new Xorg |

Xorg killed itself. The kernel oops came afterward, as a consequence of the
rollback that the dying session triggered.

### The 11ms was a coincidence with a cause

The near-miss between SIGTERM and settle-end looked causal and drove a wrong
hypothesis (see below). It is the signature of **two independent ~15s intervals
starting 3ms apart from one trigger**:

- insmod created the DRM node at `57.028` → Xorg died at `57.494` → session scope
  teardown reached toadStool at `09:46:12.020`
- the same insmod started the 15,000ms settle at `57.031` → would end at `09:46:12.031`

Two clocks, one origin, ends 11ms apart.

---

## What `modeset=2` Actually Does

`modeset=2` suppresses display *output* — the card reports no CRTCs — but still
calls `drm_dev_register`. `/dev/dri/cardN` appears exactly as in full KMS mode.

The evidence was present and misread from the first run:

- `Initialized nouveau 1.4.2 ... on minor 0` — **minor 0 is card0**. Read as benign.
- `[drm] No compatible format found` / `Cannot find any crtc or sizes` — read as
  proof that headless mode suppressed the node. It only means no monitor is
  attached.
- A post-hoc `ls /dev/dri` showed only `card1`, which "confirmed" the fix. The node
  was already gone because the module had torn down by then.

**Lesson:** a post-hoc check of a transient resource cannot confirm the resource
never existed. The DRM watch now samples during the window, not after it.

---

## False Trails (both shipped as fixes)

### Trail 1 — "DRM node creation, fixed by `modeset=2`"

Correct mechanism, wrong remedy. `modeset=2` does not prevent registration. Shipped
as `NOUVEAU_HEADLESS_PARAMS` and declared closed. Two further crashes followed and
were attributed to new causes because this vector was believed shut.

### Trail 2 — "toadStool's process group was torn down by the calling shell"

toadStool was launched `nohup ... &` with no `setsid`, leaving it in the caller's
process group. This is real, and the 11ms alignment made it compelling.

**Falsified by direct experiment.** Launching both patterns and ending the command
block: `nohup`-only survived (pgid shared with a long-lived stateful shell that is
never torn down between commands). The hypothesis was wrong.

The `setsid` hardening was kept — it is correct hygiene — but it fixed nothing here,
and shipping it as *the* fix would have left the real cause live.

**Lesson:** a mechanism that is real, plausible, and temporally aligned can still
not be the cause. Cheap falsification beats a good story.

---

## Genuine Second Bug: Teardown Page Fault

Independent of the session kill, and real.

The `volta_warm_handoff` patch set NOPed `gf100_gr_fini`. On nouveau 1.4.2 that
function releases the FECS falcon:

```
gr: fini failed, -1028627904
gr: fecs falcon already acquired by gr!
gr: init failed, -16                      <- EBUSY
```

Teardown then moved buffer objects with a copy engine that never initialized and
page-faulted in `nve0_bo_move_copy`. The oops leaked nouveau's refcount to 2,
producing a zombie module immune to forced `delete_module` and requiring a reboot.

The patch set was authored against an older nouveau whose teardown hung. On kernel
7.0 it converts a hang into an oops. `gf100_gr_fini` is now excluded from both the
Volta and Kepler sets, guarded by a regression test.

Trade-off accepted: GR state likely will not survive unbind, degrading achievable
tier. Tier classification reports that honestly; a kernel oops does not.

---

## Fixes Landed

### Host configuration

| Change | File | Effect |
|--------|------|--------|
| Xorg GPU hot-add disabled | `/etc/X11/xorg.conf.d/10-biomegate-no-gpu-hotplug.conf` | `AutoAddGPU`/`AutoBindGPU` off. Both default **ON**; the directory was empty. Confirmed honored: `(**) Option "AutoAddGPU" "off"`. |
| Full SysRq | `/etc/sysctl.d/99-biomegate-sysrq.conf` | Mask was `176` — sync(8) and reboot(64) **disabled**, so a hung shutdown could only be escaped by cutting power to a live ZFS root. Now `1` (REISUB available). |

### toadStool (`toadstool-cylinder`)

New module `vfio::session_safety` — 12 tests:

- `DrmNodeWatch` — arms a baseline per BDF, reports `card*` nodes appearing since.
- `host_state` — kernel oops taint (bit 7), Xorg hot-add config, display-server
  detection, display-GPU identification. **Absent Xorg config reads as unsafe**,
  because both options default on.
- `SessionSafety::evaluate()` — composes concerns, each carrying a remedy string.

Wired into the handoff pipeline at two points:

- **Preflight** refuses the rotation and logs the remedy.
- **Settle** polls every 100ms and aborts on card-node breach. The observed window
  between node creation and Xorg hot-add was **466ms**.

The watch arms in *preflight*, not settle: the node registers during insmod, which
precedes settle, so a watch armed at settle would capture the hazard as its own
baseline and never fire.

Also fixed this session, each a silent corrupter of earlier results:

| Bug | File | Symptom |
|-----|------|---------|
| `.ko.zst` not decompressed | `module_patch/mod.rs` | 0/8 patches applied; compressed bytes never matched symbols |
| PKCS#7 signature invalidated by patching | `module_patch/mod.rs` | `finit_module` errno 129 (EKEYREJECTED) |
| `O_RDWR` on write-only sysfs | `hw-safe/device_io.rs`, `guarded_sysfs/driver_ops.rs` | EACCES on `unbind` despite CAP_SYS_ADMIN |
| `M=$(PWD)` in generated Makefile | `kmod_build/build.rs` | `Makefile: No such file or directory` |
| Missing `-isystem` for `-nostdinc` | `kmod_build/build.rs` | `stddef.h: No such file or directory` |
| Section attribute on struct type, not variable | `kernel_health/probe.rs` | GCC 13 dropped `.note.module_offsets` |

### Hygiene

`infra/scripts/biomegate-gpu-restore.sh` now uses `setsid nohup`. Not the root
cause, but primals should not inherit a caller's process group.

---

## Known Gaps

- **Xorg check reads config, not the running server.** A file edited after Xorg
  starts reads "safe" while the live server still has hot-add enabled. The taint
  check covers the reboot window in practice, but this is a proxy.
- **Untested against a real breach.** The DRM watch is unit-tested against the
  recorded failure shape; it has not yet fired on live hardware.
- **`modeset=0` unexplored.** Would prevent registration entirely, but also
  prevents hardware init, defeating the seeding purpose.
- **The original teardown hang is unverified on 7.0.** The patch set exists to
  prevent a hang that may no longer occur. Running stock unpatched nouveau would
  settle whether the premise is obsolete.

---

## Method Notes

What actually cracked this was correlating three clocks that had never been on one
axis: toadStool's structured log, `dmesg`, and the systemd journal. The Xorg abort
existed only in the journal. The DRM node creation existed only in `dmesg`, in a
line whose meaning turned on the word "minor". Neither was visible to the
bash/python harness driving the experiment, which reported "halted safely at
preflight" while the session was already gone.

A harness that cannot observe what it is causing will keep producing confident
wrong answers. That is the argument for moving experiment orchestration into Rust
primals, now underway.

**Three forced power cycles.** ZFS (`bpool`, `rpool`) came through all of them
`ONLINE` with no errors.

---

## Next

| # | Item | Status |
|---|------|--------|
| 1 | Signal provenance via `SA_SIGINFO` (`si_pid`/`si_uid`) | PENDING |
| 2 | Handoff as critical section — defer SIGTERM to a safe point | PENDING |
| 3 | Phase-correlated dmesg/journal capture in the handoff timeline | PENDING |
| 4 | Retire `exp-r6-run.py` / `nouveau-headless-check.sh` into the Rust runner | PENDING |
| 5 | Re-run R6 on Titan V with guards active; classify tier | READY |
| 6 | K80 track (co-equal target): unsigned falcons, firmware extraction | READY |

Both cards are targets. QCD is a target; sovereign deployment is the goal.
