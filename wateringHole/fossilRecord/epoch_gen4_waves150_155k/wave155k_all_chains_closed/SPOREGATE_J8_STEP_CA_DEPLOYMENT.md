# sporeGate Deployment Team: J8 step-ca SSH Certificate Authority

**Date**: 2026-07-28 | **Priority**: P1 | **Owner**: sporeGate deployment team
**Dependency**: cellMembrane J8 (key enrollment portal)

---

## What

Deploy **step-ca** (Smallstep) as a sovereign SSH certificate authority on
golgiBody (or sporeGate). This replaces manual SSH key exchange via chat with
short-lived SSH certificates issued by our own CA.

step-ca is a single Go binary (~100MB RAM), Apache 2.0 licensed, 8.5k stars,
mature (v0.30.2). It issues both X.509 and SSH certificates.

## Why

SSH keys are currently exchanged via chat (J8 jelly string). This creates:
- No audit trail for key distribution
- No expiry on authorized_keys entries
- TOFU (Trust On First Use) on every new gate connection
- Manual `deploy_membrane.sh keys` for VPS authorized_keys management

## Deployment Steps

### 1. Install step-ca on golgiBody

```bash
# Install step CLI + step-ca
wget https://dl.smallstep.com/gh-release/cli/docs-cli-install/v0.28.6/step-cli_0.28.6_amd64.deb
wget https://dl.smallstep.com/gh-release/certificates/docs-ca-install/v0.30.2/step-ca_0.30.2_amd64.deb
sudo dpkg -i step-cli_*.deb step-ca_*.deb

# Initialize with SSH support
step ca init \
  --name "ecoPrimals CA" \
  --dns "ca.primals.eco,golgi.primals.eco,10.13.37.2" \
  --address ":9443" \
  --provisioner admin \
  --ssh
```

### 2. Configure systemd service

```bash
sudo useradd --system --home /etc/step-ca --shell /bin/false step
sudo mkdir -p /etc/step-ca
sudo cp -r $(step path)/* /etc/step-ca/
sudo chown -R step:step /etc/step-ca
```

Create `/etc/systemd/system/step-ca.service`:
```ini
[Unit]
Description=ecoPrimals SSH Certificate Authority (step-ca)
After=network.target

[Service]
Type=simple
User=step
ExecStart=/usr/bin/step-ca /etc/step-ca/config/ca.json --password-file /etc/step-ca/secrets/password
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 3. Configure all gates to trust the CA

On each gate, add to `/etc/ssh/sshd_config`:
```
TrustedUserCAKeys /etc/ssh/step_user_ca.pub
```

Copy the user CA public key to each gate:
```bash
step ssh config --roots > /etc/ssh/step_user_ca.pub
sudo systemctl restart sshd
```

### 4. Issue host certificates (eliminates TOFU)

On each gate:
```bash
sudo step ssh certificate $(hostname) /etc/ssh/ssh_host_ecdsa_key.pub \
  --host --sign \
  --provisioner admin
```

Add to `/etc/ssh/sshd_config`:
```
HostCertificate /etc/ssh/ssh_host_ecdsa_key-cert.pub
```

### 5. DNS entry

Add `ca.primals.eco` DNS record pointing to golgiBody's WAN IP (or mesh IP
`10.13.37.2` for mesh-only access).

### 6. Caddy reverse proxy (optional)

If exposing over HTTPS:
```
ca.primals.eco {
    reverse_proxy localhost:9443
}
```

## Operator Workflow (after deployment)

```bash
# Bootstrap step CLI on a new gate
step ca bootstrap --ca-url https://ca.primals.eco:9443 --fingerprint <ROOT_FP>

# Get an SSH certificate (valid 8h)
step ssh certificate sporegate@primals.eco ~/.ssh/id_ecdsa

# SSH using certificate (no authorized_keys needed)
ssh root@golgi.primals.eco

# Renew before expiry
step ssh renew ~/.ssh/id_ecdsa-cert.pub ~/.ssh/id_ecdsa --force
```

## What cellMembrane Will Wire

cellMembrane `gate.enroll` will add a phase 8 (`ssh_cert`) that:
1. Calls step-ca API to request an SSH certificate
2. Installs the cert locally
3. Sets up renewal (systemd timer or bare cron)

New CLI commands: `gate.keys` (status) and `gate.keys.renew` (force renewal).

## Constants cellMembrane Will Use

| Constant | Default | Env Override |
|----------|---------|-------------|
| CA URL | `https://ca.primals.eco:9443` | `STEP_CA_URL` |
| SSH cert lifetime | `8h` | `STEP_CA_SSH_LIFETIME` |
| Provisioner | `admin` | `STEP_CA_PROVISIONER` |
| CA fingerprint | (set at deploy) | `STEP_CA_FINGERPRINT` |

## Deliverables

- [ ] step-ca running on golgiBody with SSH CA enabled
- [ ] User CA key distributed to all online gates
- [ ] Host certificates on golgiBody and sporeGate (first two)
- [ ] DNS `ca.primals.eco` pointing to golgiBody
- [ ] Root CA fingerprint shared back to cellMembrane team

---

*J8 jelly string: SSH keys exchanged via chat → sovereign certificate authority.
cellMembrane code (Phase 2) depends on this deployment being live.*
