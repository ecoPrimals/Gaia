# Genetics Architecture: Eukaryotic Model

**Date**: 2026-06-16  
**From**: eastGate overwatch  
**Status**: DEFINITIVE — this is the canonical genetics position for all primals

---

## Two Streams, One Cell

Like eukaryotic biology: mitochondrial and nuclear DNA coexist in the same cell
but are **compartmentalized** — carried differently, inherited differently, used
for different purposes.

### Stream 1: MitoBeacon (Shared / Relay / Discovery)

| Property | Value |
|----------|-------|
| **Purpose** | Group membership, relay access, mesh discovery, birdsong |
| **Inheritance** | Freely clonable — matrilineal, shared across group |
| **Metaphor** | "Grandma can tell a cousin how to reach you" |
| **Wire signal** | `0xEC` (clear) / `0xED` (mito-obfuscated) |
| **BearDog RPC** | `genetic.derive_lineage_beacon_key` (HKDF, domain `birdsong_beacon_v1`) |
| **Use cases** | ABG member access, RustDesk relay auth, mesh enrollment, depot fetch |
| **Current env** | `FAMILY_SEED` (legacy name — IS mito-beacon material) |

A mitoBeacon gets you **through the relay**. It proves you belong to the family/group.
It does NOT grant permissions — only transport-level access.

### Stream 2: Nuclear Lineage (Per-User / Non-Fungible / Permissions)

| Property | Value |
|----------|-------|
| **Purpose** | Individual identity, permissions, auth, secure tunnels |
| **Inheritance** | **Never copied** — always spawned fresh per generation |
| **Metaphor** | "Your specific DNA — unique, verifiable, non-transferable" |
| **Wire signal** | `0xEE` (nuclear-sealed) |
| **BearDog RPC** | `genetic.derive_lineage_key` + `genetic.mix_entropy` |
| **Use cases** | Per-ABG-member permissions, view/action separation, tiered access |
| **Current env** | Not yet exposed as env var (BearDog internal derivation) |

Nuclear lineage gives each user their **specific identity**. BearDog derives it
fresh each generation — parent hash chain + context entropy. Enables:
- Observer tier (can view, cannot act)
- Reviewer tier (can view + comment, limited action)
- User tier (full action within scope)
- Operator tier (admin)

---

## BearDog Owns Both

BearDog is the sole cryptographic authority. It:
1. **Stores** the mito-beacon material (from `FAMILY_SEED`)
2. **Derives** mito-beacon keys via HKDF for birdsong/dark forest
3. **Spawns** nuclear lineage keys per user/session (never copies)
4. **Validates** both tiers at connection accept

The eukaryotic principle: both live in BearDog, but they are **handled and passed
differently**. Mito material can be scp'd, copied, handed to a field agent. Nuclear
material is always derived on-demand by BearDog from parent lineage + entropy.

---

## riboCipher Wire Mapping

| Tier Byte | Genetics Stream | What It Means |
|-----------|-----------------|---------------|
| `0xEC` | Tag/Clear (legacy) → evolving to MitoBeacon clear | "I belong to this group, serve me plaintext" |
| `0xED` | MitoBeacon obfuscated | "I belong to this group, obfuscate the tunnel" |
| `0xEE` | Nuclear sealed | "I have lineage identity, encrypt per-session" |

Current state: `0xEC` (clear) and `0xED` (mito-beacon) are implemented. toadStool
S320 accepts `0xED` on all accept loops (Unix/TCP/BTSP/early-health) — HMAC tag
read and logged, validation deferred to Wave 115 HKDF. `0xEE` (nuclear sealed) is
defined but deferred until per-user tiered access requires it (Wave 115).

---

## Deprecation Path

| Legacy | Becomes | Timeline |
|--------|---------|----------|
| `FAMILY_SEED` env var | `MITO_BEACON_KEY` (or keep name, modernize docs) | Wave 115 |
| `BEARDOG_FAMILY_SEED` env var | **DEPRECATED** — redundant alias, remove | Wave 115 |
| `GUIDESTONE_SEED` env var | Keep (CI/test isolation override) | — |
| Tag tier (Tier 3 in genetics model) | Fully deprecated → mito-beacon replaces | Wave 115 |
| Per-primal riboCipher ad-hoc fixes | Centralized in `universal-patterns` or sourDough scaffold | Wave 114-115 |

---

## For ABG Compute Access (Wave 114 Goal)

The path from "ABG member" to "sovereign compute" is:

```
ABG Member
    │
    ├── MitoBeacon (shared group key) ─── proves group membership
    │       │
    │       └── RustDesk relay access (transport-level)
    │       └── Depot fetch (can pull binaries)
    │       └── Mesh visibility (can see nodes)
    │
    └── Nuclear Lineage (per-user, BearDog-derived) ─── proves identity
            │
            └── Tiered permissions (observer/reviewer/user/operator)
            └── View vs action separation
            └── Audit trail (generation counter + parent hash)
```

For the Friday deadline: mito-beacon access (shared key via RustDesk) is sufficient.
Nuclear lineage per-user is Wave 115+ evolution.

---

## Server-Side Acceptance (The Actual Fix)

The riboCipher "rejection" by 7/11 primals is a **genetics-layer wiring** issue:

- **BearDog**: Already has full riboCipher detection (UDS + TCP). Failure in logs
  suggests a mode-detection race or socket-path confusion — needs debugging, not new code.
- **Squirrel**: Has `universal-patterns/transport/ribocipher.rs` with proper
  `SignalResult` enum. May not be wired into accept loop.
- **PetalTongue**: Properly strips prefix via `strip_ribocipher_prefix()` using
  `AsyncBufRead::fill_buf` + consume. This is the reference pattern.
- **Other 6 primals**: No detection at all. Their accept loops try to parse
  `[0xEC, 0x01, {...}]` as JSON text.

The fix is NOT "add 2 bytes per primal" — it's ensuring the **genetics layer entry
point** (mito-beacon detection at connection accept) is present in all primals.
This can be centralized:
- Squirrel's `universal-patterns` crate already has the server-side enum
- PetalTongue's `strip_ribocipher_prefix()` is the reference async impl
- A synchronous version exists in primalSpring's test harness

---

*Authored by eastGate overwatch — Jun 16, 2026*
