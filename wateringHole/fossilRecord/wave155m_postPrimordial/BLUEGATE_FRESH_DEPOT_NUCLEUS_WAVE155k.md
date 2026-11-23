# blueGate Fresh Depot NUCLEUS Deployment — Wave 155k

**Date**: Jul 30, 2026 09:50 EDT | **Wave**: 155k | **Gate**: blueGate (Windows)
**From**: blueGate overwatch | **Sequence**: A3 (Fresh depot → lifecycle-managed NUCLEUS)

---

## Summary

Pulled 14/14 fresh depot binaries (rebuilt by sporeGate Jul 30) and deployed full
13-primal NUCLEUS stack with correct boot ordering (Tower → Nest → Node → biomeOS).

**Result**: 13/13 primals RUNNING. bearDog `crypto.sign_ed25519` VALIDATED.
toadStool riboCipher framing CONFIRMED. biomeOS v4.47 BTSP auth enforcement OBSERVED.

---

## Cascade

12 repos updated from Forgejo with Wave 155k code:

| Repo | Key Commit | What |
|------|-----------|------|
| bearDog | `d6b1003bb` | Windows platform gating + crypto.sign |
| biomeOS | `4e8f00c9` | Chain 1 COMPLETE, NUCLEUS orchestrator v4.47 |
| songBird | `90466648` | TCP registration uses shared ServiceRegistry |
| toadStool | `2df71399b` | S347 Windows cross-compile fix |
| sweetGrass | `4b5167b` | P2 UUID mismatch fix |
| coralReef | `edcd696` | `--bind` alias |
| loamSpine | `5b3cabf` | `--bind` alias |
| rhizoCrypt | `4716bf5` | Cross-compile hygiene |
| barraCuda | `d2ccce46` | MultiDevicePool wire-up |
| cellMembrane | `2b82722` | dns.configure/dns.apply |
| wateringHole | `708336bf` | All chains closed, 50 handoffs fossilized |
| sporePrint | (broken branch) | Non-blocking |

---

## Fresh Depot Binaries (14/14)

All downloaded from `https://depot.primals.eco/primals/x86_64-pc-windows-gnu/`:

| Primal | Version | Size | Delta |
|--------|---------|------|-------|
| bearDog | 0.9.0 | 7.5 MB | was 10 MB (25% smaller) |
| songBird | 0.2.1 | 20.3 MB | was 22.8 MB (depot build, no source-build needed) |
| skunkBat | 0.2.18 | 2.6 MB | unchanged |
| nestGate | 0.5.0 | 8.1 MB | unchanged |
| loamSpine | 0.9.16 | 4.1 MB | unchanged |
| rhizoCrypt | 0.14.17 | 5.7 MB | unchanged |
| sweetGrass | **0.8.0** | 15.1 MB | was 0.7.61 (major bump, G3 wiring) |
| petalTongue | **1.7.0** | 25 MB | was 1.6.6 |
| squirrel | 0.1.0 | 3.6 MB | unchanged |
| biomeOS | 0.1.0 | 19 MB | was 18.2 MB |
| toadStool | 0.2.0 | 8.8 MB | unchanged |
| barraCuda | 0.4.0 | 4.9 MB | unchanged |
| coralReef | 0.2.0 | 6.8 MB | unchanged |
| sourdough | 0.1.0 | 2.8 MB | (build tool, not runtime) |

---

## NUCLEUS Stack — Health Proofs

### Process Inventory (13/13 running)

```
ProcessName      PID   Mem(MB)
beardog        14200    12.6
songbird       12588    14.8
skunkbat       15276     6.9
nestgate       24256     9.7
loamspine       6480     6.7
rhizocrypt     14676     7.0
sweetgrass      4368     8.0
petaltongue    22760    10.9
squirrel       13904    17.2
biomeos        12316    10.1
toadstool      19732    11.7
barracuda      21900     8.6
coralreef      13872     6.9
────────────────────────────
TOTAL          13/13   131.1 MB
```

Memory dropped from 147.5 MB (Wave 155i depot) to **131.1 MB** with fresh builds.

### JSON-RPC Health

| Primal | Port | Status | Response |
|--------|------|--------|----------|
| bearDog | 9100 | **HEALTHY** | `{"primal":"beardog","status":"alive","version":"0.9.0"}` |
| songBird (IPC) | 9901 | **HEALTHY** | `{"primal":"songbird","services":0,"status":"healthy","version":"0.2.1"}` |
| songBird (disc) | 7700 | **HTTP OK** | HTTP 200 (discovery port, not JSON-RPC) |
| nestGate | 9200 | **HTTP OK** | Full comms layers: event, MCP, SSE, streaming, websocket |
| loamSpine | 9201 | **HEALTHY** | `{"primal":"loamspine","status":"ok","version":"0.9.16"}` |
| rhizoCrypt | 9202 | **RESPONSIVE** | Returns alive, delayed response pattern |
| sweetGrass | 9203 | **HEALTHY** | `{"primal":"sweetgrass","status":"healthy","version":"0.8.0"}` |
| petalTongue | 9204 | **RUNNING** | Connection reset on probe (known pattern) |
| squirrel | 9205 | **HEALTHY** | `{"primal":"squirrel","status":"healthy","version":"0.1.0"}` |
| biomeOS | 9206 | **BTSP AUTH** | HTTP 200 /health, 403 on API (correct behavior) |
| toadStool | 9300 | **RIBOCIPHER** | Rejects bare JSON-RPC, accepts `[0xEC, 0x01]` framing |
| barraCuda | 9301 | **HEALTHY** | `{"status":"alive"}` |
| coralReef | 9302 | **RESPONSIVE** | Responds, `health` method not found (different method) |

### HTTP Health

| Primal | URL | Status |
|--------|-----|--------|
| songBird | :7700/health | **200 OK** |
| nestGate | :9200/health | **200** `v0.5.0, 5 comms layers` |
| sweetGrass | :9213/health | **200** `v0.8.0, memory store, 0 braids` |
| biomeOS | :9206/health | **200** (empty body — lifecycle coordinator) |

---

## Key Validations (Wave 155k features)

### 1. bearDog crypto.sign_ed25519 — WORKING

```json
Request:  crypto.sign_ed25519 {"message":"<base64>"}
Response: {
  "algorithm": "Ed25519",
  "key_id": "default_signing_key",
  "public_key": "pGdlDu8KLgpZC1sLGDXX3ZmjVtTVuNU4TD4WEB6G5Ws=",
  "signature": "z8O0lAVIbHZtAiO993h+SzL2cLMYySxmtrqGW7Mm+5P..."
}
```

Both `crypto.sign_ed25519` and `crypto.sign` return identical valid Ed25519 signatures.

`auth.public_key` returns:
- DID: `did:key:z6Mkryaa7n6hfpSbGaZwbqPMD6MzXukgdQK3XRKzwFSgce8o`
- Algorithm: Ed25519
- Hex public key available for verification

**Provenance 7/7 readiness**: bearDog can now sign provenance attestations on Windows.

### 2. toadStool riboCipher Enforcement — CONFIRMED

Bare JSON-RPC: `"Connection rejected: missing riboCipher signal. Prepend [0xEC, 0x01]."`
With `[0xEC, 0x01]` prefix: `{"primal":"toadstool","status":"alive","version":"0.2.0"}` — HEALTHY.

### 3. biomeOS v4.47 BTSP Auth — ENFORCED

`/health` returns 200. All `/api/v1/*` endpoints return **403 Forbidden**.
This is correct behavior — biomeOS requires BTSP authentication for API access.

### 4. bearDog v0.9.0 FAMILY_SEED Requirement — NEW

bearDog v0.9.0 now requires `FAMILY_SEED` or `BEARDOG_FAMILY_SEED` env var for
production BTSP mode. Previous versions accepted bare `FAMILY_ID` only.

### 5. songBird 0.2.1 Depot Build — NO SOURCE BUILD NEEDED

The fresh depot `songbird.exe` (0.2.1) runs on Windows out of the box.
No more source-build workaround needed. The P0 Windows fix (`90466648`) is included.

---

## Boot Order Validated

Per blurb guidance: Tower → Nest → Node → biomeOS LAST.

```
09:45:18  bearDog      (Tower — crypto/trust foundation)
09:45:22  songBird     (Tower — discovery/IPC)
09:45:26  skunkBat     (Tower — defense)
09:45:28  nestGate     (Nest — content-addressed storage)
09:45:30  loamSpine    (Nest — certificates)
09:45:32  rhizoCrypt   (Nest — DAG)
09:45:34  sweetGrass   (Nest — braids)
09:45:36  petalTongue  (Nest — topology)
09:45:38  squirrel     (Nest — capabilities)
09:45:40  toadStool    (Node — workload orchestrator)
09:45:42  barraCuda    (Node — GPU compute, --no-gpu-probe)
09:45:44  coralReef    (Node — shader compiler)
09:45:46  biomeOS      (Orchestrator — discovers all, starts last)
```

All primals accepted TCP binding. No UDS fallback needed on Windows.

---

## Issues for Upstream

### P2: biomeOS API auth without BTSP client

biomeOS v4.47 correctly enforces 403 on API endpoints. However, there is no
documented BTSP client handshake sequence for external callers (overwatch, CLI tools).
Need: documented BTSP auth flow for API consumers, or a `/api/v1/health` exemption.

### P3: coralReef `--version` output

coralReef emits a full ERROR log line before version output:
```
2026-07-30T13:44:50.212964Z ERROR coralreef: invalid command line error=coralreef-core 0.2.0
```
Should be clean version string like other primals.

### P3: petalTongue connection reset on JSON-RPC probe

petalTongue v1.7.0 forcibly closes TCP connections on JSON-RPC health probes.
Process is running and stable, but the IPC protocol may have changed.

### P3: sporePrint branch corruption

`infra/sporePrint` reports `fatal: your current branch appears to be broken` during cascade.
Non-blocking but needs manual repair or re-clone.

### INFO: bearDog FAMILY_SEED requirement

bearDog v0.9.0 requires `FAMILY_SEED` env var. This is a breaking change from v0.8.x
which accepted `FAMILY_ID` alone. Deployment scripts should be updated.

---

## blueGate Status

| Dimension | Status |
|-----------|--------|
| Primals running | **13/13** |
| Memory footprint | **131.1 MB** (down from 147.5 MB) |
| Depot currency | **14/14 fresh** (Jul 30 rebuild) |
| Repos synced | **40** (12 updated, 28 current) |
| Boot ordering | **Tower → Nest → Node → biomeOS** ✓ |
| crypto.sign | **VALIDATED** (Ed25519) |
| riboCipher | **VALIDATED** (toadStool enforcement) |
| BTSP auth | **ENFORCED** (biomeOS 403 on API) |
| Platform | Windows x86_64-pc-windows-gnu |
| Transport | TCP-only (all ports) |

**Next**: Sub-builder activation via songBird IPC (J12), Provenance 7/7 live validation.
