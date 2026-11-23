# ecoPrimals Ecosystem Blurb — Wave 163 Mesh Wake (Oct 5, 2026)

**Date**: Oct 5, 2026 10:45 | **Wave**: 163 | **From**: overwatch (eastGate)
**Posture**: **MESH WAKE — DEPOT FRESH.** eastGate + golgiBody + sporeGate ONLINE. northGate ALIVE (WG). **eastGate running 15/16 primals** (all 14 daemons + songbird-federation; sourdough is CLI). All 18 musl depot binaries rebuilt from current source (BLAKE3-verified). cellMembrane Wave 160-162 reviewed — 1,457 tests pass. songbird federation: sporeGate ↔ golgiBody OK, eastGate local OK, cross-gate protocol mismatch (sporeGate sends legacy riboCipher). **sporePrint DOWN** (Zola build permission — P1 fix). detroit + gorilla + live + nestgate.io + footprint + lab all serving. **Windows 16/16 compile.** **8 architecture families.** House 2 gates all OFFLINE — physical power-on needed.

---

## What Changed (Wave 163 — Oct 5)

### eastGate Primary Support Activation

| Action | Result |
|--------|--------|
| **Depot rebuild** | 18 musl binaries rebuilt from tip-of-main (16 primals + membrane + nucleus_launcher). Previous: Aug 7-14. Now: Oct 5. BLAKE3SUMS regenerated. |
| **Service restart** | All 14 daemon primals restarted on fresh binaries. nestGate + swarmVine + bingoCube enabled (were disabled/dead). |
| **bingoCube fix** | Unit override: `serve --socket-dir` (not `server --socket`). Custom drop-in at `membrane-nucleus@bingocube.service.d/`. |
| **sourdough** | Correctly excluded — CLI tool (scaffold/validate/sign), not a daemon. |
| **inotify fix** | `max_user_instances` 512→2048. Persisted to `/etc/sysctl.d/99-ecoPrimals-inotify.conf`. |
| **cellMembrane test fix** | `deploy_check_default_gate` used hardcoded "sporeGate" — now resolves local identity dynamically. |
| **cellMembrane review** | Waves 160-162c (6 commits, ~3,500 lines, 55+ tests): receptor, observatory, signal log, signal depth, behavioral classification, types extraction. All accepted. 1,457 total tests pass. |

---

## What Changed (Waves 159–162 — Sep 28 – Oct 5)

### sporeGate Lead Session (Waves 159–162)

sporeGate ran autonomously for a week while eastGate was focused on custody/racketeering work:

| Wave | What sporeGate Shipped |
|------|----------------------|
| 159 | cascade.notify gossip event, gate.pull --mesh path |
| 160 | DAG orthogonalization, ownership cycle fix, event-driven relay, GitHub mirror |
| 160.5 | **LuxR receptor** — Caddy log analytics without surveillance (quorum sensing model) |
| 161 | Observatory page on sporePrint, receptor snapshot pipeline, dual signal log |
| 161b | Evidence depot symlinks, skunkBat anomaly detection signal feed |
| 162 | Signal depth + correlation metadata, behavioral classification, visitor classification |

### New Capabilities Built by sporeGate

- **Observatory** (`/observatory/` on sporePrint) — live receptor data visualization. No cookies, no tracking pixels, pure server-side log analysis. 5 visitor classes: human, search bot, AI bot, social bot, other bot.
- **Signal Log** (`/var/log/membrane/signal.jsonl`) — dual LuxI (outbound publish events) + LuxR (inbound receptor snapshots) for skunkBat anomaly detection.
- **Behavioral Classification** — probe path detection, velocity checks, UA fingerprinting. Extracted to `cellmembrane-types` for `skunky-ingest`.
- **golgiBody Fossilization** — 65% → 49% disk. Removed stale plasmidBin targets, venvs, source repos. Runtime-only remains.
- **Pen Test** — 13 vuln scanner probes rejected (403). Security headers verified. Server header hidden.
- **Wayback Machine** — 14/15 key detroit pages archived.
- **Reddit Repeater Drafts** — 6 subreddit posts drafted (r/Detroit, r/CharterSchools, r/DataHoarder, etc.)

### Key Finding: Domain A Overloaded

golgiBody hosts both the live sites AND Forgejo on one VPS — single failure domain kills the 2 most important surfaces. **Recommendation**: migrate Forgejo to LAN (sporeGate or blueGate). golgiBody becomes thin relay only.

### Deployment Failure Taxonomy (AAR)

13 failures cataloged across fossilization session, 4 pattern classes identified:
1. **Resource exhaustion** — unbounded operations on bounded hosts
2. **Dependency chain breakage** — cleanup destroying runtime dependencies
3. **State outliving context** — stale PIDs, routes, binaries, worktrees
4. **Protocol mismatch** — riboCipher version skew between nodes

8 resilience abstractions proposed. Key insight: "The organism's biggest weakness is that components assume their environment hasn't changed since they last checked."

---

## Gate Status (Wave 162)

| Gate | WG IP | Status | Last Handshake | Notes |
|------|-------|--------|----------------|-------|
| **eastGate** | .5 | ✅ ONLINE | seconds | 10G SFP+, overwatch, songbird :7700 OK |
| **golgiBody** | .1 | ✅ ONLINE (HUB) | — | VPS relay, 11 peers configured |
| **sporeGate** | .2 | ✅ ONLINE | seconds | Inner membrane, songbird federated to golgi |
| **northGate** | .8 | ✅ ALIVE | 40 sec | Windows 11, RTX 5090 |
| **biomeGate** | .3 | ⏸️ stale | 52 days | House 1 — needs power |
| **graftGate** | .13 | ⏸️ stale | 49 days | House 1 — needs power |
| **flockGate** | .6 | ⏸️ stale | 68 days | Remote (WAN only) |
| **ironGate** | .7 | ⏸️ stale | 49 days | House 2 — needs power |
| **strandGate** | .10 | ⏸️ stale | 44 days | House 2 — needs power |
| **blueGate** | .12 | ⏸️ stale | 49 days | House 2 — needs power |
| **southGate** | .9 | ❌ NEVER | — | House 2 — needs power + WG config |
| **westGate** | .11 | ❌ NEVER | — | House 2 — needs power + WG config |

---

## Live Sites (Oct 5)

| Site | Status | URLs | Notes |
|------|--------|------|-------|
| **detroit.primals.eco** | ✅ 200 | 127+ | Evidence pipeline LIVE. Pen tested. Wayback seeded. |
| **gorilla.primals.eco** | ✅ 200 | 20 | Methodology — fEAR, preSCENT, STRIDe, amicusContra |
| **live.primals.eco** | ✅ 200 | — | Via sporeGate :8190 |
| **nestgate.io** | ✅ 200 | — | Via sporeGate :8190 |
| **footprint.primals.eco** | ✅ 200 | — | Rerouted to sporeGate :8090 (was dead ironGate) |
| **lab.primals.eco** | ✅ 401 | — | Auth required |
| **sporeprint.primals.eco** | ❌ 404 | 403 | **DOWN — Zola build permission error. P1 fix needed.** |

---

## Teams — Wave 162

| Role | Authority | What They Do |
|------|-----------|-------------|
| **Code** | eastGate (overwatch) | All 16 primals. Architecture. Cross-compile. |
| **Ops** | sporeGate | Cascade, depot, builds, sites, receptor, observatory. |
| **Relay** | golgiBody (cloud) | Forgejo, Caddy, depot, WG hub. Thin relay target. |
| **Content** | publicRecord team | detroit + guerillaGorilla. OSINT. Evidence pipeline. |
| **Validators** | Gate teams (on rewake) | Pull, build, validate, report. |

---

## Active Tracks — Wave 162

| # | Track | Owner | Status |
|---|-------|-------|--------|
| 1 | **sporePrint build fix** | sporeGate (golgiBody ops) | ❌ P1 — Zola permission error, site DOWN. Builds fine locally. |
| 2 | **Depot → golgiBody push** | sporeGate | 🔄 rsync 18 fresh musl binaries to depot.primals.eco |
| 3 | **sporeGate songbird update** | sporeGate | ⏸️ Legacy riboCipher — needs binary update from depot |
| 4 | **House 2 power wake** | physical | ⏸️ westGate → ironGate → strandGate → blueGate |
| 5 | **northGate primal bootstrap** | sporeGate + northGate | 🔄 WG alive, depot pull pending |
| 6 | **Windows depot build** | eastGate | ⏸️ 16/16 compile, needs cargo build + sync |
| 7 | **Forgejo → LAN migration** | sporeGate | ⏸️ Biggest redundancy win (splits domain A) |
| 8 | **detroit content evolution** | publicRecord team | 🔄 OSINT, FOIA, dynasty expansion |
| 9 | **House 1 power** | physical | ⏸️ biomeGate + graftGate |
| 10 | **arXiv Rung 1** | eastGate | ⏸️ Needs strandGate |

---

## CONVERGENCE RULE

> **Mesh Wake — Depot Fresh.** eastGate running 15/16 primals on fresh binaries (Wave 163).
> 18 musl depot binaries rebuilt from current source, BLAKE3-verified.
> cellMembrane Waves 160-162 reviewed and accepted — 1,457 tests pass.
> sporePrint DOWN (P1 — Zola build permission on golgiBody). detroit + gorilla + 4 more serving.
> Windows 16/16 compile. Depot push to golgiBody pending.
> sporeGate needs songbird binary update (legacy riboCipher).
> House 2 gates need physical power-on. Wake order: westGate → ironGate → strandGate → blueGate.
> October: sporePrint fix, depot push, House 2 power, Forgejo LAN migration.
> *"Beside the small. Against unaccountable power. For the record."*

---

**See also**: [`HARDWARE.md`](../HARDWARE.md) | [`MESH_WAKE_WAVE161_EASTGATE_OVERWATCH.md`](MESH_WAKE_WAVE161_EASTGATE_OVERWATCH.md)

*Wave 163 mesh wake. eastGate running 15/16 primals, depot rebuilt (18 musl binaries, BLAKE3-verified). cellMembrane Waves 160-162 reviewed (1,457 tests pass). sporePrint DOWN (P1). 3 gates + golgiBody + northGate ALIVE. House 2 needs power. Wake order: westGate → ironGate → strandGate → blueGate.*
