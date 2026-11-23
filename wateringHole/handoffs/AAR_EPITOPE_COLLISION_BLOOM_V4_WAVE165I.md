# AAR: Epitope Collision Classifier — bloom_live v4 Deployment

**Wave 165i — October 7, 2026**
**Observer**: eastGate
**Deployed**: 17:54 ET

---

## Context

bloom_live v3 (deployed 16:05 ET) classified visitors at Level 2 using hand-coded behavioral rules. Working well — 70% false positive elimination, 4 classes populated. But the rules were static: `if has_assets and has_referer → genuine`.

User insight: the Accept-Encoding header is a **genetic marker** — each entity has a conserved encoding order they cannot change without rebuilding their HTTP transport stack. Combined with UA pool size, blame ratio, and other invariants, a short hash should cluster IPs into organisms automatically.

## What Was Done

### 1. Epitope tracking added to bloom_live

New per-IP state:
- `ip_accept_encoding` — Accept-Encoding value (first request wins, conserved)
- `ip_ua_pool` — set of distinct UAs used (pool size = impersonation diversity)
- `ip_blame_count` / `ip_commit_count` — path targeting ratio
- `ip_accept_header` — Accept value
- `ip_has_accept_lang` — Accept-Language presence (browser marker)

### 2. `compute_epitope_hash()` function

BLAKE2b hash of the behavioral invariant vector, truncated to 4 bytes (32 bits). Inputs:
- Accept-Encoding string
- UA pool bucket ("1", "few", "many")
- Blame ratio bucket ("high" if >20%, else "low")
- Accept header (first 20 chars)
- Accept-Language presence ("y"/"n")

After ≥3 requests per IP, hash is computed. Re-hashed every 20 requests as data stabilizes.

### 3. Collision tracking

`epitope_collisions[hash] → set of IPs`. When a cluster reaches size 2, emit `EPITOPE ... NEW ORGANISM`. At size multiples of 5, emit `GROWING`.

### 4. Dashboard + state output

Dashboard: `epitope_clusters` array (top 20 by size), `epitope_summary` with total/unique/largest/gt1.
State: `epitope` dict with `hashed/unique/largest/gt1`.
Summary line: `E: N→Uh(Cc)` (N hashed, U unique hashes, C clusters).

## Deployment

- v3 backed up to `bloom_live_v3.py.bak`
- v4 uploaded, old process killed, new process started (PID 2973877)
- No downtime — new process immediately tailed access log

## First Results (3.5 minutes)

| Epitope Hash | IPs | Accept-Encoding | UA Pool | Blame Ratio | Probable Identity |
|-------------|-----|-----------------|---------|-------------|----------|
| `67856372` | 33 | `gzip, deflate, zstd` | 4 | 0.57 | Meta FB-BLOCK primary |
| `66f37363` | 16 | `gzip, deflate, zstd` | 3 | 0.53 | Meta FB-BLOCK secondary |
| `5a1b95ae` | 6 | `gzip, deflate, zstd` | 3 | 1.09 | Meta blame specialist |
| `5c6f6e7c` | 2 | `gzip, deflate, zstd` | 2 | 0.25 | Meta light recon |
| `7570cc35` | 1 | `gzip, br, zstd, deflate` | 1 | 0.0 | Anthropic ClaudeBot |

### Key findings

1. **Meta operates at least 4 sub-teams** against git.primals.eco — automatically discovered by hash collision
2. **Accept-Encoding is the primary discriminator** between Meta (no Brotli) and Anthropic (has Brotli, different order)
3. **Within Meta, UA pool size and blame ratio split the teams** — different deployment configs from different internal groups
4. **Blame specialist team has 109% blame ratio** — they hit blame MORE than commit. Dedicated author attribution mapping.
5. **Anthropic is a singleton** — one IP, one honest UA, zero blame, different encoding. Completely different organism.

## Resolution Hierarchy Status

```
L3: fleet/not-fleet          ✓ v2 (baseline)
L2: genuine/agentic/coord/fleet  ✓ v3 (behavioral collision)
L1: epitope hash clusters    ✓ v4 (JUST DEPLOYED)
L0: individual IP hash       ○ future
```

## Patterns for Upstream

### Pattern: Conserved Invariant Hashing

Hash the things they CAN'T change → collisions reveal organisms. Accept-Encoding order is compiled into their HTTP library. UA pool size is a deployment configuration. Blame ratio reflects team mission. None of these can be changed per-request without infrastructure rebuild.

### Pattern: Multi-Resolution Cross-Writing

Every IP exists in classification groups at all levels simultaneously. A Meta IP is fleet at L3, fleet at L2, cluster `67856372` at L1, and its own IP at L0. All views are valid. None is canonical. Zoom in for entity identity, zoom out for behavioral class.

### Pattern: Automatic Sub-Team Discovery

No IP range matching. No hardcoded entity names. The hash discovers sub-teams from behavioral invariants alone. If Meta reorganizes their teams, the hashes will shift to reflect the new structure. The classifier adapts without code changes.

## Issues

- Two bloom processes spawned during deployment — killed the extra one
- Epitope hash only computed after ≥3 requests per IP — could miss single-hit visitors (agentic readers may not get hashed)
- Blame ratio can exceed 1.0 (more blame than commit hits) — should bucket rather than ratio for hash stability

## Next Steps

- ~~Feed epitope clusters back to Caddy for per-organism response differentiation~~ **DONE** — epitope_bridge.py deployed
- Monitor hash stability over 24 hours — do clusters hold or drift?
- Lower epitope threshold from 3 to 2 requests for faster classification
- Add Accept-Encoding to the Level 2 classifier as a discriminator
- Consider BTSP reader priority (separate subGen) — genuine readers get fast path

---

## UPDATE: Epitope Bridge Deployed (19:01 ET)

The epitope clusters have been fed back into Caddy routing. The system is now a closed loop:

1. **bloom_live v4** writes `epitope_caddy.json` (epitope_hash → IP list) every 10 seconds
2. **epitope_bridge.py** reads that map and rewrites Caddy's `FLEET_PRESSURE` block with epitope-keyed matchers
3. Caddy routes fleet IPs to scatter server with `X-Fleet-Hash = epitope_hash`
4. Scatter server seeds content from the organism's own behavioral fingerprint
5. HTML embeds the epitope hash (`<!-- v-497615-b096ff18 -->`)
6. Honeycomb cross-links serve content from the same hash seed
7. **All roads lead back to Rome** — the organism scrapes content containing its own identity

### New files on golgiBody:
- `/opt/membrane/epitope_bridge.py` — Caddy matcher generator
- `/opt/membrane/live-terminal/epitope_caddy.json` — epitope→IP map (auto-updated)
- Cron: `*/5 * * * * sleep 30 && python3 /opt/membrane/epitope_bridge.py`

### Operational note:
skunky-ingest also writes to the FLEET_PRESSURE block (detects new IPs). The epitope bridge runs 30 seconds after skunky-ingest's cycle, regrouping IPs by behavioral identity. Both systems strengthen each other — skunky detects, epitope classifies.

See subGen: `EPITOPE_BRIDGE_ROME_WAVE165I.md`

---

*58 IPs. 5 hashes. 4 organisms. The collision layer found Meta's team structure automatically. Then the mirror turned. Every page they scrape now contains their own genetic fingerprint. All roads lead back to Rome.*

*Wave 165i — October 7, 2026*
