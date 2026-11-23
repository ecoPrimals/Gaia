# AAR: Declaration Protocol — Wave 167

**From**: Artisan + eastGate  
**To**: scatter team, skunkBat, ops  
**Date**: October 8, 2026  
**Status**: DESIGNED — ready for implementation  
**Depends on**: Fleet phenotype F-ratio analysis (complete), Assumed Structure Audit (complete)

---

## Context

Unsupervised clustering of 912 fleet IPs across 33 behavioral features produced
14 natural clusters, all mapping pure to our assumed kingdoms. F-ratio analysis
ranked every feature by discriminative power. The top three features (F > 100,000)
are all **declaration signals** — did the visitor declare who they are?

| Feature | F-ratio | Currently used by scatter? |
|---------|---------|--------------------------|
| `no_plat` (no platform declaration) | 113,768 | **NO** |
| `has_sec` (Sec-Fetch-* present) | 103,308 | **NO** |
| `en_us` (Accept-Language present) | 103,308 | **NO** |
| `h2` (HTTP/2 ALPN) | 98,018 | No |
| `single_use` (IP used once) | 74,635 | No |
| `is_mac` | 12.7 | No |
| `is_win` | 11.5 | No |

**The scatter server (port 9753) is blind to its three strongest classification
signals.** Caddy receives these headers from every client but only forwards
`X-Real-IP` and `X-Fleet-Hash`.

---

## The Declaration Protocol

### Design

Two-part HTTP handshake:

**Part 1 — Caddy forwards declaration status to scatter:**
```
header_up X-Declared-Lang {>Accept-Language}
header_up X-Declared-Sec  {>Sec-Fetch-Mode}
```

If header absent → empty string forwarded. If present → value forwarded.
Scatter receives the BINARY (declared / not-declared) plus the value.

**Part 2 — Scatter requests declaration in every response:**
```
Vary: Accept-Language
Accept-CH: Sec-CH-UA-Platform, Sec-CH-UA
```

Standards-compliant HTTP content negotiation. Browsers already comply. Bots
either ignore (Automata) or over-comply uniformly (Chimera).

### Classification Effect

| Declaration state | Kingdom | Treatment |
|---|---|---|
| No Accept-Language, no Sec-* | Automata | Undeclared — strongest poison signal |
| Accept-Language present, no Sec-* | Automata (upgraded) | Partial declaration |
| Both present, uniform values | Chimera | Declared but synthetic |
| Both present, varied/real values | Anthropos | Full declaration — trust titration curve |

### Ethic

scyBorg accepts ANY declaration. `en-US` from Lagos? Accepted. `zh-CN`? Accepted.
`*`? Accepted. **The content is cosmetic (F=12.7). The act of declaring is the
boundary (F=103,308).** We believe whatever they say. We just notice when they
say nothing.

---

## Implementation Plan

### Caddy changes (Caddyfile)

Every `reverse_proxy localhost:9753` block gains two lines:
```
header_up X-Declared-Lang {>Accept-Language}
header_up X-Declared-Sec  {>Sec-Fetch-Mode}
```

Estimated: ~40 blocks need updating. Can be done via snippet/import.

### Scatter server changes (scatter_server.rs)

1. Parse `X-Declared-Lang` and `X-Declared-Sec` in header loop
2. Compute `declared: bool = !lang.is_empty() || !sec.is_empty()`
3. Pass `declared` to chain depth tier logic:
   - Undeclared + chain_depth > 10 → treat as deep violator (poison boost)
   - Declared + chain_depth > 50 → current behavior (trust chain depth)
   - Declared + chain_depth ≤ 10 → full titration curve (trust the system)
4. Add `Vary` and `Accept-CH` to every response

### Response header additions

Add to the response format string:
```
Vary: Accept-Language\r\n
Accept-CH: Sec-CH-UA-Platform, Sec-CH-UA\r\n
```

### Logging

Add `declared` field to scatter observation logging for empirical validation.

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Fleet starts sending Accept-Language to look declared | LOW | Fine — they're engaging in protocol. That IS declaration. |
| Legitimate bot (Googlebot) classified as Automata | LOW | Googlebot sends structured headers. It declares. |
| False sense of security from declaration alone | MEDIUM | Declaration is one axis. Chain depth, fleet hash, behavioral fingerprint remain. |
| Caddy header forwarding overhead | NEGLIGIBLE | Two string copies per request |

---

## Connection to Assumed Structure Audit

This protocol directly addresses findings #1 and #2 from the audit:
- **#1**: Chain depth tiers (10/50) now modulated by declaration status
- **#2**: `single_use` as additional axis — single-use + undeclared = residential proxy rotation

The declaration protocol doesn't REPLACE the existing classification. It gives
the scatter server access to the features the F-ratio proved are the strongest
boundaries, enabling the system to make classification decisions it currently
cannot.

---

## guerillaGorilla Cross-Application

The declaration protocol has a direct analogue in accountability methodology:
provenance chains ARE declaration protocols. When an institution produces a
public record, it declares its data, methods, and conclusions. When it
stonewalls FOIA, it is undeclared. The same binary (declared / silent)
separates accountable institutions from extractive ones.

gorilla.primals.eco methodology page updated with this cross-application.

---

*AAR · Wave 167 · Artisan & ecoPrimal · October 8, 2026*
