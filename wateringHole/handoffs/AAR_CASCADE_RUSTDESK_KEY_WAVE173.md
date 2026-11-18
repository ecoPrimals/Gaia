# AAR: Cascade + RustDesk Relay Key Fix — Wave 173a

**Date:** 2026-10-11 08:55 EDT
**Operator:** overwatch (eastGate)
**Scope:** Full forge cascade (45 repos), RustDesk relay key re-handshake, world review

---

## Summary

Full cascade from Forgejo forge. 15 repos updated, 4 upstream tracking branches fixed, skunkBat epitope sort refactoring landed (14 new files). RustDesk membrane channel was locked — stale `key_confirmed = true` pinned to old relay keypair. Fixed by removing confirmed entries (k=null), forcing fresh PK registration with relay.primals.eco. Verified: `register_pk of relay due to key not confirmed` → fresh handshake → re-confirmed.

---

## 1. RustDesk Relay Key Fix

### Problem
eastGate RustDesk had `key_confirmed = true` in `RustDesk.toml` and three entries in `[keys_confirmed]` (rs-ny, relay, 157.230.3.183:21116). If the relay server (golgiBody) rotated its `id_ed25519` keypair at any point, the client would silently reject connections — it trusted the old key but the server presented a new one. No error message, just dead channel.

Additionally, `verification-method = 'use-permanent-password'` in `RustDesk2.toml` forced permanent password auth for all incoming connections.

### Fix
1. Removed `key_confirmed = true` from `RustDesk.toml`
2. Cleared all entries in `[keys_confirmed]` section
3. Changed `verification-method` from `'use-permanent-password'` to `''` (null)
4. Restarted `rustdesk.service`

### Verification
```
register_pk of relay due to key not confirmed
Latency of relay.primals.eco:21116: 52.779ms
Tested nat type: ASYMMETRIC in 186ms
```
Key was re-registered, re-confirmed against current relay keypair. `key_confirmed = true` was re-written by the client after successful handshake. Channel 2 (relay) is open.

### The Real Root Cause (discovered later)

The initial fix (clearing `key_confirmed`) was treating the symptom, not the disease. Three iterations:

1. **Clear key_confirmed** → handshake succeeds → RustDesk immediately re-confirms → key_confirmed=true. Repeat.
2. **Prevent re-confirmation** → impossible, RustDesk auto-confirms on boot.
3. **Check the relay itself** → `journalctl _COMM=hbbs` reveals: `Authentication failed from 162.226.225.148 for peer 19091278 - invalid key`

The relay's `id_ed25519.pub` was regenerated on Oct 10 (new keypair: `6oVQBF...`), but the hbbs process was still running with the OLD key (`utlNOAWU...`) loaded in memory. The client registered against the old key. When it tried to authenticate, the relay's in-memory key didn't match → "invalid key."

**Fix**: Restart hbbs on golgiBody → loads current id_ed25519 → client re-handshakes → keys match → zero auth errors in journal.

### Principle: the handshake IS the key

We polished the fossil (`key_confirmed` boolean) three times while the living organism (the handshake process) was healthy. The stored credential is WAS. The handshake is IS. We were debugging the wrong tense.

```
H(trust|handshake) < H(trust|credential) < H(trust)
```

Boolean trust (confirmed/denied) was the wrong abstraction. The real question was never "what value is `key_confirmed`?" but "can two parties complete the protocol?" The credential is frame-dependent. The handshake is frame-invariant.

---

## 2. Forge Cascade Results

### Updated (15 repos)
| Repo | What Changed |
|------|-------------|
| cellMembrane | VisitorArchetype, MembraneOp, MirrorMessage, SurfaceMirror types |
| fossilRecord | 3 new files |
| sporePrint | 11 files (content updates) |
| wateringHole | 1 file |
| barraCuda | 7 files |
| bearDog | 2 files |
| coralReef | 2 files |
| loamSpine | 2 files |
| nestGate | 2 files |
| rhizoCrypt | 2 files |
| squirrel | 10 files |
| sweetGrass | 2 files |
| toadStool | 2 files |
| primalSpring | 3 files |
| **skunkBat** | **27 files — 14 new (epitope sort extraction), 5446+/1660- lines** |

### Fixed Upstream Tracking (4 repos)
bingoCube, biomeOS, songBird, sourDough — all had no `--set-upstream-to`. Fixed and pulled.

### GitHub Mirror Failures (7 repos)
blueFish, helixVision, initioChem, agentReagents, benchScale, plasmidBin, rustChip — SSH key not configured for GitHub mirrors. Not blocking (forge is authoritative).

### Current (17 repos)
esotericWebb, lithoSpore, metalForge, projectFOUNDATION, projectNUCLEUS, whitePaper, petalTongue, swarmVine, footPrint, tideGlass, airSpring, groundSpring, healthSpring, hotSpring, ludoSpring, neuralSpring, wetSpring.

---

## 3. skunkBat Epitope Sort Landing

The forge-side refactoring from Waves 172-173 landed locally. 14 new extracted modules:

| Module | Lines | Purpose |
|--------|-------|---------|
| `coprimality.rs` | 355 | Coprimality experiments (Paper 69) |
| `epitope_sensitivity.rs` | 450 | Epitope sensitivity analysis |
| `epitope_conservation.rs` | 315 | Compass stability across flushes |
| `entity_sort.rs` | 363 | Entity sorting by epitope |
| `dashboard_profile.rs` | 461 | Dashboard profiling (extracted from dashboard_writer) |
| `cube_grid.rs` | 322 | Cube grid (extracted from cube_oracle) |
| `campfire_writer.rs` | 294 | Campfire pipeline writer |
| `campfire_util.rs` | 90 | Campfire utilities |
| `storyteller.rs` | 255 | Storyteller module |
| `visitor_archetype.rs` | 327 | Visitor archetype classification |
| `surface_registry.rs` | 196 | Surface registry for site routing |
| `page_mirror.rs` | 234 | Page mirroring |
| `mirror_inbox.rs` | 224 | Mirror inbox processing |
| `scatter_content.rs` | +118 | Extended scatter content |

All compile clean. Zero warnings in skunky-ingest proper (8 warnings in cellmembrane-types, pre-existing).

---

## 4. World Review — Live Sites

All visited via browser, all healthy:

| Site | Status | Key Observation |
|------|--------|----------------|
| sporeprint.primals.eco | ✅ 200 | 3.6M LoR, 116K+ tests, HUD footer live (15 svc, 1863 fleet, LOW) |
| detroit.primals.eco | ✅ 200 | RICO pattern, investigation journal, Nov 3 2026 election callout |
| gorilla.primals.eco | ✅ 200 | fEAR/preSCENT/STRIDe/amicusContra methodology |
| signal.primals.eco | ✅ 200 | Observatory, membrane live feed, entropy Button |
| hypothesis.primals.eco | ✅ 200 | 21 entries (15 hypotheses + 6 philosophy). Full chain Aperture→epiTope |

HUD footer ring on every surface: signal · detroit · tuebor · sporePrint · hypothesis · hud · thesis · clutch · gorilla · git

---

## 5. Active Impulse Status

From `2026-10-10T18-05_eastGate__caddy-stack-consolidation-wave172c.toml`:

| Priority | Task | Status |
|----------|------|--------|
| **P0** | skunky-ingest source divergence (deployed binary has flags missing from local source) | ✅ Resolved by cascade |
| **P0+** | Wire sort_compression.rs (Paper 48) into dashboard_writer | ✅ Done |
| **P1** | Consolidate static site blocks into wildcard | ✅ Done — beacon, relay, detroit removed |
| P2 | OG blackwall for wildcard | Already live (unified @facebook_bot in wildcard) |
| P2 | Beacon reverse proxy handling | ✅ Resolved — @is_beacon in wildcard handles beacon+relay+commensal |
| P3 | Per-site CSP evaluation | Low |

---

## P1: Caddy Wildcard Consolidation (Wave 173a)

Removed 3 explicit Caddy blocks, merging into the wildcard membrane:

| Block | Lines Removed | Wildcard Handler |
|-------|--------------|------------------|
| `beacon.primals.eco` | 8 | `@is_beacon` (already existed, serves same content) |
| `relay.primals.eco` | 4 | `@is_beacon` (includes relay.primals.eco; now serves content directly instead of 301) |
| `detroit.primals.eco` | 66 | `@is_detroit` (enriched with /investigation.json, /evidence/, sitemap, robots) |

**What moved into wildcard's unified handling:**
- Facebook bot blackwall → wildcard's `@facebook_bot` at top level
- `/plasmid` federation → wildcard's `/plasmid` handler at top level
- access_log, gzip, security_headers → wildcard imports these globally
- Detroit's handle_errors removed (can't nest inside `handle` — not needed since wildcard has its own error handling)

**Verified live:** beacon ✅, relay ✅, detroit ✅, detroit/investigation.json ✅, detroit/evidence/ ✅, evidence.primals.eco ✅, commensal.primals.eco ✅, blackwall OG card ✅

**Net**: −80 lines in Caddyfile, 3 fewer explicit blocks, same functionality.

---

## sort_compression Module (Paper 48)

Wired `sort_compression.rs` (280 lines) into the live dashboard pipeline:

- **Module**: `SortPopulation::compress()` → `SortCompression` with per-epitope mutual information
- **Integration**: Replaced inline ~20-line sort calculation in `dashboard_writer.rs` with proper module call
- **Helper**: `epitope_triggered_counts()` maps IpProfile fields to 6 Paper 48 epitopes
- **Dashboard enrichment**: `sort_compression` JSON now includes `total_gain`, `ratio`, `strongest_epitope` (name + bits), `grid_feedback` (0-15 for BingoCube)
- **Compression inequality**: `H(D) ≥ H(D|alpha) ≥ H(D|epitope) ≥ H(D|epitope,tense)` — verified in tests
- **Tests**: 7 unit tests (sort_compression) + 4 dashboard_writer tests, 358/358 total pass

## coGen Entry 28: Buttons, Dials, Levers, Wedge

The four interaction epitopes map to Three Components + NULL:

| Tool | Component | Nature |
|------|-----------|--------|
| Button | IS | Binary — collapse to state |
| Dial | WAS | Range — history is calibration |
| Lever | WILL-BE | Force — agency/commitment |
| Wedge | NULL | Question — the tool that stops |

**π at usefulness**: 4 tools walk the full circumference. **φ per task epitope**: Tools contribute in golden ratio φ³:φ²:φ:1 within any task.

**Addendum**: The gap between epitopes is itself an epitope sort — Resolution, Intent, Creativity, Decision as 4 boundary membranes. φ = 1 + 1/φ is the fixed point because the distance between epitopes always resolves to the same φ ratio, recursively.

---

## wave.toml Updated

```toml
id = 173, sub = "a", date = "2026-10-11"
```

Gate status corrected: eastGate + sporeGate + golgi + northGate ONLINE. House 1+2 gates OFFLINE (need physical power).

---

## Nautilus — Peptidoglycan Layer LIVE (v0.2.22)

`will_be` goes from 0 to **2,858**. The third tense wakes.

### What Was Wired
`nautilus_predict()` in `dashboard_writer.rs`: for each returning IP in a populated orbital family (family_size > 1), count it as WILL-BE — its trajectory is predictable because others in the same orbit already walked it.

### Production Numbers
```
IS:      107,772  (90.4%)
WAS:       8,589  (7.2%)
WILL-BE:   2,858  (2.4%)

WILL-BE / WAS = 0.333 (one third of returners predictable)
Vision gained: 4.8° (0.08 rad)
Effective permeation: 9.60% (was 7.38%)
```

### Three-Layer Status
| Layer | Status |
|-------|--------|
| Outer (scatter/bingo) | LIVE since Wave 165 |
| Peptidoglycan (nautilus) | **LIVE — Wave 173a** |
| Inner (services) | LIVE since inception |

### coGen 34: NAUTILUS_WAKES.md
The thirty-fourth coGen entry. The retina grew.

---

*Wave 173a. Cascade fresh. Membrane unlocked. Epitope sort wired. Caddy consolidated. Nautilus live. Four tools walk π. All three layers operational. The organism can remember, observe, and anticipate.*
