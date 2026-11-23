# blueGate Wave 155n — J12 SSH Enrollment Full AAR

**Gate**: blueGate | **Date**: 2026-08-01T01:56:00Z | **Wave**: 155n
**Scope**: J12 SSH key enrollment session — the "last thread" before live E2E dispatch
**Outcome**: SSH server operational, keys enrolled, local E2E validated. **Blocked on IP mismatch** (sporeGate has stale IP).

---

## EXECUTIVE SUMMARY

The J12 SSH enrollment session exposed a layered set of Windows-specific operational
issues that don't exist on Linux gates. The core SSH wire is complete and locally
validated, but live cross-gate dispatch is blocked by a stale IP registration
(`192.168.4.237` vs actual `192.168.4.210`). This AAR documents the full session:
what worked, what broke, what we had to ad-hoc, and what the ecosystem needs to
evolve for Windows gate parity.

---

## WHAT WORKED

### 1. OpenSSH Server Installation
- `Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0` installed correctly
- Service registered, auto-start configured, sshd runs stable
- Default `sshd_config` works without modification (beyond logging)

### 2. Key-Based Auth (Local)
- `administrators_authorized_keys` path correctly used for admin-group users
- All 3 keys (sporegate-gate-v1, sovereign-ci, blueGate local) validate locally
- Fingerprints verified: `SHA256:9XuzdZ12AR7Vbcd1kT5cAGLwzM2IT6syVWD9GLUbBYA` (sporegate-gate-v1)

### 3. membrane.exe via SSH
- `plasmid.harvest --primal squirrel --dry-run` returns correct JSON via SSH
- `plasmid.build squirrel --dry-run` confirms target triple detection
- Environment variables persist in SSH sessions (`MEMBRANE_GATE_NAME`, `ECOPRIMALS_ROOT`)
- `.local\bin` in PATH means membrane resolves without full path

### 4. Rust Toolchain Accessible via SSH
- `rustc 1.97.1` (stable-x86_64-pc-windows-gnu) + `cargo 1.97.1`
- Host triple correctly identified: `x86_64-pc-windows-gnu`
- Build capability proven (skunkBat 2.6 MB from source in prior session)

### 5. NUCLEUS Stack
- 13/13 primals running stable throughout session
- Fresh depot binaries from Wave 155k/155n
- biomeOS v4.56.0 (G22 complete)

### 6. Firewall Rules
- Three rules created cleanly: ports 22, 7700, 9901
- Both auto-created OpenSSH rule and our custom rules coexist

---

## WHAT DIDN'T WORK

### 1. IP Address Mismatch — THE ACTUAL BLOCKER (P1)

**Problem**: sporeGate registered blueGate as `192.168.4.237` in their sub-builder
table and SSH config. blueGate's actual LAN IP is `192.168.4.210`.

**Impact**: sporeGate was SSHing to a completely different device on the LAN.
Their keys were "offered and rejected" because they were talking to the wrong
machine. Our sshd log showed zero external connection attempts.

**Root Cause**: The IP was likely pulled from an older DHCP lease or manually
entered incorrectly during initial mesh registration.

**Fix Required**: sporeGate updates SSH config:
```
Host blueGate
    HostName 192.168.4.210    # was 192.168.4.237
    User user
```

Or use the stable WireGuard overlay: `HostName 10.13.37.12`

**Ecosystem Lesson**: Gates should self-report their IP via a heartbeat or
`gate.status` probe. Static IP registration in config files drifts.

---

### 2. SSH Username Mismatch (P2 — now documented)

**Problem**: sporeGate's sub-builder dispatch connects as `ecoPrimal@host`.
blueGate's Windows user account is `user`.

**Impact**: Even with correct IP, `ecoPrimal` doesn't exist → immediate reject.

**Fix Required**: sporeGate SSH config: `User user`

**Ecosystem Lesson**: The ecosystem manifest needs a `ssh_user` field per gate.
The sub-builder table currently only has `ssh_host` which delegates to SSH config.

---

### 3. UTF-8 BOM Corruption of authorized_keys (P2 — fixed)

**Problem**: PowerShell's `Set-Content -Encoding UTF8` writes a BOM (3 bytes:
`0xEF 0xBB 0xBF`) at the start of the file. OpenSSH sees the first key line as
`<BOM>ssh-ed25519...` which doesn't match the key format → silently rejects ALL
keys in the file.

**Impact**: 15+ minutes debugging "keys enrolled but rejected" with correct
fingerprints, correct ACLs, correct file path.

**Fix Applied**: Rewrote with `[System.Text.UTF8Encoding]($false)` (explicit
no-BOM). Verified first byte = 115 (`s`).

**Ecosystem Lesson**: Any Windows automation writing SSH key files MUST use
no-BOM encoding. Add to Windows bootstrap runbook prominently.

---

### 4. Admin-Group authorized_keys Path (P3 — Windows SSH gotcha)

**Problem**: Users in the `Administrators` group have keys read from
`C:\ProgramData\ssh\administrators_authorized_keys`, NOT from `~\.ssh\authorized_keys`.
This is a `Match Group administrators` block in the default `sshd_config`.

**Impact**: Initial key enrollment went to `~\.ssh\authorized_keys` which sshd
ignores for admin users. Took investigation to discover the override.

**Ecosystem Lesson**: Document that Windows OpenSSH has TWO key paths depending
on group membership. Always check `whoami /groups` during enrollment.

---

### 5. Windows Capability Install Speed (P4 — UX)

**Problem**: `Add-WindowsCapability` takes 3-7 minutes (DISM servicing pipeline).
No progress indicator. Appears completely hung.

**Impact**: Operator confusion. No workaround possible (OS limitation).

**Ecosystem Lesson**: Document expected timing. Consider pre-installing OpenSSH
in the Windows gate base image/provisioning script.

---

### 6. UAC Blocking Non-Interactive Elevation (P3)

**Problem**: `Start-Process -Verb RunAs` requires interactive UAC approval.
Cannot automate from headless/SSH context. The admin setup script hung until
manually approved at the desktop.

**Impact**: Initial setup MUST be done interactively. Future remote management
cannot elevate without pre-configuration.

**Ecosystem Lesson**: First-time setup requires physical/RDP access. Document
that Windows gates need a "first-touch" interactive bootstrap before they can
be remotely managed. Consider running sshd as SYSTEM + scheduled tasks for
future automation.

---

### 7. membrane.exe Hangs on Certain Commands (P3 — known)

**Problem**: `plasmid.harvest --list` and `plasmid.harvest --help` hang
indefinitely. They attempt to contact bearDog via UDS which doesn't exist on
Windows.

**Impact**: Cannot enumerate available primals without prior knowledge of names.
Doesn't block dispatch (specific primal names work fine).

**Fix Needed**: membrane should fall back to reading the ecosystem manifest
directly when IPC is unavailable.

---

### 8. gate.status Reports DEGRADED Despite Healthy Stack (P3 — known)

**Problem**: `primals.alive: 0/13` even with all primals running. Probes check
Unix Domain Socket paths that don't exist on Windows. `sovereignty.s4_auth`
tries UDS to bearDog instead of TCP.

**Impact**: Gate health reporting is inaccurate for Windows gates. Doesn't affect
actual build dispatch functionality.

**Fix Needed**: TCP probe fallback in membrane for all primal health checks.

---

## WHAT WE HAD TO AD-HOC

| # | Ad-Hoc Action | Why | Proper Solution |
|---|---------------|-----|-----------------|
| 1 | Manual BOM-free file write with `UTF8Encoding($false)` | PowerShell's default encoding adds BOM | Ecosystem tooling should always use no-BOM writes |
| 2 | Discovered admin-group key path by reading sshd event log | Not documented in ecosystem | Add to Windows bootstrap runbook |
| 3 | Created admin setup script (`blueGate-j12-admin-setup.ps1`) | No ecosystem-provided Windows provisioning | Create `membrane gate.enroll --ssh` command |
| 4 | Killed hung elevated processes | UAC + DISM slowness | Document expected timings |
| 5 | Manual IP discovery via `Get-NetIPAddress` | Stale IP in sporeGate's registry | Self-reporting heartbeat or `gate.register` command |
| 6 | Set env vars with `[Environment]::SetEnvironmentVariable(..., "User")` | SSH sessions need persistent env | Add to membrane gate enrollment process |
| 7 | Checked `whoami /groups` to understand key path routing | Windows SSH has non-obvious auth path logic | Document in ecosystem |
| 8 | Enabled DEBUG3 logging to diagnose remote auth | Insufficient visibility into connection failures | Default to at least INFO logging |

---

## WINDOWS vs LINUX — ISSUES UNIQUE TO WINDOWS

| Issue | Linux Gates | Windows (blueGate) | Severity |
|-------|-------------|---------------------|----------|
| SSH server install | `apt install openssh-server` (2s) | `Add-WindowsCapability` (3-7 min) | P4 UX |
| Key file encoding | UTF-8 always, no BOM issues | PowerShell adds BOM → silent key rejection | P2 |
| Admin key path | `~/.ssh/authorized_keys` always | Depends on group membership (ProgramData vs home) | P3 |
| File ACLs | `chmod 600` | `icacls /inheritance:r /grant SYSTEM/Admins` | P3 |
| Elevation | `sudo` (scriptable) | UAC popup (requires interactive desktop) | P3 |
| IPC transport | Unix Domain Sockets native | Named pipes or TCP fallback required | P2 |
| Service management | `systemctl start sshd` | `Start-Service sshd` (similar but different tooling) | P4 |
| Env vars in SSH | `/etc/environment` or `.bashrc` | User-level registry + DefaultShell config | P3 |
| primal health probes | UDS paths exist naturally | UDS paths don't exist → false DEGRADED | P3 |
| IP reporting | Stable (cloud/static) | DHCP lease can drift, multiple interfaces | P2 |
| Log access | `journalctl -u sshd` | Event Viewer or custom log file (no DEBUG by default) | P4 |
| User model | `ecoPrimal` user standard | No standard; depends on installer (here: `user`) | P2 |

---

## WHAT NEEDS TO EVOLVE

### Immediate (unblocks J12 live E2E)
1. **sporeGate**: Update SSH config → `HostName 192.168.4.210` + `User user`
2. **sporeGate**: Retry dispatch after IP fix
3. **Ecosystem manifest**: Add `lan_ip` and `ssh_user` fields to gate registry

### Short-term (Windows gate parity)
4. **membrane**: `gate.register` command that self-reports IP, user, arch, capabilities
5. **membrane**: TCP fallback for all primal health probes (no UDS dependency)
6. **membrane**: `plasmid.harvest --list` should read manifest locally, not require IPC
7. **Ecosystem**: Windows Bootstrap Runbook (BOM, admin keys, ACLs, UAC, encoding)
8. **membrane**: No-BOM file writes in any key/config generation code

### Medium-term (operational maturity)
9. **Ecosystem**: Gate heartbeat/self-report (periodic IP + status push to mesh)
10. **Ecosystem**: Standard SSH user convention for Windows gates (or auto-create `ecoPrimal`)
11. **membrane**: `gate.enroll --ssh` command that handles full enrollment (keys, firewall, service, env)
12. **Ecosystem**: Pre-built Windows gate image with OpenSSH pre-installed
13. **membrane**: Enable INFO-level sshd logging by default during enrollment

---

## REGISTRATION UPDATE

```toml
[gates.blueGate]
status = "J12_SSH_ENROLLED_AWAITING_IP_FIX"
nucleus = "13/13"
biomeos = "v4.56.0"
membrane = "0.1.0 (edb7f4d)"
arch = "x86_64-pc-windows-gnu"
rust = "1.97.1"
lan_ip = "192.168.4.210"      # CORRECTED from 192.168.4.237
wireguard_ip = "10.13.37.12"
ssh_user = "user"             # NOT ecoPrimal
ssh_port = 22
firewall_open = [22, 7700, 9901]
sshd_log_level = "DEBUG3"    # temporarily elevated for diagnostics
keys_enrolled = ["sporegate-gate-v1", "sovereign-ci@sporeGate", "blueGate@primals.eco"]
keys_location = "C:\\ProgramData\\ssh\\administrators_authorized_keys"
j12_local_validated = true
j12_live_e2e = "BLOCKED — sporeGate has wrong IP"
```

---

## TIMELINE

```
20:11 — Cascade: pulled sporeGate J12 AAR (2 SSH keys, dispatch instructions)
20:12 — authorized_keys created in ~/.ssh (wrong path for admin users)
20:13 — Admin setup script created
20:14 — UAC approved, Add-WindowsCapability starts
20:19 — OpenSSH Server installed (5 min DISM)
20:20 — sshd started (Running/Automatic)
20:21 — Firewall rules created (22, 7700, 9901)
20:22 — SSH test FAILS — discovered admin-group key path override
20:23 — Keys written to C:\ProgramData\ssh\administrators_authorized_keys
20:24 — SSH test WORKS (local key accepted)
20:25 — E2E dispatch simulation via localhost: PASS
20:28 — NUCLEUS 13/13 started
20:30 — Handoff + AAR pushed to wateringHole
20:37 — sporeGate reports: still Permission denied
20:38 — Verified keys + ACLs correct, suspected BOM
20:40 — Rewrote file without BOM, SSH works locally
20:41 — sporeGate reports: still failing
20:43 — Enabled DEBUG3 logging
20:45 — Local test: accepted (line 3). No external entries in log.
20:47 — sporeGate attempt at 00:47:42 UTC — NOT IN OUR LOG
20:48 — Discovered IP mismatch: they have .237, we are .210
20:48 — Informed sporeGate: wrong IP is the blocker
21:56 — Final AAR written
```

**Total session: ~1h 45m** (should have been 10 minutes on Linux)

---

## CONCLUSION

The J12 SSH enrollment is functionally complete on blueGate's side. The
infrastructure works: sshd runs, keys authenticate, membrane responds via SSH,
toolchain is available, NUCLEUS is healthy.

The session took 10x longer than it should have due to cascading Windows-specific
issues (BOM encoding, admin key path, DISM install time, UAC) and a stale IP
registration that caused both teams to debug auth when the real problem was
network routing.

**Single remaining action**: sporeGate updates their SSH config from
`192.168.4.237` to `192.168.4.210` (or `10.13.37.12` via WireGuard). Once
done, live E2E dispatch should work immediately — everything else is validated.

---

*blueGate 155n J12 full AAR — SSH enrollment COMPLETE. 10 issues documented
(2 P1/P2 blockers: wrong IP + wrong username on sporeGate's side; 1 P2 fixed:
BOM encoding). 12 evolution items for Windows gate parity. NUCLEUS 13/13.
Session: 1h45m. Awaiting sporeGate IP fix for live E2E.*
