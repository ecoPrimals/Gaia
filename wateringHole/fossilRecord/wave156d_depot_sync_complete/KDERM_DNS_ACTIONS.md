# K-Derm DNS Actions

**Date**: Aug 4, 2026 | **Wave**: 155v/156d
**Context**: Three-domain topology separation (G59)

---

## Summary

All three K-derm layers are now properly separated at the DNS level.

| Layer | Domain | DNS Provider | Status |
|-------|--------|-------------|--------|
| Outer membrane | primals.eco | **Cloudflare** | **LIVE** — Zola + Caddy on golgi |
| Peptidoglycan | nestgate.io | **Sovereign Knot DNS** (ns1/ns2.primals.eco) | **LIVE** — petalTongue on sporeGate via mesh |
| Inner membrane | primal.eco | **Sovereign Knot DNS** (ns1/ns2.primals.eco) | **SEALED** — all public A records REMOVED |

### DNS Infrastructure

```
primals.eco  → Cloudflare (albertus/serena.cloudflare.com)
nestgate.io  → Sovereign (ns1.primals.eco = golgi, ns2.primals.eco = golgi-ext)
primal.eco   → Sovereign (ns1.primals.eco = golgi, ns2.primals.eco = golgi-ext)
```

Sovereign DNS: **Knot DNS** with automatic DNSSEC signing. Master on golgi, slave on golgi-ext.

---

## Completed Actions

### DONE: primal.eco — all 6 public A records REMOVED

**When**: Aug 4, 2026 | **Where**: Knot DNS master (golgi)
**What**: Removed all A records from the primal.eco zone:
- `primal.eco` A → ~~137.184.197.151~~ **REMOVED**
- `api.primal.eco` A → ~~137.184.197.151~~ **REMOVED**
- `auth.primal.eco` A → ~~137.184.197.151~~ **REMOVED**
- `dns.primal.eco` A → ~~137.184.197.151~~ **REMOVED**
- `mesh.primal.eco` A → ~~137.184.197.151~~ **REMOVED**
- `relay.primal.eco` A → ~~137.184.197.151~~ **REMOVED**

Zone infrastructure (SOA, NS, DNSKEY, DNSSEC, CAA, TXT/SPF) preserved.
Zone serial: `2026060417`. Inner membrane is now invisible to the public internet.

### DONE: www.nestgate.io → fixed to golgi

**When**: Aug 4, 2026 | **Where**: Knot DNS master (golgi)
**What**: Changed `www.nestgate.io` A from `137.184.197.151` (golgi-ext) to `[RELAY_PUBLIC]` (golgi).
Zone serial: `2026060412`. Caddy redirect `www.nestgate.io → nestgate.io` added to Caddyfile.

### DONE: golgi SSH host key fixed

Removed stale host key for `git.primals.eco`, re-accepted new key.

### DONE: Caddyfile updated

- `nestgate.io` mesh reverse proxy block (→ sporeGate 10.13.37.2:8190)
- `www.nestgate.io` permanent redirect block
- `sporeprint.primals.eco` Zola block

### DONE: dnsmasq config created

`primal-eco.dnsmasq.conf` — all gate WireGuard IPs mapped to `*.primal.eco`.

---

## Remaining Actions

### Cloudflare (user action)

| ID | What | Where | Priority |
|----|------|-------|----------|
| ~~KD-05~~ | ~~Add footprint CNAME~~ | — | **NOT NEEDED** — wildcard `*.primals.eco` already resolves all subdomains to golgi. sporeGate owns routing via Caddy blocks. |
| ~~KD-06~~ | ~~Verify primals.eco DNSSEC chain~~ | — | **VERIFIED** — DS 2371/13/2 at .eco TLD matches Cloudflare KSK (ECDSA P-256). Chain intact. |

### Porkbun (user action)

| ID | What | Where | Priority |
|----|------|-------|----------|
| KD-04 | Decide primal.eco nameserver posture — keep on sovereign Knot DNS (current, zone now empty of A records) or park on Porkbun defaults | Porkbun → primal.eco | P3 (optional) |

### sporeGate (autonomous)

| Action | Detail |
|--------|--------|
| Deploy Caddyfile to golgi | `nestgate.io` + `www.nestgate.io` + `sporeprint.primals.eco` blocks ready. Deploy via `deploy_membrane.sh`. |
| Deploy dnsmasq config | `primal-eco.dnsmasq.conf` → `/etc/dnsmasq.d/primal-eco.conf` + `systemctl restart dnsmasq`. |
| Wire nestgate.io content backend | petalTongue DIV-1: connect content-provider socket for live CAS data. |
| Brand nestgate.io | petalTongue DIV-4: update title/header from "petalTongue Dashboard" to "nestgate.io". |
| Add footprint Caddy block | Wildcard DNS already resolves `footprint.primals.eco` to golgi. Just add Caddy block routing to ironGate via mesh. |

---

## Future DNS Actions

| Action | When | Where | Detail |
|--------|------|-------|--------|
| Add `git.nestgate.io` | Phase 5 (git migration) | Knot DNS master (golgi) | A record → golgi for Forgejo migration |
| Move Forgejo under nestgate.io | After git.nestgate.io is live | Caddy + Forgejo config | Update base URL |

---

## Tower Atomic Strategy

nestgate.io and primal.eco run on **fully sovereign infrastructure** — no Cloudflare,
no external CDN. Security posture relies on the primal stack:

| Layer | Primal | Role |
|-------|--------|------|
| DNS | Knot DNS (DNSSEC auto-signed) | Authoritative nameserver with ECDSA signing |
| TLS | Caddy (Let's Encrypt, CAA-locked) | Auto-cert with CAA restricting to LE only |
| Auth | rhizoCrypt (BTSP) | Mutual authentication for mesh services |
| Compute | toadStool + barraCuda | Rate limiting, WAF-like protections (future) |
| Render | petalTongue | Web serving from primal composition |
| Mesh | songBird (WireGuard) | Gate-to-gate federation, not exposed publicly |
| Storage | nestGate (CAS) | Content-addressed, provenance-tracked data |
