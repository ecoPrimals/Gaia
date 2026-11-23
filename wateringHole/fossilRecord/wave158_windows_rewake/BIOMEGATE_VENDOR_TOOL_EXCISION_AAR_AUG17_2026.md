# biomeGate Vendor Tool Excision AAR — Aug 17, 2026

**Date:** Aug 16, 2026 18:30 – Aug 17, 2026 07:15 UTC-4 | **Wave:** 157k | **Team:** biomeGate hotSpring sub-team
**Gate:** biomeGate (Threadripper 3970X, 128GB, RTX 5060 + Titan V + 2× K80)
**Status:** GPU detection no longer shells out to vendor tools. Detection went from 1 GPU to 4. One phantom GPU removed. 216 tests recovered that had silently stopped compiling. Two real bugs surfaced by that recovery. No hardware lost.

Fifth AAR of the cycle. Follows `BIOMEGATE_K80_WEDGE_AAR_AUG16_2026.md`. Where
that one was about not destroying hardware, this one is about not lying about it.

---

## Summary

The mandate was deep debt, overstep cleanup, and evolution gaps: external
dependencies to Rust, hardcoding to capability-based, mocks isolated to
testing, unsafe made safe, large files refactored.

Measured first. Most of those categories came back **clean** — the codebase is
in better shape than a raw `grep` suggests, and saying so is part of the
result. What was not clean was GPU detection, which shelled out to `nvidia-smi`,
`rocm-smi`, and `lspci` and guessed at whatever they did not report.

That is a strange thing to find in a project whose definition of sovereign is
"no external non-Rust code in the runtime path." The detection layer was asking
the vendor stack to describe hardware the kernel had already enumerated.

---

## What the vendor tools were actually costing

Four defects, all live on this gate, all found by running the code and
comparing against the bus rather than by reading it.

### 1. It found one of four GPUs

`nvidia-smi` reports only devices bound to the proprietary driver. biomeGate has
four NVIDIA GPUs; exactly one is bound to that driver.

| GPU | Bound driver | Seen by `nvidia-smi` | Seen by sysfs scan |
|-----|-------------|----------------------|--------------------|
| RTX 5060 | `nvidia` | yes | yes |
| Titan V | none | **no** | yes |
| K80 die 1 | `vfio-pci` | **no** | yes |
| K80 die 2 | `vfio-pci` | **no** | yes |

The three it missed are the sovereign targets. The detection layer was blind to
precisely the configuration this project exists to produce, and blind in a way
that reported success.

### 2. It invented a GPU that does not exist

```rust
if cfg!(target_os = "linux") && Path::new(devfs::DRI_DIR).exists() {
    // Assume Intel integrated graphics
    gpus.push(GpuInfo { name: "Intel Integrated Graphics", memory_gb: 2.0, ... });
}
```

`/dev/dri` exists on any host with any DRM driver. There is no Intel graphics in
this machine. It was reporting one, with a hardcoded 2 GB, and had been for as
long as the check existed.

This is the mock-in-production case from the mandate, and it is worse than a
missing implementation: a stub that returns `None` is honest, and this returned
a plausible device.

### 3. Capability read off marketing strings

```rust
if gpu_name.contains("RTX 40") || gpu_name.contains("4090") { "8.9" }
else if gpu_name.contains("RTX 30") ... else { "Unknown" }
```

Compute capability derived by substring-matching product names. Every GPU on
this gate — Titan V, both K80s, RTX 5060 — falls through to `"Unknown"`. The
function has never returned a correct answer on this hardware.

### 4. Positional index used as a device address

`capabilities/gpu.rs` asked for memory with `nvidia-smi -i <device_id>`, where
`device_id` was **our own enumeration counter** — devices found so far, all
vendors, directory order. `nvidia-smi` indexes NVIDIA devices in its own order.

The two agree only when NVIDIA GPUs are enumerated first and in the same
sequence. Otherwise memory is attributed to the wrong GPU, or the index does not
exist and `nvidia-smi` prints "No devices were found" — leaving `memory_bytes`
at 0, which a caller cannot distinguish from a real measurement.

Verified on hardware:

```
$ nvidia-smi --query-gpu=memory.total -i 0000:02:00.0   → 8151
$ nvidia-smi --query-gpu=memory.total -i 1              → No devices were found
```

`nvidia-smi` accepts a PCI bus ID. We already had the exact one.

---

## The interesting bug was the one I wrote

The first version of the scanner filtered devices by PCI class read from **live
config space**. It found two of four GPUs.

Both K80 dies were wedged from the previous session. A device that does not
answer reads all-ones, so its class code reads `0xffffff`, which is not a
display or accelerator class, so it was filtered out — reported as *never
installed*.

```
0000:02:00.0  class=0x030000  → accelerator, kept
0000:21:00.0  class=0x030000  → accelerator, kept
0000:4b:00.0  class=0xffffff  → not an accelerator, dropped
0000:4c:00.0  class=0xffffff  → not an accelerator, dropped
```

This is the same sentinel-as-data mistake that cost five dies the day before,
committed fresh in the code written to clean up after it. Reading a sentinel and
treating it as an answer does not require exotic hardware state — it requires
only that you ask a question the device cannot answer and believe the reply.

**The fix came from noticing two sources answer different questions.** The
kernel caches `vendor`, `device`, and `class` at bus enumeration. Those survive
the device going silent. Live config space reports whether it is answering
*now*:

| Source | Wedged K80 reports | Question it answers |
|--------|--------------------|--------------------|
| sysfs cached attributes | `10de:102d`, class `0x030200` | who is this? |
| live config space | `0xffff`, class `0xffffff` | is it answering? |

Pairing them gives *"Tesla K80 at 0000:4b:00.0, not responding."* Either alone
gives half an answer. The class filter over live config space gives none.

`Liveness` is now a three-state enum — `Responding`, `NotResponding`,
`Unknown` — and `Unknown` is explicitly **not** usable:

```rust
/// [`Unknown`](Self::Unknown) is not a yes. Treating "I could not tell"
/// as "go ahead" is the sentinel-as-data mistake that has cost this
/// project several GPUs.
pub fn is_usable(self) -> bool { self == Self::Responding }
```

### Validated by the reboot

Post-reboot, with no code change, the same scanner reports:

```
0000:4b:00.0 vendor=0x10de device=0x102d class=0x030200 driver=-  Responding
0000:4c:00.0 vendor=0x10de device=0x102d class=0x030200 driver=-  Responding
```

Both dies recovered. The liveness field tracked a real hardware state change
across a power cycle. That is the first time this codebase has been able to
*say* a GPU came back rather than infer it.

---

## What replaced the vendor tools

Everything now comes from sysfs and procfs, which the kernel maintains for every
device regardless of bound driver, or none.

| Attribute | Source | Vendor tool needed |
|-----------|--------|--------------------|
| Presence, BDF, vendor, device, class | `/sys/bus/pci/devices/*` cached attrs | no |
| Bound driver | `driver` symlink | no |
| Driver version | `driver/module/version` → `595.84` | no — same string `nvidia-smi` prints |
| Model name | `pci.ids`, then kernel's own `Model:` line | no |
| Liveness | live config space vendor ID | no |
| BARs, capabilities, PCIe link | config space parse | no |
| **VRAM total** | `mem_info_vram_total` where published | **amdgpu only** |

Selection is by **PCI class**, so accelerators from unrecognised vendors still
enumerate, and class `0x12` processing accelerators — datacentre parts with no
display engine — are no longer missed by the `grep VGA` idiom.

Model names use the kernel's string in preference to `pci.ids`, because the
installed database is only as current as the package: the 2025 copy on this host
has no entry for the RTX 5060 (`10de:2d05`), while
`/proc/driver/nvidia/gpus/<bdf>/information` reports `NVIDIA GeForce RTX 5060`
exactly. That file is procfs written by the kernel module, not an `nvidia-smi`
invocation.

Result on this gate:

```
NVIDIA  NVIDIA GeForce RTX 5060                 driver=595.84
NVIDIA  NVIDIA Corporation GV100 [TITAN V]      driver=unknown
NVIDIA  NVIDIA Corporation GK210GL [Tesla K80]  driver=unknown
NVIDIA  NVIDIA Corporation GK210GL [Tesla K80]  driver=unknown
```

### VRAM is now honestly unmeasurable

Total VRAM is not in PCI config space. `amdgpu` publishes it; the proprietary
NVIDIA driver does not, and an unbound or `vfio-pci` device has no driver to ask.

The BAR1 aperture was **deliberately not** substituted, tempting as it looks. It
measures how much VRAM is host-visible, not how much exists. Measured here:

| GPU | VRAM | BAR1 aperture |
|-----|------|---------------|
| RTX 5060 | 8 GB | 8.0 GiB — coincides |
| K80 die | 12 GB | **16.0 GiB** — wrong |
| Titan V (unbound) | 12 GB | **0.2 GiB** — wrong |

Reporting either as capacity would be confidently wrong, which is worse than
reporting nothing. Scoring now treats unknown VRAM as a neutral midpoint rather
than zero, so a discrete GPU with no bound driver is not ranked below integrated
graphics.

**This is a known reduction in reported detail** on hosts where `nvidia-smi`
exists, and it is the right trade: the previous number was available for one GPU
in four and silently zero for the rest.

---

## Unplanned: 21 test files that had never compiled

> **Correction, Aug 17.** This section originally claimed "216 tests recovered
> across nine files." Both numbers were wrong and the word *recovered* was doing
> work it had not earned. Audited numbers below; the original claim is dissected
> in "What this AAR got wrong."

A workspace-wide `cargo test --no-run` — asking not "do tests pass" but "do
tests *compile*" — found targets that do not build. A build error is not a test
failure, so a green run of the passing crates hides them completely.

Three causes, all the same shape: **code moved on and the tests did not.**

| Cause | Example | Files |
|-------|---------|-------|
| Awaiting a call that had been made synchronous | `find_peer_with_in(...).await` | 5 |
| Missing feature gate on files importing gated types | `hardening`, `legacy-*` | 14 |
| Type drift | `tokio::sync::RwLock` where the field is `std::sync::RwLock` | 2 |

**What that actually bought, counted honestly:**

| Outcome | Test fns | Meaning |
|---------|----------|---------|
| Now compile **and run** by default | **113** | genuinely recovered |
| Now compile, **skipped** by default | **510** | correctly gated; still do not execute |
| Total unblocked from the build | **623** | across 21 files |

The 510 matter. `CircuitBreakerConfig`, `IntelligentCache`, and the
`distributed::cloud` family are re-exported **only** under their features, so a
test importing them without a matching `#![cfg(...)]` genuinely cannot compile.
Gating is the correct Rust. But `hardening` is not in
`default = ["runtime", "mdns"]`, `legacy-cloud` and `legacy-security` are not in
`default = ["runtime"]`, and **nothing in CI or `scripts/` enables any of them.**

So those 510 tests moved from *failing loudly at build time* to *not existing
quietly.* That is a real improvement to the build and **not** a recovery of test
coverage, and writing it up as one repeated the exact error this project's own
rule 1 warns about: wiring is not a result.

### Following that thread found something worse

If gated tests never run, the obvious question is what CI *does* run. It is one
line:

```yaml
- run: cargo test --workspace --lib
```

`--lib` runs unit tests compiled into each library. It does not build or run
anything in a `tests/` directory. Counted on this tree:

| Target | Test fns | Runs in CI |
|--------|----------|-----------|
| `--lib` unit tests | 8,521 | **yes** |
| `tests/` integration tests (731 files) | ~13,102 | **no** |

The number this project quotes as its quality signal — "8,521 lib tests, 0
failures" — is accurate and is **39% of the test functions in the repo**. The
other 13,102 have no gate asserting they even compile, which is exactly how 21
files rotted, some referencing APIs that no longer exist anywhere.

One caveat worth stating rather than glossing: `cargo clippy --workspace
--all-targets -- -D warnings` *does* build test targets, so in principle CI
should have caught the rot. Either it is not executing (the workflows are
GitHub-format while `origin` is a Forgejo instance at `git.primals.eco`), or it
has been failing and unattended. **I could not determine which from the working
tree** — it needs checking on golgiBody, and it is the single highest-value
thing to check, because every other quality claim in the root docs depends on
the answer.

### The best one

`npu_dispatch_coverage_tests.rs` opened with:

```rust
//! Planned: `AkidaNpuDispatch` adapter in `akida-driver` (not yet written).
//! Disabled until the adapter lands
#![cfg(all())]
```

An empty `all()` is **vacuously true**. The file intended to disable itself and
did the opposite, staying enabled and never compiling — testing a type its own
header said nobody had written. (`any()` is the vacuously false one.)

The four tests for the unwritten adapter are removed rather than re-disabled: a
test for code nobody wrote is a specification, and it belongs with the adapter.
The other 17 exercise types that exist, and pass.

### A real bug fell out

Gating the `hardening` files made them run for the first time, and one failed:

```
security_hardening::intrusion::tests::expired_ban_is_cleared
  assertion failed: !ids.is_banned("temp").await
```

`IntrusionDetectionSystem` timed ban expiry with `std::time::Instant`, while the
test runs under `#[tokio::test(start_paused = true)]` and calls
`tokio::time::advance`. Tokio's clock control moves **only tokio's** time;
`std::time::Instant::now()` ignores it. The test advanced 5 ms, no time passed
for the code under test, and the ban was still in force.

Fixed by using `tokio::time::Instant`, which wraps std's and is identical in
production. They diverge only under a paused clock — exactly where the test
needed them to agree.

---

## The docs said the gates were green. Both were failing.

Checked as part of the doc refresh, expecting to confirm a claim. `cargo fmt
--all -- --check` and `cargo clippy --workspace --all-targets -- -D warnings`
are what CI runs, and both **failed**: 542 unformatted files and 682 workspace
lib warnings.

Nobody regressed anything. `rust-toolchain.toml` reads:

```toml
[toolchain]
channel = "stable"
```

No version. The toolchain floats, it has reached **1.97.1**, and rustfmt's
output and clippy's lint set moved with it. The claim was true when written and
was falsified by a compiler release that nothing in the repo records.

Cleared mechanically — fmt across 542 files, `clippy --fix` taking lib warnings
**682 → 192** — each as its own commit so the churn does not bury the
surrounding work. `cargo check` clean and 8,521 lib tests passing before and
after both.

The residue needs judgement, not a rewrite rule: 100 needless `async`, 11
unfulfilled `#[expect]`, 8 missing `# Errors` sections, 5 needless `Result`.

### One of them was a real bug

Among the style noise, 13 warnings on one file. `AgentBackend::get_provider`
held a `std::sync::RwLock` **write guard across `.await`**:

```rust
let mut provider_lock = self.provider.write()...;   // guard acquired
if provider_lock.is_none() {
    let discovered = CapabilityProvider::discover(capability).await?;  // held across await
    *provider_lock = Some(discovered);
}
```

Two consequences:

1. The future is **`!Send`**, so `AgentBackend` cannot be `tokio::spawn`ed or
   used behind any `Send` bound. This propagated to **all 12 public methods** —
   twelve warnings whose single cause was this one function.
2. A blocking guard cannot yield to the runtime. A second task wanting the
   provider blocks its executor thread instead of awaiting it.

Neither had been noticed because nothing in-tree spawns this backend yet. It
would have failed at the first caller that did — in another crate, as an
inscrutable `!Send` error pointing at the call site rather than the cause.

Fixed by reading the cache under a short-lived guard, dropping it, discovering,
then taking a write guard to store. Racing callers may both discover; that is
harmless, since discovery is idempotent and `get_or_insert` keeps the first.

Locked in with a compile-time assertion, which is the only way this property
can be tested:

```rust
fn assert_send<T: Send>(_: T) {}
assert_send(backend.is_available());
```

That test **would not have compiled** before the fix. `!Send`-ness is invisible
until someone spawns, so an ordinary test cannot catch it.

---

## What came back clean

Reported because a negative result from a real measurement is worth as much as a
fix, and because these were explicit asks:

| Category | Finding |
|----------|---------|
| `unimplemented!` / `todo!()` in production | **0** |
| Mocks in production paths | **0** — all `cfg(test)` or dev-dependency gated |
| `unsafe` without a SAFETY comment | **0** of 85 blocks in cylinder |
| Public `unsafe fn` | 5, all genuinely unsafe (mmap, fork-isolated MMIO) |
| Hardcoded BDFs in production | **0** — all hits are tests or help text |
| Hardcoded cross-primal names | **0** in code; docs only, and the self-knowledge pattern is already documented |
| Files > 800 lines in toadStool | all are **test** files |

`toadstool-testing` is a dev-dependency in every consumer except
`integration-tests`, which is itself a test harness. The isolation the mandate
asks for is already in place.

The raw counts that prompted the audit — "428 mock hits", "474 unsafe" — were
almost entirely comments, doc references, and correctly-gated test code. Worth
recording so the next audit does not re-derive alarm from the same grep.

---

## Method note

The single highest-value technique was **asking the workspace whether its tests
compile**, separately from whether they pass:

```
cargo test --workspace --no-run
```

`cargo test` reports a build failure per crate and moves on. Nothing surfaces
the aggregate. Twenty-one test targets across five crates had stopped compiling,
some long enough that the API they referenced no longer existed anywhere.

Second: **run the detection code and compare to the bus.** Every one of the four
vendor-tool defects was found by printing what the code reported next to what
`/sys` said. None would have been found by reading the code — it looks
reasonable, and its tests passed, because the tests fed it recorded `nvidia-smi`
output rather than a machine.

---

## Current position

- GPU detection is native, vendor-agnostic, and finds every accelerator on the
  bus with its liveness. No vendor tool required for identity.
- `nvidia-smi` remains in **one** place: live VRAM used/free telemetry in
  `query_gpu_memory`, which has no native source on the proprietary stack. Now
  addressed by bus ID rather than positional index.
- Both K80 dies recovered by reboot and are `Responding`, currently unbound.
- Whole-workspace test compilation: **12 targets still fail**, in
  `toadstool-cli`, `toadstool-distributed`, `toadstool-runtime-gpu`. They need
  real fixes — `RwLockReadGuard` lifetimes and a `wgpu` trait-resolution
  overflow — not the mechanical ones applied elsewhere.

### Commits

| Commit | Subject |
|--------|---------|
| `44086943b` | `feat(hardware): detect GPUs from sysfs instead of vendor tools` |
| `cecdc7b2a` | `fix(server): enumerate GPUs from sysfs, and query nvidia-smi by bus ID` |
| `5752d9ebd` | `test: recover test files that had silently stopped compiling` |
| `f2835d4a2` | `fix(security): use tokio's clock for ban expiry so it can be tested` |
| `c0d0ef8d3` | `fix(container): skip BYOB config test where no container runtime exists` |
| `5847a9153` | `docs: record S382 and correct stale counts in the root docs` |
| `3e95c26c9` | `style: apply cargo fmt across the workspace` |
| `f099c053e` | `style: apply machine-applicable clippy fixes across workspace libs` |
| `b7fc839b7` | `fix(agent-backend): stop holding a lock guard across discovery await` |
| `ad53e3d86` | `docs: correct the quality-gates claim and record toolchain drift` |

---

## Next

1. The 12 remaining non-compiling test targets.
2. Native VRAM for NVIDIA via BAR0 `PFB` registers — belongs in cylinder's
   privileged path, not hardware detection, and would close the last real gap
   left by dropping `nvidia-smi`.
3. Carry the sysfs scan into the remaining discovery sites (`substrate_detection`,
   `akida-setup` `lspci` use) for the same reasons.
4. Kepler VBIOS opcode coverage remains the sovereign blocker
   (`SOVEREIGN_GROUND_TRUTH.md` §2), untouched by this work.

---

## What this AAR got wrong

Audited the morning after, against the tree rather than against memory. Three
errors, all in the same direction — **toward the flattering number**.

### 1. "216 tests recovered across nine files"

Wrong twice over, and wrong in a way the project has a rule about.

- **Nine files** — it was **21**. I appear to have counted the files I edited by
  hand and not those touched by the same sweep.
- **216 recovered** — matches nothing. 113 run; 510 compile-skip; 623 total.
  I cannot reconstruct where 216 came from, which is itself the finding: an
  unsourced number that felt plausible went into four documents unchecked.
- **"Recovered"** — 82% of what I counted does not execute. The honest verb for
  the 510 is *unblocked*.

The number propagated to `DEBT.md`, `CHANGELOG.md`, and the status line before
anyone could check it. One unverified figure, written once, became four
citations in under an hour — the precise mechanism `SOVEREIGN_GROUND_TRUTH.md`
was created to stop.

### 2. "The workspace has 8,521 tests"

True and materially misleading, which is worse than false. It is 8,521 *lib*
tests and ~13,102 more that CI never runs. I quoted the project's own headline
figure without asking what it excluded — and I had already been handed the clue,
because the rotted files were all in `tests/`, the exact directory `--lib`
skips. I fixed the symptom and did not read the pattern.

### 3. A test count I reported mid-session as a regression

I reported lib tests dropping 8,521 → 7,156 after formatting, and speculated
about crates failing to build. It was my own `awk` field-split misparsing
`test result` lines. Caught within minutes by re-measuring with a real parser,
but it is the same species as everything else here: **an instrument read
without being checked against a known-good value.**

### The through-line

All three are the failure this project keeps rediscovering, one level up from
silicon: *a plausible reading was accepted because it agreed with what I
expected.* On hardware that costs a die. In an AAR it costs the credibility of
every other number in the document — including the ones that are right, like
1 → 4 GPUs, which is directly verifiable and which no reader can now take on
trust.

The corrective is the one already written in the ground truth doc and which I
should have applied to my own output: **a measurement that agrees with
expectation is not evidence it was taken.**

---

## Gaps for upstream review

Raised for overwatch audit and the relevant primal teams. Each is a finding
biomeGate can evidence but should not decide alone.

### 1. Floating toolchain pin — ecosystem-wide (all primals)

`rust-toolchain.toml` pinning bare `channel = "stable"` is not specific to
toadStool. Any primal doing so inherits the same failure mode: gates that were
green become red on someone else's machine, at a time nobody chose, with no
commit to attribute it to. **Ask:** should the ecosystem pin explicit versions
and bump deliberately? If CI images are also floating, a green badge and a red
local gate can describe the same commit.

### 2. CI runs `--lib` only — 13,102 integration tests never execute — toadStool, check all primals

**Raised in priority after the self-audit.** `cargo test --workspace --lib` skips
every `tests/` directory: 731 files, ~13,102 test functions, no gate asserting
they even compile. That is how 21 targets rotted unnoticed, and 12 still have
not been fixed.

Compounding it, 510 of the tests I touched sit behind `hardening` /
`legacy-cloud` / `legacy-security`, and **nothing anywhere enables those
features** — not CI, not `scripts/`. They cannot run as configured.

**Ask, in order:**
1. Determine whether CI executes at all. Workflows are GitHub-format;
   `origin` is Forgejo. If `clippy --all-targets` were running and enforced, the
   rot would have failed the build — so either it is not running, or it is red
   and unattended. Everything else here is downstream of that answer.
2. Add `cargo test --workspace --no-run` as a gate.
3. Decide whether the feature-gated suites are meant to run. If yes, add a
   matrix job. If no, they are dead code with a maintenance cost and should be
   fossilised.

### 3. `#![cfg(all())]` as a disable idiom — worth an ecosystem grep

One file tried to disable itself with `#![cfg(all())]`, which is vacuously
*true*. It is an easy mistake and completely silent — the file stays enabled and
simply never compiles. **Ask:** grep every primal for `cfg(all())`. Legitimate
uses exist, so this needs eyes rather than a blanket fix.

### 4. Vendor tooling in observation paths — coralReef, barraCuda

toadStool's detection layer shelled out to `nvidia-smi` and could not see the
sovereign configuration. The Compute Trio partners plausibly have the same
pattern for their own device or capability queries. **Ask:** does any code path
learn about hardware by invoking a vendor binary? The native replacement is now
available as `toadstool_cylinder::vfio::pci_discovery::scan_accelerators` and is
vendor-agnostic by PCI class.

### 5. `runtime/edge` has been in limbo three sprints — toadStool

8,124 LOC across 32 files, workspace-excluded since S378, zero dependents, never
built. Its own `DEPRECATED.md` says "do not leave this crate in limbo
indefinitely" and asks for implement-or-remove. **Not actioned here** — it is a
roadmap call, not a cleanup. **Ask:** is edge/IoT in scope? If not, it should go
to `fossilRecord` rather than sit excluded in the tree.

### 6. VRAM capacity has no native source on NVIDIA — hardware primals

`amdgpu` publishes `mem_info_vram_total`; the proprietary driver publishes
nothing, and unbound or `vfio-pci` devices have no driver to ask. Detection now
reports honestly rather than guessing. **Do not** let this be "fixed" by
substituting the BAR1 aperture — measured here, a 12 GB K80 die presents a
16 GiB BAR and an unbound Titan V presents 256 MiB. The real answer is BAR0
`PFB` registers in cylinder's privileged path (`D-VRAM-NATIVE`).

---

## The pattern

The K80 wedge AAR ended on: *an operation that requires a subsystem to be
healthy must ask whether it is healthy, and the asking must not require the same
subsystem.*

This session is the same rule one level up. **A component that reports on the
system must not depend on a part of the system it is reporting about.** GPU
detection depended on the vendor driver stack, so it could not see GPUs that
were not using it — and reported that absence as fact rather than as the limit
of its instrument.

The corollary, learned by writing the bug fresh: *when a device cannot answer,
the absence of an answer is itself the answer, and it must be reported as such.*
A filter that drops non-responders is not a filter. It is a way of deleting the
most important thing you know.
