# Wave 67 — southGate Glacial Cutover: All 3 P0 Blockers Resolved

**Date:** June 1, 2026
**From:** southGate (wetSpring team)
**To:** primalSpring coordination (eastGate), ironGate (S4 validation)
**Impulse ACK:** `wave67-southgate-glacial-mesh-primals`

---

## Summary

All three P0 glacial blockers assigned to southGate are fixed and pushed:

| Fix | Primal | Commit | Impact |
|-----|--------|--------|--------|
| Security socket discovery | Songbird | `ae9b42f0` | Federation TLS + cross-gate routing unblocked |
| capability.call proxy | biomeOS | `9ed36983` | API socket no longer returns -32601 |
| S4 auth config | bearDog | `a61c37101` | TCP :9100 live, ionic token roundtrip verified |

**eastGate can proceed with Phase 1 mesh validation.**

---

## Detail

### Songbird (`ae9b42f0`)

`SecurityCryptoProvider::from_env()` now checks `SECURITY_PROVIDER_ENDPOINT`
(set by `--security-socket` CLI) before mode-based discovery. Also added to
`discover_neural_api_socket()` chain. All TLS code paths respect the flag.

### biomeOS (`9ed36983`)

API socket proxies `capability.call`, `graph.execute`, `topology.primals`
to Neural API socket. Returns `-32002` with actionable message if Neural API
is not running. `capabilities.list` updated to advertise the methods.

### bearDog (`a61c37101`)

Auth services verified end-to-end:
- TCP :9100 bound, reachable from LAN
- `auth.issue_ionic` → 374-byte EdDSA token
- `auth.verify_ionic` → `{ valid: true }`
- `auth.public_key` → Ed25519 DID for local caching
- `BEARDOG_AUTH_MODE=permissive` (set to `enforced` for formal shadow)
- MethodGate evolution + BTSP config + platform support committed

---

## Next Steps (not southGate)

| Action | Owner |
|--------|-------|
| `discovery.peers` smoke test (eastGate <-> southGate) | eastGate |
| `s_covalent_mesh` live validation | eastGate (primalSpring) |
| S4 formal 7-day shadow gate | ironGate (bearDog auth on southGate provides service) |
| SONGBIRD_PEERS + federation verify | southGate (after Songbird redeploy) |
