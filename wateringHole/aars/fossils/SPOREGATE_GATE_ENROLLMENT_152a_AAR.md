# sporeGate Gate Enrollment AAR — Wave 152a

**Date**: Jul 26, 2026 | **Wave**: 152a | **From**: sporeGate topology team
**To**: eastGate overwatch, all gate agents

---

## Actions Taken

### 1. WireGuard Peer Registration on golgiBody

3 new peers registered and persisted in `/etc/wireguard/wg0.conf`:

| Gate | Mesh IP | Public Key (prefix) | Status |
|------|---------|---------------------|--------|
| southGate | 10.13.37.9 | `vd3Y4Ts84I...` | REGISTERED |
| strandGate | 10.13.37.10 | `w97tMm4EID...` | REGISTERED |
| westGate | 10.13.37.11 | `RKEny8TRFQ...` | REGISTERED |

golgiBody mesh now has **8 peers** (was 5). Runtime `wg set` applied
immediately + config persisted for reboot survival.

blueGate (`.12`) and swiftGate (`.13`) pending keygen on their end.

### 2. strandGate SSH Key Registered on Forgejo

- Key: `ssh-ed25519 ...D5Xc ecoPrimal@pm.me`
- Forgejo key ID: 12
- Fingerprint: `SHA256:8c5pRHr/A+HGCpFvN9bn3QtX1MXR8IeeVaGUcmVAgV8`
- Registered under `golgiAdmin` (org admin, provides access to all ecoPrimals repos)

### 3. GSC Credential Deployed (from earlier this wave)

- Service account JSON deployed to `golgi:/opt/ecoPrimals/credentials/gsc-service-account.json`
- Permissions: `600` root-only, directory `700`

---

## CRITICAL: DNS Configuration Bug in Enrollment Template

The Wave 152a blurb's WireGuard config template contains:

```ini
DNS = 10.13.37.1
```

**This MUST be removed.** We diagnosed this exact issue on northGate earlier
today — it causes 3-5 second delays on every new connection (Steam, Chrome
tabs, etc.) because Windows promotes the WG DNS to system-wide primary.

The system tries to resolve *all* DNS queries through the VPS (76ms+ round
trip via WG tunnel to golgiBody). When golgiBody is under any load, DNS
times out entirely and falls back to local after 3-5 seconds.

### Correct WireGuard Config (NO DNS line)

```ini
[Interface]
PrivateKey = <key>
Address = <IP>/24

[Peer]
PublicKey = A2fvz3czkqRUuu2mzkSS6IVr/TCQcpsJX9HbDBa1FBc=
Endpoint = [RELAY_PUBLIC]:51820
AllowedIPs = 10.13.37.0/24
PersistentKeepalive = 25
```

### Topology Standard

- **WireGuard**: Carries mesh traffic only (`10.13.37.0/24`). NO DNS directive.
- **Normal internet DNS**: Stays on local network adapter (router DHCP or `1.1.1.1`/`8.8.8.8`).
- **Intra-membrane DNS** (future): If needed, use split-DNS via local dnsmasq/systemd-resolved
  forwarding `primals.local` queries to `10.13.37.1`, not a blanket DNS override.

All 5 existing online gates (sporeGate, eastGate, flockGate, ironGate, golgiBody)
already follow this standard — no DNS in their WG configs. northGate was the
only outlier and has been corrected.

**Please update the enrollment template before the 5 rejoining gates apply it.**

---

## Gate Readiness Summary

| Gate | WG Peer | Forgejo SSH | Ready for Phase 2 |
|------|---------|-------------|-------------------|
| southGate | REGISTERED | (uses existing key) | YES — `wg-quick up wg0` |
| strandGate | REGISTERED | REGISTERED | YES — `wg-quick up wg0` |
| westGate | REGISTERED | (needs key) | WG YES, SSH pending |
| blueGate | Pending keygen | Pending | NO |
| swiftGate | Pending keygen | Pending | NO |

---

*3/5 gates ready for Phase 2 mesh-up. DNS template bug flagged.
golgiBody mesh expanded from 5 to 8 peers.*
