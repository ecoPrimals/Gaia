# sporeGate Overwatch — Wave 119 Blurb

**Date**: Jun 19 2026 14:10 EDT | **From**: eastGate overwatch
**Status**: Reference gate (13/13, WG .2, cascade, SSH). Nest provenance authority. **pepti P0 FIXED.**
**Atomic Role**: Nest (NestGate, RhizoCrypt, LoamSpine, SweetGrass) — data/provenance dispatch target.
**Key Win**: pepti SSH→forgejo resolved (wrong URLs, not firewall). All 37 repos now reachable from pepti.

---

## Priority 0: SSH into flockGate + ironGate (unblocks Tower + Node work)

You have SSH access across the mesh. Connect and authorize keys so those gates can receive
their assigned primals and start their Tower/Node work.

### flockGate (Tower atomic — BearDog, Songbird, SkunkBat)

```bash
# flockGate is on WG — reach via golgi relay or direct
ssh flockgate@10.13.37.6   # may need golgi as jump host

# Once in:
# 1. Add your pubkey:
mkdir -p ~/.ssh && echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILU4i9hEtHJA02/JZ8XR/OHaR/bSiuAaDRMhdJX7zuRp sporegate-gate-v1" >> ~/.ssh/authorized_keys

# 2. Allow SSH on wg0 (if firewall blocks):
sudo ufw allow in on wg0 to any port 22

# 3. Deploy NUCLEUS:
scp /usr/local/bin/membrane flockgate@10.13.37.6:/tmp/
ssh flockgate@10.13.37.6 "sudo mv /tmp/membrane /usr/local/bin/ && membrane gate.bootstrap flockGate"
```

**After**: flockGate team opens IDE, starts Tower trust work (BTSP over WAN, mesh.init, threat detection).

### ironGate (Node atomic — ToadStool, BarraCuda, CoralReef)

```bash
# ironGate is on sovereign relay. Check SSH:
ssh irongate@<IP>   # IP from DHCP table or RustDesk session

# If SSH not enabled (operator may need to assist via RustDesk):
# On ironGate: sudo apt install -y openssh-server
# Then add your key: echo "<your-pubkey>" >> ~/.ssh/authorized_keys

# Once SSH live:
membrane gate.preflight
sudo membrane gate.bootstrap ironGate
```

**After**: ironGate team opens IDE, starts Node compute work (ToadStool fleet, BarraCuda tensors, CoralReef shaders).

---

## Priority 1: Nest Provenance Work (your assigned atomic)

You are the **provenance authority**. These primals need active work:

| Primal | Socket | Work Needed |
|--------|--------|-------------|
| **RhizoCrypt** | /run/membrane/rhizocrypt.sock | Wire rootpulse commit into cascade: `dag.session.create` on each wave push |
| **LoamSpine** | /run/membrane/loamspine.sock | Start sovereign ledger commits (wave state → merkle root → persist) |
| **SweetGrass** | /run/membrane/sweetgrass.sock | Enable commit braids — track attribution per gate per wave |
| **NestGate** | /run/membrane/nestgate.sock | Generate `checksums.toml` for depot (fixes DEGRADED probe) |

### Wiring rootpulse into cascade:

```bash
# After each cascade push, call rootpulse commit:
membrane rootpulse commit --wave <N> --gate sporeGate
# This creates a DAG session in rhizoCrypt, signs via beardog, commits to loamspine
```

### Fix depot integrity:

```bash
# On pepti (build authority):
ssh root@10.13.37.4
cd /opt/depot/primals/x86_64-unknown-linux-musl
membrane depot.checksums --generate   # produces checksums.toml
# Then gate.status should show depot.integrity: OK
```

---

## Priority 2: Flint 2 WiFi Swap (this weekend)

| Task | Who | When |
|------|-----|------|
| Physical swap (Eero out, Flint 2 in) | Operator | Weekend |
| Flint 2 config: AP bridge, same SSID, SSH enabled | You (SSH in) | After install |
| swiftGate reconnect → Flint 2 WiFi | You | After AP live |
| Push sovereign relay config to swiftGate | You | After WiFi confirmed |

---

## Priority 2: Remaining Relay Migration

| Gate | Access | Status |
|------|--------|--------|
| strandGate | Omada wired (house2) | Push sovereign config (RustDesk or SSH) |
| southGate | Omada wired (house2) | Push sovereign config (RustDesk or SSH) |
| swiftGate | Flint 2 WiFi (after swap) | BLOCKED until WiFi live |

---

## Key Infra

| Resource | Access |
|----------|--------|
| golgi | ssh root@[RELAY_PUBLIC] (WG: 10.13.37.1) |
| pepti | ssh root@[RELAY_PUBLIC] (WG: 10.13.37.4) |
| eastGate | ssh eastgate@192.168.4.244 (WG: 10.13.37.5) |
| flockGate | ssh flockgate@10.13.37.6 (WG, via golgi jump) |
| Forgejo | https://git.primals.eco |
| Sovereign relay | See RUSTDESK_CONFIG.md |

---

## Ecosystem State

| Metric | Value |
|--------|-------|
| eastGate | **13/13 NUCLEUS** (user systemd, no sudo) |
| sporeGate | **13/13 NUCLEUS** (system systemd) |
| flockGate | WG .6 LIVE, SSH pending key auth |
| ironGate | Sovereign relay, SSH pending |
| cellMembrane | **680 tests**, rootpulse+webhook wired, SSH consolidated |
| VCS | All repos at parity — pepti can now reach forgejo (P0 fixed) |
| WireGuard | 5 nodes (golgi, sporeGate, pepti, eastGate, flockGate) |

---

## What NOT to Touch

- **northGate**: Windows hobby (5090). P3. After Linux proven.
- **fieldGate**: Dead CMOS. Hardware fix when operator has time.
- **[ISP] passthrough**: Operator handles WAN config.
- **primalSpring code**: eastGate team owns evolution.
- **sporePrint content**: flockGate team owns.
