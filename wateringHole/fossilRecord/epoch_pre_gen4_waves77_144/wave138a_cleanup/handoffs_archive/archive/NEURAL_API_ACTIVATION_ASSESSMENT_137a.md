# AAR — Neural API Activation Assessment (Wave 137a)

**Date**: Jul 12, 2026
**Gate**: sporeGate
**Operator**: agentic session
**Priority**: HIGH — operational gap between built infrastructure and deployment practice

---

## Summary

Assessed Neural API readiness on sporeGate in response to the Wave 137a
Neural API as Deployment Authority directive. Found the infrastructure
is present but the orchestration layer is not running. Documented the
exact gap and what each team needs to do.

---

## Current State — sporeGate

### What IS Running

| Component | PID | Uptime | Mode |
|-----------|-----|--------|------|
| `biomeos api` | 859 | 5+ days (Jul 6) | HTTP/WebSocket API server |
| bearDog server | 602114 | active | Crypto IPC (`beardog.sock`) |
| songBird mesh | — | active | Port 7700 listening |

- **26 primal sockets** live in `/run/membrane/`: bearDog, songBird, skunkBat,
  nestGate, petalTongue, coralReef, loamSpine, sweetGrass, toadStool, squirrel,
  barracuda, rhizoCrypt, provenance, permanence, plus crypto/transport aliases.
- biomeOS `doctor`: 2/2 healthy in user namespace, system resources healthy.

### What is NOT Running

| Component | Mode | What It Does |
|-----------|------|-------------|
| `biomeos neural-api` | Graph orchestration | capability.call routing, lifecycle management, graph execution, composition health |

**The `api` mode and `neural-api` mode are distinct.** The `api` mode provides
HTTP/WS access. The `neural-api` mode provides the graph-based orchestration,
L4 adaptive routing, lifecycle management, and capability translation that the
directive describes. The Neural API is **not running on sporeGate**.

### Available Graphs

3 deployment graphs in `wateringHole/graphs/`:
- `context_weave_anchored.toml`
- `impulse_post_signed.toml`
- `waterfall_publish.toml`

### Socket Permissions

All `/run/membrane/*.sock` sockets are `root:root srw-------`. This blocks
non-root processes from connecting. Same pattern as the SIGN-01 blocker.
Neural API will need root access or socket permission fixes to route
`capability.call` to primal sockets.

---

## Gap Analysis

| What the Directive Says | What Exists | Gap |
|------------------------|-------------|-----|
| Neural API live 23 days | `biomeos api` running 5 days | Different mode — `api` ≠ `neural-api` |
| 320+ capability translations | In biomeOS codebase | Not activated — neural-api not running |
| 171 route table entries | In biomeOS codebase | Not activated |
| LifecycleManager supervises primals | systemd manages each primal | LifecycleManager not started |
| `capability.call` routes to primals | Direct socket paths used | No routing layer active |
| Cross-gate via songBird | songBird mesh listening | Neural API not on either end |

---

## Activation Plan — sporeGate

### Step 1: Start Neural API (sporeGate — ready NOW)

```bash
sudo biomeos neural-api \
  --socket /run/membrane/neural-api.sock \
  --graphs-dir /home/sporegate/Development/ecoPrimals/infra/wateringHole/graphs
```

Validates: socket discovery, capability translation table, primal health scan.

### Step 2: Validate capability.call Round-Trip

```bash
# Route through Neural API to bearDog crypto
echo '{"jsonrpc":"2.0","id":1,"method":"capability.call","params":{"domain":"crypto","method":"sign_ed25519","params":{"message":"dGVzdA==","key_id":"depot-signer","purpose":"test"}}}' \
  | socat - UNIX-CONNECT:/run/membrane/neural-api.sock
```

Success: response contains `signature` + `public_key` from bearDog.

### Step 3: Validate lifecycle.status

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"lifecycle.status","params":{}}' \
  | socat - UNIX-CONNECT:/run/membrane/neural-api.sock
```

Success: returns health of all 26 discovered primal sockets.

### Step 4: Promote to systemd Service

```ini
[Unit]
Description=biomeOS Neural API — Graph Orchestration Layer
After=network.target

[Service]
Type=simple
ExecStart=/path/to/biomeos neural-api --socket /run/membrane/neural-api.sock --graphs-dir /path/to/graphs
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Step 5: Execute Deployment Graph

```bash
biomeos graph execute waterfall_publish.toml --socket /run/membrane/neural-api.sock
```

---

## Team Handoffs

### cellMembrane Team

Wire `membrane deploy.*` commands as CLI front-ends to Neural API:
- `membrane deploy.composition <gate> <tier>` → `capability.call("composition", "deploy", ...)`
- `membrane deploy.graph <gate> <graph.toml>` → `capability.call("graph", "execute", ...)`
- `membrane lifecycle.status` → `capability.call("lifecycle", "status", ...)`

These route through the Neural API socket, not direct primal sockets.

### biomeOS Team

- Activate LifecycleManager as primary supervisor (systemd → biomeOS → primals)
- Dependency-aware restart ordering (bearDog → songBird → mesh)
- Composition health aggregation endpoints

### bearDog / All Primals

- Socket permissions: IPC sockets should be accessible to the Neural API
  process (currently `root:root srw-------`, needs group or world read)
- Transition from direct socket paths to `capability.call` pattern

### Mesh Team (songBird)

- Cross-gate `capability.call` routing via songBird `http.proxy`
- Requires Neural API running on both ends of the mesh
- Blocked by FLOCKGATE-MESH port 7700 gap for flockGate

---

## Also Delivered This Session

| ID | Status | Details |
|----|--------|---------|
| FP-DEPLOY | **DONE** | footPrint SPA live at `primals.eco/footprint/` — Vite build, Caddy handle_path, CSP |
| SKUNKY-DEPLOY | **DONE** | skunky-ingest on golgi (dry-run) — tailing Caddy logs, systemd enabled |
| Ecosystem manifest | **DONE** | bind_mode + mobility enum fixes unblocked cascade-sense |

---

*Wave 137a: Neural API infrastructure is built (26 sockets, 3 graphs,
320+ translations in code) but the orchestration layer (`biomeos neural-api`)
is not running. The `biomeos api` HTTP server is a different mode. Activation
is a single command — validation pending. Socket permissions are a cross-cutting
blocker (same root cause as SIGN-01). First live composition (footPrint) and
log ingest (skunky-ingest) deployed this session.*
