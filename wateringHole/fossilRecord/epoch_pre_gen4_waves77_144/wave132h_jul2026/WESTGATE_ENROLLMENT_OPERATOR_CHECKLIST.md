# westGate Enrollment — Operator Checklist

**Authority**: Overwatch  
**Status**: Ready when hardware is connected  
**Date**: 2026-06-04  
**Source FRAGO**: `wave73-westgate-skunkbat-enrollment`  
**Hardware**: i7-4771, RTX 2070 Super, 32GB RAM, 76TB ZFS

---

## What westGate Brings

westGate is a 76TB ZFS cold storage node joining the LAN mesh.
Primary role: Nest Atomic (content-addressable storage for NestGate).
Secondary: 3rd physical gate for Plasmodium collective validation (glacial criterion 2).

---

## Phase A: Physical Setup

### A1. Connect Hardware

- [ ] Connect westGate to LAN (same switch/subnet as eastGate: 192.168.1.x)
- [ ] Boot and verify network connectivity
- [ ] Assign or confirm static IP (e.g., 192.168.1.XXX)
- [ ] Verify bidirectional ping to:
  - eastGate: `ping 192.168.1.144`
  - strandGate: `ping 192.168.1.132`

### A2. ZFS Pool Verification

- [ ] Verify ZFS pool is imported: `zpool status`
- [ ] Confirm available space: `zfs list`
- [ ] Note the ZFS dataset path for NestGate (e.g., `/tank/nestgate` or similar)

---

## Phase B: Identity and Toolchain

### B1. Gate Identity

```bash
# Create the .gate identity file in the home or project root
echo 'westGate' > .gate
```

- [ ] Verify: `cat .gate` returns `westGate`

### B2. Clone ecoPrimals

```bash
# Clone the repository tree
git clone git@<forgejo-or-origin>:ecoPrimals/ecoPrimals.git
cd ecoPrimals
git submodule update --init --recursive
```

- [ ] Verify: all submodules present (`ls gardens/ primals/ springs/ infra/`)

### B3. Install Rust Toolchain

If not already installed:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
rustup default stable
```

- [ ] Verify: `rustc --version` returns 1.85+

### B4. Install plasmidBin

```bash
cargo install --path infra/plasmidBin
```

- [ ] Verify: `plasmidbin --version` runs without error

---

## Phase C: Core Services

### C1. Set Environment

```bash
export FAMILY_ID=westgate
export NODE_ID=tower1
export ECOPRIMALS_ROOT=$(pwd)
```

Add to shell profile (`.bashrc` / `.zshrc`) for persistence.

### C2. Copy Family Seed

The family seed is the Ed25519 key material that establishes trust within
the ecoPrimals family. Copy it from an existing gate.

**From eastGate or strandGate**:
```bash
# On the source gate, locate the family seed
# Typically in bearDog's config or FAMILY_SEED env var
# Copy the value securely (SSH, USB, etc.)
```

**On westGate**:
```bash
export FAMILY_SEED='<copied-seed-value>'
```

**Security**: Transfer the seed over a trusted channel only (SSH, physical media).
Never transmit over unencrypted channels.

### C3. Start bearDog

```bash
beardog server \
  --family-id westgate \
  --orchestrator-id west-gate
```

- [ ] Verify: bearDog starts without error
- [ ] Verify: UDS socket is created (check for socket file in runtime dir)
- [ ] Verify: `auth.status` RPC responds (via UDS)

### C4. Start Songbird

```bash
SONGBIRD_PEERS='east-gate@192.168.1.144:7700,strand-gate@192.168.1.132:7700' \
songbird server \
  --node-id west-gate \
  --federation-port 7700 \
  --security-endpoint http://127.0.0.1:9100
```

- [ ] Verify: Songbird starts and logs peer connections
- [ ] Verify: Port 7700 is listening: `ss -tlnp | grep 7700`

### C5. Start skunkBat

```bash
skunkbat server
```

- [ ] Verify: `defense.status` responds on UDS

---

## Phase D: Mesh Enrollment

### D1. Mesh Init

Send the mesh initialization RPC to register westGate with the mesh:

```bash
# Via Songbird RPC (exact method depends on current RPC interface)
# mesh.init with bootstrap peers
```

Songbird should discover peers automatically via the `SONGBIRD_PEERS` env.

### D2. Verify Mesh Connectivity

```bash
# Check peer discovery
# RPC: discovery.peers
# Expected: peer_count >= 2 (eastGate + strandGate)

# Check mesh health
# RPC: mesh.health_check
# Expected: all_healthy: true
```

- [ ] `discovery.peers` returns >= 2 peers
- [ ] `mesh.health_check` returns `all_healthy: true`
- [ ] Both eastGate and strandGate appear in peer list

### D3. Verify Cross-Gate Connectivity

From eastGate or strandGate, verify westGate is visible:

```bash
# On eastGate, run discovery.peers
# westGate should appear as a new peer with latency_ms < 5
```

---

## Phase E: NestGate Storage Configuration

### E1. Configure NestGate Storage Path

```bash
export NESTGATE_STORAGE_BASE_PATH=/path/to/zfs/dataset
```

Update the NestGate configuration to use the ZFS pool.

### E2. Verify CAS (Content-Addressable Storage)

```bash
# Test content.put → content.get round-trip
# Verify BLAKE3 hash integrity
```

- [ ] Content round-trip works
- [ ] BLAKE3 hash matches

---

## Phase F: Validation

### F1. Run primalSpring Validation

From eastGate, run the covalent mesh scenario with westGate included:

```bash
cd springs/primalSpring
cargo test s_covalent_mesh -- --nocapture
```

- [ ] All existing mesh checks pass
- [ ] westGate appears as 3rd peer in results

### F2. Fire Sitrep

Once everything is green:

```bash
# Via impulse system
# impulse.post --to eastGate --type sitrep --subject 'westGate online'
```

---

## Post-Enrollment: Notify Overwatch

Once westGate is online and all checks pass, overwatch will:

1. Update `GATE_TEAM_COORDINATION_MATRIX.md` — westGate to OPERATIONAL
2. Run full `s_covalent_mesh` validation with 3 gates
3. Update gen5 trust validation paper (Plasmodium collective: 3 gates)
4. Mark glacial criterion 2 as MET
5. Blurb westGate teams for ongoing work

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| bearDog won't start | Check FAMILY_SEED is set. Check UDS directory permissions. |
| Songbird can't find peers | Verify IPs and port 7700 are reachable. Check firewall. |
| ZFS pool not imported | `zpool import <poolname>` |
| Mesh health check fails | Check all 3 gates have Songbird running. Check subnet routing. |
| skunkBat UDS not found | Check socket path. May need `SKUNKBAT_SOCKET_PATH` env. |

---

## Summary

| Phase | Steps | Time Estimate |
|-------|-------|---------------|
| A: Physical setup | 4 checks | 15 min |
| B: Identity + toolchain | 4 steps | 30 min (including compile) |
| C: Core services | 5 services | 20 min |
| D: Mesh enrollment | 3 verifications | 10 min |
| E: NestGate storage | 2 steps | 10 min |
| F: Validation | 2 tests | 10 min |
| **Total** | | **~1.5 hours** |

---

*"The third gate opens. Three physical nodes, one sovereign mesh.
The glacier finds its mass."*
