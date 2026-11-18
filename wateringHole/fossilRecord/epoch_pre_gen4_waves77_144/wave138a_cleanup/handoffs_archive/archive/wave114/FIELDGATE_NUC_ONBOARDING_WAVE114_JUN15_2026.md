<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# fieldGate NUC Onboarding — Wave 114

**Date**: June 15, 2026
**Status**: Active
**Owner**: cellMembrane/ironGate (bootstrap) + ops (physical setup)
**Profile**: `canary-fieldmouse` (full NUCLEUS 13/13, previous-good binaries)
**Gate Class**: NUC canary — validates gate.bootstrap on zero-context hardware

---

## Objective

Bootstrap a fresh NUC (`fieldGate`) from zero to full NUCLEUS 13/13 using
`gate.bootstrap`. This validates the end-to-end onboarding pipeline — if
gate.bootstrap works on a machine with no prior primal code, it works anywhere.

fieldGate replaces the DO canary droplet (ephemeral) with owned hardware
(permanent). Successful onboarding satisfies Wave 113 exit criterion #4
(hardware enrollment) and proves the canary-fieldmouse profile for future
NUC deployments.

---

## Prerequisites (ops — physical only)

| # | Task | Notes |
|---|------|-------|
| 1 | Physical placement | Rack/shelf in basement LAN |
| 2 | Power | PSU connected, NUC powered on |
| 3 | Cat6e cable | Connect to LAN switch (same network as eastGate/ironGate) |
| 4 | Base OS install | Pop!_OS or Ubuntu Server minimal (22.04+) |
| 5 | SSH access from eastGate | `ssh fieldGate` must work from eastGate |
| 6 | Static IP or DHCP reservation | Stable LAN address for mesh peering |

**ops hands off to cellMembrane once SSH is reachable from eastGate.**

---

## Bootstrap Procedure (cellMembrane/ironGate)

```
gate.bootstrap --gate fieldGate --profile canary-fieldmouse
```

### Expected Bootstrap Phases

| Phase | Action | Validation |
|-------|--------|------------|
| 1 | Connect via SSH | SSH reachable from ironGate |
| 2 | Pull depot binaries from VPS | 13 primals + membrane launcher fetched from membrane.primals.eco/depot/ |
| 3 | BLAKE3 integrity verification | All 13 checksums match checksums.toml |
| 4 | Generate gate identity | `gate-identity.toml` created with fieldGate name + keys |
| 5 | Install systemd units | Per-primal units (ServerContract-aware) + membrane services |
| 6 | Start NUCLEUS | `systemctl start membrane-nucleus.target` |
| 7 | Health sweep | 13/13 primals alive (profile-aware expectations) |
| 8 | Mesh enrollment | Register with songBird mesh via `SONGBIRD_PEERS` |
| 9 | Federation validation | fieldGate visible from eastGate + golgiBody mesh |

### Post-Bootstrap Validation

```
membrane gate.status --gate fieldGate
```

Expected output:
- Gate: fieldGate (x86_64-unknown-linux-musl) — HEALTHY
- Probes: 8/8 GREEN (S1-S4 sovereignty all operational)
- Primals: 13/13 alive
- Mesh: 3+ peers reachable (eastGate, ironGate, golgiBody)
- Profile: canary-fieldmouse (previous-good binaries)

---

## Manifest Entries (already added by overwatch)

**ecosystem_manifest.toml**:
```toml
[gates.fieldGate]
target = "x86_64-unknown-linux-musl"
mobility = "fixed"
bind_mode = "uds"
composition = "full"
transport = "lan"
mesh_peer = "[RELAY_PUBLIC]:7700"
profile = "canary-fieldmouse"
```

**DEPLOYMENT_INSTANCE.toml**:
```toml
[fleet.gates.fieldGate]
arch = "x86_64-unknown-linux-musl"
mobility = "fixed"
transport = "lan"
profile = "canary-fieldmouse"
role = "NUC canary — full NUCLEUS 13/13, previous-good binaries"
```

---

## RustDesk Integration

After bootstrap, fieldGate should be reachable via RustDesk relay:

1. Install RustDesk client on fieldGate during bootstrap (or as post-bootstrap task)
2. Configure relay server: golgiBody-ext (137.184.197.151:21116)
3. Exchange public key from relay (distributed during bootstrap key phase)
4. Validate: remote desktop session from eastGate → fieldGate via relay

---

## Success Criteria

| # | Criterion | How to Verify |
|---|-----------|---------------|
| 1 | gate.bootstrap completes without manual intervention | Exit code 0, no SSH-in required |
| 2 | 13/13 primals alive | `membrane gate.status` shows 13/13 |
| 3 | fieldGate in songBird mesh | `membrane mesh.status` shows fieldGate reachable |
| 4 | Depot binaries match checksums | BLAKE3 verification during phase 3 |
| 5 | RustDesk relay reachable | Desktop session from eastGate succeeds |
| 6 | Cascade from VPS works | `temporal.cascade` pulls updates to fieldGate |

---

## Failure Modes to Watch

| Failure | Likely Cause | Recovery |
|---------|--------------|----------|
| SSH timeout | NUC not on LAN / IP wrong | Check cable, DHCP, firewall |
| Depot fetch fails | VPS depot stale or unreachable | `plasmid.harvest --all` on VPS first |
| Checksum mismatch | Depot binary not from HEAD | Rebuild specific primal on VPS |
| Primal won't start | Missing runtime dependency | Check journalctl for that primal |
| Mesh enrollment fails | SONGBIRD_PEERS not updated | Update VPS songbird env + restart |
| S4 auth fails | BearDog BTSP not configured | Verify gate identity + family seed |

---

## Timeline

- **Day 0**: ops physical setup (cable, power, OS, SSH)
- **Day 0+**: cellMembrane `gate.bootstrap` execution
- **Day 0+**: Validation + RustDesk configuration
- **Wave 114 exit**: fieldGate healthy in mesh = hardware enrollment criterion MET

---

## References

- [GATE_NUCLEUS_SYSTEMD_STANDARD.md](../GATE_NUCLEUS_SYSTEMD_STANDARD.md) — deployment standard
- [VPS_SURFACE_MINIMIZATION_EVOLUTION_JUN12_2026.md](VPS_SURFACE_MINIMIZATION_EVOLUTION_JUN12_2026.md) — NUC canary plan
- [CELLMEMBRANE_FIELDMOUSE_DEPLOYMENT.md](../CELLMEMBRANE_FIELDMOUSE_DEPLOYMENT.md) — fieldMouse deployment class
- [MEMBRANE_CHANNEL_ARCHITECTURE.md](../MEMBRANE_CHANNEL_ARCHITECTURE.md) — RustDesk relay + channel docs
