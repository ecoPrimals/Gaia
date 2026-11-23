# AAR: westGate G68 Gate Redeploy + NG-05 CAS Federation

**Gate**: westGate | **Wave**: 157a (G68) | **Date**: Aug 8, 2026
**Session**: ~25 min | **Operator**: overwatch/eastGate

---

## What Happened

Two tasks from the Wave 157a blurb executed in sequence:

### 1. Gate Redeploy from Golgi Depot

Pulled all 17 G68-converged musl binaries from `depot.primals.eco` (HTTP file
server on golgi). No local building — binaries are static-linked
`x86_64-unknown-linux-musl`, built by sporeGate and pushed to golgi on Aug 7.

**Pattern**: stop all → pull from depot → restart in dependency order.

```
depot.primals.eco/primals/x86_64-unknown-linux-musl/{primal}
→ curl → /home/westgate/.../plasmidBin/primals/{primal}
→ systemctl --user restart
```

| Step | Detail |
|------|--------|
| Pull | 17/17 binaries from golgi via HTTPS, ~15s total |
| Stop | `systemctl --user stop` all 13 tower services |
| Start order | provenance chain (nestgate, loamspine, rhizocrypt, sweetgrass, beardog) → biomeOS → remaining |
| Result | **13/13 active**, all G68-converged (Aug 7 builds) |

**Key learning**: initial instinct was to rebuild locally from cascaded source
(`cargo build --release`). User corrected: "we should be deploying from golgi
depot, not building." SporeGate already built everything — gate teams just pull.
This is the intended deployment topology: build once on sporeGate, push to golgi
depot, gates pull and restart.

### 2. NG-05: nestGate TCP + songBird Content Registration

This was the last westGate-owned blocker from the nestgate.io dashboard AAR.

**What was already working**:
- nestGate TCP on `0.0.0.0:8080` (was configured in the systemd unit)
- nestGate UDS at `/run/user/1000/membrane/nestgate-westgate-tower-155f.sock`
- songBird mesh with ironGate peer visible at `192.168.4.213:7700`
- songBird auto-discovered primals (coralreef, petaltongue, math) but without
  capability metadata

**What was missing**:
- songBird had no knowledge of nestGate's `content.*` capabilities
- No primal in the provenance chain was registered with capabilities
- `capability.resolve("content.get")` returned nothing
- nestgate.io Data Braids section couldn't query westGate CAS

**What we did**:
Registered the full provenance chain with songBird via `ipc.register`:

| Primal | Capabilities Registered |
|--------|------------------------|
| nestgate | content.get, content.put, content.ingest, content.stat, content.exists, content.list |
| loamspine | spine.list, spine.status, entry.list, session.commit, anchor.publish, anchor.verify, slice.anchor, slice.checkout |
| rhizocrypt | dag.event.append, dag.event.append_batch, dag.query, dag.session.create, dag.session.commit |
| sweetgrass | braid.create, braid.verify, braid.batch_create, convergence.check |
| beardog | identity.sign, identity.verify, identity.public_key |

**Verification**:
- `capability.resolve("content.get")` → nestgate ✓
- `capability.resolve("braid.create")` → sweetgrass ✓
- `capability.resolve("spine.list")` → loamspine ✓
- `capability.resolve("identity.sign")` → beardog ✓
- nestGate TCP health check from LAN IP (`192.168.4.149:8080`) ✓
- 10 services registered with songBird (5 provenance chain + 5 auto-discovered)

**Persistence**: created `songbird-register.service` (systemd oneshot, enabled at
boot) + `songbird-register.sh` script. Runs after songBird starts, idempotent
(handles "already registered" gracefully).

---

## CAS Pool Status

| Tier | Path | Size |
|------|------|------|
| Warm (NVMe) | /mnt/cas-hot/ | 1.1 TB |
| Cold (ZFS) | /mnt/nestgate/cold/zfs/cas/ | 1.4 TB |
| **Total** | | **~2.5 TB** |

CAS data organized under `datasets/` namespace hierarchy, not loose `objects/`
buckets. Multi-tier CAS with 10 GB high-water mark backpressure on warm tier.

---

## What Unblocks

1. **nestgate.io Data Braids**: sporeGate topology team can now wire
   `/api/content/stats` in petalTongue against westGate's nestGate TCP endpoint
   (`192.168.4.149:8080`). The songBird `capability.resolve("content.get")`
   path is live.

2. **Cross-gate content.replicate.pull**: ironGate can sync CAS objects from
   westGate via the TCP endpoint.

3. **Neural API capability routing**: biomeOS on westGate can now resolve
   provenance chain capabilities through songBird IPC, not just direct socket
   paths.

---

## Patterns for the Ecosystem

### Deploy from depot, don't build
Gates should never `cargo build` primal binaries. SporeGate builds once
(musl-static), pushes to golgi depot, gates pull via HTTPS. Total deploy time:
~30 seconds vs ~20 minutes for a full rebuild. The depot at
`depot.primals.eco/primals/{arch}/` serves static files via Caddy.

### songBird IPC registration is the capability advertisement layer
Auto-discovery finds primals but doesn't know their capabilities. Explicit
`ipc.register` with capability lists is required for `capability.resolve` to
work. Each gate needs a registration script that runs after songBird starts.
This is a gap — primals should self-register their capabilities with songBird
on startup (upstream enhancement).

### TCP listener is the federation surface
UDS is for local IPC. TCP is for mesh/inter-gate access. Both are served by
the same binary (`--socket` for UDS, `--port` + `--bind` for TCP). The TCP
endpoint is what other gates, petalTongue dashboards, and external consumers
hit.

---

## Files Changed

| File | Change |
|------|--------|
| `~/.config/systemd/user/songbird-register.sh` | New — IPC registration script |
| `~/.config/systemd/user/songbird-register.service` | New — systemd oneshot, enabled |
| `plasmidBin/primals/*` | 17 binaries replaced from golgi depot |

---

## Remaining Owned Work

| Item | Status |
|------|--------|
| Gate redeploy | **DONE** — 13/13 alive, G68 depot binaries |
| NG-05 federation | **DONE** — TCP live, 5 primals registered, capability resolve working |
| nestgate.io Data Braids backend | Upstream — sporeGate topology team (petalTongue `/api/content/stats`) |
| Primal self-registration | Upstream — primals should `ipc.register` on startup |

---

*westGate G68 gate redeploy: 17 binaries from golgi depot in 15 seconds, 13/13
alive. NG-05 federation: nestGate TCP on 0.0.0.0:8080, full provenance chain
registered with songBird (26 capabilities across 5 primals),
capability.resolve working. CAS pool at 2.5 TB across warm+cold. Deploy from
depot, don't build. Register capabilities explicitly until primals learn to
self-register.*
