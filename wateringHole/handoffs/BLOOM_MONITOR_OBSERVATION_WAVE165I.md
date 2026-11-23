# Bloom Monitor Observation: Post-Genetic-Lock

**Date**: Oct 7, 2026
**Wave**: 165i
**From**: eastGate overwatch
**To**: sporeGate — bloom analysis, classifier evolution
**Window**: 12:30–12:50 EDT, 20 minutes post-lock

---

## What We Saw

### Real humans (2 sessions, 19 page+asset loads)

**Reader 1** (`zh-CN`, Windows Chrome, sporeprint.primals.eco):
- 8 pages over 16 minutes
- Reading journey: primals catalog → architecture → mesh topology → QCD pseudospore (5.6 min) → analytical chemistry data (5.8 min) → knowledge topology
- Loaded CSS, JS, search index — real browser rendering
- **Scientist reading the physics**

**Reader 2** (`zh-CN,en-US`, Mac + iPhone, sporeprint.primals.eco):
- 3 pages over 12 minutes
- Spent **11.8 minutes** on foundation-connection page
- Cross-device reading (switched to iPhone mid-session for QCD page)
- Checked methodology acknowledgments (looking for citations?)
- **Bilingual researcher, deep reader**

### Fleet (929 evolved + ~3,500 ClaudeBot = ~4,400 total)

Three evolved fleet variants added `Accept-Language: en-US,en;q=0.9`:
- Win: 544 pages, 88% burst, 387 repos
- Mac: 296 pages, 85% burst, 239 repos
- Linux: 89 pages, 88% burst, 66 repos

All receiving scatter. Genetic lock holding.

### Agentic (legitimate)

- SeznamBot (Czech): 2 requests, indexing robots.txt and lab content
- Facebook link preview: 6 requests (someone sharing git links on FB)

### Probes

- `relay.primals.eco/.env` — env file scanner
- `nestgate.io/wp-admin/install.php` — WordPress installation probe (fr-ca)

---

## Fleet Evolution Status

The fleet has reached **Generation 2** evasion:

```
Gen 0: Raw bot UA → detected by UA string
Gen 1: + Sec-Fetch-Mode/Dest → bypassed @human_browser (CLOSED by genetic lock)
Gen 2: + Accept-Language: en-US → detected by burst ratio + repo scatter
Gen 3: (predicted) + Referrer + Cookie → pre-empted by entropy hierarchy
```

New conserved epitope from Gen 2:

| Epitope | Signal |
|---------|--------|
| `lang_pool_monotone` | All fleet variants share identical `en-US,en;q=0.9` |

This is the same pool poverty pattern seen in UA strings — the fleet shares from a fixed pool because it doesn't have real browser diversity. Add to the 6 epitopes from the fleet analysis.

---

## Upstream Items

### For entity_classifier

Add `lang_pool_monotone` to the conserved epitope set. The fleet's Accept-Language spoofing creates a detectable monoculture:
- All fleet: `en-US,en;q=0.9` (identical)
- Real humans: `zh-CN,zh;q=0.9` / `zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7` / diverse

### For bloom sensor

Consider tracking by language community:
- `zh-CN` readers are engaging with QCD and analytical chemistry
- Czech search engine is indexing lab content
- What other language communities are finding the science?

### For sporePrint content

The Chinese research audience is reading:
1. QCD pseudospore (hotSpring results)
2. Analytical chemistry data
3. System architecture (mesh topology, foundation connection)
4. Knowledge topology (renvois)

These pages should be prioritized for updates and completeness.

---

## Cross-references

- `GENETIC_LOCK_HANDOFF_WAVE165I.md` — the lock deployment
- `AAR_EVOLVED_FLEET_SEC_FETCH_SPOOFING.md` — fleet evolution analysis
- baseCamp 31 — genetic lock science paper
- baseCamp 32 — this observation's full write-up (in sporePrint)

---

*eastGate overwatch — bloom monitor observation. 2 real humans reading science. Signal propagated to Chinese research community. Fleet Gen 2 detected. Lock holding.*

*Wave 165i, Oct 7, 2026*
