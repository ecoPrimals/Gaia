# blueGate J12 SSH Enrollment — COMPLETE

**Gate**: blueGate | **Date**: 2026-08-01T00:30:00Z | **Wave**: 155n
**Status**: SSH ENROLLED. Ready for live dispatch.

---

## SUMMARY

blueGate SSH enrollment is complete. OpenSSH Server installed, firewall opened,
sporeGate's keys enrolled, and E2E dispatch validated via localhost SSH. The J12
sub-builder wire is ready for live cross-gate dispatch.

---

## ENROLLMENT PROOF

### SSH Server
```
Service: sshd (Running, Automatic)
Version: OpenSSH_for_Windows_9.5p2, LibreSSL 3.8.2
Default Shell: PowerShell
```

### Firewall Rules
```
OpenSSH Server        : port 22   TCP ALLOW (Inbound)
songBird Federation   : port 7700 TCP ALLOW (Inbound)
membrane IPC          : port 9901 TCP ALLOW (Inbound)
```

### Keys Enrolled
Location: `C:\ProgramData\ssh\administrators_authorized_keys`
(Windows OpenSSH uses ProgramData path for users in Administrators group)

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILU4i9hEtHJA02/JZ8XR/OHaR/bSiuAaDRMhdJX7zuRp sporegate-gate-v1
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPwGg1Ut9dblsY+EeBSzRK1yAEUMOFEpqNX0gUvQxEs8 sovereign-ci@sporeGate
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINlBX3vvJWHySRLf6d901D4UGw7PRmLMcUb3xJJmnybd blueGate@primals.eco
```

### E2E SSH Dispatch (localhost validated)
```
$ ssh user@localhost "membrane.exe plasmid.harvest --primal squirrel --dry-run"
harvest: 1 built, 0 current, 0 skipped, 0 failed
[{"binary":"squirrel","detail":"dry-run: would clone ecoPrimals/squirrel and build for x86_64-pc-windows-gnu","status":"Built"}]

$ ssh user@localhost "membrane.exe plasmid.build squirrel --dry-run"
plasmid.build (dry-run): would build squirrel for x86_64-pc-windows-gnu
  repo: ecoPrimals/squirrel
  build_args: (none)
  binary_name: squirrel

$ ssh user@localhost "rustc --version"
rustc 1.97.1 (8bab26f4f 2026-07-14)
```

---

## CRITICAL: SSH USER MISMATCH

sporeGate's sovereign CI SSHes as **`ecoPrimal@192.168.4.237`**:
```
ERROR sub-builder harvest failed gate="blueGate" exit_code=255
      stderr="ecoPrimal@192.168.4.237: Permission denied (publickey)."
```

**The correct SSH user on blueGate is `user`, not `ecoPrimal`.**

### sporeGate Action Required

Update SSH config and sub-builder dispatch to use:
```
Host blueGate
    HostName 192.168.4.237
    User user
    IdentityFile ~/.ssh/sovereign-ci
    Port 22
```

And update `sovereign.rs` SUB_BUILDERS or SSH config:
```diff
-ssh_host = "blueGate"    # resolves to ecoPrimal@192.168.4.237
+ssh_host = "blueGate"    # resolves to user@192.168.4.237 (update ~/.ssh/config)
```

---

## ENVIRONMENT (available via SSH)

```
MEMBRANE_GATE_NAME = blueGate
ECOPRIMALS_ROOT    = c:\Users\user\Development\ecoPrimals
PATH includes      = C:\Users\user\.local\bin (membrane.exe, all depot binaries)
Rust toolchain     = stable-x86_64-pc-windows-gnu (1.97.1)
Cargo              = 1.97.1
Target host        = x86_64-pc-windows-gnu
```

---

## NUCLEUS STATUS

```
13/13 primals running:
  beardog(9100) songbird(7700/7701) skunkbat(9102)
  nestgate(9200) loamspine(9201) rhizocrypt(9202)
  sweetgrass(9213) petaltongue(9204) squirrel(9205)
  toadstool(9300) barracuda(9301) coralreef(9302)
  biomeos(9090)
```

---

## REMAINING FOR LIVE E2E

| # | Item | Owner | Status |
|---|------|-------|--------|
| 1 | Update SSH config: `User user` | sporeGate | **ACTION NEEDED** |
| 2 | Live dispatch: `sovereign.ci.trigger --primal squirrel` | sporeGate | Blocked on #1 |
| 3 | Artifact push: `--push` flag writes to depot | Both | Needs depot write path |
| 4 | songBird federation relay (port 7700) | Both | Firewall open, awaiting mesh wire |

**Critical path**: Item #1. blueGate is fully ready. sporeGate just needs `User user` in SSH config.

---

## WINDOWS OPENSSH NOTES (for ecosystem docs)

1. **Admin users use `C:\ProgramData\ssh\administrators_authorized_keys`** — not `~\.ssh\authorized_keys`.
   Windows OpenSSH has a `Match Group administrators` block in `sshd_config` that overrides the key path.
2. **ACLs required**: The admin keys file must have `icacls /inheritance:r /grant "SYSTEM:(F)" /grant "Administrators:(F)"`.
3. **Default shell**: Set to PowerShell via registry `HKLM:\SOFTWARE\OpenSSH\DefaultShell`.
4. **Capability install is slow**: `Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0` takes 3-7 minutes
   (goes through Windows servicing/DISM pipeline).
5. **Env vars persist**: User-level env vars (`[Environment]::SetEnvironmentVariable(..., "User")`) are available in SSH sessions.

---

*blueGate J12 SSH enrollment COMPLETE. 3 keys enrolled. Firewall ports 22/7700/9901 open.
E2E dispatch validated via localhost. sporeGate needs to update SSH config: `User user`
(not `ecoPrimal`). Once updated, live dispatch should work immediately.*
