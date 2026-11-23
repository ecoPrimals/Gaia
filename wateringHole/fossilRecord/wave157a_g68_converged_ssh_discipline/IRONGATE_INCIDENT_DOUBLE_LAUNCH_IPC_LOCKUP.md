# ironGate INCIDENT: Double-Launch IPC Lockup — Wave 157a

**Date**: 2026-08-08 10:38 EDT
**Gate**: ironGate (10.13.37.7)
**Severity**: P1 — forced hardware reboot required
**From**: ironGate hardware team
**To**: eastGate overwatch, all gate teams

---

## Incident Summary

ironGate locked up requiring a forced reboot. Root cause: **two full NUCLEUS compositions running simultaneously**, fighting over IPC sockets. This is the **second occurrence** of this failure mode on ironGate.

---

## Root Cause

The `membrane-nucleus@*.service` systemd user services auto-start 12 primals from `/usr/local/bin/` on boot/login. During the earlier session, we manually launched a second set of 13 primals via `nohup ~/.local/bin/<primal> server --socket ...` — creating **26+ processes** all doing JSON-RPC IPC on overlapping socket namespaces in `/run/user/1000/biomeos/`.

The contention pattern:
1. systemd services bind sockets (e.g., `beardog-default.sock`, `btsp.sock`)
2. Manual launch tries to bind same capability sockets → some succeed (new paths), some get "address in use"
3. songBird discovers both sets and routes IPC to both
4. Cross-talk and socket storms saturate CPU IPC bandwidth
5. System becomes unresponsive → hard lockup → forced reboot

---

## Why This Keeps Happening

1. **No guard against double-launch**: Neither `plasmidbin launch` nor manual startup checks for existing membrane services
2. **Two binary locations**: `/usr/local/bin/` (systemd) vs `~/.local/bin/` (depot pull) — easy to forget which is "live"
3. **Socket namespace collision**: Both sets use `/run/user/1000/biomeos/` with primal auto-naming
4. **Silent success**: The second set partially starts (sockets that aren't taken), giving a false "35/35 HEALTHY" while the system degrades

---

## Prevention — Required Changes

### Immediate (gate teams)

1. **NEVER manually launch primals when systemd services are active**
   - Check: `systemctl --user list-units 'membrane-nucleus@*' --state=running`
   - If services exist, use `systemctl --user restart membrane-nucleus@<primal>.service`

2. **Unify binary path**: systemd services should run from `~/.local/bin/` (depot path), not `/usr/local/bin/`
   - Update service templates: `ExecStart=%h/.local/bin/<primal> server`
   - Or symlink: `/usr/local/bin/<primal> → ~/.local/bin/<primal>`

3. **Pre-flight check in scripts**: Any startup script must `pgrep -f "<primal> server"` before launching

### Upstream (plasmidBin / biomeOS)

4. **`plasmidbin launch` should refuse if membrane services are running**
5. **`biomeos serve` should detect and warn on duplicate primal PIDs**
6. **PID file enforcement**: Each primal should write a PID file and refuse to start if a live process holds it
7. **Socket-level guard**: `bind()` failure on UDS should be FATAL with a clear message naming the conflicting PID

---

## Resolution

- Forced reboot at ~10:33 EDT
- Post-reboot: systemd services auto-started cleanly (12/12, 60 MB RSS)
- Updated 4 stale `/usr/local/bin/` binaries to G68 depot versions
- Installed 2 missing binaries (sourDough, bingoCube)
- Verified 29/29 HEALTHY, load 1.89 on 32 cores
- **No data loss** (CAS on /mnt/nestgate, ext4 journal clean)

---

## Affected Gates

Any gate with `membrane-nucleus@*.service` systemd units AND manual launch workflows is vulnerable. Known:
- **ironGate**: Hit twice (this incident + prior)
- **All gates**: Potentially vulnerable if operator runs `plasmidbin launch` or manual `nohup` while services are active

---

## Action Items

| Action | Owner | Priority |
|--------|-------|----------|
| Add pre-flight PID check to `plasmidbin launch` | plasmidBin team | P1 |
| Update membrane-nucleus@ ExecStart to `%h/.local/bin/` | gate teams | P2 |
| Add duplicate-detection warning to `biomeos serve` | biomeOS team | P2 |
| Document "systemd vs manual" in gate ops runbook | wateringHole | P3 |
| PID file + socket bind FATAL on conflict | primal teams (upstream) | P3 |

---

*INCIDENT: Double-launch IPC lockup on ironGate. Forced reboot. Second occurrence. Root cause: 26+ primal processes contending on socket namespace. Prevention: never manual-launch over systemd services; unify binary path; add pre-flight guards upstream.*
