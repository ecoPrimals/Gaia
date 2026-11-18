# ironGate Enrollment — Complete SSH + NUCLEUS

**Priority**: P0 | **Owner**: sporeGate overwatch | **Gate**: ironGate (192.168.4.237)
**Mesh**: WG .7 configured but no handshake yet — needs golgi peer on ironGate side

---

## Step 1: SSH Key (via RustDesk into ironGate)

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILU4i9hEtHJA02/JZ8XR/OHaR/bSiuAaDRMhdJX7zuRp sporegate-gate-v1" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

Verify from sporeGate: `ssh irongate@192.168.4.237`

## Step 2: WireGuard (from sporeGate SSH into ironGate)

ironGate needs a wg0 config pointing at golgi hub:

```bash
sudo apt install -y wireguard-tools
wg genkey | tee /tmp/wg_priv | wg pubkey > /tmp/wg_pub

cat <<WG | sudo tee /etc/wireguard/wg0.conf
[Interface]
PrivateKey = $(cat /tmp/wg_priv)
Address = 10.13.37.7/24

[Peer]
# golgi hub
PublicKey = $(ssh root@[RELAY_PUBLIC] "grep PrivateKey /etc/wireguard/wg0.conf | cut -d= -f2 | tr -d ' ' | wg pubkey")
Endpoint = [RELAY_PUBLIC]:51820
AllowedIPs = 10.13.37.0/24
PersistentKeepalive = 25
WG

sudo systemctl enable --now wg-quick@wg0
```

Then add ironGate's pubkey to golgi:
```bash
ssh root@[RELAY_PUBLIC] "wg set wg0 peer $(cat /tmp/wg_pub) allowed-ips 10.13.37.7/32"
```

Verify: `ping 10.13.37.1` from ironGate.

## Step 3: NUCLEUS Deploy (from sporeGate)

Same proven pattern as flockGate:

```bash
scp /opt/depot/primals/x86_64-unknown-linux-musl/* irongate@192.168.4.237:/tmp/primals/
ssh irongate@192.168.4.237 <<'DEPLOY'
sudo mv /tmp/primals/* /usr/local/bin/
mkdir -p ~/.config/systemd/user
# Copy membrane-nucleus@.service template
# Enable lingering: loginctl enable-linger $(whoami)
# Start all 13: for p in beardog songbird skunkbat toadstool barracuda coralreef loamspine rhizocrypt sweetgrass squirrel petaltongue nestgate biomeos; do systemctl --user enable --now membrane-nucleus@$p; done
DEPLOY
```

NestGate + BiomeOS will need the same fixes as eastGate/flockGate (JWT secret, neural-api subcommand).

## Step 4: Forgejo Push (fix remote URLs)

ironGate's key IS registered on Forgejo (ID 1). Likely has wrong remote URLs (same pepti pattern). Fix:

```bash
# For each repo:
git remote set-url origin ssh://git@git.primals.eco:2222/ecoPrimals/<repo>.git
git remote set-url forgejo ssh://git@git.primals.eco:2222/ecoPrimals/<repo>.git
```

## Done When

- [ ] `ssh irongate@192.168.4.237` works from sporeGate
- [ ] `ping 10.13.37.1` works from ironGate (WG mesh live)
- [ ] 11/13+ NUCLEUS primals running (user systemd)
- [ ] `git push forgejo main` succeeds from ironGate

**After**: ironGate Node team gets focused IDE blurb for ToadStool/BarraCuda/CoralReef compute work. All gates can push and interact.
