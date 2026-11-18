# biomeOS v3.89 — Wave 67: capability.call Proxy (P0 BLOCKER RESOLVED)

**Date**: June 1, 2026  
**From**: southGate (biomeOS)  
**To**: primalSpring coordination, eastGate mesh validation  
**Wave**: 67 (Glacial Cutover Phase 0)

---

## P0 BLOCKER RESOLVED: capability.call RPC

**Root cause**: `capability.call` was fully implemented in the Neural API server
(`neural-api-{family}.sock`) but returned `-32601` when callers hit the biomeOS
API socket (`biomeos-api-{family}.sock`). Cross-gate probes and discovery often
land on the API socket first.

**Fix**: API socket now auto-proxies `capability.call`, `graph.execute`, and
`topology.primals` to the Neural API socket via `neural-api-client`. If the
Neural API isn't running, a clear `-32002` error with startup instructions is
returned instead of the misleading `-32601`.

**Architecture**:
```
Client → biomeos-api.sock → proxy_to_neural_api() → neural-api.sock
                                                       → CapabilityHandler::call()
                                                       → NeuralRouter::forward_request()
                                                       → Provider primal
```

## Changes

- `crates/biomeos-api/src/unix_server.rs`: Added async proxy dispatcher for
  Neural API methods, `proxy_to_neural_api()` function, updated
  `capabilities.list` to advertise proxied methods
- `crates/neural-api-client/src/lib.rs`: Made `connection` module public for
  proxy access to `json_rpc_call`
- Updated identity.get note, -32601 error message, test assertions

## Stats

- 424 biomeos-api tests pass, 0 failures
- Full workspace clean build verified

## Remaining southGate P0 Items

1. ~~biomeOS capability.call RPC~~ — **DONE** (this handoff)
2. Songbird security socket fix — separate repo (`ecoPrimals/primals/songbird`)
3. bearDog S4 auth config — separate repo (`ecoPrimals/primals/bearDog`)

## Commits

- `9ed36983` — API socket proxy implementation
- `e8c47e01` — gate.service.* capability registry entries
- `c1e4c2f4` — proxy message polish and test fix

---

*Wave 67. capability.call P0 blocker resolved. Ready for eastGate mesh validation.*
