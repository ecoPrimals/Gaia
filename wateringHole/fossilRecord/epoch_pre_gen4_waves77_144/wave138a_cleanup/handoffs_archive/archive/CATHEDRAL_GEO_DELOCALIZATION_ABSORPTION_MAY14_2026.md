# CATHEDRAL Geo-Delocalization Absorption

**Date**: May 14, 2026
**From**: CATHEDRAL (lithoSpore + Foundation)
**For**: primalSpring, infrastructure, projectNUCLEUS
**Absorbs**: `LITHOSPORE_USB_DEPLOYMENT.md`, `MEMBRANE_CHANNEL_ARCHITECTURE.md`, `CELLMEMBRANE_FIELDMOUSE_DEPLOYMENT.md`

---

## Executive Summary

CATHEDRAL absorbed the cellMembrane geo-delocalization infrastructure update.
The litho-core discovery chain now extends through Songbird TURN, and
`liveSpore.json` records the operating mode for every validation run.

**Code changes**: 4 files modified in litho-core, zero breakage, all tests pass.
**Schema evolution**: `LiveSporeEntry` gains `discovery_path` + `turn_relay`.
**Documentation**: Spore taxonomy, three operating modes, and discovery chain
diagram added to README and ARCHITECTURE.md.

---

## What Was Absorbed

### 1. Discovery Chain Extension

`litho_core::discovery` previously: env → UDS → None.

Now: env → UDS → Songbird TURN → None.

```rust
pub enum DiscoveryPath { Env, Uds, Turn, Standalone }

pub fn discover_full(capability: &str) -> Option<DiscoveryResult>
pub fn probe_operating_mode() -> (DiscoveryPath, Option<String>)
```

TURN discovery checks `$SONGBIRD_TURN_SERVER` and
`$SONGBIRD_TURN_DISCOVERY_PORT`. When both are set, discovery resolves
through the cellMembrane relay. The actual TURN client protocol is
upstream-blocked (requires Songbird client library).

### 2. liveSpore.json Provenance Evolution

Each validation run now records:

```json
{
  "timestamp": "2026-05-14T14:30:00Z",
  "hostname_hash": "blake3(hostname)",
  "arch": "x86_64",
  "os": "linux",
  "tier_reached": 2,
  "modules_passed": 6,
  "modules_total": 7,
  "runtime_ms": 342000,
  "discovery_path": "uds",
  "turn_relay": null
}
```

Geo-delocalized runs: `"discovery_path": "turn"`,
`"turn_relay": "[RELAY_PUBLIC]:3478"`.

Backward compatible — existing entries without `discovery_path` deserialize
with serde defaults. New entries always include both fields.

### 3. Spore Taxonomy in Documentation

README now documents the ColdSpore → LiveSpore → lithoSpore (Hypogeal
Cotyledon) taxonomy, three operating modes (Standalone / LAN /
Geo-delocalized), and references `LITHOSPORE_USB_DEPLOYMENT.md`.

ARCHITECTURE.md now includes the discovery chain diagram showing the
env → UDS → TURN → Standalone priority and how each maps to an
operating mode.

---

## What Requires Upstream

| Item | Blocked On | Owner |
|------|-----------|-------|
| Songbird TURN client library | Songbird relay client for actual TURN-relayed RPC | Songbird team |
| BearDog FIDO2/CTAP2 for SoloKey witness | BearDog + SoloKey 2 integration (exp096 Phase 4) | BearDog team |
| sporePrint pipeline wiring | `notify-sporeprint.yml` → Zola rendering on primals.eco | sporePrint / Channel 3 |
| USB build script for hypogeal cotyledon | Assembles USB layout per `LITHOSPORE_USB_DEPLOYMENT.md` | CATHEDRAL (next sprint) |
| `liveSpore.json` SoloKey witness field | `solokey_witness: { attestation, key_id }` — awaiting BearDog | BearDog + CATHEDRAL |

---

## Verification

```
cargo check      — PASS (zero warnings, 9 crates)
cargo test       — 35+ tests PASS (includes new DiscoveryPath serde/display tests)
cargo clippy     — zero warnings (pedantic)
```

---

## Cross-References

- `LITHOSPORE_USB_DEPLOYMENT.md` — upstream USB layout spec (absorbed)
- `MEMBRANE_CHANNEL_ARCHITECTURE.md` — three-channel architecture (referenced)
- `CELLMEMBRANE_FIELDMOUSE_DEPLOYMENT.md` — fieldMouse deployment (referenced)
- `CATHEDRAL_HARDENING_PASS_MAY13_2026.md` — previous CATHEDRAL handoff
- `lithoSpore/crates/litho-core/src/discovery.rs` — discovery chain implementation
- `lithoSpore/crates/litho-core/src/spore.rs` — liveSpore.json schema
