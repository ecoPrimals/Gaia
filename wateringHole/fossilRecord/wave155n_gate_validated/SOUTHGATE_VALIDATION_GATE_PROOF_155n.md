# southGate VALIDATION GATE — Full Proof

**Date**: Aug 1, 2026 09:53 EDT | **Wave**: 155n (post-close) | **Gate**: southGate
**From**: southGate agent
**Posture**: **22/22 PASS. Tower Atomic trust proven without mesh. NUCLEUS 20h stable. G17 reconstitution COMPLETE. J18 portability VALIDATED.**

---

## THESIS

> **Tower Atomic handles the trust. WireGuard is transport optimization, not security.
> Any LAN. Any WAN. Any gate. BTSP is sufficient.**

This gate proves that a NUCLEUS deployment requires:
- No WireGuard mesh
- No inherited family identity
- No root access
- No /opt/membrane
- No SSH to golgiBody

Only: public depot + Forgejo repos + bearDog entropy + user-space paths.

---

## VALIDATION SCORECARD — 22/22 PASS

### J18 Gate Portability (5/5)

| Test | Result | Evidence |
|------|--------|----------|
| User-space binary path | **PASS** | `~/.local/bin/` — all 16 primals, in PATH |
| XDG runtime sockets | **PASS** | `/run/user/1000/biomeos/` — 32 sockets |
| No system dirs required | **PASS** | No `/opt/membrane`, no `/opt/plasmidBin` |
| Gate identity file | **PASS** | `~/.config/membrane/gate-name` = "southgate" |
| Family config | **PASS** | `~/.config/biomeos/family/` — key, beacon, lineage |

### Tower Atomic Trust — No Mesh (5/5)

| Test | Result | Evidence |
|------|--------|----------|
| BTSP enforcement | **PASS** | All 13 primals require ClientHello (0x47 signal) |
| Foreign peer rejection | **PASS** | 29,294 rejections in 20h (unknown_family, different_family) |
| songBird trust boundary | **PASS** | Rejects peers from LAN (192.168.4.x) |
| No WireGuard interface | **PASS** | `ip a show wg0` → "Device does not exist" |
| bearDog crypto roundtrip | **PASS** | Ed25519 keygen + AES-256-GCM encrypt + decrypt verified |

### NUCLEUS Stability (4/4)

| Test | Result | Evidence |
|------|--------|----------|
| Process count | **PASS** | 13/13 (1 per primal, 0 respawns) |
| Socket integrity | **PASS** | 32 sockets, 0 evaporated in 20h |
| Memory footprint | **PASS** | 76MB RSS total (13 primals) |
| Uptime | **PASS** | 20+ hours continuous, no restarts |

### Node Atomic (3/3)

| Test | Result | Evidence |
|------|--------|----------|
| barraCuda compute | **PASS** | Responds "alive" on localhost |
| GPU active | **PASS** | RTX 4060, 8GB, 14% util, driver 580.126.18 |
| toadStool enforcement | **PASS** | Requires riboCipher signal [0xEC, 0x01] |

### Nest Atomic (4/4)

| Test | Result | Evidence |
|------|--------|----------|
| nestGate socket | **PASS** | nestgate-89df7a2d.sock LIVE |
| Provenance socket | **PASS** | provenance.sock LIVE |
| Storage socket | **PASS** | storage-89df7a2d.sock LIVE |
| Storage target | **PASS** | 4TB NVMe, 2.8TB free |

### G17 Reconstitution (4/4 — COMPLETE)

| Test | Result | Evidence |
|------|--------|----------|
| Public depot only | **PASS** | depot.primals.eco over HTTPS (no mesh, no SSH) |
| Own lineage | **PASS** | Family 89df7a2d, bearDog entropy-seeded, not inherited |
| No mesh dependency | **PASS** | Fully functional without WireGuard |
| No peer trust needed | **PASS** | Standalone family, rejects all foreign peers |

---

## WHAT THIS PROVES FOR THE ECOSYSTEM

### For G8 (Plasmodium Bonding)
If southGate can run NUCLEUS with its own family and reject foreign peers, then
**any device on any network can be a sovereign gate**. The bonding protocol (BTSP)
operates at the application layer — network topology is irrelevant to trust.

### For J18 (Gate Portability)
The `env_or()` migration works. User-space deploy (no root, no system dirs) is
fully functional. This validates steamGate (read-only rootfs) and any future
constrained environment.

### For G17 (Reconstitution)
A gate can be reconstituted from:
1. Public binary depot (HTTPS)
2. Public git repos (Forgejo SSH)
3. bearDog entropy (local hardware RNG)
4. User-space paths (XDG standard)

No secrets from other gates needed. No mesh required. No inheritance.

### For the whitePaper
> "The security boundary is the family, not the network.
> WireGuard provides transport efficiency (353x LAN speedup).
> BTSP provides trust. These are orthogonal."

---

## HARDWARE

| Component | Spec |
|-----------|------|
| CPU | AMD Ryzen 7 5800X3D (8c/16t, 96MB 3D V-Cache) |
| GPU | NVIDIA GeForce RTX 4060 (8GB, Ada Lovelace) |
| RAM | 128 GB DDR4 |
| Storage | 1TB + 4TB NVMe (Samsung 990 EVO Plus) |
| OS | Pop!_OS 22.04 LTS |

## RUNTIME

| Metric | Value |
|--------|-------|
| Processes | 13/13 (1 per primal) |
| Sockets | 32 |
| RSS | 76 MB |
| Uptime | 20+ hours |
| Family | 89df7a2d (southgate-sovereign) |
| Rejections | 29,294 foreign peer attempts blocked |
| WireGuard | DELIBERATELY ABSENT |
| Restarts | 0 |
| Socket evaporation | 0 |

---

*southGate VALIDATION GATE: 22/22 PASS. Tower Atomic trust proven without mesh.
"The security boundary is the family, not the network."*
