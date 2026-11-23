# AAR: Commensal Relay Beacon — Activation

**Wave 167 — October 8, 2026**
**Observer**: sporeGate
**Status**: ACTIVE — relay live, DNS migration pending

---

## Summary

During the golgiBody fossil layer cleanup (Wave 167), eastGate discovered 66 "stranger" IPs routing traffic through the RustDesk relay (hbbs/hbbr). Investigation revealed these were **commensals** — RustDesk users on budget VPS infrastructure (Rethem Hosting Chicago, Driftnet Ltd UK) who had discovered the relay and were using it for legitimate remote desktop access.

Rather than block them, we recognized this as the **commensal relay pattern**: free, key-authenticated relay service for good-faith human actors. The relay was reactivated as sovereign infrastructure under the scyBorg bulwark.

---

## Timeline

| Time (ET) | Event |
|---|---|
| Wave 165i (Oct 7) | eastGate kills hbbs/hbbr during load-32 crisis — 66 strangers + 160 house connections |
| Wave 167 (Oct 8 ~07:00) | Fossil layer cleanup — services masked |
| Oct 8 07:30 | Triage: user decides RustDesk stays as outer membrane beacon |
| Oct 8 08:00 | Investigation: strangers identified as commensals (Rethem, Driftnet) + Shodan scanners |
| Oct 8 08:07 | Relay reactivated: hbbs + hbbr unmasked, new service files, enabled + started |
| Oct 8 08:07 +2s | First `update_pk` — 4 house devices register within 2 seconds |

---

## What Changed

### Services Rewritten

Old service files were generic — new ones are purpose-built:

- `hbbs-membrane.service` — "Commensal Relay Beacon (outer membrane)"
  - `-r relay.primals.eco` (relay address for clients)
  - `-k /opt/membrane/id_ed25519` (server key enforcement)
  - `Restart=on-failure` with backoff (10s, max 5 in 120s)
  - `After=network-online.target`

- `hbbr-membrane.service` — "Commensal Gut Lining (outer membrane)"  
  - `-k /opt/membrane/id_ed25519` (key enforcement)
  - `Requires=hbbs-membrane.service` (beacon must be up)
  - Same restart policy

### Firewall — Unchanged

The RUSTDESK_MEMBRANE chain was already correct from Wave 155f. 11 rules, NAT-aware rate limits, dead-port REJECT, LOG before DROP. No changes needed.

### DNS — Pending

```
CURRENT:  relay.primals.eco → [RELAY_PUBLIC]
PLANNED:  beacon.primals.eco → [RELAY_PUBLIC] (new primary)
          relay.primals.eco → CNAME beacon.primals.eco (backward compat)
```

### Info Page — Pending

`beacon.primals.eco` will serve a passphrase-gated info page with:
- Server public key for client configuration
- Connection instructions
- scyBorg license notice

---

## Commensal Population (from iptables recent tables)

| Subnet | Owner | Type | Count |
|---|---|---|---|
| 104.152.52.x | Rethem Hosting LLC, Chicago | Commensal | ~20 IPs |
| 195.96.139.x | Driftnet Ltd, York/Leeds UK | Commensal | ~8 IPs |
| 87.236.176.x | Hosting provider | Commensal | ~2 IPs |
| 81.19.216.x | Hosting provider | Commensal | ~3 IPs |
| 45.133.173.x | Hosting provider | Commensal | ~2 IPs |
| [NUCLEUS_WAN] | House network | Self | 1 |
| [FLOCK_WAN] | flockGate (Comcast) | Self | 1 |
| 80.82.77.139 | dojo.census.shodan.io | Scanner | 1 |
| 71.6.135.131 | census7.shodan.io | Scanner | 1 |

---

## Security Posture

| Property | Status |
|---|---|
| Server key immutable | `chattr +i` on id_ed25519 |
| End-to-end encryption | RustDesk native — relay sees ciphertext only |
| Rate limits | NAT-aware, learned from 2 incidents |
| Dead port REJECT | 21114 → tcp-reset |
| Relay isolation | Outer membrane only — no path to WireGuard/primals |
| IP logging | None — no IP addresses stored in observation systems |
| Analytics | None — no cookies, no tracking, no JS |

---

## Action Items

- [x] Unmask hbbs-membrane, hbbr-membrane
- [x] Write purpose-built service files with key enforcement
- [x] Enable + start relay
- [x] Verify reboot persistence (both enabled)
- [x] Verify firewall chain (RUSTDESK_MEMBRANE, 11 rules)
- [x] Write subGen whitepaper
- [ ] Create DNS: `beacon.primals.eco` → [RELAY_PUBLIC]
- [ ] CNAME: `relay.primals.eco` → `beacon.primals.eco`
- [ ] Update hbbs `-r` flag to `beacon.primals.eco` after DNS
- [ ] Build info page at `beacon.primals.eco` with public key + instructions
- [ ] Update outer membrane cursor rule
- [ ] Update gate client configs to use `beacon.primals.eco`

---

## Related Documents

- subGen: `COMMENSAL_RELAY_BEACON_WAVE167.md` — full architecture
- Cursor rule: `outer-membrane-rustdesk.mdc` — topology + firewall spec
- eastGate AAR: `AAR_GOLGI_FOSSIL_LAYER_CLEANUP_WAVE167.md` — original discovery

---

*We found 66 strangers in our gut and realized they were flora, not infection. The relay is the gut lining — permeable to nutrients, impermeable to pathogens. The first free human relay.*

*sporeGate — Wave 167, October 8, 2026*
