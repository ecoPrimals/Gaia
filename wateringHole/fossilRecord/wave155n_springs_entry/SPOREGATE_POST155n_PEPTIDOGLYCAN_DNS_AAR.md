# sporeGate AAR — Peptidoglycan DNS Fix (Post-155n)

**Date**: August 1, 2026
**Wave**: Post-155n (Springs+Gardens Phase)
**Gate**: sporeGate (build authority, site router, DNS/DHCP)
**Posture**: DNS was a recurring SPOF. strandGate DNS dead. northGate 2-3s delays. Fixed.

---

## Root Cause Analysis

### The Failure Chain

```
Gate WG config: DNS = 10.13.37.1 (golgi WG interface)
  → wg-quick tells systemd-resolved: "use 10.13.37.1 for wg0"
  → systemd-resolved routes queries to 10.13.37.1
  → golgi knotd listens on [RELAY_PUBLIC]:53 ONLY, NOT 10.13.37.1
  → connection refused → SERVFAIL
  → all DNS broken on any gate with WG + systemd-resolved
```

### Contributing Factors

1. **Single DNS in DHCP**: `dhcp-option=option:dns-server,192.168.4.3` — no fallback. If sporeGate dnsmasq stalls, every DHCP client loses DNS.
2. **Single upstream in dnsmasq**: Only `server=127.0.0.1#5353` (stubby DoT). If stubby hangs, dnsmasq can't resolve.
3. **No auto-restart**: dnsmasq had no `Restart=always` — crash = permanent outage until manual intervention.
4. **Phantom DNS on WG**: Every gate's WireGuard config sets `DNS = 10.13.37.1`, but no DNS server existed at that address. systemd-resolved's split-DNS routing sends queries there → timeout → SERVFAIL.
5. **strandGate mislabeled**: DHCP reservation had strandGate (192.168.4.169) named `irongate-compute` — we couldn't identify or reach it.
6. **Missing gate DNS entries**: northGate, blueGate, strandGate had no static DNS entries in dnsmasq. eastGate entry pointed to wrong IP (.30 instead of .244).

---

## Fixes Applied

### Layer 1: sporeGate dnsmasq (peptidoglycan anchor)

| Fix | Detail |
|-----|--------|
| **Redundant DHCP DNS** | `dhcp-option=option:dns-server,192.168.4.3,1.1.1.1` — clients now get sporeGate + Cloudflare fallback |
| **Direct upstream fallback** | Added `server=1.1.1.1` and `server=1.0.0.1` alongside stubby — if DoT hangs, dnsmasq falls back to direct DNS |
| **Auto-restart watchdog** | `Restart=always, RestartSec=5` via systemd drop-in — dnsmasq self-heals on crash |
| **DHCP label fix** | Renamed `irongate-compute` → `strandgate` at 192.168.4.169 |
| **DNS entry corrections** | Fixed eastGate (.30 → .244), added strandGate (.169), northGate (.147), blueGate (.210) |

### Layer 2: golgi mesh DNS (WG overlay fix)

| Fix | Detail |
|-----|--------|
| **Mesh DNS forwarder** | Installed dnsmasq on golgi, listening on `10.13.37.1:53` only (WG interface) |
| **Upstream forwarding** | Forwards to DigitalOcean DNS (67.207.67.2/3) + Cloudflare (1.1.1.1) |
| **No conflict** | Doesn't interfere with knotd ([RELAY_PUBLIC]:53) or resolved (127.0.0.53) |
| **Auto-restart** | `Restart=always, RestartSec=5` watchdog applied |

**Impact**: Every gate with `DNS = 10.13.37.1` in WG config now gets working DNS through the mesh. No per-gate fixes needed for the WG DNS path.

### Layer 3: strandGate (emergency fix)

| Fix | Detail |
|-----|--------|
| **Bypassed systemd-resolved** | Stopped resolved, wrote direct `/etc/resolv.conf` with `nameserver 192.168.4.3`, `nameserver 1.1.1.1`, `nameserver 1.0.0.1` |
| **DNS verified** | Resolution confirmed working: google.com (1ms), git.primals.eco (resolves to [RELAY_PUBLIC]) |

---

## Topology Discovered

### Physical Path (verified via ping latencies)

```
AT&T ISP
  └── Flint H1 (.1) ─── NAT/gateway              ✅ 0.5ms
        ├── sporeGate (.3) ─── DNS/DHCP            ✅ local
        ├── northGate (.147) ─── Windows            ✅ 0.2ms
        ├── MikroTik CRS310 (.2)                    ✅ 0.2ms
        │     ├── eastGate (.244) ─── Pop!_OS       ✅ 0.3ms
        │     ├── ironGate (.237) ─── ASRock        ✅ 0.4ms
        │     └── [80m AOC backbone]
        │           └── Omada SX3008F (.111)        ✅ 0.9ms
        │                 ├── strandGate (.169) ─── Dual EPYC  ✅ 0.2ms
        │                 ├── southGate (IP unknown)
        │                 ├── westGate (IP unknown)
        │                 └── Flint H2 (.250)       ✅ 0.5ms
        │                       └── blueGate (.210) ─── Windows
        └── Flint H2-alt (.251)                     ❌ DOWN
```

### WireGuard Mesh (via golgi hub)

| WG IP | Gate | Zone | LAN IP |
|-------|------|------|--------|
| 10.13.37.1 | golgi (hub) | WAN | [RELAY_PUBLIC] |
| 10.13.37.2 | sporeGate | Backbone | 192.168.4.3 |
| 10.13.37.5 | eastGate | Backbone | 192.168.4.244 |
| 10.13.37.6 | flockGate | WAN | [FLOCK_WAN] |
| 10.13.37.7 | ??? | — | — |
| 10.13.37.8 | ??? | — | — |
| 10.13.37.9 | southGate | House 2 | unknown |
| 10.13.37.10 | strandGate | House 2 | 192.168.4.169 |
| 10.13.37.11 | westGate | House 2 | unknown |
| 10.13.37.12 | blueGate | House 2 | 192.168.4.210 |

### Data Corrections Needed

| Item | Was | Should Be |
|------|-----|-----------|
| `cytoplasm.rs` westGate zone | `House1` | `House2` (manifest says house2, physically at Omada) |
| `ecosystem_manifest.toml` strandGate | no `ipv4` field | `ipv4 = "192.168.4.169"` |
| `ecosystem_manifest.toml` eastGate | no `ipv4` field | `ipv4 = "192.168.4.244"` |
| DHCP hostname at .169 | `irongate-compute` | `strandgate` (fixed) |
| dnsmasq static for eastGate | `.30` | `.244` (fixed) |

---

## Architecture: Zero-Touch Peptidoglycan

**Goal**: Hook up any computer to the mesh and DNS just works. No manual `/etc/resolv.conf`, no custom interactions.

### DNS Redundancy Pattern (now implemented)

```
LAN path:  DHCP → sporeGate (192.168.4.3) + Cloudflare (1.1.1.1)
                    ↓
              dnsmasq → stubby (DoT) → Cloudflare/Quad9
                    ↓ (fallback)
              dnsmasq → 1.1.1.1 / 1.0.0.1 (direct)

WG path:   WG config → golgi (10.13.37.1:53)
                    ↓
              dnsmasq → DigitalOcean DNS + Cloudflare
```

Any device connecting via DHCP gets two DNS servers automatically. Any gate on the WG mesh gets DNS through the overlay. Both paths have fallback.

### Remaining Evolution

1. **blueGate as H2 DNS secondary**: When blueGate is online, it could run a DNS forwarder for House 2 gates, adding a third DNS path independent of the backbone.
2. **Gate enrollment script**: Standardize DNS config during `gate-enroll.sh` — bypass systemd-resolved on all Ubuntu gates with direct resolv.conf.
3. **southGate/westGate LAN IPs**: Need discovery — run diagnostics from strandGate or local access.
4. **Tower Atomic abstraction**: biomeOS mesh (:7700) should provide service discovery above DNS, so the peptidoglycan only needs to be reliable enough for mesh bootstrap.
5. **WG config cleanup**: Consider removing `DNS = 10.13.37.1` from gate WG configs now that DHCP handles DNS. The golgi forwarder is a safety net, not primary.

---

## SSH Enrollment Pending

sporeGate SSH key needs enrollment on strandGate:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILU4i9hEtHJA02/JZ8XR/OHaR/bSiuAaDRMhdJX7zuRp sporegate-gate-v1
```

SSH config added for `Host strandgate → 192.168.4.169`.

---

*The peptidoglycan layer is the cell wall. When DNS fails, nothing above it works — no builds, no deploys, no cascades. This fix makes DNS self-healing (auto-restart), redundant (multiple upstreams + fallback), and mesh-aware (golgi WG DNS). The next evolution is making it isomorphic — any gate failure routes around automatically.*
