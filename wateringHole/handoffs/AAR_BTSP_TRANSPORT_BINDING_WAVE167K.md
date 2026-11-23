# AAR: BTSP Transport-Bound Session Keys (Wave 167k)

**Date**: October 9, 2026
**Operator**: AI/Human pair
**Scope**: bearDog BTSP handshake → riboCipher + mitoCipher + BirdSong genetics integration
**Outcome**: ✅ Deployed to golgiBody, 0 rejections, 2,649 tests pass

---

## Situation

BTSP (BearDog Transport Security Protocol) performed a full 4-step handshake using:
- `family_seed` → HKDF handshake key
- X25519 ephemeral keys → shared secret
- HMAC-SHA256 challenge/response → family membership verification
- Session keys: `HKDF(shared_secret, "btsp-session-v1", session_id)`

**Problem**: Three authentication systems operated in isolation:

| System | Role | Integration with BTSP |
|--------|------|----------------------|
| riboCipher | Transport signal routing (tiers 1-3) | Routing only — not in crypto |
| mitoCipher | Family-obfuscated signal (HMAC tag) | Verified but discarded |
| BirdSong | Lineage/genetics key derivation | Completely separate |

Session keys were identical regardless of whether a connection arrived via:
- Direct BTSP (no signal prefix)
- riboCipher Tier 1 clear signal
- riboCipher Tier 2 mito-obfuscated signal
- With or without BirdSong lineage enrollment

## Action

### New: `TransportBinding` type (crypto.rs)

```
TransportBinding::NONE           → legacy, no signal
TransportBinding::clear(proto)   → Tier 1 local IPC (0xEC)
TransportBinding::mito(proto, tag) → Tier 2 cross-gate (0xED + 4-byte HMAC)
   .with_lineage(hash)           → attach BirdSong genetics (32-byte hash)
```

### Modified HKDF session key derivation

```
v1 (old): HKDF(shared_secret, salt="btsp-session-v1", info=session_id)
v2 (new): HKDF(shared_secret, salt="btsp-session-v2", info=session_id || transport_tag)

transport_tag = [tier_byte, proto_byte, mito_tag[4], lineage_hash[32]] = 38 bytes
```

### Lineage enrichment via BirdSong manager

```
enrich_binding_with_lineage():
  birdsong.list_lineage_chains() → first chain
  HMAC-SHA256(family_seed, "btsp-lineage-binding-v1" || chain_id)
  → 32-byte lineage hash
```

### Session metadata

`BtspSession` now carries `transport_tier: u8` and `lineage_bound: bool` for
downstream introspection.

### All entry points updated

| Entry Path | Binding |
|------------|---------|
| Direct BTSP binary frame | NONE + lineage |
| riboCipher CLEAR → BTSP_BINARY | clear(proto) + lineage |
| riboCipher MITO → BTSP_BINARY | mito(proto, tag) + lineage |
| riboCipher → BTSP_JSONLINE | binding + lineage |
| BTSP JSON-line (server.rs auto-detect) | NONE + lineage |

## Files Modified

| File | Changes |
|------|---------|
| `btsp_handshake/crypto.rs` | +`TransportBinding`, +`derive_session_keys_bound()`, +7 tests |
| `btsp_handshake/handshake.rs` | +`perform_server_handshake_bound()`, +`continue_server_handshake_jsonline_bound()` |
| `btsp_handshake/session.rs` | +`transport_tier`, +`lineage_bound` fields |
| `btsp_handshake/mod.rs` | New exports |
| `connection_handlers.rs` | `dispatch_by_protocol()` now takes binding, +`enrich_binding_with_lineage()` |
| `server.rs` | Direct BTSP path uses `perform_server_handshake_bound()` |

**6 files, +446 lines, −22 lines**

## Backward Compatibility

`TransportBinding::NONE` falls back to v1 salt → identical keys. Existing
clients that don't send riboCipher signals or connect to older primals get
the same session keys they always did. Test `bound_none_matches_unbound`
verifies this invariant.

## Tests

- 7 new crypto tests (binding structure, tier/lineage differentiation, backward compat)
- 2,649 total tests pass (beardog-tunnel)
- 0 BTSP rejections on golgiBody since deploy

## Lessons

1. **Bind transport authentication into session crypto** — routing ≠ binding.
   A mito-verified connection should produce different session keys than clear.

2. **Graceful degradation** — if no lineage chains enrolled, binding is
   transport-only. If no riboCipher signal, binding is NONE. System works
   at every enrollment stage.

3. **Salt versioning** — v1→v2 salt change ensures no accidental key collision
   between bound and unbound sessions, even with empty transport tags.
