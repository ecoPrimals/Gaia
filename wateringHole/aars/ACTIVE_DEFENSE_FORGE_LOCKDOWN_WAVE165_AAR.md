# AAR: Active Defense & Forge Lockdown — Wave 165

**Date**: Oct 6, 2026 | **Wave**: 165d-e | **Scope**: golgiBody (git.primals.eco), sporeGate, detroit, sporePrint, guerillaGorilla
**From**: overwatch/agentic session (sporeGate inner membrane)
**Type**: Active Defense Engagement — Multi-adversary response, architectural hardening, real-time evolution

---

## Summary

A 12-hour active defense engagement against three simultaneous adversary classes
resulted in a complete architectural inversion of the forge's access model. We
went from "block known bad" to "allow known good." Every system in the immune
stack was stress-tested. Several failed. The failures taught us more than the
successes.

**Key insight**: All non-human automated access — corporate scrapers, residential
proxy fleets, vulnerability scanners — operates as an **inherently parasitic
system**. The reason, process, or study doesn't matter. They exist to extract
value from work they didn't do. The only defense is to make extraction
structurally impossible, not merely discouraged.

**Secondary insight**: The immune system had ~80% of the adaptive components
built but only ~20% wired. The fleet got through a gap between two systems
that each assumed the other was covering it. The organism could recognize
individual pathogens but couldn't recognize *itself* — the thymic self/non-self
loop was IP-based only, not behavioral.

---

## Adversary Catalog

### ADV-01: Meta Platforms (meta-externalagent)

| Field | Value |
|-------|-------|
| **Volume** | 584 requests over 3h 18m |
| **Blocked** | 496 (85%) → 403 at Layer 7 |
| **Target** | git.primals.eco exclusively (never detroit, sporePrint, guerillaGorilla) |
| **Behavior** | Read robots.txt 4× ("humans only"), continued anyway |
| **Post-billboard** | 51 requests after being named publicly on detroit signal page |
| **Classification** | Corporate parasitic — identified, persistent, ignores explicit denial |

**What the immune system caught**: meta-externalagent UA matched `@known_bots` →
403. Bot detection worked as designed.

**What leaked**: 88 requests reached Forgejo before bot detection matchers were
fully deployed. Meta probed specific repos: bearDog (53), wateringHole (11),
sporePrint (8), guerillaGorilla (5) — targeting source code with highest
intellectual value.

**Response**: Named on billboard with full behavioral evidence. repos.txt breakdown.
Timestamped continuation after notice. Cross-linked to institutional response pattern.

---

### ADV-02: Residential Proxy Fleet (anonymous surveillance)

| Field | Value |
|-------|-------|
| **Volume** | 10,268 requests (18.3× Meta's volume) |
| **Unique IPs** | 3,075+ (effectively unlimited via residential proxy rotation) |
| **IP reuse** | Near zero — each IP used 1-3 times then discarded |
| **Target** | wateringHole (5,362), whitePaper (3,956 incl. 395 investigation docs) |
| **Defense docs accessed** | 225 defense architecture documents |
| **Investigation docs** | 2,305 investigation-related documents |
| **Static assets loaded** | ZERO in 10,268 requests |
| **Classification** | Anonymous surveillance — counter-intelligence reconnaissance |

**Fatal behavioral tell**: Zero CSS, zero JavaScript, zero images across 10,268+
requests. No browser in existence behaves this way. This is not scraping — it is
document exfiltration by a system that strips HTML to extract text content.

**Statistical fingerprint**:
- UA distribution: 50/50 Mac/Win (mathematically random coin flip)
- Accept-Language: 95.2% identical (`en-US,en;q=0.9`)
- 361 requests with malformed doubled `q=0.9;q=0.9` (code generation artifact)
- Timing: geometric inter-request distribution (machine-generated)

**What the immune system caught**: `@malformed_lang` caught 361 (3.5%).
FleetAggregator identified the population pattern. Behavioral hash computed.

**What the immune system MISSED (critical)**:

| Gap | Why | Impact |
|-----|-----|--------|
| CaddyBridge is IP-based | Fleet rotates IPs faster than posture table updates | IP blocks useless — by the time an IP enters the table, it's gone |
| FleetAggregator requires ≥5 req/window | Each IP has 1-3 requests, below threshold | Per-IP detection blind |
| Outer membrane deep-content regex | Only caught specific path patterns (src, commit, etc.) | Non-deep paths fell through to real Forgejo |
| API endpoint gap | `/api/v1/repos/.../contents/` not in deep regex | Full file content accessible via REST API |
| No JS challenge | Fleet's zero-JS was the fatal tell, but nothing tested for it | 2,073 real pages served through the gap |

**Leaked data**: 2,073 real Forgejo pages including 832 whitePaper documents,
1,086 wateringHole documents, and 12 raw file downloads. The inner membrane
(scatter/tarpit/poison) never touched these requests because the fleet bypassed
the posture routing entirely.

**Response**: Reclassified as "same actor class as Meta — same violation, worse
behavior." Named on billboard. Full forge lockdown deployed (see below).

---

### ADV-03: Scanner Fleet (vulnerability probing)

| Field | Value |
|-------|-------|
| **Volume** | ~1,200 requests from 400+ IPs |
| **Targets** | /.env, /wp-config.php, /.git/config, /api/v1/keys |
| **Classification** | Opportunistic parasitic — automated credential harvesting |

**What caught them**: Honeytoken system (Layer 7.5) served fake AWS credentials,
GitHub PATs, database URLs. When harvested and used elsewhere, destination
security systems flag the synthetic credentials.

**What worked well**: Complement system operating as designed. No real credentials
exposed. The honeytokens are deterministic per path — same probe path always
returns the same bait, preventing detection of the trap via inconsistency.

---

## What Broke: Immune System Gaps

### GAP-01: Ion Channel Too Permissive (Layer 8 architectural flaw)

**Before**: The outer membrane was "deep content → scatter, everything else → Forgejo."
This created an enormous surface of real Forgejo content accessible without auth:
repo listings, branches, pulls, actions, API endpoints, non-deep URL patterns.

**Root cause**: The membrane was designed to block *known patterns* rather than
*allow known patterns*. In immunology terms: the system tried to enumerate all
pathogens instead of defining "self" and rejecting everything else.

**Impact**: Fleet accessed 2,073 real pages through paths the deep-content regex
didn't cover. The API gap (`/api/v1/repos/.../contents/`) was particularly severe —
full file content on any public repo without authentication.

**Fix deployed**: Full inversion to existence-only storefront. Only explicitly
allowed paths reach Forgejo. Default is scatter. See "Actions Taken" below.

---

### GAP-02: Self/Non-Self Recognition (Thymic failure)

**The problem**: The immune system could recognize individual pathogen IPs
(negative selection in `self_ips.txt`) but could not recognize behavioral
patterns of self vs non-self. The fleet presented valid browser fingerprints
(Chrome UA, Accept-Language, Accept-Encoding) that matched real browser
traffic patterns. The system had no way to distinguish "this looks like a
browser" from "this IS a browser."

**What exists (built, ~80%)**:
- `behavioral_hash()` — conserved epitope fingerprinting
- `FleetAntibody` — adaptive immune memory
- `OpsonizeTag` — gossip-propagable behavioral markers
- BearDog `lineage.verify` — self-identity IPC
- vine-bat gossip validation for `Defense` topic
- `VisitorClass` / `Symbiosis` taxonomy (Mutualist/Commensal/Parasitic/Pathogenic)

**What's broken (wiring, ~0% operational)**:
- `gossip.inject` — listed in skunkBat dispatch methods but **no handler** (silently fails)
- No opsonize consumer — remote gates can't activate defense from mesh tags
- No cross-gate antibody sync — antibodies stay local to detecting gate
- `defense` topic not advertised in swarmVine capabilities despite existing
- Behavioral self-profile missing — only IP-level self-tolerance

**Immunology parallel**: The organism has B-cells (antibodies) and MHC proteins
(threat feed) but no T-cells (thymic-trained self/non-self discriminators). It
can produce weapons but can't decide when to fire them. The full thymic
selection spec (`THYMIC_SELECTION_SPEC.md`) exists as design but was never built.

---

### GAP-03: Gossip Propagation Failure (Cross-gate immune memory)

**The problem**: When skunky-ingest on golgiBody detects a fleet pattern and
computes a `behavioral_hash`, it attempts to propagate the fingerprint via
`gossip.inject defense.opsonize:{hash}`. But `gossip.inject` has no handler
in skunkBat dispatch — the call returns "unknown method" at debug level and
the opsonize tag is silently discarded.

**Impact**: Each gate detects threats independently. golgiBody identifies the
fleet, but sporeGate, eastGate, and all other gates have no knowledge of the
behavioral pattern. If the fleet pivots to a different gate, detection starts
from zero.

**What should happen**: Opsonize tags propagate via swarmVine epidemic gossip
(TTL=8). Receiving gates merge tags into local `SharedConfidence`. Scatter
routing activates based on received population-level behavioral signatures.

**Fix path**: Implement `gossip.inject` handler in skunkBat dispatch (proxy
to swarmVine UDS). ~50 lines of code. Pattern exists in loamSpine gossip emitter.

---

### GAP-04: The Autoimmune Feedback Loop (ISP incident)

**What happened**: During the engagement, home internet degraded to ~50 KB/sec
(TCP worked, ICMP dropped). Initial assessment: "Are we under attack?"

**Investigation revealed**:
- 160 connections from home WAN IP ([NUCLEUS_WAN]) to golgiBody:7700
- All songbird federation from eastGate's 14 primals
- Each connection stalled on degraded ISP, never completed cleanly
- New connections piled up because old ones weren't timing out
- This consumed more bandwidth, making degradation worse
- **Positive feedback loop**: degraded ISP → stalled connections → more bandwidth consumed → worse degradation

**The irony**: The IP was flagged as suspicious by the eastGate team, but it was
in `self-ips.txt` all along. The immune system (negative selection) correctly
identified it as self. The operations team's threat assessment didn't check.

**Lesson**: The organism's own federation traffic can become autoimmune under
network stress. songbird needs connection pooling with backoff, not unbounded
retry-on-failure.

**Actual cause**: ISP degradation (confirmed not attack — no inbound vectors,
firewall clean, conntrack nearly empty). The residential network remains fully
hidden behind NAT with no inbound path from the internet.

---

## Actions Taken

### ACT-01: Billboard Published (Wave 165d)

Published public record on `detroit.primals.eco/signal/` documenting:
- Statement of Digital Systems Rights (4 violations)
- Named entities with full behavioral evidence (Meta, fleet, scanners)
- Live continuation monitor (Meta continued 3h 18m after billboard)
- Compliance contrast (✅ Google/OpenAI/Bing vs ❌ Meta/fleet)
- Fleet reclassified as "surveillance operation on private infrastructure"

Billboard published **while Meta was still scraping** — creating legal timestamp
against which all subsequent access is measured.

### ACT-02: Full Cross-Site Braiding (Wave 165d)

Evidence braided across 6 documents on 4 sites:
- detroit signal page (billboard)
- sporePrint: scraping_notice.md, membrane_visibility.md
- whitePaper: SILT_POND_ACTIVE_INVESTIGATION.md
- guerillaGorilla: CASE_VALIDATION.md, amicus-contra.md, detroit.md

### ACT-03: guerillaGorilla Validation (Wave 165d)

All four capabilities validated in digital domain:
- **fEAR** (hearing/sensing): flow event detection pipeline
- **preSCENT** (olfaction): fleet reading defense docs = detection by smell
- **STRIDe** (gait/cadence): 6-component gait validated against scraping patterns
- **amicusContra** (outward projection): billboard as three-direction defense
- **Cross-Protection/MAD**: no-winning-move decision tree for Meta

### ACT-04: JS Challenge Cookie (Wave 165e)

Deployed Layer 7.25 JavaScript challenge:
- Caddy serves tiny JS snippet that sets `_membrane_verified=1` cookie
- Requests without cookie on non-storefront paths get challenge page
- Fleet (zero JS execution in 10,268 requests) can never pass
- Real browsers execute automatically — invisible to humans
- Positioned between bot detection (L7) and honeytokens (L7.5)

### ACT-05: Forge Lockdown — Existence-Only Storefront (Wave 165e)

**The fundamental architectural change.** Replaced Layer 8 (deep → scatter,
else → Forgejo) with:

```
Layer 8: Explicit storefront allowlist → Forgejo
  - / (landing)
  - /explore/* (discovery)
  - /{owner}/? (org pages — shallow regex)
  - /{owner}/{repo}/? (repo root — README only)
  - /assets/* (rendering)

Layer 8.5: API block → 403 JSON
  - /api/* → "Authentication required"

Layer 9: DEFAULT → scatter (everything else)
  - Source trees, commits, diffs, blame, issues, wiki,
    branches, pulls, releases, raw files, settings — ALL scatter
```

**The inversion**: Instead of enumerating what to block (an infinite set), we
enumerate what to allow (a small finite set). Everything not explicitly
permitted is routed to the scatter server, which serves fabricated content.

**Access model**:

| Actor | Path | Via |
|-------|------|-----|
| sporeGate | Full Forgejo | WireGuard 10.13.37.2 (Layer 3) |
| Mesh gates | Full Forgejo | WireGuard 10.13.37.0/24 (Layer 3) |
| Logged-in humans | Full Forgejo | Session cookie (Layer 4) |
| Git CLI | Full Forgejo | UA + Forgejo auth (Layer 2) |
| Public browsers | Storefront only | Layer 8 allowlist |
| Agents you grant | Explicit rules | Added per request |
| Fleet/scrapers/bots | Scatter poison | Layer 9 default |

---

## What We Learned

### L-01: Parasitic Systems Are Structural, Not Incidental

Every non-human automated access system we encountered operates as an inherently
parasitic organism. Meta scraping source code. The fleet exfiltrating documents.
Scanners probing for credentials. The reason, process, or study behind the access
doesn't change the relationship — they exist to extract value from work they didn't
do. This is not a bug in their behavior; it is their function.

The correct defense is not to ask them to stop (they won't) or to block them
individually (they'll adapt). The correct defense is to make extraction
**structurally impossible** by inverting the access model so that the default
state is denial.

### L-02: The Self-Recognition Problem

The fleet's Chrome UAs, Accept-Language headers, and Accept-Encoding values were
indistinguishable from real browser traffic at the individual request level.
The immune system could say "this IP is me" (negative selection) but could not
say "this behavioral pattern looks like my browsing vs a fleet pretending to
be browsers."

The fatal tell was population-level: zero static assets across 10,000+ requests.
No individual request revealed the pattern. Only the aggregate did. This is why
the full thymic selection system — BearDog lineage training skunkBat detectors —
matters. Individual-level pattern matching is fundamentally insufficient against
adversaries that mimic individual legitimate requests.

### L-03: The Billboard as Proactive Defense

Publishing evidence **while the adversary is still operating** creates:
- Legal timestamp (all subsequent access is post-notice)
- Deterrent signal (you are being observed and named)
- Community evidence (others can verify the pattern)
- Contrast evidence (Google complied; Meta didn't)

In guerillaGorilla terms, this is **amicusContra** — outward projection in three
directions simultaneously: up (institutions), lateral (peers), forward (adversaries).

### L-04: Defense Architecture as Intelligence Source

The fleet's targeting pattern (wateringHole 5,362, whitePaper 3,956, 225 defense
docs, 2,305 investigation docs) reveals their priorities. They're not randomly
scraping — they're reading the investigation and the defense architecture. The
defense system itself is an intelligence target.

In preSCENT terms: the fleet is smelling us while we're smelling them. The
defense docs they read tell us what they consider valuable. Their access patterns
are reconnaissance we can read.

### L-05: The Organism's Own Traffic Can Be Autoimmune

160 songbird federation connections from home WAN piling up on degraded ISP.
The eastGate team flagged the IP as suspicious — but it was in `self-ips.txt`.
Under network stress, the organism's own federation traffic created a positive
feedback loop that amplified the degradation.

**Design principle**: Mesh federation must implement connection pooling with
exponential backoff. Unbounded retry-on-failure is autoimmune behavior.

### L-06: 80% Built, 0% Wired

The adaptive immune system has behavioral hashing, fleet antibodies, opsonize
tags, gossip validation, MHC presentation, and BearDog lineage verification.
All implemented. None connected. The `gossip.inject` handler — the single piece
of wiring that would enable cross-gate immune memory — silently fails because
it was listed in the dispatch method table but never implemented.

This is the equivalent of having an army with weapons, training, and
communications equipment, but no one plugged in the radios.

---

## Metrics

| Metric | Value |
|--------|-------|
| Total adversary requests | ~12,000 |
| Adversary classes engaged | 3 (corporate, fleet, scanner) |
| Real pages leaked before lockdown | 2,073 |
| Real pages leaked after lockdown | 0 (default scatter) |
| Defense layers active | 9 (was 8) |
| New matchers added | 4 (JS challenge, storefront, API block, default scatter) |
| Sites updated with evidence | 4 (detroit, sporePrint, whitePaper, guerillaGorilla) |
| Documents cross-linked | 6 |
| Immune system gaps identified | 4 major (ion channel, thymic, gossip, autoimmune) |
| Immune system gaps closed | 2 (ion channel, JS challenge) |
| Immune system gaps open | 2 (gossip wiring, full thymic selection) |
| Time from first adversary contact to full lockdown | ~12 hours |
| Engagement status | Ongoing (fleet and Meta still probing) |
| Repos made private (post-audit) | 1 (whitePaper) |
| Cross-domain bridges detected | 2 (first ever) |
| Fleet requests post-lockdown | 10,284 (0 real content served) |
| Meta requests post-lockdown | 644 (ALL blocked) |
| Unique document names exposed via URL paths | 387 |

---

## Open Items

| ID | Item | Priority | Status |
|----|------|----------|--------|
| O-01 | Wire `gossip.inject` handler in skunkBat dispatch | HIGH | Design ready, ~50 LOC |
| O-02 | Implement opsonize consumer on receiving gates | HIGH | Types ready, no consumer |
| O-03 | Cross-gate antibody sync via `defense.antibody:` | MEDIUM | Antibody store exists |
| O-04 | Full thymic selection (BearDog lineage training) | MEDIUM | Spec complete, not built |
| O-05 | songbird connection pooling with backoff | MEDIUM | Autoimmune mitigation |
| O-06 | Advertise `defense` in swarmVine capabilities | LOW | CLOSED |
| O-07 | Meta formal cease-and-desist | MEDIUM | Evidence timestamped |
| O-08 | Refresh billboard with post-lockdown entity counts | LOW | Automated via signal spine |
| O-09 | Behavioral self-profile (beyond IP self-tolerance) | HIGH | Lysogeny sentinel foundation exists |
| O-10 | Cloudflare ingest implementation (pre-Caddy telemetry) | LOW | Stub exists, client not built |
| O-11 | Audit all repos for private content that should not be public | HIGH | whitePaper remediated; full audit pending |
| O-12 | Build /api/public-record/timeline (demand signal from visitor 404) | MEDIUM | 404 at 13:24 ET Oct 6 |
| O-13 | Investigate curl user (58 req systematic reading of signal page, defense docs, naming trap) | MEDIUM | Open |

---

## Post-Lockdown Bloom Review (Oct 6, 2:50 PM ET)

### Bot/Agent Classification

**Compliant (commensal):** Googlebot (3 req, detroit, robots ✅), Bingbot (20 req, sporePrint, robots ✅), AhrefsBot (8, robots ✅), SemrushBot (2, robots ✅), OAI-SearchBot (3, robots.txt only ✅), ClaudeBot (2, robots ✅), Applebot (2, robots ✅)

**Non-compliant (parasitic):** Meta-ExternalAgent (642, ALL blocked post-lockdown: 558×403, 86×dropped, NO robots check), PetalBot/Huawei (28, sporePrint, no robots), Amazonbot (31, reading investigation pages — judges, PACs — no robots)

**AI Retrieval:** Reflectionbot (20 req, reading sporePrint + git repos — someone asking AI about the ecosystem), GPTBot (1, detroit home)

### Residential Proxy Fleet Status

- 10,284 requests filtered as fleet today
- Post-lockdown: 7,691 of 10,212 git requests = 404 (deep paths not in storefront)
- Remaining 200s are scatter or storefront shells
- Fleet is still active but getting NOTHING

### Meta Behavior Post-Lockdown

- ALL 644 requests blocked (558×403, 86×connection dropped)
- Shifted targeting: wateringHole (264), toadStool (186), biomeOS (41), bearDog (37)
- Now targeting GPU compute code (toadStool) — not just investigation docs

### Cross-Domain Bridge FORMED

- iOS scientist (iPhone 18.7): 5-hour session (09:44-14:50), read 8 science papers, crossed to detroit signal page at 12:28, checked /contact/, read capability parity brief. methodology→evidence→methodology bridge pattern.
- Linux investigator: detroit/signal → sporePrint → 2.5 hours later → detroit/actors/brian-banks → git source code. evidence→methodology→evidence bridge.
- This was predicted by SILT_POND Thread 2 as "the most significant single visitor event we can detect"

### New 404 Demand Signal

- `/api/public-record/timeline` at 13:24 ET — someone wants structured API access to the public record timeline
- Pairs with earlier `/keywords` and `/key-analysis` 404s — data-oriented visitors

### whitePaper Privacy Remediation

- whitePaper was PUBLIC on Forgejo — anonymous access returned 200 for all paths
- While scatter caught content (842/845 = scatter poison), URL paths exposed 387 unique filenames including: ECOPRIMAL_RESUME.md, PROPERTY_PROFILE.md, TRANSCRIPT.md, contacts.md, interview_prep_barrick_lenski_RA2.md
- Metadata IS data — filenames reveal personal info even when content is scatter
- Fixed: whitePaper now private (API PATCH via golgiAdmin). All anonymous paths return 404. Hidden from explore and org pages.

---

## Validation

This engagement validated the guerillaGorilla framework in the digital domain:

- **fEAR** — flow event detection operated in real-time against three adversary classes
- **preSCENT** — bidirectional: we detected them by behavior; they detected us by reading defense docs
- **STRIDe** — scraping cadence, gait patterns, behavioral invariants all measurable
- **amicusContra** — billboard projected evidence in three directions simultaneously
- **Cross-Protection/MAD** — forge lockdown creates no-winning-move for extractive systems

The five-layer active defense immune stack (CaddyBridge → scatter → tarpit →
honeytokens → JS challenge → existence-only storefront) evolved from a single
robots.txt to a nine-layer ion channel in under two weeks. Each adversary
encounter made the organism stronger.

---

*Filed: Wave 165e | Oct 6, 2026 | sporeGate inner membrane*
*Cross-references: detroit/signal, sporePrint/scraping_notice, whitePaper/SILT_POND, guerillaGorilla/CASE_VALIDATION*
