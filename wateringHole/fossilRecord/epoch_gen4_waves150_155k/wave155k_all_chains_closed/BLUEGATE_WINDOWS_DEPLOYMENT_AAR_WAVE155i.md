# blueGate Windows Deployment AAR — Wave 155i

**Date**: Jul 29, 2026 12:50 EDT | **Wave**: 155i | **From**: blueGate
**Gate**: blueGate | **OS**: Windows 10.0.26200 (Win32NT)
**Purpose**: Comprehensive AAR of first Windows gate deployment. All findings
are upstream-actionable. This is a new OS domain — Linux assumptions exposed
throughout the stack.

---

## EXECUTIVE SUMMARY

blueGate is the first full Windows deployment in the ecoPrimals mesh. The
bootstrap succeeded (40/40 repos synced, mesh live, SSH live, 2/3 Tower
primals healthy), but exposed **15 Windows-specific issues** across four
categories: toolchain, filesystem, IPC transport, and operational. The
critical finding is that songBird has a compile-time platform gate that
blocks Windows — but the fix is narrow because the transport layer
(`songbird-universal-ipc`) already ships complete Windows named pipe and
TCP fallback implementations. They just aren't wired into the orchestrator.

**Classification**:
- 2 P0 (songBird platform gate, admin elevation for WireGuard)
- 5 P1 (filesystem, credential manager, transport fallback)
- 8 P2 (operational, documentation, quality-of-life)

---

## CATEGORY 1: TOOLCHAIN & SPIN-UP

### T1. Git not pre-installed (P2)

**What happened**: Fresh Windows has no `git`. The blurb's Phase 1 scripts
assume `git` is available and use bash syntax.

**Fix**: Add to blurb Phase 0 for Windows:
```powershell
winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements
```

**Consideration**: `winget` is available on Windows 10 1709+ and Windows 11.
Older Windows versions need manual Git install.

### T2. Rust not pre-installed (P2)

**What happened**: Rust toolchain absent. Needed for source builds if depot
binaries are stale or need recompilation.

**Fix**: Add to blurb Phase 2 for Windows:
```powershell
winget install --id Rustlang.Rustup -e --accept-source-agreements --accept-package-agreements
rustup default stable
```

**Result**: Rust 1.97.1 stable (x86_64-pc-windows-msvc) installed cleanly.
Note: this is the MSVC target, not the GNU target that depot binaries use.
Cross-target may be needed: `rustup target add x86_64-pc-windows-gnu`.

### T3. PATH not refreshed after installs (P2)

**What happened**: After `winget install Git.Git`, the current PowerShell
session doesn't see `git` until PATH is manually refreshed:
```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

**Consideration**: This affects any agent or automated session. Human users
opening a new terminal get it automatically. Agent sessions (Cursor, CI)
must refresh PATH after installs.

### T4. Blurb scripts are bash, not PowerShell (P2)

**What happened**: Phase 1 sync scripts use bash syntax (`for d in ...; do`,
`[ -d ... ]`, `$(basename ...)`, etc.). Windows gates need PowerShell
equivalents.

**Recommendation**: Add a "Windows PowerShell" variant to Steps 1a–1f in the
blurb, or provide a `gate-sync.ps1` script in `plasmidBin/`.

---

## CATEGORY 2: FILESYSTEM & GIT

### F1. Colon in filenames — NTFS prohibition (P1)

**What happened**: 6 files in `springs/primalSpring/benchScale/tower_shadow/`
have IP:port format colons in filenames:
```
tower-atomic_10_13_37_2:7700_20260723T204413.json
tower-atomic_10_13_37_5:7700_20260723T154353.json
tower-atomic_192_168_4_244:7700_20260723T203912.json
wireguard_10_13_37_2:7700_20260723T204413.json
wireguard_10_13_37_5:7700_20260723T154353.json
wireguard_192_168_4_244:7700_20260723T203912.json
```

Windows NTFS prohibits `:` in filenames (reserved for NTFS Alternate Data
Streams). Git creates truncated files at the colon point, resulting in 12
permanent dirty entries (6 deleted tracked + 6 untracked fragments).

**Fix**: Rename upstream — replace `:` with `_` or `-`. Affects
`primalSpring` repo only. Benchmark data, no code impact.

**Impact**: Any Windows gate (blueGate, swiftGate, northGate) hits this.

### F2. MAX_PATH 260-char limit (P1)

**What happened**: `infra/fossilRecord` checkout failed — deeply nested
archive paths under `misc/archive-pre-2026/` exceed 260 characters.

**Fix applied**: `git config --global core.longpaths true` + force checkout.
All 10,905 files recovered.

**Upstream action**: Add `core.longpaths=true` to Windows gate instructions.
Also recommend enabling OS-level long paths (requires admin):
```powershell
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1
```

### F3. git-credential-manager blocking in non-interactive sessions (P1)

**What happened**: Git for Windows ships with Git Credential Manager (GCM)
which tries to pop an interactive authentication dialog. In agent sessions
(Cursor, SSH, CI), this blocks indefinitely — the process hangs waiting for
a GUI that never appears.

**Workaround applied**:
```powershell
$env:GIT_TERMINAL_PROMPT = "0"
$env:GCM_INTERACTIVE = "never"
```

**Upstream action**: Add these env vars to Windows gate instructions, or
configure git globally:
```
git config --global credential.interactive never
```

For public HTTPS repos this is unnecessary (no auth needed), but GCM doesn't
know that until it tries.

### F4. ssh-keyscan known_hosts format mismatch (P1)

**What happened**: `ssh-keyscan -p 2222 git.primals.eco` writes entries in
`[host]:port` format, but OpenSSH for Windows checks without port brackets
when using SSH config aliases. The host key was in known_hosts but couldn't
be verified.

**Fix applied**: Used `StrictHostKeyChecking=accept-new` on first connection.

**Upstream action**: Add explicit note to blurb Phase 0b-3:
```powershell
ssh -o StrictHostKeyChecking=accept-new -T git@git.primals.eco
```

### F5. sporePrint empty repo (P2)

`infra/sporePrint` is an empty repository on Forgejo (no commits). Clones
successfully but has no branch, no HEAD, no working tree. Harmless but
confusing for automated inventory checks.

### F6. springs/helixVision layout discrepancy (P2)

The blurb workspace layout lists `springs/helixVision` but no such repo
exists under `syntheticChemistry/` on Forgejo. `gardens/helixVision` exists
under `sporeGarden/`. Either the layout doc has a duplicate or a separate
springs repo needs to be created.

---

## CATEGORY 3: IPC TRANSPORT & PRIMAL FAILURES

### I1. songBird compile-time platform gate — G1 BLOCKER (P0)

**What happened**: songBird exits immediately on Windows with:
```
Error: IPC server requires Unix domain sockets (Linux/macOS/BSD). On Windows use WSL2 for parity.
```

**Root cause**: Compile-time `#[cfg(not(unix))]` gate in
`songbird-orchestrator/src/app/core/mod.rs:474-486`:

```rust
#[cfg(not(unix))]
pub(crate) async fn start_ipc_server(&self) -> Result<()> {
    // Always returns Err on non-unix platforms
    Err(anyhow::anyhow!(
        "IPC server requires Unix domain sockets (Linux/macOS/BSD)..."
    ))
}
```

This fires at compile time. The `--listen` TCP flag is never evaluated.

**The irony**: songBird's own `universal-ipc` crate already ships complete
transport implementations for Windows:

| File | Lines | Status |
|------|-------|--------|
| `songbird-universal-ipc/src/platform/windows.rs` | 341 | **Complete** — named pipes via tokio, pure Rust |
| `songbird-universal-ipc/src/platform/fallback.rs` | 156 | **Complete** — TCP localhost fallback |
| `songbird-universal-ipc/src/platform/mod.rs:26` | — | `pub mod windows;` is declared |

The transport layer is ready. The orchestrator just doesn't call it.

**Fix**: Replace the `#[cfg(not(unix))]` gate with platform-aware transport
selection that uses named pipes on Windows and TCP fallback as last resort:

```rust
#[cfg(not(unix))]
pub(crate) async fn start_ipc_server(&self) -> Result<()> {
    if let Some(listen_addr) = &self.config.listen_addr {
        // TCP mode — already supported
        self.start_tcp_ipc_server(listen_addr).await
    } else {
        // Named pipes on Windows, TCP fallback elsewhere
        #[cfg(windows)]
        { self.start_named_pipe_ipc_server().await }
        #[cfg(not(windows))]
        { Err(anyhow::anyhow!("No IPC transport available")) }
    }
}
```

**Impact**: songBird is the Tower Atomic orchestrator. Without it:
- No `tower.health` facade
- No mesh discovery (`tower.mesh_status`)
- No gate enrollment (`mesh.gate_enroll`)
- No inter-primal IPC routing
- No ACME HTTP-01 challenge responder
- bearDog and skunkBat run but can't be discovered or orchestrated

### I2. bearDog UDS socket bind failure on Windows (P2 — self-resolving)

**What happened**: bearDog's default `auto` bind mode tried filesystem UDS
first, which failed:
```
ERROR Unix socket server error: Failed to bind socket on Unix (filesystem)
```

**Fix applied**: `--bind-mode tcp --port 9100` — bearDog immediately works
on TCP with full capability surface (200+ methods, 16 capability types).

**Note**: bearDog's `--socket` default already shows named pipe format
(`\\.\pipe\biomeos_beardog`) and has `beardog-tunnel/src/platform/windows.rs`
with full named pipe support. The `auto` detection should prefer named pipes
on Windows. Low priority because TCP works.

### I3. bearDog health socket UDS-only (P2)

**What happened**: bearDog's plaintext health socket (for cellMembrane probes)
exits with:
```
health socket exited error=System error: health socket requires Unix domain sockets
```

**Impact**: cellMembrane health probes can't reach bearDog via the dedicated
health socket. The main TCP JSON-RPC port still handles health methods.

**Fix**: Health socket should fall back to named pipe or TCP on Windows.

### I4. skunkBat UDS warning — graceful degradation (P2 — informational)

**What happened**: skunkBat warns `Unix domain sockets not available on this
platform` but continues running in standalone mode with full health reporting.

**Assessment**: skunkBat handles this correctly — warns and degrades gracefully.
This is the pattern songBird should follow.

### I5. Virtual relay UDS-only (P2)

songBird virtual relays have a `#[cfg(not(unix))]` bail:
```rust
// songbird-universal-ipc/src/service/virtual_relay.rs:188
#[cfg(not(unix))]
pub async fn start_relay(...) -> anyhow::Result<PathBuf> {
    anyhow::bail!("Virtual relays require Unix domain sockets")
}
```

**Fix**: Use named pipes or TCP for relay transport on Windows.

---

## CATEGORY 4: OPERATIONAL — ADMIN, UAC, SERVICES

### O1. WireGuard tunnel requires admin elevation (P0)

**What happened**: `wireguard.exe /installtunnelservice` requires admin
privileges. In a standard (non-admin) PowerShell session, it silently fails.
Had to use `Start-Process -Verb RunAs` to elevate.

**Impact**: Any agent session (Cursor, SSH remote, CI) running as standard
user cannot activate WireGuard without UAC elevation.

**Recommendations for Windows gates**:

1. **Pre-install WireGuard tunnel as admin during gate setup** — once the
   service is installed with `Automatic` start type, it persists across
   reboots. This is a one-time admin action.

2. **Add blueGate user to `Network Configuration Operators`** group for
   routine network management without full admin.

3. **Consider running Cursor/agent as admin** on dedicated gate machines
   (not daily drivers). Gate machines are single-purpose.

### O2. UAC prompts in automated sessions (P1)

**What happened**: Windows UAC (`ConsentPromptBehaviorAdmin=5`) prompts for
every admin action. In non-interactive sessions, this blocks indefinitely.

**Current UAC state on blueGate**:
- `EnableLUA`: 1 (UAC enabled)
- `ConsentPromptBehaviorAdmin`: 5 (prompt for consent)
- Running as: standard user (not admin)

**Recommendations**:

For **dedicated gate machines** (not daily drivers like northGate):
```powershell
# Option A: Reduce UAC to auto-elevate for admins (less secure, more automated)
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" `
    -Name "ConsentPromptBehaviorAdmin" -Value 0

# Option B: Add gate user to local Administrators group
net localgroup Administrators $env:USERNAME /add
```

For **daily drivers** (northGate): Leave UAC at default. Accept manual prompts.

### O3. Windows Defender scan overhead on Rust builds (P1)

**What happened**: Not directly observed yet, but Windows Defender real-time
scanning is known to dramatically slow Rust compilation (2-5x slower) by
scanning every intermediate `.rlib`, `.rmeta`, and `.d` file.

**Recommendation**: Exclude the build directory from Defender:
```powershell
# Requires admin
Add-MpExclusion -Path "C:\Users\user\Development\ecoPrimals"
Add-MpExclusion -Path "$env:USERPROFILE\.cargo"
Add-MpExclusion -Path "$env:USERPROFILE\.rustup"
```

This is safe on dedicated gate machines. Do NOT do this on daily drivers.

### O4. Windows Service integration for primals (P2)

**What happened**: Tower Atomic primals are started as background processes
(`Start-Process`). They don't survive logoff, don't auto-start on boot, and
have no service management (restart on crash, logging, dependency ordering).

**Recommendation**: Register primals as Windows Services. Options:

1. **NSSM (Non-Sucking Service Manager)** — wraps any .exe as a Windows
   Service. Zero code changes needed:
   ```powershell
   nssm install beardog "C:\Users\user\.local\bin\beardog.exe" "server --bind-mode tcp --port 9100"
   nssm set beardog AppDirectory "C:\Users\user"
   nssm set beardog Start SERVICE_AUTO_START
   nssm set beardog AppStdout "C:\Users\user\.local\log\beardog.log"
   nssm set beardog AppStderr "C:\Users\user\.local\log\beardog.err"
   ```

2. **Native Windows Service support** in cellMembrane's `InitSystem` dispatch
   (foundation already shipped — `InitSystem::WindowsService` variant exists).

3. **Startup order**: bearDog → songBird → skunkBat (trust foundation first),
   then workload primals. NSSM supports service dependencies.

### O5. Log management (P2)

**What happened**: Primal stdout/stderr goes to the terminal or is lost when
run via `Start-Process -WindowStyle Hidden`. No persistent logging.

**Recommendation**:
```powershell
$logDir = "$env:USERPROFILE\.local\log"
New-Item -ItemType Directory -Force -Path $logDir
```
Use NSSM (O4) for log rotation, or configure primals to log to files via
`RUST_LOG` and `tracing-appender`.

### O6. Named pipe security ACLs (P2)

When primals switch to named pipes (after I1 fix), Windows ACLs control pipe
access. By default, only the creating user can connect. For multi-user gate
setups or service accounts, pipes may need explicit ACL grants.

**Reference**: bearDog's `platform/windows.rs` already handles this correctly
with `SecurityDescriptor` configuration.

### O7. PowerShell execution policy (P2)

Fresh Windows may have `Restricted` execution policy, blocking `.ps1` scripts
like `gate-enroll.ps1`. Check and set:
```powershell
Get-ExecutionPolicy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### O8. Firewall rules for Tower ports (P2)

Windows Firewall may block Tower Atomic ports. If songBird's HTTP discovery
binds to `0.0.0.0:7700`, it needs a firewall exception:
```powershell
New-NetFirewallRule -DisplayName "songBird Discovery" -Direction Inbound -Port 7700 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "bearDog IPC" -Direction Inbound -Port 9100 -Protocol TCP -Action Allow
```

Only needed for cross-device discovery. Localhost IPC doesn't need rules.

---

## PRIMAL COMPATIBILITY MATRIX — WINDOWS

| Primal | Version | TCP Mode | Named Pipes | Health | Status |
|--------|---------|----------|-------------|--------|--------|
| bearDog | 0.9.0 | **WORKS** (`--bind-mode tcp`) | Code exists, not default | HEALTHY | **OPERATIONAL** |
| songBird | 0.2.1 | Flag exists, gate blocks | Code exists in universal-ipc | BLOCKED | **P0 FIX NEEDED** |
| skunkBat | 0.2.18 | N/A | N/A | HEALTHY (standalone) | **OPERATIONAL** (degraded) |

**Transport layer readiness** (in `songbird-universal-ipc`):

| Platform module | File | Lines | Status |
|-----------------|------|-------|--------|
| `platform/unix.rs` | UDS | ~200 | Production |
| `platform/android.rs` | Abstract sockets | ~150 | Production |
| `platform/windows.rs` | Named pipes | 341 | **Written, not wired** |
| `platform/fallback.rs` | TCP localhost | 156 | **Written, not wired** |

The fix surface is narrow: wire `windows.rs` and `fallback.rs` into the
orchestrator's `start_ipc_server()` on `#[cfg(not(unix))]` platforms.

---

## RECOMMENDED UPSTREAM ACTIONS

### Immediate (blocks G1 completion)

1. **songBird `start_ipc_server` platform gate** — Replace compile-time
   rejection with transport selection. Wire `windows.rs` named pipes and
   `fallback.rs` TCP into the orchestrator. File:
   `songbird-orchestrator/src/app/core/mod.rs:474-486`

2. **songBird virtual relay platform gate** — Same pattern. File:
   `songbird-universal-ipc/src/service/virtual_relay.rs:188-194`

### Short-term (Windows quality-of-life)

3. **Rename primalSpring colon files** — 6 files in
   `benchScale/tower_shadow/`, replace `:` with `_`

4. **Add `core.longpaths=true` to Windows gate instructions** in blurb

5. **Add GCM_INTERACTIVE=never** to Windows gate instructions

6. **Document Windows Defender exclusions** for Rust build directories

7. **Provide PowerShell sync scripts** or add PS1 variants to blurb

### Medium-term (Windows operational maturity)

8. **bearDog `auto` bind mode** — should prefer named pipes on Windows
   instead of failing on UDS then requiring manual `--bind-mode tcp`

9. **bearDog health socket** — add named pipe or TCP fallback on Windows

10. **Windows Service integration** — either via NSSM wrapper or native
    cellMembrane `InitSystem::WindowsService` implementation

11. **Startup script / gate-provision.ps1** — automated Windows gate
    bootstrap script in `plasmidBin/` covering: Git install, Rust install,
    PATH refresh, `core.longpaths`, Defender exclusions, WireGuard install,
    SSH key generation, Tower Atomic download + service registration

12. **Firewall rule automation** — part of `gate-provision.ps1`

### Blurb evolution

13. **Add Windows Phase 0+1 section** with PowerShell equivalents

14. **Note depot Windows binaries are available** (saves compile time)

15. **Document admin requirements** — WireGuard, LongPathsEnabled, Defender
    exclusions, firewall rules all need one-time admin elevation

---

## WHAT WENT RIGHT

- HTTPS zero-config clone: 40/40 repos, zero auth friction
- Forgejo public VPS model: no WireGuard needed for code sync
- Depot Windows binaries: all 14 `.exe` files present and working
- bearDog TCP mode: full 200+ method capability surface on Windows
- skunkBat graceful degradation: the correct pattern for platform gaps
- WireGuard mesh: 38ms to golgiBody, 76ms to eastGate/sporeGate
- SSH key + config: straightforward once known_hosts format was fixed
- winget: clean installs for Git, Rust, WireGuard
- Fresh clone from Forgejo: no shallow roots, no repoint, no rename

## WHAT WENT WRONG

- songBird compile-time platform gate kills Windows deployment
- git-credential-manager hangs in non-interactive sessions
- ssh-keyscan known_hosts format doesn't match OpenSSH for Windows lookup
- bearDog `auto` bind mode fails before trying named pipes
- No PowerShell equivalents for bash sync scripts
- Admin elevation required for WireGuard (no way around this)
- MAX_PATH requires both git config AND OS registry changes

## WHAT WE LEARNED

- **songBird universal-ipc already solved this** — the transport layer has
  complete Windows support. The gap is orchestrator wiring only.
- **bearDog proves TCP works on Windows** — JSON-RPC over TCP is a viable
  Windows transport. Named pipes are better but TCP is functional today.
- **skunkBat shows the right degradation pattern** — warn and continue in
  standalone mode, don't hard-fail.
- **Windows gates need a provisioning script** — too many one-time admin
  actions to document in a blurb. Automate them.
- **Admin vs. standard user is a real operational concern** — dedicated gate
  machines should run as admin; daily drivers should not.

---

*blueGate — Wave 155i Windows deployment AAR. First Windows gate in the mesh.
2/3 Tower primals operational. songBird platform gate is the sole G1 blocker
— narrow fix, transport layer already written. 15 issues documented across
4 categories. Mesh LIVE, SSH LIVE, bearDog HEALTHY, skunkBat HEALTHY.
Ready for songBird fix → full Tower → Nest → Node atomic stack.*
