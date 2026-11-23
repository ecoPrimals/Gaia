# Evolution AAR: DNS Cutover → Divergence Catalog

**Date**: 2026-07-09 (Wave 134k)
**Scope**: Complete DNS/TLS cutover retrospective — what worked, what broke,
every patch becomes a divergence for fractal/isomorphic evolution

---

## Sovereignty Model

The ecosystem has a consistent replacement pattern for external dependencies:

```
External tool         Sovereign replacement         Status
─────────────────     ─────────────────────────     ──────────
Cloudflare Tunnel  →  birdSong / darkForest         In progress
Cloudflare DNS     →  birdSong / darkForest         In progress
WireGuard          →  birdSong / darkForest         In progress
Caddy (TLS+route)  →  Tower atomics (bearDog+song)  Divergences below
Zola (static gen)  →  Sovereignty tool (depot)       Installed
GitHub Pages       →  golgi + Caddy (done)           Done
```

**Caddy is the parity target, not the permanent solution.** The tower atomics
(bearDog for TLS/crypto/ACME, songBird for routing/discovery/dispatch) replace
Caddy the same way birdSong/darkForest replaces WireGuard and Cloudflare.

Caddy stays operational as the **sovereign validation baseline** — the thing
the tower stack must match and exceed before it takes over. Every divergence
below is a gap between where the tower atomics are and where Caddy sits today.

---

## What Worked

### 1. Tower atomics in partial operation

bearDog successfully issued a multi-domain Let's Encrypt certificate (ACME
HTTP-01 with CSR SANs). songBird's drawbridge routes lab traffic from golgi
through the mesh to ironGate. These are the two halves of the future TLS +
routing stack — they work individually, they just don't compose as a full
Caddy replacement yet.

**Parity signal**: bearDog ACME ✓, songBird HTTP routing ✓, combined
Host-dispatch TLS ✗

### 2. Sovereignty path validated end-to-end

The full path `DNS → golgi TLS → WireGuard → songBird → JupyterHub` works.
No Cloudflare in the chain. The DNS cutover itself proved that the sovereign
relay architecture can serve production traffic — the tooling just needs to
mature from "Caddy does it" to "tower atomics do it."

### 3. Thin Forgejo relay

golgi disk 69% → 34% with depth=1 bare repos. Monthly re-shallowing timer.
Full history on sporeGate. This pattern is fractal — any edge gate can run
shallow relays.

### 4. pepti depot + sovereign CI

15 primals × 2 arches = 30 binaries, checksummed, depot-synced. Binary
deployment is `rsync` from depot. This is the foundation for fractal gate
provisioning — every gate pulls from the depot.

### 5. bearDog ACME capability

bearDog obtained a production Let's Encrypt cert with multi-domain SANs.
The CSR SAN fix was absorbed. This is real sovereign cert issuance — no
Cloudflare origin certs, no external CA integration.

---

## What Broke — Each Patch = Divergence from Tower Parity

Every item below is a gap between the tower atomics and Caddy. The patch
keeps things running on Caddy. The evolution closes the gap in the primals.

### DIV-DNS-01: bearDog has no Host/SNI dispatch

**What broke**: bearDog on :443 proxied all traffic to a single upstream.
Every subdomain got sporePrint instead of its correct backend.

**Patch**: Caddy restored on :443 (Host-based routing).

**Caddy parity gap**: Caddy dispatches by Host header to N upstreams.
bearDog dispatches to 1 upstream. This is the single biggest gap.

**Tower evolution**:
bearDog needs `BEARDOG_GATEWAY_ROUTES` — a route table mapping
SNI/Host → upstream. Implementation path:
1. TLS termination already works (rustls)
2. After TLS, parse HTTP/1.1 Host or HTTP/2 :authority
3. Dispatch to configured upstream per hostname
4. Default upstream for unmatched hosts
5. Config: env var or TOML route table

When bearDog can dispatch N hosts, it replaces Caddy's core function on
every gate. This is the bearDog milestone that unblocks full tower TLS.

### DIV-DNS-02: No ALPN negotiation (HTTP/2 regression)

**What broke**: bearDog's raw TCP proxy doesn't negotiate ALPN. Browsers
fell back to HTTP/1.1.

**Patch**: Caddy restored (HTTP/2 + HTTP/3 alt-svc).

**Caddy parity gap**: Caddy negotiates h2/h1.1 via ALPN, serves HTTP/3
via QUIC. bearDog does neither.

**Tower evolution**:
bearDog's rustls already supports ALPN — needs to be surfaced:
1. Set ALPN protocols `["h2", "http/1.1"]` in rustls ServerConfig
2. After negotiation, if h2: use hyper h2 server; if h1.1: current path
3. HTTP/3 (QUIC) is a later milestone — songBird's TURN relay may
   inform the UDP transport layer

### DIV-DNS-03: Static file serving gap

**What broke**: petalTongue serves its dashboard, not the Zola static site.
No tower primal currently serves static files.

**Patch**: Caddy :8091 serves sporePrint static files.

**Caddy parity gap**: Caddy's `file_server` + `try_files` is the static
serving baseline. No primal has an equivalent.

**Tower evolution**:
Two paths converge here:
1. **petalTongue gains file_server mode** — serve Zola output as baseline
   content, overlay with dynamic API endpoints. This makes petalTongue the
   sporePrint host on any gate.
2. **Zola as sovereignty tool** — Zola v0.22.1 is now installed on
   sporeGate. sporePrint builds locally (239 pages, 15s). Build pipeline:
   `sovereign-ci → zola build → rsync public/ → petalTongue serves it`.

Target: petalTongue serves static + dynamic, replaces Caddy file_server.

### DIV-DNS-04: Port displacement (:8443)

**What broke**: Moving Caddy to non-standard :8443 broke all subdomain links.

**Patch**: Standard ports restored.

**Caddy parity gap**: None — this was an operational error, not a capability
gap. The tower atomics must own :443 when they're ready, not share it.

**Tower evolution**: Rule: the TLS front door is either Caddy OR bearDog on
:443, never both. No port displacement. When bearDog reaches parity
(DIV-DNS-01 + DIV-DNS-02), it takes :443 and Caddy retires.

### DIV-DNS-05: CSR SAN missing in bearDog ACME

**What broke**: `build_csr()` only set CN, not SAN extensions. Multi-domain
ACME orders require SANs.

**Patch**: Fixed `issuance.rs` with `SubjectAltName` extension.

**Caddy parity gap**: Caddy's ACME automatically handles multi-domain certs.
bearDog now does too, but lacks test coverage.

**Tower evolution**: Add `#[test] fn csr_includes_all_sans()` to
beardog-acme. This is absorbed — the capability works, it just needs a
regression gate.

### DIV-DNS-06: Dual ACME ownership conflict

**What broke**: bearDog on :80 blocked Caddy's HTTP-01 cert renewal.

**Patch**: Caddy owns :80 and :443, renews its own certs.

**Caddy parity gap**: Caddy handles ACME for all domains on the IP.
bearDog can only ACME for its configured domains.

**Tower evolution**: When bearDog takes :443 (post DIV-DNS-01), it must
also handle ACME for ALL domains on that gate — not just primals.eco.
`BEARDOG_ACME_DOMAINS` needs to cover every Host in the route table.
Alternative: bearDog implements DNS-01 for domains it doesn't own :80 for.

### DIV-DNS-07: Content drift (stale Cloudflare references)

**What broke**: compute-access.md still described Cloudflare Tunnel.

**Patch**: Rewrote for songBird drawbridge architecture.

**Caddy parity gap**: N/A — content problem, not a tool gap.

**Tower evolution**: `spore-validate` content-infra drift check. Scan for
stale patterns ("Cloudflare Tunnel", "Cloudflare Access", ":8443") and
flag. This is a natural validation pipeline extension.

### DIV-DNS-08: Zola version skew

**Discovery**: golgi Zola 0.19.2, sporeGate 0.22.1.

**Tower evolution**: Zola becomes a pepti-managed binary in the depot,
pinned at 0.22.1 for both arches. Same sovereignty pattern as the primals.

---

## Sovereignty Layer — Parity Targets

Every external tool maps to either a primal replacement or a depot-managed
sovereign tool. The DNS cutover exposed which tools still need parity:

| External Tool | Sovereign Replacement | Parity Status |
|---------------|----------------------|---------------|
| **Caddy TLS** | bearDog ACME gateway | ACME ✓, Host routing ✗, ALPN ✗ |
| **Caddy routing** | bearDog SNI dispatch | Not implemented |
| **Caddy file_server** | petalTongue static mode | Not implemented |
| **Caddy HTTP/2** | bearDog ALPN + hyper h2 | rustls ready, not surfaced |
| **Caddy HTTP/3** | (future) | Not started |
| **Cloudflare Tunnel** | birdSong / darkForest | In progress |
| **Cloudflare DNS** | birdSong / darkForest | In progress |
| **WireGuard** | birdSong / darkForest | In progress |
| **Zola** | pepti depot binary | Installed, needs depot pin |

### Tower Atomic Parity Milestones

The tower atomics replace Caddy in phases:

```
Phase 1 (current):  Caddy :443, bearDog standby
                    bearDog ACME works, songBird routes work
                    Gap: Host dispatch, ALPN, file serving

Phase 2:            bearDog gains BEARDOG_GATEWAY_ROUTES
                    SNI/Host → upstream dispatch
                    Can serve N domains on :443
                    Gap: ALPN, file serving

Phase 3:            bearDog gains ALPN (h2 + h1.1)
                    HTTP/2 parity with Caddy
                    Gap: file serving

Phase 4:            petalTongue gains file_server mode
                    Static Zola content + dynamic API
                    bearDog dispatches to petalTongue + Forgejo + songBird
                    Caddy retires from production

Phase 5:            birdSong / darkForest replaces WireGuard
                    Full sovereign mesh — no external tools in the chain
```

---

## Architecture — Current Production (Post-134k)

```
Internet
  │
  └── golgi ([RELAY_PUBLIC]) — thin edge relay
      │
      ├── Caddy :443 (PARITY TARGET — tower atomics replace this)
      │   ├── primals.eco      → file_server (Zola static)
      │   ├── www.primals.eco  → 301 → primals.eco
      │   ├── membrane.*       → depot + health + nestgate
      │   ├── git.*            → Forgejo :3000
      │   └── lab.*            → WireGuard → sporeGate songBird :7780
      │
      ├── bearDog (standby, port 9999 — ACME ready, awaiting SNI dispatch)
      │
      ├── songBird (mesh federation — routing works, needs TLS integration)
      │
      ├── Forgejo :3000 / :2222 (shallow bare repos)
      │
      └── WireGuard :51820 (PARITY TARGET — birdSong/darkForest replaces this)
          └── sporeGate (10.13.37.2)

sporeGate (10.13.37.2) — sovereign compute
  │
  ├── Full git mirrors (/opt/forgejo-mirror/)
  ├── pepti depot (/opt/ecoPrimals/depot/)
  ├── Rust/Cargo/cross (build toolchain)
  ├── Zola v0.22.1 (sovereignty tool — sporePrint builder)
  ├── songBird (drawbridge + capability routing)
  ├── sovereign-ci (build + deploy cascade)
  │
  └── WireGuard → ironGate (10.13.37.7), flockGate (10.13.37.3)
```

---

## Divergence Summary

| ID | Gap | Patch (Caddy) | Tower Evolution |
|----|-----|---------------|-----------------|
| DNS-01 | No Host dispatch | Caddy Host routing | bearDog GATEWAY_ROUTES |
| DNS-02 | No ALPN/HTTP/2 | Caddy h2 | bearDog rustls ALPN + hyper h2 |
| DNS-03 | No file serving | Caddy file_server | petalTongue static mode |
| DNS-04 | Port displacement | Standard ports | Rule: :443 or nothing |
| DNS-05 | CSR SAN missing | Code fix | bearDog ACME test suite |
| DNS-06 | Dual ACME conflict | Caddy owns ACME | bearDog multi-domain ACME |
| DNS-07 | Content drift | Manual rewrite | spore-validate drift check |
| DNS-08 | Zola version skew | Both installed | Zola in pepti depot |

---

## Next Steps

1. **bearDog `GATEWAY_ROUTES`** — SNI/Host dispatch. This is the gate that
   unblocks tower TLS ownership. Closes DNS-01.
2. **bearDog ALPN** — surface rustls ALPN for h2/h1.1. Closes DNS-02.
3. **petalTongue file_server mode** — serve Zola output + dynamic overlay.
   Closes DNS-03.
4. **Zola + Caddy in pepti depot** — pin versions, checksum, both arches.
   Closes DNS-08. Caddy stays in depot as the parity reference even after
   tower atomics replace it.
5. **bearDog ACME tests** — multi-domain CSR regression gate. Closes DNS-05.
6. **spore-validate content drift** — automated stale-pattern scan. Closes DNS-07.
7. **Wire `zola build` into sovereign-ci** — build on sporeGate, deploy to gates.
