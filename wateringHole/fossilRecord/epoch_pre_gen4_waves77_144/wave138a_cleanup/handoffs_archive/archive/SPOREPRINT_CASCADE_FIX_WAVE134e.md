# sporePrint Cascade Fix — Wave 134e

**Date**: Jul 9, 2026 | **From**: eastGate overwatch | **To**: golgi/sporeGate team
**Priority**: P0 — site is serving stale build since DNS cutover

---

## Problem

DNS for `primals.eco` now points to golgi's Caddy (sovereign — correct). But golgi has no automated pipeline to rebuild sporePrint after a push. The GitHub Pages deploy still runs (trailing shadow), but DNS no longer points there.

Result: golgi serves a stale static export. 259 pages exist in the repo; ~40 are actually served. Philosophy, story, thesis, sharing-the-pen — all return the homepage via catch-all fallback.

---

## Root Cause

The primal cascade pipeline (Forgejo → sporeGate → cargo build → depot → golgi serves binaries) was wired. The **static site** cascade was never wired. When DNS cut over from GitHub Pages to golgi, the site lost its build trigger.

---

## Fix: Forgejo post-receive hook

### 1. Install Zola on golgi

```bash
# Single static binary, no dependencies
curl -sL https://github.com/getzola/zola/releases/download/v0.22.1/zola-v0.22.1-x86_64-unknown-linux-gnu.tar.gz | tar xz
sudo mv zola /usr/local/bin/
zola --version  # should print 0.22.1
```

### 2. Create a bare-repo hook or systemd timer

**Option A — Forgejo webhook (preferred if Forgejo supports it):**

In Forgejo UI → `ecoPrimals/sporePrint` → Settings → Webhooks → Add webhook (Forgejo type):
- Target URL: `http://127.0.0.1:9876/hooks/sporeprint-rebuild` (local webhook receiver)
- Trigger: Push events on `main` branch only

Then create a lightweight webhook receiver (or use a systemd path unit on the bare repo).

**Option B — git post-receive hook (simplest):**

Find the bare repo on golgi (likely `/data/forgejo/repositories/ecoPrimals/sporePrint.git/`) and add:

```bash
#!/bin/bash
# /data/forgejo/repositories/ecoPrimals/sporePrint.git/hooks/post-receive.d/rebuild-site.sh

WORK_DIR="/srv/sporePrint-build"
SITE_ROOT="/srv/primals.eco"
BRANCH="main"

while read oldrev newrev refname; do
  if [[ "$refname" == "refs/heads/$BRANCH" ]]; then
    echo "[sporePrint cascade] Rebuilding site from $newrev..."

    # Update working copy
    if [[ ! -d "$WORK_DIR" ]]; then
      git clone /data/forgejo/repositories/ecoPrimals/sporePrint.git "$WORK_DIR"
    fi
    cd "$WORK_DIR"
    git fetch origin
    git reset --hard "origin/$BRANCH"

    # Build
    zola build --output-dir "$SITE_ROOT"

    echo "[sporePrint cascade] Done. $(find $SITE_ROOT -name 'index.html' | wc -l) pages deployed."
  fi
done
```

Make executable:
```bash
chmod +x /data/forgejo/repositories/ecoPrimals/sporePrint.git/hooks/post-receive.d/rebuild-site.sh
```

### 3. Point Caddy file_server at the build output

In the Caddy config for `primals.eco`:

```caddy
primals.eco {
    root * /srv/primals.eco
    file_server
    encode gzip

    # Return proper 404 — do NOT fallback to index.html
    handle_errors {
        respond "{err.status_code} {err.status_text}" {err.status_code}
    }
}
```

**Remove** any `try_files {path} /index.html` directive. Static sites should 404 on missing paths, not silently serve the homepage.

### 4. Trigger initial build manually

```bash
cd /srv/sporePrint-build
git pull origin main
zola build --output-dir /srv/primals.eco
```

Verify:
```bash
curl -s https://primals.eco/philosophy/the-city-of-omelas/ | head -1
# Should NOT be the homepage. Should start with the essay title.
```

---

## Verification Checklist

- [ ] `zola --version` works on golgi
- [ ] Post-receive hook fires on push
- [ ] `primals.eco/philosophy/the-city-of-omelas/` returns essay content (not homepage)
- [ ] `primals.eco/story/i-dont-know-rust/` returns story content
- [ ] `primals.eco/thesis/` returns thesis index
- [ ] Missing paths return 404 (not homepage)
- [ ] Total deployed pages ≥ 259

---

## Also fix: Caddy catch-all

The current config has a fallback that serves `index.html` for unknown paths. This:
- Hides deployment failures (broken links look like the homepage)
- Creates duplicate content for search engines
- Makes it impossible to detect missing pages

Remove it. Let 404 be 404.

---

## Post-fix: cascade flow for sporePrint

```
eastGate pushes to Forgejo (ssh://git@git.primals.eco:2222)
  → post-receive hook fires on golgi
  → zola build → /srv/primals.eco/
  → Caddy serves immediately (no restart needed, file_server is live)
  → GitHub Pages continues as trailing shadow (deploy.yml still runs)
```

End-to-end latency: <10 seconds from push to live.

---

## Context

- Local `main` builds 259 pages with `zola build` (2.1s)
- Forgejo and GitHub both at commit `a53eea0`
- Philosophy (12 essays), Story (3 essays), Thesis (16 chapters), Bibliography all exist in HEAD
- The GitHub Pages trailing shadow is still serving the correct build — it just doesn't get traffic since DNS cutover
