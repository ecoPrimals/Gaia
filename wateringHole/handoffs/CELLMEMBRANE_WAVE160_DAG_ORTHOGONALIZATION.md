# sporeGate → cellMembrane Team — Wave 160 Tasking

**Date**: Oct 1, 2026 | **Wave**: 160 | **From**: sporeGate topology
**To**: cellMembrane parallel IDE
**Priority**: P1 — publish pipeline orthogonalized, needs membrane-side fixes

---

## Context: What Wave 160 Just Completed (from sporeGate IDE)

### Ownership Cycle Killed

The `chown` ping-pong in publish hooks is eliminated. Both `50-publish` (sporePrint)
and `10-publish` (detroit) now call `sudo membrane site.publish <site>` directly.
No more ownership dance — root builds, root owns, no chown ever.

**Changed files on golgiBody:**
```
/opt/forgejo/data/repositories/ecoprimals/sporeprint.git/hooks/post-receive.d/50-publish
/opt/forgejo/data/repositories/publicrecord/detroit.git/hooks/post-receive.d/10-publish
/etc/sudoers.d/membrane-publish   (NEW — replaces git-sporeprint-chown, old membrane-publish)
```

**Removed:**
```
/etc/sudoers.d/git-sporeprint-chown   (stale Wave 158 chown rules)
```

**Current sudoers:**
```
git ALL=(root) NOPASSWD: /usr/local/bin/membrane site.publish sporeprint
git ALL=(root) NOPASSWD: /usr/local/bin/membrane site.publish detroit
```

### Event-Driven Relay (golgi → golgi-ext)

New `60-relay` hook fires after `50-publish`. Triggers golgi-ext rebuild via SSH
instead of relying on the 15-minute poll timer (now reduced to hourly fallback).

**New file:**
```
/opt/forgejo/data/repositories/ecoprimals/sporeprint.git/hooks/post-receive.d/60-relay
```

Timer on golgi-ext changed from `OnCalendar=*:0/15` to `OnCalendar=hourly`:
```
/etc/systemd/system/sporeprint-rebuild.timer   (golgi-ext)
```

### One-Way GitHub Mirror

New `70-github-mirror` hook pushes to `github.com:ecoPrimals/sporePrint.git`
from the bare repo after every publish. Background, one-way DAG (no return edge).

**New file:**
```
/opt/forgejo/data/repositories/ecoprimals/sporeprint.git/hooks/post-receive.d/70-github-mirror
```

---

## Complete sporePrint Hook DAG (as deployed)

```
30-sovereign-ci  → SKIP (sporePrint is not a primal repo)
50-publish       → sudo membrane site.publish sporeprint (root builds, ~4 min)
60-relay         → SSH golgi-ext: systemctl restart sporeprint-rebuild (background)
70-github-mirror → git push github from bare repo (background)
```

Detroit:
```
10-publish       → sudo membrane site.publish detroit (root builds, ~5s)
gitea            → Forgejo internal hook
```

---

## Task 1: Fix `membrane site.publish sporeprint` Caddy WARN

### The Problem

Every `membrane site.publish sporeprint` emits:
```
WARN publish: Caddy vhost not found — run `membrane caddy.deploy sporeprint` to provision
```

The Caddy vhost **does exist** on golgi (`sporeprint.primals.eco` block in `/etc/membrane/Caddyfile`),
but membrane's publish command can't find it — likely looking for a marker comment or config
section that doesn't match the actual Caddyfile format.

### What to Check

1. What does `membrane caddy.deploy sporeprint` actually do? Is it safe to run?
2. Does membrane look for a specific comment format (e.g., `# managed: sporeprint`) in the Caddyfile?
3. The vhost exists and works — this is a config detection issue, not a missing vhost.

### Impact

Advisory only — publish works, pages are served. But it blocks any membrane-side
auto-provisioning and generates noise in every push log.

---

## Task 2: Fix IndexNow Site Verification

### The Problem

```
[seo] indexnow: FAILED sporeprint.primals.eco: HTTP 403 —
  {"errorCode":"SiteVerificationNotCompleted","message":"Site Verification is not completed."}
```

IndexNow requires a verification file at the web root. The file exists:
```
golgi:   /opt/ecoPrimals/sporePrint/public/0CB4A351F4F113D99E0E1970B2AA29A6.txt
golgi-ext: /opt/ecoPrimals/infra/sporePrint/public/0CB4A351F4F113D99E0E1970B2AA29A6.txt
```

### What to Check

1. Is the IndexNow key file being included in zola builds, or does `zola build` overwrite it?
   Check if it's in `static/` so it persists across builds.
2. Verify the file is accessible: `curl -s https://sporeprint.primals.eco/0CB4A351F4F113D99E0E1970B2AA29A6.txt`
3. The verification key might be for Bing — check if IndexNow submission is going through
   Bing's API (api.indexnow.org) or another engine.

---

## Task 3: Create Detroit GitHub Mirror

### The Problem

The `defendDetroit/detroit` repo doesn't exist on GitHub. The `ecoPrimal` SSH key on
golgi authenticates fine (`Hi ecoPrimal!`) but the repo hasn't been created yet.

### What to Do

1. Create repo `defendDetroit/detroit` (or `ecoPrimals/detroit`) on GitHub
   - Public repo, no initial commit (mirror will push)
   - Description: "Public evidence library documenting Detroit charter school racketeering"
2. Add `70-github-mirror` hook to detroit:
   ```bash
   cat > /opt/forgejo/data/repositories/publicrecord/detroit.git/hooks/post-receive.d/70-github-mirror << 'HOOK'
   #!/bin/bash
   # 70-github-mirror — one-way Forgejo → GitHub push mirror
   # Wave 160: DAG (no return edge)
   BARE_REPO="/opt/forgejo/data/repositories/publicrecord/detroit.git"
   (
       cd "$BARE_REPO" && \
       git push --force git@github.com:defendDetroit/detroit.git refs/heads/main:refs/heads/main \
           2>&1 | logger -t "github-mirror" || \
       logger -t "github-mirror" "WARN: detroit github mirror push failed"
   ) &
   HOOK
   chmod +x /opt/forgejo/data/repositories/publicrecord/detroit.git/hooks/post-receive.d/70-github-mirror
   ```
3. Test: push to detroit, verify GitHub receives it
4. Add README.md to GitHub repo with backlinks to `https://detroit.primals.eco`

---

## Task 4: sporePrint Path Discrepancy Between Servers

### Observation

```
golgi:     /opt/ecoPrimals/sporePrint/          (checkout for membrane publish)
golgi-ext: /opt/ecoPrimals/infra/sporePrint/    (checkout for timer rebuild)
```

Two different paths, two different checkouts of the same repo. The golgi path matches
the Caddy vhost config (`root * /opt/ecoPrimals/sporePrint/public`). The golgi-ext path
is deeper (`/infra/`).

### Impact

Both work independently, but the asymmetry is a latent source of confusion. Consider
standardizing to one path on both servers, or at minimum documenting the discrepancy
in OUTER_MEMBRANE_TOPOLOGY.md.

---

## Architecture Reference: The Orthogonalized DAG

### Before (cyclic):
```
push → chown(git) → build(root) → own(root) → push → chown(git) → ∞
golgi builds independently ←→ golgi-ext builds independently (15-min drift)
```

### After (DAG):
```
push(git) ──→ sudo membrane(root) ──→ build ──→ serve (golgi)
                                        │
                                        ├──→ SSH relay ──→ golgi-ext rebuild
                                        │
                                        └──→ GitHub mirror (one-way, background)
```

No cycles. No ownership contests. Event-driven relay with hourly defense-in-depth fallback.

---

## Verification Checklist

After implementing fixes, validate:

- [ ] `membrane site.publish sporeprint` — no WARN
- [ ] `membrane site.publish detroit` — clean
- [ ] Push to sporePrint → 50-publish → 60-relay → 70-mirror all fire
- [ ] golgi-ext receives relay trigger, rebuilds within ~90s of push
- [ ] GitHub mirror shows latest commit on `ecoPrimals/sporePrint`
- [ ] IndexNow returns 200 (not 403)
- [ ] `curl -s https://sporeprint.primals.eco/0CB4A351F4F113D99E0E1970B2AA29A6.txt` returns key

---

## Task 5: Inbound Signal Receptor — Analytics Without Surveillance

### The Problem

The membrane secretes but cannot sense. It publishes pages, submits sitemaps, pings
IndexNow, pushes to GitHub — all outbound. But there is **zero inbound signal path**
for understanding what happens after secretion:

- Who visits? (human vs bot already parsed from Caddy logs, but no dashboard)
- Which pages convert to engagement? (time on page, scroll depth, return visits)
- What search queries lead people here? (GSC Performance, but 24-48hr delay)
- Is the MHC strategy working? (which hub pages cascade into which leaf pages?)

Cloudflare shows 0 because DNS is gray-cloud (DNS-only). All traffic hits golgi
directly. Cloudflare never touches it, so Cloudflare analytics are blind.

### Current Signal Sources (manual, no dashboards)

| Source | What it shows | Latency | Method |
|---|---|---|---|
| Caddy access.log | All requests, bot + human | Real-time | SSH + python parse |
| GSC Performance | Impressions, clicks, position, queries | 24-48 hrs | Manual browser |
| GSC Page Indexing | Indexed/not-indexed counts, reasons | 24-48 hrs | Manual browser |
| IndexNow response | Submission acceptance | Immediate | Push log |

### What cellMembrane Should Evolve

The membrane needs a **receptor** — an inbound signal pathway that:

1. **Parses Caddy logs continuously** (skunky-ingest already exists for skunkBat —
   extend it or create a parallel ingest for SEO/visitor signal)
2. **Separates bot signal from human signal** (bot = crawl coverage map,
   human = engagement/conversion)
3. **Feeds back into publish decisions** (which pages get priority in IndexNow
   batches, which need content improvement, which are dead ends)
4. **Exposes a dashboard** — either:
   - Self-hosted Umami/Plausible (privacy-respecting, no cookies, GDPR-compliant)
   - Or a membrane-native endpoint that serves parsed log summaries
   - NOT Google Analytics or any third-party that exfiltrates visitor data

### The Anderson Analogy

The membrane currently has **LuxI** (autoinducer synthase — it secretes signals)
but no **LuxR** (receptor — it cannot detect what bound). Without LuxR, you cannot
do affinity maturation: iterative improvement of the signal based on response.

The publish pipeline is the secretory pathway:
```
content → zola build → Caddy serves → sitemap → IndexNow → GSC
                                                              ↓
                                                        [BLACK HOLE]
                                                    no signal comes back
```

The receptor would close the loop:
```
content → zola build → Caddy serves → sitemap → IndexNow → GSC
   ↑                        ↓                                ↓
   └── membrane.seo.adapt ← receptor ← Caddy logs ← crawler visits
```

### Constraints

- **No third-party analytics** on detroit. This is a public evidence site documenting
  racketeering. Visitor privacy is non-negotiable.
- **Self-hosted or log-based only**. Caddy logs are the canonical source of truth.
- **skunky-ingest** already runs on golgi (`skunky-ingest.service — Caddy JSON log
  tailer → skunkBat baseline.observe`). Can it be extended to emit SEO/visitor
  signal, or does it need a parallel ingest?

---

## Verification Checklist

After implementing fixes, validate:

- [ ] `membrane site.publish sporeprint` — no WARN
- [ ] `membrane site.publish detroit` — clean
- [ ] Push to sporePrint → 50-publish → 60-relay → 70-mirror all fire
- [ ] golgi-ext receives relay trigger, rebuilds within ~90s of push
- [ ] GitHub mirror shows latest commit on `ecoPrimals/sporePrint`
- [ ] IndexNow returns 200 (not 403) for sporePrint
- [ ] Inbound signal receptor emitting bot/human separation
- [ ] `curl -s https://sporeprint.primals.eco/0CB4A351F4F113D99E0E1970B2AA29A6.txt` returns key

---

*Wave 160. The cyclic ownership graph is now a DAG. The polling relay is now event-driven.
The GitHub mirror is one-way. The membrane secretes but cannot sense — Task 5 adds the
LuxR receptor. cellMembrane owns Tasks 1-5 above.*
