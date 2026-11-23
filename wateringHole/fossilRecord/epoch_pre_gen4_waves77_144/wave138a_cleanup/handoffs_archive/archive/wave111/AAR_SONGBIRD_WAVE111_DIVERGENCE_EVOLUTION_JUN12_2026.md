# AAR: songBird — Wave 111-113 Divergence Evolution

**Date**: 2026-06-12  
**Team**: songBird  
**Waves**: 111 → 113  
**Stream 6 Score**: 4/4 SHIPPED (ALL COMPLETE)  
**Key Commits**: f18aeb6b (Wave 111), 32a8d700 (Wave 112), 9903cf50 (Wave 113)

---

## Shipped (Stream 6 Divergence Scenarios — ALL COMPLETE)

### FEDERATION-STATUS-WIRE (f18aeb6b, Wave 111)
- **Scenario**: `federation.status` RPC reports `enabled: false` despite port bound
- **Solution**: Read `SONGBIRD_FEDERATION_ENABLED`, `SONGBIRD_PEERS`, `SONGBIRD_FEDERATION_PORT` env vars in bin_interface UDS/TCP path
- **Pattern**: Status RPC reflects runtime config, not compile-time defaults
- **Deprecates**: Hardcoded `false` in federation status response

### FEDERATION-RECONNECT (f18aeb6b, Wave 111)
- **Scenario**: Kill VPS songBird, restart after 60s — does flockGate auto-reconnect?
- **Solution**: `spawn_peer_health_loop` — 30s probe with exponential backoff (30→60→120→cap 300s). Auto-reconnects via `record_direct_connection()`.
- **Pattern**: Mesh peers self-heal after transient failures without manual `mesh.init`
- **Deprecates**: Manual `mesh.init` after every VPS restart or network hiccup

### MESH-PARTITION-TOLERANCE (9903cf50, Wave 113)
- **Scenario**: Split mesh — VPS reachable from eastGate but not from flockGate
- **Solution**: Cross-gate reachability gossip via `mesh.capabilities_announce`. `PeerMetadata` tracks per-peer version + cross-gate views. `partition_status_for()` computes `PartialPartition` / `LocallyUnreachable`. `mesh.status` and `mesh.health_check` surface partition warnings.
- **Pattern**: Mesh topology is observable — partitions are detected, not invisible
- **Deprecates**: Mesh assumes full connectivity, silent failures on unreachable peers

### PEER-VERSION-MISMATCH (9903cf50, Wave 113)
- **Scenario**: songBird v0.2.0 on one gate, v0.2.1 on another — do they mesh?
- **Solution**: `probe_peer_full()` extracts version from `health.ping` response. `spawn_peer_health_loop` records peer versions. `mesh.status` reports `version_skew` array. `mesh.peers` includes `version` and `version_mismatch` per peer. Backward-compatible wire protocol.
- **Pattern**: Version diversity is observable and wire-protocol is backward-compatible
- **Deprecates**: Protocol breaks on minor version bumps, invisible version skew

---

## Additional Evolution (Non-Stream-6)

### Wave 112 Deep Debt (32a8d700)
- Hardcoding elimination
- Stub replacements with real health probes (env-only → TCP probes)
- Dependency hoisting
- Security provider naming made agnostic
- Test count: 8918 total passing

### Wave 113 Documentation (fe47c012)
- Root docs updated to Wave 113 state
- Total test count documented: 8918

---

## Convergence Criteria for songBird

All Stream 6 scenarios are SHIPPED. songBird convergence depends on:

1. ✅ All 4/4 divergence scenarios implemented and tested
2. ❌ Depot rebuild needed — current depot has `32a8d700`, need `fe47c012`+
3. ❌ flockGate WAN handshake validated with fresh binary
4. ✅ Wire protocol is backward-compatible (v0.2.0 and v0.2.1 can mesh)

**Single blocker**: `plasmid.harvest --targets songbird` on VPS to build from HEAD.
Once deployed to flockGate, federation is fully validated.

---

## Old Patterns Deprecated by songBird Evolution

| Old Pattern | New Pattern | Since |
|-------------|-------------|-------|
| Manual `mesh.init` after restart | Auto-reconnect via peer_health_loop | f18aeb6b |
| Status RPC lies about federation state | Runtime config reflected in responses | f18aeb6b |
| Mesh blind to partitions | Reachability gossip + partition detection | 9903cf50 |
| Protocol break on version bump | Backward-compatible wire + version_skew reporting | 9903cf50 |
| Hardcoded probe endpoints | TCP health probes via capability resolution | 32a8d700 |

---

## Test State

- 8918 tests passing (Wave 113)
- Zero clippy warnings
- Backward-compatible wire protocol (no breaking changes between versions)
