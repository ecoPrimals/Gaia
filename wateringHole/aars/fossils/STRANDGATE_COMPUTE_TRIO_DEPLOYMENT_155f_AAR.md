# AAR: strandGate Compute Trio Deployment — Wave 155f

**Date**: Jul 28, 2026 | **Wave**: 155f | **Gate**: strandGate
**Reporter**: strandGate overwatch
**Scope**: Full gate bootstrap (Phase 0–3) + Compute Trio deployment

---

## TIMELINE

1. Phase 0: SSH connectivity to Forgejo — verified (key `strandGate-wave152a`)
2. Phase 1: Sync 42 repos from Forgejo — 7 repointed from GitHub, 3 cloned fresh
3. Phase 2: WireGuard mesh (10.13.37.10) + Tower Atomic (beardog + songbird + skunkbat)
4. Phase 3: Compute Trio deployment — barraCuda, coralReef, toadStool

---

## WHAT WENT RIGHT

- Forgejo SSH worked first try — no connectivity issues from strandGate
- All 15 primals + 27 other repos synced cleanly (zero merge conflicts)
- WireGuard peered with golgiBody on first attempt (36ms RTT)
- Tower Atomic started cleanly — beardog healthy, skunkbat healthy, songbird IPC up
- barraCuda (source-built) discovered RTX 3090 immediately via wgpu Vulkan
- GPU stack validation passed: matmul_identity, tensor_roundtrip, eigenvalues
- SHADER_F64 enabled on RTX 3090 (14/9 builtins native)

---

## WHAT WENT WRONG

### P0: musl genomeBins Cannot Access GPU

**Impact**: Any gate with GPU hardware cannot use depot genomeBins for compute primals.

**Root cause**: The depot pipeline on sporeGate cross-compiles all genomeBins
for `x86_64-unknown-linux-musl` (static linking). The musl ABI cannot `dlopen`
the system's glibc-linked Vulkan ICD (`libGLX_nvidia.so.0`). wgpu requires
dynamic loading of the Vulkan driver, which is always glibc on NVIDIA systems.

**Symptom**: barraCuda from depot starts and runs, but reports:
```
no compute device available (GPU, CPU software rasterizer, and sovereign IPC all unavailable)
running degraded (cpu-shader only)
```

**Fix applied**: Built barraCuda from source on strandGate using native glibc
toolchain (`stable-x86_64-unknown-linux-gnu`, Rust 1.92.0). GPU lit up immediately.

**Recommended action**: Add a glibc target to the depot pipeline for compute
primals (at minimum: barraCuda, coralReef, toadStool). The musl target remains
correct for Tower Atomic (no GPU needed) and Nest primals. Possible approach:
- `x86_64-unknown-linux-musl` — Tower, Nest, utility primals (current)
- `x86_64-unknown-linux-gnu` — Node/compute primals (new)

This makes the depot pipeline aware of composition tiers: Tower primals are
portable (musl), compute primals need host GPU drivers (glibc).

### P1: coralReef Compile Errors on main

**Impact**: Cannot build coralReef from source on any gate.

**Root cause**: 10 compile errors on `main` branch with Rust 1.92.0:
- `compile_timeout` not found in `newline_jsonrpc` module (5 instances)
- `beardog_socket` not found in `config` module
- Private function access: `discover_by_capability`, `discover_security_socket`
- Type inference failures (2 instances)

These look like API changes in dependencies (possibly songBird or bearDog IPC
crates) that weren't propagated to coralReef after the IPC merge resolution
commit (`8ebd97d`).

**Fix**: eastGate needs to update coralReef's imports and visibility to match
current IPC API. The depot binary (built on sporeGate before the API change)
still works.

### P1: toadStool Has No Server Mode

**Impact**: Cannot deploy toadStool as a standing IPC service.

**Detail**: toadStool is a biome orchestrator — its commands are `run`, `up`,
`down`, `ps`, `validate`, `init`, `capabilities`. There is no `server`
subcommand. It requires a `biome.yaml` manifest to run workloads.

The `capabilities` subcommand ran but reported "No platforms detected yet"
(same musl/glibc issue — the capabilities binary also needs Vulkan access).

**Recommended action**: Document how toadStool fits into the Node Atomic
deployment model. Is it a systemd service with a default biome? Does it
need a manifest per gate? The current startup blurb assumes all primals
have a `server` subcommand — toadStool is architecturally different.

### P2: WireGuard DNS Hijacks All Resolution

**Impact**: `depot.primals.eco` and all public domains fail to resolve.

**Root cause**: The wg0.conf template has `DNS = 10.13.37.1`. When wg-quick
brings up the interface, systemd-resolved assigns `~.` (catch-all) domain
routing to wg0, sending ALL DNS queries to golgiBody (10.13.37.1). golgiBody's
DNS does not resolve public domains like `depot.primals.eco`.

**Fix applied**: `resolvectl dns wg0 ""` and `resolvectl domain wg0 ""` to
clear the override. Public DNS resumed via LAN resolver (192.168.4.1).

**Recommended action**: Remove the `DNS =` line from the wg0.conf template
in the startup blurb and enrollment scripts. If inner-membrane DNS is needed
later, scope it to `~primals.local` instead of catch-all.

---

## DIVERGENCES FOUND

### Repo Remote Divergences (7 repos)

These repos on strandGate still pointed at GitHub, not Forgejo:
- `gardens/foundation` (also cross-wired with projectFOUNDATION)
- `gardens/projectNUCLEUS`
- `springs/groundSpring`, `healthSpring`, `neuralSpring`, `wetSpring`
- `infra/benchScale`

All had **incompatible commit histories** — the GitHub clones could not
fast-forward from Forgejo (error: "shallow roots are not allowed to be
updated"). These were GitHub clones from earlier waves that diverged when
repos were re-imported to Forgejo.

**Fix applied**: Fresh `git clone` from Forgejo for all 7.

### Missing Repos (3)

- `gardens/metalForge` — cloned, has content
- `springs/coralForge` — cloned, **empty repo** on Forgejo
- `infra/fossilRecord` — cloned (10,905 files). Was a non-git local directory.

### Naming / Layout

- `gardens/projectFOUNDATION` is a symlink → `gardens/foundation` (same repo)
- No case-mismatched directories found
- No `master` branches found
- Extra top-level dirs: `sort-after/`, `fossilRecord/` (stale local copies)
- `infra/testing-secrets` is local-only (contains secrets, not a git repo)

### Dirty Files (pre-existing, untracked)

| Repo | Files |
|------|-------|
| airSpring | 3 files: `barracuda/src/data/{biomeos_provider,nestgate,songbird}.rs` |
| plasmidBin | 1 dir: `biomeos/` |

### Binary Version Delta

skunkBat depot binary was v0.2.8 (fetched Jun 9). Current is v0.2.18.
Tower genomeBins on strandGate were 6 weeks stale. Refreshed from depot.

### wave.toml Note

Jelly strings count diverges between ECOSYSTEM_BLURB.md (6/8, includes J8)
and the startup blurb (6/7, no J8). J8 (key enrollment portal) is new.

---

## ECOSYSTEM OBSERVATIONS

1. **The gate bootstrap works.** A gate can go from bare hardware to live
   primals in a single session. The four-phase flow (connectivity → sync →
   enrollment → deploy) is sound.

2. **The musl/glibc split is the biggest deployment gap.** It's invisible
   until you try to run compute workloads on real GPU hardware. Tower Atomic
   works perfectly from musl binaries (no GPU needed), which masks the issue.

3. **songbird's TCP 7700 + UDS IPC model works.** Capability symlinks
   (btsp.sock → beardog, security.sock → skunkbat, math.sock → barracuda,
   shader.sock → coralreef) create a clean service discovery surface.

4. **Fresh gates get a lot of legacy BTSP warnings.** Every 10 seconds,
   skunkBat/coralReef receive non-BTSP connection probes. These are harmless
   but noisy. Consider rate-limiting the warning log.

---

## ACTION ITEMS FOR EASTGATE

| # | Priority | Action | Owner |
|---|----------|--------|-------|
| 1 | **P0** | Add glibc target to depot pipeline for compute primals | sporeGate build |
| 2 | **P1** | Fix coralReef compile errors on main (10 errors, Rust 1.92.0) | eastGate coralReef |
| 3 | **P1** | Document toadStool deployment model (biome.yaml, Node Atomic) | eastGate toadStool |
| 4 | **P2** | Remove `DNS =` from wg0.conf template + enrollment scripts | eastGate songBird/cellMembrane |
| 5 | **P2** | Add Forgejo remotes for 7 stale GitHub-only repos across gates | eastGate overwatch |
| 6 | **P3** | Rate-limit legacy BTSP connection warnings in skunkBat/coralReef | eastGate |
| 7 | **P3** | Add hostname check to enrollment script | cellMembrane |
| 8 | **P3** | Clone coralForge content or archive empty repo | eastGate |

---

*strandGate is online. Tower Atomic live. barraCuda running on RTX 3090
(source-built, GPU verified). coralReef running (depot binary). toadStool
awaiting biome manifests. Main blocker for full Node Atomic: musl genomeBins
can't access GPU. eastGate action required on depot pipeline + coralReef
compile fix + toadStool documentation.*
