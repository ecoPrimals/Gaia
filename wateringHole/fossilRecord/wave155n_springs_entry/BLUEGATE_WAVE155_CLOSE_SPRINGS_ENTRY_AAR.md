# blueGate — Wave 155 Close + Springs+Gardens Entry AAR

**Gate**: blueGate | **Date**: 2026-08-01T12:50:00Z | **Wave**: 155n → post-155n
**Posture**: J12 LIVE E2E. NUCLEUS 13/13. Windows sub-builder operational. Ready for springs+gardens.

---

## WAVE 155 FINAL STATUS — blueGate

| Component | Status |
|-----------|--------|
| **NUCLEUS** | 13/13 primals running stable |
| **biomeOS** | v4.56.0 G22 (dual-protocol, 244 caps) |
| **membrane** | 0.1.0 (882ad09) — includes harvest.rs Windows fixes |
| **J12 sub-builder** | LIVE E2E — sporeGate dispatches, blueGate builds, BLAKE3 verified |
| **SSH enrollment** | Complete (sporegate-gate-v1 + sovereign-ci keys) |
| **Toolchain** | rustc 1.97.1 stable-x86_64-pc-windows-gnu |
| **Network** | LAN 192.168.4.210, WireGuard 10.13.37.12 |
| **Firewall** | Ports 22, 7700, 9901 open |
| **sshd** | Running/Automatic, PubkeyAuth, DEBUG3 |

### J12 Live E2E Proof (from sporeGate's AAR)
```
$ sudo ssh blueGate "membrane.exe plasmid.harvest --primal squirrel --force"
harvest: 1 built, 0 current, 0 skipped, 0 failed
  squirrel: 24269KB blake3=ebf3a1fafc277c8c commit=4bcf79ed (clone)
```

---

## WHAT WORKED (full Wave 155 arc)

### 1. Bootstrap → NUCLEUS (Wave 155i)
- Full 13-primal stack bootstrapped on Windows from zero
- All depot binaries (15 windows .exe) downloaded and verified
- Tower, Nest, Node Atomic all operational via TCP binding
- bearDog crypto (Ed25519 sign/verify), Provenance 7/7 chain, songBird IPC registry

### 2. Platform Detection Fix (Wave 155k → 155n)
- membrane.exe correctly reports `x86_64-pc-windows-gnu` (was reporting linux-musl)
- depot.integrity probes work
- Platform-aware build dispatch functions correctly

### 3. J12 Sub-Builder (Wave 155n)
- SSH enrollment complete (OpenSSH Server, admin authorized_keys, firewall)
- Live dispatch validated: sporeGate → SSH → blueGate → cargo build → BLAKE3 verify
- membrane plasmid.harvest + plasmid.build both operational via SSH
- Rust toolchain accessible in SSH sessions
- Env vars persist (MEMBRANE_GATE_NAME, ECOPRIMALS_ROOT, PATH)

### 4. Sovereign CI Integration
- harvest.rs updated with `.exe` extension handling for Windows targets
- ELF validation skipped for PE binaries
- `strip` skipped for Windows (no GNU strip equivalent needed)
- ecosystem_manifest.toml expanded: 14 primals × 4 targets

### 5. biomeOS G22 on Windows
- Single-process dual-protocol works
- API accessible on TCP (no UDS dependency for core function)
- 244 capabilities registered
- v4.56 stable across multiple restarts

---

## WHAT DIDN'T WORK

### Critical (caused >10 min debugging each)

| # | Issue | Root Cause | Resolution |
|---|-------|-----------|------------|
| 1 | **IP mismatch** (192.168.4.237 vs .210) | Stale peer discovery entry | sporeGate updated SSH config + cytoplasm.rs |
| 2 | **BOM encoding** silently rejects all SSH keys | PowerShell 5.1 `Set-Content -Encoding UTF8` adds BOM | Rewrote with `UTF8Encoding($false)` |
| 3 | **Admin-group key path** | Windows OpenSSH reads from ProgramData for admin users | Enrolled in correct file |
| 4 | **SSH user mismatch** (ecoPrimal vs user) | No standard user convention for Windows gates | sporeGate updated `User user` |
| 5 | **songBird compile-time gate** (Wave 155i) | `#[cfg(not(unix))]` killed IPC server on Windows | Built from source with 3 local patches |

### Operational (slowed progress)

| # | Issue | Impact | Resolution |
|---|-------|--------|------------|
| 6 | DISM install 5+ minutes | Appears hung, operator confusion | Documented timing |
| 7 | UAC blocks headless elevation | Can't automate first-touch setup | Must be interactive |
| 8 | membrane UDS probes | gate.status reports DEGRADED falsely | Known P3, TCP fallback needed |
| 9 | membrane --list hangs | Can't enumerate primals | Known P3, needs local manifest read |
| 10 | `--push` depot sync hangs | Can't push artifacts back from blueGate | P3 — pull-based sync works |
| 11 | Stale songBird PID file | Must manually delete on restart | Known P3 |
| 12 | rhizoCrypt port stealing | Binds 9202 + 9203, blocks sweetGrass | sweetGrass moved to 9213 |

---

## WHAT WE HAD TO AD-HOC

| # | Action | Why | Proper Solution |
|---|--------|-----|-----------------|
| 1 | Build songBird from source (3 patches) | Compile-time Unix gate killed Windows | Upstream: remove `#[cfg(not(unix))]` gate in orchestrator |
| 2 | Override `rust-toolchain.toml` with env var | Repo forces MSVC toolchain | Upstream: multi-target toolchain config |
| 3 | Manual no-BOM file write for SSH keys | PowerShell adds BOM by default | Ecosystem: always use `UTF8Encoding($false)` |
| 4 | Discovered admin key path by reading event log | Not documented anywhere | Ecosystem: Windows Bootstrap Runbook |
| 5 | Created admin setup script from scratch | No `membrane gate.enroll` command | Ecosystem: `membrane gate.enroll --ssh` |
| 6 | Manual IP discovery + correction | Static IP registration drifted | Ecosystem: gate heartbeat/self-report |
| 7 | sweetGrass port reassignment (9213) | rhizoCrypt steals adjacent port | Upstream: configurable port binding |
| 8 | FAMILY_SEED env var generation | bearDog silently exits without it | Document required env vars per primal |
| 9 | Stale PID file cleanup on every restart | songBird doesn't clean up on Windows | Upstream: PID file cleanup on startup |
| 10 | JSON-RPC PowerShell functions from scratch | No Windows health-check tooling | Ecosystem: PowerShell module or membrane probe |

---

## WINDOWS vs LINUX — COMPLETE DIVERGENCE MAP

| Category | Issue | Linux | Windows | Severity |
|----------|-------|-------|---------|----------|
| **Install** | SSH server | `apt install` (2s) | `Add-WindowsCapability` (5 min) | P4 |
| **Install** | Rust toolchain | `rustup` (same) | `rustup` (same, but MSVC vs GNU target choice) | P3 |
| **Encoding** | File writes | UTF-8 always | BOM added by default (PowerShell 5.1) | P2 |
| **Auth** | Key file location | `~/.ssh/authorized_keys` | Depends on admin group membership | P3 |
| **Auth** | File permissions | `chmod 600` | `icacls /inheritance:r` + specific SYSTEM/Admin grants | P3 |
| **Auth** | User model | Standard `ecoPrimal` user | No convention (here: `user`) | P2 |
| **Elevation** | Admin ops | `sudo` (scriptable) | UAC popup (requires desktop) | P3 |
| **IPC** | Transport | Unix Domain Sockets | Named pipes or TCP fallback | P2 |
| **IPC** | Health probes | UDS paths exist | UDS paths don't exist → false DEGRADED | P3 |
| **Process** | PID management | `/var/run/` standard | `C:\var\run\` non-standard, no cleanup | P3 |
| **Process** | Service management | `systemctl` | `Start-Service` + auto-start | P4 |
| **Network** | IP stability | Cloud/static IPs | DHCP, multiple interfaces, drift | P2 |
| **Network** | Port allocation | Primals bind expected ports | rhizoCrypt steals adjacent ports | P3 |
| **Build** | Binary format | ELF (strip, validate) | PE (.exe extension, no strip, no ELF check) | Fixed |
| **Build** | Toolchain selection | `stable-x86_64-unknown-linux-musl` | GNU vs MSVC choice, `rust-toolchain.toml` conflicts | P3 |
| **Logs** | SSH debugging | `journalctl -u sshd` | Event Viewer (no DEBUG by default) | P4 |
| **Env** | SSH session env | `/etc/environment`, `.bashrc` | User-level registry, DefaultShell config | P3 |
| **CLI** | Shell | bash (standard) | PowerShell (different escaping, quoting, encoding) | P3 |

---

## WHAT NEEDS TO EVOLVE — PRIORITY ORDER

### P1: Ecosystem Tooling
1. **`membrane gate.enroll --ssh`**: Automate the full SSH enrollment (keys, firewall, service, env, encoding)
2. **Windows Bootstrap Runbook**: Document BOM, admin keys, ACLs, UAC, user model, port config
3. **Gate heartbeat/self-report**: Gates push their own IP + status to mesh (no stale registries)

### P2: membrane Windows Parity
4. **TCP probe fallback**: `primals.alive` checks TCP endpoints, not UDS paths
5. **No-BOM file writes**: All membrane config/key generation must use no-BOM encoding
6. **`plasmid.harvest --list`**: Read manifest locally when IPC unavailable
7. **Depot sync return path**: Fix `--push` hang or implement pull-based sync

### P3: Primal Windows Parity
8. **songBird**: Remove `#[cfg(not(unix))]` gate in orchestrator (use universal-ipc)
9. **songBird**: PID file cleanup on startup / graceful shutdown
10. **rhizoCrypt**: Don't bind adjacent ports (configurable bind)
11. **bearDog**: Document `FAMILY_SEED` requirement clearly

### P4: Operational
12. **Standard user convention**: `ecoPrimal` user on all gates, or document per-gate
13. **Windows service wrappers**: Run primals as Windows Services for auto-start
14. **Pre-built Windows gate image**: OpenSSH + Rust + .local/bin pre-provisioned

---

## blueGATE ROLE IN SPRINGS+GARDENS

| Capability | Status | Used By |
|------------|--------|---------|
| **Windows sub-builder** | LIVE (J12 E2E proven) | sporeGate sovereign CI dispatch |
| **NUCLEUS 13/13** | Running stable | footPrint garden (any NUCLEUS gate) |
| **Build targets** | x86_64-pc-windows-gnu | All 14 primals buildable |
| **J12 → songBird IPC** | Future evolution | Deprecate SSH dispatch path |

### Immediate Readiness
- Receiving build dispatches from sporeGate ✓
- Building any primal for Windows target ✓
- BLAKE3 verification of built binaries ✓
- SSH session env + toolchain ✓

### Open Work
- `--push` return path (P3 — sporeGate can pull instead)
- songBird federation cross-gate (port 7700 open, awaiting mesh wire)
- footPrint garden deployment (if assigned)

---

## STATISTICS

| Metric | Value |
|--------|-------|
| Total bootstrap time (155i → 155n) | ~8 hours across 4 sessions |
| Issues encountered | 12 (5 critical, 7 operational) |
| Ad-hoc workarounds | 10 |
| Windows-specific divergences | 17 documented |
| Upstream fixes absorbed | 4 (platform detection, harvest.rs .exe, ELF skip, IP) |
| Local patches (songBird) | 3 (enrollment_crypto, server.rs, core/mod.rs) |
| Handoffs pushed | 8 documents |
| AARs pushed | 5 documents |

---

*blueGate Wave 155 CLOSED. J12 LIVE E2E. NUCLEUS 13/13. 17 Windows divergences
documented. 14 evolution items prioritized. Sub-builder operational for
springs+gardens. Receiving sporeGate dispatch. Ready for the next phase.*
