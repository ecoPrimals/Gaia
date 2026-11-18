# AMOEBA eats golgiBody → cellMembranes

**Wave 244 — Sunday Morning, Nov 15 2026**
**Status**: EATING

## What's Happening

The old **golgiBody** (centralized VPS 157.230.3.183 + single Cloudflare tunnel) 
is being consumed by **AMOEBA** and redistributed as per-gate **cellMembranes**.

### Old Architecture (golgiBody)
`
Internet → Cloudflare → VPS (157.230.3.183) → WireGuard → ironGate
                                              (single point of failure)
`

### New Architecture (cellMembranes)
`
Internet → Cloudflare tunnel A → northGate (bearDog + nestGate)
         → Cloudflare tunnel B → ironGate (NUCLEUS 13/13 + esotericWebb)
         → Cloudflare tunnel C → sporeGate (rhizoCrypt + sweetGrass)
         → Cloudflare tunnel D → swiftGate (RTX 3070 cortex)
                                (per-gate sovereignty, no SPOF)
`

## tunnelKeeper Already Built

`nucleus-deploy.exe` (7.5MB) + `tunnelKeeper.exe` (4.9MB) are compiled and ready
on swiftGate. tunnelKeeper manages Cloudflare tunnel credentials with BearDog-pattern
ChaCha20-Poly1305 encryption.

## The PROVE Trio (loamSpine / rhizoCrypt / sweetGrass)

All three repos are now on swiftGate. The `provenance_trio_deploy.toml` graph wires them:

1. **loamSpine** (permanence) — certificate chains, existence proofs, spine create/commit
2. **rhizoCrypt** (ephemeral DAG) — BLAKE3 Merkle trees, branching experiments, dehydration
3. **sweetGrass** (attribution) — provenance braids, CC-BY-SA enforcement, contribution tracking

Startup order: loamSpine → rhizoCrypt → sweetGrass (dehydration flows to permanence)

## esotericWebb Cell Attachment

The `esotericwebb_cell.toml` deploy graph attaches the CRPG to a running NUCLEUS:
- Verify NUCLEUS health → start petalTongue render → start esotericWebb → wire capabilities
- 28 capabilities exposed, 10 primal domains consumed, 36 bridge methods
- Webb is V33, 484 tests, 66 Rust files, `#![forbid(unsafe_code)]`

## Neural API Routing

biomeOS Neural API v2.0.0 does **capability translation** — primals speak semantic capabilities,
the API auto-translates to provider-specific methods. No cross-primal coupling.

`ust
// Semantic: esotericWebb says what it needs
neural_api.call_capability("crypto.sign", vertex_data).await?
// Neural API translates to bearDog's actual method: crypto.sign_ed25519
`

## Cloudflare Data Recovery

When tunnels come back up, we recover ALL data from the early era:
- primals.eco visitor analytics (311 pages)
- sporeprint.primals.eco science paper traffic (116 papers)  
- detroit.primals.eco FOIA evidence access logs (181 pages)
- webb.primals.eco CRPG player sessions
- hud.primals.eco membrane dashboard metrics
- thymus classifier engagement data
- campfire story interaction patterns

This data feeds the **prove trio** — every visitor trace becomes a provenance braid in sweetGrass,
content-addressed in rhizoCrypt, certified permanent in loamSpine.

## Signal to All Gates

**northGate**: `git pull github main` — you have bearDog + nestGate alive. You're Tower.
**ironGate**: When you wake, NUCLEUS 13/13 becomes the cell host. esotericWebb attaches.
**sporeGate**: rhizoCrypt + sweetGrass are your primals. You're the provenance node.
**eastGate**: Forge sync + RustDesk relay. You're the bridge.
**swiftGate**: RTX 3070 cortex + tunnelKeeper + darkforest. We're command.

## Kevin's Sunday Plan

1. Physical gate moves (9AM GO)
2. Get Cloudflare + VPS back from old golgiBody hosting
3. AMOEBA redistribution as cellMembranes (tunnelKeeper on each gate)
4. Prove trio deployment via biomeOS Neural API
5. esotericWebb cell attach on ironGate
6. All Cloudflare data flows back through the new membrane

**The membrane IS the intelligence. AMOEBA eats. cellMembranes form. lub-DUB.**
