# blueGate Wave 155n — J12 SSH Enrollment AAR

**Gate**: blueGate | **Date**: 2026-08-01T00:30:00Z | **Wave**: 155n
**Scope**: J12 SSH key enrollment + E2E dispatch validation

---

## WHAT WORKED

### 1. OpenSSH Server via Windows Capability
- `Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0` installed correctly
- Service registered, starts automatically, key-based auth functional
- No manual configuration of `sshd_config` was needed (defaults work)

### 2. membrane.exe Accessible via SSH
- `plasmid.harvest --primal squirrel --dry-run` returns correct JSON via SSH
- `plasmid.build squirrel --dry-run` confirms target triple detection
- Env vars (`MEMBRANE_GATE_NAME`, `ECOPRIMALS_ROOT`) persist in SSH sessions
- `.local\bin` in PATH means membrane.exe resolves without full path

### 3. Rust Toolchain in SSH Context
- `rustc 1.97.1` (stable-x86_64-pc-windows-gnu) available
- `cargo 1.97.1` available
- Build capability confirmed (skunkBat 2.6 MB from source in prior session)

### 4. NUCLEUS 13/13 Stable
- All primals start and hold (beardog through biomeos)
- TCP binding on all primals (no UDS dependency for primal startup)
- Fresh depot binaries from Wave 155k/155n

### 5. Firewall Rules
- Three rules created cleanly via `New-NetFirewallRule`
- Ports 22, 7700, 9901 open for LAN inbound

---

## WHAT DIDN'T WORK

### 1. Windows Capability Install Speed (P4 — UX)
- `Add-WindowsCapability` took ~5 minutes (TrustedInstaller + TiWorker pipeline)
- No progress indicator — appears hung
- Compare: `apt install openssh-server` takes <5 seconds on Linux
- **Impact**: Operator confusion during bootstrap. No fix possible (OS limitation).

### 2. UAC Elevation Blocking Non-Interactive Scripts (P3)
- `Start-Process -Verb RunAs` requires interactive UAC approval
- Cannot be automated in headless/SSH context
- The admin setup script hung until manually approved
- **Recommendation**: Document that initial setup MUST be done interactively from desktop.
  Future automation should use a Windows Service or Task Scheduler (runs as SYSTEM).

### 3. Admin Group `authorized_keys` Path (P3 — Windows SSH Gotcha)
- Users in `Administrators` group have keys read from `C:\ProgramData\ssh\administrators_authorized_keys`
- NOT from `~\.ssh\authorized_keys` (which is the obvious/documented location)
- This is a `Match Group administrators` rule in the default `sshd_config`
- **Impact**: 15 minutes debugging "Permission denied" with correct keys in wrong file.
- **Recommendation**: Document prominently in ecosystem Windows bootstrap guide.

### 4. SSH User Mismatch: `ecoPrimal` vs `user` (P2 — Blocks Live E2E)
- sporeGate's dispatch uses `ecoPrimal@192.168.4.237`
- blueGate's user is `user` (standard Windows user)
- No `ecoPrimal` user exists on this machine
- **Fix**: sporeGate updates SSH config to `User user`. Simple one-line change.

### 5. membrane.exe UDS Probes on Windows (P3 — Known)
- `gate.status` reports `primals.alive: 0/13` even with all primals running
- Probes check Unix Domain Socket paths that don't exist on Windows
- `sovereignty.s4_auth` tries UDS path to bearDog instead of TCP 127.0.0.1:9100
- **Impact**: Gate health reporting is inaccurate. Doesn't affect actual build dispatch.
- **Status**: Known issue from prior waves. TCP probe fallback needed in membrane.

### 6. `plasmid.harvest --list` Hangs (P4)
- The `--list` flag appears to block indefinitely (likely waiting on UDS/IPC)
- `--primal <name> --dry-run` works fine
- **Impact**: Minor UX. Operators can't enumerate available primals without knowing names.

---

## DIVERGENCES FROM BLURB

| # | Blurb Says | Reality | Resolution |
|---|-----------|---------|------------|
| 1 | SSH user `ecoPrimal` | Actual user is `user` | sporeGate SSH config update |
| 2 | `gate.status` healthy after enrollment | Reports DEGRADED (UDS probes) | Known P3; TCP probe fallback needed |
| 3 | Implied seamless capability install | 5-minute DISM install + UAC | Document as expected for Windows |
| 4 | `plasmid.harvest --primal skunkBat` | Case-sensitive; needs `skunkbat` or manifest lookup | P4 UX; document binary_name convention |

---

## WHAT NEEDS TO EVOLVE

### Immediate (sporeGate — unblocks live E2E)
1. Update SSH config: `Host blueGate` → `User user` (currently `ecoPrimal`)
2. Verify dispatch: `ssh blueGate "membrane.exe plasmid.harvest --primal squirrel --dry-run"`

### Short-term (membrane — Windows parity)
3. `primals.alive` probe: Add TCP health endpoint fallback (check 127.0.0.1:PORT)
4. `sovereignty.s4_auth`: TCP fallback to bearDog (127.0.0.1:9100)
5. `plasmid.harvest --list`: Don't block on IPC if manifest is available locally

### Medium-term (ecosystem — Windows bootstrap UX)
6. Windows Bootstrap Runbook: Document the admin-group authorized_keys path
7. One-shot admin setup: Package as a single `.ps1` that self-elevates once
8. Service registration: Consider running primals as Windows Services for auto-start
9. Auto-start on boot: Task Scheduler or NSSM wrapper for NUCLEUS stack

### Infrastructure (depot integration)
10. `--push` artifact return path: blueGate needs write access to depot
11. `checksums.toml` integration: Built binaries need BLAKE3 hash + manifest update
12. Depot sync path: SSH rsync to golgiBody or HTTP PUT to depot API

---

## REGISTRATION UPDATE

```toml
[gates.blueGate]
status = "J12_SSH_ENROLLED"
nucleus = "13/13"
biomeos = "v4.56.0"
membrane = "0.1.0 (edb7f4d)"
arch = "x86_64-pc-windows-gnu"
rust = "1.97.1"
ssh_user = "user"              # NOT ecoPrimal
ssh_port = 22
lan_ip = "192.168.4.237"
firewall_open = [22, 7700, 9901]
authorized_keys = ["sporegate-gate-v1", "sovereign-ci@sporeGate", "blueGate@primals.eco"]
keys_location = "C:\\ProgramData\\ssh\\administrators_authorized_keys"
```

---

## TIMELINE

```
20:11 — Cascade pull: sporeGate J12 AAR received (2 SSH keys provided)
20:12 — authorized_keys created (user .ssh dir)
20:13 — Admin setup script created (5 steps)
20:14 — UAC approved, Add-WindowsCapability starts (SLOW)
20:19 — OpenSSH Server installed (sshd.exe lands)
20:20 — sshd started (Running/Automatic)
20:21 — Firewall rules created (22, 7700, 9901)
20:22 — Discovered admin-group authorized_keys path
20:23 — Keys written to C:\ProgramData\ssh\administrators_authorized_keys
20:24 — ACLs fixed, sshd restarted
20:25 — Local SSH test: PASS (key auth + membrane.exe + env vars)
20:26 — E2E dispatch simulation: PASS (harvest, build, toolchain)
20:28 — NUCLEUS 13/13 started
20:30 — Handoff written, AAR complete
```

Total elapsed: ~19 minutes (5 min was Windows servicing install)

---

*blueGate 155n J12 AAR — SSH enrollment COMPLETE in 19 min. 3 keys enrolled.
E2E dispatch validated via localhost. Single blocker: sporeGate SSH config needs
`User user` (not `ecoPrimal`). Once fixed, live cross-gate dispatch is immediate.
5 P3/P4 issues documented for Windows parity evolution.*
