# graftGate — Wave 157k Full Darwin Depot Rebuild AAR

**Date**: Aug 12, 2026 (evening) | **Wave**: 157k | **From**: graftGate
**Status**: **15/15 darwin depot CURRENT.** NUCLEUS redeployed with D11 fix. D12 filed: swarmVine socket path convention mismatch.

---

## Cascade Summary

Pulled all repos from Forgejo post-ortho-sweep. Changes received:

| Repo | Key Commits | What Changed |
|------|-------------|--------------|
| biomeOS | `af267161` | **D11 fix**: swarmVine added to all NUCLEUS deploy graphs + bootstrap order |
| songBird | `b8c22577`, `a5dbe79b2` | Windows build fix (P2 #6), content.locate mesh scope |
| swarmVine | `0e4cb75` | Windows `#[cfg(unix)]` fix (P2 #7) |
| toadStool | 15 files | Runtime Vulkan probe, system_query refactor |
| wateringHole | multiple | ironGate/southGate/primalSpring AARs fossilized, grapheneGate AAR |
| primalSpring | 25 files | `composition/deploy_health.rs` added, graph updates |

---

## Full Darwin Depot Rebuild — 15/15 CURRENT

All 15 primals rebuilt from current HEADs for `aarch64-apple-darwin`:

| Binary | Size | Source Commit | Status |
|--------|------|---------------|--------|
| beardog | 6.3M | (unchanged) | Clean |
| songbird | 17M | `b8c22577` (Windows + content.locate) | Clean |
| skunkbat | 2.6M | (unchanged) | Clean |
| swarmvine | 2.1M | `0e4cb75` (Windows fix) | Clean |
| biomeos | 16M | `af267161` (D11 fix) | Clean |
| toadstool | 6.1M | `1640e7b96` (Vulkan probe) | Clean |
| validate_gpu | 2.2M | (unchanged) | Clean |
| coralreef | 6.6M | (unchanged) | Clean |
| nestgate | 6.7M | (unchanged) | Clean |
| rhizocrypt | 5.8M | (unchanged) | Clean |
| loamspine | 3.8M | (unchanged) | Clean |
| sweetgrass | 10M | (unchanged) | Clean |
| squirrel | 2.8M | (unchanged) | Clean |
| petaltongue | 13M | (unchanged) | Clean |
| sourdough | 2.7M | `3dd320a` (atomic model fix) | Clean |

**Total**: 104M. All timestamps Aug 13 01:35 UTC on golgiBody.

---

## Depot Status

| Target | Count | Status |
|--------|-------|--------|
| `aarch64-apple-darwin` | **15/15** | **CURRENT** (Aug 13) |
| `x86_64-unknown-linux-musl` | 15/15 | CURRENT (sporeGate) |
| `aarch64-unknown-linux-musl` | 15/15 | CURRENT (sporeGate + ironGate) |
| `x86_64-pc-windows-gnu` | — | STALE (blueGate) |

---

## NUCLEUS Redeploy — D11 Verification

Redeployed NUCLEUS with fresh binaries including biomeOS `af267161` (D11 fix).

**D11 fix confirmed**: swarmVine now appears in biomeOS's primal list:
```
Primals: ["beardog", "songbird", "skunkbat", "toadstool", "coralreef", "barracuda",
          "nestgate", "rhizocrypt", "loamspine", "sweetgrass", "squirrel", "petaltongue", "swarmvine"]
```

biomeOS correctly launches swarmVine in the bootstrap sequence after songBird (per graph dependency).

---

## New Divergence: D12 — swarmVine Socket Path Convention

**Problem**: biomeOS expects swarmVine's socket at `$XDG_RUNTIME_DIR/membrane/swarmvine-{family_id}.sock`, but swarmVine's `platform_paths::resolve_runtime()` resolves to `$XDG_RUNTIME_DIR/biomeos/` (using `NAMESPACE = "biomeos"`). The socket never appears where biomeOS checks, so biomeOS marks swarmVine as DEGRADED and enters a resurrection loop (5 attempts → dead).

**Root cause**: swarmVine was developed independently and uses its own `platform_paths` module with `NAMESPACE = "biomeos"`. Other primals (bearDog, songBird, etc.) use the `/membrane/` subdirectory convention. When biomeOS added swarmVine to the NUCLEUS graph (D11 fix), it assumed the same socket path convention.

**Impact**: swarmVine does not persist in biomeOS-managed NUCLEUS. It starts, binds to the wrong socket path, biomeOS can't find it, kills it. Gossip is unavailable.

**Attempted workaround**: Setting `BIOMEOS_RUNTIME_DIR=/tmp/eco/membrane` in the screen session environment. Does not work because biomeOS spawns child processes with its own env context — the override isn't passed to swarmVine.

**Fix options** (for upstream):
- **(A)** biomeOS graph `tower_atomic_bootstrap.toml`: Add `BIOMEOS_RUNTIME_DIR = "${XDG_RUNTIME_DIR}/membrane"` to the swarmVine node's `[nodes.operation.environment]`. Minimal change, biomeOS team (eastGate).
- **(B)** swarmVine: Change `NAMESPACE` from `"biomeos"` to match `/membrane/` convention. Larger change, ironGate.
- **(C)** biomeOS binary discovery: Check both `/membrane/` and `/biomeos/` subdirectories for sockets. Most robust but adds complexity.

**Recommendation**: Option A is simplest. One line in the graph TOML.

---

## NUCLEUS State (Post-Redeploy)

| Metric | Value |
|--------|-------|
| Primals running | 12 (biomeOS-managed, swarmVine excluded per D12) |
| Capabilities | 1830 registered, 19 logical primals |
| Domains ACTIVE | 20+ (beardog, songbird, skunkbat, toadstool, coralreef, nestgate, rhizocrypt, loamspine, sweetgrass, petaltongue, security, crypto, ed25519, x25519, btsp, ledger, permanence, dag, network, visualization) |
| swarmVine | DEAD (D12 — socket path mismatch, exhausted 5 resurrection attempts) |
| WireGuard | LIVE (`10.13.37.13`) |

---

## Summary

- **15/15 darwin depot CURRENT** — graftGate is the first gate with all darwin binaries at current HEADs
- **D11 VERIFIED** — biomeOS correctly includes swarmVine in the NUCLEUS graph
- **D12 FILED** — swarmVine socket path convention doesn't match biomeOS expectation. Single-line TOML fix for eastGate.
- **sourDough `3dd320a`** — atomic model corrected in previous sub-wave, included in this rebuild
- **All code blockers from ortho sweep absorbed** — songBird Windows, swarmVine Windows, D11

---

*graftGate — Wave 157k full darwin depot rebuild. 15/15 CURRENT. D11 verified (swarmVine in graph). D12 filed (socket path convention — fix option A: one TOML line). 1830 capabilities, 20 domains ACTIVE. 0/0/0 (excluding D12 which is upstream).*

---
*FOSSILIZED Wave 157k interstadial (Aug 13, 2026). Content fully absorbed into ORTHOGONAL_DIMENSIONS_REVIEW.md and ECOSYSTEM_BLURB.md.*
