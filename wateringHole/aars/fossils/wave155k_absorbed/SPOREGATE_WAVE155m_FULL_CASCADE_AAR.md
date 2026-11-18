# sporeGate AAR — Wave 155m Full Cascade + Depot Rebuild

**Date**: Jul 30, 2026 | **Gate**: sporeGate | **Wave**: 155m
**Scope**: Sovereign CI activation, 5 team shipments rebuilt, membrane.exe P1 resolved, depot 15/15 Windows

---

## Summary

Three major phases completed in one session:

1. **Sovereign CI activated** — 4 config fixes turned the existing cellMembrane pipeline
   from dormant code into a live push-to-deploy system. J9+J10+J11 jelly strings killed.
2. **Wave 155m cascade** — pulled 5 simultaneous code team shipments, rebuilt all for
   musl+gnu+windows via sovereign CI + manual cross-compile.
3. **membrane.exe P1 RESOLVED** — the last blocked `.exe` now compiles. Depot is 15/15
   Windows binaries. J12 (blueGate sub-builder) is unblocked.

---

## Phase 1: Sovereign CI Activation

### Problem

cellMembrane had a complete sovereign CI pipeline in Rust (`sovereign.ci.trigger` →
harvest → sandbox → refresh → depot push). The golgi post-receive hook was installed
on all 20 Forgejo repos. But 4 config links were broken, so we were building manually.

### Fixes Applied

| Fix | What | Effort |
|-----|------|--------|
| SSH key exchange | Authorized `forgejo-relay@golgiBody` on sporeGate root. Added host keys both directions. | 10 min |
| `MEMBRANE_BUILD_AUTHORITY=1` | Added to `/etc/environment` | 1 line |
| `/usr/local/bin/membrane` | Updated to current build (2b82722 → 4e77ffd) | 1 command |
| Rust toolchain for root | Symlinked `cargo`/`rustc`/`rustup` to `/usr/local/bin/`. Set `RUSTUP_HOME`, `CARGO_HOME`, `ECOPRIMALS_ROOT` in `/etc/environment`. | 5 min |
| Root SSH config | Created `/root/.ssh/config` with golgi host alias for depot_sync push-back. | 2 min |

### `/etc/environment` Final State

```
PATH="..."
DEPOT_TRUST_POLICY=require-signed
MEMBRANE_BUILD_AUTHORITY=1
RUSTUP_HOME=/home/sporegate/.rustup
CARGO_HOME=/home/sporegate/.cargo
ECOPRIMALS_ROOT=/opt/ecoPrimals
```

### Validation

Full chain tested end-to-end:

```
golgiBody (git user) → SSH → sporeGate (root) → membrane sovereign.ci.trigger
  → harvest: clone from Forgejo, cargo build --release --target musl
  → sandbox: start binary, health check, PASS
  → refresh: SCP to golgiBody depot, BLAKE3 verified
  → RESULT: 1 pushed, 0 skipped, 0 failed
```

Validated with two primals:
- **squirrel** (via golgi SSH path): build OK, sandbox PASS, depot push 1/1
- **songBird** (via `plasmid.harvest --push`): 18,789 KB, commit 90466648, pushed to 5 architectures

### Jelly Strings Killed

| Jelly | Before | After |
|-------|--------|-------|
| J9 (push trigger) | Hook installed but SSH broken | **KILLED** — SSH plumbed, validated E2E |
| J10 (drift auto-harvest) | Code existed but env var missing | **KILLED** — BUILD_AUTHORITY=1, drift pipeline active |
| J11 (multi-target manifest) | Code existed, manifest entries verified | **KILLED** — targets_for_primal() reads manifest |

---

## Phase 2: Wave 155m Cascade + Rebuild

### Pulls

| Primal | From | To | Key Change | Lines |
|--------|------|----|------------|-------|
| bearDog | d6b1003 | 5e80b53 | Dual-socket fix + 94 orphan files purged | -19,214 |
| biomeOS | 4e8f00c | b0b6046 | v4.49 — capability wipe cycle fix (3-strike prune) | -1,483 net |
| toadStool | 2df7139 | 92aeb14 | JSON-RPC health endpoint + S349 deep debt | net reduction |
| petalTongue | d60e67d | 71c95c7 | `--family-id` propagation + BIND_MODE fix | +68 |
| cellMembrane | 2b82722 | 4e77ffd | membrane.exe P1 fix + steamGate user-space + reqwest purge | multi-commit |

### Builds

| Binary | musl | gnu | windows | Method |
|--------|------|-----|---------|--------|
| beardog | 8,459 KB | — | 7,866 KB | sovereign CI (`plasmid.harvest --push`) + cross-compile |
| biomeos | 16,060 KB | — | cross-compiled | sovereign CI + cross-compile |
| toadstool | 13,131 KB | 12,947 KB | cross-compiled | sovereign CI (2 targets) + cross-compile |
| petaltongue | 34,157 KB | — | cross-compiled | sovereign CI + cross-compile |
| membrane | 14,017 KB | — | 15,527 KB | manual `cargo build` (not in sources.toml) |

### membrane.exe — P1 RESOLVED

**Before**: `membrane.exe` failed to cross-compile due to `UnixStream` and
`handshake_async` not being `#[cfg(unix)]` gated. The last blocked `.exe`.

**Fix**: cellMembrane commit `4ccbab1` added `#[cfg(unix)]` gates + Windows stubs.

**After**: `membrane.exe` compiles cleanly (29 warnings, all non-blocking). 15,527 KB.
Deployed to depot. Serving via `depot.primals.eco` HTTP 200.

**Impact**: Depot is now **15/15 Windows binaries**. J12 (blueGate sub-builder) is
unblocked — blueGate can run membrane natively.

### Depot State

| Target | Count | Status |
|--------|-------|--------|
| `x86_64-unknown-linux-musl` | 16 | ALL FRESH (Wave 155m) |
| `x86_64-unknown-linux-gnu` | 3 | ALL FRESH (Wave 155m) |
| `x86_64-pc-windows-gnu` | **15** | ALL FRESH — membrane.exe NEW |
| Total x86_64 | **34** | BLAKE3 verified, pushed to golgiBody |

---

## Phase 3: Local Deployment

biomeOS v4.49, bearDog (dual-socket fix), toadStool (S349), petalTongue (BIND_MODE fix)
deployed to sporeGate's local install path. songBird (TCP registration fix) deployed
in earlier session.

### Gate Health

```
sporeGate (x86_64-unknown-linux-musl) — 10/11 OK
  [OK] depot.integrity: 16 verified, 0 hash mismatch
  [OK] mesh.reachability: 3 peers, 3 reachable
  [OK] primals.alive: 13/13 alive
  [OK] depot.freshness: 13/13 binaries present
  [OK] sovereignty.s1_tls: depot.primals.eco 200 OK
  [OK] sovereignty.s2_relay: federation REACHABLE, RustDesk hbbs+hbbr OK
  [OK] sovereignty.s3_content: depot serving 8,459 KB
  [OK] sovereignty.s4_auth: beardog reachable via neuralAPI
  [OK] vcs.parity: 0 repos drifted
  [OK] service.crash-loop: 14 services, no crash-loops
  [DEGRADED] rootpulse.ledger: not yet implemented (cellMembrane code team)
```

---

## Issues & Divergences Encountered

### Issue 1: sovereign.ci.trigger Permission Chain (RESOLVED)

When `sovereign.ci.trigger` runs as root via golgi SSH, it clones from Forgejo and
builds. But `cargo` wasn't in root's PATH, and `RUSTUP_HOME`/`CARGO_HOME` weren't set.

**Symptom**: `cargo build spawn failed: No such file or directory (os error 2)`

**Fix**: Symlinked cargo/rustc/rustup to `/usr/local/bin/`, set env vars in `/etc/environment`.

**Residual**: The SSH session reads `/etc/environment` but not `.bashrc`. Any env var
needed by the build must be in `/etc/environment`, not user profile.

### Issue 2: Depot Push Fails as sporegate User (WORKAROUND)

`sovereign.ci.trigger` running as sporegate user can build and sandbox, but the
refresh (depot push to golgiBody) fails because the `depot_sync` module uses the
`ShadowConfig.ssh_host` alias (`golgi`), which is only configured in sporegate's
`~/.ssh/config`. The root user has a separate SSH config.

**Symptom**: `scp failed (exit 1): lost connection` when running as sporegate.
Works fine when running as root (via golgi SSH path).

**Workaround**: Use `plasmid.harvest --push` (which uses the sporegate user's SSH config
directly) instead of `sovereign.ci.trigger` for local builds. The golgi SSH hook path
(running as root) works correctly end-to-end.

**Root cause**: `depot_sync` constructs the SCP target from `config.ssh_host` which
resolves to `golgi` — a hostname alias that only exists in the current user's SSH
config. Root has it, sporegate has it, but the resolution path differs.

### Issue 3: Socket Permission Lifecycle (CHRONIC)

Primals started by `sudo` (biomeOS) create sockets owned by `root:root` in `/run/membrane/`.
When non-root primals (beardog, songbird) try to bind or connect, they get Permission denied.

**Fix applied**: Set `/run/membrane` to `1777` (sticky world-writable). Socket group
changed to `membrane` with `660` permissions post-creation. sporegate user is in `membrane` group.

**Residual divergence**: This is a recurring manual step. Every time biomeOS or a primal
restarts, sockets need permission fixup. The proper fix is one of:
1. biomeOS creates sockets with `membrane` group ownership from the start
2. A systemd tmpfiles.d rule sets the directory ACL
3. All primals run as the same user (eliminating the root/sporegate split)

**Recommendation for code team**: biomeOS should `chown :membrane` and `chmod 660` its
sockets at creation time, or respect a `MEMBRANE_SOCKET_GROUP` env var.

### Issue 4: Checksums.toml Drift After Sovereign CI Rebuilds (RESOLVED)

When `sovereign.ci.trigger` or `plasmid.harvest` rebuilds a primal, it updates the
depot binary and pushes to golgiBody. But the `checksums.toml` in the depot isn't
always regenerated to match the new binaries.

**Symptom**: `depot.integrity` shows hash mismatches (binary is new, checksum is old).

**Root cause**: The harvest pipeline updates checksums for the target it built, but
when running as a clone (not `--local`), the checksum update may write to a different
path than the depot probe reads.

**Fix applied**: Manual `checksums.toml` regeneration from actual depot binaries using
`b3sum`. Synced to workspace path and golgiBody.

**Recommendation**: The `plasmid.harvest` pipeline should always regenerate the full
`checksums.toml` from the depot directory after staging, not just append/update the
single primal entry.

### Issue 5: bearDog Neural API Capability Registration (OBSERVED)

After deploying the new bearDog (5e80b53, dual-socket fix), the Neural API reports
`Capability 'beardog' not registered` when probed. The available capabilities list
shows `crypto.delegate`, `network.btsp`, etc. — capability-based names, not primal names.

**Impact**: `sovereignty.s4_auth` still reports OK (beardog responds to direct socket
health check), but capability-based routing via Neural API uses capability names rather
than primal names.

**Not a bug**: This is the correct behavior for the new biomeOS capability registry.
The `gate.status` probe that checks `beardog` by name is using a legacy routing path.
The probe should be updated to query by capability (`crypto.delegate` or `crypto.sign`).

### Issue 6: cellMembrane Not in sources.toml (NOTED)

`membrane plasmid.harvest --primal membrane` fails because cellMembrane isn't registered
in `sources.toml` or manifest `[build.*]` entries. It's a self-build (the tool builds itself).

**Impact**: Sovereign CI can't auto-rebuild membrane on push. Must build from local source.

**Recommendation**: Add `[sources.cellmembrane]` and `[build.membrane]` to the manifest
so sovereign CI treats it like any other primal.

### Issue 7: /run/membrane Not Persistent Across Reboot (NOTED)

`/run/membrane` is a tmpfs. The `1777` permission and directory structure are lost on
reboot. Need a systemd tmpfiles.d rule or init script.

**Recommendation**: Add `/etc/tmpfiles.d/membrane.conf`:
```
d /run/membrane 1777 root membrane -
```

---

## Summary of Divergences for Code Teams

| Divergence | Severity | Owner | Status |
|-----------|----------|-------|--------|
| Socket ownership on creation (biomeOS) | P2 | biomeOS | OPEN — recurring manual fixup |
| checksums.toml partial update on harvest | P2 | cellMembrane | OPEN — needs full regeneration |
| bearDog probe uses primal name vs capability name | P3 | cellMembrane (gate.status) | OBSERVED — cosmetic |
| cellMembrane not in sources.toml | P3 | cellMembrane | NOTED — blocks self-CI |
| /run/membrane tmpfiles.d rule | P3 | cellMembrane (deploy) | NOTED — reboot resilience |
| rootpulse.ledger not implemented | P2 | cellMembrane | OPEN — sole remaining degraded probe |
| biomeOS socket evaporation (health ping format) | P2 | biomeOS | OPEN — from overwatch blurb |
| biomeOS binary path retention | P2 | biomeOS | OPEN — from overwatch blurb |

---

## Timeline

```
Jul 30 09:07  — Session start. Pipeline automation AAR written.
Jul 30 09:37  — Phase A execution: SSH key, env var, membrane binary, cargo symlinks.
                Sovereign CI validated E2E (squirrel via golgi, songBird harvest --push).
                J9+J10+J11 killed. cellMembrane team blurb pushed.
Jul 30 10:05  — songBird TCP registration fix deployed via sovereign CI.
                Gate health 10/11 OK. Checksums regenerated.
Jul 30 12:03  — Wave 155m blurb received. Cascade from golgiBody.
                5 team shipments pulled (bearDog, biomeOS, toadStool, petalTongue, cellMembrane).
Jul 30 12:10  — bearDog rebuilt via sovereign CI (8,459 KB, 5e80b53). Pushed.
Jul 30 12:15  — biomeOS v4.49 rebuilt (16,060 KB, b0b6046). Pushed.
Jul 30 12:22  — toadStool rebuilt for 2 targets (musl+gnu, 92aeb14). Pushed.
Jul 30 12:25  — petalTongue rebuilt (34,157 KB, 71c95c7). Pushed.
Jul 30 12:24  — cellMembrane built from local source (14,017 KB, 4e77ffd).
Jul 30 12:25  — membrane.exe COMPILES — P1 RESOLVED. 15,527 KB. Deployed to depot.
Jul 30 12:27  — beardog.exe, biomeos.exe, toadstool.exe, petaltongue.exe cross-compiled.
Jul 30 12:35  — All pushed to golgiBody. Checksums regenerated.
                Depot: 34 x86_64 binaries (16 musl + 3 gnu + 15 windows).
Jul 30 12:40  — Local deployment: biomeOS v4.49 + bearDog + toadStool + petalTongue.
                Gate health 10/11 OK. Head updated. Pushed upstream.
```

---

*sporeGate Wave 155m — Sovereign CI live (J9+J10+J11 killed). 5 code team shipments
rebuilt and pushed. membrane.exe P1 RESOLVED — depot 15/15 Windows (was 14/14).
J12 sub-builder UNBLOCKED. biomeOS v4.49 + bearDog dual-socket deployed. 34 x86_64
binaries, all BLAKE3 verified. Gate 10/11 OK. 8 divergences documented for code teams.
Zero P0s. Zero P1s.*
