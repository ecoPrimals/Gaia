# AAR: flockGate Divergence + Topology Issues — Wave 136b

**Date**: 2026-07-11 21:40 EDT  
**Author**: flockGate overwatch  
**Wave**: 136b  
**Severity**: P2 (data divergence) + P2 (mesh topology gap)

---

## Executive Summary

Two issues surfaced during flockGate's 136b sync and WAN probe cycle:

1. **DIVERGENCE** — `s_cascade_provenance_match` scenario reported 0 checksums despite `checksums.toml` having 14 entries per architecture. Parser was reading at the wrong TOML nesting level.
2. **TOPOLOGY** — songBird mesh has **zero peers** from flockGate. Federation port 7700 is not reachable on the WireGuard overlay. `capability.call` remains fully blocked — not just missing `DRAWBRIDGE_ROUTES`, but no mesh connectivity at all.

---

## Issue 1: Checksums Parser Divergence

### Symptom

```
[FAIL] xref:checksums_loaded: 0 entries in checksums.toml
[FAIL] xref:all_have_checksums: checksum coverage: 0/13 (missing: barracuda, beardog, ...)
```

Suite reported 0 checksums despite the file containing 28 entries (14 per architecture).

### Root Cause

`load_checksums()` in `s_cascade_provenance_match.rs` assumed a flat structure:

```toml
barracuda = { blake3 = "...", size = ... }
```

Actual structure is arch-nested:

```toml
[x86_64-unknown-linux-musl]
barracuda = { blake3 = "...", size = ... }

[aarch64-unknown-linux-musl]
barracuda = { blake3 = "...", size = ... }
```

The parser iterated top-level keys (arch triples), found tables, and looked for `blake3` directly in the arch table rather than iterating into the per-primal entries within.

### Fix

Committed as `fb03030` on primalSpring. Parser now iterates into architecture sub-tables:

```rust
for (_key, section) in &table {
    if let Some(arch_table) = section.as_table() {
        for (slug, entry) in arch_table {
            if let Some(t) = entry.as_table() {
                if let Some(hash) = t.get("blake3").and_then(|v| v.as_str()) {
                    map.insert(slug.clone(), hash.to_owned());
                }
            }
        }
    }
}
```

### Impact

- `cascade-provenance-match` scenario was silently FAILING on all gates
- `registry_all_rust_tier_pass` integration test caught it (asserts 0 failures for all Rust-tier scenarios)
- Without `ECOPRIMALS_ROOT` + `ECOPRIMALS_PLASMID_BIN` env vars, the test was skipped rather than failing — masking the bug on CI-like environments

### Recommendation

- Gates running primalSpring should set both `ECOPRIMALS_ROOT` and `ECOPRIMALS_PLASMID_BIN` for full depot validation coverage
- Consider adding a `[meta]` key to `checksums.toml` that declares the structure version, so parsers can validate expectations

---

## Issue 2: Mesh Topology — Federation Port Unreachable

### Symptom

```json
{"error":{"code":-32603,"message":"No local provider for 'jupyter' and no reachable mesh peers for remote dispatch"}}
```

songBird on flockGate initializes fine (`mesh.init` succeeds, `mesh.announce` succeeds) but has **0 peers** — no remote dispatch possible.

### Topology Observed

```
flockGate (NYC)
  └── WireGuard wg0 → 10.13.37.x/24
       └── Peer: golgiBody ([RELAY_PUBLIC] / 10.13.37.1)
            ├── ICMP: 0% loss, ~30ms RTT ✓
            ├── Port 443 (Caddy): REACHABLE via public DNS ✓
            ├── Port 7700 (songBird federation): CONNECTION REFUSED ✗
            ├── Port 8080 (drawbridge): TIMEOUT ✗
            └── Port 9090 (alt): TIMEOUT ✗
```

### Root Cause (Revised — Wave 137a probe)

**CORRECTION**: Initial AAR overstated the gap. Live TCP probes from flockGate (scenario `s_federation_wan_readiness`, commit `a2f1950`) reveal:

| Peer | Address | Port 7700 | Status |
|------|---------|-----------|--------|
| golgi | 10.13.37.1 | UNREACHABLE | No federation listener on relay |
| sporeGate | 10.13.37.2 | **REACHABLE** | Federation exposed |
| eastGate | 10.13.37.5 | **REACHABLE** | Federation exposed |
| ironGate | 10.13.37.7 | UNREACHABLE | No federation listener |

**2/4 WAN peers have federation port open.** The mesh is partially functional — the gap is specifically:
1. **golgi** (the relay node all traffic traverses) does not have songBird federation listening on 7700
2. **ironGate** does not expose 7700

sporeGate **does** have songBird federation running. The initial assessment that "no songBird process [is] running on golgi/sporeGate" was **incorrect for sporeGate**.

### Revised Root Cause (Wave 137a deep probe)

**Full topology observed via HTTP JSON-RPC to `http://10.13.37.2:7700/jsonrpc`:**

sporeGate's songBird v0.2.1 is fully operational with 3 mesh peers:
- `[RELAY_PUBLIC]:7700` (golgi public IP) — direct, reachable
- `192.168.4.237:7700` (eastGate LAN) — direct, 0ms latency
- `10.13.37.0:8080` (WG drawbridge) — direct, reachable

eastGate's songBird sees golgi at [RELAY_PUBLIC]:7700 (112ms latency).

**Three distinct problems:**

1. **golgi binds songBird federation to its public IP ([RELAY_PUBLIC]:7700) but NOT the WG interface (10.13.37.1:7700)**. From flockGate's WG overlay, 10.13.37.1:7700 is CONNECTION REFUSED. But sporeGate and eastGate reach golgi via its public IP.

2. **flockGate's local songBird (UDS) cannot join the HTTP-based federation mesh.** `peer.connect` establishes a TCP channel (70ms latency, state "connected") but the mesh.peers list remains empty. The local songBird's mesh engine expects raw socket protocol for peer registration, but the remote federation endpoints serve HTTP JSON-RPC at `/jsonrpc`. This is a **protocol layer mismatch** between the UDS client and the HTTP federation server.

3. **SONGBIRD_DRAWBRIDGE_ROUTES is NOT configured on sporeGate.** `discover_capabilities` on sporeGate returns songBird's built-in capabilities (http.*, relay.*, mesh.*, crypto.*) but NO `jupyter` capability. `capability.call("jupyter")` on sporeGate itself returns: "No local or remote provider found for capability 'jupyter'".

### Impact (Wave 137a — Final Assessment)

- **capability.call("jupyter") from flockGate**: BLOCKED at three levels
  1. flockGate songBird has 0 mesh peers (protocol mismatch)
  2. Even if peered, sporeGate doesn't advertise `jupyter` (missing DRAWBRIDGE_ROUTES)
  3. Even if advertised, routing to ironGate would fail (ironGate port 7700 closed)
- **HTTP transport workaround**: flockGate CAN reach sporeGate's federation directly via `curl -X POST http://10.13.37.2:7700/jsonrpc` — this proves the data path works at application level
- **The mesh is operational** between sporeGate, eastGate, and golgi on the LAN/public-IP topology. The WAN overlay (WireGuard 10.13.37.x) is a secondary path that works for routing but not for federation binding on golgi.

### Required Actions (Revised — Wave 137a)

| # | Action | Owner | Priority |
|---|--------|-------|----------|
| 1 | Bind golgi songBird to wg0 interface (10.13.37.1:7700) in addition to public IP | golgi/sporeGate | **CRITICAL** |
| 2 | Set `SONGBIRD_DRAWBRIDGE_ROUTES=/hub=jupyter` on sporeGate songBird | sporeGate | **CRITICAL** |
| 3 | Investigate UDS ↔ HTTP federation protocol mismatch — flockGate `peer.connect` succeeds at TCP but mesh doesn't register the peer | songBird team | HIGH |
| 4 | Expose songBird 7700 on ironGate (for direct capability routing) | ironGate | MEDIUM |
| 5 | Consider `http.request` as interim workaround — flockGate can HTTP POST to sporeGate federation directly | flockGate | LOW |

### Workaround (Proven)

HTTP JSON-RPC to sporeGate's federation endpoint works from flockGate:
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"mesh.peers","id":1}' \
  http://10.13.37.2:7700/jsonrpc
```

This bypasses the local songBird UDS mesh engine and talks directly to sporeGate's federation. Latency: ~220ms (WG hop). Public HTTP path via membrane.primals.eco: ~138ms p50.

---

## Latency Baseline (137a)

| Path | p50 | p95 | Method |
|------|-----|-----|--------|
| flockGate → membrane.primals.eco (HTTPS) | 138ms | 172ms | curl to /depot/ (5 samples) |
| flockGate → golgi (WireGuard ICMP) | 31ms | 34ms | ping -c3 10.13.37.1 |
| flockGate → golgi (federation 10.13.37.1:7700) | — | — | CONNECTION REFUSED |
| flockGate → sporeGate (federation 10.13.37.2:7700) | 220ms | — | HTTP JSON-RPC `/jsonrpc` |
| flockGate → eastGate (federation 10.13.37.5:7700) | ~250ms | — | HTTP JSON-RPC `/jsonrpc` |
| flockGate → sporeGate (peer.connect TCP) | 70ms | — | songBird peer.connect (connects but no mesh registration) |
| flockGate → capability.call mesh (UDS) | — | — | 0 PEERS (protocol mismatch) |

---

## Validation State (137a)

| Metric | Value |
|--------|-------|
| primalSpring SHA | `a2f1950` |
| Tests | 1,106 |
| Scenarios | 133 |
| Failures | 0 |
| Suite | GREEN |
| New scenario | `s_federation_wan_readiness` — validates port 7700 reachability |
| Env required | `ECOPRIMALS_ROOT` + `ECOPRIMALS_PLASMID_BIN` |

---

## Summary

**Divergence** (Issue 1): Parser bug, fixed in `fb03030`, now green.

**Topology** (Issue 2): Fully characterized across 3 probe sessions. The mesh is NOT dead — it's operational between sporeGate, eastGate, and golgi on LAN/public-IP paths. The WAN gap has THREE compound causes:

1. golgi binds to public IP only, not WG interface (prevents flockGate from reaching it)
2. flockGate's UDS songBird can't join the HTTP-based federation (protocol layer mismatch)
3. DRAWBRIDGE_ROUTES not set on sporeGate (no `jupyter` capability advertised)

**Key finding**: flockGate CAN talk to sporeGate's federation via HTTP at `10.13.37.2:7700/jsonrpc` — the data path works, only the mesh registration protocol is incompatible with the local UDS client.

**Priority**: Items 1-2 above are CRITICAL for mesh convergence. Item 3 is a songBird architectural question (UDS client → HTTP federation peering).

**Scenario `s_federation_wan_readiness` (a2f1950)** will transition from partial-FAIL → full-PASS as fixes land.
