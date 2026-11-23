# footPrint Phase 2 — ironGate Deployment Ready

**Date**: 2026-08-04 08:00 EDT | **Wave**: 156b | **Gate**: ironGate (10.13.37.7)
**From**: ironGate local overwatch

---

## EXECUTIVE SUMMARY

footPrint Phase 2 deployment on ironGate is **STRUCTURALLY READY**. Server starts,
health endpoint responds, and the CAS client connects to nestgate.sock via riboCipher
[0xEC, 0x01] transport signal — `health.check` confirmed live against NUCLEUS nestGate
v0.5.0. CAS data operations (`content.list`) return BTSP authentication required (expected
production posture). 572 tests pass.

**Remaining blocker**: BTSP authentication for CAS write/read operations. Options:
1. nestGate team adds local-trust exception for same-gate callers (no BTSP for membrane group)
2. TypeScript BTSP client (X25519 + HKDF-SHA256 + ChaCha20-Poly1305 — significant effort)
3. Cleartext override env var (`BIOMEOS_INSECURE=1` + no `FAMILY_ID` — dev only)

**footPrint is deployable NOW** — health, projects, proxy, agent bridge all work. CAS
persistence is the only feature awaiting BTSP resolution.

---

## VALIDATION RESULTS

```
Port:               3002 (3000=reserved, 3001=petalTongue)
MEMBRANE_SOCKET:    /run/membrane/nestgate.sock
Transport:          riboCipher [0xEC, 0x01] + JSON-RPC 2.0 NDJSON

GET /api/health:    ✓ {"status":"ok","version":"2.0.0","uptime":3}
GET /api/projects:  ✓ ["lansing-scuffle"]
GET /api/cas/health:✓ {"primal":"nestgate","status":"healthy","version":"0.5.0"}
GET /api/cas/index: ✗ "BTSP authentication required" (expected)
```

**Socket connectivity**: PROVEN via `sg biomeos` group context.
**Permission model**: `membrane` user/group has socket access (systemd service configured).

---

## CHANGES THIS SESSION

### Neural API Client (`src/neural-api.ts`)
- JSON-RPC 2.0 over UDS with **riboCipher [0xEC, 0x01]** transport signal prefix
- Targets `/run/membrane/nestgate.sock` directly (biomeOS only proxies capability.call/graph.execute)
- Graceful degradation: socket → NESTGATE_URL HTTP → 503 disabled
- 9 tests with mock UDS server (strips riboCipher prefix)

### Deploy Configs
- **Port**: 3002 (not 3000/3001 which are occupied on ironGate)
- **Caddy snippet**: Points to `10.13.37.7:3002`, explicit WebSocket upgrade headers
- **systemd service**: `MEMBRANE_SOCKET=/run/membrane/nestgate.sock`, `ReadOnlyPaths=/run/membrane`
- **README**: Documents BTSP gap, CAS routing order, port allocation

### Test Suite
- 572 tests, 36 files, ~750ms
- Neural API tests validate riboCipher framing + mock responses

---

## IRONGATE PORT ALLOCATION

| Port | Service | Status |
|------|---------|--------|
| 3000 | (unknown, localhost-only) | Occupied |
| 3001 | petalTongue | LIVE |
| 3002 | **footPrint** | READY |
| 7700 | nestGate (HTTP health only) | LIVE |
| 8080 | (public, unknown) | Occupied |
| 8081 | (localhost, unknown) | Occupied |
| 8082 | songBird drawbridge | LIVE |

---

## UPSTREAM GAPS FOR PRIMAL TEAMS

### nestGate — BTSP local-trust (HIGH PRIORITY for Phase 2)

footPrint (and likely all gardens/protists on same gate) needs to call `content.put`,
`content.get`, `content.list` without full BTSP X25519 handshake. Proposed solutions:

1. **Same-gate trust**: If caller connects from `membrane` group via UDS, skip BTSP
   (process-level authentication via SO_PEERCRED). Already authenticated by filesystem perms.
2. **Local-only token**: nestGate issues a session token to membrane-group callers on
   `auth.local` method; subsequent calls include token in params.
3. **INSECURE env flag**: `NESTGATE_INSECURE_LOCAL=1` disables BTSP on UDS only (not TCP).

**Recommendation**: Option 1 (SO_PEERCRED) — most primal-like, zero config, already
secure via filesystem permissions. The socket is group-writable `biomeos` only.

### golgi/sporeGate — Caddy DNS routing

`footprint.primals.eco` DNS + Caddy config needs pointing to ironGate (10.13.37.7:3002).
Caddy snippet is ready at `deploy/caddy-footprint-api.snippet`.

### biomeOS — Neural API method routing

The `biomeos.sock` currently only auto-proxies `capability.call` and `graph.execute`.
For full Neural API pattern, it should also proxy `content.*` methods to nestGate
(capability-based routing). Until then, consumers target primal sockets directly.

---

## DEPLOY COMMANDS (copy-paste when BTSP resolved or accepted without CAS)

```bash
# On ironGate as root
mkdir -p /opt/ecoPrimals/protists
cd /opt/ecoPrimals/protists
git clone ssh://git@git.primals.eco:2222/protoKarya/footPrint.git
cd footPrint
npm ci && npm run build

cp deploy/footprint.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now footprint

# Verify
curl http://localhost:3002/api/health
journalctl -u footprint -f
```

---

## PHASE 2 STATUS

| Component | Status | Blocker |
|-----------|--------|---------|
| Express server | **READY** | — |
| Static client (Vite build) | **READY** | — |
| Health endpoint | **PROVEN** on NUCLEUS | — |
| Project CRUD (local JSON) | **READY** | — |
| Agent bridge (JSON-RPC 2.0) | **READY** | — |
| petalTongue WS bridge | **READY** (petalTongue on :3001) | — |
| External proxy (songBird) | **READY** | — |
| CAS read/write via nestGate | **BLOCKED** | BTSP auth |
| CAS health check | **PROVEN** | — |
| Caddy routing | **READY** (snippet prepared) | sporeGate deploy |
| systemd service | **READY** | — |

**footPrint is deployable without CAS.** Projects persist locally. CAS dual-write
activates automatically once BTSP is resolved — no code change needed.

---

*Session complete. ironGate Phase 2 deployment structurally validated against live
NUCLEUS. riboCipher transport signal working. BTSP auth gap documented for nestGate
team. Caddy snippet ready for sporeGate/golgi. 572 tests, zero errors.*
