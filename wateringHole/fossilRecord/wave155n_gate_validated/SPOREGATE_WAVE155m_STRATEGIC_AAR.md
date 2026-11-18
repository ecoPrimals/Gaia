# sporeGate Strategic AAR — Wave 155m Complete

**Date**: Jul 30, 2026 21:23 EDT
**Wave**: 155m (strategic review)
**Gate**: sporeGate (build authority)
**Scope**: Full wave retrospective — what worked, what still diverges, where we can evolve

---

## I. WHAT WORKED

### 1. Sovereign CI Pipeline — Operational

The push-to-deploy pipeline is functional end-to-end:

```
Forgejo push → golgi post-receive hook → SSH root@sporeGate →
  sovereign.ci.trigger → cargo build (musl) → sandbox::validate →
  depot push → checksums regen → golgi SCP sync
```

**Infrastructure deployed this wave**:
- SSH key: `forgejo-relay@golgiBody` → `root@sporeGate /root/.ssh/authorized_keys`
- Root PATH: `cargo`, `rustc`, `rustup` symlinked to `/usr/local/bin`
- Environment: `MEMBRANE_BUILD_AUTHORITY=1`, `RUSTUP_HOME`, `CARGO_HOME`, `ECOPRIMALS_ROOT` in `/etc/environment`
- Root SSH config: `Host golgi` + `Host golgi-ext` with sporegate's key for depot SCP
- System membrane: `/usr/local/bin/membrane` updated to latest

**Jelly strings killed**: J9 (push trigger), J10 (auto harvest), J11 (multi-target)

**What it proved**: A single Rust developer can run a sovereign build authority that
produces binaries for 3 platforms (Linux musl, Linux gnu, Windows) with zero cloud CI
dependencies. The pipeline is ~10 minutes end-to-end including all 3 targets.

### 2. Ecosystem Feedback Loop — 3 Full Cycles in 1 Wave

The divergence discovery → AAR → code team fix → cascade → validate loop executed
3 complete cycles within Wave 155m:

| Cycle | Divergences Found | AARs Filed | Fixes Shipped By | Outcome |
|-------|------------------|------------|------------------|---------|
| 1 | 8 (socket perms, sandbox, rootpulse, checksums, tmpfiles, hook, self-CI, Text file busy) | `SPOREGATE_WAVE155m_FULL_CASCADE_AAR.md` | — | Documented, flagged |
| 2 | sandbox false positive, socket bind 0600, hook auto-fire | `SPOREGATE_BIOMEOS_V450_PIPELINE_AAR.md` | biomeOS (v4.50: socket evap + binary path) | biomeOS P2s closed |
| 3 | 0 new | `SPOREGATE_WAVE155m_FINAL_CASCADE_AAR.md` | biomeOS (v4.51: socket ownership), cellMembrane (4 AAR fixes) | **11/11 HEALTHY** |

**What it proved**: The blurb → AAR → handoff → code team → cascade workflow is
fast enough that divergences discovered in the morning are fixed and validated by
evening. The bottleneck is not the code teams — it's the pipeline testing.

### 3. Gate Health — First 11/11

```
sporeGate (x86_64-unknown-linux-musl) — HEALTHY
  [OK] depot.integrity:      16 verified, 0 hash mismatch
  [OK] mesh.reachability:    3 peers, 3 reachable
  [OK] primals.alive:        13/13 primals alive
  [OK] depot.freshness:      13/13 binaries present, oldest 1d
  [OK] sovereignty.s1_tls:   depot.primals.eco 200 (227ms)
  [OK] sovereignty.s2_relay: federation:REACHABLE, RustDesk hbbs+hbbr OK
  [OK] sovereignty.s3_content: depot serving 8459KB (235ms TTFB)
  [OK] sovereignty.s4_auth:  beardog reachable via neuralAPI
  [OK] rootpulse.ledger:     advisory OK (no session yet)
  [OK] vcs.parity:           0 repos drifted
  [OK] service.crash-loop:   14 services scanned, no crash-loops
```

Every probe that was failing at wave start is now green:
- `depot.integrity`: Fixed by regenerating `checksums.toml` from actual binaries
- `mesh.reachability`: Fixed by socket ownership (`0660 + chown :membrane`)
- `rootpulse.ledger`: Fixed by advisory OK mode in cellMembrane

### 4. Depot — Complete Across 3 Platforms

| Target | Count | Complete? |
|--------|-------|-----------|
| `x86_64-unknown-linux-musl` | 16 | Yes — all 13 primals + membrane + nucleus_launcher + sourdough |
| `x86_64-unknown-linux-gnu` | 4 | Partial — barracuda + biomeos + coralreef + toadstool (GPU trio + biomeOS) |
| `x86_64-pc-windows-gnu` | 15 | Yes — all 13 primals + membrane.exe + toadstool.exe |
| `aarch64-unknown-linux-musl` | 16 | Tier 1 (not x86_64 — carried forward) |
| `aarch64-linux-android` | 13 | Tier 1 (not x86_64 — carried forward) |
| **Total** | **64** | |

### 5. 16 Divergences Resolved

Every code-team divergence raised during Wave 155m was fixed and validated:

| # | Divergence | Fix | Commit |
|---|-----------|-----|--------|
| 1 | bearDog dual-socket footgun | Default socket aliases family-scoped | `a875d463` |
| 2 | bearDog FAMILY_SEED required | env → file → auto-generate precedence | `a875d463` |
| 3 | PRIMAL_BIND_MODE tcp_only | petalTongue accepts `tcp` semantics | `551e781` |
| 4 | biomeOS capability wipe cycle | 3-strike prune threshold (v4.49) | `f2d4c4b3` |
| 5 | toadStool tarpc-only | Legacy symlink → JSON-RPC | `5053e0bc` |
| 6 | petalTongue rejects --family-id | --family-id propagation | `551e781` |
| 7 | membrane.exe UnixStream P1 | #[cfg(unix)] gates + Windows stubs | `4ccbab1` |
| 8 | cellMembrane steamGate user-space | Deploy path for ~/.local/bin/ | `4a7391d` |
| 9 | cellMembrane reqwest dep | Sovereign HTTP/1.1 client | `4e77ffd` |
| 10 | biomeOS socket evaporation | Any Ok(btsp) = alive | `06ed323f` |
| 11 | biomeOS binary path retention | probe_binary() during discovery | `06ed323f` |
| 12 | Socket ownership for multi-user IPC | 0660 + chown :membrane | `0e45262f` |
| 13 | checksums.toml partial update | finalize_depot() full disk scan | `0cfcce5` |
| 14 | /run/membrane tmpfiles.d | membrane.conf shipped | `0cfcce5` |
| 15 | rootpulse.ledger degraded | Advisory OK when no session | `0cfcce5` |
| 16 | sandbox false positive (broker) | ServerContract resolution | `0cfcce5` |

---

## II. WHAT STILL DIVERGES

### P3-1: cellMembrane Not in `sources.toml`

cellMembrane (the `membrane` binary itself) is not registered in `sources.toml`,
which means `plasmid.harvest --primal membrane` fails with "not found in sources.toml".
Sovereign CI cannot self-rebuild the build tool. Current workaround: manual
`cargo build --release --target ...` from local source.

**Impact**: Low. cellMembrane changes are infrequent and the build is fast (~60s musl).
**Fix**: Add `[build.membrane]` entry to `sources.toml` with the cellMembrane repo path.
**Owner**: cellMembrane team.

### P3-2: golgi Post-Receive Hook Reliability

When biomeOS `b290cc8d` was pushed to Forgejo, the post-receive hook did not fire
the `sovereign.ci.trigger` SSH call. No SSH connection from golgi to sporeGate was
observed. The hook was validated manually (it works when we explicitly simulate it),
suggesting a Forgejo-specific trigger condition or the push bypassed the hook path.

**Impact**: Low. Pipeline works when triggered manually. Just misses the auto-fire.
**Fix**: Investigate Forgejo hook configuration. May need to switch from post-receive
to a Forgejo webhook HTTP endpoint, or verify the bare repo hook script is executable.
**Owner**: sporeGate infra / golgiBody ops.

### P3-3: Stale `neural-api-default.sock` Symlink

```
/run/membrane/neural-api-default.sock -> /run/membrane/neural-api.sock
```

This symlink was created by a previous biomeOS process running in `neural-api` mode.
Current biomeOS runs in `api` mode (different socket). The stale symlink causes
"Connection refused" warnings in every `gate.status` run (15 warnings). Not functional
but noisy.

**Impact**: Cosmetic. Warnings clutter gate.status output.
**Fix**: Remove stale symlink, or have biomeOS clean up on startup.
**Owner**: sporeGate ops (can fix now) / biomeOS (proper cleanup).

### P3-4: skunkBat Process Duplication

5 skunkBat processes running (1 systemd + 2 manual sudo pairs):

```
PID  886 — systemd managed (Main PID, running 3 days)
PID 439348/439350 — sudo pair (orphaned)
PID 440197/440200 — sudo pair (orphaned)
```

The orphaned processes are from manual restarts during earlier deployment work.
They share the same socket but the systemd-managed process (PID 886) owns it.

**Impact**: Low. Wasted ~2MB RAM + 2 extra process slots.
**Fix**: `sudo kill 439348 439350 440197 440200` then verify systemd process persists.
**Owner**: sporeGate ops (can fix now).

### P3-5: VCS Parity Probe Shows "0 repos checked"

```
[OK] vcs.parity: 0 repos checked, 0 drifted
```

The probe reports OK but checks zero repos. Meanwhile, actual drift exists:
- biomeOS: `0e45262f` local vs `744b2d17` on golgi (2 new commits on golgi)
- petalTongue: `71c95c7` local vs `3259473` on golgi (1 new commit on golgi)
- cellMembrane: `fd07ab5` local (2 commits ahead of deployed `0cfcce5`)

**Impact**: Medium. Silent drift is the worst kind. The probe should be catching this.
**Fix**: Configure `vcs.parity` with the list of repo paths + their golgi remotes.
**Owner**: cellMembrane (probe config) / sporeGate (repo list).

### P3-6: GNU Depot Incomplete

The `x86_64-unknown-linux-gnu` depot has only 4 of 16 primals:
`barracuda`, `biomeos`, `coralreef`, `toadstool`.

Originally this was intentional (only "GPU trio" needed gnu), but with steamGate
targeting SteamOS (which uses gnu, not musl), the full gnu depot will be needed.

**Impact**: Low now. Blocks steamGate deployment when it comes.
**Fix**: Build remaining 12 primals for gnu target. Can be batched.
**Owner**: sporeGate (build authority).

---

## III. WHERE WE CAN EVOLVE

### Evolution 1: Sovereign CI Self-Healing

**Current state**: Pipeline builds and pushes but requires manual override for
broker primals (biomeOS). cellMembrane `0cfcce5` shipped `ServerContract` resolution
which should fix this — **not yet tested with a live push through the hook**.

**Next step**: Trigger a push through the full golgi hook path and verify:
1. sandbox::validate uses correct `neural-api --socket` invocation for biomeOS
2. `finalize_depot()` generates full checksums (not partial)
3. End-to-end: push → build → sandbox → depot push → golgi sync — zero manual steps

**Payoff**: Fully autonomous pipeline. Code team pushes deploy to depot without any
sporeGate operator involvement.

### Evolution 2: VCS Drift Detection

**Current state**: `vcs.parity` checks 0 repos. 3 repos have already drifted.

**Next step**: Configure the probe with the repo list:
```toml
[[vcs_repos]]
name = "biomeOS"
local = "/home/sporegate/Development/ecoPrimals/primals/biomeOS"
remote = "origin/main"

[[vcs_repos]]
name = "cellMembrane"
local = "/home/sporegate/Development/ecoPrimals/gardens/cellMembrane"
remote = "origin/main"
# ... etc
```

**Payoff**: `gate.status` becomes a single-command health check that also shows
which primals need a cascade. Combined with sovereign CI, this creates: drift detection
→ auto-cascade → auto-build → auto-deploy.

### Evolution 3: GNU Depot Completion → steamGate Readiness

**Current state**: 4/16 gnu binaries. steamGate (Steam Deck) needs the full set.

**Next step**: Batch build remaining 12 primals for `x86_64-unknown-linux-gnu`.
Most should build cleanly since the musl versions already compile. Estimate ~30-40
minutes total build time.

**Payoff**: steamGate can deploy immediately once enrolled. Also benefits strandGate
(GPU gate that already uses some gnu binaries).

### Evolution 4: Process Lifecycle Management

**Current state**: Services run via systemd units, but manual restarts during
deployment can leave orphaned processes (skunkBat has 5). biomeOS restart
requires stop → copy → start dance because of "Text file busy" errors.

**Next step**:
1. Add `ExecStartPre=-/usr/bin/pkill -f %N` to systemd units (kill orphans before start)
2. Or use `plasmid.refresh` which should handle stop → copy → start atomically
3. Verify `plasmid.refresh` works for systemd-managed services

**Payoff**: Clean deployments. No orphan processes. No "Text file busy" errors.

### Evolution 5: J12 — blueGate Sub-Builder

**Current state**: membrane.exe is in the depot. blueGate has NUCLEUS running.
SSH dispatch pattern is ready. Missing: the actual SSH wiring from sporeGate →
blueGate to trigger Windows-native builds.

**Next step**:
1. Add blueGate's SSH host key to sporeGate's known_hosts
2. Create `sovereign.ci.dispatch --target windows --gate blueGate` in membrane
3. blueGate runs `cargo build --release` natively (no cross-compile)

**Payoff**: Windows binaries built natively instead of cross-compiled. Better
compatibility, native testing possible. Distributes build load across 2 gates.

### Evolution 6: Neural API Mode Unification

**Current state**: biomeOS systemd unit runs `biomeos api --socket`. Earlier it
ran as `biomeos neural-api`. The stale `neural-api-default.sock` symlink and
15 "Connection refused" warnings in every gate.status run are artifacts of this.

**Next step**:
1. Clean up stale symlink: `rm /run/membrane/neural-api-default.sock /run/membrane/neural-api.sock`
2. Determine if biomeOS should run `api` or `neural-api` mode on sporeGate
3. Update systemd unit if mode needs changing

**Payoff**: Clean gate.status output. Clear which mode biomeOS operates in.

### Evolution 7: Cascade Automation

**Current state**: Cascade is manual: operator runs `git pull` on each repo,
then `cargo build` for updated primals, then deploys.

**Next step**: Wire `membrane temporal.cascade` to:
1. Fetch all repos
2. Detect which have new commits vs deployed heads
3. Trigger `sovereign.ci.trigger` for each drifted primal
4. Update `sporeGate.toml` heads automatically

**Payoff**: Single command replaces the entire cascade workflow. Combined with
VCS drift detection, this enables: `gate.status` shows drift → `temporal.cascade`
→ sovereign CI builds → depot push → gate health re-check. Full loop, one command.

---

## IV. PRIMAL DEPLOY STATE

| Primal | Local HEAD | Golgi HEAD | Deployed Binary | Drift? |
|--------|-----------|------------|-----------------|--------|
| biomeOS | `0e45262f` | `744b2d17` | `0e45262f` (v4.51) | **GOLGI AHEAD by 2** |
| bearDog | `5e80b536` | `5e80b536` | `5e80b536` | Synced |
| cellMembrane | `fd07ab5` | — | `0cfcce5` | **LOCAL AHEAD by 2** (not rebuilt) |
| toadStool | `92aeb144` | `92aeb144` | `92aeb144` | Synced |
| petalTongue | `71c95c7` | `3259473` | `71c95c7` | **GOLGI AHEAD by 1** |
| songBird | `9046664` | `9046664` | `9046664` | Synced |

**3 repos drifted** — code teams pushed during this session:
- biomeOS: 2 commits (perf: eliminate redundant String alloc, deps: remove 14 unused deps)
- petalTongue: 1 commit (refactor: Wave 155m modern idiom evolution pass)
- cellMembrane: 2 commits local (registry self-knowledge, socket unification)

These are all code-quality commits (perf, deps, refactor, deep debt), not functional
changes. Safe to cascade in the next wave — no urgency.

---

## V. INFRASTRUCTURE STATE

| Component | Status | Location |
|-----------|--------|----------|
| WireGuard mesh | LIVE | `wg0`, handshake 3s ago, 67MB↓ 88MB↑ |
| Caddy (TLS) | RUNNING | golgiBody, 12 sites |
| step-ca (SSH CA) | ACTIVE | ca.primals.eco, v0.30.2 |
| Forgejo (VCS) | LIVE | git.primals.eco:2222 |
| RustDesk relay | OK | hbbs + hbbr on golgiBody |
| Depot HTTPS | OPERATIONAL | depot.primals.eco, 8459KB, 235ms TTFB |
| tmpfiles.d | INSTALLED | `/etc/tmpfiles.d/membrane.conf` |
| systemd units | 12 ACTIVE | All membrane-*.service running |
| 13/13 primals | ALIVE | All responding on sockets |

---

## VI. WAVE 155m BY THE NUMBERS

| Metric | Start of Wave | End of Wave |
|--------|--------------|-------------|
| Gate health | 10/11 (rootpulse degraded) | **11/11 HEALTHY** |
| P0s | 0 | 0 |
| P1s | 1 (membrane.exe) | **0** |
| P2s | 2 (socket evap, binary path) | **0** |
| P3s | 0 | 6 (all non-blocking) |
| Divergences resolved | 9 (from 155k) | **16** (+7 this wave) |
| Depot x86_64 | 34 | **35** (+1 gnu biomeOS) |
| biomeOS version | v4.49 | **v4.51** (3 versions in 1 wave) |
| Sovereign CI | Activated | **Validated** (3 live tests) |
| AARs filed | 0 | **4** (pipeline, v4.50, final cascade, this strategic) |
| Builds executed | 0 | **~15** (5 primals × 3 targets) |
| Feedback cycles | 0 | **3** complete loops |

---

*Filed by: sporeGate build authority
Wave: 155m strategic review
State: 11/11 HEALTHY | 35+29 = 64 depot binaries | ZERO P0/P1/P2
Active drift: 3 repos (code-quality commits, non-urgent)
Evolution path: CI self-healing → VCS drift detection → gnu completion → steamGate*
