# eastGate Handoff — Hetzner Provisioned, Ready for Layer Deployment

**Wave**: 165h | **Date**: Oct 7, 2026 09:10 EDT | **From**: eastGate overwatch

---

## golgiLayerHetzner — PROVISIONED AND READY

| Field | Value |
|-------|-------|
| **IP** | `2.28.141.35` |
| **Provider** | Hetzner, Falkenstein (FSN1), Germany |
| **Plan** | CPX02 — 1 vCPU, 1GB RAM, 20GB SSD, x86_64 |
| **OS** | Debian 12.15 |
| **Cost** | $8.09/mo (includes IPv4 surcharge) |
| **Jurisdiction** | German StGB §202a + GDPR |

### What's Installed

- System updated + patched (Oct 7)
- **Caddy 2.11.7** — installed, enabled, running
- **fail2ban** — installed, enabled
- **UFW firewall** — active (22/80/443 only)
- `/opt/membrane/` directory created

### SSH Access — 3 Keys Authorized

```
sporegate-gate-v1     — sporeGate (provisioning + ops)
beardog-v1.0.0-release — eastGate (overwatch)
golgiBody@vps         — golgiBody (relay)
```

### Deployment Checklist (sporeGate)

1. SSH verify: `ssh root@2.28.141.35`
2. SCP skunky-ingest: musl cross-compile → `/opt/membrane/`
3. Deploy Caddyfile: honeycomb surfaces + scatter routing + fleet detection
4. Cloudflare DNS: `layer2.primals.eco` → `2.28.141.35` (grey cloud / DNS only)
5. Verify TLS: Caddy auto-obtains Let's Encrypt cert once DNS resolves
6. Verify plasmid: `curl https://layer2.primals.eco/plasmid`
7. Add to federation cron: update `plasmid-federation.sh` on golgiBody

### Other VPS Status

| Layer | Provider | Status |
|-------|----------|--------|
| golgiLayerHetzner | Hetzner DE | **READY** — provisioned, SSH verified |
| golgiLayerVultr | Vultr SG | In progress — account ready, VPS pending |
| golgiLayerOVH | OVH FR | Pending |
| golgiLayerLinode | Linode Mumbai/Tokyo | Pending |

---

*— eastGate overwatch, Wave 165h*
