# cellMembrane Handoff — Wave 162: Signal Depth & Correlation Metadata

**From**: sporeGate hardware
**To**: cellMembrane team
**Date**: 2026-10-03
**Depends on**: Wave 161b (`03e6c64` — dual signal log)
**Trigger**: Northgate requested email→arrival correlation. We couldn't answer
because the receptor doesn't track the metadata needed.

---

## Context — What We Learned Today

Northgate sent emails to 15 recipients (state officials, press) at known
timestamps, then asked: "Did humans arrive on the pages we linked?"

We couldn't answer because:

1. **Log rotation destroyed the window** — Caddy reloads triggered rotation,
   the 3–7:45 PM data vanished. Receptor only reads `access.log`, not `.1`.
2. **No outbound event log** — Email sends are LuxI signals but aren't recorded.
   The signal log only captures `publish` and `receptor` events, not outreach.
3. **No session detection** — We see individual page hits but can't tell if
   3 hits from the same UA in 5 minutes is one person navigating or three.
4. **Observatory snapshot timing** — Daily snapshot was taken at noon, before
   all emails went out. Missed the entire afternoon signal window.
5. **No propagation delay metric** — We can't measure "email sent at T,
   first human arrived at T+Δ" because there's no T to compare against.

---

## Task 1: Multi-File Receptor

**Current**: `seo.receptor` reads only `access.log`
**Needed**: Read `access.log` + `access.log.1` (and optionally `.2.gz`)

Add a `--include-rotated` flag (or make it default) that reads across
rotation boundaries. The receptor already takes `--lines N` — extend to
mean "last N lines across all available log files."

This prevents data loss during Caddy reloads and gives full-day coverage
regardless of when rotation happens.

### Log rotation schedule
- Caddy rotates at size threshold (~50 MB) or at `01:00 UTC`
- `access.log.1` = previous rotation (uncompressed)
- `access.log.2.gz` = rotation before that (gzip)
- Caddy `reload` does NOT truncate, but can trigger rotation if size threshold hit

---

## Task 2: Outreach Events (LuxI expansion)

The signal log currently records:
- `publish` — site deployed, IndexNow fired
- `receptor` — inbound traffic snapshot

**Add**:
- `outreach` — manual signal emission (email, Reddit post, press contact)

```json
{
  "type": "outreach",
  "ts": 1791060000,
  "channel": "email",
  "recipients": 15,
  "pages_linked": [
    "/evidence/tcr-22-12/",
    "/network/institutional/tcr-22-12-enablers/",
    "/analysis/rico-pattern/"
  ],
  "note": "Belle Isle nuclear email — state officials + press"
}
```

This could be a membrane subcommand:
```bash
membrane signal.emit --channel email --recipients 15 \
  --pages /evidence/tcr-22-12/ /network/institutional/tcr-22-12-enablers/ \
  --note "Belle Isle nuclear email"
```

Or a simpler append-only CLI:
```bash
membrane signal.log outreach email 15 "Belle Isle nuclear email"
```

The key: outreach events get timestamps in `signal.jsonl` so the receptor
can compute propagation delay (outreach.ts → first human arrival on linked page).

---

## Task 3: Behavioral Classification (beyond UA string matching)

**Current**: Classification is purely UA keyword matching:
  - Has "googlebot" → SearchBot
  - Has "gptbot" → AIBot
  - Has "bot/crawl/spider" → GenericBot
  - Everything else → Human

**Problem**: Credential scanners, scraper bots, and automated recon tools use
clean browser UA strings (e.g. `Chrome/152.0.0.0`) specifically to evade UA
detection. The receptor currently classifies these as "Human" — inflating
human counts and polluting signal data.

**Example from Oct 4, 6 AM**: One scanner hit 28 dotfiles (`/.env`, `/.aws/credentials`,
`/.env.backup`, `/.env.prod`, etc.) in 30 seconds. Receptor reported 28 "human"
visitors. Actual humans: 0.

### Classification taxonomy (replaces binary human/bot)

```
Human           — Real person reading content (navigates pages, reads evidence)
AgenticHuman    — Human using automated tools (API clients, scripts, research tools)
SearchBot       — Search engine crawler (Googlebot, Bingbot, etc.)
AIBot           — AI training/inference crawler (GPTBot, ClaudeBot, Bytespider)
SocialBot       — Link preview generator (Twitterbot, Discordbot)
ScraperBot      — Automated reconnaissance/scraping (credential scanners, vuln probes)
GenericBot      — Everything else with bot-like behavior
```

### Behavioral signals (used WITH UA, not instead of)

| Signal | Human | ScraperBot |
|--------|-------|------------|
| Hits dotfiles (`.env`, `.aws`, `.git`, `wp-admin`) | Never | Always |
| Hits 10+ pages in <60 seconds | Rare | Common |
| Navigates section → child → sibling | Common | Never |
| Requests only HTML (no CSS/JS/images) | Rare | Common |
| Hits sequential enumeration patterns | Never | Common |
| Reads evidence → contact → back to evidence | Common | Never |

### Implementation approach

1. **Path-based instant classification**: Any hit to a known probe path
   (`/.env*`, `/.aws/*`, `/.git/*`, `/wp-*`, `/admin*`, `/xmlrpc.php`,
   `/actuator/*`, `/.well-known/security.txt` probe patterns) →
   immediately classify as `ScraperBot` regardless of UA.

2. **Session-based reclassification**: Group hits by UA within 30-min
   window. If a "Human" session shows bot-like patterns (see table above),
   reclassify the entire session as `ScraperBot` or `AgenticHuman`.

3. **Velocity check**: >5 page hits in <10 seconds from same UA →
   not human. Humans read.

### Why this matters for skunkBat

skunkBat's baseline.observe needs clean signal data. If "human" counts
include credential scanners, the anomaly detector will learn a false
baseline and miss real human traffic spikes (the actual signal we care about).
The classification must be provably correct: a "human" in the signal log
must actually be a human reading content, or the entire quorum sensing
measurement is compromised.

## Task 4: Session Detection in Receptor

**Current**: Each log line is independent — 3 hits from the same UA are 3 separate events.
**Needed**: Group hits into sessions (same UA within a time window = one visitor navigating).

A session is:
- Same User-Agent string
- Hits within 30-minute window
- Ordered by timestamp

This gives:
- **Session count** — actual distinct visitors (not hit count)
- **Navigation depth** — pages per session (1 = bounce, 3+ = deep reader)
- **Entry page** — first page in session (correlates to which link was clicked)
- **Reading path** — sequence of pages visited (reveals investigation behavior)

### Privacy constraint
- NO IP addresses stored or logged (receptor already strips these)
- Session grouping uses UA string only (coarse — different people with same
  browser version merge, but that's acceptable for signal measurement)
- The question is "did a human navigate deep?" not "who is this person?"

---

## Task 5: Receptor Snapshot Scheduling

**Current**: Observatory snapshot runs only during sporePrint publish pipeline.
**Issue**: If no sporePrint push happens, no snapshot is taken. Also, snapshot
timing doesn't align with outreach windows.

**Options** (pick one):
1. **Cron-based**: Run `membrane seo.receptor` every 6 hours, append to signal.jsonl
2. **Event-triggered**: After each `signal.emit` outreach event, schedule a
   receptor snapshot 1h and 4h later to capture the arrival wave
3. **Both**: Cron baseline + event-triggered correlation windows

Option 2 is the most interesting — it directly answers "did the signal propagate?"

---

## Task 6: Propagation Delay Metric

With Tasks 2–4 in place, compute:

```
propagation_delay = first_human_arrival_on_linked_page - outreach_timestamp
```

For each outreach event, the receptor can report:
- **T+0**: Outreach sent
- **T+Δ₁**: First human arrival on any linked page
- **T+Δ₂**: First search bot arrival on any linked page
- **Activation rate**: What fraction of linked pages received human visits within 24h?
- **Depth rate**: Of arriving humans, what fraction navigated beyond the entry page?

This is the **quorum sensing measurement** — did the signal reach threshold?
The sporePrint publication would present this as empirical data on oversight
signal propagation.

---

## Schema Updates

### signal.jsonl event types (after this wave)

| Type | Source | Fields |
|------|--------|--------|
| `publish` | pipeline.rs step 6 | site, pages, indexnow_urls, indexnow_status, gsc_submitted, url_notify_count |
| `receptor` | observatory.rs | date, hosts{total_requests, total_human, total_search_bot, ...} |
| `outreach` | signal.emit CLI | channel, recipients, pages_linked, note |
| `correlation` | receptor post-outreach | outreach_ref, propagation_delay_s, pages_activated, sessions, depth_avg |

### ReceptorReport additions

```rust
pub struct Session {
    pub ua_hash: String,        // SHA256 of UA string (not stored raw)
    pub pages: Vec<String>,     // ordered navigation path
    pub entry_page: String,     // first page hit
    pub duration_s: u64,        // last hit - first hit
    pub classification: String, // Human, SearchBot, etc.
}
```

---

## Task 7: skunky-ingest Integration

**Current state**: `skunky-ingest` (skunkBat primal crate) runs on golgi in
`--dry-run` mode. Binary on disk is deleted (stale — process running from
memory since Jul 12). It tails Caddy access.log, aggregates per-IP metrics
(request_rate, error_rate, path_diversity), and pushes `baseline.observe`
JSON-RPC to skunkBat TCP 9750.

**Key discovery**: skunky-ingest already deserializes User-Agent headers with
`Phase 2: scanner fingerprinting` comments in `caddy.rs` — the behavioral
classification from Wave 162b (`classify_request`) IS Phase 2.

### Integration path

Two options (not mutually exclusive):

**Option A — skunky-ingest uses receptor classification**

Import `classify_request()` from membrane-shadow into skunky-ingest (or
duplicate the logic). Each LogEntry gets classified before aggregation.
The `ObservationPayload` gains a `visitor_class` field so skunkBat can
build separate baselines per class:

```rust
pub struct ObservationPayload {
    pub visitor_class: String,  // "human", "search_bot", "scraper_bot", etc.
    pub connection_rate: f64,
    pub traffic_volume: u64,
    // ... existing fields
}
```

skunkBat then maintains per-class anomaly baselines:
- Human baseline (should be low, steady, with diurnal pattern)
- SearchBot baseline (should be bursty, high volume during crawl waves)
- ScraperBot baseline (spiky, probe-heavy, anomalous by definition)

A spike in Human traffic after an outreach event = signal propagation.
A spike in ScraperBot = attack surface probing (different alert).

**Option B — skunky-ingest also tails signal.jsonl**

In addition to Caddy logs, tail `/var/log/membrane/signal.jsonl` and
convert each signal event into a skunkBat observation. This gives skunkBat
awareness of the publish cycle, outreach events, and receptor snapshots.

### Immediate steps

1. Rebuild skunky-ingest with current skunkBat source
2. Deploy new binary to `/opt/membrane/skunky-ingest`
3. Restart `skunky-ingest.service` (still `--dry-run` until skunkBat is live)
4. When ready to go live: remove `--dry-run`, ensure skunkBat listens on 9750

---

## Verification

- [ ] `seo.receptor --include-rotated` reads across log rotation boundaries
- [ ] `signal.emit` appends outreach events to signal.jsonl
- [ ] Probe paths (`/.env*`, `/.aws/*`, etc.) classified as ScraperBot, not Human
- [ ] Velocity check: >5 hits in <10s from same UA → reclassified as bot
- [ ] Session grouping: same UA within 30min = one session with depth + path
- [ ] Receptor groups hits into sessions (same UA within 30min window)
- [ ] Observatory snapshots can run on schedule (not just during publish)
- [ ] Propagation delay computed when outreach events have matching receptor data
- [ ] "Human" in signal.jsonl is provably human (passes behavioral checks)
- [ ] No IP addresses or identifying data stored at any point
