# AAR: detroit.primals.eco Live Probe — Wave 175
## Agent Observation: What's Live, What's Stale, What's Happening
## Oct 11, 2026 15:59 ET | northGate observation layer

---

## HEADLINE FINDING

**853 clones, 280 unique entities in 14 days.** The repo is being
pulled at scale. The clone rate is ACCELERATING — Oct 9-10 alone:
323 clones, 154 unique entities.

This is NOT reflected in the view count (5 views, 3 unique). Views
= people browsing the GitHub page. Clones = people/systems pulling
the ENTIRE DATASET. Someone (or many someones) is pulling the evidence.

---

## TRAFFIC DATA

### GitHub Views (people browsing github.com page)

| Date | Views | Unique |
|------|-------|--------|
| Sep 27 | 1 | 1 |
| Sep 28 | 2 | 2 |
| Oct 3 | 1 | 1 |
| Oct 8 | 1 | 1 |
| **Total** | **5** | **3** |

Referrer: github.com (2 views, 1 unique). Popular paths: repo overview (4/3), issues (1/1).

### GitHub Clones (entities pulling the repo)

| Date | Clones | Unique | Trend |
|------|--------|--------|-------|
| Sep 27 | 1 | 1 | baseline |
| Sep 28 | 48 | 20 | ▲ burst |
| Sep 29 | 3 | 2 | ▼ |
| Sep 30 | 36 | 18 | ▲ |
| Oct 1 | 64 | 32 | ▲▲ |
| Oct 2 | 27 | 13 | ▼ |
| Oct 3 | 29 | 15 | ─ |
| Oct 4 | 8 | 4 | ▼▼ |
| Oct 5 | 126 | 17 | ▲▲ (low unique = bot burst?) |
| Oct 6 | 0 | 0 | gap |
| Oct 7 | 79 | 39 | ▲▲ |
| Oct 8 | 109 | 52 | ▲▲▲ |
| Oct 9 | **165** | **81** | ▲▲▲▲ PEAK |
| Oct 10 | **158** | **73** | ▲▲▲▲ sustained |
| **Total** | **853** | **280** | **ACCELERATING** |

### Analysis of Clone Pattern

The clone traffic shows three distinct patterns:

**1. Bot bursts (Oct 5: 126 clones, only 17 unique)**
High clone count but low unique = same entities pulling multiple times.
Likely automated scrapers, CI systems, or mirror bots. The 126/17 ratio
(7.4 clones per unique) suggests programmatic access.

**2. Organic growth (Oct 7-10: climbing unique counts)**
Oct 7: 39 unique → Oct 8: 52 → Oct 9: 81 → Oct 10: 73.
Unique counts nearly DOUBLED between Oct 7 and Oct 9. This is new
entities discovering the repo each day. Not bots — new eyeballs.

**3. The Oct 9 peak (165 clones, 81 unique)**
81 unique entities pulled the repo on a single day. That's significant.
Something drove discovery on Oct 9. Possible triggers:
- Google Search Console indexing kicking in (120 URLs submitted)
- Social sharing / link posting we can't see
- A news article or social post referencing the repo
- The Bing IndexNow notification propagating
- Automated research tools (AI agents) discovering the dataset

**Note**: We can't distinguish human clones from bot clones in this
data. GitHub doesn't expose user-agent for clone traffic.

---

## SITE STATE

### graph.json: ✅ CURRENT

| Metric | graph.json | Site HTML |
|--------|-----------|-----------|
| Nodes | **129** | 91 (stale) |
| Edges | **215** | 140 (stale) |
| Node types | 66 actors, 48 entities, 15 institutions | — |

graph.json is serving the LATEST data (129/215). The static JSON
file was pushed to the repo and is serving from Caddy directly.
Anyone pulling graph.json gets current data.

### Site HTML: 🔴 STALE

The Zola-rendered HTML pages have NOT been rebuilt. The homepage
still references "91 nodes and 140 documented connections." The
analysis pages reference old counts.

**Impact**: Users reading the site see old numbers. Users pulling
graph.json get current data. This creates a perception gap —
the narrative says 91 but the data says 129.

### New Pages: ❌ NOT LIVE

| Page | URL | Status |
|------|-----|--------|
| Epitope Table | `/analysis/epitope-table/` | Falls through to homepage |
| Knowledge Commons | `/analysis/the-knowledge-commons/` | Falls through to homepage |

Both committed and pushed to GitHub. Both need `zola build` to
render into HTML. Currently 404-ing (Caddy fallback serves homepage).

### Sitemap: ❌ 500 ERROR

`/sitemap.xml` returns 500. Known issue from Wave 158 notes.
May have regressed or may not have been rebuilt since fix.

### Existing Analysis Pages: ✅ WORKING

The analysis index (`/analysis/`) is live and serving 20+ articles.
All existing analysis pages appear functional. The content is
comprehensive — RICO pattern, Anderson Localization, Dykema
Chronology, Dark Money Pipeline, Damages Calculator, and more.

The investigation platform features are active:
- ✅ Discovery journal (localStorage, "Your nodes 0/91")
- ✅ 6 analysis lenses
- ✅ BLAKE3 content integrity
- ✅ No cookies/tracking confirmed
- ✅ Nov 3 election notice (Judge Miller)
- ✅ Community progress aggregation (anonymous)

---

## ASSESSMENT

### What's working better than expected:
- **853 clones in 14 days with accelerating unique count** — the data
  is being pulled. By who, we can't tell. But 280 unique entities is
  NOT nothing. The seed germinated.
- **graph.json is current** at 129/215 — anyone consuming the API gets
  fresh data even though the HTML is stale.
- **20+ analysis articles live** — the evidence library is comprehensive.
- **Investigation UX is functional** — discovery journal, lenses, integrity.

### What needs fixing:
1. **Zola rebuild** — `git pull && zola build` on golgi. Unblocks new pages
   AND updates the HTML counts from 91→129. HIGHEST PRIORITY.
2. **Sitemap 500** — blocks search engine discovery of new pages.
3. **Homepage count** — "91 nodes" is wrong. graph.json says 129.
4. **New pages** — Epitope Table + Knowledge Commons committed but not built.

### What we can't see (and shouldn't):
- WHO is cloning (no user-agent data in GitHub traffic API)
- WHAT they do with it (no tracking, by design)
- WHETHER humans are reading the analysis pages (no Caddy logs from here)
- The actual site traffic on detroit.primals.eco (only GitHub-side visible)

### Open questions for sporeGate team:
1. Can you check Caddy access logs on golgi? They would show:
   - Actual visitor count to detroit.primals.eco (not just GitHub)
   - Which pages are most visited
   - Whether the graph visualization is being used
   - Whether /analysis/ pages are getting traffic
2. What triggered the Oct 9 spike? Any social posts, news articles,
   or referrals we should know about?
3. Is the Forgejo post-receive hook running? Or is the site only
   updated by manual `zola build`?

---

## RECOMMENDATIONS

| Priority | Action | Impact |
|----------|--------|--------|
| P0 | **Rebuild Zola on golgi** | Unblocks 2 new pages, fixes stale counts, fixes sitemap |
| P1 | **Check Caddy logs** for detroit.primals.eco traffic | Shows actual visitor behavior |
| P2 | **Investigate Oct 9-10 clone spike** | 81 unique entities in one day — what triggered it? |
| P3 | **Update homepage node count** | 91→129 in the Zola template |
| P4 | **Google Search Console check** | Are the 120 submitted URLs indexed? |

---

*853 clones. 280 unique entities. Accelerating.*
*graph.json is current. HTML is stale. New pages not built.*
*The data is out there. We just can't see who has it.*
*That's privacy_is_holographic. It works both ways.*

---
