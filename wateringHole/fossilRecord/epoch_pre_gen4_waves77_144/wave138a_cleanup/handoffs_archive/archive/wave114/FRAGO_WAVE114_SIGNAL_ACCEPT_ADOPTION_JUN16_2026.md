# FRAGO: Converge on sourdough riboCipher Transport Standard

**Date**: 2026-06-16T11:46Z (updated 12:05Z)  
**From**: primalSpring overwatch (eastGate)  
**To**: ALL primal teams  
**Priority**: P1 for Friday deadline  
**Standard**: `sourdough_core::transport::ribocipher` + `ribocipher_server`  

---

## Architecture: Convergence, Not Shared Code

Primals do NOT import primalSpring. Primals do NOT "wire" sourdough directly.

**sourdough defines the standard. Each primal converges independently.**

This is more robust than shared code: each primal's accept loop evolves to match
the sourdough-defined wire format. The validation (primalSpring) then confirms
convergence by probing deployed NUCLEUS instances from the plasmidBin depot.

---

## The Standard (sourdough_core::transport::ribocipher)

sourdough defines:
- Wire format: `[tier_byte][protocol_type_or_envelope]`
- `RiboCipherAcceptLoop` — reference accept loop pattern
- `detect_signal()` — tier + protocol classification  
- `ConnectionRoute` enum — deterministic routing after classification
- Legacy fallback policy (Warn → Reject migration path)

**Each primal must converge its accept loop to consume the signal prefix.**
The specific implementation is up to each team — the wire format is the contract.

---

## Convergence Pattern (reference from sourdough)

```rust
// Each primal evolves its own version of this pattern:
// 1. Read first byte
// 2. Classify: 0xEC=Clear, 0xED=Mito, 0xEE=Nuclear, other=Legacy
// 3. If signal tier: consume envelope bytes, route by protocol_type
// 4. If legacy: route by first_byte heuristic ({=JSON, G/P/H=HTTP, else=BTSP)
```

The minimum viable convergence for Friday:
```rust
// At connection accept, before any existing read logic:
let mut first = [0u8; 1];
stream.read_exact(&mut first).await?;
if first[0] == 0xEC || first[0] == 0xED || first[0] == 0xEE {
    let mut _version = [0u8; 1];
    stream.read_exact(&mut _version).await?;
    // Signal consumed — proceed with existing handler
} else {
    // Legacy client — prepend first[0] back to stream processing
}
```

---

## Per-Primal Status + Fix Guidance

| Primal | Current State | Fix |
|--------|---------------|-----|
| **petaltongue** | ✅ Reference impl | Already works |
| **coralreef** | ✅ Passes (accepts connection, no health method) | No change needed |
| **nestgate** | ✅ Passes (accepts connection, no health method) | No change needed |
| **beardog** | Has code, debug mode-detection race | Wire `accept_signal()` before BTSP frame parse |
| **squirrel** | Has enum, not wired | Wire `accept_signal()` in TCP accept loop |
| **songbird** | Needs + TLS config fix | Add `accept_signal()` + fix federation URL |
| **rhizocrypt** | Needs | Add `accept_signal()` at UDS/TCP accept |
| **barracuda** | Needs | Add `accept_signal()` at UDS/TCP accept |
| **loamspine** | Needs | Add `accept_signal()` at UDS/TCP accept |
| **toadstool** | Needs | Add `accept_signal()` at UDS/TCP accept |
| **sweetgrass** | Needs | Add `accept_signal()` at UDS/TCP accept |

---

## Why This Matters for Friday

Without signal acceptance, `nucleus_launcher` health probes report UNREACHABLE for
primals that are actually running. This means:
- `gate.update` can't validate "13/13 ALIVE" on any gate
- ABG members connecting via riboCipher-aware clients get rejected
- The mesh can't self-validate health state

**The fix is mechanical** — 3-5 lines at each primal's connection accept entry point.
Use the pattern above. Test with:

```bash
# From primalSpring:
cargo run --bin nucleus_launcher -- --profile primalspring validate --scenario ribocipher-signal-acceptance
```

---

## Genetics Architecture Reference

| Tier Byte | sourdough constant | Stream | Status |
|-----------|-------------------|--------|--------|
| `0xEC` | `SIGNAL_CLEAR` | MitoBeacon (clear) | **ACTIVE — converge now** |
| `0xED` | `SIGNAL_MITO` | MitoBeacon (obfuscated) | Defined, not active |
| `0xEE` | `SIGNAL_NUCLEAR` | Nuclear (sealed) | Defined, not active |

sourdough is the SSOT. BearDog owns both genetics streams. `FAMILY_SEED` IS mito-beacon material.

---

## Also Fixed

- `s_socket_discovery` now recognizes capability-domain sockets (`compute.sock`,
  `storage.sock`, etc.) and family-suffixed naming (`{primal}-{family}.sock`,
  `{cap}-{family}-tarpc.sock`). Previous false-positive orphan count: 28 → expected: 0.

---

*Filed by primalSpring overwatch — disseminate to all primal teams immediately.*
