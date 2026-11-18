# footPrint — Wave 156c: Manifest-Driven Sources + Coverage Expansion

**Date**: 2026-08-04 | **Gate**: ironGate | **From**: footPrint deep-debt session
**Commit**: `01e1adc` on `protoKarya/footPrint`

---

## Summary

Deep-debt elimination pass focused on three pillars:
1. **Manifest-driven source registration** — sources only activate when endpoints exist
2. **Constants centralization** — single source of truth, no scattered magic values
3. **Test coverage expansion** — 572 → 628 tests (+56), 7 new test files

---

## Changes Made

### Manifest-Driven Source Registration (P1 complete for runtime)

- New `src/client/source-registry.ts`: wraps 8 registrars, gates each on endpoint availability
- `app.ts` reduced from 8 imperative calls to single `registerAllSources()`
- Sources that cannot be satisfied (missing endpoints in registry) are silently skipped
- Michigan/Lansing data only registers when Michigan endpoints are bootstrapped

### Dynamic Category Boosts

- Removed hardcoded `Lansing: 0.6` / `Michigan: 0.4` from `src/types/spatial.ts`
- `deriveCategoryBoosts()` computes regional boosts from manifest coverage areas
- Universal categories (OSM, FEMA, USGS) retain intrinsic boosts
- Regional categories derive boost proportional to inverse coverage area

### Constants Centralization

| Constant | Source | Consumers |
|----------|--------|-----------|
| `CAS_PATH` | constants.ts | nestgate-cas.ts, server.ts, primals.ts |
| `CAS_FAMILY` | constants.ts | nestgate-cas.ts |
| `RPC_TIMEOUT_MS` | constants.ts | petal-tongue.ts |
| `NEURAL_API_TIMEOUT_MS` | constants.ts | neural-api.ts |
| `CACHE_KEY_HASH_LENGTH` | constants.ts | server.ts |

### Membrane Socket Default Unified

- `server.ts` no longer hardcodes fallback socket path
- `createNeuralApiClient()` resolution: `MEMBRANE_SOCKET` env → `/run/membrane/nestgate.sock`
- No more `biomeos.sock` vs `nestgate.sock` confusion

### Dead Code Removed

- `sendUserMessage()` — exported but zero call sites → removed
- `agentMessages[]` queue — written at line 239, never consumed → removed

### Michigan GIS Host → Manifest

- `gisp.mcgi.state.mi.us` removed from hardcoded `ALLOWED_HOSTS`
- Registered as `mi-gisp` endpoint in `manifest-defaults.ts`
- `endpointHosts()` now includes it automatically

### Test Coverage (+56 tests, 7 new files)

| File | Coverage Target |
|------|----------------|
| `nestgate-cas.test.ts` | CAS client CRUD + error handling |
| `storage.test.ts` | Dual-write persistence, graceful CAS failure |
| `discover.test.ts` | Capability scoring, auto-enable logic |
| `petal-tongue.test.ts` | JSON-RPC framing, timeout, reconnection |
| `server-bridge.test.ts` | WebSocket bridge, project.command flow |
| `source-registry.test.ts` | Manifest-gated registration |
| `spatial.test.ts` | Dynamic boost derivation |

---

## Current Metrics

| Metric | Value |
|--------|-------|
| Tests | 628 (43 files) |
| Statement coverage | 48.3% |
| TypeScript errors | 0 |
| ESLint errors | 0 |
| Format violations | 0 |
| Largest file | 604L (server.ts) |

---

## Remaining Evolutionary Targets (glacial priority)

### For footPrint

| Priority | Item | Effort |
|----------|------|--------|
| P2 | Declarative JSON source manifests (CAS-stored) | Medium |
| P2 | Municipality discovery (reverse geocode → source lookup) | Medium |
| P2 | Client E2E tests via Playwright (28 DOM modules at 0%) | High |
| P3 | CSP img-src derived from registered endpoint hostnames | Low |
| P3 | Protocol handlers (shared Overpass/ArcGIS fetch layer) | Medium |

### Upstream Dependencies

| Primal | Need | Status |
|--------|------|--------|
| nestGate | BTSP local-trust (SO_PEERCRED for same-gate UDS callers) | Blocks CAS write |
| songBird | Drawbridge route absorption (proxy → songBird) | Blocks Express removal |
| coralReef | GPU terrain batch (DEM raster → slope/contour) | Blocks terrain offload |

---

## Self-Knowledge Compliance

After this pass, footPrint's production code:
- Does NOT hardcode primal socket paths (env-configured via `MEMBRANE_SOCKET`)
- Does NOT hardcode data source URLs (manifest-driven via `getEndpoint()`)
- Does NOT assume which sources exist (manifest-gated registration)
- Does NOT hardcode category scoring (derived from coverage areas)
- DOES reference `nestGate` by name in comments/docs (acceptable for operator context)
- DOES assume `/ws` routes to petalTongue (deployment knowledge in Caddy config, not code)

---

*Sources are discovered, not hardcoded. Registration is conditional, not imperative.*

---

## Addendum: TCP Local-Trust Discovery (2026-08-04 09:45)

**Critical finding**: BTSP is enforced on UDS only. TCP JSON-RPC (port 8080) provides
full `content.*` access without authentication — this is the designed "local-trust" pattern
for same-gate services.

| Transport | Auth Required | Use Case |
|-----------|---------------|----------|
| UDS (`nestgate.sock`) | **BTSP** (X25519 + ChaCha20-Poly1305) | Inter-primal IPC |
| TCP (`localhost:8080`) | **None** (loopback local-trust) | Same-gate services (footPrint, tideGlass) |

### BTSP Handshake Protocol (documented from binary analysis)

1. Client → `ClientHello` (JSON-line): `{type, client_ephemeral_pub, protocol: "btsp-v1", family_id}`
2. Server → `ServerHello` (JSON-line): `{version, server_ephemeral_pub, challenge}`
3. Client → `ChallengeResponse`: `{type, response: sig(challenge), public_key}`
4. Server verifies via bearDog `btsp.session.verify` (family membership check)
5. Post-handshake: ChaCha20-Poly1305 encrypted tunnel (Phase 3)

The `family` key in bearDog (`key_id: "family"`) can sign challenges, but verification
requires the public key to be registered as a family member — not just a valid signature.

### Resolution

footPrint's Neural API client now defaults to TCP transport. Env resolution:
`NESTGATE_RPC_URL` → `NESTGATE_RPC_PORT` → `MEMBRANE_SOCKET` (UDS) → TCP `:8080`

**Live validated**: Full CAS put/get/list round-trip against production nestGate
(v0.5.0, FAMILY_ID=e8b62b6e) on ironGate over TCP. Two objects stored successfully.

### Upstream Note for nestGate Team

The BTSP UDS gate blocks ALL methods except `health.check` — even `btsp.verify` and
`auth.*` methods are behind the gate, creating a bootstrap paradox for new clients.
The TCP path resolves this for same-gate services, but remote clients would need a
bootstrap mechanism (perhaps a pre-shared session token or out-of-band key exchange).
