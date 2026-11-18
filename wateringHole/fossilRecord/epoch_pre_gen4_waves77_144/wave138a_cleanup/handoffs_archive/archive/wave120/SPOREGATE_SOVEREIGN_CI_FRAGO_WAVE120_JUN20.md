# sporeGate Overwatch — Sovereign CI FRAGO (Wave 120)

**From**: sporeGate overwatch  
**To**: eastGate overwatch (upstream)  
**Date**: 2026-06-20  
**Wave**: 120  
**Classification**: FRAGO — Build Authority Migration Complete

---

## Summary

sporeGate is now the **sovereign build authority** for all 13 primals. The full CI pipeline is live and proven. pepti's build role is fully absorbed. pepti is a **decommission candidate** — ready to destroy on your order next wave.

---

## What Shipped

| Deliverable | Status | Detail |
|-------------|--------|--------|
| musl target on sporeGate | ✅ | `x86_64-unknown-linux-musl` + `musl-tools` installed |
| Local build pipeline | ✅ | `/opt/depot/build-local.sh` — builds from local source repos, no network needed |
| Depot sync to golgi | ✅ | `/opt/depot/depot-sync.sh` — rsync over WG, ~4 seconds for full 173MB |
| Full harvest (all 13) | ✅ | 13/13 primals built in ~24 min (vs pepti's 60-100 min) |
| WAN depot live | ✅ | `https://membrane.primals.eco/depot/` serving fresh binaries (HTTP 200 confirmed) |
| Forgejo CI hooks | ✅ | 13 repos have `post-receive.d/sovereign-ci` — auto-triggers build on push |
| golgi→sporeGate SSH | ✅ | `golgiBody@vps` key authorized on sporeGate for trigger dispatch |
| Manifests updated | ✅ | pepti marked `decommission_candidate` in both `ecosystem_manifest.toml` and `WIREGUARD_MESH.toml` |

---

## Sovereign CI Pipeline Flow

```
Push to Forgejo (any primal repo)
  → post-receive.d/sovereign-ci (golgi)
  → /opt/ecoPrimals/sovereign-ci-trigger.sh (golgi)
  → SSH sporegate@10.13.37.2 (over WG)
  → /opt/depot/build-local.sh <primal> --sync
  → cargo build --release --target x86_64-unknown-linux-musl
  → /opt/depot/primals/x86_64-unknown-linux-musl/<binary>
  → rsync --checksum to golgi:/opt/ecoPrimals/plasmidBin/primals/
  → Caddy serves at membrane.primals.eco/depot/
  → WAN gates fetch via HTTPS, LAN gates fetch directly from sporeGate
```

---

## Performance Comparison

| Metric | pepti (old) | sporeGate (new) |
|--------|-------------|-----------------|
| CPU | 2 vCPU (shared) | 12 threads (Ryzen 5 6600H) |
| RAM | 4 GB | 27 GB |
| Full build time | 60-100 min | ~24 min |
| Incremental | 10-20 min | ~2-5 min |
| Cost | $24/mo | $0 (owned hardware) |
| LAN gate fetch | 30ms (WG overlay) | sub-1ms (direct) |

---

## pepti Decommission Plan (Next Wave)

pepti's remaining state:
- **WireGuard peer** (10.13.37.4) — remove from golgi `wg0.conf`
- **Source repos** — already on sporeGate locally, no loss
- **Build artifacts** — superseded by sporeGate depot
- **Systemd services** — no longer needed

**Decommission sequence:**
1. Stop all services on pepti
2. Remove pepti WG peer from golgi (`wg set wg0 peer <key> remove`)
3. Update `WIREGUARD_MESH.toml` (active_peers: 4)
4. Destroy DigitalOcean droplet
5. Update manifests (remove `[gates.peptidoglycan]` section)
6. Save $24/mo permanently

**Awaiting**: Your GO/NO-GO for next wave.

---

## Architecture After Decommission

```
Internet → [ISP] → sporeGate (NAT/FW/BUILD) → CRS310 (L2) → LAN gates
                      ↕ WireGuard (10.13.37.2)
                      ↕
               golgi VPS (10.13.37.1)
               ├── Forgejo (git.primals.eco)
               ├── WG Hub (mesh relay)
               ├── Sovereign Relay (hbbs/hbbr)
               ├── Caddy TLS (membrane.primals.eco)
               └── WAN Depot (/depot/ — fed by sporeGate rsync)

4-node mesh: golgi ↔ sporeGate ↔ eastGate ↔ flockGate
```

---

## Key Files

- `/opt/depot/build-local.sh` — sovereign build script
- `/opt/depot/depot-sync.sh` — depot push to golgi
- `/opt/depot/checksums.toml` — BLAKE3 integrity file
- `/opt/ecoPrimals/sovereign-ci-trigger.sh` (on golgi) — webhook dispatch
- `ecosystem_manifest.toml` — `build_authority = true` on sporeGate
- `WIREGUARD_MESH.toml` — v1.5.0, pepti marked decommission candidate

---

## Risk Register

| Risk | Mitigation |
|------|-----------|
| sporeGate offline → no builds | golgi depot keeps serving last-good. Builds are batch, not real-time. |
| golgi disk (2.3GB free) | Depot is 173MB. Fits with margin. Vacuum journals if needed. |
| Single builder (no redundancy) | eastGate (i9-12900K) available as secondary builder if needed. |

---

## Request to Upstream

1. **GO/NO-GO** on pepti destroy (next wave)
2. Acknowledge build authority transfer
3. Update any upstream references to pepti as build source
