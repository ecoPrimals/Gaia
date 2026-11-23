# flockGate Wave 137b — Full Debt Checkpoint

**Date**: Jul 12, 2026 16:20 EDT | **Wave**: 137b | **From**: flockGate overwatch
**Purpose**: Comprehensive debt inventory. Every open item across the primal mountain listed for resolution by end of wave.

---

## Current State (Checkpoint)

| Metric | Value |
|--------|-------|
| primalSpring HEAD | `f2efaf6` (141 scenarios, 1,135 tests, 0 fail, 0 clippy) |
| wateringHole HEAD | `b6411694` |
| Mesh peers (TCP) | 2 (sporeGate, eastGate) |
| Mesh peers (registered) | 0 (bidirectional deploy pending) |
| WAN RTT primals.eco | 114ms |
| WG ICMP golgi | 31ms |
| Outer membrane | ALL PASS (4 endpoints) |
| footPrint | LIVE (primals.eco/footprint/) |
| Neural API sporeGate | LIVE (19 primals, 156 translations) |

---

## TIER 1 — Blockers for `capability.call` WAN (end this wave)

These must resolve for SHOW-HN readiness and full WAN dispatch validation.

| # | ID | Description | Owner | Status |
|---|-----|-------------|-------|--------|
| 1 | **NAPI-CROSS-GATE** | Deploy songBird `f05918a` to sporeGate + eastGate. Required for bidirectional mesh peering. flockGate already upgraded. | sporeGate + eastGate | **BLOCKED** — needs operator deploy |
| 2 | **GOLGI-WG-BIND** | songBird on golgi must bind to `10.13.37.1:7700` (currently binds public IP only). 1 of 4 overlay peers unreachable. | golgi | **BLOCKED** — needs config edit + restart |
| 3 | **DRAWBRIDGE-ROUTES** | Confirm `SONGBIRD_DRAWBRIDGE_ROUTES=/hub=jupyter` set on sporeGate. `jupyter` cap not advertised in mesh.status. | sporeGate | **UNVERIFIED** — needs SSH check |
| 4 | **NAPI-SYSTEMD** | Promote Neural API from manual start to systemd unit on sporeGate. Survives reboot. | sporeGate | HIGH — straightforward |
| 5 | **NAPI-LIFECYCLE** | LifecycleManager registration — `lifecycle.status` shows count=0. Primals aren't registering lifecycle hooks. | biomeOS | HIGH — code change needed |

**Resolution path**: Items 1-3 unblock flockGate's `capability.call` E2E. Item 1 is the critical gate — once sporeGate runs `f05918a`, flockGate gets bidirectional peers and can route `capability.call jupyter` through the mesh.

---

## TIER 2 — flockGate Local Debt

Items flockGate can resolve unilaterally.

| # | ID | Description | Priority | Effort |
|---|-----|-------------|----------|--------|
| 1 | **DEPOT-POPULATE** | Local depot has 0/13 primals. Only songBird binary present. Need `plasmid fetch` or manual depot sync from pepti. | MEDIUM | 30min |
| 2 | **FORGEJO-PARITY** | forgejo/main drifted behind origin/main. Need `git push forgejo main`. | LOW | 5min |
| 3 | **GATE-NAME-ENV** | Set `GATE_NAME=flockGate` in shell profile. Eliminates `struct:local_gate_identified` failure and removes hostname-detection fallback. | LOW | 2min |
| 4 | **FP-API-WIRE** | Wire footPrint `/api/proxy` through songBird drawbridge — design the route alignment between Express `?url=` pattern and songBird path-based routes. | MEDIUM | 2-4hr |
| 5 | **FP-PERSIST** | Replace footPrint Express CRUD (`/api/projects`) with nestGate CAS persistence. Design the content-addressable project schema. | MEDIUM | 4-8hr |
| 6 | **CLIPPY-FIX** | `Duration::from_millis(2000)` → `from_secs(2)` in `s_federation_wan_readiness.rs`. Already fixed locally, needs commit+push. | LOW | done |

---

## TIER 3 — Upstream Primal Mountain (other gates/teams)

Items tracked here for visibility that require action from other gates.

| # | ID | Description | Owner | Wave Target |
|---|-----|-------------|-------|-------------|
| 1 | **SOCKET-DIR-UNIFY** | Unify `/run/membrane/` and `/run/biomeos-root/` socket paths. 7 orphan names in manifest. | biomeOS | 137b |
| 2 | **SKUNKY-LIVE** | Remove `--dry-run` from skunky-ingest. Requires skunkBat `baseline.observe` listener deployed on golgi. | skunkBat + golgi | 137b |
| 3 | **TOPO-VIS** | sporePrint topology viz: petalTongue consumes `topology.primals` + `routing_weights` from Neural API (not hardcoded). | petalTongue | 138 |
| 4 | **LIVE-ACTIVATE** | `live.primals.eco` — petalTongue NUCLEUS on sporeGate. | sporeGate | 138 |
| 5 | **THREAT-ACTIVATE** | Feed 122 attacker IPs into skunkBat `baseline.observe`. | skunkBat | 138 |
| 6 | **VERSION-SKEW** | 3 distinct versions across local primals (v0.2.0/v0.9.16/v1.6.6). Major skew severity. | all teams | 138 |
| 7 | **PEPTI-TARGETS** | Missing depot targets: `aarch64-linux-android`, `x86_64-unknown-linux-gnu`. Awaiting Sovereign CI pipeline. | cellMembrane | 138+ |
| 8 | **BEARDOG-GATEHOUSE** | bearDog gatehouse TLS on golgi — sovereign ACME cert lifecycle. | bearDog + sporeGate | 139 |
| 9 | **NAPI-NICHE** | Gate enrollment via `niche.deploy` — replace manual provision scripts. | biomeOS + cellMembrane | 139 |
| 10 | **STRANDGATE** | Enroll strandGate — REALWORLD physical access needed. | operator | 139 |

---

## TIER 4 — Structural/Architectural Debt (Long-tail)

Not blocking anything, but tracked for eventual resolution.

| # | ID | Description | Priority |
|---|-----|-------------|----------|
| 1 | **SPORE-OWNERSHIP** | `SPORE_OWNERSHIP_MATRIX.md` doesn't exist — documents the three-way split between nestGate/rhizoCrypt/sweetGrass. | LOW |
| 2 | **NUCLEUS-MATRIX** | `NUCLEUS_VALIDATION_MATRIX` columns U/V/W undefined — spore ingest/emit/profile spec. | LOW |
| 3 | **CERT-OWNER** | Certificate owner shows `loamspine`, expected `beardog`. ACME lifecycle ownership TBD. | LOW |
| 4 | **SHADER-SUPPORT** | shader.list and trust.list registered in capability_registry.toml but no implementation. | LOW |
| 5 | **BOND-METADATA** | 0/16 deployment graphs have `bond_type` metadata. | LOW |
| 6 | **TIER-PRIORITY** | 7 compositions have tier priority = None (primalspring, cellmembrane, nucleus, etc.). | LOW |
| 7 | **FP-PARITY** | petalTongue visual parity with footPrint — 12 VT areas. | MEDIUM |

---

## Summary — Resolution Plan (End of Wave 137b)

### Must resolve (flockGate can action now):
1. Commit+push clippy fix to primalSpring
2. Push updated `heads/flockGate.toml`
3. Set `GATE_NAME=flockGate` in profile
4. Fix forgejo parity drift

### Must resolve (needs operator/upstream):
1. **NAPI-CROSS-GATE** — deploy `f05918a` to sporeGate + eastGate (CRITICAL)
2. **GOLGI-WG-BIND** — edit songBird config on golgi
3. **DRAWBRIDGE-ROUTES** — verify on sporeGate
4. **NAPI-SYSTEMD** — promote to service

### Can defer to Wave 138:
- FP-API, FP-PERSIST, TOPO-VIS, LIVE-ACTIVATE, THREAT-ACTIVATE
- DEPOT-POPULATE (non-blocking, informational scenario)
- VERSION-SKEW (coordination across teams)
- All TIER 4 items

---

*Once NAPI-CROSS-GATE deploys, flockGate can immediately verify bidirectional mesh peering and attempt the first `capability.call jupyter` E2E from WAN. That's the SHOW-HN gate.*
