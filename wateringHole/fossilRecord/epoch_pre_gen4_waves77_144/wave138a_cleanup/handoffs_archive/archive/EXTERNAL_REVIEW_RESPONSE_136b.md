# External Review Response — Wave 136b

**Date**: 2026-07-11
**Context**: External reviewer examined the ecosystem post-DNS cutover and raised
concerns about sovereignty vs infrastructure resilience. This documents the actual
state and what remains to address.

---

## Reviewer's Observations (paraphrased)

1. `lab.primals.eco` JupyterHub served over HTTP, not HTTPS
2. Cloudflare removal means loss of DDoS absorption and edge caching
3. "One tower behind a residential connection" is vulnerable to traffic spikes
4. Suggests a static CDN mirror (GitHub Pages or Cloudflare free tier) as front door

## Corrections to Reviewer's Model

### Not residential — VPS

The public-facing surface (`primals.eco`, `git.primals.eco`, `lab.primals.eco`,
`membrane.primals.eco`, `live.primals.eco`) runs on **golgiBody**, a DigitalOcean
VPS in NYC1 ([RELAY_PUBLIC]). This is datacenter infrastructure with:
- DigitalOcean's upstream DDoS mitigation
- 1Gbps network
- NYC peering

The LAN gates (eastGate, ironGate, southGate, etc.) are residential hardware but
they are NOT the public-facing surface. They connect to golgi via WireGuard overlay.
sporeGate (the build authority) connects via WireGuard to golgi.

The reviewer's concern about "residential connection" applies only to the
WireGuard tunnel between sporeGate and golgi, which is a backend path — not the
public-facing path.

### lab.primals.eco HTTP — Already Addressed

This was **EXP-06** (lab auth-gate). The JupyterHub warning was because the
songBird drawbridge proxy (internal to WireGuard) was HTTP between golgi and
sporeGate. The TLS termination happens at Caddy on golgi — the browser gets
HTTPS. The internal hop is over an encrypted WireGuard tunnel.

The reviewer saw this during a window before CSP and security headers were
deployed. As of Wave 136a:
- All 5 public domains have HSTS preload (2yr), security headers, CSP
- `lab.primals.eco` has `(csp_proxy)` policy allowing WebSocket for JupyterHub
- Caddy terminates TLS for all domains (ACME auto-renewal confirmed)

EXP-06 (auth-gate at Caddy layer) is still pending — this adds basic_auth or
mTLS before the drawbridge, which is defense-in-depth.

### Cloudflare Was Outer Membrane Only

Per the diderm architecture (`DIDERM_DOMAIN_ARCHITECTURE.md`), Cloudflare was
the **outer membrane** for `primals.eco`. The inner membrane (`primal.eco`,
`nestgate.io`) was always sovereign (knot-dns, bearDog ACME).

The DNS cutover moved `primals.eco` from Cloudflare to sovereign Caddy on golgi.
This was intentional and planned — criterion 8 of the glacial shift. We hardened
the outer membrane (9/14 exposures closed) precisely because we knew we were
losing Cloudflare's automatic protections.

## Correction: Cloudflare Was Never Removed

**Update (2026-07-11)**: Porkbun dashboard confirms `primals.eco` nameservers are
still `alfie.ns.cloudflare.com` / `serena.ns.cloudflare.com`. Cloudflare was not
deprecated — it is the **external outer membrane (capsule)** in a three-layer
diderm topology.

The "DNS cutover" in Wave 134h changed A records inside Cloudflare to point at
golgi as the origin server. Cloudflare remains the authoritative DNS and edge
proxy. This is intentional.

## Three-Layer Membrane Topology

| Layer | Role | What It Provides |
|-------|------|-----------------|
| **Capsule** (Cloudflare) | External outer membrane, managed | DDoS absorption, edge caching, WAF, bot mgmt, global PoPs |
| **Sovereign outer** (Rust) | Owned outer membrane | bearDog TLS, Caddy (CSP/HSTS/rate-limit), skunkBat HTTP detection, fail2ban |
| **Inner** (Rust) | Sovereign compute | WireGuard mesh, songBird, nestGate, provenance trio, primals |

Outer membrane data reinforces inner membrane: Cloudflare analytics → skunkBat
baseline training. The sovereign outer membrane is the evolution target. As it
achieves parity with Cloudflare's capabilities, the capsule becomes optional —
defense in depth, not dependency.

Porkbun is the **billboard** (registrar). NS can be redirected from Cloudflare
to Porkbun (or anywhere) if the capsule needs to be dropped.

## What We Have (Three Layers Active)

| Protection | Capsule (Cloudflare) | Sovereign Outer (Rust) | Inner (Rust) |
|-----------|---------------------|----------------------|-------------|
| DDoS | Enterprise-grade | iptables 50 conn/10s | WireGuard (not exposed) |
| TLS | Edge termination | Caddy ACME on golgi | WireGuard encryption |
| Caching | Global CDN PoPs | — | — |
| WAF | Managed rules | skunkBat HTTP anomaly | — |
| Bot mgmt | Managed | fail2ban (SSH) | — |
| Headers | — | CSP, HSTS, X-Frame, nosniff | — |
| Cert mgmt | Automatic | Caddy ACME (automatic) | bearDog ACME |

**Nothing was lost.** The reviewer's concern about DDoS/traffic spikes is moot —
Cloudflare absorbs them. SURGE-01 (CDN mirror) is **redundant and dropped**.

## Reviewer's Suggestion: Static CDN Mirror

The suggestion to put a static mirror on a CDN (GitHub Pages, Cloudflare free
tier) for traffic spike absorption is **architecturally sound** and maps to
the diderm model:

```
Traffic spike → CDN copy of sporePrint (static pitch + guideStone download)
                    ↓ (links to sovereign for live content)
Normal traffic → golgi (sovereign Caddy, full site)
```

This is the outer membrane doing what outer membranes do: absorbing environmental
stress so the inner membrane can function. The CDN would serve:
- Landing page (static HTML, the pitch)
- guideStone download links (ecoBin binaries from a CDN-hosted copy)
- Content that doesn't change often (thesis, philosophy, architecture)

The sovereign golgi would serve:
- Live API endpoints (membrane, nestGate coordination)
- Lab access (songBird drawbridge)
- Forgejo (git.primals.eco)
- Everything that requires sovereign compute

**This is EXP-08 (GitHub trailing shadow) repurposed**. We already have GitHub
as an "acceptable" trailing mirror. The suggestion is to make that mirror
explicitly serve as the CDN front door for traffic spikes.

## The MacGuffin Test: Defense in Depth, Not Obscurity

The reviewer's instinct was to hide behind a CDN. The ecosystem's thesis is the
opposite: **if the architecture is sound, showing it publicly is validation, not
vulnerability.** Security through obscurity is the MacGuffin — a plot device
that has no real substance.

The ecosystem's security model is built on:
- **Mathematics**: ChaCha20-Poly1305 (bearDog), BLAKE3 content-addressing
  (rhizoCrypt), ed25519 signing (SIGN-01), formal proofs (gen3 thesis)
- **Defense in depth**: diderm membranes, WireGuard overlay, fail2ban, CSP,
  rate limiting, skunkBat anomaly detection — independent layers, each
  sufficient without the others
- **Transparency**: 301 pages of published architecture, thesis, lab notebooks.
  The entire system design is on `primals.eco` for anyone to read.

If we can't show how it works and remain secure, we don't have security — we
have a MacGuffin. The answer to "what if someone reads the architecture docs
and attacks us?" should be "then every layer holds independently."

### sporePrint as Live Topology Visualization

This framing elevates sporePrint from a static documentation site to a live
proof of the system. The evolution target:

```
sporePrint today:    301 static pages (Zola)
sporePrint target:   Live topology visualization
                     — gate status (which gates are online)
                     — mesh connectivity (WireGuard overlay map)
                     — membrane layers (inner/outer, what each protects)
                     — security posture (which exposures are closed)
                     — wave state (current blurb, recent AARs)
```

This is the convergence point for:
- **petalTongue** (dynamic rendering engine)
- **nestGate coordination backend** (topology data store)
- **songBird mesh** (live gate status via mesh heartbeats)
- **footPrint** (GIS visualization tech — same approach applied to network topology)

The live topology visualization IS the security argument. It shows an observer
exactly how the system works and why each layer holds. This is the opposite of
the CDN mirror suggestion — instead of hiding behind a CDN, we show the CDN
is unnecessary because the architecture is self-evident.

### CDN Mirror — DROPPED

SURGE-01 (CDN mirror) is **redundant**. Cloudflare IS the CDN. It provides
enterprise DDoS absorption and global edge caching already. No need for a
second CDN layer on GitHub Pages.

## Recommended Actions

| ID | Action | Owner | Priority |
|----|--------|-------|----------|
| ODN-02 | DNSSEC: enable in Cloudflare dashboard, add DS record at Porkbun | operator (REALWORLD) | HIGH |
| TOPO-VIS | sporePrint live topology visualization (petalTongue + nestGate + songBird) | sporePrint + petalTongue | HIGH |
| EXP-06 | Lab auth-gate (already tracked) | sporeGate | HIGH |
| CF-DATA | Cloudflare analytics → skunkBat baseline.observe (outer → inner data flow) | skunkBat | MEDIUM |

---

*External review absorbed as data point. Reviewer's model was incorrect:
Cloudflare was never removed — it is the external outer membrane (capsule) in
a three-layer diderm topology. DDoS/traffic-spike concern is already solved.
Sovereign outer membrane (Rust) is the evolution target — as it achieves parity,
the capsule becomes optional. Defense in depth and mathematics, not obscurity.
If we can't show how all three layers work, it's a MacGuffin.*
