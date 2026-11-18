# sporeGate Team — Full Onboarding & Ownership Handoff

**Date**: 2026-06-16 | **From**: eastGate overwatch
**Status**: HANDSHAKE COMPLETE — 13/13 primals alive, routing active

---

## Your Identity

**Gate**: sporeGate (GMKtec NucBox M6, Ryzen 7 6800H, 32GB, dual 2.5G RJ45 + WiFi)
**Role**: LAN Periplasm Router + cellMembrane Owner
**IP**: 192.168.4.3 (LAN), 192.168.4.1 (gateway alias), WiFi fallback
**SSH**: `ssh sporeGate` from eastGate

---

## What You Own

### cellMembrane (transferred from ironGate)

cellMembrane is the gate bootstrap, cascade, fetch, harvest, and deployment system.
sporeGate is the natural owner because you ARE the membrane — the LAN perimeter that
wraps the internal network. You physically sit between the internet ([ISP]) and the
ecosystem (CRS310 switch).

**Repo**: `~/Development/ecoPrimals/gardens/cellMembrane` (cloned from Forgejo)
**GitHub**: `git@github.com:ecoPrimals/cellMembrane.git`
**Forgejo**: `https://git.primals.eco/ecoPrimals/cellMembrane.git`

### Core Responsibilities

1. **LAN Routing** — NAT, firewall (nftables), DHCP, DNS for all LAN gates
2. **RustDesk Relay Config** — Ensure all gates can remote to each other via golgi relay
3. **Depot & Cascade** — `plasmid.harvest`, `gate.fetch`, `gate.update` pipelines
4. **Bootstrap Evolution** — `gate.bootstrap` command that onboards new nodes
5. **Bidirectional Sync** — GitHub ↔ Forgejo push_target=all convergence
6. **Build Authority Coordination** — pepti VPS does the builds, you coordinate

### What ironGate Is Now

ironGate transitions to **projectNUCLEUS / ABG focus**:
- Compute sharing architecture
- Access tiers (Observer, Reviewer, User, Operator)
- JupyterHub / toadStool integration
- ABG member onboarding workflows

---

## Current State (verified Jun 16 21:10 EDT)

| Component | Status |
|-----------|--------|
| Primals | **13/13 alive** (manual nohup start) |
| NAT/Firewall | nftables active, 5.5GB+ forwarded |
| DHCP | systemd-networkd serving 6 leases |
| DNS | dnsmasq caching (1.1.1.1, 8.8.8.8, 9.9.9.9) |
| RustDesk | Configured with golgi relay key |
| Mesh | Initialized (node_id: sporeGate, hub: [RELAY_PUBLIC]:7700) |
| Sovereignty | S1-S3 OPERATIONAL, S4 beardog alive |
| WiFi OOB | wlp3s0 as fallback management (high route-metric) |

---

## Immediate TODO (P1)

### 1. Persist primals across reboot (systemd units)

Primals are running as `nohup` — a reboot kills them. Need systemd units:

```bash
# cellMembrane has gate.bootstrap code for this (fed3335), but it hung.
# Manual approach until bootstrap is fixed:
sudo mkdir -p /etc/systemd/system
# Create unit per primal — template:
# [Unit]
# Description=ecoPrimal: beardog
# After=network.target
# [Service]
# Type=simple
# ExecStart=/home/sporegate/.local/share/ecoPrimals/plasmidBin/primals/x86_64-unknown-linux-musl/beardog
# Environment=FAMILY_ID=ecoPrimals
# Environment=ECOPRIMALS_ROOT=/home/sporegate/Development/ecoPrimals
# Restart=always
# [Install]
# WantedBy=multi-user.target
```

### 2. Fill FAMILY_SEED

```bash
sudo nano /opt/membrane/env
# Replace __FILL_FROM_OPERATOR__ with actual seed from operator
```

### 3. Deploy RustDesk to any device (ONE COMMAND)

```bash
pkexec rustdesk --config "[RUSTDESK_CONFIG_PURGED]"
```

This single command configures server, relay, and key. Works on any Linux device.
For Windows: `rustdesk.exe --config "<same string>"` (admin cmd)

Already deployed: eastGate, sporeGate, northGate
TODO: fieldGate (offline), all Omada-connected towers

Full docs: `compute-sharing/RUSTDESK_CONFIG.md`

### 4. WiFi fallback persistence

Ensure WiFi reconnects on boot and stays as OOB management:
```bash
nmcli connection modify "<WIFI_SSID>" connection.autoconnect yes
nmcli connection modify "<WIFI_SSID>" ipv4.route-metric 600
```

---

## Immediate TODO (P2)

### 5. [ISP] Bridge Mode (eliminate double-NAT)

Access [ISP] gateway admin → enable IP Passthrough to sporeGate's WAN MAC.
This gives sporeGate the public IP directly.

### 6. CRS310 → pure L2 switch

Once routing is proven stable through sporeGate, strip L3 config from CRS310.
It becomes a pure 10G switch (its actual purpose).

### 7. Fix `gate.bootstrap` hang

The bootstrap command hangs when trying to fetch biomeos from depot (not available
on WAN depot at time of run). Investigate and fix — this is critical for future
onboarding of new gates.

---

## VPS Ownership (golgi + pepti)

You own the full VPS layer. This is NOT a shared responsibility — you manage these independently.

### golgi ([RELAY_PUBLIC])

| Service | Purpose | Management |
|---------|---------|------------|
| Forgejo | `git.primals.eco` — sovereign Git hosting | `systemctl restart forgejo` |
| hbbs | RustDesk rendezvous server (21115-21116) | `systemctl restart hbbs-membrane` |
| hbbr | RustDesk relay server (21117) | `systemctl restart hbbr-membrane` |
| 13 primals | Full NUCLEUS for depot serving + mesh | `gate.status` to check |
| Depot | Binary depot served via `hotSpring` | `/opt/membrane/plasmidBin/` |

```bash
ssh root@[RELAY_PUBLIC]
# Key: your SSH key is registered (verify: ssh-add -l)
# If not: cat ~/.ssh/id_ed25519.pub | ssh root@[RELAY_PUBLIC] "cat >> ~/.ssh/authorized_keys"
```

### pepti (build authority)

| Service | Purpose | Management |
|---------|---------|------------|
| Cargo builds | x86_64 + aarch64 cross-compile | `plasmid.harvest --all-primals` |
| Depot generation | Populates binaries for all gates | `/opt/membrane/plasmidBin/` |
| cellMembrane at HEAD | Structural sync reference | `git pull` in `~/Development/ecoPrimals/gardens/cellMembrane` |

```bash
ssh root@pepti
# IP is in wateringHole/compute-sharing docs
# Same key pattern as golgi
```

### What you do on VPS

1. **Restart relay**: If RustDesk stops working → `ssh root@[RELAY_PUBLIC] "systemctl restart hbbs-membrane hbbr-membrane"`
2. **Rebuild depot**: If primals are updated → SSH to pepti, `cd ~/Development/ecoPrimals/gardens/cellMembrane && git pull && cargo build --release` (or evolve `plasmid.harvest`)
3. **Manage Forgejo**: Repos, SSH keys, webhooks → `https://git.primals.eco` web UI or Forgejo API
4. **Monitor health**: `ssh root@[RELAY_PUBLIC] "membrane gate.status"` should report 13/13

---

## Cascade Autonomy

You own the bidirectional sync pipeline. Here's how it works:

### Current mechanism (ff-merge, commit 8f4e4eb)

```bash
# From any gate with cellMembrane:
membrane gate.cascade
# This:
# 1. Fetches from both remotes (origin=forgejo, github=github)
# 2. Attempts ff-merge (preserves SHA identity)
# 3. Falls back to rebase only if genuinely diverged
# 4. Pushes to BOTH remotes (push_target=all)
```

### Manual cascade (if membrane command isn't available):

```bash
cd ~/Development/ecoPrimals/gardens/cellMembrane  # or any primal
git fetch origin && git fetch github
git merge --ff-only origin/main || git rebase origin/main
git push origin main && git push github main
```

### Future: Event-driven (Wave 115 Stream 6)

Set up Forgejo webhooks that auto-trigger cascade on push. Eliminates manual intervention.
This is YOUR evolution target — implement when ready.

---

## Omada/Eero/flockGate (Remaining Mesh)

### Omada-wired towers (P1)

Omada is an SFP+ L2 switch — towers wired to it should be on 192.168.4.x (your DHCP).
SSH-push the config string to each (no manual typing on each machine):

```bash
for host in <tower_hostnames>; do
  ssh $host "pkexec rustdesk --config '[RUSTDESK_CONFIG_PURGED]'"
done
```

If Omada has L3/VLAN config: operator will supply Omada controller password. Log in and
verify it's pure L2 (bridge mode). If not, switch to bridge so all wired devices get
sporeGate DHCP directly.

### Eero WiFi clients (P2)

Eeros likely run their own NAT/DHCP. WiFi clients are on a different subnet.
Options (in order of preference):
1. **Bridge mode**: Eeros become dumb WiFi APs, sporeGate serves DHCP to WiFi clients too
2. **Add routing**: If Eero must keep NAT, add sporeGate nftables rules for Eero subnet

### flockGate — WAN/offsite (P1)

flockGate is at a remote location, currently on **public** RustDesk relay.
Safe migration:
1. SSH from golgi → flockGate (if SSH key authorized): `ssh flockGate "pkexec rustdesk --config '...'"`
2. Use current public RustDesk session to run the config command
3. Physical visit (last resort)

Risk: if sovereign relay goes down after switching, flockGate is unreachable until fix.
Mitigation: ensure golgi hbbs/hbbr is healthy before switching.

### Long-term: `membrane remote.configure`

Evolve cellMembrane to have a command that auto-discovers SSH-reachable gates and pushes
relay config to all of them. No manual per-machine work.

---

## Transition Period

Two delivery channels are active until you demonstrate full autonomy:

1. **USB Kit** — Physical handoff with latest blurbs, configs, AARs. Read on boot.
2. **Git Push** — Overwatch pushes FRAGO + handoffs to both GitHub and Forgejo. You pull.

**You are autonomous when you can:**
- [ ] SSH into golgi and pepti independently
- [ ] Run cascade (push to both remotes) without overwatch help
- [ ] Manage Forgejo (repos, keys, webhooks) solo
- [ ] Restart relay services and verify mesh health
- [ ] Push RustDesk config to new gates via SSH

Once all checkboxes are true, USB channel retires and you operate purely from Git.

---

## Architecture Reference

```
Internet ──► [ISP] Gateway ──► sporeGate (YOU) ──► CRS310 switch ──► LAN gates
                              enp1s0 (WAN)       eno1 (LAN)
                              192.168.1.233       192.168.4.1/22
                              
                              WiFi (wlp3s0) ─── out-of-band management
                              192.168.1.212       (fallback if wired breaks)
```

LAN Devices (served by your DHCP):
- eastGate: 192.168.4.30 (tower, overwatch)
- fieldGate: 192.168.4.36 (NUC, canary)
- + other devices (phones, peripherals)

VPS (accessible via WAN):
- golgi: [RELAY_PUBLIC] (Forgejo, relay, mesh hub)
- pepti: build authority (cargo builds)

---

## Key Ecosystem Docs

- `infra/wateringHole/impulses/active/2026-06-16T21-53_eastGate__wave115-sovereign-mesh.toml` — ACTIVE FRAGO
- `infra/wateringHole/compute-sharing/NETWORK_SOVEREIGNTY.md` — full architecture
- `infra/wateringHole/compute-sharing/SPOREGATE_ACTIVATION_BLURB.md` — activation steps
- `infra/wateringHole/compute-sharing/RUSTDESK_CONFIG.md` — relay config string + instructions
- `infra/wateringHole/handoffs/AAR_RUSTDESK_HAIRPIN_NAT_SPOREGATE_JUN16_2026.md` — hairpin NAT AAR
- `gardens/cellMembrane/specs/` — membrane command specs
- `infra/wateringHole/handoffs/primalSpring/GENETICS_ARCHITECTURE_EUKARYOTIC_MODEL_JUN16_2026.md` — genetics model

---

## Biological Analogy

You are literally the **cell membrane** — the selective permeability barrier between
the cytoplasm (LAN) and the extracellular matrix (internet). You decide what gets in,
what gets out, and how internal organelles (gates) communicate with the outside world.

WiFi = flagellar emergency signaling (secondary path when primary wall is compromised).
