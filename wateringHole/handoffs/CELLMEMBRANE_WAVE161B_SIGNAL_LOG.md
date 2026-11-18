# cellMembrane Handoff — Wave 161b: Dual Signal Log for skunkBat

**From**: sporeGate hardware
**To**: cellMembrane team
**Date**: 2026-10-03
**Depends on**: Wave 161 (`7b0742d` — observatory + receptor deployed)

---

## Context

The membrane now has both halves of the quorum loop:
- **LuxI (outbound)**: `site.publish` → IndexNow, GSC sitemaps, URL notifications
- **LuxR (inbound)**: `seo.receptor` → Caddy log analysis, bot/human classification

Both signals need to be recorded as long-term datapoints for skunkBat anomaly
detection and trend analysis. A signal log has been initialized at:

```
/var/log/membrane/signal.jsonl
```

Currently seeded with manual entries. Needs automated integration.

---

## Task 1: Log Publish Events (LuxI)

**File**: `crates/membrane-shadow/src/webhook/pipeline.rs`
**Where**: At the end of each successful publish

After the publish pipeline completes, append a JSON line:

```json
{
  "type": "publish",
  "ts": 1790980000,
  "site": "detroit",
  "pages": 233,
  "indexnow_urls": 232,
  "indexnow_status": 200,
  "gsc_submitted": true,
  "url_notify_count": 50,
  "url_notify_quota_exhausted": false,
  "observatory_snapshot": true,
  "observatory_lines": 275
}
```

Write to `/var/log/membrane/signal.jsonl` (append, one line per event).
Non-fatal — if write fails, publish still succeeds.

---

## Task 2: Log Receptor Snapshots (LuxR)

**File**: `crates/membrane-shadow/src/seo/observatory.rs`
**Where**: After writing the observatory snapshot

After generating the receptor snapshot (in the observatory step), also
append a summary to the signal log:

```json
{
  "type": "receptor",
  "ts": 1790980000,
  "date": "2026-10-03",
  "hosts": {
    "detroit.primals.eco": {
      "total_requests": 54,
      "total_human": 4,
      "total_search_bot": 35,
      "unique_paths": 27,
      "crawl_coverage": 15
    },
    "sporeprint.primals.eco": {
      "total_requests": 31,
      "total_human": 12,
      "total_search_bot": 6,
      "unique_paths": 26,
      "crawl_coverage": 3
    }
  }
}
```

This is essentially the same as `observatory-history.jsonl` but in the
unified signal log format.

---

## Task 3: skunkBat Integration Path

The signal log at `/var/log/membrane/signal.jsonl` is a JSONL file that
skunkBat's `baseline.observe` can tail. When skunky-ingest exits dry-run
mode, it should also tail this file (or a rotated version) alongside the
Caddy access log.

**Key anomaly signals skunkBat should watch for**:
- Sudden drop in `total_search_bot` (crawlers stopped coming)
- Spike in `total_human` after a publish (Reddit repeater effect)
- `indexnow_status` != 200 (IndexNow key invalidated)
- `crawl_coverage` regression (pages dropping out of bot reach)
- `url_notify_quota_exhausted` becoming persistent (need to optimize)

---

## Signal Log Format

```
/var/log/membrane/signal.jsonl
```

- One JSON object per line
- `type` field: `"publish"` | `"receptor"` | `"gsc_inspection"` | `"bloom_check"`
- `ts` field: Unix epoch seconds
- Append-only
- No rotation needed yet (will be small for months)

---

## Task 4: Evidence Depot Symlinks (detroit post-build)

**Operational fix applied 2026-10-03**: The detroit Caddyfile had a broken
`handle /evidence/*` route that pointed to a separate evidence depot directory
(`/opt/ecoPrimals/detroit/evidence/`), preventing Zola evidence pages from
being served. Fixed by removing the separate handler and symlinking depot
files into `public/evidence/`.

**Post-build step needed**: After each detroit `zola build`, recreate symlinks:

```bash
# After zola build for detroit, symlink depot files into public/evidence/
for f in /opt/ecoPrimals/detroit/evidence/*; do
  name=$(basename "$f")
  target="/opt/ecoPrimals/detroit/public/evidence/$name"
  [ ! -e "$target" ] && [ "$name" != "README.md" ] && ln -sf "$f" "$target"
done
```

This ensures raw evidence files (PDFs, braids, FOIA docs) remain accessible
at `/evidence/filename.pdf` alongside the Zola-generated evidence section pages.

---

## Verification

- [ ] `site.publish` appends a `publish` event to signal.jsonl
- [ ] Observatory step appends a `receptor` event to signal.jsonl
- [ ] Signal log grows by 2 lines per sporePrint publish (1 publish + 1 receptor)
- [ ] Signal log grows by 1 line per detroit publish (publish only, no receptor)
- [ ] File permissions allow both root (membrane) and git (hooks) to append
- [ ] Detroit post-build recreates evidence depot symlinks
