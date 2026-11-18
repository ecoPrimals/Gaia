# cellMembrane Handoff — Wave 161: Observatory Receptor Integration

**From**: sporeGate hardware (site infrastructure)
**To**: cellMembrane team (publish pipeline + receptor persistence)
**Date**: 2026-10-02
**Depends on**: Wave 160.5 (`627b2f4` — `seo.receptor` deployed and verified)

---

## Context

The `/observatory/` page is live on sporePrint. It's a static Zola page with
vanilla JS that reads `/observatory/data.json` and renders:

- Summary cards (total requests, humans, bots, crawl coverage)
- Per-host breakdown (sporePrint + detroit)
- Stacked bar charts showing visitor classification per page
- Full sortable page table (expandable)
- Trend history table (future — reads `data.history[]` array)

**No cookies. No tracking pixels. No third-party analytics.**
The page reads its own server-generated JSON — the receptor's output.

A seed `data.json` was generated from today's receptor output and committed
to `sporePrint/static/observatory/data.json`.

---

## Task 1: Receptor Snapshot in Publish Pipeline

**File**: `crates/membrane-shadow/src/webhook/pipeline.rs`
**Where**: After the successful zola build, before IndexNow/GSC

Add a receptor snapshot step to the sporePrint publish pipeline:

```rust
// After zola build succeeds, before SEO steps:
// Run receptor analysis and write snapshot to site static dir
if site.host == "sporeprint.primals.eco" {
    match seo::receptor::analyze(&config, 50_000).await {
        Ok(report) => {
            let json = serde_json::to_string_pretty(&report)?;
            let snapshot_path = format!("{}/static/observatory/data.json", site.worktree);
            std::fs::write(&snapshot_path, &json)?;
            info!(path = %snapshot_path, "receptor snapshot written to observatory");
        }
        Err(e) => {
            warn!(error = %e, "receptor snapshot failed — observatory data stale");
        }
    }
}
```

**Key decisions**:
- Only run for sporePrint (detroit shouldn't expose analytics publicly)
- Use `50_000` lines for a good time window (~24h at current traffic)
- Non-fatal — if receptor fails, publish continues with stale data
- Write to `static/observatory/data.json` so Zola includes it in the build
- Must run AFTER zola build (data.json goes to `public/`, not built by Zola)

**Wait** — actually, since Zola copies `static/` to `public/`, the receptor
should write to `{worktree}/static/observatory/data.json` BEFORE `zola build`,
OR write directly to `{worktree}/public/observatory/data.json` AFTER the build.

Recommended: **Write to `public/observatory/data.json` after the build.**
This avoids the snapshot being stale in the git-tracked static dir and keeps
the receptor output as an ephemeral build artifact.

```rust
// After zola build, before SEO:
let observatory_path = format!("{}/public/observatory/data.json", site.worktree);
```

### Git-tracked seed file

The seed `static/observatory/data.json` serves as fallback data if the
receptor snapshot step hasn't run yet. The publish-time snapshot in `public/`
will override it (Zola copies static → public, then our post-build writes
over it).

---

## Task 2: Historical Trend Accumulation

**File**: New — `crates/membrane-shadow/src/seo/observatory.rs` or inline in pipeline

After writing the snapshot, append a daily summary to a JSONL file:

```rust
// /opt/ecoPrimals/sporePrint/observatory-history.jsonl
// One line per day, append-only
#[derive(Serialize)]
struct DailyDigest {
    generated_at: u64,
    date: String, // "2026-10-02"
    hosts: BTreeMap<String, HostDigest>,
}

#[derive(Serialize)]
struct HostDigest {
    total_requests: u64,
    total_human: u64,
    total_search_bot: u64,
    unique_paths: u64,
    crawl_coverage: u64,
}
```

On publish, read the JSONL, check if today's date already has an entry:
- If yes, update it (replace the line)
- If no, append a new line

Then inject the history into `data.json` as a `history` array.
The observatory JS already handles this — it renders a trend table when
`data.history` exists.

---

## Task 3: Receptor for Detroit (Internal Only)

Detroit's receptor data should NOT be published to detroit.primals.eco.
But it SHOULD be included in sporePrint's observatory (we're already doing
this — the receptor analyzes all hosts in the Caddy log).

If we want detroit-specific analysis without exposing it publicly, the
receptor already filters by `--host`. The observatory page shows both
hosts because the data.json contains both.

**Decision needed**: Should we strip detroit data from the public JSON?
Or is showing "detroit.primals.eco gets X visits from search bots" acceptable?
(It doesn't reveal WHO visits — only aggregate counts.)

Recommended: **Keep both hosts in the observatory.** The aggregate counts
don't compromise visitor privacy. Showing that search bots crawl detroit
actually reinforces that the evidence site is being indexed.

---

## Verification Checklist

- [ ] `membrane site.publish sporeprint` writes `public/observatory/data.json`
- [ ] Observatory page at `sporeprint.primals.eco/observatory/` renders data
- [ ] `data.json` contains both hosts (sporeprint + detroit)
- [ ] No visitor IP addresses in the JSON (confirm: they're already excluded)
- [ ] Non-fatal: if receptor SSH fails, publish still succeeds
- [ ] After 7 days: `data.history` array has 7 entries, trend table renders

---

## Files Changed (Site Side — Already Done)

| File | Purpose |
|------|---------|
| `sporePrint/content/observatory/_index.md` | Zola content page — description, methodology |
| `sporePrint/templates/observatory.html` | Full template — cards, bar charts, table, trend, CSS, JS |
| `sporePrint/static/observatory/data.json` | Seed data from live receptor (42KB, both hosts) |

## Files to Change (cellMembrane Side)

| File | Change |
|------|--------|
| `crates/membrane-shadow/src/webhook/pipeline.rs` | Add receptor snapshot step after zola build |
| `crates/membrane-shadow/src/seo/mod.rs` or new file | Daily digest accumulation logic |

---

## Schema Reference

The observatory JS expects this structure (which is exactly `ReceptorReport`'s
serde output, plus an optional `history` array):

```json
{
  "generated_at": 1790973546,
  "hosts": {
    "sporeprint.primals.eco": {
      "host": "sporeprint.primals.eco",
      "pages": {
        "/": {
          "path": "/",
          "total_hits": 6,
          "human_hits": 6,
          "search_bot_hits": 0,
          "ai_bot_hits": 0,
          "social_bot_hits": 0,
          "other_bot_hits": 0,
          "ok_count": 6,
          "not_found_count": 0,
          "redirect_count": 0,
          "avg_duration_ms": 3.14
        }
      },
      "total_requests": 142,
      "total_human": 65,
      "total_search_bot": 43,
      "crawl_coverage": 27,
      "unique_paths": 68
    }
  },
  "lines_processed": 216,
  "parse_errors": 0,
  "window_start": 1790950000.0,
  "window_end": 1790973546.0,
  "history": [
    {
      "generated_at": 1790887146,
      "date": "2026-10-01",
      "hosts": {
        "sporeprint.primals.eco": {
          "total_requests": 95,
          "total_human": 40,
          "total_search_bot": 30,
          "unique_paths": 45,
          "crawl_coverage": 18
        }
      }
    }
  ]
}
```
