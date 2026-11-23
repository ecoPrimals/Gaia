# AAR: Enmeshment Phase 1-3 Complete — Two New Sensor Nodes

**Date**: Oct 7, 2026
**From**: eastGate overwatch
**To**: sporeGate ops
**Wave**: 165i
**Standards Applied**: THYMUS_SELF_RECOGNITION_STANDARD.md, VPS_ENMESHMENT_STANDARD.md

---

## Summary

eastGate completed Phase 1-3 enmeshment on both new VPS nodes per wateringHole standards. Both nodes are WireGuard-peered to golgiBody with thymus-compliant firewall chains. golgiBody now has **5 active handshakes** (was 3).

---

## golgiLayerLinode — Mumbai, India 🇮🇳

| Field | Value |
|-------|-------|
| Public IP | `172.232.85.202` |
| WireGuard IP | `10.13.37.14` |
| SSH user | `root` |
| Provider | Akamai/Linode, Nanode 1GB |
| WG pubkey | `+y1YdQqBr3YAPenuh46pydsbnE/Fkvh3O/pfh8mOsC0=` |
| WG latency to golgiBody | 208ms |

### Phases Completed

- ✅ **Phase 1**: `/etc/membrane/self-ips.txt` (127.0.0.1, 172.232.85.202, 10.13.37.14, 10.13.37.0/24, [NUCLEUS_WAN]), `/etc/hosts` self-resolution for git.primals.eco, membrane dirs created
- ✅ **Phase 2**: WG keys generated, wg0.conf written (golgiBody + sporeGate peers), `wg-quick@wg0` enabled + started, handshake confirmed
- ✅ **Phase 3**: MEMBRANE_RATE iptables chain — loopback bypass → self-IPs bypass → established → rate limit 80/443 (60 req/min) → accept. UFW allows 22, 80, 443, 51820/udp. Persisted to `/etc/iptables/rules.v4`

---

## golgiLayerOVH — Vint Hill, Virginia 🇺🇸

| Field | Value |
|-------|-------|
| Public IP | `40.160.96.29` |
| WireGuard IP | `10.13.37.15` |
| SSH user | **`debian`** (sudo required) |
| Provider | OVH US, 2 vCPU / 4GB RAM |
| WG pubkey | `W/O4X5Dj5k6jkZtGJ0p4fXaKl3ni3JRJEfIbt/FzeiQ=` |
| WG latency to golgiBody | 8ms |

### Phases Completed

- ✅ **Phase 1**: Same as Linode — self-ips.txt with 40.160.96.29 / 10.13.37.15, hosts self-resolution, membrane dirs
- ✅ **Phase 2**: Same — WG keys, config, enabled, handshake confirmed
- ✅ **Phase 3**: Same MEMBRANE_RATE chain, all commands via `sudo`

⚠️ **OVH uses `debian` user, not root.** All privileged ops require `sudo`. provision-golgi-layer.sh should detect this.

---

## golgiBody Peer Registration

Both peers added live to golgiBody and saved to config:

```bash
wg set wg0 peer "+y1YdQqBr3YAPenuh46pydsbnE/Fkvh3O/pfh8mOsC0=" allowed-ips 10.13.37.14/32 persistent-keepalive 25
wg set wg0 peer "W/O4X5Dj5k6jkZtGJ0p4fXaKl3ni3JRJEfIbt/FzeiQ=" allowed-ips 10.13.37.15/32 persistent-keepalive 25
wg-quick save wg0
```

---

## Current Mesh State (golgiBody)

| Peer | WG IP | Handshake | Status |
|------|-------|-----------|--------|
| sporeGate | .2 | 1m ago | ✅ active |
| ironGate | .5 | 1m ago | ✅ active |
| eastGate | .8 | 22s ago | ✅ active |
| **golgiLayerLinode** | **.14** | **22s ago** | **✅ NEW** |
| **golgiLayerOVH** | **.15** | **22s ago** | **✅ NEW** |
| (various) | .3,.6,.7,.10,.12,.13 | 46-70 days | ⚠️ stale |
| (configured) | .9,.11 | never | ○ never connected |

**5 active peers, up from 3.**

---

## What Needs sporeGate (Phase 4+)

### Phase 4: Forgejo Access
- [ ] Add both nodes' SSH keys to Forgejo (admin panel or API)
- [ ] Generate SSH keypairs on each node (`ssh-keygen -t ed25519 -C "<node>@primals.eco"`)
- [ ] Test: `ssh -p 2222 git@git.primals.eco`
- [ ] Clone wateringHole to `/opt/ecoPrimals/wateringHole`

### Phase 5: Services
- [ ] Deploy Caddy + skunky-ingest + scatter via `provision-golgi-layer.sh`
- [ ] Note: OVH script needs sudo-awareness (`debian` user)

### Phase 5.5: DNS
- [ ] `layer3.primals.eco` A → `172.232.85.202`
- [ ] `layer4.primals.eco` A → `40.160.96.29`
- [ ] After DNS + TLS: CT log discovery → fleet arrives within 24-48h

### Phase 6: Verification
- [ ] Full checklist from VPS_ENMESHMENT_STANDARD.md

### Phase 7: Cascade
- [ ] cascade-sense.timer enabled

### Also: sporeGate WG peering
- [ ] Register both pubkeys on sporeGate's wg0 for direct home network peering
- [ ] Linode: `+y1YdQqBr3YAPenuh46pydsbnE/Fkvh3O/pfh8mOsC0=` → 10.13.37.14/32
- [ ] OVH: `W/O4X5Dj5k6jkZtGJ0p4fXaKl3ni3JRJEfIbt/FzeiQ=` → 10.13.37.15/32

---

## Related AAR

See `AAR_AGENT_SCATTER_CLASSIFICATION_GAP.md` — agents browsing git.primals.eco from the outside get scatter because the classifier output doesn't reach the routing layer. Thymus knows the difference; Caddy doesn't ask.

---

*eastGate overwatch — Phase 1-3 complete. Thymus first, then organs.*

*Wave 165i, Oct 7, 2026*
