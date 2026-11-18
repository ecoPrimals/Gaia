# sporeGate AAR — Pipeline Automation: Ad-Hoc → K-Derm (Wave 155k)

**Date**: Jul 30, 2026 | **Gate**: sporeGate | **Wave**: 155k
**Scope**: Map every ad-hoc build/push step to its cellMembrane automation primitive, identify concrete gaps, plan blueGate sub-builder role

---

## Executive Summary

The ad-hoc build/push workflow is **85% dead code walking** — cellMembrane already
has the full pipeline in Rust. The chain is built; specific links are broken.
This AAR maps exactly what exists, what's broken, and the minimal config/code
changes to transition from `ssh + manual cargo build + scp` to sovereign CI
triggered automatically by Forgejo push events.

---

## The Ad-Hoc Workflow (What We Do Today)

Every time a code team ships, sporeGate runs this manually:

```
1. Read ECOSYSTEM_BLURB.md for what changed           ← human reads blurb
2. ssh golgi / git pull in each repo                   ← temporal.cascade does this
3. cd ~/Development/ecoPrimals/gardens/<primal>
4. cargo build --release --target x86_64-unknown-linux-musl  ← plasmid.harvest does this
5. strip the binary                                    ← harvest does this
6. cp to /opt/ecoPrimals/depot/primals/<arch>/         ← harvest stages to depot
7. b3sum the binary, update checksums.toml             ← harvest auto-checksums
8. scp to golgi:/opt/ecoPrimals/depot/                 ← plasmid.push does this
9. Repeat for gnu and windows targets                  ← targets_for_primal() does this
10. Update provenance.toml                             ← harvest writes provenance
11. Update heads/sporeGate.toml                        ← temporal.cascade --publish does this
12. Push wateringHole upstream                         ← cascade auto-commits heads
```

Every single step has a Rust equivalent in cellMembrane. We're doing manually
what the code already automates.

---

## What cellMembrane Already Has (Working Today)

### Full Pipeline Chain

| Step | Ad-Hoc Today | cellMembrane Equivalent | Status |
|------|-------------|------------------------|--------|
| Pull latest code | `git pull` in each repo | `temporal.cascade --clone-missing` | **WORKS** |
| Detect what changed | Read blurb / eyeball | `drift::has_upstream_changes` (ls-remote vs provenance.toml) | **WORKS** |
| Build from source | `cargo build --release` | `plasmid.harvest --primal X [--target T]` | **WORKS** |
| Multi-target builds | Manual per triple | `targets_for_primal()` reads `[build.*].targets` from manifest | **WORKS** |
| Strip + ELF validate | `strip` + manual check | `harvest.rs` → auto-strip + ELF validation | **WORKS** |
| Stage to depot | `cp` to depot dir | `stage_to_depot_async` → atomic copy + BLAKE3 | **WORKS** |
| Checksum generation | `b3sum` + manual TOML edit | `update_checksums` → auto BLAKE3 + TOML write | **WORKS** |
| Sign checksums | Not done | `sign_and_persist` → Ed25519 of checksums.toml | **WORKS** |
| Push to golgiBody | `scp` manually | `plasmid.push` / `depot_sync_push_standalone` (BLAKE3-gated SSH) | **WORKS** |
| Record provenance | Manual or forgotten | `update_provenance()` → commit SHA, builder, rustc, timestamp | **WORKS** |
| Publish heads | Manual TOML edit | `publish_gate_heads()` → auto tree-hash commit + push | **WORKS** |
| Notify mesh | Not done | `notify_mesh_depot_updated()` → songBird UDS JSON-RPC | **WORKS** |
| Consumer auto-fetch | Not done | `auto_fetch::handle_depot_updated()` → BLAKE3 verified pull | **WORKS** |

### Sovereign CI Pipeline (Single Command)

`sovereign.ci.trigger --primal <name> --commit <sha>` does:
1. Resolve primal from service registry
2. `plasmid::harvest` (manifest-driven build from Forgejo clone)
3. `sandbox::validate` (start binary, health check, stop — fail-closed)
4. `plasmid::refresh` (atomic deploy to install dir + VPS depot sync)
5. Return structured JSON outcome with provenance

This is the **entire ad-hoc workflow in one typed command**.

### Forgejo Trigger (Production Hook)

`golgi-post-receive-ci.sh` is **installed on all 20 repos** on golgiBody.
On push, it SSHes to sporeGate and runs `sovereign.ci.trigger`.

### Webhook Pipeline (Code-Level)

`webhook/pipeline.rs` has `run_harvest_pipeline()` and `run_cascade_pipeline()`.
HMAC-SHA256 verification, Forgejo/GitHub provider detection, push event
classification — all implemented and tested.

### Post-Cascade Auto-Build

`temporal/post_sync.rs::run_commit_drift_pipeline()` detects drifted primals
after cascade and auto-harvests them when `MEMBRANE_BUILD_AUTHORITY=1`.

---

## What's Broken (Concrete Gaps)

### Gap 1: SSH Key Exchange golgiBody → sporeGate — BROKEN

The post-receive hook runs as the `git` user on golgiBody. It SSHes to
`root@10.13.37.2` (sporeGate mesh IP). This path is **broken**:

```
$ ssh golgi 'sudo -u git ssh root@10.13.37.2 whoami'
Host key verification failed.
```

**Fix**: Add sporeGate's host key to `/home/git/.ssh/known_hosts` on golgiBody,
and authorize the git user's public key in sporeGate's `/root/.ssh/authorized_keys`.
Alternatively, run the hook as root or use a dedicated `ci@sporeGate` user.

**Effort**: 10 minutes of SSH key plumbing.

### Gap 2: MEMBRANE_BUILD_AUTHORITY Not Set

`post_sync.rs` checks `MEMBRANE_BUILD_AUTHORITY=1` before auto-harvesting.
sporeGate doesn't export this in its shell environment.

```
$ echo $MEMBRANE_BUILD_AUTHORITY
(empty)
```

**Fix**: Add to `/etc/environment` or the membrane systemd unit's `Environment=`.

**Effort**: 1 line.

### Gap 3: /usr/local/bin/membrane is Stale

The golgi hook calls `/usr/local/bin/membrane` on sporeGate. That binary is
from Jul 23 (15.6 MB, pre-dns.configure). The current build is Jul 30 (16.0 MB).
If `sovereign.ci.trigger` uses any newer code paths, the stale binary will fail.

```
/usr/local/bin/membrane  — Jul 23, 15671368 bytes
~/.local/bin/membrane    — Jul 30, 15963344 bytes
```

**Fix**: `sudo cp ~/.local/bin/membrane /usr/local/bin/membrane && sudo chmod 755 /usr/local/bin/membrane`

**Effort**: 1 command.

### Gap 4: No HTTP Webhook Server in membrane

The Rust webhook modules have full event processing (HMAC verify, classify,
dispatch), but **no HTTP/UDS listener**. The bash hook works as a bridge, but
the architecture intent is `Forgejo → Caddy → membrane UDS socket`.

- `WebhookProvider::detect()` is `#[allow(dead_code)]`
- `capability_registry.toml` declares `webhook_receive = { protocol = "http" }` — not wired
- Architecture comment references the UDS path but it's not implemented

**Fix**: Code team ships an HTTP/UDS listener in membrane-shadow (small — the
dispatch logic exists, it just needs a hyper/axum endpoint or UDS accept loop).
OR — keep the bash hook. It works. The UDS server is a polish item.

**Effort**: Code team — ~200 LOC for axum UDS endpoint. OR zero (bash hook is fine).

### Gap 5: harvest --push Not in Sovereign CI

`sovereign.ci.trigger` calls `harvest(force=true, push=false)` then `refresh()`.
The refresh does VPS depot sync, but the harvest itself doesn't push. The
push happens in refresh via `depot_sync`, which is the correct flow.

**Status**: Actually fine. The push path works: harvest → stage → refresh (which syncs to VPS). No gap here, just a clarification.

### Gap 6: mesh.build_pending is Stub-Only

`notify_mesh_build_pending()` logs but doesn't actually publish to songBird.
Consumer gates don't know a build is in progress — they only get `depot.updated`
after completion.

**Fix**: Wire the same songBird UDS JSON-RPC call as `depot.updated` uses.

**Effort**: ~20 LOC — copy `notify_mesh_depot_updated()` pattern with topic `depot.build_pending`.

### Gap 7: blueGate Sub-Builder Dispatch — Not In Code

No mechanism to say "sporeGate, dispatch this Windows build to blueGate."
The manifest has `topology.roles.build_authorities` (ordered failover list)
and `manifest.is_build_authority(gate)`, but there's no RPC for remote builds.

**Fix**: Two options:
1. **SSH dispatch** (like golgi hook) — sporeGate SSHes to blueGate:
   `membrane sovereign.ci.trigger --primal X --target x86_64-pc-windows-gnu`
2. **Mesh dispatch** — songBird `mesh.publish { topic: "build.request" }` →
   blueGate subscribes and auto-builds. Requires `auto_fetch` pattern for builds.

**Effort**: Option 1: 50 LOC + SSH keys. Option 2: ~300 LOC (new mesh topic + handler).

---

## Jelly Strings: Revised Mapping

Previous AAR mapped J9-J13 abstractly. Here's the concrete revision based on
what the code actually contains:

| Jelly | Description | Code State | Gap | Fix |
|-------|-------------|-----------|-----|-----|
| **J9** | Push → Build trigger | `golgi-post-receive-ci.sh` INSTALLED on 20 repos. `sovereign.ci.trigger` IMPLEMENTED. | SSH key exchange broken (git@golgi → root@sporeGate) | SSH key plumbing: 10 min |
| **J10** | Cascade → Drift → Auto-harvest | `post_sync::run_commit_drift_pipeline` IMPLEMENTED | `MEMBRANE_BUILD_AUTHORITY` not set in env | 1 env var |
| **J11** | Multi-target manifest build | `targets_for_primal()` reads `[build.*].targets` from manifest | None — this works today if manifest `[build.*]` entries have `targets` | Verify manifest has target lists |
| **J12** | blueGate Windows sub-builds | Not in code | No remote build dispatch RPC | SSH dispatch (~50 LOC) or mesh topic (~300 LOC). Blocked on blueGate NUCLEUS. |
| **J13** | Mesh depot notification | `notify_mesh_depot_updated()` WORKS. `auto_fetch` handler WORKS. | `build_pending` is stub-only (log, no publish) | ~20 LOC to wire songBird UDS call |

---

## The Kill Order

Steps to transition from ad-hoc to k-derm automated, by effort:

### Phase A: Immediate (Today, No Code Changes)

1. **Fix SSH keys** — authorize git@golgi to SSH to sporeGate as root (or ci user)
2. **Set MEMBRANE_BUILD_AUTHORITY=1** in `/etc/environment`
3. **Update /usr/local/bin/membrane** to current build
4. **Verify manifest [build.*] target entries** exist for all primals

After Phase A: pushing to Forgejo automatically triggers build on sporeGate.
**J9, J10, J11 are killed. Pipeline is automated for single-arch builds.**

### Phase B: Short Term (blueGate Live)

5. **SSH key exchange** — sporeGate → blueGate for build dispatch
6. **Windows build dispatch** — `sovereign.ci.trigger --target x86_64-pc-windows-gnu`
   via SSH from sporeGate to blueGate (same pattern as golgi→sporeGate)
7. **Wire build_pending notification** — 20 LOC, consumers can show build status

After Phase B: cross-platform builds automated. sporeGate builds musl/gnu,
blueGate builds Windows natively. **J12, J13 killed.**

### Phase C: Polish (When Convenient)

8. **HTTP/UDS webhook listener** in membrane — replace bash hook with native Rust
9. **Build queue** — if build volume grows, add a lightweight queue (songBird mesh topic)
10. **Provenance signing chain** — bearDog Ed25519 signs provenance.toml
11. **membrane.exe Windows fix** — code team: `#[cfg(unix)]` gate remaining UnixStream uses

---

## What blueGate Needs to Be Ready

| Requirement | Status |
|-------------|--------|
| blueGate NUCLEUS (biomeOS) running | PENDING — needs Windows biomeOS or WSL deployment |
| membrane installed on blueGate | PENDING — `.exe` blocked (code team P1) |
| SSH key: sporeGate → blueGate | PENDING — WireGuard mesh is live, SSH not configured |
| Rust toolchain on blueGate | UNKNOWN — needs `rustup` + `x86_64-pc-windows-gnu` target |
| Forgejo SSH access for clone | DONE — blueGate key registered (155i) |
| Depot write access on golgiBody | DONE — via sporeGate relay (push back to depot) |

**Blocker**: `membrane.exe` doesn't compile (UnixStream not `#[cfg(unix)]` gated).
blueGate can't run membrane until this is fixed. Workaround: blueGate runs
builds via plain `cargo build` triggered by SSH, and sporeGate handles depot push.

---

## Summary

The pipeline is not "mostly ad-hoc with some automation." It's **fully automated
in code, with 3 broken config links preventing activation**:

1. SSH key (10 min)
2. One env var (1 line)
3. Stale binary (1 command)

Fix those three and J9+J10+J11 are killed. Every `git push` to Forgejo
automatically builds, sandboxes, deploys, checksums, pushes to depot, and
notifies the mesh. The blurb-reading, manual cargo build, manual scp, manual
checksum dance — all dead.

blueGate sub-builder (J12) requires blueGate NUCLEUS + SSH dispatch. The pattern
is identical to golgi→sporeGate. We wait for blueGate to come online, then wire
the same hook.

---

*sporeGate Wave 155k — Pipeline automation audit complete. The chain is built.
Three config fixes activate sovereign CI. Ad-hoc workflow is 85% redundant today
and will be 100% redundant after Phase A. blueGate sub-builder queued for Phase B
when NUCLEUS is live. Mesh notification gap is 20 LOC.*
