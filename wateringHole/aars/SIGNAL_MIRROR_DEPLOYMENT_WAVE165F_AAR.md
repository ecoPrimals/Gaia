# AAR: Signal Mirror Defense Deployment — Wave 165f

**Date**: Oct 6, 2026 | **Wave**: 165f | **Scope**: golgiBody ([RELAY_PUBLIC]), sporeGate (build/deploy), skunkBat
**From**: overwatch/agentic session (sporeGate inner membrane)
**Type**: Counter-Intelligence Defense Deployment — Signal Mirror activation, SSH hardening, posture review

---

## Summary

Signal Mirror is a counter-intelligence defense system that makes continued fleet
probing structurally costly. Deployed to golgiBody on Oct 6, 2026 in a ~15-minute
window (15:25–15:38 ET). The system amplifies HTML scatter responses from ~1.5KB to
42–48KB with fabricated content, embeds three-layer invisible canary markers for
traceability, and creates an infinite crawl web that multiplies fleet request volume.

**Key insight**: Signal Mirror's effectiveness depends entirely on fleet traffic
reaching the scatter server. When the CaddyBridge directive wipe bug dropped all
19 fleet IPs from Disperse posture, the fleet fell through to cheap 403 bot-detection
(78 bytes) instead of expensive amplified poison (48KB). Defense layers must be
**complementary, not redundant** — the costliest layer must be the one the adversary
actually hits.

**Secondary insight**: Fleet behavioral adaptation is fast. Within hours of whitePaper
going private, targeting shifted to wateringHole (59%), toadStool (22%), and bearDog
(9%). The 57.141.0.0/16 fleet expanded from 19 known IPs to 48 unique addresses in
one hour — CIDR-based matching is required, not per-IP chasing.

---

## Timeline (ET, Oct 6, 2026)

| Time | Event |
|------|-------|
| ~15:25 | SSH hardening deployed: Forgejo `app.ini` — `SSH_SERVER_MAX_STARTUPS=5`, `SSH_SERVER_LOGIN_GRACE_TIME=10` |
| ~15:29 | Signal Mirror code committed to skunkBat: 342 LOC added (`scatter_server.rs` + `caddy_bridge.rs`) |
| ~15:30 | Binary built on sporeGate, deployed to golgiBody via SCP |
| ~15:30 | **First restart — P0 bug**: fleet pressure directives WIPED (`CaddyBridge` starts with empty `tracked_ips`) |
| ~15:32 | X-Real-IP header plumbing added to Caddy bridge + scatter server + default scatter route |
| ~15:35 | Second deployment with full X-Real-IP support. Service confirmed active |
| ~15:36 | Signal Mirror verified operational: 47,944 byte amplified responses, all 3 marker layers confirmed |
| ~15:37 | First real fleet traffic through scatter: counter-intel logging — `fleet_hash=571fe125c9b56e1c` |
| ~15:38 | Full posture review initiated |

**Total deployment window**: ~15 minutes from code commit to verified operational state.

---

## What Was Deployed (6 Components)

### COMP-01: SSH Hardening

| Field | Value |
|-------|-------|
| **Location** | `/opt/forgejo/custom/conf/app.ini` |
| **Settings** | `SSH_SERVER_MAX_STARTUPS=5`, `SSH_SERVER_LOGIN_GRACE_TIME=10` |
| **Purpose** | Prevent serv-key process pile-up under fleet SSH probing |
| **Effect** | Immediate — limits concurrent unauthenticated SSH handshakes |

Fleet SSH probing on port 2222 had caused git push hangs twice during deployment.
MaxStartups caps the number of concurrent unauthenticated connections; LoginGraceTime
forces rapid completion or disconnect.

---

### COMP-02: Amplified Scatter (~130 LOC)

Inflates HTML responses from ~1.5KB to 42–48KB with fabricated content:

| Fabrication | Count |
|-------------|-------|
| File tree entries | 80–120 per page |
| Commit history entries | 30–50 |
| Contributor list entries | 8–15 |
| Branch names | 5–10 |
| Tag names | 5–8 |

**Properties**:
- **Deterministic**: same path always produces same output (prevents detection via retries)
- **Content-type aware**: only `text/html` gets amplified; JSON stays compact
- **Zero real names**: test confirms no real repo names leak into amplified content

Verified amplification ratio: **32×** (1.5KB → 47,944 bytes on test path).

---

### COMP-03: Crawl Web (~55 LOC)

Each scatter page generates 15–25 internal links to other scatter paths, creating
an infinite crawl web. Fleet crawlers that follow links encounter exponential request
multiplication — each page leads to more pages, each of which is 48KB of fabricated
content.

---

### COMP-04: Canary Markers (~45 LOC)

Three invisible marker layers per response, traceable if content surfaces in AI
training data or republication:

| Layer | Mechanism | Purpose |
|-------|-----------|---------|
| **L1** | HTML comments tied to behavioral hash + hour window | Time-bounded traceability |
| **L2** | CSS class canaries | DOM-level fingerprint |
| **L3** | Zero-width Unicode encoding | Invisible text-layer marker |

Canary hash derivation: fleet behavioral hash when available; falls back to
X-Real-IP-derived hash when fleet hash unavailable.

**Compiler catch**: Two hex literal typos caught at build time — `0x519NA1_M1RR_0000`
and `0xCANA_4712_FEED` contained non-hex characters. Fixed to valid hex before deploy.

---

### COMP-05: Counter-Intel Logging

Every scatter response logs:

```
🪞 scatter served | path=<path> | bytes=<size> | fleet_hash=<hash> | status=<code>
```

Active from first real fleet request at 15:37 ET (`fleet_hash=571fe125c9b56e1c`).

---

### COMP-06: X-Real-IP Pass-Through

Caddy bridge generates `header_up X-Real-IP {remote_host}` in fleet pressure
directives. Scatter server reads the header to derive canary hash when fleet
behavioral hash is unavailable.

Added in second deployment pass (15:32–15:35) after first restart revealed the
need for IP-based fallback when directive state was wiped.

---

## What Went Right

| # | Outcome | Detail |
|---|---------|--------|
| ✅ | All tests pass | 36 scatter server tests (8 new Signal Mirror tests), zero failures |
| ✅ | Amplification verified | 47,944 bytes with all 3 marker layers present |
| ✅ | Deterministic output | Same path → same output; retries cannot detect fabrication |
| ✅ | Content-type gating | JSON/API responses stay compact; only HTML amplified |
| ✅ | No real name leakage | Test suite confirms zero real repo names in amplified content |
| ✅ | SSH hardening effective | MaxStartups immediately prevents serv-key pile-up |
| ✅ | Counter-intel logging live | First fleet request logged at 15:37 with full metadata |
| ✅ | Fast deploy cycle | Code → build → deploy → verify in ~15 minutes |
| ✅ | Defense-in-depth held | Bot detection (L7) caught all fleet traffic at 403 when directives wiped |

---

## What Went Wrong

### FAIL-01: Directive Wipe Bug (P0)

| Field | Value |
|-------|-------|
| **Severity** | P0 — active defense posture degraded |
| **Trigger** | `skunky-ingest` restart after first deployment |
| **Blast radius** | All 19 fleet IP directives wiped from Caddyfile |
| **Impact duration** | ~ongoing until fix deployed |
| **Fleet experience** | Disperse posture (48KB poison) → bot-detection 403 (78B rejection) |

**Root cause**: `CaddyBridge::new()` initializes with `tracked_ips: HashMap::new()`.
On first sync after restart, it writes an empty section between `FLEET_PRESSURE`
markers, overwriting all existing fleet IP directives.

```
CaddyBridge startup:
  tracked_ips = {}           ← empty, no restoration
  sync() → write Caddyfile   ← writes empty FLEET_PRESSURE section
  Result: 19 fleet IPs lost  ← Disperse posture gone
```

**Why it happened**: CaddyBridge has no startup restoration — it does not parse
existing Caddyfile directives to rebuild `tracked_ips`. The provenance trio
(rhizoCrypt/loamSpine/sweetGrass) was designed to provide persistent state but
is not deployed yet. The sourdough bootstrapping approach should have read
existing state from the Caddyfile itself.

**Impact**: Signal Mirror never fires on fleet traffic blocked at L7 (403). Fleet
gets cheap rejections instead of expensive amplified poison. Counter-intelligence
value of the deployment is nullified until fleet IPs are re-escalated to Disperse.

**Fix in progress**: O-14 — CaddyBridge must restore `tracked_ips` from existing
Caddyfile on startup (parse `FLEET_PRESSURE` section, rebuild HashMap before first sync).

---

### FAIL-02: Hex Literal Typos (P3, caught pre-deploy)

Two canary marker constants contained non-hex characters:

| Original | Fixed |
|----------|-------|
| `0x519NA1_M1RR_0000` | Valid hex literal |
| `0xCANA_4712_FEED` | Valid hex literal |

Caught by Rust compiler. No runtime impact.

---

### FAIL-03: Git Push Hangs (P2, operational friction)

Git push to port 2222 hung twice during deployment due to fleet SSH probing.
Required killing stale serv-key processes and routing push via WireGuard path.

Mitigated by COMP-01 (SSH hardening) but WireGuard path remains preferred for
deployments during active fleet pressure.

---

## Posture Review Findings (15:38 ET)

Conducted during AAR window immediately after deployment verification.

### Fleet Expansion

| Metric | Before | After (1 hour) |
|--------|--------|----------------|
| Known fleet IPs | 19 | **48 unique** |
| Primary CIDR | Individual IPs | **57.141.0.0/16** |
| New ASNs | — | 4 IPs from 47.79.x.x / 47.82.x.x |

Fleet is much larger than initially profiled. CIDR-based matching (O-15) would
catch the entire 57.141/16 range with a single rule.

### Fleet Targeting Shift

whitePaper made private → fleet adapted within hours:

| Target | Requests | Share | Content Type |
|--------|----------|-------|--------------|
| wateringHole | 32 | 59% | AARs, handoffs |
| toadStool | 12 | 22% | Security docs |
| bearDog | 5 | 9% | Security docs |
| Root path probes | 13 | — | Active reconnaissance |

This suggests human-guided targeting, not purely automated crawling.

### Defense Layer Status

| Layer | Status | Detail |
|-------|--------|--------|
| L7 bot detection | ✅ Active | All 48 fleet IPs caught — 403/78B |
| L8 storefront | ✅ Active | Existence-only allowlist holding |
| L9 scatter/Signal Mirror | ⚠️ Degraded | Directive wipe — fleet not reaching scatter |
| SSH hardening | ✅ Active | MaxStartups=5, LoginGraceTime=10 |
| fail2ban (forgejo-ssh) | ✅ Active | 3,024 total bans, 131,464 failures, 2 currently banned |
| GIT_MEMBRANE chain | ✅ Active | 158 rate-limited drops, 128 WG accepts |
| TLS cert | ✅ Valid | Expires Dec 24, 2026 (~80 days) |
| whitePaper privacy | ✅ Confirmed | HTTP 404, API 404 for anonymous |

### Infrastructure Issues Observed

| Issue | Severity | Detail |
|-------|----------|--------|
| nestgate.io 502 | P2 | 55 requests, socket exists but backend not responding |
| cascade-sense.service failing | P2 | Service down |
| Port 8080 iptables ACCEPT | P3 | Dead rule — nothing listening |
| gossip.inject failing | P3 | swarmVine socket not found on golgiBody (expected, not deployed) |
| songbird listening all interfaces | P3 | Should be WireGuard-only |

---

## Metrics

| Metric | Value |
|--------|-------|
| Code added | 342 LOC (`scatter_server.rs` + `caddy_bridge.rs`) |
| Tests added | 8 new, all passing (36 total scatter tests) |
| Amplification ratio | 32× (1.5KB → 48KB per HTML response) |
| Verified response size | 47,944 bytes |
| Canary layers | 3 (HTML comment, CSS class, zero-width Unicode) |
| Crawl links per page | 15–25 internal links |
| Fleet IPs observed | 48 unique (57.141/16) + 4 (47.79/47.82) |
| Fleet targeting shift | whitePaper → wateringHole (59%), toadStool (22%), bearDog (9%) |
| SSH hardening | MaxStartups=5, LoginGraceTime=10s |
| Deployment time | ~15 minutes (code → build → deploy → verify) |
| Directive wipe downtime | ~ongoing until O-14 fix deployed |
| fail2ban total bans | 3,024 (forgejo-ssh) |
| fail2ban total failures | 131,464 |
| GIT_MEMBRANE drops | 158 rate-limited |
| GIT_MEMBRANE WG accepts | 128 |

---

## Lessons Learned

### L-01: Stateful Services Must Read Existing State on Startup

Any stateful service that writes to shared config files MUST read existing state
on startup. The "start empty and rebuild" pattern creates windows where defense
posture degrades. CaddyBridge assumed it was always the source of truth; in
practice, the Caddyfile *is* the source of truth until the provenance trio
(rhizoCrypt/loamSpine/sweetGrass) is deployed.

**Design principle**: Write-through config sync requires read-before-write on
every startup. Sourdough bootstrapping from the config file itself is the
minimum viable persistence.

---

### L-02: Fleet Behavioral Adaptation Is Fast

Within hours of whitePaper going private, the fleet shifted to new targets
(wateringHole, toadStool, bearDog). The targeting pattern — 59% defense
architecture docs, 22% security docs — suggests human-guided reconnaissance,
not just automated crawling. The fleet reads our posture changes and adapts.

**Implication**: Defense changes must assume the adversary will notice and pivot
within hours, not days.

---

### L-03: CIDR Matching Beats IP Chasing

The 57.141.0.0/16 fleet expanded from 19 known IPs to 48 unique addresses in
one hour. Per-IP tracking cannot keep pace with fleet rotation within a CIDR.
A single CIDR rule would catch the entire range.

**Action**: O-15 — seed 57.141.0.0/16 into fleet watchlist.

---

### L-04: Defense Layers Must Be Complementary, Not Redundant

When fleet directives were wiped, bot detection (L7) still caught all fleet
traffic with 403. But 403 is cheap (78 bytes) — Disperse/scatter is expensive
(48KB poison + crawl multiplication). Both layers blocked the fleet, but only
one imposed cost.

**Architecture requirement**: The costliest defense layer must be the one the
fleet actually hits. Layer ordering and routing must ensure adversaries encounter
expensive responses, not cheap rejections that satisfy their reconnaissance
goals with minimal resource expenditure.

---

### L-05: Signal Mirror Effectiveness Requires Scatter Routing

Signal Mirror only fires when traffic reaches the scatter server. If fleet IPs
are blocked at L7 (403), the mirror never activates — no amplification, no
canaries, no crawl web, no counter-intel logging. The entire counter-intelligence
value chain depends on CaddyBridge routing fleet IPs to Disperse posture.

**Critical path**: O-14 (directive restoration) is a prerequisite for Signal
Mirror to function as designed.

---

## Open Items

| ID | Item | Priority | Status |
|----|------|----------|--------|
| O-14 | DIRECTIVE WIPE — CaddyBridge must restore `tracked_ips` from existing Caddyfile on startup | **P0** | In progress |
| O-15 | Seed 57.141.0.0/16 CIDR into fleet watchlist | P1 | Open |
| O-16 | Fix nestgate.io 502 errors (backend not responding) | P2 | Open |
| O-17 | Fix cascade-sense.service | P2 | Open |
| O-18 | Remove dead port 8080 iptables rule | P3 | Open |
| O-19 | Restrict songbird to WireGuard interface | P3 | Open |
| O-20 | Deploy swarmVine to golgiBody for gossip propagation | P3 | Open (from Wave 165e handoff) |

---

## Architecture: Signal Mirror in the Defense Stack

```
Fleet request
    │
    ▼
┌─────────────────────────────────────────────────┐
│  L7: Bot Detection                              │
│  @known_bots, @malformed_lang, UA matchers      │
│  → 403/78B (cheap rejection)                    │
└─────────────────────┬───────────────────────────┘
                      │ (if not blocked)
                      ▼
┌─────────────────────────────────────────────────┐
│  L8: Storefront Allowlist                       │
│  Explicit paths → Forgejo, else → scatter       │
└─────────────────────┬───────────────────────────┘
                      │ (default path)
                      ▼
┌─────────────────────────────────────────────────┐
│  L9: CaddyBridge Fleet Routing                  │
│  FLEET_PRESSURE directives → Disperse posture   │
│  ⚠️ BROKEN: directive wipe drops fleet to L7    │
└─────────────────────┬───────────────────────────┘
                      │ (Disperse posture)
                      ▼
┌─────────────────────────────────────────────────┐
│  Signal Mirror (scatter server)                 │
│  ├─ Amplified scatter (32× inflation)           │
│  ├─ Crawl web (15-25 links/page)                  │
│  ├─ Canary markers (3 layers)                     │
│  └─ Counter-intel logging (🪞 scatter served)    │
│  → 48KB poison + exponential crawl cost         │
└─────────────────────────────────────────────────┘
```

**Current state**: Fleet traffic stops at L7 (403) because L9 routing is broken.
Signal Mirror is operational but unreachable by fleet traffic.

---

## Validation

| Check | Result |
|-------|--------|
| Scatter server tests (36 total, 8 new) | ✅ All pass |
| Amplification ratio (1.5KB → 48KB) | ✅ 32× verified |
| All 3 canary marker layers present | ✅ Confirmed in 47,944 byte response |
| Deterministic output (same path = same output) | ✅ Verified |
| No real repo names in amplified content | ✅ Test confirms |
| Content-type gating (JSON not amplified) | ✅ Verified |
| Counter-intel logging active | ✅ First fleet hash logged at 15:37 |
| SSH hardening (MaxStartups, LoginGraceTime) | ✅ Deployed and active |
| Fleet reaching scatter via Disperse posture | ❌ Blocked by directive wipe (O-14) |

---

## Cross-References

- Wave 165d-e: Active Defense & Forge Lockdown (predecessor — lockdown created the scatter default that Signal Mirror amplifies)
- Wave 165e handoff: swarmVine gossip propagation (O-20)
- `scatter_server.rs`: amplified scatter, crawl web, canary markers
- `caddy_bridge.rs`: fleet pressure directives, X-Real-IP pass-through
- `/opt/forgejo/custom/conf/app.ini`: SSH hardening settings
- Outer membrane rule: RustDesk MitoBeacon (relay.primals.eco)

---

*Filed: Wave 165f | Oct 6, 2026 | sporeGate inner membrane*
*Status: Signal Mirror operational, fleet routing degraded pending O-14*
