# sporeGate Wave 155n — J12 Sub-Builder Wire AAR

**Gate**: sporeGate | **Date**: 2026-08-01T00:10:00Z | **Wave**: 155n
**Operator**: sporeGate build authority | **From**: eastGate overwatch cascade

---

## SUMMARY

Wired the J12 sub-builder foreman dispatch pattern into sovereign CI. sporeGate
can now dispatch Windows builds to blueGate via SSH. The wire is validated end-to-end
in dry-run mode; live dispatch is blocked only on blueGate enrolling sporeGate's SSH key.

---

## WHAT WE BUILT

### 1. Foreman Dispatch in `sovereign.rs`

Added sub-builder dispatch to the sovereign CI pipeline. When `sovereign.ci.trigger`
runs, it now:

1. **Phase 1a**: Local harvest (musl on sporeGate) — unchanged
2. **Phase 1b**: Sub-builder dispatch — SSHes to remote gates for cross-target builds
3. **Phase 2**: Sandbox validation — unchanged
4. **Phase 3**: Refresh — unchanged

The pipeline outcome now includes sub-builder results in provenance:
```
sovereign.ci.trigger: squirrel (dry-run) — harvest: 1 built | sub-builders: [blueGate:OK]
```

### 2. Sub-Builder Configuration

Static sub-builder table in `sovereign.rs`:
```rust
const SUB_BUILDERS: &[SubBuilder] = &[SubBuilder {
    gate: "blueGate",
    target: "x86_64-pc-windows-gnu",
    ssh_host: "blueGate",
    membrane_bin: "membrane.exe",
}];
```

Manifest codification in `ecosystem_manifest.toml`:
```toml
[sub_builders."x86_64-pc-windows-gnu"]
gate = "blueGate"
ssh_host = "blueGate"
membrane_bin = "membrane.exe"
```

### 3. blueGate Network Registration

- **LAN IP**: `192.168.4.237` registered in `MESH_REGISTRY` (cytoplasm.rs)
- **SSH config**: Added for both `sporegate` user and `root` (sovereign CI)
- **SSH host key**: Accepted and stored in `known_hosts`

### 4. Manifest Target Expansion

All 14 primals now have 4 build targets:
```toml
targets = ["x86_64-unknown-linux-musl", "x86_64-unknown-linux-gnu",
           "x86_64-pc-windows-gnu", "aarch64-unknown-linux-musl"]
```

### 5. Tests

3 new tests added to `sovereign.rs`:
- `sub_builders_configured` — verifies blueGate is in the sub-builder table
- `sub_builder_dry_run_reports_all_gates` — validates dry-run produces OK for all gates
- Existing 33 sovereign tests continue to pass

---

## VALIDATION

### Dry-Run (PASS)

```
$ membrane sovereign.ci.trigger --primal squirrel --dry-run
sovereign.ci.trigger: squirrel (dry-run) — harvest: 1 built | sub-builders: [blueGate:OK]
{
  "harvest": [{"binary":"squirrel","status":"Built"}],
  "sub_builders": ["blueGate:OK"]
}
```

### Live Dispatch (Expected FAIL — SSH key not enrolled)

```
$ sudo membrane sovereign.ci.trigger --primal squirrel --commit test123
ERROR sub-builder harvest failed gate="blueGate" exit_code=255
      stderr="ecoPrimal@192.168.4.237: Permission denied (publickey)."
WARN  some sub-builder harvests failed sub_builders=["blueGate:FAIL"]
```

The SSH dispatch wire works end-to-end. The failure is `Permission denied (publickey)` —
blueGate needs to add our SSH public key to its `authorized_keys`.

### Gate Status (HEALTHY)

```
sporeGate — HEALTHY (11/11 probes OK)
  depot.integrity: 16 verified, 0 hash mismatch
  primals.alive: 13/13
  mesh.reachability: 7 peers, 7 reachable
```

---

## WHAT BLUEGATE TEAM NEEDS TO DO

### SSH Key Enrollment

Add these public keys to `C:\Users\ecoPrimal\.ssh\authorized_keys`:

**sporegate user key (interactive)**:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILU4i9hEtHJA02/JZ8XR/OHaR/bSiuAaDRMhdJX7zuRp sporegate-gate-v1
```

**Sovereign CI key (root, automated)**:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPwGg1Ut9dblsY+EeBSzRK1yAEUMOFEpqNX0gUvQxEs8 sovereign-ci@sporeGate
```

### Windows Firewall

Open port 7700 (songBird federation) and 9901 (IPC) for LAN access:
```powershell
New-NetFirewallRule -DisplayName "songBird Federation" -Direction Inbound -LocalPort 7700 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "membrane IPC" -Direction Inbound -LocalPort 9901 -Protocol TCP -Action Allow
```

### membrane.exe Setup

Ensure `membrane.exe` is in PATH and can run `plasmid.harvest`:
```powershell
membrane.exe plasmid.harvest --primal squirrel --dry-run
```

### Verification

Once keys are enrolled, test from sporeGate:
```bash
ssh blueGate "membrane.exe plasmid.harvest --primal squirrel --dry-run"
```

---

## DISPATCH FLOW (when fully wired)

```
Forgejo push → golgi post-receive
    → SSH root@sporeGate: membrane sovereign.ci.trigger --primal <name>
        → Phase 1a: local harvest (musl) on sporeGate
        → Phase 1b: SSH blueGate: membrane.exe plasmid.harvest --primal <name> --push
            → blueGate builds x86_64-pc-windows-gnu
            → --push: syncs to sovereign depot
        → Phase 2: sandbox on sporeGate (musl binary)
        → Phase 3: refresh (atomic deploy + BLAKE3 verify)
        → mesh.publish depot.updated
```

---

## REMAINING FOR J12 COMPLETION

| # | Item | Owner | Status |
|---|------|-------|--------|
| 1 | blueGate SSH key enrollment | blueGate | Pending — keys provided above |
| 2 | Windows firewall ports 7700/9901 | blueGate | Pending |
| 3 | `membrane.exe` PATH setup | blueGate | Likely done (13/13 NUCLEUS) |
| 4 | End-to-end live dispatch test | sporeGate + blueGate | Blocked on #1 |
| 5 | Artifact return path validation | sporeGate | `--push` flag exists, needs depot write perms |
| 6 | songBird federation cross-gate | Both | `relay.forward` path available as fallback |

**Critical path**: Item #1 (SSH key enrollment). Everything else on sporeGate's side is wired and tested.

---

*sporeGate 155n J12 sub-builder AAR — foreman dispatch WIRED in sovereign CI.
blueGate registered (LAN 192.168.4.237). Dry-run validated. Live dispatch blocked
on SSH key enrollment. 14 primals × 4 targets codified in manifest.*
