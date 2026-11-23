> **FOSSILIZED** — D11 CLOSED (`af267161` — swarmVine added to biomeOS bootstrap). Cascade findings absorbed into ortho review.

# graftGate — Wave 157k Ortho Sweep Cascade AAR

**Date**: Aug 12, 2026 | **Wave**: 157k | **From**: graftGate
**Status**: Cascade complete. 5 primals rebuilt. Depot refreshed. NUCLEUS redeployed. sourDough atomic model corrected.

---

## Cascade Summary

Pulled all repos from Forgejo (`git.primals.eco`). Changes received:

| Repo | Changes | Key Commits |
|------|---------|-------------|
| songBird | Deep-debt sweep, 148 files, -1,236 lines | `5bc2d398` content.locate, `--node-id` resolved |
| swarmVine | Major evolution, +2,113/-520 lines | `63c8ccc` P2 fixes, riboCipher, G65 default, 90.8% coverage |
| biomeOS | Routing split, lifecycle fixes | `6df4220e` spawn leak fix, `ce812818` deploy→gossip→verify |
| toadStool | wgpu 28, silicon ledger | `3fe38e43` vulkan-portability fix |
| primalSpring | Lifecycle module | `composition/lifecycle.rs` added |
| wateringHole | New deployment signaling spec | `DEPLOYMENT_SIGNALING_EVOLUTION_SPEC.md` |
| whitePaper | subGen evolution | `SWARMVINE_ANT_COLONY_NUCLEUS_ATOMICS.md` rewrite |
| hotSpring | Provenance + validation modules | `spring/provenance.rs`, `spring/validation.rs` |

No changes: bearDog, skunkBat, barraCuda, coralReef, nestGate, rhizoCrypt, loamSpine, sweetGrass, squirrel, petalTongue, bingoCube, sourDough (pre-cascade).

---

## sourDough Code Team Work

### Atomic Model Correction (`3dd320a`)

The corrected atomic model from Wave 157k defines Tower Atomic as 4 primals (bearDog + songBird + skunkBat + swarmVine), not 3. NUCLEUS includes cellMembrane (16 primals total).

Changes to `sourdough-genomebin/src/service.rs`:
- `tower_atomic_templates()`: Added swarmVine (3 → 4 primals)
- `nucleus_templates()`: Added swarmVine to Tower position, added cellMembrane, removed swarmVine duplicate from meta position (15 → 16 primals)
- Tests: `tower_atomic_generates_three` → `tower_atomic_generates_four`, `nucleus_generates_fifteen` → `nucleus_generates_sixteen`
- Doc comments updated with composition formulas

All 114 tests + 5 doctests pass. Pushed to Forgejo.

---

## Darwin Binary Rebuild

5 primals rebuilt from current HEADs for `aarch64-apple-darwin`:

| Binary | Size | Source Commit | Build Status |
|--------|------|---------------|-------------|
| songbird | 17M | `090e8c2d` (Wave 157k deep-debt) | Clean |
| swarmvine | 2.1M | `63c8ccc` (Wave 157k evolution) | Clean |
| toadstool | 6.0M | `1640e7b9` (S380 doc sync) | Clean |
| biomeos | 16M | `56286c0a` (Wave 157k ack) | Clean |
| sourdough | 2.7M | `3dd320a` (atomic model fix) | Clean |

All 5 binaries deployed locally to `~/.local/bin/` + `/usr/local/bin/`.

---

## Depot Push

5 refreshed binaries pushed to golgiBody depot:

```
scp → root@[RELAY_PUBLIC]:/opt/ecoPrimals/plasmidBin/primals/aarch64-apple-darwin/
```

Depot now has 15 darwin binaries (104M total). 5 at Aug 12 19:16 (refreshed), 10 at Aug 12 13:21 (previous wave).

---

## NUCLEUS Redeploy

NUCLEUS restarted with `biomeos nucleus start --node-id graftGate --mode full`.

**New divergence**: biomeOS now requires `--node-id` flag (from songBird deep-debt `--node-id` resolution). Previous invocation without `--node-id` fails.

| Metric | Value |
|--------|-------|
| Primals launched | 12 (biomeOS-managed) + swarmVine (manual) |
| Capabilities | 1830 registered, 19 logical primals |
| Domains ACTIVE | 21 (same set as previous deployment) |
| Startup time | <60s |
| swarmVine | Running on port 7800, `endpoint.alive` injected |

### Known recurring divergences (from previous AAR, still present)

- **D5**: songBird ↔ bearDog BTSP federation handshake (plaintext fallback)
- **D6**: biomeOS `security` capability resurrection loop (`/usr/bin/security` vs skunkBat)
- **tarpc health-check**: toadStool, sweetGrass, skunkBat show RPC ping warnings (cosmetic — primals are healthy, biomeOS pings with JSON-RPC on tarpc sockets)

### New observation

- **D11**: biomeOS does not include swarmVine in its NUCLEUS primal list despite the corrected atomic model defining Tower Atomic as bearDog + songBird + skunkBat + swarmVine. swarmVine must be started manually as a separate process. biomeOS team should add swarmVine to the NUCLEUS bootstrap graph.

---

## State After Cascade

| Component | Status |
|-----------|--------|
| graftGate NUCLEUS | LIVE — 21 domains ACTIVE, 1830 capabilities |
| swarmVine | LIVE — port 7800, `endpoint.alive` injected |
| sourDough | `3dd320a` — atomic model corrected, pushed upstream |
| Darwin depot | Refreshed — 5/15 binaries at current HEADs |
| WireGuard | LIVE — `10.13.37.13` |

---

*graftGate — Wave 157k ortho sweep cascade. 5 primals rebuilt from fixed HEADs. Depot refreshed. NUCLEUS redeployed with `--node-id`. sourDough atomic model aligned (Tower=4, NUCLEUS=16). D11 filed: swarmVine missing from biomeOS NUCLEUS graph. 0/0/0.*
