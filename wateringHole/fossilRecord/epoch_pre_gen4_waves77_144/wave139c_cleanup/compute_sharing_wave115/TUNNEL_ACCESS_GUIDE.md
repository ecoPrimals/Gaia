# Tunnel Access Guide — External JupyterHub Access

**Security posture**: Phase 1 — Assume insecure. Human monitors.
**Pattern**: Make `127.0.0.1:8000` on the gate reachable from an
external user's machine.

---

## Physical Context

The ecoPrimals cluster is a LAN — ~11 machines in a basement on Cat6e
ethernet. External access means punching a hole from the internet to
one machine on this LAN. The recommended pattern:

```
Internet → [tunnel] → NUC intake node → Cat6e → workload gate (JupyterHub)
```

The NUC is expendable — no valuable data, easy to wipe. The workload
gate (strandGate, biomeGate, etc.) never directly faces the internet.
The tunnel terminates at the NUC; the NUC reverse-proxies to the
internal gate running JupyterHub.

For Phase 1, this can be simplified: run everything on one gate (tunnel
+ JupyterHub) if LAN isolation isn't yet a priority. Split to NUC
intake + internal gate when the first external user connects.

---

## Option A: Tailscale (Recommended for Phase 1)

Tailscale creates a WireGuard-based mesh VPN with zero firewall
configuration. Both the gate operator and the friend install Tailscale,
join the same tailnet (or use share nodes), and the friend accesses
JupyterHub via the gate's Tailscale IP.

### Gate Setup (one-time)

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Start and authenticate
sudo tailscale up

# Note your Tailscale IP
tailscale ip -4
```

Then update `jupyterhub_config.py` to bind on the Tailscale interface:

```python
# Bind to Tailscale IP instead of localhost
c.JupyterHub.ip = '0.0.0.0'
# OR more restrictive: bind only to the Tailscale interface
# c.JupyterHub.ip = '<tailscale-ip>'
```

### Friend Setup

```bash
# Install Tailscale on their machine
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

The operator shares the node or invites the friend to the tailnet.
Friend accesses: `http://<gate-tailscale-ip>:8000`

### Pros
- Zero firewall/NAT configuration
- Encrypted transport (WireGuard under the hood)
- Easy to revoke access (remove from tailnet)
- Free for personal use (up to 100 devices)

### Cons
- Requires a Tailscale account
- Third-party dependency (Tailscale control plane)
- Not sovereign — acceptable for Phase 1, not for Phase 4

---

## Option B: SSH Tunnel

The friend uses an SSH tunnel to forward the gate's JupyterHub port
to their local machine. Requires SSH server on the gate and the friend
to have an SSH account.

### Gate Setup (one-time)

```bash
# Install SSH server
sudo apt install openssh-server

# Ensure TCP forwarding is enabled (default on most distros)
# In /etc/ssh/sshd_config:
#   AllowTcpForwarding yes

sudo systemctl enable ssh
sudo systemctl start ssh
```

Create a limited account for the friend:

```bash
sudo adduser --disabled-password <friend-username>
# Add their SSH public key
sudo mkdir -p /home/<friend-username>/.ssh
sudo cp <friend-pubkey> /home/<friend-username>/.ssh/authorized_keys
sudo chown -R <friend-username>: /home/<friend-username>/.ssh
```

### Friend Connects

```bash
# From their machine:
ssh -L 8000:localhost:8000 <friend-username>@<gate-ip-or-domain>

# Then open in browser:
# http://localhost:8000
```

### Pros
- No third-party dependencies
- Encrypted (SSH)
- Fine-grained access control (per-user keys)
- Standard tooling, works everywhere

### Cons
- Requires SSH server exposed to the internet (port 22 or custom)
- Requires NAT port forwarding on home router
- Friend must keep SSH session open
- More operational burden (key management, fail2ban, etc.)

---

## Option C: WireGuard (Manual)

Direct WireGuard VPN between the gate and the friend. No third-party
control plane. Fully sovereign but more setup.

### Gate Setup

```bash
sudo apt install wireguard

# Generate keys
wg genkey | tee /etc/wireguard/privatekey | wg pubkey > /etc/wireguard/publickey

# Configure /etc/wireguard/wg0.conf
```

```ini
[Interface]
PrivateKey = <gate-private-key>
Address = 10.0.0.1/24
ListenPort = 51820

[Peer]
PublicKey = <friend-public-key>
AllowedIPs = 10.0.0.2/32
```

```bash
sudo wg-quick up wg0
sudo systemctl enable wg-quick@wg0
```

### Friend Setup

```ini
[Interface]
PrivateKey = <friend-private-key>
Address = 10.0.0.2/24

[Peer]
PublicKey = <gate-public-key>
Endpoint = <gate-public-ip>:51820
AllowedIPs = 10.0.0.1/32
PersistentKeepalive = 25
```

Friend accesses: `http://10.0.0.1:8000`

### Pros
- Fully sovereign — no third-party dependencies
- Kernel-level performance
- songBird evolution path (BTSP can eventually replace WireGuard keys)

### Cons
- Requires NAT port forwarding (UDP 51820)
- Manual key exchange
- More complex setup for non-technical friends

---

## Option D: RustDesk via cellMembrane (Sovereign Relay)

Self-hosted RustDesk server on the cellMembrane VPS provides remote
desktop access to any gate without third-party dependencies. RustDesk
handles NAT traversal, encryption, and relay — same architecture as
Songbird but for human desktop sessions.

### Gate Setup (one-time)

```bash
# Install RustDesk client (Debian/Ubuntu)
wget https://github.[KEY_SCRUBBED]-<ver>-x86_64.deb
sudo dpkg -i rustdesk-*.deb

# Configure to use cellMembrane as rendezvous/relay
# In RustDesk client settings:
#   ID Server:    [RELAY_PUBLIC]
#   Relay Server: [RELAY_PUBLIC]
#   Key:          [KEY_SCRUBBED]
```

### Friend / Remote Gate Connects

Install RustDesk on their machine with the same server and key config.
Enter the gate's RustDesk ID to connect. All traffic routes through
the cellMembrane relay, encrypted end-to-end.

### Pros
- Fully sovereign — self-hosted rendezvous and relay on cellMembrane
- Encrypted end-to-end (RustDesk encryption + server keypair verification)
- No third-party control plane
- Works across NAT (hole-punching via hbbs, relay via hbbr)
- GUI remote desktop, not just terminal access

### Cons
- Requires RustDesk client on both ends
- Relay traffic traverses cellMembrane VPS (bandwidth-limited)
- Server keypair must be distributed to each client

### Relationship to Other Options
- **Tailscale** (Option A): Third-party control plane, zero-config but not sovereign
- **SSH** (Option B): Terminal only, requires port forwarding
- **WireGuard** (Option C): Sovereign but manual key management, no GUI
- **RustDesk** (Option D): Sovereign GUI remote desktop via cellMembrane relay

---

## Recommendation for Phase 1

**Use Tailscale** for the first ABG connection. It's zero-config, free,
and encrypted. The third-party dependency is acceptable under the Phase 1
"assume insecure" posture — we're not trusting it with security, we're
trusting it with convenience.

### Tunnel Evolution — Eliminating External Dependencies

Each phase replaces a third-party dependency with sovereign infrastructure:

| Phase | Tunnel | External Dependency |
|-------|--------|---------------------|
| 1 | Tailscale | Tailscale control plane |
| 1.5 | RustDesk via cellMembrane | Self-hosted (VPS only) — sovereign GUI remote desktop |
| 2 | WireGuard (manual keys) | None (but manual key management) |
| 3 | songBird NAT traversal | STUN/TURN relay (can self-host) |
| 4 | Full BTSP tunnel | **Zero** — bearDog keys, songBird transport, no externals |

The endgame: a BTSP-only tunnel where bearDog handles identity,
songBird handles NAT traversal and transport, and no external service
(Tailscale, Cloudflare, GitHub) sits in the path. We get there in
cycles — each cycle validates the next primitive.

This mirrors the sporePrint evolution: GitHub Pages + Cloudflare today,
self-hosted petalTongue tomorrow, BTSP-only sovereign site eventually.

**Membrane channel mapping**: Tunnel Phase 3 (Songbird NAT) is where
the membrane channel architecture begins. The VPS relay is **Channel 2
(Relay)** — see `MEMBRANE_CHANNEL_ARCHITECTURE.md` for the full model
of how Channel 2 (Relay), Channel 1 (Signal/DNS), and Channel 3
(Surface/TLS) compose into the external surface. Earlier tunnel phases
(Tailscale, WireGuard) bypass the membrane architecture entirely.

---

## Security Checklist for Any Tunnel

- [ ] JupyterHub binds to localhost by default — only expose after tunnel is configured
- [ ] Per-user Linux accounts with PAM authentication
- [ ] Resource limits (cgroups) per notebook server
- [ ] Human monitors JupyterHub logs during external sessions
- [ ] No sensitive data on the compute gate beyond what the project needs
- [ ] Kill switch: operator can stop JupyterHub or tear down tunnel instantly
- [ ] User data lives in `~/notebooks` — easy to back up and wipe

---

## Testing Procedure (Pre-External User)

Before inviting an ABG member, verify the tunnel works end-to-end:

1. **Start JupyterHub**: `bash ~/jupyterhub/start.sh`
2. **Set up tunnel** (Tailscale, SSH, or WireGuard)
3. **From a second device** on the tailnet/VPN/tunnel:
   - `curl http://<gate-tunnel-ip>:8000/hub/api/` → should return `{"version": "5.4.5"}`
   - Open `http://<gate-tunnel-ip>:8000` in browser → login page
   - Log in with test account credentials
   - Launch a notebook, select the "Bioinformatics (Python 3.12)" kernel
   - Run: `import scanpy; print(scanpy.__version__)` → verify package loads
   - Run: `import torch; print(torch.cuda.is_available())` → verify GPU access (if applicable)
4. **Monitor from gate**: watch JupyterHub logs for activity
5. **Test kill switch**: stop JupyterHub, verify tunnel drops
6. **Test idle culling**: leave notebook idle for 1+ hour, verify server shuts down

---

*This guide covers Phase 1 tunnel options. Each external dependency
is a target for elimination. Tailscale → WireGuard → songBird → full
BTSP. We get there in cycles.*
