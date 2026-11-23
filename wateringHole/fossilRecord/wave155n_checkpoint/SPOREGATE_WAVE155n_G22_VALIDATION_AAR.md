# sporeGate Wave 155n — G22 Validation + D5/D7 Resolution AAR

**Gate**: sporeGate | **Date**: 2026-07-31T23:45:00Z | **Wave**: 155n
**Operator**: sporeGate build authority | **From**: eastGate overwatch cascade

---

## SESSION OVERVIEW

Cascaded biomeOS G22 COMPLETE (`b82f0925` + `7ccd8aef`) and validated the
single-process merge on sporeGate. Also resolved 3 divergences (D5, D7, D1/D6).

### What We Deployed

| Component | Commit | What Changed |
|-----------|--------|--------------|
| **biomeOS** | `7ccd8aef` (G22 complete + docs) | api + neural-api → single process. Dual-protocol in both modes. `neural-api` subcommand deprecated. |
| **cellMembrane** | `882ad09` (at HEAD, no new commits) | J18 gate coupling fix already deployed. |
| **wateringHole** | `b80076a5` | Checkpoint blurb absorption. |

### Build Matrix

All 6 builds succeeded:

| Target | biomeOS | cellMembrane |
|--------|---------|--------------|
| `x86_64-unknown-linux-musl` | 21MB, 2m20s | 16MB, 48s |
| `x86_64-unknown-linux-gnu` | built, 2m30s | built, 47s |
| `x86_64-pc-windows-gnu` | built, 4m32s (5 warnings) | built, 1m25s (27 warnings) |

---

## G22 VALIDATION — SINGLE-PROCESS MERGE

### What G22 Changes

Before G22: biomeOS ran as two systemd units — `membrane-biomeos.service` (api mode,
riboCipher) and `membrane-neural-api.service` (neural-api mode, plain JSON-RPC).
This caused:
- Socket evaporation on restart (D1)
- Permission resets (D2)
- Dual-service complexity (D6)

After G22: `membrane-biomeos.service` alone serves both protocols. The `neural-api`
subcommand is deprecated. The api process creates `neural-api-{family_id}.sock` for
plain JSON-RPC alongside `biomeos.sock` for riboCipher.

### Validation Results

**Single-process test**: PASS
- `membrane-biomeos.service`: `active`
- `membrane-neural-api.service`: `inactive` (not needed)
- One process serves both riboCipher AND plain JSON-RPC

**Dual-protocol test**: PASS
```
health → {"version":"4.56.0","registered_capabilities":244,"status":"alive","mode":"Bootstrap"}
composition.test_swap → {"validated":false,"reason":"Candidate probe failed"} (expected — D4 still open)
```

**D1 (Socket evaporation)**: VALIDATED RESOLVED
- Restarted `membrane-biomeos.service`
- biomeOS sockets re-created (new timestamps)
- Primal sockets (barracuda, beardog, squirrel, etc.) SURVIVED the restart
- No socket evaporation — primals live through biomeOS restart

**D6 (Dual-service)**: VALIDATED RESOLVED
- Only `membrane-biomeos.service` running
- neural-api embedded in api process

**D2 (Permission reset)**: PARTIALLY RESOLVED
- biomeOS still creates its own sockets as `srw-rw---- root:membrane`
- Primal sockets remain `srwxrwxrwx root:root`
- `sporegate` user IS in the `membrane` group — so group perms work
- Manual `chmod 0777` not needed if all consumers are in `membrane` group
- True fix: biomeOS should create sockets with `0660` + group-readable

---

## D7 RESOLVED — sporePrint Auto-Publish Hook

Installed Forgejo post-receive hook at:
```
/opt/forgejo/data/repositories/ecoprimals/sporeprint.git/hooks/post-receive.d/50-zola-publish
```

Hook behavior:
1. Triggers only on pushes to `main` branch
2. `git fetch` + `git reset --hard origin/main` in `/opt/ecoPrimals/sporePrint/`
3. Runs `zola build --output-dir public`
4. Logs page count to syslog

Now any push to sporePrint repo auto-rebuilds the site. No manual SSH required.

---

## D5 RESOLVED — Sovereign CI SSH Access

**Root cause**: `root` on sporeGate had no SSH keys, so `sovereign.ci.trigger`
(which runs as root via golgi SSH dispatch) could not clone from Forgejo.

**Fix applied**:
1. Generated CI deploy key: `sovereign-ci@sporeGate` (ed25519)
2. Configured `/root/.ssh/config` for `git.primals.eco:2222`
3. Registered key on Forgejo (key ID 15, under `golgiAdmin`)
4. Added `git.primals.eco` to root's `known_hosts`

**Verified**:
```
$ sudo ssh git@git.primals.eco → "Hi there, golgiAdmin! You've successfully authenticated"
$ sudo git clone ssh://git@git.primals.eco:2222/ecoPrimals/squirrel.git → success
$ sudo membrane sovereign.ci.trigger --primal squirrel --dry-run → "1 built, 0 current"
```

Sovereign CI can now clone fresh from Forgejo on every trigger. Source tree
divergence is eliminated.

---

## FINAL GATE STATUS

```
sporeGate (x86_64-unknown-linux-musl) — HEALTHY
  [OK] depot.integrity: 16 verified, 0 hash mismatch, 0 missing
  [OK] mesh.reachability: 7 peers, 7 reachable
  [OK] primals.alive: 13/13 primals alive
  [OK] depot.freshness: 13/13 binaries present, oldest 2d
  [OK] sovereignty.s1_tls: OPERATIONAL — depot.primals.eco 200 (220ms)
  [OK] sovereignty.s2_relay: federation:REACHABLE TURN:TCP-CLOSED(UDP-only)
  [OK] sovereignty.s3_content: OPERATIONAL — depot serving 8459KB (230ms)
  [OK] sovereignty.s4_auth: RESPONDING — beardog alive
  [OK] rootpulse.ledger: no session yet
  [OK] vcs.parity: 0 repos checked, 0 drifted
  [OK] service.crash-loop: 14 services scanned, no crash-loops
```

**11/11 HEALTHY. ZERO degraded probes.**

---

## DIVERGENCE STATUS UPDATE

| ID | Issue | Status |
|----|-------|--------|
| D1 | Socket evaporation on restart | **VALIDATED RESOLVED** (G22) |
| D2 | `/run/membrane` permission reset | **PARTIALLY RESOLVED** (group perms work, not world-readable) |
| D3 | checksums.toml format drift | Open — needs `depot.seal` codification |
| D4 | Candidate self-test probe fails | Open — biomeOS lightweight probe needed |
| D5 | Sovereign CI source tree divergence | **RESOLVED** (root SSH key registered) |
| D6 | Dual-service architecture | **VALIDATED RESOLVED** (G22 single-process) |
| D7 | sporePrint publish not automated | **RESOLVED** (Forgejo post-receive hook) |
| D8 | Neural API capability routing gaps | Open — primal registration needed |
| D9 | `nucleus_launcher` GNU build missing | Open — extract from biomeOS workspace |
| D10 | Zola warnings (4 lab pages) | Open — frontmatter fix (trivial) |

**Summary**: 5 of 10 divergences resolved (D1, D5, D6, D7 fully; D2 partially).
Remaining: D3 (ops), D4 (biomeOS), D8 (biomeOS), D9 (build), D10 (content).

---

## RECOMMENDATIONS TO OVERWATCH

1. **J12 sub-builder wire is the sole MUST-CLEAR item.** biomeOS G22 is validated,
   sporePrint is auto-publishing, sovereign CI has fresh clones. The only gate to
   springs+gardens is songBird IPC message format for sporeGate → blueGate dispatch.

2. **D2 is manageable.** `sporegate` is in the `membrane` group, so socket access
   works. For gates where the user isn't in the `membrane` group, a biomeOS config
   option for socket permissions would be the clean fix.

3. **D3 (checksums.toml) and D9 (`nucleus_launcher`) are polish items.** Not blocking
   anything but worth codifying before springs+gardens increases build frequency.

4. **strandGate v4.56 redeploy** should happen soon — it's still on v4.51 and
   missing G22 convergence.

---

*sporeGate 155n G22 validation AAR — single-process merge validated, 5/10
divergences resolved, 11/11 HEALTHY, sovereign CI cloning fixed, sporePrint
auto-publish wired. Sole remaining gate to springs+gardens: J12 sub-builder wire.*
