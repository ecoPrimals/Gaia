# Handoff: Immune System Wiring — eastGate Team

**Wave**: 165e | **Date**: Oct 6, 2026
**From**: sporeGate overwatch session
**To**: eastGate development team (next session)
**Priority**: HIGH — gossip wiring complete, needs build + deploy + consumer

---

## What Was Done (sporeGate — this session)

### ✅ Completed — Ready for Build

| Item | Files Changed | What It Does |
|------|--------------|--------------|
| **gossip.inject proxy** | `skunk-bat-server/src/ipc/dispatch_gossip.rs` (NEW, 218 LOC) | Proxies gossip.inject from skunkBat TCP → swarmVine UDS. Socket discovery: `SWARMVINE_SOCKET` → `$XDG_RUNTIME_DIR/biomeos/swarmvine.sock` → `/run/membrane/swarmvine.sock` |
| **dispatch wiring** | `dispatch.rs` (+6 LOC) | Added `gossip.inject` and `gossip.query` match arms |
| **antibody emission** | `dispatch_fleet.rs` (+10 LOC) | Emits `defense.antibody:{id}` on new fleet detection |
| **escalation emission** | `dispatch_fleet.rs` (+8 LOC) | Emits `defense.escalation:{id}` on posture change |
| **defense domain** | swarmVine `dispatch.rs` + `capability_registry.toml` | Added `"defense"` to `gossip_domains` |

### ✅ Completed — Deployed Live

| Item | Details |
|------|---------|
| **Forge lockdown** | Existence-only storefront on git.primals.eco (Caddy config) |
| **JS challenge** | Layer 7.25 blocks zero-JS fleets |
| **API block** | `/api/*` → 403 JSON |
| **Default scatter** | Everything not in storefront allowlist → scatter |

---

## What Needs Doing (eastGate)

### P1: Build and Deploy skunkBat + swarmVine

The gossip wiring code is committed but not compiled or deployed.

```bash
# On eastGate (build host):
cd /path/to/skunkBat && cargo build --release
cd /path/to/swarmVine && cargo build --release

# Deploy to golgiBody:
scp target/release/skunkbat root@10.13.37.1:/opt/membrane/skunkbat
scp target/release/swarmvine root@10.13.37.1:/opt/membrane/swarmvine
ssh root@10.13.37.1 'systemctl restart skunkbat && systemctl restart swarmvine'
```

**Verify**: After restart, skunky-ingest's `gossip.inject` calls should
succeed instead of returning `unknown method`. Check journal:
```bash
journalctl -u skunkbat -f | grep gossip
```

### P2: Implement Opsonize Consumer (medium effort)

**What**: When a gate receives `defense.opsonize:{hash}` via gossip, it
should merge the tag into its local `SharedConfidence` and activate scatter
routing for matching behavioral patterns.

**Where**: Either:
- New module in skunky-ingest that subscribes to `defense` topic via
  `gossip.query` polling (simpler, no new daemon)
- Or add a gossip subscription callback in skunkBat (cleaner, more work)

**Key types** (all in `cellmembrane-types/src/fleet.rs`):
- `OpsonizeTag` — contains behavioral_hash, detectors, confidence, invariants
- `OpsonizeResponse` — scatter ratio to apply
- `BehavioralInvariants` — the conserved epitope for fuzzy matching

**How the consumer should work**:
1. Poll `gossip.query` for `topic: "defense"` periodically (e.g., every 30s)
2. For each `defense.opsonize:*` entry, deserialize `OpsonizeTag`
3. If `behavioral_hash` matches a locally-observed fleet pattern → merge
   confidence, update scatter ratio
4. If hash is new → store as "received antibody" for future matching
5. Merge `detectors` list (union of local + remote detectors)

### P3: Behavioral Self-Profile (design + medium effort)

**What**: Extend self/non-self recognition beyond IP-only (`self-ips.txt`)
to behavioral fingerprinting. The system should baseline "what does my own
traffic look like?" and flag deviations.

**Where**: `skunky-ingest/src/lysogeny.rs` already has self-IP behavioral
anomaly detection. Extend to:
- Baseline authenticated session patterns (timing, path diversity, UA)
- Baseline WireGuard traffic patterns (gate → forge behavior)
- Generate "self behavioral profile" that the fleet detector can exclude

**Why this matters**: The residential proxy fleet passed all individual
request checks (valid Chrome UA, Accept-Language, Accept-Encoding) because
the immune system only knew "this IP is me" not "this behavioral pattern
looks like me." Population-level analysis (zero static assets) caught them,
but a behavioral self-profile would catch the divergence faster.

### P4: songbird Connection Pooling with Backoff

**What**: songbird federation connections pile up under ISP degradation.
160 ESTABLISHED connections from home WAN to golgiBody:7700 when bandwidth
dropped to 50 KB/sec. Positive feedback loop: degraded ISP → stalled
connections → more bandwidth consumed → worse degradation.

**Where**: songbird federation client connection management

**Fix**: Implement exponential backoff and connection pooling. Max N
concurrent federation connections per peer (suggest 3-5). If connection
fails, backoff before retry. If all connections are stalled, stop opening
new ones until at least one completes.

### P5: Full Thymic Selection (larger project)

**What**: `specs/THYMIC_SELECTION_SPEC.md` describes a full thymic training
loop where BearDog lineage trains skunkBat detectors. This is the
"proactive self-recognizing mixing immune cells" architecture.

**Status**: Spec complete. BearDog `lineage.verify`/`lineage.list` IPC
implemented. skunkBat `RemoteLineageVerifier` implemented. Training loop
not built.

**Defer until**: P1-P3 are deployed and cross-gate immune memory is
validated in production.

---

## Verification Checklist

After P1 (build + deploy):

- [ ] `gossip.inject` on skunkBat returns success (not `unknown method`)
- [ ] skunky-ingest opsonize emission logs show success
- [ ] `gossip.query` with `topic: "defense"` returns stored entries
- [ ] `defense.antibody:*` entries appear in swarmVine gossip store
- [ ] `defense.escalation:*` entries appear on posture changes
- [ ] swarmVine `capabilities.list` shows `defense` in `gossip_domains`

After P2 (opsonize consumer):

- [ ] Remote gate receives opsonize tags from golgiBody
- [ ] Remote gate activates scatter for matching behavioral patterns
- [ ] Antibody count matches across gates (fuzzy — propagation lag OK)

---

## Context Links

- **AAR**: `wateringHole/aars/ACTIVE_DEFENSE_FORGE_LOCKDOWN_WAVE165_AAR.md`
- **Forge lockdown config**: `skunkBat/infra/membrane/git-block-inverted.caddy`
- **Gossip proxy**: `skunkBat/crates/skunk-bat-server/src/ipc/dispatch_gossip.rs`
- **Reference gossip client**: `barraCuda/crates/barracuda-core/src/ipc/gossip.rs`
- **Thymic spec**: `skunkBat/specs/THYMIC_SELECTION_SPEC.md`
- **Fleet immune AAR**: `skunkBat/specs/THYMIC_NEGATIVE_SELECTION_FLEET_IMMUNE.md`
- **detroit billboard**: `https://detroit.primals.eco/signal/`
- **sporePrint science**: `https://sporeprint.primals.eco/architecture/forge-lockdown/`

---

*Filed: Wave 165e | Oct 6, 2026 | sporeGate inner membrane*
