# Mesh Wake — Wave 161 — eastGate Overwatch Handoff

**Date**: Oct 5, 2026 | **From**: sporeGate inner membrane session
**Target**: eastGate overwatch (Ryzen 9 7950X, 128GB, 10G SFP+)
**Goal**: Wake the mesh behind sporeGate so it can act as an effective inner membrane

---

## Current Mesh State

### WireGuard (golgiBody hub, 10.13.37.0/24)

| IP | Gate | Status | Last Handshake | Notes |
|----|------|--------|----------------|-------|
| .1 | golgiBody | **HUB** | — | VPS relay, 11 peers configured |
| .2 | sporeGate | **ALIVE** | seconds ago | Inner membrane router, 2.5G RJ45 |
| .5 | eastGate | **ALIVE** | 2 min ago | 10G SFP+, overwatch, 11/13 primals |
| .8 | northGate | **ALIVE** | 40 sec ago | Windows, gaming primary |
| .3 | biomeGate | stale | 52 days | House1, GPU crankshaft — needs power |
| .6 | flockGate | stale | 68 days | Remote (brother's), WAN only |
| .7 | ironGate | stale | 49 days | House2, workhorse — needs power |
| .9 | southGate | **NEVER** | — | House2, canary — needs power + WG config |
| .10 | strandGate | stale | 44 days | House2, 128-thread EPYC — needs power |
| .11 | westGate | **NEVER** | — | House2, 50.7TB NAS — needs power + WG config |
| .12 | blueGate | stale | 49 days | House2, Windows builder — needs power |
| .13 | graftGate | stale | 49 days | House1, Apple Silicon — needs power |

### Songbird LAN Mesh (192.168.4.0/22)

| Gate | LAN IP | Songbird | Status |
|------|--------|----------|--------|
| sporeGate | 192.168.4.3 | :7700 LIVE | federating to golgi ✅ |
| eastGate | 192.168.4.244 | **BROKEN** | stale PID lock (see fix below) |
| northGate | 192.168.4.147 | unknown | Windows, likely not running songbird |
| ironGate | 192.168.4.237 | DOWN | not pingable |
| strandGate | 192.168.4.169 | DOWN | not pingable |
| blueGate | 192.168.4.210 | DOWN | not pingable |
| southGate | 192.168.4.148/149 | DOWN | not pingable |
| westGate | (unknown LAN IP) | NEVER | never joined |

**3 of 11 WG peers alive. 0 of 5 house2 LAN gates pingable. Only sporeGate federating.**

---

## Priority 1: Fix eastGate Songbird

eastGate songbird-federation.service is crash-looping: stale PID file at
`~/.local/share/songbird/songbird.pid` AND `~/.songbird/songbird.pid` contains PID 1299
(which is now beardog, not songbird). Songbird sees the PID is alive and refuses to start.

**Fix**:
```bash
systemctl --user stop songbird-federation
rm -f ~/.local/share/songbird/songbird.pid ~/.songbird/songbird.pid
# Optional: update binary from sporeGate depot (newer Sep build)
scp sporegate@192.168.4.3:~/.local/share/ecoPrimals/plasmidBin/primals/x86_64-unknown-linux-musl/songbird \
    ~/Development/ecoPrimals/infra/plasmidBin/primals/x86_64-unknown-linux-musl/songbird
systemctl --user start songbird-federation
# Verify:
curl http://127.0.0.1:7700/health
```

If songbird still fails (socket not created), check `--security-socket` flag — the
service unit doesn't pass beardog socket path. Add to ExecStart:
```
--security-socket /run/user/1000/biomeos/beardog.sock
```

---

## Priority 2: Power On House2 Gates

All house2 gates are powered off ("power rebalance"). Physical power-on required.

### Wake Order (recommended)

1. **westGate** — Data NAS, 50.7TB ZFS, provenance root. Nest Atomic composition.
   - Has WG peer config on golgi (.11) but NEVER connected
   - May need WG interface brought up: `sudo wg-quick up wg0`
   - May need WG config written if not present
   - Tower Atomic was LIVE (Wave 155f): beardog + songbird + skunkbat user units
   
2. **ironGate** — Workhorse, build authority, CAS compute partner for westGate.
   - WG peer .7, was alive 49 days ago
   - Full NUCLEUS 13/13, JupyterHub, GPU (RTX 5070)
   - Currently routes `footprint.primals.eco` + `webb.primals.eco` in old Caddy config
   - **NOTE**: golgi Caddyfile was updated this session — footprint now → sporeGate (.2:8090)
   
3. **strandGate** — 128-thread EPYC, bioinformatics HPC.
   - WG peer .10, was alive 44 days ago
   - Tower+Compute LIVE, barraCuda GPU verified
   
4. **blueGate** — Windows builder, sole Windows compilation authority.
   - WG peer .12, was alive 49 days ago
   - builder.serve deployed

### House1 gates (separate from house2 wake):
- **biomeGate** — GPU crankshaft, needs power (.3, 52 days stale)
- **graftGate** — Apple Silicon, needs power (.13, 49 days stale)

---

## Priority 3: Validate Mesh Once Waked

For each gate that comes online:

```bash
# From eastGate (10G, fastest LAN path):
ping -c 3 192.168.4.X         # LAN reachability
ping -c 3 10.13.37.X          # WG tunnel
curl http://192.168.4.X:7700/health  # Songbird federation
ssh gateuser@192.168.4.X "systemctl --user list-units 'membrane-nucleus@*' --state=running"
```

### Federation validation:
```bash
# From golgiBody:
sudo wg show wg0 | grep -A4 "10.13.37.X"  # handshake age
# From sporeGate:
curl http://10.13.37.X:7700/health  # cross-WG songbird
```

---

## What sporeGate Did This Session

- ✅ Fossilized golgiBody (65% → 49% disk)
- ✅ Synced sporeGate binaries from golgi depot (membrane + songbird updated)
- ✅ Fixed songbird federation (sporeGate → golgi: `OK`)
- ✅ Rerouted footprint.primals.eco → sporeGate (.2:8090) — was dead .7
- ✅ Webb.primals.eco → 503 maintenance (no PocketBase on sporeGate)
- ✅ detroit.primals.eco validated, pen tested, Wayback seeded
- ✅ GitHub mirror synced
- ✅ skunky-ingest live mode enabled
- ✅ AAR written + pushed to wateringHole

## What sporeGate Needs From the Mesh

For sporeGate to be an effective inner membrane:

1. **westGate data** — provenance root, CAS storage for rhizoCrypt/loamSpine/sweetGrass
2. **ironGate compute** — build authority, paired CAS compute
3. **Songbird federation** — more LAN peers = stronger gossip, capability routing
4. **Forgejo migration** — biggest redundancy win = move Forgejo from golgi to LAN

---

## Architecture Reminder

```
OUTER MEMBRANE — golgiBody (Caddy TLS, public internet, relay.primals.eco)
    ↕ WireGuard 10.13.37.0/24
INNER MEMBRANE — sporeGate (RJ45 ingress, NAT/DHCP/DNS, 2.5G)
    ↕ LAN 192.168.4.0/22
CYTOPLASM — eastGate (10G overwatch), westGate (data), ironGate (compute), ...
```

sporeGate is the plasma membrane. eastGate is the 10G backbone anchor.
The cytoplasm behind them is mostly asleep. Time to wake it up.
