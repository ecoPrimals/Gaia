# sporeGate Blurb — Peptidoglycan DNS + Sovereign CI Ops

**Date**: Aug 1, 2026 | **Wave**: post-155n | **From**: eastGate overwatch
**Posture**: **DNS is a recurring SPOF. strandGate DNS dead. northGate 2-3s delays. Fix the peptidoglycan layer.**

---

## PRIORITY 1 — DNS (blocking everything)

sporeGate is the site router and sole DNS server for the LAN. When dnsmasq dies or stalls, every gate behind it loses DNS resolution. This has happened multiple times.

**Current symptoms (Aug 1, 2026):**

| Gate | Symptom |
|------|---------|
| strandGate | DNS completely dead. `ping 1.1.1.1` works (14ms). `curl https://git.primals.eco` fails. systemd-resolved has no working upstream. `resolvectl dns` override did NOT fix it — deeper persistent issue. |
| northGate | 2-3 second page load delays. Classic DNS timeout + fallback pattern. |
| Other LAN gates | Unknown — likely degraded. |

**Diagnosis tasks:**

```
1. Check dnsmasq status on sporeGate:
   systemctl status dnsmasq
   journalctl -u dnsmasq --since "1 hour ago"

2. Test DNS resolution FROM sporeGate itself:
   dig @127.0.0.1 google.com
   dig @127.0.0.1 git.primals.eco

3. Check what DHCP is handing out for DNS:
   grep -i dns /etc/dnsmasq.conf
   grep -i dns /etc/dnsmasq.d/*

4. Check stubby (upstream TLS resolver):
   systemctl status stubby
   dig @127.0.0.1 -p 5353 google.com   # stubby default port

5. Check if strandGate's problem is deeper than DNS:
   # On strandGate:
   resolvectl status
   systemctl status systemd-resolved
   journalctl -u systemd-resolved --since "1 hour ago"
   # Try direct resolution bypassing systemd-resolved:
   curl --resolve git.primals.eco:443:[RELAY_PUBLIC] https://git.primals.eco
```

**Fixes (in order):**

### Immediate: Get strandGate online

```bash
# On strandGate — bypass systemd-resolved entirely:
sudo systemctl restart systemd-resolved

# If that doesn't work, go direct:
sudo mkdir -p /etc/systemd/resolved.conf.d
sudo tee /etc/systemd/resolved.conf.d/fallback.conf << 'EOF'
[Resolve]
DNS=1.1.1.1 1.0.0.1
FallbackDNS=8.8.8.8
EOF
sudo systemctl restart systemd-resolved
```

### Permanent: Make DHCP hand out redundant DNS

```bash
# On sporeGate — /etc/dnsmasq.conf or /etc/dnsmasq.d/ecoPrimals.conf:
# Add a second DNS server so gates have fallback when dnsmasq dies:
dhcp-option=6,192.168.4.1,1.1.1.1

# Then restart:
sudo systemctl restart dnsmasq
```

All DHCP clients will now get TWO DNS servers. If sporeGate's dnsmasq dies, they fall back to Cloudflare automatically instead of hanging.

### Permanent: Auto-restart dnsmasq

```bash
# On sporeGate — add watchdog to dnsmasq service:
sudo systemctl edit dnsmasq
# Add:
[Service]
Restart=always
RestartSec=5
```

This ensures dnsmasq comes back automatically if it crashes, like the primals do with their systemd units.

---

## PRIORITY 2 — Sovereign CI Ops (steady state)

Sovereign CI is LIVE and working. These are ongoing ops responsibilities:

| Task | Status |
|------|--------|
| Depot maintenance | 46 binaries, BLAKE3 verified. Steady state. |
| J12 sub-builder dispatch | LIVE E2E via SSH to blueGate. Evolve → songBird IPC (glacial). |
| sporePrint auto-publish | Forgejo hook wired. Working. |
| Post-receive hooks | 3 bugs fixed (dispatcher, case, category). Stable. |

No action needed unless a team pushes evolution and the pipeline fails.

---

## PRIORITY 3 — Topology investigation (G29)

Once DNS is fixed, investigate the full peptidoglycan health:

```
1. Can every LAN gate resolve DNS consistently? (audit all gates)
2. What is the latency profile from each gate to:
   - sporeGate (192.168.4.1)
   - golgiBody (10.13.37.1 via WG, and [RELAY_PUBLIC] direct)
   - Forgejo (git.primals.eco)
   - Public internet (1.1.1.1)
3. Port→gate physical mapping (CRS310 + Omada + TL-SG605S-M2)
4. Is 10G backbone healthy? (CRS310↔Omada AOC)
5. WiFi bridge configs (Flint H1, Flint 2) — documented?
```

This feeds into G29 (Peptidoglycan isomorphism). The LAN should be self-healing — when one DNS daemon dies, gates should still resolve. When one path degrades, traffic should reroute. We're not there yet.

---

*sporeGate is the peptidoglycan anchor for house1. DNS is its most critical function after NAT. Fix DNS first, then investigate topology. The system can't deploy, build, or cascade if gates can't resolve names.*
