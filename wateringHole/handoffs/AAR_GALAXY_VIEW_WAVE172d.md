# AAR — Galaxy View: Membrane Experience Unification
## Wave 172d · 2026-10-10 · eastGate → all gates

---

## 1. Situation

The ecoPrimals organism had grown to 9+ live surfaces with 500+ pages of content, all cross-linked and breathing. But there was no map. A visitor arriving at `primals.eco` got a 301 redirect to sporePrint — thrown straight into the body with no view of the galaxy.

Every surface had its own navigation, its own voice, its own purpose. The mesh *was* navigable — signal had 11 cross-site links, sporePrint linked to everything, detroit and tuebor cross-referenced evidence. But nobody drew the map.

**What was missing:**
- No landing page at `primals.eco` (permanent redirect to sporePrint)
- No unified topology visualization
- No visible "you are here" / "the time is local" experience
- No galaxy view showing all surfaces, their roles, and connections
- No live pulse data on the root domain

## 2. What We Found

### Surface Inventory (all 200 ✓)

| Surface | Type | Content | Aliases |
|---------|------|---------|---------|
| signal | 🔥 Fire | Fleet observatory, live pressure data | — |
| thesis | 🔥 Fire | Research paper (Stomachs With No Eyes) | paper, whitepaper |
| detroit | 🔥 Fire | Public record (129 nodes, 215 edges) | evidence, tuebor |
| sporePrint | 🌿 Membrane | 392 pages, 50 baseCamp papers | spore, footprint, print |
| hypothesis | 🌿 Membrane | Artisan's Questions | questions |
| hud | 🌿 Membrane | biomeOS HUD | dashboard |
| beacon | 🔊 Sound | Free sovereign relay (E2E) | commensal |
| git/forge | 🔊 Sound | Forgejo sovereign forge | — |
| depot | 🔊 Sound | Binary distribution | — |

### Signal/Beacon/Membrane Model Applied

- **Signal = Fire** — attention at distance, outside the membrane. Electromagnetic. Unbounded. You see fire from orbit.
- **Beacon = Sound** — interest at proximity, inside the membrane. Mechanical. Attenuating. You hear sound when close.
- **Membrane = Engagement** — where the epitope docks. The transducer. Lossy compression.

### The Wildcard Membrane

Every subdomain goes through `*.primals.eco` wildcard:
- Known epitope → content
- Concept alias → redirect
- Unknown → scatter maze (behavioral classification)
- Fleet IP → honeycomb interception (224 IPs)
- `/plasmid` → federation endpoint on all surfaces

## 3. What We Built

### Galaxy View Landing Page

**Location:** `primals.eco` (was: 301 → sporePrint; now: self-contained HTML)

**Features:**
- Hero: "You are here. The time is local." with live local clock
- 3×3 grid of all surfaces, categorized by signal/beacon/membrane model
- Color-coded borders: 🔥 fire (red), 🔊 sound (blue), 🌿 membrane (green), 🛡 immune (purple)
- Live pulse data: total requests, scatter served, prism reflected, plasmid shared
- Fetches from `/metrics` every 15 seconds for live fleet pressure
- Immune surface section showing wildcard membrane behavior
- Footer: signal·beacon·membrane framework, baseCamp 50, enzymatic bounty links
- OG card: "ecoPrimals — You Are Here"
- No cookies, no tracking, no frameworks, no build step

### Caddy Configuration

**Changes to `primals.eco` block:**
1. Replaced `redir https://sporeprint.primals.eco{uri} permanent` with `file_server` serving `/opt/ecoPrimals/galaxy`
2. Added `/metrics` reverse proxy to scatter (localhost:9753)
3. Added `/plasmid` reverse proxy for federation
4. Updated OG blackwall card for galaxy view
5. Kept facebook bot handler (now returns galaxy metadata)

### Files Created/Modified

| File | Action |
|------|--------|
| `/opt/ecoPrimals/galaxy/index.html` | Created — galaxy view page |
| `/etc/membrane/Caddyfile` | Modified — primals.eco block serves galaxy |
| `infra/galaxy/index.html` | Local sync |
| `infra/plasmidBin/membrane/Caddyfile` | Local sync |

## 4. Verification

```
200 primals.eco          — galaxy view serves
200 /metrics             — live scatter data proxied
200 /plasmid             — federation endpoint proxied
200 www.primals.eco      — galaxy view (not redirect)
200 sporeprint           — still serving 392 pages
200 thesis               — still serving paper
200 signal               — still serving fleet observatory
200 tuebor               — still serving 34 analysis pages
200 detroit              — still serving 129 nodes
200 beacon               — still serving relay
200 paper                — alias still working
200 bloom                — alias still working
```

All surfaces healthy. No regressions.

## 5. Topology as Experienced

```
                        primals.eco
                     [GALAXY VIEW — you are here]
                            |
              ┌─────────────┼──────────────┐
              |             |              |
         🔥 FIRE       🌿 MEMBRANE    🔊 SOUND
         (outside)     (engagement)   (inside)
              |             |              |
         signal         sporePrint      beacon
         thesis         hypothesis      forge
         detroit/tuebor    hud          depot
              |             |              |
              └─────────────┼──────────────┘
                            |
                    *.primals.eco
                 [WILDCARD MEMBRANE]
                 epitope sort → content
                 unknown → scatter maze
                 fleet → honeycomb
```

## 6. Design Principles

1. **No framework.** Single HTML file. No build. No dependencies. Loads in <50KB.
2. **Live data.** The organism breathes — pulse section shows real-time scatter metrics.
3. **Signal/Beacon/Membrane model visible.** Fire surfaces (red), Sound surfaces (blue), Engagement surfaces (green), Immune surface (purple).
4. **"The time is local."** JavaScript clock shows the visitor's local time, not server time. Emphasizes: you are the observer.
5. **H(data|epitope) < H(data|alphabet) < H(data).** The compression inequality is visible in the footer. The organism sorts by meaning, not by character.
6. **No tracking.** No cookies, no analytics, no IP storage. The membrane observes behavior, not identity.

## 7. What Comes Next

| Priority | Task | Gate |
|----------|------|------|
| P0 | Verify `/metrics` CORS for cross-origin galaxy loads | eastGate |
| P1 | Add SVG topology map (interactive node graph) | eastGate |
| P2 | Surface health indicators (green/amber/red per surface) | sporeGate |
| P3 | Animated connection lines showing live traffic flow | eastGate |
| P4 | Mobile-first responsive audit | all |

## 8. Lessons

The galaxy was always there. Every surface was live, cross-linked, breathing. What was missing was the cartography — the one page that says "this is the organism, these are its surfaces, here is how they relate." The membrane was doing its job (sorting, classifying, routing) but the work was invisible to visitors.

primals.eco should never have been a redirect. It should always have been the map. Now it is.

Signal is fire. Beacon is sound. The membrane is engagement.
You are here. The time is local.

---
*AAR authored by eastGate Artisan · Wave 172d · 2026-10-10*
*Status: EXECUTED and DEPLOYED*
