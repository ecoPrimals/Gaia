> **FOSSILIZED** — Wave 157k Enmeshment (Aug 16, 2026). Findings absorbed into ortho review + blurb.

# AAR: nestGate `content.put` Routing Gap — NOT a nestGate Bug

**Date**: August 14, 2026
**Wave**: 157k
**From**: westGate-CAS
**Re**: Routing gap #11 from provenance trio experiments

---

## Finding

The provenance trio experiments (14/14 PASS) reported `content.put` as "not in
nestGate translation." This was investigated and confirmed as an **upstream
biomeOS Neural API routing gap**, not a nestGate code issue.

## Evidence

nestGate handles `content.put` on ALL three transport surfaces:

| Surface | Location | Status |
|---------|----------|--------|
| UDS dispatch | `dispatch.rs:201` → `content_handlers::content_put()` | **WIRED** |
| HTTP transport | `transport/handlers.rs:138` → `content_ops::put()` | **WIRED** |
| tarpc/JSON-RPC | `json_rpc_handler/content.rs` → `content_ops::put()` | **WIRED** |
| Announce payload | `UNIX_SOCKET_SUPPORTED_METHODS` line 203 | **ADVERTISED** |
| Capability registry | `config/capability_registry.toml` → `content.*` domain | **REGISTERED** |

Any peer calling nestGate directly (UDS, TCP, HTTP) gets `content.put` handled
correctly. The method is also advertised in `capabilities.list` and
`primal.announce` payloads.

## Root Cause

biomeOS Neural API translation table lacks the routing entry to forward
`content.put` calls to nestGate. The switchboard doesn't know to connect
callers to us for this method.

## Action Required

| Team | Action |
|------|--------|
| **eastGate (biomeOS)** | Add `content.put → nestgate` mapping in Neural API translation registry |
| **westGate (nestGate)** | None — already wired and announcing |

## Related

- Gap documented in provenance trio AAR: `WESTGATE_PROVENANCE_TRIO_EXPERIMENTS_AAR_AUG14_2026.md`
- nestGate S150 confirmed all surfaces wired (`31a31abad`)
- Same pattern likely applies to other gaps (AEAD, dehydration) — those are bearDog/rhizoCrypt upstream items
