# AAR: grapheneGate Full Deployment — Wave 108 (13/13 ALIVE)

**Date**: 2026-06-10
**Team**: primalSpring + grapheneGate deployment team on eastGate
**Device**: Pixel 8a (44251JEKB04957), GrapheneOS, aarch64-unknown-linux-musl
**Composition**: `--composition full` (all 13 NUCLEUS primals)
**Result**: **13/13 primals ALIVE on TCP**, validated via pgrep + TCP probe + JSON-RPC health
**Prior AAR**: Wave 107 (11/13) — `archive/wave107/AAR_GRAPHENEGATE_WAVE107_FULL_DEPLOY_11_OF_13_JUN10_2026.md`

---

## Executive Summary

Third-generation grapheneGate deployment. Progressed from Wave 105b (6/13) → Wave 107 (11/13) → **Wave 108 (13/13)**. All upstream blockers resolved: CR-TARPC-01 (coralReef), BM-UDS-01 (biomeOS), NG-DOWNCAST-01 (nestGate). aarch64 depot rebuilt locally on eastGate via `cargo build --target aarch64-unknown-linux-musl` (not `cross`/Docker). coralReef required a separate local rebuild because `build-primal.sh` produced a stale binary due to staging directory caching. All 13 primals confirmed alive on device with TCP transport.

**This is a first-solution deployment. It works, but it is not yet guideStone-grade.** This AAR catalogs what must be abstracted and evolved to achieve deterministic, reproducible, topology-agnostic deployment.

---

## What Worked

### 1. All 13 Primals Running on TCP

| Primal | Port | Protocol | Health Response | Bind Mode |
|--------|------|----------|-----------------|-----------|
| beardog | 9100 | JSON-RPC + abstract socket | `alive` | fallback (abstract UDS + TCP) |
| songbird | 9200 | HTTP REST | `200 OK` | N/A (HTTP-only) |
| skunkbat | 9140 | JSON-RPC | `ok` | `--no-uds` |
| toadstool | 9400 | JSON-RPC | `ok` | fallback |
| barracuda | 9740 | JSON-RPC | `alive` | `--no-unix` |
| coralreef | 9730 | JSON-RPC | `ok` | tcp_only (tarpc skipped) |
| nestgate | 9500 | JSON-RPC | `healthy` | tcp_only (`NESTGATE_SOCKET=""`) |
| rhizocrypt | 9601 | TCP alive | process alive | fallback |
| loamspine | 9700 | JSON-RPC | `ok` | fallback |
| sweetgrass | 9850 | JSON-RPC | `ok` | fallback |
| biomeos | 9800 | JSON-RPC | `ok` | tcp_only |
| squirrel | 9300 | JSON-RPC | `ok` | fallback |
| petaltongue | 9900 | TCP alive | process alive | fallback + TRANSPORT_ENDPOINT |

### 2. Local Cross-Compilation Works

eastGate (x86_64) successfully cross-compiled all 14 aarch64 binaries using:
```
cargo build --release --target aarch64-unknown-linux-musl
```
No Docker/`cross` required. Prerequisites: `rustup target add aarch64-unknown-linux-musl`, `lld`, `gcc-aarch64-linux-gnu`, `musl-tools`.

Total build time: ~21 minutes for 13 primals via `build-primal.sh --all`. Individual rebuild (coralReef alone): 48 seconds.

### 3. Upstream Fixes All Landed and Work

| Fix | Commit | Behavior on grapheneGate |
|-----|--------|------------------------|
| CR-TARPC-01 | coralReef `b1ec1f4` | `skip_tarpc=true` when PRIMAL_BIND_MODE=tcp_only. tarpc UDS bind skipped entirely. |
| BM-UDS-01 | biomeOS v4.20 `d35c943e` | Neural API skips UDS bind on tcp_only. TCP server starts cleanly. |
| NG-DOWNCAST-01 | nestGate `7c3fe9a6` | `is_platform_constraint()` walks full error chain. NESTGATE_SOCKET="" workaround still deployed. |

### 4. deploy_pixel.sh 6-Phase Flow

The script's structure is sound:
- Phase 1: Binary verification (13/13 present, correct arch)
- Phase 2: ADB push (~150MB, <2s at 160-400 MB/s over USB)
- Phase 3: Startup script generation with per-primal env overrides
- Phase 4: Sequential startup with sleep intervals
- Phase 5: ADB port forwarding
- Phase 6: TCP reachability probe

### 5. BLAKE3 Checksum Verification

All binaries verified against `checksums.toml` before deployment. This prevented deploying an unverified depot.

---

## What Didn't Work

### 1. build-primal.sh Staging Cache Poisoning (CRITICAL)

**Symptom**: coralReef binary deployed to device did NOT have the CR-TARPC-01 fix (`b1ec1f4`), despite that commit being the tip of GitHub main.

**Root Cause**: Two `build-primal.sh` runs occurred. The first was killed mid-build. The staging directory (`/tmp/primalspring-deploy/primals/aarch64-unknown-linux-musl/`) persisted between runs. When the second run built coralReef, the staged binary from the first (killed) run was still present. The staging code checks:
```bash
if [[ ! -f "$out_dir/$dest_name" ]]; then
    cp "$bin" "$out_dir/$dest_name"
fi
```
This `if ! -f` guard means a stale binary from a previous run is never overwritten. The second run's fresh coralReef binary was silently discarded.

**Evidence**: The deployed binary had no `"skipping tarpc server"` string (checked via `strings | grep`). The locally-rebuilt binary from the same source code did.

**Impact**: coralReef crashed on device with the same tarpc EACCES error that the upstream fix was supposed to prevent. Required manual diagnosis and rebuild.

**Fix Required (build-primal.sh)**:
1. Clean staging directory at start of `--all` run: `rm -rf "$STAGING"`.
2. Or: always overwrite staged binaries (remove the `! -f` guard).
3. Or: timestamp-compare staged vs freshly-built.

**Determinism lesson**: Mutable staging directories between interrupted runs violate reproducibility. The build pipeline must be idempotent: same inputs → same outputs, regardless of previous interrupted runs.

### 2. build-primal.sh ELF Detection Failure (5/13 Primals)

**Symptom**: `file "$bin" | grep -q "ELF"` returned false for 5 aarch64 binaries (toadstool, barracuda, coralreef, nestgate, petaltongue), causing false FAIL reports.

**Root Cause**: The `file` command on x86_64 inconsistently identifies aarch64 ELF binaries. For statically-linked musl binaries, some are detected as `ELF 64-bit LSB executable, ARM aarch64`, others are not. The inconsistency correlates with binary size and section layout, not correctness.

**Impact**: The script reported 5 FAILs when all 5 binaries compiled successfully. Confusing diagnostic output.

**Note**: Despite the FAIL reports, the binaries WERE staged to the output directory (the ELF check happens after copy for some code paths). This is why the staging cache poisoning (issue #1) was masked — the stale binary was already in place, and the "FAIL" message didn't trigger a clear alert that something was wrong.

**Fix Required (build-primal.sh)**:
1. Use `readelf -h "$bin" 2>/dev/null` instead of `file`. It's more reliable for cross-arch detection.
2. Or: check for `!*.d && !*.rlib && executable` without ELF type check (already filtered by extension).
3. Report architecture of detected binaries for verification.

### 3. ADB Port Forwarding Collision (PB-FORWARD-01, recurring)

**Symptom**: `adb forward tcp:9800 tcp:9800` (biomeOS) fails with `Address already in use`.

**Root Cause**: FluidSynth (MIDI synthesizer) bound to local port 9800. `deploy_pixel.sh` doesn't check local port availability before forwarding.

**Workaround**: Manual forward on offset port `adb forward tcp:19800 tcp:9800`.

**Fix Required (deploy_pixel.sh)**:
1. Pre-check: `lsof -i :$PORT` before `adb forward`.
2. Auto-offset: if port occupied, try PORT+10000.
3. Report final port mapping table at end of deploy.

### 4. harvest.sh Naming Mismatch

**Symptom**: After building, `harvest.sh` looked for `beardog-aarch64-linux-musl` but staging contained `beardog-aarch64-unknown-linux-musl`. Zero binaries harvested.

**Root Cause**: harvest.sh uses `{primal}-{arch_short}` (e.g., `aarch64-linux-musl`) while build-primal.sh stages as `{primal}-{TARGET}` (e.g., `aarch64-unknown-linux-musl`). The `-unknown-` component is dropped by harvest's arch-shortening logic.

**Impact**: Automated harvest pipeline broken for aarch64. Manual binary copy required.

**Fix Required (harvest.sh)**: Normalize naming to use the full target triple, or make harvest look for both `{primal}-{target}` and `{primal}-{arch_short}`.

### 5. Per-Primal Startup Divergence in deploy_pixel.sh

**Symptom**: The deploy script has 13 separate `case` blocks with different env vars, flags, and bind strategies per primal. No two primals start the same way.

**Examples of divergence**:
- beardog: `--abstract --family-id --listen`
- songbird: `--port` only, plus `BEARDOG_SOCKET` env
- nestgate: `PRIMAL_BIND_MODE=tcp_only NESTGATE_SOCKET="" NESTGATE_JSONRPC_TCP=1 --dev --enable-http --listen --family-id`
- biomeos: `PRIMAL_BIND_MODE=tcp_only TRANSPORT_ENDPOINT=... BIOMEOS_BTSP_ENFORCE=0 --port --bind --btsp-optional`
- coralreef: `PRIMAL_BIND_MODE=tcp_only TRANSPORT_ENDPOINT=... --rpc-bind`
- barracuda: `--port --no-unix`
- skunkbat: `--port --no-uds`

**Impact**: Every primal is a snowflake. Adding a 14th primal requires reading the source code to determine which flags and env vars it needs. There is no standard startup contract.

---

## Evolution Gap Analysis: First Solution → guideStone Grade

### The Problem Statement

The current deployment works but violates the core principle: **the same NUCLEUS should deploy identically across every gate.** Today, deploying to grapheneGate requires:

1. Per-primal flag knowledge encoded in bash `case` blocks
2. Platform-specific env var overrides hand-tuned per primal
3. Manual build artifact verification and staging workarounds
4. Operator knowledge of which primals need `tcp_only` vs `fallback` vs `--no-uds`

A guideStone-grade deployment has none of these. The gate bootstrap command should be:
```
gate.bootstrap --gate grapheneGate --arch aarch64-unknown-linux-musl
```
And it should produce 13/13 alive, every time, with no human decisions.

### Gap 1: No Standard Primal Startup Contract

**Current state**: Each primal has its own CLI flags, env vars, and transport semantics. The knowledge of how to start each primal lives in `deploy_pixel.sh` case blocks and operator memory.

**Target state**: Every primal accepts a **standard startup envelope**:
```
$PRIMAL server \
  --bind-mode $PRIMAL_BIND_MODE \
  --port $PORT \
  --family-id $FAMILY_ID
```
All additional configuration flows through environment variables with standard prefixes (`PRIMAL_*`, `BIOMEOS_*`).

**What must change**:
- Primals that use `--abstract`, `--no-uds`, `--no-unix`, `--enable-http`, `--dev`, `--listen`, `--rpc-bind` etc. must converge on a common flag set.
- `PRIMAL_BIND_MODE` must be the single source of truth for transport selection across ALL primals.
- Primals must NOT require primal-specific flags to achieve basic TCP operation.

**Concrete upstream items**:
- beardog: `--abstract` should be auto-detected from bind mode, not a flag.
- nestgate: `--enable-http --dev --listen` should be default server behavior, not opt-in flags.
- biomeos: `--btsp-optional` should be inferred from environment (no BTSP provider available → degrade gracefully).
- coralreef: `--rpc-bind` should be just `--bind` (or implied from `--port`).
- barracuda/skunkbat: `--no-unix`/`--no-uds` should be replaced by `PRIMAL_BIND_MODE` reading.

### Gap 2: No Platform Capability Discovery

**Current state**: `deploy_pixel.sh` hardcodes knowledge that Android = tcp_only. Each primal is manually told which transport to use.

**Target state**: Primals auto-detect platform capabilities at startup:
```rust
let caps = PlatformCapabilities::detect();
// caps.uds_available = false  (Android SELinux)
// caps.tcp_available = true
// caps.abstract_sockets = partial
// caps.btsp_provider = None | Some(addr)
```

Transport selection flows from capabilities, not from environment variables set by an operator.

**What must change**:
- `is_platform_constraint()` becomes `PlatformCapabilities::detect()` — a positive capability model, not error-based detection.
- The result is published to a shared runtime context so other primals can adapt.
- `PRIMAL_BIND_MODE` remains as an override, but the default is auto-detection.

### Gap 3: Build Pipeline is Fragile

**Current state**: `build-primal.sh` clones from GitHub (shallow), builds, stages to a mutable temp dir, then `harvest.sh` copies with different naming conventions. Multiple failure modes:
1. Staging cache poisoning between interrupted runs
2. ELF detection fails for cross-compiled binaries
3. Harvest naming mismatch drops all binaries
4. No checksum verification of built binaries against expected hashes
5. No provenance tracking (which commit was built?)

**Target state**: Build pipeline is deterministic and verifiable:
```
membrane plasmid.build --target aarch64-unknown-linux-musl --all \
  --verify-checksum \
  --record-provenance \
  --clean-staging
```

**What must change**:
- `build-primal.sh` → Rust implementation in cellMembrane (`membrane plasmid.build`).
- Staging directory is ephemeral (created fresh, destroyed after harvest).
- Each built binary is checksummed and compared against `checksums.toml` expectations (or expectations are updated with provenance).
- Build provenance records: `{primal, commit_sha, target, timestamp, blake3}`.
- No shell-based ELF detection — use `object` crate or `readelf`.

### Gap 4: deploy_pixel.sh is Not Reusable Across Gates

**Current state**: The script is Android/Pixel-specific. It assumes ADB, `/data/local/tmp/`, `Toybox` shell, and specific process management semantics.

**Target state**: Gate deployment is topology-aware but uses a common engine:
```
gate.bootstrap --gate grapheneGate
```
Where `grapheneGate`'s gate profile specifies:
```toml
[gate.grapheneGate]
arch = "aarch64-unknown-linux-musl"
transport = "adb"           # how to reach the device
deploy_root = "/data/local/tmp/plasmidBin"
runtime_root = "/data/local/tmp/biomeos"
bind_mode = "tcp_only"      # platform constraint
capabilities = ["tcp", "abstract_socket_partial"]
```

The deployment engine reads the gate profile and generates the correct startup commands without per-primal case blocks.

### Gap 5: No Post-Deploy Validation Contract

**Current state**: Phase 6 does TCP reachability (connect to port). JSON-RPC health is a separate manual step.

**Target state**: Every primal exposes a standard health endpoint:
```json
{"jsonrpc":"2.0","method":"health","id":1}
→ {"result":{"status":"ok","primal":"beardog","version":"0.9.0","uptime_s":42}}
```
The deploy engine validates health for all primals and reports a structured result. Failed health → automatic restart with backoff.

**What must change**:
- All 13 primals must respond to `health` method on their primary transport.
- rhizocrypt and petaltongue currently don't respond to JSON-RPC health probes (different protocol or timeout). Must converge.
- songbird (HTTP) should also accept JSON-RPC health OR expose `/health` as standard.

### Gap 6: No Composition-Level Orchestration on grapheneGate

**Current state**: Primals start independently. No inter-primal discovery or wiring happens on device. biomeOS starts but doesn't orchestrate because it can't find other primals via UDS discovery.

**Target state**: The startup script (or a thin on-device launcher) handles:
1. Start primals in dependency order
2. Wait for each to be healthy before starting dependents
3. Inject discovery addresses (env or file) so primals find each other
4. Monitor for crashes and restart

This is what `nucleus_launcher` does on x86_64 gates. grapheneGate needs an equivalent — possibly the same binary cross-compiled, or a simpler version.

### Gap 7: BTSP Authentication Not Validated End-to-End

**Current state**: sweetGrass and petalTongue enforce BTSP on TCP. We confirmed they reject unauthenticated connections (correct behavior). But we haven't validated that BTSP handshake succeeds from a client.

**Target state**: beardog provides BTSP bootstrap keys → clients authenticate → sweetGrass/petalTongue accept authenticated requests.

This is the Tier 3 transport authentication layer. Without it, 2/13 primals are technically "alive but unreachable" for real workloads.

---

## Metrics: Wave-over-Wave Progression

| Metric | Wave 105b | Wave 107 | Wave 108 | Target |
|--------|-----------|----------|----------|--------|
| Primals running | 6/13 | 11/13 | **13/13** | 13/13 |
| TCP health responding | 4/13 | 9/13 | **11/13** | 13/13 |
| BTSP-enforced (alive) | 0 | 2/13 | 2/13 | 2/13 |
| Upstream blockers | 7 | 3 | **0** | 0 |
| deploy_pixel.sh issues | 3 | 1 | **1** | 0 |
| Build pipeline issues | N/A | 0 | **4** | 0 |
| Standard startup contract | 0/13 | 0/13 | 0/13 | **13/13** |
| Platform auto-detection | 0/13 | 0/13 | 0/13 | **13/13** |
| Deterministic deploy | No | No | No | **Yes** |

---

## Action Items

### P2: Immediate (unblock guideStone-grade)

| ID | Item | Owner | Acceptance |
|----|------|-------|------------|
| BUILD-CACHE-01 | build-primal.sh: clean staging dir before --all | cellMembrane | Interrupted runs cannot poison subsequent builds |
| BUILD-ELF-01 | build-primal.sh: replace `file | grep ELF` with readelf or cross-aware detection | cellMembrane | Zero false-negative ELF detections for aarch64 |
| HARVEST-NAME-01 | harvest.sh: normalize naming to full target triple | cellMembrane | harvest after build produces correct depot layout |
| PB-FORWARD-01 | deploy_pixel.sh: pre-check local port availability | cellMembrane | No silent ADB forward failures |

### P3: Standard Startup Contract (medium-term)

| ID | Item | Owner | Acceptance |
|----|------|-------|------------|
| CONTRACT-01 | Define standard primal server startup flags | primalSpring | RFC document: `--port`, `--bind-mode`, `--family-id` minimum |
| CONTRACT-02 | beardog: auto-detect abstract socket from bind mode | beardog team | Remove `--abstract` flag |
| CONTRACT-03 | nestgate: make `--enable-http` default in server mode | nestgate team | Remove opt-in flag |
| CONTRACT-04 | biomeos: infer `--btsp-optional` from environment | biomeOS team | Remove explicit flag |
| CONTRACT-05 | barracuda/skunkbat: replace `--no-unix`/`--no-uds` with PRIMAL_BIND_MODE | respective teams | Single transport control mechanism |
| CONTRACT-06 | coralreef: unify `--rpc-bind` with standard `--port --bind` | coralreef team | Common flag names |

### P3: Platform Capabilities (medium-term)

| ID | Item | Owner | Acceptance |
|----|------|-------|------------|
| CAPS-01 | `PlatformCapabilities::detect()` in primalSpring ecoPrimal | primalSpring | Positive capability model replaces error-based detection |
| CAPS-02 | Auto-bind-mode: primals select transport from capabilities | all primals | `PRIMAL_BIND_MODE` becomes override, not requirement |
| CAPS-03 | Abstract socket availability detection | primalSpring | Distinguish full/partial/none support |

### LOW: Infrastructure Evolution

| ID | Item | Owner | Acceptance |
|----|------|-------|------------|
| RUST-BUILD-01 | Port build-primal.sh to `membrane plasmid.build` (Rust) | cellMembrane | Reproducible builds, provenance tracking |
| GATE-PROFILE-01 | Gate profile TOML for topology-aware deployment | cellMembrane | `gate.bootstrap` reads profile, generates correct commands |
| LAUNCHER-01 | Cross-compile nucleus_launcher for aarch64 | primalSpring | On-device orchestration with dependency-ordered startup |
| HEALTH-01 | Standard health endpoint RFC for all primals | primalSpring | 13/13 respond to `{"method":"health"}` on primary transport |
| BTSP-E2E-01 | Validate BTSP handshake on TCP (sweetGrass + petalTongue) | primalSpring | Authenticated workloads on grapheneGate |

---

## Deployment Topology: Current vs Target

### Current (Wave 108 — first solution)

```
eastGate (x86_64)
  └─ operator runs: ./deploy_pixel.sh --composition full
       ├─ build-primal.sh --all --target aarch64 (21 min, fragile)
       ├─ manual staging verification + workaround for stale cache
       ├─ manual coralReef rebuild from local repo
       ├─ adb push (13 binaries, <2s)
       ├─ generated start_gate.sh (13 case blocks, per-primal snowflakes)
       ├─ adb shell sh start_gate.sh (sequential, sleep-based ordering)
       ├─ adb forward (12/13 auto, 1 manual offset)
       └─ manual health verification
```

### Target (guideStone-grade)

```
any gate (any arch)
  └─ operator runs: gate.bootstrap --gate grapheneGate
       ├─ reads gate profile (arch, transport, capabilities)
       ├─ membrane plasmid.build (Rust, clean staging, provenance)
       ├─ membrane plasmid.verify (BLAKE3 against checksums.toml)
       ├─ gate.deploy (transport-aware push: ADB/SSH/WAN)
       ├─ gate.start (standard contract, dependency-ordered, auto-restart)
       ├─ gate.forward (collision-aware port mapping)
       └─ gate.validate (structured health check, 13/13 required)
```

**Key difference**: zero per-primal knowledge in the deployment engine. All primal-specific behavior is encapsulated in the standard startup contract and platform capability detection.

---

## Conclusion

Wave 108 achieved the operational milestone: 13/13 primals alive on grapheneGate. The upstream ecosystem delivered all required fixes (CR-TARPC-01, BM-UDS-01, NG-DOWNCAST-01). The aarch64 cross-compilation pipeline works from eastGate.

But this is a **handcrafted deployment**, not a deterministic one. The path to guideStone-grade requires:

1. **Standard startup contract** — primals speak the same language
2. **Platform capability detection** — primals adapt without operator intervention
3. **Rust build pipeline** — reproducible, provenance-tracked, no shell fragility
4. **Gate profiles** — topology knowledge is data, not code
5. **On-device orchestration** — nucleus_launcher on aarch64

The first-solution deployment teaches us exactly where the abstractions need to go. Every workaround in `deploy_pixel.sh` is a signal pointing at a missing abstraction in the primal startup contract.

---

*Dissemination: overwatch → all gates via wateringHole temporal.cascade*
*Prior AAR: Wave 107 (11/13) archived at `archive/wave107/`*
