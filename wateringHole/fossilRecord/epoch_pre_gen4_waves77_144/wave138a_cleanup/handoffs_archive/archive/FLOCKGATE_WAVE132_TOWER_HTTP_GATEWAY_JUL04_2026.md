# flockGate Handoff — Wave 132: Tower Atomic HTTP Gateway

**Date**: Jul 4, 2026  
**Gate**: flockGate  
**Primals**: songBird, bearDog, skunkBat  
**From**: eastGate overwatch  
**Type**: Feature evolution — sovereign HTTP gateway (replaces Caddy)

---

## Objective

Evolve the Tower atomic trio (songBird + bearDog + skunkBat) into a sovereign HTTP reverse proxy that replaces Caddy on sporeGate. External HTTPS traffic terminates at bearDog (TLS), routes through songBird (mesh dispatch), and reaches backend services on remote gates via `capability.call`.

---

## Architecture

```
INTERNET
    │ HTTPS :443
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  bearDog (TLS front — HotReloadAcceptor, ACME certs)            │
│    Terminates TLS for lab.primals.eco                           │
│    Forwards plain HTTP → songBird gateway (UDS or localhost)     │
└────────────────────────────┬────────────────────────────────────┘
                             │ plain HTTP (Host + path intact)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  songBird HTTP Gateway                                           │
│    Host/path match → capability name + target gate              │
│    capability.call → remote songBird on target gate             │
│    skunkBat advisory scan (non-blocking)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │ capability.call (HTTP POST /jsonrpc)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Remote gate songBird (e.g. ironGate :7700)                     │
│    http.proxy local handler → localhost:8000 (JupyterHub)       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Work Item 1: songBird `http.proxy` IPC Method

**Crate**: `songbird-orchestrator`  
**Location**: `src/http_gateway/unix_listener.rs` (existing, has partial `proxy`/`http.proxy` handler)

The `UnixSocketListener` already defines a `proxy` / `http.proxy` method but routes it to `UniversalProxy` (outbound API proxying). Evolve this into a **reverse proxy** method:

### New method signature

```json
{
  "method": "http.proxy",
  "params": {
    "host": "lab.primals.eco",
    "path": "/hub/login",
    "method": "GET",
    "headers": {"Cookie": "..."},
    "body": null
  }
}
```

### Resolution logic

1. Match `host` + `path` prefix against `ReverseProxyConfig` rules (see Work Item 2)
2. Resolve matched rule → capability name + target gate ID
3. `capability.call` to target gate with `operation: "http.proxy"` and the full request params
4. Target gate's songBird receives `capability.call`, extracts `http.proxy` operation, proxies to local backend (e.g. `localhost:8000`)
5. Return response (status, headers, body bytes) back through the chain

### Existing infrastructure to reuse

- `remote_dispatch.rs` — `forward_to_remote_gate` already sends `capability.call` via HTTP POST to peer `/jsonrpc`
- `CapabilityRouter` in `http_gateway/capability_router.rs` — has `register_provider`, `route()`, discovery
- `UniversalProxy` — rate limiter + cache + credential manager (keep for outbound, split inbound)

---

## Work Item 2: Wire `http_gateway/` Module

**Location**: `songbird-orchestrator/src/http_gateway/`

Currently Phase 1 (stub). Wire into production:

### A. Evolve `ReverseProxyConfig`

Current location: `songbird-config/src/canonical/network/advanced.rs`

```rust
pub struct ReverseProxyConfig {
    pub enabled: bool,
    pub upstream_timeout_secs: u64,
    pub max_upstream_connections: usize,
}
```

**Add route rules**:

```rust
pub struct ReverseProxyConfig {
    pub enabled: bool,
    pub upstream_timeout_secs: u64,
    pub max_upstream_connections: usize,
    pub routes: Vec<ProxyRoute>,
}

pub struct ProxyRoute {
    pub host: String,
    pub path_prefix: String,
    pub capability: String,
    pub target_gate: Option<String>,  // None = auto-discover via mesh
}
```

### B. Wire `HttpGatewayService::start()` into orchestrator startup

In `songbird-orchestrator/src/app/mod.rs` or the server startup path, call `HttpGatewayService::start()` after mesh init. It should:
1. Load `ReverseProxyConfig` from config TOML
2. Register routes into `CapabilityRouter`
3. Start `UnixSocketListener` for bearDog → songBird forwarding

### C. Add Axum catch-all route (optional, Phase 2)

If bearDog forwards via HTTP (not UDS JSON-RPC), add a catch-all `.fallback()` to `build_router` in `http_server.rs` that routes unmatched requests through the gateway logic. But UDS JSON-RPC is preferred for Phase 1.

---

## Work Item 3: bearDog ACME Front

**Crate**: `beardog-acme`  
**Critical gaps identified**:

1. `Http01Solver::serve()` is **never spawned** — issuance will fail without it
2. `HotReloadAcceptor` is **not wired** into `beardog-tunnel` TCP server
3. ACME-stored certs are not auto-loaded into the TLS listener

### Implementation steps

#### A. Spawn HTTP-01 solver during ACME mode

In `beardog-cli/src/handlers/server/mod.rs`, when `ENV_TLS_MODE=acme`:

```rust
// After spawning renewal daemon:
let solver = acme_client.solver().clone();
tokio::spawn(async move {
    if let Err(e) = solver.serve(config.challenge_port).await {
        error!("HTTP-01 solver failed: {e}");
    }
});
```

#### B. Replace static `TlsAcceptor` with `HotReloadAcceptor`

In `beardog-tunnel/src/tcp_ipc/server/mod.rs`:

Replace:
```rust
tls_acceptor: Option<tokio_rustls::TlsAcceptor>,
```

With:
```rust
tls_acceptor: Option<beardog_acme::HotReloadAcceptor>,
```

Accept loop becomes:
```rust
let tls_stream = acceptor.current().accept(tcp_stream).await?;
```

#### C. New gateway listener (port 443)

Add a dedicated TLS listener for the public gateway (separate from bearDog's own IPC TLS):

- Binds `0.0.0.0:443`
- Uses `HotReloadAcceptor` with ACME-issued cert for `lab.primals.eco`
- Accepts TLS connections, reads HTTP request (Host, path, method, headers, body)
- Serializes as JSON-RPC `http.proxy` call
- Sends to songBird UDS (or localhost:7700 `/jsonrpc`)
- Returns response to client

**Config env**: `BEARDOG_GATEWAY_BIND=0.0.0.0:443`, `BEARDOG_GATEWAY_DOMAINS=lab.primals.eco`, `BEARDOG_SONGBIRD_SOCKET=/run/songbird/songbird.sock`

#### D. Renewal hooks `HotReloadController`

When `run_renewal_loop` issues a new cert, call:
```rust
controller.reload_from_store(&store, &domain)?;
```

---

## Work Item 4: skunkBat Advisory Scan

**Crate**: `skunk-bat-core/src/defense/`  
**Scope**: Non-blocking advisory only (no request blocking in Phase 1)

Wire a `security.scan` call from songBird's gateway before dispatching `capability.call`:

```json
{"method": "security.scan", "params": {
    "source_ip": "...",
    "host": "lab.primals.eco",
    "path": "/hub/login",
    "method": "GET"
}}
```

skunkBat responds with threat assessment (score, flags). songBird logs telemetry but does not block. Phase 2 introduces configurable blocking thresholds.

---

## Config Example (songbird.toml)

```toml
[network.reverse_proxy]
enabled = true
upstream_timeout_secs = 30
max_upstream_connections = 100

[[network.reverse_proxy.routes]]
host = "lab.primals.eco"
path_prefix = "/hub"
capability = "jupyter"

[[network.reverse_proxy.routes]]
host = "lab.primals.eco"
path_prefix = "/user"
capability = "jupyter"

[[network.reverse_proxy.routes]]
host = "lab.primals.eco"
path_prefix = "/api"
capability = "jupyter"
```

---

## Acceptance Criteria

1. `songBird` accepts `http.proxy` JSON-RPC over UDS, resolves host/path to capability, dispatches via mesh
2. `bearDog` binds :443 with ACME cert for `lab.primals.eco`, forwards plain HTTP to songBird UDS
3. `curl -k https://localhost:443/hub/login` on sporeGate → JupyterHub login page from ironGate
4. skunkBat `security.scan` fires on each request (logged, non-blocking)
5. All tests pass, zero clippy warnings

---

## Dependencies

- ironGate must have JupyterHub running on `localhost:8000` (see IRONGATE handoff)
- songBird mesh must include ironGate as peered (already validated Wave 132b)
- ironGate songBird must register `jupyter` capability via `primal.announce`

---

## Delivery

Push evolved songBird + bearDog + skunkBat to Forgejo. sporeGate cellMembrane team will deploy (see SPOREGATE handoff).

---

*Tower atomic becomes the membrane. Caddy becomes optional.*
