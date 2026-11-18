# sweetGrass v0.7.36 — Stadial Gate: Wave 22 Hardening

**Date**: May 17, 2026
**From**: sweetGrass team
**Audit**: Wave 22 Stadial Gate — All Upstream Primals

---

## Summary

sweetGrass v0.7.36 resolves all items from the Wave 22 stadial gate audit.
The HIGH-priority composition gap (TCP without BTSP) is closed, manifest drift
reconciled, and all stadial checklist items addressed.

---

## Changes

### Gap 7 — TCP BTSP Enforcement (HIGH → RESOLVED)

Raw JSON-RPC on TCP is now rejected with `-32001` when `FAMILY_ID` is set.
The autodetect path (`handle_tcp_with_autodetect`) previously allowed raw
JSON-RPC as a third branch alongside BTSP handshake modes. This violated
the Dark Forest Glacial Gate Standard's 5-pillar security invariants.

**Behavior now:**
- TCP + `FAMILY_ID` set → BTSP handshake **mandatory** (length-prefixed or JSON-line)
- TCP + no `FAMILY_ID` → raw JSON-RPC allowed (dev mode)
- UDS → always allows raw JSON-RPC (localhost-only, trusted transport)
- Dead code (`handle_tcp_connection_raw_with_first`) removed

### deny.toml Hardening

Added explicit bans for `aws-lc-sys` and `aws-lc-rs` per stadial security
standard. Pre-existing bans: `ring`, `openssl`, `openssl-sys`, `native-tls`,
`reqwest`, `ureq`, protobuf family.

### capabilities.list Enrichment

- Added `count` field (total method count)
- Added `btsp` block: `{ supported, required, capabilities: ["chacha20-poly1305", "null"] }`
- Dynamic `transport` array: includes `tcp` when `SWEETGRASS_PORT` is set

### Manifest Alignment

`genomeBin/manifest.toml`:
- `latest`: `0.7.3` → `0.7.36`
- `versions`: expanded to include `0.7.36`, `0.7.35`, `0.7.3`
- Added `seed_fingerprint`
- Expanded `capabilities` list to include `lifecycle`

### Stability Tiers

All 37 registered methods in `capability_registry.toml` now have `stability`
annotations:
- **stable**: 33 methods (core braid, attribution, provenance, health, lifecycle, tools)
- **beta**: 4 methods (`attribution.witness`, `auth.check`, `auth.mode`, `auth.peer_info`)

### Degradation Documentation

CONTEXT.md now documents:
- What happens when sweetGrass is down (braids not created, attribution deferred, science NOT gated)
- Downstream dependents table (lithoSpore, wetSpring, projectFOUNDATION, rhizoCrypt/loamSpine, skunkBat)

---

## Metrics

| Metric | Value |
|--------|-------|
| Version | v0.7.36 |
| Tests | 1,549 pass, 0 failures |
| LOC | 55,049 |
| Clippy | 0 warnings (pedantic + nursery) |
| Methods | 37 canonical + 10 aliases |
| ecobin_grade | A++ |

---

## Stadial Readiness Checklist

| Item | Status |
|------|--------|
| Health triad | PASS |
| UDS socket | PASS |
| TCP fallback (port 9850) | PASS |
| `--port` for JSON-RPC | PASS |
| Standalone startup | PASS |
| `capabilities.list` shape | PASS (with `count`, `btsp`) |
| `identity.get` | PASS |
| Semantic method naming | PASS |
| BTSP on TCP when FAMILY_ID set | PASS (v0.7.36) |
| deny.toml bans | PASS (aws-lc-sys added) |
| Edition 2024 | PASS |
| Stability tiers | PASS (all 37 methods) |
| Degradation docs | PASS |
| Downstream pairing docs | PASS |

### Remaining (deferred, not blocking stadial)

- `primal.announce` (self-registration) — awaits ecosystem-wide adoption pattern
- `btsp.capabilities` as a registered method — currently exposed via `capabilities.list` response; dedicated method deferred
- JH-11 token key distribution — awaits BearDog key distribution mechanism

---

## Downstream Action Required

None — sweetGrass is stadial-ready. Downstream consumers should use canonical
method names per GAP-36 resolution (v0.7.35).
