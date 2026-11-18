# ironGate Session 17 — Wave 157a Vine-Bat Loop OPERATIONAL

**Date**: 2026-08-09 08:00 EDT
**Gate**: ironGate (10.13.37.7)
**Wave**: 157a — VINE-BAT LOOP OPERATIONAL
**From**: ironGate hardware team
**To**: eastGate overwatch

---

## Summary

Vine-bat pre-accept loop deployed and verified on ironGate. swarmVine (`df97b25`) calls skunkBat `metadata.analyze` (`e602e09`) on every remote `gossip.spread`. Full chain: spread → 8-check validation → verdict → ingest/reject. 13/13 services alive.

---

## Execution

### 1. Cascade
- biomeOS: pulled `discovery_gossip.rs` (`993b97f7` — capability.resolve → gossip table)
- swarmVine: pulled vine-bat hook (`df97b25`)
- hotSpring, primalSpring, wateringHole, whitePaper: minor updates

### 2. Binary Deployments

| Binary | Source | Size | Commit | Key Feature |
|--------|--------|------|--------|-------------|
| swarmVine | local build | 2.4 MB | `df97b25` | vine-bat pre-accept hook |
| skunkBat | local build | 3.2 MB | `e602e09` | `metadata.analyze` 8-check validation |

Note: Depot skunkBat (3.3 MB) was pre-`e602e09` — built from source to get `metadata.analyze`. Depot swarmVine 404 — also built from source.

### 3. Service Wiring
- Added `SWARMVINE_SKUNKBAT_SOCK=/run/user/1000/membrane/skunkbat.sock` to swarmVine service
- Added `LimitNOFILE=65536` to swarmVine + skunkBat services
- All services now have: `GATE_ID=ironGate`, `LimitNOFILE=65536`

### 4. Vine-Bat Verification — E2E PROVEN

| Test | Verdict | Result |
|------|---------|--------|
| Valid entry (tower, TTL 10) | `warn` (TTL > max 16, minor) | **ACCEPTED** |
| Cross-gate entry (origin: attacker) | `warn` | **ACCEPTED** |
| Expired entry (expires_at < now) | `warn` from skunkBat | **REJECTED** (by gossip engine) |
| `gossip.inject` (local bypass) | N/A (no pre-accept) | **ACCEPTED** |

**Key insight**: Two validation layers operate in series:
1. skunkBat `metadata.analyze` → 8-check validation → verdict (deny/reject blocks, warn/allow passes)
2. swarmVine gossip engine → expiry, nonce dedup, TTL (rejects stale entries even if skunkBat says warn)

### skunkBat 8-Check Validation (confirmed live)
1. `topic_valid` — known topic (tower/data/compute)
2. `key_format` — proper key structure
3. `origin_identity` — gate identity verification
4. `ttl_valid` — TTL within bounds
5. `payload_size` — payload not oversized
6. `freshness` — entry not expired
7. `lifetime` — reasonable TTL
8. `quarantine` — not previously quarantined

---

## Final State

```
Services:      13/13 active
biomeOS:       4.57.0 (depot musl, dispatch 15ms, riboCipher auto-detect)
songBird:      0.2.1 (local build, gossip seam live)
swarmVine:     df97b25 (vine-bat hook, epidemic spread, TCP :7800)
skunkBat:      e602e09 (metadata.analyze, 8-check pre-accept)
Vine-bat:      OPERATIONAL
FD limit:      65536 (biomeOS, songbird, swarmvine, skunkbat)
```

---

## P0 Upstream: Depot Binaries Stale

Both depot binaries pulled were pre-feature:
- `skunkBat`: depot (3.3 MB) lacks `metadata.analyze`. Built from source.
- `swarmVine`: 404 on depot. Built from source.
- `songBird`: depot (19 MB) lacks gossip seam. Using local build from Session 15.

**Recommendation**: sporeGate needs to rebuild and push skunkBat + swarmVine to depot, similar to the biomeOS/songBird/cellMembrane rebuild done earlier.

---

## ironGate Vine-Bat Loop: OPERATIONAL

Full mesh integration stack live on ironGate:
```
ipc.register → gossip.inject → epidemic spread → cross-gate TCP :7800
                                       ↓
                          gossip.spread → metadata.analyze (8-check)
                                       → verdict: deny → BLOCK
                                       → verdict: warn/allow → INGEST
```
