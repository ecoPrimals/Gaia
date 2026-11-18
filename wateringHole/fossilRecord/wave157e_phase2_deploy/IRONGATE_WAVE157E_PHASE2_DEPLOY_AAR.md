# ironGate Wave 157e — Phase 2 Deploy AAR

**Date**: 2026-08-10 11:37 EDT
**Gate**: ironGate (10.13.37.7)
**Wave**: 157e — MESH DEPLOY
**From**: ironGate hardware team
**To**: eastGate overwatch

---

## Summary

ironGate Phase 2 deployed from rebuilt golgi depot. 15 binaries replaced (pepti-layer depot), NUCLEUS restarted: 13/13 alive. Dispatch 4ms. Vine-bat operational. 166 capabilities across 8 services. 84 MB RSS. westGate in mesh (direct LAN).

---

## Execution

### 1. Cascade — 21 repos pulled
Major updates: barraCuda (video_codec), bearDog (riboCipher handoff), biomeOS (depot_lineage_batch), coralReef (sync_stream), loamSpine (13 files), petalTongue (webgl_bridge), songBird (transport_impl), swarmVine (ribocipher), cellMembrane (dispatch/builder), sporePrint (260 LOC).

### 2. Depot Pull — 16/16 binaries (pepti-layer unified)
All 16 binaries pulled from `depot.primals.eco` (pepti-layer, Caddy-direct).

**Feature verification before deploy:**
- biomeos: 4.57.0, `discovery_gossip.rs` (gossip table wire) PRESENT
- songbird: `gossip.inject` seam + `MEMBRANE_GATE_NAME` PRESENT
- swarmvine: `SWARMVINE_SKUNKBAT_SOCK` + vine-bat hook PRESENT
- skunkbat: `metadata.analyze` PRESENT

### 3. Binary Replacement

| Binary | Depot Size | Previous | Delta |
|--------|-----------|----------|-------|
| biomeos | 17 MB | 21 MB | musl vs glibc |
| songbird | 19 MB | 24 MB | musl vs glibc |
| barracuda | 8.8 MB | 12 MB | smaller |
| coralreef | 9.1 MB | 7.6 MB | +1.5 MB (sync_stream) |
| squirrel | 8.7 MB | 4.4 MB | +4.3 MB (new features) |
| swarmvine | 2.5 MB | 2.4 MB | +0.1 MB |
| skunkbat | 3.3 MB | 3.2 MB | +0.1 MB |
| *(11 others)* | *similar* | — | — |

### 4. NUCLEUS Restart — 13/13 ALIVE

Services: songbird, biomeos, barracuda, beardog, coralreef, loamspine, nestgate, petaltongue, rhizocrypt, skunkbat, squirrel, sweetgrass, swarmvine.

**toadStool**: Disabled — depot binary CLI changed (requires `biome.yaml` manifest, `--foreground` removed). Non-blocking divergence, same as strandGate AAR noted.

**sourDough**: No service file configured (new primal, not yet in NUCLEUS service template).

---

## Verification

| Check | Result |
|-------|--------|
| Dispatch latency | **4ms** (capability.call → health.liveness) |
| Vine-bat loop | **OPERATIONAL** (gossip.spread → accepted:1) |
| Capabilities | **166** across 8 registered services |
| FD limits | **65536** (biomeos, songbird, swarmvine, skunkbat) |
| Mesh peers | **1** (westGate direct LAN, 192.168.4.149:7700) |
| Cross-gate replication | **CONFIRMED** (westGate braid pen test Level 7 PASS) |
| RSS | **84 MB** total (13 services) |

---

## Final State

```
Wave:          157e
Services:      13/13 active
Binaries:      15/16 depot (toadstool disabled)
biomeOS:       4.57.0 (musl, dispatch 4ms, gossip table wire)
songBird:      0.2.1 (musl, gossip seam, mesh 1 peer)
swarmVine:     Phase 2 (musl, vine-bat hook, TCP :7800)
skunkBat:      metadata.analyze (8-check, vine-bat pre-accept)
Capabilities:  166 across 8 services
RSS:           84 MB
FD limits:     65536
Mesh:          westGate (direct LAN)
```

---

## Non-Blocking Items

1. **toadStool CLI change**: `up` now requires `<MANIFEST>` (biome.yaml). Service disabled. Needs biome.yaml template or `toadstool run` adaptation.
2. **sourDough**: No systemd service file — needs `membrane-nucleus@sourdough.service` template.
3. **nestgate socket path**: Running on TCP :8091 (tarpc), not UDS. songbird registry points to stale `/run/user/1000/biomeos/nestgate.sock`. Needs nestgate self-registration or socket symlink.
4. **Mesh peers**: Only westGate visible (direct LAN). Other gates may not be online or may need WireGuard mesh refresh.

---

## ironGate Phase 2: DEPLOYED
