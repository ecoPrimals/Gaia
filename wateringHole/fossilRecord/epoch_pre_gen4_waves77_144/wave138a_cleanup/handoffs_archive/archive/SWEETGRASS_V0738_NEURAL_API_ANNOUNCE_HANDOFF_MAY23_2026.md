# sweetGrass v0.7.38 — Neural API `primal.announce` (Wave 43)

**Date**: May 23, 2026
**From**: sweetGrass team
**Audit**: primalSpring Wave 43 — Neural API `primal.announce` adoption
**Priority**: LOW (per Wave 43 blurb — nest tier)

---

## Summary

sweetGrass now self-registers with biomeOS's Neural API routing layer
on startup via `primal.announce` JSON-RPC. This enables adaptive
`capability.call` routing for provenance/attribution/braid operations.

---

## Implementation

### Wire Payload

```json
{
  "method": "primal.announce",
  "params": {
    "primal": "sweetgrass",
    "socket": "<resolved UDS path>",
    "pid": <process ID>,
    "capabilities": ["provenance", "attribution", "braid"],
    "methods": [<all 37 registered methods>],
    "signal_tiers": ["nest"],
    "cost_hints": {
      "provenance": 10.0,
      "attribution": 8.0,
      "braid": 12.0
    },
    "latency_estimates": {
      "provenance": 15,
      "attribution": 10,
      "braid": 20
    },
    "version": "0.7.38"
  }
}
```

### Neural-API Socket Discovery

1. `$NEURAL_API_SOCKET` — explicit override
2. `$XDG_RUNTIME_DIR/biomeos/neural-api-{family}.sock`
3. `/tmp/biomeos/neural-api-{family}.sock`

Where `{family}` from `$ECOPRIMALS_FAMILY_ID` / `$BIOMEOS_FAMILY_ID`
(default: `ecoPrimal`).

### Timing

Fires 100ms after UDS listener spawns (background task, non-blocking).
Graceful degradation: if biomeOS is unavailable, sweetGrass continues
in standalone mode with debug-level logging.

---

## Validation

After sweetGrass announces, verify routing weights:

```bash
echo '{"jsonrpc":"2.0","method":"neural_api.routing_weights","params":{},"id":1}' | \
  socat - UNIX-CONNECT:$XDG_RUNTIME_DIR/biomeos/neural-api-ecoPrimal.sock
```

Should show entries for `provenance.*`, `attribution.*`, `braid.*` with
sweetGrass as a provider.

---

## Metrics

| Metric | Value |
|--------|-------|
| Version | v0.7.38 |
| Tests | 1,560 pass (+7 neural announce tests) |
| LOC | 55,496 |
| Clippy | 0 warnings |
