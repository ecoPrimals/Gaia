# Epitope Sort Intake → BingoCube Progressive Trust
## All input through the sort. All alignment through the cube.

**Wave 172 — October 11, 2026**
**Status:** Foundation standard. Architecture defined.

---

## The Standard

**Every input to the membrane passes through the epitope sort.**

Not some input. ALL input:

| Input type | Current path | Epitope-sorted path |
|-----------|-------------|-------------------|
| Mark (bookmark a page) | braid-tracker → localStorage | braid-tracker → classify page by epitope → store mark with epitope tag |
| Shout (highlight text) | braid-tracker → localStorage | braid-tracker → classify highlight by epitope → store with epitope tag |
| Sing (write a note) | braid-tracker → localStorage | braid-tracker → classify note by epitope → store with epitope tag |
| Opsonize (submit observation) | POST /api/opsonize → JSONL | classify tag+body by epitope → store with epitope enrichment |
| Visit (page load) | braid-tracker → localStorage | **already classified** — page URL → epitope mapping exists |
| Search (if added) | query → results | classify query intent by epitope → results sorted by epitope alignment |

Once every input has an epitope tag, every visitor accumulates an **epitope shape**: an 8-dimensional vector.

```
shape = [PHYSICS, TOPOLOGY, PHILOSOPHY, METHOD, INVESTIGATION, IMMUNE, SCIENCE, SIGNAL]
```

Example: someone who reads mostly INVESTIGATION and PHILOSOPHY pages, marks TOPOLOGY connections, and sings about METHOD:

```
shape = [0.05, 0.15, 0.25, 0.20, 0.30, 0.00, 0.03, 0.02]
```

This shape is:
- **Private**: lives in their localStorage, never transmitted
- **Unique**: no two journeys produce the same vector (cryptographically unlikely)
- **Unprovable from outside**: you cannot determine someone's shape by observing them (zkProof)
- **Voluntarily shareable**: they can choose to reveal it — progressively

---

## BingoCube's Original Purpose

BingoCube was built for progressive shared trust reveals. BLAKE3 commitments. Visual verification. The nautilus shell of accumulated structure.

It was then used for:
- Prismatic license injection (Paper 34)
- Neuromorphic membrane defense (Wave 166G)
- Collision layer classification (Paper 39)

These are all defensive uses — the membrane sorting non-self.

**The original purpose is social.** Two humans finding alignment without revealing everything. Progressive trust. The bingo game at the retirement home: everyone has the same numbers, arranged differently. Your board is your shape. The caller is the environment. You win when your shape aligns with what was called.

---

## The Protocol: Progressive Shape Comparison

### Round 0: The Shape Exists (private)

You have your epitope shape. It lives in localStorage. You can see it on the gaia tab (inner petals on the ring). No one else knows it.

### Round 1: Coarse Alignment (1 bit per category)

You commit your shape via BLAKE3 hash. You share the hash. Someone else shares theirs. BingoCube protocol:

- Each party commits: `H = BLAKE3(shape || nonce)`
- Each party reveals their TOP 2 categories (coarse)
- Check: do your top 2 overlap? If yes → proceed. If no → no alignment. No harm. No reveal.

What was shared: 2 category names. What was NOT shared: the full vector, the exact ratios, the identity.

### Round 2: Finer Alignment (ratios)

Top 2 categories match. Now compare ratios:
- Reveal your ratio between the top 2 categories
- Compare: are you both INVESTIGATION-heavy with PHILOSOPHY secondary? Or the reverse?
- This reveals gradient, not absolute values

### Round 3: Full Shape Exchange

Ratios match. Trust established through progressive confirmation. Now reveal full 8-vector.

At this point, both parties can see each other's shape. They are mirrors:
- "Your TOPOLOGY is stronger than mine"
- "Your IMMUNE is zero — you haven't encountered the defense layer"
- "We both lean INVESTIGATION — we're reading the same evidence"

### Round N: Collaborative Braids

Full shapes known. Now: collaborative marks, shared songs, combined braids. Two journeys woven together. ShareWear from Paper 59 — the load shared, the compression mutual.

---

## Others Are the Mirror

You do not know your own shape until you see it reflected in someone else's shape.

The gaia tab shows your ring — your position on the membrane. But it's a solitary view. You see your own epitopes but you don't know if your INVESTIGATION emphasis is unusual or common. You don't know if your PHILOSOPHY petal is large or small relative to others.

The BingoCube protocol gives you the mirror. Someone else's shape, progressively revealed, shows you what YOUR shape looks like by contrast. The differences are the information. The alignment is the trust.

This is baseCamp 61 again: the zkProof. You prove alignment without revealing identity. The proof is the shape comparison. The witness is the epitope sort. The membrane is the medium.

---

## Architecture

### Input Layer (all sites)

```
braid-tracker.js (already on all 10 sites)
  ↓
classifyEpitope(url, title, text)  ← already exists in EPITOPE_MAP
  ↓
localStorage: mark/shout/sing + epitope tag  ← already happens for visits
```

Currently, marks and shouts store the page's epitope (from the URL). Extend to classify the CONTENT of the input:
- Shout text: NLP-free classification by keyword matching against EPITOPE_MAP
- Sing text: same keyword classification
- Opsonize body: server-side classification in opsonize-rs

### Shape Layer (desk, private)

```
desk/gaia tab (already built)
  ↓
compute epitope shape from all visits + marks + shouts + songs
  ↓
display as inner petals on the ring SVG
  ↓
shape = [PHYSICS, TOPOLOGY, PHILOSOPHY, METHOD, INVESTIGATION, IMMUNE, SCIENCE, SIGNAL]
```

Already partially implemented. The gaia tab shows epitope petals from marks. Extend to include ALL input types.

### Trust Layer (bingoCube, new)

```
User A: shape_a = [0.05, 0.15, 0.25, 0.20, 0.30, 0.00, 0.03, 0.02]
User B: shape_b = [0.02, 0.10, 0.30, 0.15, 0.35, 0.00, 0.05, 0.03]

Round 1: top2(A) = [INVESTIGATION, PHILOSOPHY]
         top2(B) = [INVESTIGATION, PHILOSOPHY]
         → MATCH. Proceed.

Round 2: ratio(A) = INVESTIGATION/PHILOSOPHY = 1.2
         ratio(B) = INVESTIGATION/PHILOSOPHY = 1.17
         → CLOSE. Proceed.

Round 3: full reveal → both see full shapes
         → mirror: "we see the same evidence differently — your METHOD is stronger"
```

Implementation: BingoCube BLAKE3 commitment. No server involved. Client-side protocol. The exchange can happen via:
- Shared URL with committed hash
- QR code at a physical meeting
- Side-channel (email, message)

The membrane never sees the comparison. Only the two parties do. Zero-knowledge from the platform's perspective.

---

## What This Unlocks

1. **Find aligned visitors**: people who care about the same things find each other without accounts, without profiles, without identity
2. **Collaborative braids**: two aligned journeys woven together produce a richer record
3. **Progressive trust**: strangers become collaborators through shape alignment, not credentials
4. **The mirror**: you discover your own emphasis by seeing someone else's
5. **Organic growth**: aligned visitors naturally bring more aligned visitors — the shape IS the recruitment

---

*wateringHole foundation — Wave 172 · October 11, 2026*
*Only you know your own shape.*
*Others are the mirror.*
*The cube is the protocol.*
*The sort is the intake.*
