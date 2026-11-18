# AAR: Peptidoglycan Topology Failure — NAT Rate-Limit Collapse (UDP + TCP)

**Date**: 2026-07-28 | **Gate**: sporeGate (incident), golgiBody (root cause) | **Wave**: 155b
**Scope**: Full outer membrane failure, two cascading rate-limit collapses, peptidoglycan-layer architecture, deployment vs topology ownership
**Duration**: ~3 hours total (two incidents), 5 minutes to fix each once root cause identified
**Severity**: P1 — complete loss of remote access to all house1+house2 gates (twice)

---

## EXECUTIVE SUMMARY

Two cascading failures exposed a fundamental gap in the ecosystem's **peptidoglycan layer** — the topology and connectivity fabric that sits between the outer membrane (RustDesk/human access) and the inner membrane (primals/service mesh).

**Incident 1 (UDP)**: All house1 RustDesk gates went offline. Per-source-IP UDP rate limits on golgiBody (30/10s) were exceeded by NAT-clustered gates sharing one WAN IP. Silent DROP — no logs, no errors.

**Incident 2 (TCP)**: After fixing UDP, all connections dropped again. RustDesk clients retry TCP to port 21114 (API server, no listener). Each retry = new TCP connection. 10 NATted clients × retries overwhelmed the 60/10s TCP rate limit, blocking ALL TCP to RustDesk ports including legitimate 21116 connections.

Both failures share the same pattern: **per-IP rate limits assume one-client-per-IP, but NAT clusters amplify counts**. This AAR documents both incidents, the diagnostic journey, and the architectural separation that emerged — treating the LAN/HPC topology as a **peptidoglycan layer** with distinct ownership from both the outer membrane and the primals beneath.

---

## WHAT HAPPENED

### Symptom
- northGate could connect to flockGate (WAN: [FLOCK_WAN]) but all house1 gates (sporeGate, eastGate, northGate — WAN: [NUCLEUS_WAN]) showed as offline to each other
- RustDesk client logs showed `register_pk... due to key not confirmed` in an infinite loop
- Server-side hbbs logs showed zero `update_pk` entries for house1 gates

### Root Cause Chain

```
golgiBody iptables INPUT chain:
  Rule 4: UDP dpt:21116 → recent SET name:rustdesk_udp
  Rule 5: UDP dpt:21116 → recent UPDATE 10s hitcount:30 → DROP

house1 topology:
  sporeGate  ─┐
  eastGate   ─┼─ NAT ─→ WAN [NUCLEUS_WAN] ─→ golgiBody:21116
  northGate  ─┘

3 gates × ~10 UDP heartbeats/10s = 30 packets/10s per source IP
                                    ↑ exactly at the DROP threshold
```

The firewall saw all house1 traffic as a single flood source and silently dropped everything. flockGate, alone behind its own WAN IP, stayed well under the limit.

### Why It Was Hard to Find

1. **Silent DROP** — no iptables LOG target, no REJECT (which would produce ICMP unreachable), no server-side error. The packets simply vanished.
2. **Version red herring** — RustDesk 1.3.x on sporeGate had zero network connections (separate bug: dnsmasq was dead, causing init-time DNS hangs). This made it look like a client version incompatibility.
3. **Protocol red herring** — RustDesk 1.4.x clients connected TCP but failed to register. This looked like a 1.4.x-vs-1.1.x protocol mismatch (a real issue, but not the primary one).
4. **Key confirmation loop** — Client logs showed `key not confirmed` repeatedly, suggesting a key mismatch problem. In reality, the server simply never received the registration because the firewall ate it.

### Secondary Issue: Dead dnsmasq

sporeGate's `/etc/resolv.conf` pointed to `127.0.0.1` (dnsmasq) as primary DNS, but dnsmasq was disabled and not running. This caused RustDesk 1.3.x to hang during initialization (likely DNS lookup for API server check), producing zero outbound connections. This masked the real firewall issue by making it look like a client-side binary problem.

---

## DIAGNOSTIC TIMELINE

| Time | Action | Finding |
|------|--------|---------|
| T+0 | northGate reports LAN gates offline, flockGate works | Topology-specific failure |
| T+15m | Check client configs, key_confirmed state | Key confirmed = false, but server key present |
| T+30m | Try RustDesk 1.4.9, 1.4.8, 1.3.9, 1.3.8 on sporeGate | 1.3.x: zero connections. 1.4.x: TCP connects but no registration |
| T+45m | strace 1.4.x client | Sends UDP register_pk, tries TCP to port 21114 (API) |
| T+60m | strace 1.3.x client | Zero network syscalls — binary hangs in init |
| T+75m | Check dnsmasq | Dead. Port 53 unbound. Fix: `systemctl enable --now dnsmasq` |
| T+80m | Restart 1.3.8 with DNS fixed | Now connects! But still `key not confirmed` loop |
| T+90m | **tcpdump on golgiBody** | **SMOKING GUN**: server responds to flockGate ([FLOCK_WAN]), ignores ALL packets from [NUCLEUS_WAN] |
| T+95m | Check iptables | Rate limit: 30 UDP/10s per IP. House1 (3 gates, 1 NAT) exceeds it |
| T+100m | Raise limits, flush recent tables | **ALL 9 house1 peers register within 4 seconds** |

### Incident 2: TCP Rate-Limit Cascade (T+150m)

After restoring UDP connectivity and creating the RUSTDESK_MEMBRANE chain, a service restart on northGate triggered the second collapse.

| Time | Action | Finding |
|------|--------|---------|
| T+150m | Service restart on northGate | All RustDesk remotes go offline again |
| T+152m | Check golgiBody | hbbs running, UDP flowing to flockGate — relay is healthy |
| T+155m | sporeGate RustDesk log | `test nat: Failed to connect to [RELAY_PUBLIC]:21116` |
| T+157m | nc to ports 22, 443 | Both succeed instantly |
| T+158m | nc to port 21116 | SYN-SENT, timeout — port-specific block |
| T+160m | tcpdump sporeGate | SYNs leave 192.168.4.3 but never arrive at golgiBody |
| T+162m | tcpdump golgiBody (any traffic from house1) | SSH traffic arrives, port 21114 SYNs arrive — but zero 21116 traffic |
| T+163m | **Check RUSTDESK_MEMBRANE counters** | **Rule 5 (TCP DROP): 6267 packets dropped** |
| T+164m | Root cause | Port 21114 (API server) has NO listener. Clients retry TCP → each retry = NEW connection. 10 NATted clients × retries > 60/10s limit → ALL TCP to 21115-21118 blocked |
| T+165m | REJECT 21114 with tcp-reset, remove from rate limit, flush tables | **All connections restored** |

---

## WHAT WE FIXED

### 1. RUSTDESK_MEMBRANE Firewall Chain (golgiBody)

Created a dedicated iptables chain that isolates RustDesk traffic handling from all primals services:

```
INPUT chain:
  Rule 2: TCP 21114 → REJECT --tcp-reset  (instant RST, stops retry storms)
  Rule 3: TCP 21115-21118 → jump RUSTDESK_MEMBRANE
  Rule 4: UDP 21116      → jump RUSTDESK_MEMBRANE
  (primals rules below — HTTPS, SSH, Forgejo — completely separate)

RUSTDESK_MEMBRANE chain:
  1. REJECT TCP 21114 with tcp-reset  (API port — no service, prevent retry storms)
  2. ACCEPT ESTABLISHED,RELATED
  3. UDP 21116 recent SET rd_membrane_udp
  4. UDP 21116 recent UPDATE 10s hitcount:120 → DROP
  5. ACCEPT UDP 21116
  6. TCP 21115-21118 NEW recent SET rd_membrane_tcp
  7. TCP 21115-21118 NEW recent UPDATE 10s hitcount:60 → DROP
  8. ACCEPT TCP 21115-21118
```

**NAT-aware limits**: 120 UDP/10s supports ~10 gates behind one NAT. 60 TCP new connections/10s for legitimate use. Port 21114 (API) gets instant RST to prevent retry storms from poisoning the rate counter.

### 2. dnsmasq Re-enabled (sporeGate)

```bash
systemctl enable --now dnsmasq
```

Sovereign DNS chain restored: dnsmasq (port 53) → stubby (DoT) → upstream resolvers.

### 3. Duplicate Process Cleanup (golgiBody)

Killed stale manual-run hbbs/hbbr processes that were competing with systemd-managed services for port bindings.

### 4. Architectural Separation Documented

Cursor rule at `.cursor/rules/outer-membrane-rustdesk.mdc` codifies the separation:

| Concern | Outer Membrane (RustDesk) | Primals |
|---------|--------------------------|---------|
| Route | Public internet via default gateway | WireGuard wg0 (10.13.37.x) |
| Firewall | `RUSTDESK_MEMBRANE` chain | HTTPS rate-limit + ufw |
| Auth | Server key + per-gate password | Capability IPC / TLS |
| Failure domain | Independent | Independent |

---

## SKUNKBAT TARGETS — Future Detection

This failure class should be flaggable earlier. Key signals:

### 1. "Works from one WAN, fails from another" → NAT amplification

If a service works from one external IP but not another, and the failing IP has multiple clients behind NAT, check per-source-IP rate limits immediately. The rate limit may be counting aggregate traffic from all NATted clients as a single flood source.

### 2. "Silent DROP" → Always prefer REJECT or LOG before DROP

Silent DROPs are invisible to both client and server. For services we own (not public-facing scan targets), `LOG --log-prefix "RD_MEMBRANE_DROP: "` before DROP would make this visible in dmesg/journal. Consider adding LOG targets in the RUSTDESK_MEMBRANE chain for debugging.

### 3. "Client loops on register_pk" → Check server-side first

The client-side `key not confirmed` loop is a symptom, not a cause. The diagnostic shortcut: immediately check if the hbbs server logs `update_pk` for the client. If not, the packet isn't arriving — look at the network path, not the client config.

### 4. "Zero connections from a known-working binary" → Check local DNS

If a binary that should be making network calls shows zero sockets in `ss`, check if local DNS resolution is broken. Many applications do DNS lookups during init (API checks, update checks) and silently fail if DNS times out.

### 5. dnsmasq Health Check

Add to gate health monitoring: if `/etc/resolv.conf` points to localhost but nothing binds port 53, flag immediately.

### 6. "Dead listener port in rate-limited set" → REJECT, don't ignore

If a port has no listener but is included in a rate-limit counter set, client retries create a denial-of-service against the other ports in the set. **Always REJECT (tcp-reset) ports with no listener** so clients stop immediately. Never let a dead port silently timeout behind a shared rate counter.

### 7. "All connections drop after any service restart" → Check TCP rate limit counters

If restarting any service causes all RustDesk connections to fail, check `iptables -L RUSTDESK_MEMBRANE -n -v` for high DROP counts on the TCP rate-limit rule. The restart may trigger reconnection storms that poison the rate counter.

---

## ARCHITECTURAL INSIGHT: The Peptidoglycan Layer

### Three-Layer Model

This incident revealed that the ecosystem has three distinct connectivity layers, not two:

```
┌─────────────────────────────────────────────────────────┐
│  OUTER MEMBRANE — Human access (RustDesk)               │
│  Route: public internet → relay.primals.eco             │
│  Auth: server key + per-gate password                   │
│  Owner: golgiBody RUSTDESK_MEMBRANE chain               │
├─────────────────────────────────────────────────────────┤
│  PEPTIDOGLYCAN — LAN/HPC topology fabric                │
│  Hardware: Flints, CRS310, Omada, 10G AOC trunk         │
│  Services: NAT, DHCP (sporeGate), DNS (dnsmasq→stubby)  │
│  Scope: 192.168.4.0/22 flat LAN, both houses            │
│  Anchors: sporeGate (house1) + blueGate (house2)        │
├─────────────────────────────────────────────────────────┤
│  INNER MEMBRANE — Primal communications                 │
│  Route: WireGuard wg0 (10.13.37.x) + songBird :7700    │
│  Auth: capability IPC, TLS, BTSP                        │
│  Owner: per-primal, coordinated by overwatch             │
└─────────────────────────────────────────────────────────┘
```

Both outer and inner membranes depend on the peptidoglycan, but must not share failure domains with it. The peptidoglycan is the physical/network reality — cables, switches, NAT, DNS — that everything rides on.

### Why "Peptidoglycan"

In cell biology, peptidoglycan is the rigid structural mesh between the inner and outer membranes of Gram-negative bacteria. It provides shape, mechanical strength, and acts as a sieve. In the ecosystem:

- It provides **structure** — the physical network that gives gates their connectivity
- It acts as a **sieve** — NAT, firewall, rate limits filter what passes through
- It's **rigid** — hardware topology changes slowly (cable runs, switch configs)
- It's **vulnerable to lysis** — rate limits, DNS failures, and topology changes can crack it, collapsing both membranes simultaneously

### Deployment vs Topology: Ownership Model

| Concern | Owner | Current State | Gap |
|---------|-------|---------------|-----|
| **Outer membrane firewall** | golgiBody (RUSTDESK_MEMBRANE) | Hardened (2 incidents fixed) | Needs LOG before DROP |
| **Outer membrane clients** | Per-gate RustDesk config | house1 working, house2 Linux = provisioning gap | Standardized gate provisioning needed |
| **Peptidoglycan: DNS** | sporeGate (dnsmasq→stubby) | sporeGate fixed, northGate likely broken | Per-gate DNS health check |
| **Peptidoglycan: NAT/DHCP** | sporeGate (nftables membrane) | Working but enp1s0 DOWN, eno1 as both LAN+default | Clarify router architecture |
| **Peptidoglycan: switching** | CRS310 (house1) + Omada (house2) | Working but port map incomplete | Full port→gate mapping |
| **Peptidoglycan: trunk** | 10G AOC CRS310↔Omada | Proven (blueGate reaches relay) | Monitor link health |
| **Peptidoglycan: WiFi bridge** | Flint 2 (house2) | blueGate/swiftGate working | Document config |
| **Inner membrane: WireGuard** | sporeGate↔golgiBody | Proven (flockGate live) | Only 2 peers active |
| **Inner membrane: songBird** | Per-primal | 13/13 BTSP | Gate enrollment pending for house2 |
| **Primal deployment** | golgiBody depot + gate enrollment | Proven for house1 | House2 gates need RustDesk first |

### Immediate Goal: Harden the Peptidoglycan

Abstracting and hardening the LAN/HPC topology is the immediate prerequisite for everything else. The primals can't evolve if the connectivity fabric underneath is fragile. The outer membrane is the sovereign fallback for when the peptidoglycan cracks.

**Anchor node model**: sporeGate (house1, manages entry — router/firewall/DNS) and blueGate (house2, manages compute farm) need end-to-end communication and shared ability to configure the hardware between them. This is the peptidoglycan management plane.

**Sequencing**:
1. Harden peptidoglycan (DNS per gate, port mappings, health checks)
2. Provision outer membrane on all gates (RustDesk via relay.primals.eco)
3. Resume inner membrane evolution (WireGuard enrollment, songBird mesh)
4. Continue glacial primal goals (genomeBin convergence, etc.)

---

## CURRENT STATE

- All house1 gates (sporeGate, eastGate, northGate) online and registered
- flockGate remains online (was never affected)
- blueGate + swiftGate (Windows, house2) online via backbone
- house2 Linux gates (westGate, southGate, ironGate, strandGate) need RustDesk provisioning (network path proven via blueGate)
- 10 total peers registered in hbbs DB
- `relay.primals.eco` resolves via Cloudflare wildcard → [RELAY_PUBLIC]
- `https://relay.primals.eco` info page active (passphrase-gated bootstrap)
- `RUSTDESK_MEMBRANE` chain saved via netfilter-persistent (both UDP + TCP fixes)
- Port 21114 REJECT with tcp-reset (prevents retry storm poisoning)
- dnsmasq enabled and persistent on sporeGate
- Cursor rule `.cursor/rules/outer-membrane-rustdesk.mdc` codifies the pattern
- `TOPOLOGY_MAP.toml` has full physical layout but needs port-level completion

## OPEN ITEMS FOR OVERWATCH

| Priority | Item | Owner |
|----------|------|-------|
| P0 | Harden peptidoglycan DNS: verify dnsmasq on all Linux gates | sporeGate (via blueGate bridge for house2) |
| P1 | Provision RustDesk on house2 Linux gates | blueGate (local access) |
| P1 | Complete port→gate mapping in TOPOLOGY_MAP.toml | overwatch |
| P2 | Add LOG before DROP in RUSTDESK_MEMBRANE | golgiBody |
| P2 | northGate DNS delay diagnosis (likely dead dnsmasq) | northGate (local) |
| P2 | Document Flint H1 + Flint 2 + Omada configs | sporeGate + blueGate |
| P3 | Standardized gate provisioning script (DNS + RustDesk + health checks) | wateringHole |

*Peptidoglycan layer identified. Two rate-limit collapses diagnosed and fixed. Ownership model established. Ready for overwatch coordination. — sporeGate, wave 155b*
