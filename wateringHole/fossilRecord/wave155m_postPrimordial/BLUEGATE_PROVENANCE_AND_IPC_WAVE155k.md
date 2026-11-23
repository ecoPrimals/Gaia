# blueGate Provenance 7/7 + IPC Registry Validation — Wave 155k

**Date**: Jul 30, 2026 10:05 EDT | **Wave**: 155k | **Gate**: blueGate (Windows)
**From**: blueGate overwatch | **Validates**: A2 (Provenance 7/7), J12 (sub-builder readiness)

---

## Provenance 7/7 — E2E VALIDATED

First live provenance chain on Windows. All seven steps completed successfully using
three primals (sweetGrass v0.8.0, loamSpine v0.9.16, bearDog v0.9.0) communicating
over TCP IPC.

### Chain Execution

| Step | Primal | Method | Result |
|------|--------|--------|--------|
| 1 | loamSpine :9201 | `spine.create` | Spine `019fb34f-2b37-7403-85e2-6e827a65cf84` created with genesis hash |
| 2 | loamSpine :9201 | `entry.append` | DataAnchor at index 1, entry_hash returned (32-byte) |
| 3 | sweetGrass :9213 | `braid.create` | W3C PROV JSON-LD braid `urn:braid:82f1f424f4eb...` with `@context` |
| 4 | loamSpine :9201 | `certificate.mint` | DataProvenance cert `019fb351-a82e-7182-87bf-1f22d70be266` with mint_hash |
| 5 | bearDog :9100 | `crypto.sign_ed25519` | Ed25519 signature, key_id=`default_signing_key`, public_key returned |
| 6 | bearDog :9100 | `crypto.verify_ed25519` | **`{"valid": true}`** — round-trip verified |
| 7 | loamSpine :9201 | `proof.generate_inclusion` | Merkle inclusion proof with path through certificate mint_hash |

### Signature Proof

```json
{
  "algorithm": "Ed25519",
  "key_id": "default_signing_key",
  "public_key": "pGdlDu8KLgpZC1sLGDXX3ZmjVtTVuNU4TD4WEB6G5Ws=",
  "signature": "YsC5LFicuAAhLjjuc609zYbjqhWjj+YInYRO3GN0/SyfdLnH9t93J2TTNU9qnJ/TSewl+8Ua/joYrb5j7hy4BQ=="
}
```

Verification: `{"algorithm":"Ed25519","valid":true}`

### bearDog DID Identity

```
DID:        did:key:z6Mkryaa7n6hfpSbGaZwbqPMD6MzXukgdQK3XRKzwFSgce8o
Algorithm:  Ed25519
Public Key: uhCde0hr9ZelUZPZfMfMkMrkc0Hrx489kZ0bmpDRYQA= (base64)
Hex:        ba109d7b486bf597a55193d97cc7cc90cae47341ebc78f3d919d1b9a90d16100
```

### What This Proves

1. **bearDog crypto.sign is LIVE** — not a stub, returns real Ed25519 signatures
2. **Sign + verify round-trip works** — same key, same message, valid=true
3. **loamSpine spine→entry→certificate→proof chain is intact** — Merkle path valid
4. **sweetGrass W3C PROV braids work** — JSON-LD with `@context`, `@id`, `@type`
5. **Cross-primal IPC over TCP works on Windows** — three primals, no UDS needed
6. **Provenance Trio (sweetGrass + loamSpine + bearDog) is E2E functional**

### API Shape Notes for Upstream Documentation

The provenance chain required iterative parameter discovery. These should be documented:

| Method | Required Params | Notes |
|--------|----------------|-------|
| `spine.create` | `name`, `owner`, `description` | Returns `spine_id` + `genesis_hash` |
| `entry.append` | `spine_id`, `entry_type` (struct variant), `payload` (byte array) | `entry_type: {"DataAnchor": {"data_hash": "...", "content_type": "...", "size": N}}` |
| `braid.create` | `name`, `data_hash`, `mime_type`, `size`, `owner` | Via HTTP POST to `:9213/jsonrpc` |
| `certificate.mint` | `spine_id`, `subject`, `issuer`, `owner`, `cert_type` (struct variant) | `cert_type: {"DataProvenance": {"data_type": "...", "source_id": "...", "collected_at": <u64 epoch ms>}}` |
| `crypto.sign_ed25519` | `message` (base64) | Returns `algorithm`, `key_id`, `public_key`, `signature` |
| `crypto.verify_ed25519` | `message`, `signature`, `public_key` (all base64) | Returns `{"valid": true/false}` |
| `proof.generate_inclusion` | `spine_id`, `entry_hash` (byte array) | Returns full proof with entry, path, spine_id |

---

## J12: songBird IPC Sub-Builder Readiness

### IPC Registry — 10 Primals Registered

All runtime primals registered via `ipc.register` on songBird :9901:

| Primal | Capabilities | Endpoint |
|--------|-------------|----------|
| beardog | crypto.sign, crypto.verify, btsp, auth | tcp://127.0.0.1:9100 |
| nestgate | content.store, content.retrieve, cas | tcp://127.0.0.1:9200 |
| loamspine | spine, certificate, proof, anchor | tcp://127.0.0.1:9201 |
| rhizocrypt | dag, merkle, federation | tcp://127.0.0.1:9202 |
| sweetgrass | braid, provenance, ledger | tcp://127.0.0.1:9213 |
| squirrel | capability, access | tcp://127.0.0.1:9205 |
| toadstool | compute, workload, orchestration | tcp://127.0.0.1:9300 |
| barracuda | gpu, tensor, matmul | tcp://127.0.0.1:9301 |
| coralreef | shader, pipeline, compile | tcp://127.0.0.1:9302 |
| biomeos | lifecycle, composition, nucleus | tcp://127.0.0.1:9206 |

### Capability-First Resolution — WORKING

```
ipc.resolve("crypto.sign")  → beardog    tcp://127.0.0.1:9100
ipc.resolve("braid")        → sweetgrass tcp://127.0.0.1:9213
ipc.resolve("compute")      → toadstool  tcp://127.0.0.1:9300
ipc.resolve("lifecycle")    → biomeos    tcp://127.0.0.1:9206
```

### Mesh Status

```json
{
  "status": "awaiting_init",
  "message": "Mesh not yet initialized - will auto-seed from SONGBIRD_PEERS, persisted state, or WireGuard peers",
  "initialized": false
}
```

Mesh federation is pending — requires `SONGBIRD_PEERS` env var or WireGuard connectivity
to join the multi-gate mesh. Local IPC routing works without mesh.

### J12 Readiness Assessment

| Requirement | Status | Notes |
|-------------|--------|-------|
| songBird IPC server | **RUNNING** | v0.2.1, :9901, healthy |
| Service registry | **POPULATED** | 10 primals, 38 capabilities |
| Capability resolution | **WORKING** | Finds correct primal by capability name |
| Mesh federation | **AWAITING** | Needs SONGBIRD_PEERS or WireGuard |
| sporeGate visibility | **BLOCKED** | Requires mesh init for cross-gate dispatch |
| Build dispatch | **NOT TESTED** | Needs sporeGate-side registration of blueGate as target |

**Conclusion**: blueGate's songBird is ready to receive sub-builder dispatch commands
once mesh federation is established (WireGuard tunnel + SONGBIRD_PEERS pointing to
sporeGate). The local IPC registry and capability resolution are validated.

---

## Port Map (actual bindings)

| Primal | Listen Ports | Protocol |
|--------|-------------|----------|
| bearDog | 9100 | JSON-RPC/TCP |
| songBird | 7700 (HTTP), 9901 (JSON-RPC), 8091, 7780 | HTTP + JSON-RPC |
| skunkBat | 9750 | JSON-RPC/TCP |
| nestGate | 9200 | HTTP + JSON-RPC |
| loamSpine | 9201, 9001 | JSON-RPC/TCP |
| rhizoCrypt | 9202, 9203 | JSON-RPC/TCP (NOTE: took 9203 from sweetGrass) |
| sweetGrass | 64792 (random), 9213 (HTTP) | HTTP JSON-RPC on /jsonrpc |
| petalTongue | 9204 | JSON-RPC/TCP |
| squirrel | 9205 | JSON-RPC/TCP |
| biomeOS | 9206 | HTTP (BTSP-gated API) |
| toadStool | 9300, 64800, 64801 | JSON-RPC/TCP (riboCipher) |
| barraCuda | 9301 | JSON-RPC/TCP |
| coralReef | 9302 | JSON-RPC/TCP |

**Issue**: rhizoCrypt binds to both 9202 AND 9203, stealing sweetGrass's intended
JSON-RPC port. sweetGrass falls back to ephemeral port 64792 for raw TCP. Its HTTP
JSON-RPC on :9213 is stable and should be the canonical endpoint.

---

## Stack Status

```
PRIMALS:  13/13 RUNNING
MEMORY:   139.9 MB
UPTIME:   14+ minutes (all stable)
IPC:      10 primals registered in songBird, capability resolution working
PROV:     7/7 E2E validated (sign + verify round-trip)
MESH:     awaiting_init (local IPC only)
PLATFORM: Windows x86_64-pc-windows-gnu, TCP-only transport
```

---

*Wave 155k — blueGate Provenance 7/7 VALIDATED. First live provenance chain on Windows.
bearDog crypto.sign Ed25519 round-trip proven. songBird IPC registry populated (10
primals, 38 capabilities). Capability-first resolution working. J12 sub-builder
readiness confirmed pending mesh federation.*
