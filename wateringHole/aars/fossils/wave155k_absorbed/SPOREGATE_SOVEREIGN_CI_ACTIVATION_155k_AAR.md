# sporeGate AAR — Sovereign CI Activation (Wave 155k)

**Date**: Jul 30, 2026 | **Gate**: sporeGate | **Wave**: 155k
**Scope**: Phase A execution — activate automated build pipeline from Forgejo push to depot

---

## Summary

Sovereign CI is now **live**. Three config fixes activated the full pipeline:
`git push` to Forgejo on golgiBody now automatically triggers build, sandbox
validation, and depot push on sporeGate. Validated end-to-end with squirrel
primal — build + sandbox PASS + depot push + HTTPS serving confirmed.

---

## Fixes Applied

### 1. SSH Key Exchange: git@golgiBody → root@sporeGate

**Before**: git user on golgiBody had a key (`forgejo-relay@golgiBody`) but no
route to sporeGate. `Host key verification failed`.

**Fix**:
- Authorized `forgejo-relay@golgiBody` public key in `/root/.ssh/authorized_keys` on sporeGate
- Added sporeGate's ed25519 host key to `/opt/forgejo/.ssh/known_hosts` on golgiBody
- Created `/root/.ssh/config` on sporeGate with golgi host alias (for depot_sync push back)
- Added golgiBody's host keys to `/root/.ssh/known_hosts` on sporeGate

**Verified**: `sudo -u git ssh root@10.13.37.2 whoami` → `root`

### 2. MEMBRANE_BUILD_AUTHORITY=1

**Before**: Not set. `post_sync::run_commit_drift_pipeline` would skip auto-harvest.

**Fix**: Added to `/etc/environment`:
```
MEMBRANE_BUILD_AUTHORITY=1
```

### 3. /usr/local/bin/membrane Updated

**Before**: Jul 23 build (15,671,368 bytes, pre-dns.configure).

**Fix**: Copied current build (Jul 30, 15,963,344 bytes, commit 2b82722).
```
membrane 0.1.0 (2b82722)
```

### 4. Rust Toolchain Available to Root

**Before**: `cargo` was in sporegate user's PATH only. Root SSH sessions couldn't build.

**Fix**:
- Symlinked `cargo`, `rustc`, `rustup` to `/usr/local/bin/`
- Added `RUSTUP_HOME` and `CARGO_HOME` to `/etc/environment`
- Added `ECOPRIMALS_ROOT=/opt/ecoPrimals` to `/etc/environment`

### /etc/environment Final State

```
PATH="..."
DEPOT_TRUST_POLICY=require-signed
MEMBRANE_BUILD_AUTHORITY=1
RUSTUP_HOME=/home/sporegate/.rustup
CARGO_HOME=/home/sporegate/.cargo
ECOPRIMALS_ROOT=/opt/ecoPrimals
```

---

## End-to-End Validation

### Test: Sovereign CI via golgiBody SSH Path

Simulated the exact path the post-receive hook takes:

```
golgiBody (git user) → SSH → sporeGate (root)
  → membrane sovereign.ci.trigger --primal squirrel
    → harvest: clone from Forgejo, cargo build --release --target musl
    → sandbox: start binary, health check, PASS
    → refresh: SCP to golgiBody depot, BLAKE3 verified
  → RESULT: 1 pushed, 0 skipped, 0 failed
```

### Verification

| Check | Result |
|-------|--------|
| SSH: git@golgi → root@sporeGate | `whoami` → `root` |
| Dry-run: `sovereign.ci.trigger --primal songbird --dry-run` | 1 built (would clone + build for musl) |
| Live build: squirrel | BUILD OK, SANDBOX PASS, REFRESH 1 PUSHED |
| Depot binary on golgiBody | `/opt/ecoPrimals/plasmidBin/primals/x86_64-unknown-linux-musl/squirrel` — 8,622,080 bytes |
| BLAKE3 on golgiBody | `46c58e34866549237f8bc23dd5d33f20ef33dc1f181ca86cd537ae35e43edeec` |
| HTTPS depot serving | `https://depot.primals.eco/primals/x86_64-unknown-linux-musl/squirrel` → HTTP 200 |

### Known Soft Warnings

- `gate identity unresolved` — root's SSH session needs to re-read `/etc/environment` (fixed by adding `ECOPRIMALS_ROOT`, takes effect on next SSH session)
- `lineage incomplete` — BLAKE3 provenance chain is soft-enforced, doesn't block builds

---

## What's Automated Now (J9+J10+J11 Killed)

```
Developer pushes to Forgejo
  → golgi post-receive hook fires (30-sovereign-ci, installed on 20 repos)
  → SSH to root@sporeGate over WireGuard mesh (10.13.37.2)
  → membrane sovereign.ci.trigger --primal <slug> --commit <sha>
    → plasmid.harvest: clone, build, strip, ELF validate, stage to depot, BLAKE3
    → sandbox.validate: start binary, health check, fail-closed
    → plasmid.refresh: atomic deploy + depot_sync push to golgiBody (BLAKE3 gated)
    → notify_mesh_depot_updated: songBird UDS → mesh.publish depot.updated
  → Consumer gates: auto_fetch → BLAKE3 verified pull from WAN depot
```

Zero human intervention required for musl builds.

---

## Remaining (Phase B/C)

| Item | Status | Owner |
|------|--------|-------|
| blueGate sub-builder (J12) | BLOCKED — blueGate NUCLEUS not live, membrane.exe won't compile | sporeGate + code team |
| mesh.build_pending (J13) | ~20 LOC — wire songBird UDS call | code team (polish) |
| HTTP webhook listener | ~200 LOC axum/UDS — bash hook works fine for now | code team (polish) |
| membrane.exe cross-compile | P1 — UnixStream needs #[cfg(unix)] | code team |

---

*sporeGate Wave 155k — Sovereign CI LIVE. Push-to-deploy automated.
J9 (push trigger) + J10 (drift auto-harvest) + J11 (multi-target manifest build)
killed. Full chain validated: golgiBody → sporeGate → build → sandbox → depot → HTTPS.
Ad-hoc workflow officially redundant for musl single-target builds.*
