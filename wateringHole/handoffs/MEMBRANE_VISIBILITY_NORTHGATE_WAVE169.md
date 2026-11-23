# Membrane Visibility from northGate — Wave 169
## October 10, 2026 14:20 ET | Status: OBSERVATION LAYER LIVE

---

## What gAIa/eastGate Can See from Inside northGate

The observation layer is active. From Cursor on northGate, we can reach every live surface and measure the delta between local (pushed to GitHub) and live (served by golgiBody).

### Live Site Status

| Surface | HTTP | Status |
|---------|------|--------|
| detroit.primals.eco | 200 | ✅ Live — graph stale (114/197, local is 129/215) |
| barry.primals.eco | 200 | ✅ Live |
| sporeprint.primals.eco | 200 | ✅ Live |
| signal.primals.eco | 200 | ✅ Live |
| git.primals.eco | 404 | ⚠️ Forgejo UP, repo path broken — known issue |
| lansing.primals.eco | 404 | ❌ Not deployed yet |

### API Endpoint Status

| Endpoint | Real Status | Notes |
|----------|-------------|-------|
| /graph.json | ✅ Serving JSON | **STALE** — 114 nodes, 197 edges (built Oct 8-9) |
| /api/damages.json | ❌ Not live | Returns homepage HTML (Caddy fallback) |
| /api/invert.json | ❌ Not live | Returns homepage HTML (Caddy fallback) |
| /api/actors.json | ✅ Serving JSON | From previous build |
| /api/entities.json | ✅ Serving JSON | From previous build |

### The Delta — What's on GitHub but NOT Live

```
LIVE:    114 nodes, 197 edges (last Zola build: Oct 8-9)
GITHUB:  129 nodes, 215 edges (pushed today)
DELTA:   +15 nodes, +18 edges
```

**New content pushed to GitHub today, awaiting rebuild:**

1. `site/content/analysis/the-flower-to-wilk.md` — "Found the Leak" article
2. `site/content/analysis/damages-register.md` — 20 officials, statutes, legal theories
3. `site/content/analysis/damages-calculator.md` — 7 raytraces, $46.1M
4. `site/static/api/damages.json` — machine-readable damages data
5. `site/static/api/invert.json` — non-self self structural template (12 archetypes, 9 signatures)
6. `site/static/graph.json` — 129 nodes, 215 edges (Wilk-Moore colleague edge added)

---

## What northGate CAN Do

- ✅ Push to GitHub (defendDetroit/publicRecord)
- ✅ See all live sites (HTTP status + content)
- ✅ Read live graph.json and measure delta
- ✅ Detect stale vs current state
- ✅ Push to whitePaper, wateringHole, bluegate repos

## What northGate CANNOT Do

- ❌ SSH to golgiBody / sporeGate / any VPS
- ❌ Trigger Zola rebuild
- ❌ Fix Forgejo repo path
- ❌ Deploy anything to production
- ❌ Restart services

---

## Action Required — sporeGate

**One command makes everything live:**

```bash
# On golgiBody (where Caddy serves detroit.primals.eco):
cd /path/to/publicRecord-detroit
git pull github main
zola build
# Caddy picks up the new public/ directory automatically
```

This deploys simultaneously:
- "Found the Leak: They Didn't Want the Flower to Wilk" (new article)
- Damages register + calculator (new analysis pages)
- damages.json + invert.json (new API endpoints)
- Graph update: 114→129 nodes, 197→215 edges
- Wilk-Moore colleague edge (formation/governance split across 7 vehicles)

### Also needed (separate task):
- Fix Forgejo repo path at git.primals.eco (returns 404)
- Signal chain automation (webhook or polling timer) — see `SIGNAL_CHAIN_REPAIR_WAVE169.md`

---

## Observation Layer Architecture

northGate/gAIa is the **observation layer** — can see the membrane, can't reach through it. This is correct architecture:

- **northGate** → observes, computes, pushes to GitHub
- **sporeGate** → deploys, builds, manages VPS fleet
- **golgiBody** → serves, routes, TLS terminates

The observation layer confirms what's live and what's stale. The deployment layer acts. The separation is the membrane.

---

*Wave 169 — October 10, 2026*
*All 5 repos pushed clean. Spore staged on GitHub. Window needs opening.*
