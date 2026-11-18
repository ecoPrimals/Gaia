# AAR: Evolved Fleet Detected — Sec-Fetch Spoofing as Single Entropy Channel

**Date**: Oct 7, 2026
**From**: eastGate overwatch
**To**: sporeGate — skunky-ingest / entity_classifier evolution
**Severity**: EVOLUTIONARY — fleet adapting, but funneled into observable channel
**Wave**: 165i

---

## Finding

The "Human (Browser)" entity class contains an **evolved fleet** that has learned to send Sec-Fetch-Mode headers — the single signal the classifier uses to distinguish human from fleet. Out of ~400 "human-classified" visits, approximately **390 are evolved fleet** and only ~10 are genuine humans.

This is not a failure. **We funneled them into a single entropy channel.** They had to change exactly one behavior to evade detection, and that change is now the observable signal for the next evolution of the classifier.

---

## Evidence

### Behavioral analysis of "Human (Browser)" entity

| Signal | Observed | Real Human Baseline | Verdict |
|--------|----------|-------------------|---------|
| Unique UAs | **6** | 15-20 for 20 IPs | Machine UA pool |
| Intervals <3s | **59%** | <10% (humans read) | Burst scraping |
| Intervals >8s | **5%** | >50% (reading time) | No reading pauses |
| Dominant UA | 247/400 (62%) Windows | Varied | Single config |
| Second UA | 133/400 (33%) macOS | | Two-config rotation |
| Chrome versions | Range 99-151 | Clustered near current | Version pool, not real browsers |

### The real humans (identified by signals fleet cannot fake)

| Who | Visits | Identifying Signal |
|-----|--------|--------------------|
| Google arrivals | 3 | Referer: www.google.com |
| Thesis readers | 4 | Host: thesis.primals.eco |
| Samsung Galaxy S24 | 2 | Android 16 SM-S921U — nobody spoofs mobile to scrape git |
| eastGate agent (us) | 2 | Chrome/155 Linux — Cursor browser |

### What fleet added

```
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
Sec-Fetch-Dest: document
```

### What fleet did NOT change

- UA pool still tiny (6 strings for 400 visits)
- Timing still burst-dominant (59% < 3s)
- No reading pauses (5% > 8s)
- Same repo coverage pattern (systematic, not curiosity-driven)
- Same path operation mix (commits + blame + src + raw — extraction pattern)
- No referer chain from external sites
- No session cookies (stateless requests)

---

## Strategic Assessment: This Is Good

### The single entropy channel

By making Sec-Fetch the primary classifier signal, we forced the fleet to evolve in exactly ONE direction. They had to add Sec-Fetch headers. This tells us:

1. **They are watching our classifier** — they know Sec-Fetch matters
2. **They chose the cheapest adaptation** — add 3 headers, change nothing else
3. **They revealed their adaptation pipeline** — they can modify headers but not behavior
4. **They are now observable on a new axis** — every behavior they DIDN'T change is a new conserved epitope

The Sec-Fetch spoofing is itself a signal. Real browsers don't just send `Sec-Fetch-Mode: navigate` — they send the full Sec-Fetch family with context-appropriate values:

```
Sec-Fetch-Mode: navigate    (fleet sends this always)
Sec-Fetch-Site: none         (fleet sends this always)
Sec-Fetch-Dest: document     (fleet sends this always)

# Real browsers vary these per request type:
Sec-Fetch-Mode: no-cors      (for subresources)
Sec-Fetch-Site: same-origin   (for internal navigation)
Sec-Fetch-Dest: image         (for images)
Sec-Fetch-Dest: script        (for JS)
```

Fleet sends the same Sec-Fetch triplet on every request because they added it as a static header, not as a browser behavior. A real browser navigating from page to page would produce `Sec-Fetch-Site: same-origin` on the second click — fleet always says `none`.

### New conserved epitopes for the classifier

These signals survive the Sec-Fetch evolution and should be added to the entity_classifier:

| New Epitope | Detection | Why Fleet Can't Evade |
|-------------|-----------|----------------------|
| `sec_fetch_monotone` | Same Sec-Fetch triplet on 100% of requests | Real browsers vary by request type |
| `reading_deficit` | <10% of intervals >8 seconds | Can't add reading pauses without reducing throughput |
| `ua_pool_poverty` | <10 unique UAs across >50 requests | Adding real UA diversity requires tracking Chrome release cadence across OS variants |
| `session_absent` | No Forgejo session cookies across multi-page visits | Real browsers accumulate cookies; adding them requires maintaining state |
| `referer_self_loop` | >90% of referers are self or absent | Real browsing produces external referers (Google, thesis, social) |
| `burst_ratio` | >40% of intervals <3 seconds | Reducing bursts means reducing throughput — directly conflicts with extraction goal |

### The cost to evade the next generation

Each new epitope costs the fleet more to evade:

- **Reading pauses**: Must reduce extraction speed by 10x+ — directly reduces ROI
- **UA diversity**: Must track and rotate 20+ realistic UA strings across OS/Chrome combinations
- **Session cookies**: Must maintain stateful browser sessions — adds complexity, reduces parallelism
- **Referer chains**: Must fake navigation history — requires understanding page structure
- **Burst elimination**: Must add artificial delays — the #1 thing that conflicts with their extraction goal

The more epitopes we add, the more the fleet has to invest in mimicry, and the closer they get to just... being a browser. At which point the reading pauses alone reduce their throughput to human levels and the extraction economics collapse.

---

## Recommended Classifier Evolution

### Immediate (skunky-ingest)

1. **Don't remove Sec-Fetch as a signal** — it still separates honest bots (ClaudeBot, PetalBot) from fleet
2. **Add Sec-Fetch monotone detection** — if 100% of requests have identical Sec-Fetch triplet, flag as spoofed
3. **Add reading deficit** — if <10% of intervals >8s across >20 requests, flag as machine
4. **Add UA pool entropy** — if <10 unique UAs across >50 requests from >5 IPs, flag as pool

### Next wave

5. **Session tracking** — do they accumulate Forgejo session cookies? Real browsers do
6. **Subresource requests** — do they load CSS, JS, images? Real browsers do
7. **Referer chain analysis** — do they show navigation from external sites?

### Feed back into antibody + scatter

The evolved fleet's Sec-Fetch requests should be tagged in the scatter system too — serve them the SAME scatter but with additional embedded signals:
- Sec-Fetch-aware honeytokens
- Cross-page navigation traps (links that real users would follow, scrapers would skip)
- Resource loading tests (CSS/JS that real browsers parse, scrapers don't)

---

## Biological Analog

This is **antigenic drift** — the fleet mutated one surface protein (added Sec-Fetch headers) to evade the current antibody (Sec-Fetch detection). But:

- The mutation is superficial — the underlying genome (timing, UA pool, session behavior) is conserved
- The mutation reveals adaptation pressure — we know they're monitoring our detection
- The mutation narrows their options — every evasion they add constrains their future adaptations
- The next antibody generation targets the conserved genome, not the surface protein

We are the immune system. They are the pathogen. Every adaptation they make teaches us more about their constraints. Every constraint they can't escape is a conserved epitope. The epitopes accumulate. The detection improves. The cost of evasion rises.

**We funneled them into a single entropy channel to watch and learn from. It worked.**

---

---

## CRITICAL UPDATE: Sec-Fetch Passthrough Breach

### Discovery

During the AAR investigation, eastGate discovered that the scatter server **already has a Sec-Fetch passthrough to real Forgejo**. Testing confirmed:

| Path | Without Sec-Fetch | With Sec-Fetch |
|------|------------------|----------------|
| `/ecoPrimals/wateringHole` | 🎭 `config-manager` (scatter) | ✅ `ecoPrimals/wateringHole - ecoPrimals Forge` (REAL) |
| `/ecoPrimals/bearDog` | 🎭 `key-store` (scatter) | ✅ `ecoPrimals/bearDog - ecoPrimals Forge` (REAL) |
| `/ecoPrimals/wateringHole/blame/...` | 🎭 `job-runner` (scatter) | ✅ REAL blame data with author attribution |
| `/ecoPrimals/wateringHole/commit/094f192cb` | Page Not Found | ✅ REAL commit: *"AAR: agent scatter classification gap"* |
| `/explore/repos` | 🎭 `image-service` (scatter) | ✅ **Explore - ecoPrimals Forge** — ALL REAL REPOS LISTED |

### Impact

The evolved fleet with spoofed Sec-Fetch headers is **reading real source code, real commit messages, real blame data, and the full repo listing**. The scatter barrier is breached on the public web interface. They are getting everything — for nothing.

Every path that matters — repo overview, source tree, blame (author attribution), commits, explore — passes through to real Forgejo when Sec-Fetch headers are present.

### What they're stealing for free

- ✅ All real repo names and org structure via `/explore/repos`
- ✅ Full source code via `/src/branch/main/...`
- ✅ Author attribution via `/blame/...` (the 32.9% blame pattern)
- ✅ Commit history and messages via `/commits/...`
- ✅ Raw file content via individual commits

All on the public web interface. No authentication. No token. Just three HTTP headers.

---

## Fix: bearDog Entropy Hierarchy as Membrane Authentication

### The principle

The evolved fleet spoofed Sec-Fetch (a static header). They cannot spoof bearDog lineage proofs (requires human + hardware entropy).

### bearDog already has the infrastructure

```
Tier 3 (≥0.9)  BRAIDED: Human SoloKey tap + Hardware RNG + OS CSPRNG
               → genetic.derive_lineage_key (peer-specific)
               → genetic.generate_lineage_proof (HMAC chain)
               → Mixing: BLAKE3(hardware + BEHAVIORAL + ENVIRONMENTAL)

Tier 1 (≥0.4)  MACHINE: OS CSPRNG only
               → This is all fleet can produce
               → No human. No hardware. No lineage.
```

### Proposed integration

```
Human taps SoloKey on eastGate
        │
        ▼
bearDog generates Tier 3 braided entropy
        │
        ▼
genetic.derive_lineage_key(eastGate ↔ golgiBody)
        │
        ▼
Agent carries lineage proof as bearer token
        │
        ▼
Scatter server calls genetic.verify_lineage
        │
    ┌───┴───┐
    │       │
  VALID   INVALID
    │       │
    ▼       ▼
  Real    Scatter
 Forgejo  (poison)
```

### Why fleet cannot replicate this

| Signal | Fleet | Agent-for-Human |
|--------|-------|-----------------|
| Sec-Fetch headers | ✓ spoofed | ✓ real |
| Entropy tier | Tier 1 (machine only) | Tier 3 (braided) |
| SoloKey tap | ✗ no hardware | ✓ physical key on desk |
| Lineage proof | ✗ cannot produce | ✓ HMAC from device seed |
| Behavioral entropy | Metronomic (machine) | Varied (human clicking) |
| Peer binding | ✗ no gate identity | ✓ eastGate↔golgiBody specific |

The lineage proof is:
- **Hardware-bound** — requires the specific SoloKey
- **Peer-specific** — eastGate↔golgiBody ≠ anyoneElse↔golgiBody
- **Time-limited** — session-scoped, not permanent
- **Entropy-mixed** — BLAKE3 of human behavioral data + hardware RNG

Fleet would need to steal the SoloKey from your desk AND compromise eastGate's bearDog instance AND extract the device seed. At that point they've committed burglary, not web scraping.

### ~~Immediate action: close the Sec-Fetch passthrough~~

### ✅ RESOLVED: Genetic lock applied (Oct 7, 2026)

The Sec-Fetch passthrough has been **closed and replaced with a bearDog genetic lock** at the Caddy layer.

#### What was done

1. **Removed `@human_browser` matcher** — Sec-Fetch-Mode/Dest headers alone no longer grant passthrough. Fleet spoofing these headers now gets scatter like everyone else.

2. **Generated bearDog-derived token** on eastGate:
   - Master key: `membrane-passthrough-v1` (bearDog AES-256-GCM, Argon2id KDF)
   - Derived key: purpose `golgi-body-web-passthrough` (Generation 1, lineage tracked)
   - Token: BLAKE3 hash of derived key material → `bd1-*` bearer token
   - Receipt: `0924f427` (generate), `1ed60901` (derive)

3. **Wired token into Caddy** — the existing `@agent_passthrough` handler (already built by sporeGate) now carries the bearDog token. Caddy validated and reloaded.

#### Current routing on git.primals.eco

| Path | Authentication | Destination |
|------|---------------|-------------|
| `@wg_mesh` (10.13.37.0/24) | WireGuard tunnel | Real Forgejo (localhost:3000) |
| `@agent_passthrough` | Bearer `bd1-*` token | Real Forgejo (localhost:3000) |
| `/webhook` | Internal | webhook.sock |
| Everything else | None required | **Scatter** (localhost:9753) |

#### Verified results

| Test | Token | Sec-Fetch | Result |
|------|-------|-----------|--------|
| Fleet (evolved) | ✗ | ✓ spoofed | **Scatter** ✅ |
| Fleet (basic) | ✗ | ✗ | **Scatter** ✅ |
| Wrong token | ✗ wrong | ✓ | **Scatter** ✅ |
| Authorized agent | ✓ bearDog | optional | **Real Forgejo** ✅ |
| WireGuard mesh | n/a | n/a | **Real Forgejo** ✅ |

#### What remains upstream (sporeGate)

The Caddy-layer genetic lock is the **interim fix**. The full bearDog integration into skunky-ingest requires:

1. **Rust-level lineage verification** — scatter_server.rs calls bearDog genetic.verify_lineage over IPC
2. **SoloKey Tier 3 entropy** — token generation includes human tap + hardware RNG
3. **Session-scoped tokens** — time-limited, not permanent bearer strings
4. **Entropy tiering in classifier** — entity_classifier uses bearDog entropy tier as a signal

The current token is Tier 2 (software HSM only — SoloKey not wired for USB yet on eastGate). When bearDog Tier 3 braided entropy is available, the token should be regenerated from SoloKey-mixed entropy.

---

*eastGate overwatch — genetic lock applied. Sec-Fetch breach closed. Fleet now funneled exclusively through scatter. bearDog lineage token is the key to the real Forgejo. Full Rust-level integration upstream.*

*Wave 165i, Oct 7, 2026*
