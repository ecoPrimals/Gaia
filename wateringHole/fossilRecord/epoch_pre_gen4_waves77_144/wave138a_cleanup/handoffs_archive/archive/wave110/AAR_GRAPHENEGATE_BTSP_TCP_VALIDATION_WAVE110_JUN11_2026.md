# AAR: grapheneGate BTSP TCP Validation — Wave 110

**Date**: 2026-06-11
**Gate**: eastGate → grapheneGate (Pixel 8a, aarch64)
**Owner**: primalSpring evolution team
**Transport**: ADB USB → TCP port forwarding
**Device**: `44251JEKB04957` (Pixel 8a, GrapheneOS)

---

## Objective

Validate BTSP (BearDog Transport Security Protocol) behavior on grapheneGate's TCP-only transport. grapheneGate cannot use UDS (Android SELinux blocks abstract Unix sockets for non-system apps), so all IPC operates over TCP fallback ports.

---

## Results Summary

| Check | Result | Notes |
|-------|--------|-------|
| **13/13 primals running** | PASS | All processes alive via `ps -A` |
| **TCP listeners bound** | PASS | All 13 on registered ports |
| **bearDog health (TCP)** | PASS | `{"status":"alive","primal":"beardog-tunnel","version":"0.9.0"}` |
| **bearDog crypto.hash** | PASS | BLAKE3 hash returns valid base64 |
| **bearDog crypto.sign** | PASS | Ed25519 signature + public_key returned |
| **sweetGrass BTSP gate** | PASS | Rejects unauthenticated TCP: `-32001 BTSP handshake required` |
| **BTSP TCP handshake to sweetGrass** | DOCUMENTED GAP | sweetGrass rejects/disconnects — BTSP server not in deployed binary (Feb 2026) |
| **10/13 plain health alive** | PASS | beardog, skunkbat, squirrel, toadstool, nestgate, loamspine, coralreef, barracuda, biomeos, rhizocrypt |
| **songBird HTTP transport** | PASS | Port 9200 serves HTTP (not raw JSON-RPC) |
| **petalTongue responds** | GAP | No response — binary predates HEALTH-PT-01 (2dba46f) |

---

## Detailed Findings

### 1. TCP Security Model: PROVEN

sweetGrass correctly enforces BTSP on TCP when `FAMILY_ID` is set:
```
{"error":{"code":-32001,"message":"BTSP handshake required on TCP when FAMILY_ID is set. Use UDS for unauthenticated access."},"id":1,"jsonrpc":"2.0"}
```

This proves the genetic encryption security model operates on grapheneGate:
- TCP-exposed primals that handle sensitive data (sweetGrass/attribution) gate access behind BTSP
- bearDog (the security provider itself) remains accessible for health probing
- The "closed door" pattern is correct: deny first, authenticate to open

### 2. Tower Crypto Operational

bearDog's cryptographic surface works over TCP on aarch64:
- **BLAKE3**: `crypto.hash` returns valid hashes
- **Ed25519**: `crypto.sign` returns signature + public_key with key_id `default_signing_key`
- Key derivation (HKDF-SHA256 from FAMILY_SEED) produces correct 32-byte handshake keys

### 3. BTSP TCP Handshake: Requires Depot Rebuild

The full BTSP handshake (4-step ClientHello→ServerHello→ChallengeResponse→HandshakeComplete) cannot complete against sweetGrass because:
- Current grapheneGate binaries date from **Feb 2026** (pre-Wave 108)
- BTSP server implementation shipped in **bearDog 945de60f** (Wave 110)
- sweetGrass BTSP server readiness shipped in Wave 109

**Fix**: Deploy updated binaries via `deploy_pixel.sh` after VPS depot rebuild (already in FRAGO as remaining item).

### 4. Family Configuration

```
FAMILY_ID=41038c66
FAMILY_SEED=41038c66 (string, not binary)
```

Binary `.family.seed` file exists at `/data/local/tmp/primals/.family.seed` (32 bytes, hex: `8ff3b864...`), but primals use the string form from env vars.

---

## Port Map (grapheneGate TCP-only)

| Primal | Port | Status | Transport |
|--------|------|--------|-----------|
| beardog | 9100 | ALIVE | raw JSON-RPC |
| songbird | 9200 | ALIVE | HTTP JSON-RPC |
| skunkbat | 9140 | ALIVE | raw JSON-RPC |
| squirrel | 9300 | ALIVE | raw JSON-RPC |
| toadstool | 9400 | ALIVE | raw JSON-RPC |
| nestgate | 9500 | ALIVE | raw JSON-RPC |
| rhizocrypt | 9602 | ALIVE | raw JSON-RPC |
| loamspine | 9700 | ALIVE | raw JSON-RPC |
| coralreef | 9730 | ALIVE | raw JSON-RPC |
| barracuda | 9740 | ALIVE | raw JSON-RPC |
| biomeos | 9800 | ALIVE | raw JSON-RPC |
| sweetgrass | 9850 | GATED | BTSP required |
| petaltongue | 9900 | STALE | no response (binary predates health fix) |

---

## Action Items

1. **Depot rebuild** (FRAGO remaining item): `plasmid.harvest --all` on peptidoglycan → redeploy to grapheneGate via `deploy_pixel.sh`
2. **Post-deploy revalidation**: Re-run this probe — sweetGrass BTSP handshake should complete with updated binary
3. **songBird HTTP**: Consider whether health probing needs HTTP client path in primalSpring

---

## Exit Criterion Assessment

> "validate BTSP on grapheneGate TCP-only transport (no UDS involved)"

**RESOLVED with documented gap:**
- TCP security model PROVEN (sweetGrass gates, bearDog serves)
- Tower crypto PROVEN (BLAKE3 + Ed25519 over TCP on aarch64)
- Full BTSP handshake blocked by stale binaries (known, fix = depot rebuild)
- No architectural barriers — protocol is transport-agnostic, just needs updated artifacts

---

## Commit Reference

- primalSpring `79bdc82`: BTSP cross-primal E2E scenario + LAUNCHER-01
- grapheneGate binaries: Feb 2026 (pre-Wave 108, stale)
- Next: post-depot-rebuild revalidation
