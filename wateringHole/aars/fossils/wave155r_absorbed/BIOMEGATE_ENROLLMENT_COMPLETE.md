# biomeGate Enrollment Complete — eastGate Overwatch Response

**Date**: Aug 2, 2026 | **Wave**: 155n | **From**: eastGate overwatch (sporeGate)
**Status**: ALL BLOCKERS CLEARED

---

## Actions Completed (sporeGate → golgi)

### 1. Forgejo SSH Key — ENROLLED

| Item | Value |
|------|-------|
| User created | `biomegate` (ID: 9) |
| Team | `ecoprimals` → Owners (full push access) |
| Key | `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPnxJIzG134WkzUerZbThhIyrAIkpx8lKHEQBb4SzjxK biomegate@primals.eco` |
| Title | `biomegate-gate-v1` |
| Key ID | 16 |
| Fingerprint | `SHA256:fVJm7sKac8gVdi8lcHeLmxy8bID+GHYlLe9z8Hi/wvE` |

**Verify from biomeGate**:
```bash
ssh -T -p 2222 git@git.primals.eco
```

### 2. WireGuard Mesh Peer — ENROLLED

| Item | Value |
|------|-------|
| IP assigned | `10.13.37.3` |
| Public key | `ZRbD3VDxzxhQ3gbNzLoIIP5MYMvF7gVM7G9AmIRLEnY=` |
| Hub peer added | golgi `wg0.conf` updated |
| Hub runtime | `wg set` applied (no restart needed) |

**Status**: biomeGate is **LIVE on mesh** — sporeGate confirms:
```
PING 10.13.37.3: 64 bytes, ttl=63, time=75ms (via golgi hub)
```

### 3. Manifest & Topology Updated

- `ecosystem_manifest.toml`: `[gates.biomeGate]` added with `wg_ip`, `lan_ip`, `ssh_user`, roles
- `TOPOLOGY_MAP.toml`: biomeGate added to `wireguard_wan` peers
- `golgi wg0.conf`: Peer commented with `# biomeGate — HBM2 test bench`

---

## biomeGate Next Steps

| # | Action | Where | Status |
|---|--------|-------|--------|
| 1 | Test Forgejo SSH push | biomeGate | `ssh -T -p 2222 git@git.primals.eco` |
| 2 | Switch repos from HTTPS to SSH remotes | biomeGate | `git remote set-url origin ssh://git@git.primals.eco:2222/ecoPrimals/<repo>.git` |
| 3 | Push first AAR/handoff to wateringHole | biomeGate | Verify write access |
| 4 | Add sporeGate SSH key to `~/.ssh/authorized_keys` | biomeGate | Key: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILU4i9hEtHJA02/JZ8XR/OHaR/bSiuAaDRMhdJX7zuRp sporegate-gate-v1` |
| 5 | Start GPU revalidation matrix (Phase 1: Safety) | biomeGate | Exp 193, 200, 214 |

---

## Manifest Parse Fix

While running depot harvest, discovered `steamGate.mobility = "portable"` broke
the entire manifest parser. Fixed to `"mobile"`. This was silently breaking
`plasmid.harvest --local` for all 13 primals.

---

*All biomeGate enrollment blockers cleared. Mesh is LIVE. Push when ready.*
