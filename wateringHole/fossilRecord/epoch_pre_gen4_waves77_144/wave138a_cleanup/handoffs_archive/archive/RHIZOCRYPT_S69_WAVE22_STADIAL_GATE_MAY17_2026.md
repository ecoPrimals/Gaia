# rhizoCrypt S69 — Wave 22 Stadial Gate Response

**Date**: May 17, 2026
**Owner**: rhizoCrypt
**Scope**: `dag.partial_dehydrate` upstream ask + stadial checklist + composition readiness

---

## Summary

Response to Wave 22 stadial gate audit. Three categories of work:

1. **Upstream ask**: `dag.partial_dehydrate` — wetSpring's highest-priority
   request for Tenaillon 2016 (264-clone LTEE pipeline)
2. **Checklist compliance**: `capabilities.list` format, stability tiers,
   composition readiness docs
3. **Verification**: Hex string acceptance (gap #6) confirmed resolved

## Changes

### `dag.partial_dehydrate` (upstream ask)

Computes a Merkle root over current vertices without closing the session.

**Wire format:**
```json
→ { "method": "dag.partial_dehydrate", "params": {
      "session_id": "dag-...",
      "vertex_ids": ["<hex>", ...] // optional — omit for all vertices
    }}
← { "merkle_root": "<blake3>", "sealed_count": 3, "open_count": 1,
    "session_open": true }
```

- If `vertex_ids` is omitted or empty, all vertices are included (matches
  `dag.merkle.root` output)
- Session remains open — this is a **read-only** operation
- `provenance.partial_dehydrate` wire-name alias included
- Added to `METHOD_CATALOG`, `capability_registry.toml` (`stability = "evolving"`),
  handler dispatch, API spec

### `capabilities.list` format compliance

Response now includes `capabilities` (array) and `count` (integer) per
`CAPABILITY_WIRE_STANDARD.md`, alongside existing `methods` for backward
compatibility with existing consumers.

### Stability tier annotations

All 32 registered capabilities in `capability_registry.toml` now have
explicit `stability` annotations: 31 `"stable"`, 1 `"evolving"`
(`dag.partial_dehydrate`).

### Composition readiness documentation

README updated with:
- Downstream pairing table (wetSpring, lithoSpore, projectFOUNDATION, healthSpring)
- Degradation behavior when rhizoCrypt is unavailable
- Stability tier summary

### Hex string acceptance (composition gap #6)

Verified **closed**. `parse_hash32` accepts both hex strings and `[u8; 32]`
byte arrays with 7 unit tests. Shared gap with loamSpine resolved since S60.

## Universal Standards Checklist

| Category | Status | Notes |
|----------|--------|-------|
| Health triad | PASS | liveness, readiness, check |
| UDS socket | PASS | `$XDG_RUNTIME_DIR/biomeos/rhizocrypt.sock` |
| TCP fallback | PASS | `--port` / `RHIZOCRYPT_PORT` |
| CLI server subcommand | PASS | `server --port` |
| Standalone startup | PASS | No FAMILY_ID/NODE_ID required |
| `capabilities.list` format | PASS | Now includes `capabilities`, `count` |
| `identity.get` | PASS | Canonical response |
| Method naming | PASS | All `{domain}.{operation}` |
| BTSP when FAMILY_ID set | PASS | Phase 1/2/3 |
| ChaCha20-Poly1305 | PASS | `btsp-v1` |
| FAMILY_ID + INSECURE guard | PASS | Refuses to start |
| Zero metadata leakage | PASS | Stripped binary |
| deny.toml bans | PASS | ring, openssl, aws-lc-sys |
| Edition 2024 | PASS | Workspace Cargo.toml |
| Stability tiers | PASS | All methods annotated |
| Degradation docs | PASS | Added to README |
| Downstream pairing | PASS | Added to README |
| primal.announce | N/A | Ecosystem-wide pattern, not yet adopted |
| btsp.capabilities | N/A | Ecosystem-wide pattern, not yet adopted |

## Stats

- 1,642 tests passing (all features)
- 173 `.rs` files, ~53,623 lines
- 0 clippy warnings, 0 fmt diffs
- Deep debt: 12-category audit clean
