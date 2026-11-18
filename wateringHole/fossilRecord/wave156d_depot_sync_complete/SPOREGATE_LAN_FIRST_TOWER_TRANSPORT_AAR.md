# AAR: LAN-First Tower Transport — WG → Outer Membrane Only

**Date**: Aug 4, 2026 | **Wave**: 156d | **From**: eastGate overwatch (sporeGate)
**Status**: PROVEN + DEPLOYED on sporeGate + ironGate. Overwatch will cascade to remaining gates.

---

## What We Did

Shifted inter-gate transport from **WireGuard-centric** (all traffic through golgi VPS)
to **LAN-first** (songBird Tower Atomic on local TCP, WG as outer membrane fallback).

### Before
```
sporeGate ── WG tunnel ──→ golgi (VPS) ──→ WG tunnel ──→ ironGate
                         ~36ms                ~75ms total
```
Every inter-gate RPC routed through a VPS in New York, even for gates on
the same LAN in the same room.

### After
```
sporeGate ── LAN TCP :7700 ──→ ironGate       ~1ms  (priority 0, Local)
sporeGate ── LAN TCP :7700 ──→ eastGate        ~1ms  (priority 0, Local)
sporeGate ── LAN TCP :7700 ──→ blueGate        ~1ms  (priority 0, Local)
sporeGate ── WG overlay    ──→ golgi          ~36ms  (priority 1, Overlay)
sporeGate ── WG overlay    ──→ flockGate      ~36ms  (priority 1, Overlay)
```

### Measured Performance

| Path | RTT | Factor |
|------|-----|--------|
| LAN direct (192.168.4.x:7700) | **~1ms** | 1× (baseline) |
| WG overlay → golgi hub | ~36ms | 36× slower |
| WG overlay → eastGate via golgi | ~77ms | **77× slower** |
| WG overlay → ironGate via golgi | ~75ms | 75× slower |

---

## What Worked

### 1. songBird EndpointType already supports LAN-first

songBird has a built-in priority system:
- Priority 0: `Local` (same-LAN TCP)
- Priority 1: `Overlay` (WireGuard)
- Priority 2: `Direct` (WAN)
- Priority 3+: `FamilyRelay`, `TorOnion`

`get_best_path()` always picks lowest priority. **The code was already correct** —
we just needed to tell songBird which peers are LAN.

### 2. `mesh.init` with `lan_peers` parameter

Passing `lan_peers` in the `mesh.init` JSON-RPC registers endpoints as
`EndpointType::Local` (priority 0). This is separate from `bootstrap_peers`
(which default to `Direct`, priority 2) and `overlay_peers` (priority 1).

### 3. Systemd drop-in for persistence

Created `/etc/systemd/system/songbird-gateway.service.d/lan-first.conf`:
```ini
[Service]
Environment=SONGBIRD_LOCAL_PEERS=eastGate@192.168.4.244:7700,ironGate@192.168.4.237:7700,blueGate@192.168.4.210:7700,strandGate@192.168.4.169:7700
```

And updated `/usr/local/bin/songbird-mesh-init.sh` to pass `lan_peers`
in the `mesh.init` RPC after socket readiness.

### 4. dnsmasq primal.eco inner membrane DNS

Deployed `/etc/dnsmasq.d/primal-eco.conf` on sporeGate — all 11 gates +
bare `primal.eco` resolve to WireGuard IPs. `local=/primal.eco/` prevents
upstream forwarding. Inner membrane is DNS-invisible externally (6 public
A records removed from Knot DNS).

---

## What Diverged

### DIV-1: ironGate UFW rules not applied

UFW `status` showed 7700/tcp ALLOW from 192.168.4.0/22, but the rule was
**not in live iptables**. TCP probes from sporeGate timed out.

**Fix**: `sudo ufw reload` on ironGate loaded the rules into iptables.
**Lesson**: All gates should run `sudo ufw reload` or verify iptables
match UFW config after rule changes. Stale iptables is a silent failure.

### DIV-2: Old songBird binary ignores `lan_peers`

ironGate's songBird binary (Jul 13 build) accepted `mesh.init` with
`lan_peers` but didn't register them as Local — only overlay peers appeared.

**Fix**: Deployed Aug 3 depot build to ironGate. After restart, `lan_peers`
properly registered as `EndpointType::Local` (priority 0).
**Lesson**: All gates need the latest depot songBird for LAN-first support.

### DIV-3: eastGate songBird socket not found

eastGate's songBird runs as user process with `--socket /run/user/1000/biomeos/songbird.sock`,
but that path doesn't exist as a socket (directory artifacts instead).
Federation port 7700 is open and TCP-reachable. Can't `mesh.init` via UDS.

**Status**: Deferred to overwatch blurb. eastGate needs songBird socket fix
or binary update.

### DIV-4: strandGate songBird not running

strandGate has SSH access but no songBird process or federation port.
Needs full Tower Atomic deployment.

**Status**: Deferred to overwatch blurb.

### DIV-5: blueGate — Windows, no socat

blueGate's songBird federation port is open (7700 TCP), but Windows has
no `socat` for UDS. Needs PowerShell or TCP-based mesh init.

**Status**: Deferred to overwatch blurb. TCP path works for mesh routing;
init needs different tooling.

### DIV-6: `SONGBIRD_PEERS` vs `SONGBIRD_LOCAL_PEERS` precedence

sporeGate had `SONGBIRD_PEERS=eastGate@192.168.4.244:7700,...` which
registered eastGate at LAN IP but as `Direct` (priority 2), not `Local`.
The `SONGBIRD_LOCAL_PEERS` env var and `lan_peers` in `mesh.init` are
the correct mechanism to get priority 0.

**Lesson**: `SONGBIRD_PEERS` is for bootstrap discovery, NOT for
transport classification. Use `SONGBIRD_LOCAL_PEERS` for LAN gates.

---

## Architecture: WireGuard's New Role

WireGuard is **not deprecated** — it moves from "only transport" to
"outer membrane transport":

| Use | Still WG? | Why |
|-----|-----------|-----|
| golgi ↔ any gate | **Yes** | VPS has no LAN, WG is its only mesh path |
| WAN gates (flockGate) | **Yes** | Cross-site, no LAN reachability |
| External SSH access | **Yes** | Remote access from outside LAN |
| nestgate.io proxy | **Yes** | golgi TLS → sporeGate petalTongue over WG |
| LAN gate ↔ LAN gate | **No** | Tower Atomic LAN TCP at 1ms |
| Inner membrane routing | **No** | songBird capability.call uses Local path |

### Three-Domain Alignment

| Domain | Transport | Priority |
|--------|-----------|----------|
| primals.eco (outer) | Cloudflare → golgi Caddy → WG | N/A (public HTTP) |
| nestgate.io (peti) | golgi Caddy → WG → sporeGate petalTongue | WG (outer membrane) |
| primal.eco (inner) | **LAN TCP :7700 (Tower Atomic)** | **Local (priority 0)** |

---

## Deployed Configuration

### sporeGate (DONE)

| Item | Detail |
|------|--------|
| systemd drop-in | `/etc/systemd/system/songbird-gateway.service.d/lan-first.conf` |
| mesh init script | `/usr/local/bin/songbird-mesh-init.sh` — 4 LAN + 7 overlay peers |
| dnsmasq config | `/etc/dnsmasq.d/primal-eco.conf` — 11 gates + bare primal.eco |
| mesh.peers | 4 local (priority 0) + 2 overlay (priority 1) |
| verified | `getent hosts sporegate.primal.eco` → `10.13.37.2` |

### ironGate (DONE)

| Item | Detail |
|------|--------|
| songBird binary | Updated from Jul 13 → Aug 3 depot build |
| systemd drop-in | `/etc/systemd/system/songbird-membrane.service.d/lan-first.conf` |
| mesh init script | `/usr/local/bin/songbird-mesh-init.sh` — 3 LAN + 2 overlay |
| UFW reload | 7700/tcp rule now in live iptables |
| mesh.peers | 3 local (priority 0) + 2 overlay (priority 1) |

### Remaining Gates (for overwatch blurb)

| Gate | LAN IP | 7700 | Needs |
|------|--------|------|-------|
| **eastGate** | 192.168.4.244 | OPEN | songBird socket fix, LAN mesh.init |
| **strandGate** | 192.168.4.169 | closed | Tower deployment + LAN init |
| **blueGate** | 192.168.4.210 | OPEN | Windows mesh.init tooling |
| **northGate** | 192.168.4.147 | closed | Windows, firewall, Tower deployment |

---

## Evolution Path (for overwatch)

### Phase 2: Propagate to All LAN Gates
Each gate team receives blurb with:
1. Deploy latest depot songBird binary
2. Add `SONGBIRD_LOCAL_PEERS` to systemd env
3. Create mesh init script with `lan_peers`
4. `sudo ufw reload` to ensure 7700/tcp is live
5. Verify `mesh.peers` shows LAN peers at priority 0

### Phase 3: Manifest-Driven LAN Seeding
cellMembrane reads `[gates.*].lan_ip` + `zone` from ecosystem manifest,
auto-generates `SONGBIRD_LOCAL_PEERS` for same-zone gates. No manual env wiring.

### Phase 4: LAN Auto-Discovery
songBird `mesh.auto_discover` (UDP multicast port 2300). Zero-config —
new gates on LAN automatically register as Local.

### Phase 5: WG Deprecation for LAN Paths
Remove WG overlay entries for same-LAN gates. WG remains ONLY for
golgi + WAN gates. `primal.eco` resolves to LAN IPs via dnsmasq.
Inner membrane traffic never leaves the LAN.

---

## Key Takeaway

**The primals already had LAN-first transport built in.** songBird's
`EndpointType::Local` (priority 0) was designed for exactly this.
The gap was provisioning — gates auto-seeded from WireGuard because
that's what was configured. Adding `lan_peers` to `mesh.init` and
`SONGBIRD_LOCAL_PEERS` to systemd is all it took.

WireGuard becomes the outer membrane — the firebreak between LAN
and internet. The inner membrane runs on primals.
