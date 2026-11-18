# sporeGate Wave 155n Cascade AAR — P2 Golgi Hook Fix + 4 Primal Rebuild

**Date**: Jul 31, 2026 08:15 EDT | **Gate**: sporeGate | **Wave**: 155n
**Gate Health**: 11/11 HEALTHY | **Depot**: 35 binaries (16 musl + 4 gnu + 15 windows)

---

## P2 RESOLVED: Golgi Post-Receive Hook (3 Bugs Fixed)

The P2 escalation — "golgi post-receive hook not auto-firing" — was root-caused to **three
independent bugs** in the Forgejo hook infrastructure:

### Bug 1: Missing Post-Receive Dispatcher
Git only executes `hooks/post-receive`, not files inside `hooks/post-receive.d/`. The
`30-sovereign-ci` script was correctly installed in `post-receive.d/` but no dispatcher
script existed at the `post-receive` path. Every push was silently ignored.

**Fix**: Created `hooks/post-receive` dispatcher that iterates and executes all scripts in
`hooks/post-receive.d/`. Installed in all 20 repos on golgiBody.

### Bug 2: Repository Name Case Mismatch
Forgejo stores bare repos as lowercase (`biomeos.git`), so `basename` yields `biomeos`.
The manifest uses camelCase (`[repos.biomeOS]`). The `grep` was case-sensitive → no match
→ "not a primal repo" → skip.

**Fix**: Changed `grep` to `grep -i` for case-insensitive manifest lookup.

### Bug 3: Category Value Mismatch
Manifest has `category = "primal"` (singular). Hook grepped for `"primals"` (plural) →
no match → skip.

**Fix**: Changed grep pattern to `'"primal'` to match both `"primal"` and `"primals"`.

### Verification
- Simulated post-receive dispatch as `git` user on golgiBody
- Syslog confirmed: `Triggering sovereign CI: biomeos commit=999044e78f51 on sporeGate`
- SSH from golgi→sporeGate accepted: `Accepted publickey for root from 10.13.37.1`
- Full E2E test with squirrel: build → sandbox PASS → depot push → golgi sync → **all automated**

---

## Cascade Summary

### Repos Pulled (4 with new commits)

| Repo | Old HEAD | New HEAD | Key Changes |
|------|----------|----------|-------------|
| biomeOS | `0e45262` | `999044e7` | 5-tier binary discovery (P2 socket evap final), 14 unused deps removed, registry perf |
| cellMembrane | `0cfcce5` | `301e236` | init-scope socket discovery, gate identity 3→1, plasmid smart split (-310L) |
| petalTongue | `71c95c7` | `b135400` | modern idiom pass, debris audit |
| squirrel | `acbe09e` | `4bcf79ed` | clippy deep debt (0 warnings), universal-constants, Cargo.lock purge, 7138 tests |

No new commits: bearDog, songBird, toadStool (all STANDBY per blurb).
wateringHole: 5 new commits (squirrel status + blurb update + freshness).

### Builds Completed

| Primal | musl | gnu | windows |
|--------|------|-----|---------|
| biomeOS (999044e) | OK (3m15s) | OK (3m17s) | OK (4m18s) |
| cellMembrane (301e236) | OK (1m11s) | — | OK (1m05s) |
| petalTongue (b135400) | OK (2m41s) | — | OK (1m40s) |
| squirrel (4bcf79e) | OK (2m09s) | — | OK (1m39s) |

All builds clean. No errors.

### Depot State

- **Local depot**: 35 binaries, all BLAKE3 verified, checksums.toml regenerated
- **Golgi depot**: synced via rsync (44MB delta), verified 16+4+15 = 35
- **Sovereign CI push**: squirrel E2E test pushed updated depot to golgi with fresh checksums

---

## Gate Health: 11/11 HEALTHY

```
sporeGate (x86_64-unknown-linux-musl) — HEALTHY
  [OK] depot.integrity: 16 verified, 0 hash mismatch, 0 missing
  [OK] mesh.reachability: 3 peers, 3 reachable
  [OK] primals.alive: 13/13 primals alive
  [OK] depot.freshness: 13/13 binaries present, oldest 1d
  [OK] sovereignty.s1_tls: OPERATIONAL — depot.primals.eco 200
  [OK] sovereignty.s2_relay: federation:REACHABLE, RustDesk:hbbs=OK,hbbr=OK
  [OK] sovereignty.s3_content: OPERATIONAL — depot serving 8459KB
  [OK] sovereignty.s4_auth: RESPONDING — beardog reachable (via neuralAPI)
  [OK] rootpulse.ledger: advisory OK
  [OK] vcs.parity: 0 repos checked, 0 drifted
  [OK] service.crash-loop: 14 services scanned, no crash-loops
```

---

## Remaining Divergences

### P3-1: Sandbox False Positive for Broker Primals
`sovereign.ci.trigger` sandbox validation still fails for biomeOS because it's an
orchestrator that needs the full NUCLEUS composition to respond to health probes. The
`ServerContract` fix handles `gate.status` but not the sandbox code path.
**Impact**: biomeOS builds require manual deploy. All other primals work E2E.
**Owner**: cellMembrane team — need `sandbox::validate` to recognize broker primals.

### P3-2: GATE_NAME vs MEMBRANE_GATE_NAME
The new gate identity code in cellMembrane 301e236 uses `GATE_NAME` env var, but
`/etc/environment` has `MEMBRANE_GATE_NAME`. Both are set on sporeGate, but the inconsistency
should be unified by the code team.

### P3-3: /run/membrane Permission Reset
biomeOS restart resets `/run/membrane` to `0750 root:membrane`. The sporegate user needs
directory access for `gate.status`. Workaround: `tmpfiles.d` sets correct perms at boot,
and we manually fix after restarts. Long-term fix: biomeOS should `chmod 755` the directory
on bind.

### P3-4: cellMembrane Not in sources.toml
Still blocks sovereign CI self-rebuild. Manual `cargo build` workflow continues.

---

## What's Working

1. **Sovereign CI is fully automated for non-broker primals**: push → build → sandbox PASS →
   depot push → golgi sync. Zero human intervention.
2. **Golgi hook infrastructure**: dispatcher + 30-sovereign-ci installed in all 20 repos.
   Next push from any code team will auto-trigger builds.
3. **Gate identity consolidation**: cellMembrane 301e236 unified 3 divergent implementations
   into `resolve_gate_name_async()`. sporeGate correctly identified.
4. **biomeOS 999044e7**: 5-tier binary discovery means user-space deploys (steamGate) will
   find binaries in `~/.local/bin`, `~/.cargo/bin`, and `$PATH`.
5. **Depot**: 35 binaries across 3 targets, all BLAKE3 verified, golgi synced.

---

## Upstream Items for Overwatch

- **P2 golgi hook**: RESOLVED — 3 bugs fixed, E2E verified. Next code team push will
  auto-trigger sovereign CI.
- **steamGate readiness**: cellMembrane 301e236 shipped `resolve_socket_base()` for
  `MEMBRANE_INIT_SCOPE=user`. biomeOS 999044e7 probes `~/.local/bin`. GNU depot has 4
  binaries. Ready for Tower deployment.
- **blueGate J12**: membrane.exe in depot, all 15 Windows binaries current. Sub-builder
  enrollment is next whenever blueGate is ready.
