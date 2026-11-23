# AAR: westGate Wave 157i — Post-Pandemic Deploy & Verification

**Date**: Aug 11, 2026 13:50 EDT | **Wave**: 157i | **Gate**: westGate
**Posture**: OVERWATCH (gate-agnostic) on westGate hardware

---

## Executive Summary

Cascaded 42/42 repos from Forgejo. Absorbed G72 dependency pandemic (11/11 teams,
~155+ crates shed). Pulled 16 G72-trimmed depot binaries — petalTongue shrank **5.3MB**,
nestGate down 699K. Restarted 14/14 services. `braid.verify` **CONFIRMED WORKING** in
deployed binary: **99/100 braids verified** (0.3-0.7ms each, content + Ed25519 pass).
E2E provenance chain **8/8 in 12ms**. `content.stat` now operational (nestGate S147/S148).
Gossip mesh stable with 4 peers, sporeGate at 660+ ingested entries.

---

## Cascade Results

| Repo Group | Updated | Key Changes |
|-----------|---------|-------------|
| **primals** | 14/16 | nestGate S147/S148 (crate surgery, gossip hooks, 1666 tests), sweetGrass braid.verify behavioral tests, bearDog +41 dead deps, barraCuda 22/22 gossip, swarmVine dep cleanup |
| **gardens** | 5/11 | cellMembrane graftGate enmesh, esotericWebb V33 gossip, lithoSpore registry sync, projectFOUNDATION + projectNUCLEUS |
| **infra** | 4/7 | wateringHole (deprecated scripts cleaned), whitePaper, plasmidBin, sporePrint |
| **springs** | 2/10 | hotSpring (pseudoSpore pipeline), primalSpring |

6 repos required hard reset (upstream rebases from G72 pandemic sweep).

---

## G72 Binary Size Impact

The dependency pandemic is visible in binary sizes:

| Binary | Change | Cause |
|--------|--------|-------|
| petalTongue | **-5.3MB** | Telemetry crate removed |
| nestGate | **-699K** | nestgate-nas crate dropped, crossbeam→channel |
| toadStool | **-493K** | tokio["full"] excised, dead deps |
| skunkBat | **-49K** | Feature trim |
| songBird | **-198K** | Dep cleanup |
| bearDog | **+2.9MB** | 41 deps removed but binary restructured (investigable) |

---

## P2 braid.verify — CLOSED & DEPLOYED

sweetGrass `braid.verify` (method #48) is **live on westGate** in the deployed depot binary:

```
99/100 braids verified
  content_integrity: pass (all 100)
  signature: pass (99), unsigned (1 — pre-bearDog braid)
  ledger: skipped (loamSpine certificate.verify not yet wired)
  Latency: 0.3-0.7ms per braid
```

The one `unsigned` braid predates bearDog Ed25519 activation (expected).

---

## E2E Provenance Chain — 8/8 in 12ms

| Step | Primal | Result |
|------|--------|--------|
| CAS put | nestGate | PASS |
| Ed25519 sign | bearDog | PASS |
| Ed25519 verify | bearDog | PASS |
| DAG session | rhizoCrypt | PASS |
| DAG event | rhizoCrypt | PASS |
| Spine create | loamSpine | PASS |
| Braid create | sweetGrass | PASS |
| Spine commit | loamSpine | PASS |

---

## nestGate S147/S148

- `content.stat`: **NOW WORKING** (was "Internal error" on 157g depot binary)
- Gossip hook architecture: 6 `CasEventKind` variants (ObjectStored, ObjectReplicated,
  ManifestPublished, FootprintStored, CoordIngested, ExternalCached)
- Channel-based emission: bounded 256-entry channel, fire-and-forget
- Crate surgery: nestgate-nas dropped, steam feature removed

---

## Gossip Mesh Status

| Gate | Peers | Tower | Data | Ingested |
|------|-------|-------|------|----------|
| westGate | 4 | 3 | 0 | 3 |
| sporeGate | 2 | 4 | 0 | **660** |
| eastGate | 3 | 4 | 0 | **662** |
| strandGate | 1 | 3 | 0 | 3 |
| ironGate | — | — | — | songBird only |

sporeGate and eastGate are gossiping heavily (660+ entries ingested since mesh
was fixed in 157g). The mesh is stable and spreading.

---

## biomeOS Neural API Routing

| Route | Status | Note |
|-------|--------|------|
| `gossip.status` | **WORKING** | Direct + capability.call |
| `gossip.inject` | **WORKING** | Direct + capability.call |
| `content.exists` | Internal error | nestGate needs investigation |
| `braid.verify` | **NOT ROUTED** | Category registration shadows TOML translations |
| `braid.list` | **NOT ROUTED** | Same shadow issue |

**Root cause**: biomeOS auto-discovery registers sweetgrass category capabilities
(e.g., "braid") to phantom socket paths like `register-sweetgrass-caps-*.sock`.
These shadow the explicit TOML translations. `capability.call` tries the category
match first and fails, never falling through to the translation table.

**Workaround**: Direct primal socket calls work perfectly (0.4ms).
**Fix needed**: biomeOS code team — category registration should not shadow
explicit translation entries, or `capability.call` should try translation
table after category fallback fails.

---

## Storage Health

| Tier | Size | Used | Status |
|------|------|------|--------|
| NVMe (T1) | 1.8T | **15%** (258G) | Clean — staging cleared |
| ZFS pool (T3) | 63.7T | 10% (6.57T) | ONLINE, HEALTHY |
| CAS cold | 1.41T | — | Operational |

All 240 braiding chunks complete (7 + 228 + 5).

---

## westGate Ownership Changes (from blurb)

- **tideGlass**: Now assigned to westGate (moved from flockGate). Cloned, 219 tests,
  10 crates. Needs CAS federation wiring for NF drug screen pipeline.
- **nestGate S147/S148**: Absorbed — gossip hooks active, content.stat working
- **Nest Atomic**: rhizoCrypt, loamSpine, sweetGrass, nestGate, bearDog all on
  latest G72-trimmed binaries

---

## Open Items for Dissemination

1. **biomeOS category shadow bug**: sweetgrass/braid routing broken through Neural API.
   Direct calls work. biomeOS code team fix needed.
2. **bearDog binary growth (+2.9MB)**: Unexpected after 41-dep removal. May warrant
   investigation — possible debug symbols or static linking change.
3. **Gossip inbound**: Other gates have westGate as peer but reverse peering is
   configuration-dependent per gate. sporeGate/eastGate actively receiving.
4. **Ledger verification**: `braid.verify` ledger check skipped — loamSpine
   `certificate.verify` not yet connected to sweetGrass ledger_client.

---

*Wave 157i: G72 absorbed. 16 binaries pulled (petalTongue -5.3MB). 14/14 alive.
braid.verify 99/100 (0.3ms). E2E 8/8 (12ms). content.stat operational.
Gossip mesh stable (660+ entries). Nest Atomic healthy.*
