# Dark Forest Glacial Gate Standard

**Version**: 1.0.0
**Date**: May 14, 2026
**Status**: Active — stadial entry gate
**Authority**: primalSpring (L2 coordination)
**Related**: `BTSP_PROTOCOL_STANDARD.md`, `birdsong/DARK_FOREST_BEACON_GENETICS_STANDARD.md`, `ECOBIN_ARCHITECTURE_STANDARD.md`

---

## Abstract

The Dark Forest Glacial Gate defines five security invariants that every NUCLEUS
deployment must satisfy before stadial transition. Named after the Three-Body
Problem principle: the safest strategy in a hostile universe is to remain
invisible. A NUCLEUS composition reveals nothing about its internal structure,
identity, or capabilities to external observers.

These invariants are validated by the `s_dark_forest_gate` scenario in
primalSpring (Tier::Rust structural, no live primals needed) and should be
adopted by downstream springs via their `guidestone` feature gate.

---

## Gate Criteria

### Pillar 1: Zero Metadata Leakage

| Requirement | Validation |
|-------------|------------|
| Release binaries are stripped (no debug symbols) | ecoBin `stripped = true` in manifest |
| No hostnames, usernames, or filesystem paths embedded | Build-time path sanitization via `strip` + release profile |
| BirdSong beacons are encrypted to observers | Beacon payload is ChaCha20 encrypted with beacon seed; observers see noise |
| DNS queries never leak primal identity | All external DNS routed through Songbird; primals have no direct network |

**Pass condition**: All primal entries in `manifest.toml` declare `stripped = true`.
BirdSong encryption is structural (DARK_FOREST_BEACON_GENETICS v2.0 requires
encrypted beacons when `BEACON_SEED` is set). No primal binary contains
hardcoded external hostnames.

### Pillar 2: Zero Port Exposure

| Requirement | Validation |
|-------------|------------|
| UDS-only is the default transport | `PRIMALSPRING_TCP_TIER5` must be unset by default |
| TCP ports are opt-in, never default | Zero-Port Tower Atomic standard (Wave 10) |
| Port numbers are configurable via environment | `ports.env` uses `${VAR:-default}` pattern |
| No well-known fingerprint from port scanning | Configurable defaults, not fixed constants in binaries |

**Pass condition**: Tier 5 TCP discovery is off when `PRIMALSPRING_TCP_TIER5`
is unset. All 13 primal port assignments in `tolerances` match `ports.env`.
No port collision in the assignment table.

### Pillar 3: Songbird as Sole Network Surface

| Requirement | Validation |
|-------------|------------|
| All external traffic routes through Songbird | Deploy graphs use `by_capability = "network"` → songbird |
| No primal directly opens external TCP listeners | Only Songbird advertises `http`, `tls`, `mesh` capabilities |
| NAT traversal via Songbird STUN/TURN | cellMembrane relay is Songbird-operated |
| Cross-gate federation uses Songbird mesh | Multi-node graphs route through songbird nodes |

**Pass condition**: Every deploy graph that includes external network access
has a songbird node. No non-songbird graph node advertises `http` or `tls`
capabilities. The `tower_atomic` fragment includes songbird.

### Pillar 4: BTSP Crypto Integrity

| Requirement | Validation |
|-------------|------------|
| All IPC authenticated via BTSP handshake | 13/13 primals implement `btsp.negotiate` |
| ChaCha20-Poly1305 AEAD for data in transit | BTSP Phase 3 cipher negotiation returns `chacha20-poly1305` |
| HKDF-SHA256 key derivation from family seed | Handshake key info string is `btsp-v1` |
| No cleartext in production | `FAMILY_ID` set + `BIOMEOS_INSECURE=1` = refuse to start |
| Seed fingerprints verify binary authenticity | BLAKE3 checksums in `checksums.toml` for all binaries |

**Pass condition**: The BTSP protocol constants match the standard. Deploy
graphs declare `secure_by_default = true` in metadata. The `btsp.capabilities`
method is registered. All manifest primal entries that declare `seed_fingerprint`
use BLAKE3.

### Pillar 5: Enclave Computing

| Requirement | Validation |
|-------------|------------|
| Dual-tower ionic pattern for sensitive data | healthSpring proto-nucleate has `egress_fence` metadata |
| Compute dispatch respects enclave boundaries | toadStool dispatch uses `FAMILY_ID` for session isolation |
| Content-addressed storage is opaque | NestGate BLAKE3 hashes reveal no metadata about content |
| Provenance chains don't leak internal details | sweetGrass attribution uses opaque agent identifiers |

**Pass condition**: The healthspring enclave proto-nucleate graph declares
`trust_model` and `bonding_policy` with enclave semantics. Content-addressed
capabilities (`content.*`) are routed to NestGate which uses BLAKE3 (opaque).
The provenance trio graph fragment includes the three provenance primals.

---

## Dark Forest Membrane Classification (Wave 77b)

The 5 pillars above apply with different strictness depending on which
membrane layer a component belongs to. This is the **diderm membrane
classification** — see `DIDERM_DOMAIN_ARCHITECTURE.md` for the full
trust barrier model.

| Pillar | Outer Membrane (`primals.eco`) | Peptidoglycan (trust barrier) | Inner Membrane (`primal.eco`) |
|--------|-------------------------------|-------------------------------|------------------------------|
| 1. Zero metadata leakage | **RELAXED** — Cloudflare sees visitor IPs, headers, timing. Acceptable for world-facing surface. | **STRICT** — VPS provider sees only encrypted relay traffic volume/timing. No primal identity or capability surface leaked. | **STRICT** — zero metadata leakage. Stripped binaries, no hostnames, BirdSong encrypted. |
| 2. Zero port exposure | **RELAXED** — 80/443 (Caddy), 53 (DNS ns2). | **STRICT** — 3478 (TURN), 2222 (sync relay), 22 (admin SSH). | **STRICT** — UDS-only default. Songbird :7700 sole federation surface. |
| 3. Songbird sole network surface | **N/A** — Caddy is the network surface by design. | **STRICT** — only Songbird TURN relay handles cross-membrane traffic. | **STRICT** — all external traffic routes through Songbird. |
| 4. BTSP crypto integrity | **N/A** — external users don't use BTSP. | **STRICT** — BTSP tokens are opaque. Peptidoglycan relays but cannot read, modify, or forge them. | **STRICT** — full BTSP enforcement, ChaCha20-Poly1305 AEAD, TrustedIssuerRegistry. |
| 5. Enclave computing | **N/A** — no compute on outer membrane. | **STRICT** — no biomeOS, no orchestration, no compute. Pure relay. | **STRICT** — full enclave boundaries, BTSP-gated dispatch. |

**The trust barrier invariant**: Peptidoglycan MUST NOT be able to read,
modify, or forge inner membrane traffic. It is a dumb pipe with
BTSP-opaque relay. cellMembrane Wave 75 confirmed: "BTSP tokens OPAQUE
in all relay channels."

### Content Layer (`nestgate.io`)

The content layer follows **inner membrane classification** (STRICT) for
all 5 pillars. Content integrity is verified by BLAKE3 hashes regardless
of delivery path. Even content served through the outer membrane CDN can
be validated by comparing hashes with the inner membrane's canonical copy.

---

## Validation Tiers

### Tier::Rust (Structural — available now)

The `s_dark_forest_gate` scenario in primalSpring validates all five pillars
by reading configuration, fragments, and registry at compile time. No live
primals needed. This is the gate for interstadial → stadial transition.

### Tier::Live (Wire — deferred to stadial phase)

Live validation requires multi-gate deployments with external observers:
- Verify encrypted BirdSong beacon payloads on the wire
- Probe that BTSP handshakes reject cleartext
- Confirm no non-Songbird TCP listeners from external scan
- Validate enclave boundary enforcement with cross-family dispatch attempts

---

## Spring Adoption

Each downstream spring should adopt Dark Forest validation via their
`guidestone` CI gate. The pattern follows the existing registry cross-sync:

```rust
// In spring's guidestone test module:
#[cfg(feature = "guidestone")]
#[test]
fn dark_forest_graph_compliance() {
    // Verify spring's deploy graphs carry secure_by_default = true
    // Verify no non-songbird nodes advertise http/tls capabilities
    // Verify tower_atomic fragment referenced in all compositions
}
```

Springs that already CI-validate against the 445-method registry can add
Dark Forest checks as an additional axis in the same test suite.

### Minimum Spring Requirements

| Requirement | What to Check |
|-------------|---------------|
| Deploy graphs | All `[graph.metadata]` sections declare `secure_by_default = true` |
| Tower inclusion | All compositions reference `tower_atomic` fragment (BearDog + Songbird + skunkBat) |
| No direct network | No spring-local nodes advertise `http.*` or `tls.*` capabilities |
| BTSP in graphs | All graph nodes that interact with primals declare `security_model = "btsp"` or `"tower_delegated"` |

---

## References

- BTSP Protocol Standard: `BTSP_PROTOCOL_STANDARD.md`
- Dark Forest Beacon Genetics: `birdsong/DARK_FOREST_BEACON_GENETICS_STANDARD.md`
- ecoBin Architecture: `ECOBIN_ARCHITECTURE_STANDARD.md`
- Membrane Channel Architecture: `MEMBRANE_CHANNEL_ARCHITECTURE.md`
- Zero-Port Standard: primalSpring `s_zero_port_standard` scenario
- Deployment Validation: `DEPLOYMENT_VALIDATION_STANDARD.md`
- Diderm Domain Architecture: `DIDERM_DOMAIN_ARCHITECTURE.md`
- Sovereignty Standards: `SOVEREIGNTY_STANDARDS.md` (§Sovereignty Shadow Membrane Applicability)
- fieldMouse Contract: `gardens/cellMembrane/specs/FIELDMOUSE_CONTRACT.md` (peptidoglycan is a fieldMouse)

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-04 | Wave 77b: Added §Dark Forest Membrane Classification — per-layer strictness for outer/peptidoglycan/inner membrane. Trust barrier invariant. Content layer classification. |
| 2026-05-14 | Initial: 5 pillars, structural validation, spring adoption guidance. |
