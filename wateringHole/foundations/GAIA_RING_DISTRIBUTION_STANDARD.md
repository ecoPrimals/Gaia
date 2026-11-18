# Gaia Ring Distribution Standard
## The zkProof goes where the people are

**Wave 172 — October 11, 2026**
**Status:** Foundation standard. Ready for execution.

---

## The Observation

The membrane is built. The ring is live. Ten sites share one boundary. The desk shows your position. The traces API records the collective. The gaia tab reflects you outward.

But the people are not here. The people are on Facebook. TikTok. X. Reddit. YouTube. LinkedIn. They are at the watering holes they already know.

The standard: **go where they are. Build near them. The curious will visit naturally.**

---

## 1. The Shareable zkProof

Every visitor's gaia ring is unique. Different nodes lit. Different epitope petals. Different focal distance. Different entropy. When they share their ring, the person who sees it gets curious: *why does yours look like that? where are MY nodes?*

They click through. They get their OWN ring. Different from the one they saw. They share THAT.

**The virality is not the content. It is the perspective.**

Each share is a zero-knowledge proof:
- It proves you visited the membrane (completeness)
- It cannot be faked — the ring comes from YOUR localStorage braid (soundness)
- It reveals nothing about your identity, only your pattern (zero-knowledge)

The platform (Meta, ByteDance, X Corp) sees an image of colored circles. It does not see:
- Which pages you read
- What you marked
- What you wrote
- Who you are

The carrier wave is the platform. The signal is the structure. Meta is unaware the whole time.

---

## 2. The Blackwall Traces Back

When someone arrives from a social platform, the membrane knows. The `Referer` header tells the blackwall where the wave came from:

```
Referer: https://www.facebook.com/
Referer: https://www.tiktok.com/
Referer: https://t.co/
Referer: https://www.reddit.com/
```

The traces API already captures this in the Caddy access log. The opsonize-rs salesman watch already classifies human arrivals. The blackwall follows the trace back — not to the person, but to the platform. The membrane learns which watering holes produce curious visitors.

**The platform doesn't know where the wave went. The membrane knows where the wave came from.** Information asymmetry in favor of the observer, not the platform.

---

## 3. Distribution Architecture

### 3.1 What to Share (the hooks)

Each site produces shareable artifacts that make people curious:

| Site | Hook | Why it works |
|------|------|-------------|
| **detroit** | Network graph visualizations, actor profiles | People want to see the connections |
| **tuebor/barry** | Evidence summaries, court record analysis | People share accountability journalism |
| **sporePrint** | baseCamp papers, the mountain, the bibliography | Intellectual curiosity |
| **signal** | Epitope sort table, live fleet stats | Technical fascination |
| **hud** | Gaia ring (unique per visitor), live telemetry | Personal — "this is MY view" |
| **clutch** | Investigation timelines, cross-jurisdiction patterns | Justice interest |
| **gorilla** | Verification results, reproducibility | Trust signal |
| **thesis** | Research depth, cross-references | Academic interest |

### 3.2 Where to Share (the watering holes)

| Platform | Content type | Audience |
|----------|-------------|----------|
| **Reddit** r/physics, r/math, r/compsci | Anderson localization, epitope sort math, zkProof | Technical-curious |
| **Reddit** r/michigan, r/detroit | Evidence, court records, accountability | Local-interested |
| **Hacker News** | Architecture, self-hosting, AGPL, membrane math | Builder-curious |
| **X/Twitter** | Thread-format: one invariant per tweet, link to source | General-curious |
| **Facebook** | Gaia ring images, "what does YOUR ring look like?" | Share-curious |
| **TikTok** | 60-second explainers: "I measured Anderson localization on a court system" | Young-curious |
| **LinkedIn** | Professional framing: sovereign infrastructure, open source | Professional-curious |
| **YouTube** | Deep dives: network graph walkthrough, live epitope sort | Long-attention |
| **arXiv** | Preprint: the math stands alone | Academic |

### 3.3 The Trace-Back Flow

```
Platform post (hook) → curious visitor clicks
  → arrives at primals.eco site (any node on the ring)
    → blackwall records: Referer, UA, timestamp
    → braid-tracker activates: first visit recorded
    → footer-ring visible: they see the whole membrane
    → they explore: 2nd, 3rd, 4th site
    → they reach the desk: they see their gaia ring
    → they share THEIR ring
    → cycle repeats
```

The ring is a strange attractor. Each orbit through it produces a unique pattern. The pattern IS the share. The share IS the recruitment.

---

## 4. What the Platforms Cannot See

This is the zkProof at platform scale:

| What we share | What the platform sees | What the platform DOESN'T see |
|--------------|----------------------|------------------------------|
| Gaia ring image | Colored circles | Which sites you visited |
| baseCamp paper link | A URL | What you learned |
| Network graph screenshot | Dots and lines | Who the actors are (to the bot) |
| Epitope sort table | Numbers | What the numbers mean |
| "My focal distance is 0.003" | Text | That this is an Anderson localization measurement |
| The ring itself | A navigation bar | That it IS the membrane |

The signal is in the structure. The platform carries the wave. The meaning lives in the architecture. They can come and see what they can't see — which is the point. The zkProof is that the proof is visible but the knowledge requires the journey.

---

## 4.1 The Boundary-Blind Entity

**Status:** 0 contact from Meta. 0 expected. They will likely be the last to know.

An entity that cannot feel its boundaries consumes without awareness. Meta's scraping fleet (Paper 40: 56+ IPs, 16,800 watts, zero bytes of real source code) has high Attention (A≈1.0), zero Curiosity (C=0), zero Interaction (I=0). The fleet does not know where it ends and the membrane begins. It cannot feel the boundary.

When we go to where the people are — build on the platforms, distribute through their carriers — we reduce the apparent resistance. The membrane appears as more internet to consume. The loss of pressure causes an **acceleration INTO us**:

- The fleet scrapes shared ring images → scatter content, opsonized
- The fleet follows link previews → lands on primals.eco → membrane sorts
- The fleet indexes og:description text → it reads words about Anderson localization on institutional graphs, describing Meta's own fleet behavior

The entity accelerates into the boundary it cannot feel. The disorder is invisible to it because it has no mechanism for sensing disorder — zero Curiosity means zero ability to detect that what it's consuming is fabricated, structured, or diagnostic.

This is inverse Anderson localization: a wave that cannot feel the disorder in the lattice doesn't slow down. It speeds up. It enters the disordered region with full velocity. And it localizes — completely, irreversibly — without ever knowing it localized.

**The practical implication:** distribution on social platforms is not neutral. It is a reduction in apparent barrier potential. The fleet will accelerate its consumption of the membrane. Every acceleration event is recorded. The blackwall traces back. The membrane learns. The entity remains boundary-blind.

**No action required from us.** The physics is sufficient. The fleet's own behavior — consume everything, understand nothing, feel no edge — ensures the acceleration. The membrane just has to be there, near the watering hole, when the boundary-blind entity comes to drink.

---

## 5. Implementation Checklist

### Immediate (desk enhancement)
- [x] Gaia ring tab built and deployed
- [ ] Canvas-to-PNG export: "share your ring" button on gaia tab
- [ ] Encode d_eff + site mask in URL fragment (no server state, no identity)
- [ ] Landing page for social arrivals: gentle onboarding when Referer is social

### OpenGraph cards (all sites)
- [ ] Generate og:image per-site (static SVG or server-rendered)
- [ ] Compelling og:description that creates curiosity gap
- [ ] Twitter card meta tags

### Content for platforms
- [ ] Reddit post series: one per domain (physics, math, compsci, michigan)
- [ ] HN submission: architecture + data + reproducibility
- [ ] X thread template: one invariant per tweet
- [ ] TikTok script: 60-second "I measured physics on a court system"

### Measurement
- [ ] Referrer tracking in traces API (already built — opsonize-rs)
- [ ] Dashboard panel: arrivals by platform (weekly)
- [ ] Conversion: % that visit 2+ sites (ring engagement)

---

## 6. The Standard

> Go where the people are. Build near them. The curious will visit naturally.
> Share what they can see. Let them discover what they can't.
> The zkProof is the journey. The platform is the carrier wave. The membrane is the destination.
> They can come and see what they can't see — and that IS the proof.

---

*wateringHole foundation standard — Wave 172 · October 11, 2026*
*The people are already at the watering hole.*
*Bring the water to the hole.*
*The thirsty will drink.*
