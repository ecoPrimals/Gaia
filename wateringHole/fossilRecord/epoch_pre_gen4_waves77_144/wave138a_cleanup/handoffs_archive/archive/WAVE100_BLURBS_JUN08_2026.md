# Wave 100 Blurbs — Mesh Final Mile + Transport Evolution Trigger

**Date**: 2026-06-08
**From**: eastGate overwatch
**Context**: songBird P1 fix (4eb5111d) deployed and tested on eastGate. Detection improved but two integration gaps remain. biomeOS v4.14 + coralReef capabilities.list landed in git. sourDough TransportEndpoint is the canonical standard — triggering ecosystem-wide transport adoption.

---

## songBird Team — P1: Two Remaining Integration Gaps

We rebuilt from `4eb5111d`, deployed to eastGate with federation *:7700, and tested mesh.init against a confirmed-alive LAN peer (192.168.1.173:7700 responds to HTTP `/jsonrpc`). Result: `bootstrap_peers_added:0` still. Two gaps found:

### Gap 1: security_client uses HTTP-over-socket-path (not UDS JSON-RPC)

`security_setup.rs` now correctly resolves bare names to socket paths (good). But `security_client` appends a REST path to the socket path:

```
/tmp/biomeos/biomeos/security.sock/api/v1/trust/evaluate → Invalid URL: Missing scheme
```

The security_client is treating the UDS socket as an HTTP base URL. For local trust evaluation, it should open the UDS socket and send a JSON-RPC call (`trust.evaluate` or `btsp.session.verify`), not construct an HTTP URL from the socket path.

**Fix**: In `security_client::client`, when the endpoint is a UDS socket path (starts with `/` or contains `.sock`), use `UnixStream::connect` + JSON-RPC instead of HTTP POST.

### Gap 2: HttpRemoteConnection fallback not triggered after TLS detection

`http_remote.rs` (151 new lines) is the right approach — plain HTTP JSON-RPC to remote peers. The TLS handshake now properly detects plain HTTP responses:

```
Server responded with HTTP instead of TLS (got 'HTTP/1.1 400 Bad Request')
```

But after detection, the connection_manager exhausts all 3 TLS attempts and gives up. The `HttpRemoteConnection` fallback path never fires.

**Fix**: In `connection_manager/trust.rs`, when TLS handshake fails with HTTP-detection error, immediately construct an `HttpRemoteConnection` to the same `host:port` instead of retrying TLS. The peer is already proven reachable via plain HTTP.

### Verification when fixed

Once both gaps are closed, this should work end-to-end:
```bash
# eastGate (with songbird P1 fix v2)
SECURITY_PROVIDER_SOCKET=/tmp/biomeos/biomeos/security.sock \
SONGBIRD_PRODUCTION_BIND_ADDRESS=0.0.0.0 \
songbird server --port 7700

# Then:
echo '{"jsonrpc":"2.0","method":"mesh.init","params":{"node_id":"eastgate","peers":["192.168.1.173:7700"]},"id":1}' \
  | socat - UNIX-CONNECT:/run/user/1000/biomeos/songbird.sock
# Expected: bootstrap_peers_added:1
```

We have a live 3-gate LAN with confirmed-alive peers. The protocol layer works — just the integration plumbing remains.

---

## All Primals — Transport Evolution Trigger

sourDough has published the canonical transport standard. sourDough is the **repository of primal standards** — it defines wire formats, validates compliance, and scaffolds new primals. But primals do NOT import `sourdough-core` as a dependency. Each primal implements the standard independently using only self-knowledge. The wire format is the contract.

**IMPORTANT**: Do NOT add `sourdough-core` as a crate dependency. That violates primal self-knowledge — a primal only knows itself. Instead, implement the `TransportEndpoint` type locally in your primal's types crate, with the same `#[serde(tag = "transport")]` wire format. sweetGrass and nestGate did this correctly. barracuda and rhizoCrypt: please remove the `sourdough-core` path dep and implement locally.

### The Wire Standard (defined by sourDough, implemented by each primal)

```rust
// Wire format (JSON, serde tagged — implement this locally):
{ "transport": "uds", "path": "/run/user/1000/biomeos/beardog.sock" }
{ "transport": "tcp", "host": "127.0.0.1", "port": 9100 }
{ "transport": "mesh_relay", "peer_id": "strandgate", "capability": "security" }
```

**Env injection**: Primals accept `TRANSPORT_ENDPOINT` as a JSON string. The launcher/Tower Atomic decides the transport — primals never self-bind.

**Compliance check**: `sourdough validate transport <path>` audits any primal for self-binding anti-patterns. strandGate already ran this against 5 primals — all clean (0 self-binding violations).

### What each primal needs

1. **Implement** `TransportEndpoint` locally in your types crate (same serde tagged format — the wire format IS the standard)
2. **Implement** `connect_transport()` locally (UDS/TCP dispatch — ~30 lines of Rust)
3. **Accept** `TRANSPORT_ENDPOINT` env var in main.rs — parse with `serde_json::from_str::<TransportEndpoint>()`
4. **Remove** hardcoded `TcpListener::bind("0.0.0.0:PORT")` from production paths — the launcher binds, not the primal
5. **Keep** `--port` as a Tier 5 fallback (debug/standalone mode only)
6. **Do NOT** import `sourdough-core` — reference it as a specification, not a dependency

### Priority order

| Primal | TCP refs | Priority | Notes |
|--------|----------|----------|-------|
| bearDog | 90 | **HIGH** | Crypto spine — must be transport-injected first |
| toadStool | 101 | **HIGH** | Orchestrator — transport abstraction critical |
| squirrel | 68 | MEDIUM | Metrics — UDS-first default needed |
| rhizoCrypt | 37 | MEDIUM | Discovery transport self-binding |
| nestGate | ~30 | MEDIUM | Storage gateway |
| barracuda | ~25 | LOW | Compute — fewer transport deps |
| coralReef | ~20 | LOW | |
| loamSpine | ~15 | LOW | |
| sweetGrass | ~10 | LOW | Clean after ring elimination |
| skunkBat | ~10 | LOW | |
| petalTongue | ~10 | LOW | |
| biomeOS | ~40 | EXEMPT | Orchestrator — manages transport for others |
| songBird | 267 | EXEMPT | Transport provider — owns the transport layer |

### Reference implementation

sourDough's scaffold templates show the canonical pattern for new primals. Existing primals should reference the wire format and implement locally:
- Wire format spec: `sourDough/crates/sourdough-core/src/transport.rs` (read, don't import)
- Scaffold template: `sourDough/crates/sourdough/src/commands/scaffold/templates/server.rs`
- Correct adoption: sweetGrass `sweet_grass_core::transport` — local type, wire-compatible
- Correct adoption: nestGate `nestgate-types::transport` — local type, wire-compatible
- **Incorrect**: barracuda/rhizoCrypt `sourdough-core` path dep — remove and implement locally

**Target**: All non-exempt primals accept `TRANSPORT_ENDPOINT` by Wave 103. sourDough `validate transport` will be run against the full ecosystem and results published.

---

## biomeOS Team — Rebuild for LocalTrusted

v4.14 (`a459ec58`) adds `LocalTrusted` access level — UDS callers get orchestration method access without BTSP tokens. This directly unblocks `nucleus-deploy --graph-deploy`.

**Action**: Rebuild and harvest biomeOS v4.14 to depot. Once deployed, `composition.deploy` from local UDS should succeed without capability token. We'll retest `--graph-deploy` immediately.

---

## coralReef Team — Rebuild for capabilities.list

`15d1702` adds `capabilities.list` alias. Once rebuilt and deployed, IPC compliance goes from 11/12 to 12/12.

**Action**: Rebuild and harvest coralReef to depot. Quick verification:
```bash
echo '{"jsonrpc":"2.0","method":"capabilities.list","params":{},"id":1}' \
  | socat - UNIX-CONNECT:/run/user/1000/biomeos/coralreef-core-default.sock
```

---

## Deployment Status

| Gate | NUCLEUS | Federation | Mesh | Evolution Incoming |
|------|---------|------------|------|--------------------|
| **eastGate** | 13/13 FULL | *:7700 LIVE | bootstrap_peers:0 (songbird gap) | songbird rebuilt, biomeOS/coralReef pending |
| **strandGate** | Core + compute | :7700 LIVE | Peer confirmed alive | songbird 4eb5111d available |
| **ironGate** | Deployed (23 UDS) | — | — | Cascade 22/22 |
