# K-Derm Topology Reaffirmation — Wave 136b

**Date**: 2026-07-11
**From**: eastGate overwatch
**To**: cellMembrane team, sporeGate topology team, skunkBat team
**Context**: External review + Porkbun dashboard inspection confirmed the K-Derm
diderm architecture is operating as designed. This handoff ensures all teams are
fully tracking the three-layer model and their responsibilities within it.

---

## What Happened

An external reviewer examined the ecosystem post-DNS cutover and assumed
Cloudflare had been removed ("deprecated in favor of tower atomic"). Porkbun
dashboard confirms this is incorrect: `primals.eco` NS remains on Cloudflare
(`alfie.ns.cloudflare.com` / `serena.ns.cloudflare.com`).

The DNS cutover (Wave 134h) changed **A records inside Cloudflare** to point
at golgi as the origin server. Cloudflare remains the outer membrane proxy.
This is the correct K-Derm diderm topology as documented in:

- `DIDERM_DOMAIN_ARCHITECTURE.md` — canonical domain trust model
- `K_DERM_TOPOLOGY_STANDARD.md` — canonical K-Derm layer definitions
- `KDERM_DIDERM_ARCHITECTURE.md` (sporePrint) — published architecture page

---

## K-Derm Layer Mapping (primals.eco Path)

```
Extracellular (public internet)
  │ weak bond (public read-only)
  ▼
Outer membrane — trans face (Cloudflare + Caddy on golgi)
  │  Cloudflare: DDoS absorption, edge caching, WAF, bot mgmt
  │  Caddy: TLS termination, CSP, HSTS, rate limiting, fail2ban
  │  skunkBat: HTTP anomaly detection (sovereign, not inline yet)
  │  ionic/weak bonds
  ▼
Periplasm (sporeGate CI + golgi relay)
  │  Build authority, WireGuard hub, Forgejo, depot
  │  metallic/ionic bonds
  ▼
Plasma membrane (gate firewall — Flint/UFW)
  │  covalent/metallic bonds
  ▼
Cytoplasm (NUCLEUS on LAN gates)
    bearDog, songBird, skunkBat, nestGate, cellMembrane...
    covalent bonds only
```

### Key Principle: Outer Data Reinforces Inner

Per `DIDERM_DOMAIN_ARCHITECTURE.md` §Cross-Membrane Validation, the inner
membrane validates the outer membrane's integrity:

| Check | Method | What It Catches |
|-------|--------|-----------------|
| Content integrity | BLAKE3 hash comparison (inner vs outer) | CDN injection, content modification |
| Timing baseline | Inner response time is floor | Interception, throttling |
| Availability cross-check | Inner healthy + outer down = CF outage, not real downtime | External service failure |
| TLS cert verification | Compare inner LE cert fingerprint with outer | Certificate substitution |
| DNS consistency | Sovereign NS vs public resolver | Poisoning, hijacking |

**The dual membrane is the target architecture**, not a transitional state.
Cloudflare on the outer membrane + sovereign inner membrane = both DDoS
protection AND integrity verification.

---

## Team Responsibilities

### cellMembrane Team

You own the K-Derm typed interface (`cellmembrane-types/src/envelope.rs`).
Current: 27 tests covering `EnvelopeTopology`, `EnvelopeLayer`, `BondType`,
`ChannelProtein`, `BraidPolicy`, `BoundaryPolicy`.

**Action items**:
1. Confirm `envelope.rs` types accommodate the Cloudflare outer membrane
   position. The current `EnvelopeLayer::Outer` should represent the combined
   Cloudflare + Caddy surface, not just Caddy.
2. Consider whether `membrane caddy.configure` should manage Cloudflare-side
   settings via CF API (API token), or if Cloudflare remains a manual layer.
   The Porkbun DNSSEC flow (ODN-02) suggests some registrar/CF operations
   will always be REALWORLD.
3. Validate that `BondType::Weak` correctly models Cloudflare → Caddy origin
   pull. Cloudflare authenticates to origin via authenticated origin pulls
   or IP allowlisting — this is ionic, not weak.

### sporeGate Topology Team

You operate the physical K-Derm topology on golgi and sporeGate.

**Action items**:
1. Confirm Cloudflare proxy mode is correctly configured for `primals.eco`:
   - Orange cloud (proxied) ON for A records
   - SSL mode: Full (strict) — Caddy has valid LE cert
   - Security headers: confirm Cloudflare isn't overriding Caddy's CSP/HSTS
2. Enable DNSSEC in Cloudflare dashboard for `primals.eco`. Add the DS record
   at Porkbun under "Registry DNSSEC". This is ODN-02.
3. Verify the Sovereign CI chain still flows correctly:
   `gate push → Forgejo (covalent) → sporeGate build (metallic) → golgi deploy (ionic) → Cloudflare edge cache purge (weak)`
   Does Cloudflare edge cache need manual purge on deploy? Or does it respect
   cache-control headers from Caddy?

### skunkBat Team

You own the sovereign outer membrane detection layer.

**Action items**:
1. **CF-DATA**: Explore Cloudflare Analytics API as a data source for
   `baseline.observe`. Cloudflare sees ALL traffic before it reaches Caddy —
   this is the richest data source for outer membrane awareness.
   - Firewall events, bot scores, threat scores
   - Geographic distribution, ASN data
   - Request rates, error rates, bandwidth
2. **SKUNY-INGEST**: Continue Caddy JSON log → `baseline.observe` pipeline.
   This captures what Cloudflare passes through (post-filter), while CF-DATA
   captures what Cloudflare absorbed (pre-filter). Both views together give
   complete outer membrane awareness.
3. Long-term: skunkBat becomes the sovereign validator that can independently
   confirm whether Cloudflare is behaving correctly (cross-membrane validation
   checks from the diderm architecture doc).

---

## DNSSEC Path (ODN-02) — For sporeGate/Operator

1. Log into Cloudflare dashboard → `primals.eco` zone → DNS → Settings
2. Enable DNSSEC → Cloudflare generates signing keys + DS record
3. Copy DS record values (Key Tag, Algorithm, Digest Type, Digest)
4. Log into Porkbun → `primals.eco` Details → Registry DNSSEC → Add DS record
5. Wait 10-30 min for propagation
6. Verify: `dig +dnssec primals.eco` → expect `ad` flag + RRSIG records

Also check: `primal.eco` and `nestgate.io` use sovereign nameservers
(`ns1.primals.eco` / `ns2.primals.eco`). DNSSEC for these requires signing
the zone in knot-dns — separate task, not Cloudflare.

---

## References

| Document | Location | What |
|----------|----------|------|
| K-Derm Topology Standard | `wateringHole/K_DERM_TOPOLOGY_STANDARD.md` | Canonical layer definitions |
| Diderm Domain Architecture | `wateringHole/DIDERM_DOMAIN_ARCHITECTURE.md` | Domain trust model + cross-membrane validation |
| K-Derm Diderm Architecture | `sporePrint/content/architecture/KDERM_DIDERM_ARCHITECTURE.md` | Published architecture page |
| Bonding Model Standard | `wateringHole/BONDING_MODEL_STANDARD.md` | Bond types per boundary |
| gen5 K-Derm Envelope | `whitePaper/gen5/foundations/KDERM_DIDERM_ENVELOPE.md` | Formal foundation |
| External Review Response | `handoffs/EXTERNAL_REVIEW_RESPONSE_136b.md` | Full analysis of reviewer's feedback |

---

*K-Derm diderm is operating as designed. Cloudflare = outer membrane (trans face).
Sovereign Rust = evolution target for outer membrane parity. Inner membrane = the
organism. The dual membrane is the target architecture, not transitional. Teams:
confirm your layer, validate your bonds, report gaps.*
