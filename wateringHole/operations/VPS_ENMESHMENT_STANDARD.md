# VPS Enmeshment Standard — Bringing a Node Into the Mesh

**Wave**: 163 | **Authority**: wateringHole consensus
**Applies to**: All new VPS nodes (DigitalOcean, Hetzner, etc.)
**Prerequisites**: GATE_SETUP_STANDARD.md, THYMUS_SELF_RECOGNITION_STANDARD.md, GATEHOUSE_DARKFOREST_STANDARD.md

---

## Overview

A VPS node starts as bare metal with a public IP and nothing else.
Enmeshment is the process of integrating it into the organism — giving it
identity, connectivity, self-recognition, and purpose. The process follows
the diderm envelope model: the node must have both an outer membrane
(public-facing services) and inner membrane (WireGuard mesh) before it
can participate.

---

## Phase 0: Identity

Before touching the node, establish its identity in wateringHole:

```bash
# 1. Choose a name (biological, descriptive of function)
# 2. Add to ecosystem_manifest.toml [gates.<name>]
# 3. Assign WireGuard IP from the 10.13.37.x pool
# 4. Document in TOPOLOGY_MAP.toml
```

| Field | Example |
|-------|---------|
| Name | `riboNode-fra` (Frankfurt relay) |
| WireGuard IP | `10.13.37.14` |
| Public IP | (assigned by provider) |
| Role | Relay, compute, storage, etc. |

---

## Phase 1: Base Layer (5 minutes)

SSH in as root. Run these in order:

```bash
# 1. System update
apt update && apt upgrade -y

# 2. Create membrane directory structure
mkdir -p /etc/membrane /opt/membrane/fossils /opt/membrane/live-terminal

# 3. Self-identity file (THYMUS_SELF_RECOGNITION_STANDARD.md)
cat > /etc/membrane/self-ips.txt << EOF
# Self-IPs for <NODE_NAME>
127.0.0.1
<PUBLIC_IP>
<WIREGUARD_IP>
10.13.37.0/24
<SPOREGATE_WAN_IP>
EOF

# 4. Hostname self-resolution
echo "127.0.0.1 <SERVICE_HOSTNAME>.primals.eco" >> /etc/hosts
# If cloud-init managed:
echo "127.0.0.1 <SERVICE_HOSTNAME>.primals.eco" >> /etc/cloud/templates/hosts.debian.tmpl

# 5. Install base tools
apt install -y wireguard ufw fail2ban iptables-persistent
```

---

## Phase 2: WireGuard (Inner Membrane)

```bash
# 1. Generate keys
wg genkey | tee /etc/wireguard/privatekey | wg pubkey > /etc/wireguard/publickey
chmod 600 /etc/wireguard/privatekey

# 2. Create config
cat > /etc/wireguard/wg0.conf << EOF
[Interface]
Address = <WIREGUARD_IP>/24
PrivateKey = $(cat /etc/wireguard/privatekey)
ListenPort = 51820

# golgiBody — relay hub
[Peer]
PublicKey = A2fvz3czkqRUuu2mzkSS6IVr/TCQcpsJX9HbDBa1FBc=
Endpoint = [RELAY_PUBLIC]:51820
AllowedIPs = 10.13.37.1/32
PersistentKeepalive = 25

# sporeGate — home network
[Peer]
PublicKey = obCKmO89eCvh106gUdqu77L4F1ViASdDirGEddqyYSA=
Endpoint = <SPOREGATE_WAN>:51820
AllowedIPs = 10.13.37.2/32, 192.168.4.0/22
PersistentKeepalive = 25
EOF

# 3. Enable
systemctl enable --now wg-quick@wg0

# 4. Register this node's public key on golgiBody and sporeGate
# (add [Peer] block to their wg0.conf, then `wg syncconf wg0 <(wg-quick strip wg0)`)
```

---

## Phase 3: Firewall (Outer Membrane)

```bash
# 1. UFW basics
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp          # SSH
ufw allow 51820/udp       # WireGuard
ufw enable

# 2. Create rate-limiting chains per THYMUS_SELF_RECOGNITION_STANDARD.md
# Follow the template: loopback bypass → self-IPs → established → rate limit → accept

# 3. Persist
netfilter-persistent save
```

---

## Phase 4: Forgejo Access

```bash
# 1. Generate SSH key
ssh-keygen -t ed25519 -C "<NODE_NAME>@primals.eco" -f ~/.ssh/id_ed25519 -N ""

# 2. Register on Forgejo (from a gate that has admin access)
# Add public key via Forgejo admin panel or API

# 3. Test
ssh -p 2222 git@git.primals.eco
# Expected: "Hi <user>! You've successfully authenticated..."

# 4. Clone wateringHole (first repo — contains all standards)
git clone ssh://git@git.primals.eco:2222/ecoPrimals/wateringHole.git /opt/ecoPrimals/wateringHole
```

---

## Phase 5: Services (Role-Dependent)

Deploy only the services needed for this node's role:

### Relay Node
```bash
# Caddy (reverse proxy + TLS)
# skunky-ingest (log analysis + thymus)
# bloom_live.py (if monitoring traffic)
```

### Compute Node
```bash
# songBird (mesh discovery)
# bearDog (secrets + BTSP)
# Application-specific primals
```

### Mirror Node
```bash
# Forgejo mirror (pull-only)
# sporePrint static hosting
```

---

## Phase 6: Verification

Run the full checklist:

```bash
# WireGuard
wg show | grep "latest handshake"    # Should show recent handshakes

# Self-recognition
cat /etc/membrane/self-ips.txt       # Should list all self-IPs
getent hosts *.primals.eco           # Should resolve to 127.0.0.1 for hosted services

# Firewall
iptables -L -n | head -5            # Should show chains
dmesg | grep RATELIMIT              # Should be empty (no self-hits)

# Git access
ssh -p 2222 git@git.primals.eco     # Should authenticate
time git push origin main            # Should complete < 2 seconds

# Mesh connectivity
ping -c 3 10.13.37.1                # golgiBody via WireGuard
ping -c 3 10.13.37.2                # sporeGate via WireGuard
```

---

## Phase 7: Cascade Integration

Once verified, the node should participate in the temporal cascade:

```bash
# Install membrane CLI (from wateringHole/tools/ or build from skunkBat)
# Enable cascade timer
systemctl enable --now cascade-sense.timer
```

The node is now enmeshed. It can receive impulses, sync repos, and
participate in the gossip mesh.

---

## Reference: Current Mesh Topology

```
                    ┌─────────────┐
                    │  golgiBody  │ 10.13.37.1
                    │ (relay hub) │ [RELAY_PUBLIC]
                    └──────┬──────┘
                           │ WireGuard
              ┌────────────┼────────────┐
              │            │            │
       ┌──────┴──────┐  ┌─┴──────┐  ┌──┴────────┐
       │  sporeGate  │  │  new   │  │  new      │
       │ 10.13.37.2  │  │ nodes  │  │  nodes    │
       │ (home, NAT) │  │  ...   │  │  ...      │
       └──────┬──────┘  └────────┘  └───────────┘
              │ LAN
    ┌─────────┼─────────┐
    │         │         │
 eastGate  ironGate  biomeGate
 .8        .5        (LAN)
```

All WireGuard peers route through sporeGate's WAN IP (NAT).
golgiBody is the star hub — every peer connects to it directly.
New VPS nodes add a [Peer] block for golgiBody and optionally sporeGate.
