# westGate Wave 157e Overwatch Validation AAR

**Date**: Aug 10, 2026 | **Gate**: westGate | **Wave**: 157e
**Scope**: Cascade from Forgejo, overwatch validation, swarmVine ant colony analysis

---

## EXECUTIVE SUMMARY

eastGate overwatch position validated westGate's Wave 157e deployment. All 14/14
services alive. Provenance trio operational with Ed25519 signing (sign + verify +
tamper rejection all PASS). Convergence drain broken path fixed. Braiding state
reconciled — all 3 datasets fully braided (990,500 total files). swarmVine ant
colony pattern identified and documented for upstream dissemination.

---

## CASCADE RESULTS

Pulled 16 primals + 7 infra + 10 springs from `git.primals.eco`:

| Repo | Status | Notable |
|------|--------|---------|
| sporePrint | 14 files, 325 insertions | Stale counts fixed (16 primals, 145K tests) |
| wateringHole | 2 files | Blurb reshape + sporeGate auto-publish HEAD |
| 8 springs | New workloads | toadStool dispatch TOML pattern ecosystem-wide |

### New Spring Workloads (8 springs updated)

- `hotspring-sovereign-roundtrip.toml` — full WGSL→ISA→dispatch→readback
- `wetspring-real-ncbi-pipeline.toml` — real NCBI 16S sovereign pipeline
- `healthspring-population-pk-gpu.toml` — 10k+ virtual patient Monte Carlo
- `neuralspring-ml-validation.toml` — Anderson spectral + Evoformer
- `airspring-water-balance.toml`, `groundspring-geochemistry-validation.toml`,
  `ludospring-game-validation.toml`, `primalspring-native-workload.toml`

### Key Handoffs Arrived

- **strandGate Phase 1 AAR**: 7/7 alive, GEMM Phase 2 PASS, campaign 24/45
- **strandGate E2E Pipeline Needs**: ironGate NFT, sporePrint QCD page, petalTongue viz
- **swarmVine**: Windows port handoff, deep debt doc, vertebrate evolution

---

## OVERWATCH VALIDATION — 14/14 ALIVE

| Service | Health | Key Metric |
|---------|--------|------------|
| nestgate | ALIVE | `content.ingest` 0.6ms, 1 file |
| rhizocrypt | ALIVE | v0.14.17, riboCipher enforced |
| loamspine | ALIVE | Ephemeral (known limitation) |
| sweetgrass | ALIVE | 100 braids in store |
| beardog | ALIVE | v0.9.0, Ed25519 sign+verify PASS |
| songbird | ALIVE | 11 services registered, 1 mesh peer |
| toadstool | ALIVE | v0.2.0, 16 cores, 63 GB, dispatch PASS |
| barracuda | ALIVE | NVIDIA 0x2484 detected |
| coralreef | ALIVE | — |
| skunkbat | ALIVE | riboCipher enforced |
| swarmvine | ALIVE | tarpc UDS, TCP 7800, 13 FDs |
| squirrel | ALIVE | v0.1.0 |
| petaltongue | ALIVE | — |
| biomeOS | ALIVE | v4.57.0, 17 FDs, FD leak FIXED |

### Ed25519 Signing Roundtrip

| Test | Result |
|------|--------|
| Sign message | PASS (0.2ms) |
| Verify signature | PASS (`valid: true`) |
| Tamper rejection | PASS (modified message → `valid: false`) |
| Public key export | `MqN0UEU04VRTTB7r9V4V5hx7rvXdJIpRE0vnKSXu/Zk=` |

### toadStool Workload Dispatch

| Test | Result |
|------|--------|
| `toadstool.submit_workload` | PASS (0.3ms, status: Queued) |
| `toadstool.query_capabilities` | PASS (16 cores, 63 GB) |
| `health.check` | PASS (healthy, 0 active workloads) |

### Neural API Routing

| Test | Result |
|------|--------|
| `capability.resolve(content)` | PASS → nestgate (0.2ms) |
| biomeOS FD count | 17 FDs, 1.9h uptime — HEALTHY |

---

## BRAIDING STATE — FULLY RECONCILED

Initial check appeared to show 0/5 chunks braided — this was a schema mismatch
in the query (checking for `status == "done"` and `braid_id` fields that don't
exist in the state format). Actual state uses `completed_at` per chunk.

| Dataset | Chunks | Files | Braided | Marker |
|---------|--------|-------|---------|--------|
| alphafold | 7/7 | 324 | Aug 7, 2026 | `.braided` ✓ |
| alphafold_structures | 228/228 | 989,423 | Aug 7, 2026 | `.braided` ✓ |
| sra_fastq | 5/5 | 753 | Aug 7, 2026 | `.braided` ✓ |

100 braids in sweetGrass. Pen test 86/87 PASS confirmed.

---

## ISSUES FOUND & FIXED

### 1. Convergence Drain Path Broken

**Root cause**: Commit `b44b7115` (pepti-layer cleanup) moved `convergence_drain.py`
to `scripts/deprecated/`. Systemd service pointed to old path.

**Fix**: Updated `convergence-drain.service` `ExecStart` to `deprecated/` path.
Verified drain runs successfully — NVMe at 25.2%, below 60% high-water mark.

### 2. songBird Registration Service Failed

**Root cause**: `songbird-register.service` failed 1d 3h ago (reason unclear,
journal rotated). Registrations were stale.

**Fix**: Manual re-run of `songbird-register.sh` — all 5 provenance primals
confirmed registered ("already registered" for all).

### 3. swarmVine Gossip Peers Unreachable

**Root cause**: `SWARMVINE_PEERS=sporeGate@192.168.4.159:7800,ironGate@192.168.4.213:7800`
— neither gate is running swarmVine on TCP 7800 from westGate's perspective.

**Impact**: Cross-gate gossip blocked. Local service healthy (13 FDs, 2h uptime).
tarpc "Requests stream errored out" warnings every 30s (matching `--spread-interval`).

**Next step**: songBird mesh relay implementation or LAN topology verification.

### 4. swarmVine UDS Uses tarpc (Not JSON-RPC)

**Finding**: swarmVine creates two sockets:
- `.sock` in `/run/user/1000/biomeos/` — tarpc transport
- `.tarpc.sock` in `/run/user/1000/membrane/` — also tarpc

Both sockets use tarpc binary protocol, not JSON-RPC. This means biomeOS Neural
API cannot route to swarmVine via `capability.call`. Only the TCP gossip port
uses JSON-RPC (with riboCipher prefix).

---

## STORAGE STATUS

| Tier | Used | Available | Health |
|------|------|-----------|--------|
| NVMe (root) | 461G / 1.8T (27%) | 1.3T | Healthy |
| ZFS nestgate pool | 5.25T / 50.75T | 45.5T | Healthy |
| ZFS CAS | 1.41T | — | Healthy |
| ZFS data | 3.84T | — | Healthy |
| Convergence drain | Timer active | 25.2% (below 60% HW) | Fixed ✓ |

---

## SWARMVINE ANT COLONY PATTERN

Full analysis written to `whitePaper/subGen/SWARMVINE_ANT_COLONY_NUCLEUS_ATOMICS.md`.

Key insight: swarmVine is an ant colony — small, quiet, epidemic gossip with
TTL evaporation, three pheromone types (Tower/Data/Compute), vine-bat immune
system, and nonce dedup. The core nervous system is clean. What's missing:
**scouts** (no primal currently injects gossip) and **more trail surfaces**
(only TCP, no songBird relay).

The NUCLEUS atomic model maps primals to three compositions:
- **Tower Atomic** (electron/communication): songBird, swarmVine, skunkBat, cellMembrane
- **Node Atomic** (proton/compute): toadStool, barraCuda, coralReef
- **Nest Atomic** (neutron/data): nestGate, rhizoCrypt, loamSpine, sweetGrass, bearDog
- **Interaction layer**: petalTongue (photon/visualization), squirrel (observer/AI),
  biomeOS (Hamiltonian/dispatch)

---

## RECOMMENDATIONS FOR OVERWATCH DISSEMINATION

1. **Immediate**: All primal teams should review the ant colony pattern and
   identify which events their primal should inject as gossip entries.

2. **Tower team**: songBird mesh relay for `MeshRelay` transport variant —
   enables swarmVine gossip through existing `:7700` mesh when TCP fails.

3. **swarmVine team**: Add JSON-RPC adapter on UDS socket so biomeOS Neural
   API can route gossip queries via `capability.call`.

4. **All gates**: Deploy swarmVine on remaining Phase 2 gates (blueGate,
   southGate, ironGate) so the gossip mesh has peers.

5. **strandGate**: Ed25519 signing ceremony is ready — westGate's bearDog
   validated sign + verify + tamper rejection. Public key exported for
   pseudoSpore manifest signing.

---

*westGate Wave 157e overwatch validation complete. 14/14 alive. Provenance chain
operational. Ant colony pattern identified. NUCLEUS atomic model documented.
Ready for dissemination.*
