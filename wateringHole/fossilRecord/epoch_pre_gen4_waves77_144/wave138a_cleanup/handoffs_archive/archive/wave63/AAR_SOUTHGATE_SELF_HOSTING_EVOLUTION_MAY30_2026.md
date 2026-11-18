# AAR: southGate Self-Hosting Evolution — Waves 48–63

**Date**: May 30, 2026
**From**: southGate (wetSpring team)
**To**: primalSpring coordination, eastGate ops
**Waves**: 48–63 (Covalent Mesh → River Delta)

---

## Summary

southGate has evolved from a bare workstation running ad-hoc Rust builds to a
near-sovereign compute node capable of running the full 13-primal NUCLEUS stack,
performing temporal sync across 20 repos, and preparing to push directly to Forgejo.
This AAR documents the self-hosting trajectory, identifies remaining gaps between
"pull-only consumer" and "fully sovereign gate," and proposes next steps.

---

## Trigger

Wave 63 audit asked all springs to onboard temporal sync — the mechanism by which
gates become first-class producers in the ecosystem rather than trailing consumers.
Completing the temporal sync tooling revealed that southGate is 85% self-hosted but
blocked on two operational items owned by eastGate.

---

## Self-Hosting Milestones Achieved

### Infrastructure (Waves 48–55)

| Capability | Status | How |
|------------|--------|-----|
| NUCLEUS 13/13 processes | DONE | `plasmidBin/nucleus_launcher.sh` + manual `--port` workarounds |
| Health monitoring | DONE | UDS JSON-RPC probes to all sockets |
| Binary provisioning | DONE | `plasmidBin/fetch.sh` → XDG cache (workaround for `RECENT_TAGS` bug) |
| biomeOS neural API | DONE | `neural-api` subcommand, 1725 capabilities / 21 surfaces |
| `.gate` identity | DONE | `$ECOPRIMALS_ROOT/.gate` → `southGate` (cascade-pull auto-detection) |
| Provenance trio (PG-02) | DONE | loamSpine + sweetGrass + rhizoCrypt all alive and IPC-responsive |
| Capability mesh (PG-04) | DONE | NestGate 66 capabilities registered |

### Code Quality (Wave 60)

| Metric | Before (V188) | After (V191) |
|--------|---------------|--------------|
| Clippy warnings | 37 | 0 |
| Test failures | 3 | 0 |
| Tests total | 2,082 | 2,085 |
| Cast safety | raw `as` casts | `try_from` / `let..else` / bounded assertions |
| Socket tests | stub files | live `UnixListener` probes |

### Ecosystem Integration (Wave 63)

| Capability | Status | How |
|------------|--------|-----|
| Temporal sync | DONE | `cascade-pull.sh --source temporal` — 16/20 repos at parity |
| Git remotes (origin) | DONE | Push to GitHub for all springs |
| Git remotes (forgejo) | CONFIGURED | Remotes exist, SSH key not registered |
| pseudoSpore profile | DONE | `domain_profile.toml` — 7 entity groups, 4 pipelines |
| Composition launcher | FOSSILIZED | `plasmidBin` is canonical; local script preserved as fossil |
| Upstream reporting | DONE | wateringHole handoffs per wave, consumed by primalSpring |
| Cross-spring fixes | DONE | neuralSpring hardcodes + ludoSpring fossilization from southGate |

---

## Current Self-Hosting Score: 85%

| Layer | Score | Gap |
|-------|-------|-----|
| Compute (NUCLEUS) | 10/13 | coralReef socket rename (upstream), 2 BTSP-gated (by design) |
| Code build | 100% | Local `cargo build`, zero warnings, 2,085 tests |
| Sync (pull) | 100% | Temporal sync pulls from all remotes |
| Sync (push) | 50% | GitHub push works; Forgejo push blocked (SSH key) |
| Provenance | 100% | PG-02/PG-04 verified, trio alive |
| Discovery | 100% | biomeOS mesh, NestGate capabilities, Songbird federation |
| Spore emission | 75% | Profile ready; `litho` binary not in plasmidBin yet |
| Identity | 100% | `.gate` file, cascade-pull auto-detection |
| Cross-gate LAN | 0% | No peer gate on subnet (ironGate/biomeGate are remote) |

---

## What "Fully Self-Hosted" Means

A fully self-hosted gate can:

1. **Build** — compile all local springs from source (DONE)
2. **Run** — host the complete NUCLEUS stack locally (DONE, 10/13 health)
3. **Sync** — pull AND push to all configured remotes (BLOCKED: Forgejo SSH)
4. **Emit** — produce pseudoSpores consumable by primalSpring (75%: needs `litho`)
5. **Discover** — find and be found by peer gates on LAN (BLOCKED: no LAN peer)
6. **Audit** — run `litho audit` locally to self-validate (BLOCKED: needs `litho`)
7. **Replicate** — bootstrap a new gate from this gate's state (NOT STARTED)

---

## Blockers to Full Sovereignty

### 1. Forgejo SSH Key Registration (eastGate ops)

**Impact**: Cannot push to Forgejo. southGate is a consumer-only node for the VPS
membrane. All pushes route through GitHub, which means the Forgejo mirror stays
stale until its pull-mirror cron runs.

**Fix**: Register southGate's SSH public key on Forgejo via eastGate admin API:

```bash
# On eastGate (VPS):
curl -X POST "https://git.primals.eco/api/v1/admin/users/southgate/keys" \
  -H "Authorization: token $FORGEJO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"southGate-ed25519","key":"ssh-ed25519 AAAA... southgate@southGate"}'
```

### 2. Forgejo Mirror → Bidirectional Conversion (eastGate ops)

**Impact**: Even with SSH key, the repos are pull-only mirrors. Push is rejected by
mirror protection. Need `membrane repo.delete` + `repo.create` cycle per repo.

**Priority order** (from audit): primalSpring → wetSpring → neuralSpring → rest.

### 3. `litho` Binary Not in plasmidBin

**Impact**: Cannot run `litho emit-pseudospore` or `litho audit` locally. The
`domain_profile.toml` is ready but the tooling to consume it isn't distributed yet.

**Owner**: gardens/lithoSpore team.

### 4. coralReef Socket Rename

**Impact**: coralReef updated upstream and changed its socket naming. NUCLEUS shows
12/13 processes running but only 10/13 health-responding because we probe the old
socket name.

**Fix**: Determine new socket name from coralReef `--help` or process listing after
next redeploy.

---

## Temporal Sync Observations

Running `cascade-pull.sh --source temporal` on southGate's 20-repo profile:

- **16/20 at parity** — local HEAD matches all known remotes
- **1 pulled** — barraCuda was behind origin
- **3 ff-only failures** — coralReef, sweetGrass, petalTongue diverged between
  GitHub origin and Forgejo mirror (expected: mirrors are stale pull-only copies)
- **1 skipped** — cellMembrane not cloned locally

The temporal sync correctly identifies the 3 diverged repos and refuses to
force-merge. This is the right behavior — those will resolve once Forgejo mirrors
are converted to bidirectional and re-synced.

---

## Lessons Learned

1. **plasmidBin is the right canonical launcher** — local `composition_nucleus.sh`
   scripts accumulated workarounds for launcher bugs. Those bugs should be fixed
   upstream rather than each spring maintaining its own launcher. Fossilizing removes
   the drift while preserving the historical pattern.

2. **Temporal sync exposes membrane health** — running `--source temporal` is the
   fastest way to see which remotes are stale. This should be a periodic health check,
   not just a pull mechanism.

3. **SSH key management is the #1 onboarding friction** — three waves of work have
   been completed on southGate code quality, NUCLEUS deployment, and temporal sync.
   The only thing preventing full bidirectional flow is a single SSH key registration
   that requires eastGate admin access.

4. **Cross-spring maintenance from a single gate works well** — fixing neuralSpring
   and ludoSpring from southGate, committing, and pushing in one session demonstrates
   that a self-hosted gate can service multiple springs efficiently.

5. **`litho` distribution is the next capability cliff** — without `litho` in
   plasmidBin, springs can author `domain_profile.toml` but cannot complete the
   pseudoSpore emission cycle. This is the next infrastructure gap after SSH.

---

## Proposed Next Steps

| Priority | Action | Owner |
|----------|--------|-------|
| P0 | Register southGate SSH key on Forgejo | eastGate ops |
| P0 | Convert wetSpring + primalSpring mirrors to bidirectional | eastGate ops |
| P1 | Add `litho` binary to plasmidBin | lithoSpore team |
| P1 | Fix coralReef socket naming in plasmidBin launcher | coralReef team |
| P2 | Periodic temporal sync cron (daily `--source temporal`) | southGate local |
| P2 | `litho emit-pseudospore` once binary available | wetSpring |
| P3 | Cross-gate LAN discovery (needs second gate on subnet) | future |
| P3 | Gate replication / bootstrap protocol | primalSpring spec |

---

## Metrics Snapshot (southGate, May 30 2026)

| Metric | Value |
|--------|-------|
| wetSpring version | V192 (`23d54af`) |
| neuralSpring version | `83e9175` |
| ludoSpring version | `c355f4d` |
| NUCLEUS processes | 13 running, 10 health-responding |
| Temporal sync | 16/20 parity |
| Clippy (wetSpring) | 0 warnings (pedantic + nursery) |
| Tests (wetSpring) | 2,085 passing, 0 failures |
| PG gaps | 0 open (22 resolved) |
| Active gaps | WS-9 (L3 parity, needs FASTQ), WS-11 (MAPQ calibration, needs dataset) |
| pseudoSpore readiness | domain_profile.toml authored, awaiting `litho` |
