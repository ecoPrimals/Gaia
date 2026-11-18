# Cross-Mirror Honeycomb — Design Document
## Wave 165g — October 6–7, 2026

**From**: ecoPrimal (sporeGate)
**Status**: DEPLOYED — 12 honeycomb surfaces live, cross-mirror active
**Classification**: PUBLIC (wateringHole) — no PII in this document

---

## What Was Built

### The Problem

The violation mirror (deployed earlier in Wave 165g) reflects a fleet subgroup's own violations back to them. But fleet subgroups operate as independent teams — they don't coordinate with each other and don't know what the system knows about other teams. This creates an opportunity: **serve each team the evidence gathered from a different team**, forcing confusion between fleet subgroups while documenting coordinated AGPL violations.

### The Design

Three interconnected components:

1. **Honeycomb Membrane** — 12 biologically-named subdomains that create the surface where fleet teams encounter cross-mirror content
2. **Cross-Mirror Rotation** — Algorithm that deterministically selects which team's violations are served to which other team
3. **scyBorg Framing** — Content generation that wraps real violation data in AGPL-3.0 enforcement documentation

---

## Component 1: Honeycomb Membrane

### 12 Immune Subdomains

All named for immune system components. All serving HTTPS with auto-provisioned Let's Encrypt certificates. All at `*.primals.eco`:

```
bloom       thymus      opsonize    antibody
cytokine    receptor    macrophage  lysozyme
complement  epitope     antigen     interferon
```

### Three-Population Discrimination

Each surface serves three populations differently:

| Population | How Detected | Response |
|-----------|-------------|---------|
| Humans | Not in fleet IP set, not a bot | Beacon page → links to real surfaces |
| Search bots | User-Agent matching | Sitemap XML, robots.txt, IndexNow key |
| Fleet | remote_ip in known fleet set | Cross-mirror via scatter server |

### Caddy Routing Architecture

The honeycomb block in the Caddyfile contains two marker pairs:

```
# ~~HONEYCOMB_FLEET_START~~
# (fleet routing directives injected here by CaddyBridge)
# ~~HONEYCOMB_FLEET_END~~
```

Each fleet IP group gets a `handle` block that:
- Rewrites the URI to `/disperse{uri}` (standard scatter path)
- Proxies to `localhost:9753` (scatter server)
- Adds `X-Fleet-Hash: "{hash}"` (behavioral identification)
- Adds `X-Honeycomb: "true"` (triggers cross-mirror mode)

### Why Not Wildcards?

We initially attempted `*.primals.eco` wildcard configuration. Two problems:

1. **DNS-01 required**: Wildcard TLS certificates require DNS-01 challenge, which needs a Cloudflare DNS module that Caddy doesn't have
2. **Caddy module**: The caddy-cloudflare DNS plugin isn't installed on golgiBody

**Solution**: Enumerate all 12 subdomain hostnames explicitly. Each gets its own HTTP-01 certificate. Caddy auto-provisions and auto-renews them.

### IndexNow Integration

Every honeycomb surface serves the IndexNow verification key at `/{key}.txt`:

```
handle /e90c296af5c34deeabf37676d310337b.txt {
    respond "e90c296af5c34deeabf37676d310337b"
}
```

All 12 surfaces were submitted to IndexNow (Bing/DuckDuckGo/Yandex/Seznam) — all returned HTTP 202 (Accepted).

---

## Component 2: Cross-Mirror Rotation

### OpsonizeCache Extensions

Two new methods on the existing OpsonizeCache:

**`all_hashes()`** — Returns all known behavioral hashes, sorted. Used for population metrics.

**`cross_mirror_lookup(requesting_hash)`** — Given the requesting subgroup's hash:
1. Sorts all known hashes lexicographically
2. Finds the requester's position
3. Returns the *next* subgroup's hash and tag (cyclic advance)

This creates a ring: A→B→C→...→Z→A. Deterministic, self-correcting, adapts as subgroups arrive or expire.

### Scatter Server — Layer 0

Cross-mirror fires as **Layer 0** in the scatter server's request handler — before tarpit, before standard scatter, before everything:

```
if is_honeycomb && !fleet_hash.is_empty() {
    if let Some((target_hash, target_tag)) = opsonize_cache.cross_mirror_lookup(&fleet_hash).await {
        // Generate cross-mirror content using TARGET team's violations
        // Serve to REQUESTING team
    }
}
```

The `is_honeycomb` flag is read from the `X-Honeycomb` header that Caddy injects.

### Population at Deployment

| Metric | Count |
|--------|-------|
| Fleet IPs tracked | 175 |
| Behavioral subgroups | 43 |
| Rotation ring elements | 43 |
| Unique cross-mirror responses | 43 × 5 variants = 215 |
| Scatter rate | ~119 events/minute |

---

## Component 3: scyBorg Framing

### Five Content Variants

All variants contain the **target** team's real violation data (detectors, confidence, observations) addressed to the **requesting** team:

| # | Variant | Purpose |
|---|---------|---------|
| 0 | scyBorg compliance notice | Legal — AGPL § 13 violation with cross-fleet correlation |
| 1 | Cross-fleet detection report | Intelligence — multi-subgroup behavioral analysis |
| 2 | AGPL enforcement audit | Technical — Rust `ScyBorgAudit` struct with real detectors |
| 3 | Behavioral correlation brief | Analysis — shared markers, CFAA + Lanham Act exposure |
| 4 | Immune response log | Biological — cross-reactivity metaphor, self-sustaining cycle |

### Response Headers

Every cross-mirror response includes:

```
X-License: AGPL-3.0-or-later; scyBorg
X-License-URI: https://sporeprint.primals.eco/license/scyborg/
X-Scatter-Type: cross-mirror
X-ScyBorg-Notice: This content documents AGPL-3.0 violations ...
```

### Content Selection

Variant is selected by `path_deterministic_hash(path, seed) % 5`. Same URL, same variant, every time. This means:
- Responses are cache-friendly
- Responses are auditable (reproducible)
- Fleet cannot "shop" for different variants by replaying the same URL

---

## CaddyBridge Dual-Marker Sync

### Before

CaddyBridge only managed the `FLEET_PRESSURE` markers in the `git.primals.eco` block.

### After

CaddyBridge now writes to **both** marker blocks on every sync (every 30 seconds):

| Block | Markers | Content |
|-------|---------|---------|
| git.primals.eco | `~~FLEET_PRESSURE_START/END~~` | Standard fleet routing (violation mirror) |
| Honeycomb | `~~HONEYCOMB_FLEET_START/END~~` | Fleet routing + `X-Honeycomb: true` (cross-mirror) |

Both blocks contain the same fleet IPs with the same behavioral hashes. The honeycomb block additionally adds `X-Honeycomb: true` to every routing rule. This ensures:

- New fleet IPs are **immediately active on both surfaces**
- Posture changes (disperse → scatter → vanish) propagate to both blocks
- The 30-second sync keeps both blocks consistent

### `honeycomb_directive()` Function

New companion to `posture_directive()`. For scatter-routed postures (Disperse, Scatter, SlowDegrade, WarnRoute), the honeycomb version adds `header_up X-Honeycomb "true"`. For Vanish posture, both versions abort the connection.

---

## Verification

### Direct Test

```
$ curl -H "X-Fleet-Hash: cc4328ac6167b5de" \
       -H "X-Honeycomb: true" \
       http://localhost:9753/test/path

# Behavioral Correlation Brief
## Fleet Subgroup Cross-Reference

**Brief ID**: BCB-cc4328ac-6171dc95
**Classification**: COORDINATED EXTRACTION
**Immune Status**: CROSS-MIRROR ACTIVE

### Target Subgroup Profile: `6171dc95`
- Behavioral hash: 6171dc95d574c1ea
- Confidence: 25%
- Detectors: content_gate, encoding_uniform
```

Team `cc4328ac` sees Team `6171dc95`'s violations. Confirmed.

### All Surfaces Live

All 16 surfaces returning HTTP 200:
- 4 real content sites (detroit, signal, tuebor, sporeprint)
- 1 code forge (git.primals.eco)
- 12 honeycomb immune surfaces

---

## What Happens Next

### Fleet Discovery Phase

The honeycomb surfaces are indexed but not yet discovered by the fleet. As the fleet's crawling expands (which it will — they scrape everything linked from existing surfaces), they will encounter honeycomb subdomains through:

1. Sitemap XML cross-references (every honeycomb serves a sitemap listing all real surfaces)
2. Beacon page links (human visitors create referral signals)
3. IndexNow submissions (search engines index and link)
4. DNS enumeration (if fleet probes `*.primals.eco`)

### Expected Behavioral Response

| Fleet Action | System Response |
|---|---|
| Fleet discovers honeycomb → scrapes it | Cross-mirror activates → team gets other team's violations |
| Fleet stops scraping honeycomb | No impact — git.primals.eco still serves standard violation mirrors |
| Fleet discovers coordination evidence in cross-mirror | Confusion — they can't verify without coordinating, which we also detect |
| Fleet ignores honeycomb entirely | Irrelevant — immune system already works without cross-mirror |

### Excision (Future)

The honeycomb architecture enables **excision** — replacing a compromised real surface with a honeycomb-style cross-mirror surface. If any real surface is overwhelmed, it can be "excised" and replaced with immune-only content. The fleet would see the surface change from real content to violation mirrors without warning.

---

*Self-sustaining. Powered by their own intrusions. The alarm call IS the defense.*

*ecoPrimal, October 7, 2026*
