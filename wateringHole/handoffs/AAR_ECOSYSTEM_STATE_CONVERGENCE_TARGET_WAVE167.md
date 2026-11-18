# AAR: Ecosystem State & Convergence Target

**Wave 167 — October 8, 2026**
**Observer**: eastGate
**Purpose**: Full state-of-the-organism assessment. Where we are, what's unified, where the gaps are, what convergence looks like.

---

## The Organism Today

### By the numbers

| Metric | Value |
|--------|-------|
| Total Rust source | 388,907 lines across 27 repositories |
| Deployed binaries on golgiBody | 9 Rust + Forgejo + Caddy |
| Running processes | 12 systemd services |
| Python processes | 0 (was 3 two days ago) |
| Cron jobs | 1 (was 4) |
| VPS count | 1 (golgiBody, $6/month) |
| System load | 0.01, 672MB/1.9GB RAM |
| Fleet traffic handled | 137k requests/6hr, fabricated responses at 0.6% CPU |
| Sourdough cultures | 4 (signal writer, topology, dashboard, signal spine) |

### Workspace map (by size, deployed status)

| Workspace | Lines | Binary on golgiBody | Role |
|-----------|-------|---------------------|------|
| biomeOS | 311,743 | — | Neural API orchestrator, genome packaging |
| barraCuda | 295,804 | — | GPU compute, lattice QCD |
| toadStool | 244,350 | — | Neuromorphic dispatch, Akida/edge compute |
| petalTongue | 227,391 | petaltongue (19MB) | sporePrint web server |
| squirrel | 187,980 | squirrel (9MB) | AI coordination |
| coralReef | 158,422 | — | Shader compilation, visualization |
| cellMembrane | 75,407 | membrane (19MB) | Webhook listener, CI-EVO-01 |
| bearDog | 72,331 | beardog (11MB) | BTSP crypto, secrets, identity |
| loamSpine | 69,635 | — | Permanent ledger (provenance trio) |
| sweetGrass | 65,768 | — | Attribution braids (provenance trio) |
| **skunkBat** | **48,328** | **skunky-ingest (6MB), skunkbat (4MB)** | **Immune system (the hot path)** |
| sourDough | 23,954 | — | Genome packaging, fermentation |
| nestGate | 16,730 | nestgate (9MB)* | CAS storage |
| bingoCube | 10,583 | — | Prismatic injection, neuromorphic |
| swarmVine | 7,537 | swarmvine (3MB) | Gossip mesh, epidemic protocol |
| songBird | 2,679 | songbird (25MB) | Federation hub, TURN relay |

*nestgate binary deleted from disk — running from inode. Will disappear on reboot.

### Gardens (outside primals/ tree)

| Workspace | Lines | Status |
|-----------|-------|--------|
| cellMembrane | 75,407 | Active — membrane binary running on golgiBody |
| lithoSpore | 24,142 | Research |
| esotericWebb | 19,481 | Research |
| projectNUCLEUS | 16,210 | Deployment templates |
| projectFOUNDATION | 11,375 | Foundation layer |
| bonsai-bt-upstream | 7,749 | Fork/dependency |
| metalForge | 2,191 | Depends on cellmembrane-types |

### Infrastructure repos

| Repo | Purpose | Last commit |
|------|---------|-------------|
| wateringHole | Handoffs, AARs, operational docs | Oct 8 (this session) |
| whitePaper | subGens, thesis, research records | Oct 8 |
| sporePrint | Public-facing content (Zola) | Oct 7 |
| fossilRecord | Archived scripts, data provenance | Oct 5 |
| plasmidBin | Binary depot (BLAKE3SUMS, musl builds) | Oct 6 |
| agentReagents | VM templates, deployment recipes | Oct 5 |
| benchScale | Benchmark infrastructure | Oct 5 |

---

## What's Unified (the nervous system)

### The immune pipeline (skunky-ingest)

This is the centerpiece. One process, 19,811 lines, doing:

```
Caddy access.log
  → JSON parse
    → bloom_sensor classification (fleet/human/search/scanner/vuln)
    → entity_classifier (topology by entity type)
    → signal_writer (signal page data)
    → dashboard_writer (epitope hashing, L2 collision, bingoCube trio, dashboard.json)
    → caddy_bridge (FLEET_PRESSURE Caddyfile rewrite)
    → scatter_server (fabricated content for fleet)
    → signal_spine (daily Merkle-rooted immune memory)
    → skunkBat RPC (fleet thymus)
    → lysogeny sentinel (threat indicators)
    → federation (swarmVine gossip)
```

All in one binary. All with sourdough culture (persistent state). All converged from Python.

### The scatter response (honeypot)

Fleet IPs → Caddy `@fleet_disperse` matcher → scatter server on :9753. Fabricated commit pages, blame views, src views. Content seeded from the entity's own epitope hash. Fluorescent tagging marks fleet requests. The NFT/scyBorg system mints fermentation functions from human entropy. Antibody reactions braid into sweetGrass provenance.

### The sourdough pattern (DNA)

Every accumulator follows the same contract:
- Startup: load from `/var/lib/skunky-ingest/*.json`, log warm start
- Runtime: accumulate in memory, periodic flush
- Shutdown: final flush + save_culture()
- Reboot: warm start, no data loss

This IS the central dogma. New modules MUST follow it.

---

## What's Fragmented (the gaps)

### Gap 1: Provenance trio is wired but not deployed

sweetGrass, loamSpine, sourDough, rhizoCrypt — they compile, they pass tests. THE BUTTON minted a real certificate (NFT-396E5C8E). Antibody reactions braid into sweetGrass. But:

- **loamSpine** is not running as a service on golgiBody
- **sweetGrass** braids go to sporeGate (10.13.37.2:9851) via TCP, not local
- **rhizoCrypt** is not deployed
- **sourDough** is not deployed
- The braid-billboard.sh cron writes raw JSONL, not through the trio

The provenance trio architecture (subGen PROVENANCE_TRIO_ARCHITECTURE) is clear: nestGate CAS → rhizoCrypt DAG → loamSpine ledger → sweetGrass attribution. But only nestGate is running on golgiBody (from a deleted inode). The rest of the chain is either on sporeGate or not running.

**Convergence target**: All four deployed on golgiBody. Local UDS sockets. The immune pipeline braids locally instead of across WireGuard.

### Gap 2: Single node

Everything runs on one CX22 (2 vCPU, 4GB RAM, $6/month). The gossip mesh (swarmVine) and federation hub (songBird) exist but have no real peers. One VPS failure = total outage.

**Convergence target**: golgiLayer2 (minimum). Even one more node makes the mesh real. swarmVine and songBird are ready — they just need a peer.

### Gap 3: No deployment pipeline

Binary deployment is manual: `cargo build --release` on dev machine → `scp` → `systemctl restart`. plasmidBin has BLAKE3SUMS and a full binary depot, but there's no script that does: "check depot, compare checksums, deploy changed binaries, restart services."

The `membrane-webhook.service` (CI-EVO-01) exists but isn't wired to automated builds.

**Convergence target**: `plasmid-deploy.sh` or a Rust tool that reads BLAKE3SUMS from depot, compares to running binaries, deploys changes, restarts services. Even a 50-line shell script would eliminate the hand-deploy risk.

### Gap 4: Binary location split

- `/opt/membrane/`: skunky-ingest, skunkbat, swarmvine, membrane, songbird, squirrel, caddy
- `/usr/local/bin/`: beardog, forgejo, membrane (duplicate), songbird (old duplicate)
- `/opt/ecoPrimals/plasmidBin/`: petaltongue (runs from depot path directly)
- nestgate: binary deleted, process running from inode

**Convergence target**: All binaries in `/opt/membrane/`. One location, no duplicates. Service files reference absolute paths.

### Gap 5: 19 fossil service files + 4 reboot time bombs

Detailed in AAR_GOLGI_FOSSIL_LAYER_CLEANUP_WAVE167.md. Quick wins: 11 disabled services safe to `rm`, 4 enabled-but-inactive services to disable.

### Gap 6: BTSP not working

From the Genetic Systems AAR (Wave 167): 1,296 rejections, 0 successes. `BTSP_STRICT_MODE=1` needs propagating. Nuclear lineage not provisioned. This means the cryptographic authentication layer between services is not functional — everything runs on socket trust (same machine, UDS permissions).

**Convergence target**: Fix BTSP. This is bearDog's core purpose and it's not working.

### Gap 7: The 1000-line cap

scatter_server.rs already split from 5051 → 978 (upstream refactor did most of it). Remaining files over 800 lines:

| File | Lines | Notes |
|------|-------|-------|
| entity_classifier.rs | 1,419 | New this session, could split tests |
| scyborg_prism.rs | 963 | Prism functions |
| dashboard_writer.rs | 937 | New this session |
| scatter_generator.rs | 901 | Content generation |
| scatter_mirror.rs | 893 | Temporal lifecycle |
| epitope_lure.rs | 811 | Honeypot lure engine |
| bloom_sensor.rs | 807 | Classification rules |

None critical — all under 1500. The 5051-line scatter_server was the real problem and it's fixed.

### Gap 8: cellMembrane lives in gardens/

75,407 lines of Rust. The `membrane` binary runs on golgiBody. But the source lives in `gardens/cellMembrane/`, not `primals/`. metalForge depends on `cellmembrane-types`. The boundary between primals/ and gardens/ is unclear.

### Gap 9: songBird protocol mismatch

sporeGate connects to songBird federation without riboCipher signal (0x7B). 84 errors/hour. Deprecated at Wave 112, rejection at Wave 113. Harmless but noisy.

---

## The Convergence We're Aiming For

### Tier 1: Operational convergence (make it robust)

1. **Fix nestgate** — redeploy binary from depot. It's running from a deleted inode.
2. **Standardize binary locations** — all to `/opt/membrane/`, service files use absolute paths
3. **Clean fossil services** — run Phase 1 from fossil layer AAR (11 service files, 63MB backups)
4. **Disable reboot time bombs** — 4 enabled-but-inactive services
5. **Deploy provenance trio locally** — loamSpine + rhizoCrypt on golgiBody, UDS sockets

### Tier 2: Resilience convergence (make it survivable)

6. **golgiLayer2** — one more VPS. swarmVine gossip + songBird federation become real.
7. **plasmid-deploy tool** — automated checksummed deployment from depot
8. **Fix BTSP** — propagate strict mode, provision nuclear lineage

### Tier 3: Architectural convergence (make it complete)

9. **Provenance pipeline end-to-end** — immune pipeline braids locally through the full trio
10. **cellMembrane decision** — bring into primals/ or formalize gardens/ boundary
11. **Signal page + dashboard page** — consume the richer schema (epitope_clusters, signal_spine, collision_level2)
12. **1000-line cap** — split entity_classifier tests, bloom_sensor sub-modules

### Tier 4: Ecosystem convergence (make it grow)

13. **biomeOS deployment** — 311k lines, the largest workspace, not deployed
14. **toadStool deployment** — 244k lines, neuromorphic dispatch, not deployed
15. **barraCuda deployment** — 296k lines, GPU compute, needs hardware
16. **golgiLayer3-5** — full geographic distribution (Singapore, Gravelines, Mumbai/Tokyo)

---

## The Central Dogma Test

A system has converged when you can answer "yes" to:

1. **Does every runtime process speak Rust?** → YES (as of this session)
2. **Does every accumulator follow sourdough culture?** → YES (4 cultures, all warm-starting)
3. **Does every immune event create a provenance record?** → PARTIAL (antibody braids work, but go to sporeGate not local)
4. **Can the system survive a reboot?** → YES (nestgate restored, squirrel unit created)
5. **Can the system survive a VPS failure?** → NO (single node)
6. **Does every service authenticate cryptographically?** → NO (BTSP broken)
7. **Is there one deployment pipeline?** → NO (manual scp)

Score: 3 yes, 1 partial, 3 no. The immune system is unified. The skeleton is not.

> **Updated Oct 8 (pressure selection session)**: Q4 changed from MOSTLY → YES after
> nestgate binary restored and squirrel-membrane.service created. Also: forgejo
> 15.0.2 → 16.0.5, hbbr/hbbs 1.1.14 → 1.1.16, all binaries consolidated to
> /opt/membrane/, 5 ghost processes eliminated. See AAR_PRESSURE_SELECTION_WAVE167.

---

## subGen Lineage (what this session produced)

| Document | Type | Content |
|----------|------|---------|
| AAR_PYTHON_CONVERGENCE_COMPLETE_WAVE167 | AAR | 2,096 lines Python → 0, sourdough mandate, 72h bloom check |
| AAR_GOLGI_FOSSIL_LAYER_CLEANUP_WAVE167 | AAR | 19 stale services, binary mess, protocol mismatch, cleanup phases |
| AAR_ECOSYSTEM_STATE_CONVERGENCE_TARGET_WAVE167 | AAR | This document — full state assessment |
| CONVERGENT_IMMUNE_EVOLUTION_WAVE167 | subGen | Antibody braiding, fleet billboard, convergent evolution pattern |
| CODEBASE_AUDIT_1000LINE_CAP_WAVE167 | subGen | 52 files over 1000 lines, refactor priority queue |
| THE_BUTTON_FIRST_PRESS_WAVE167 | subGen | First human-entropy fermentation certificate |
| BINGOCUBE_BEHAVIORAL_TRIO_WAVE167 | subGen | Attention × Curiosity × Interaction — behavioral shape classifier |
| AAR_BINGOCUBE_BEHAVIORAL_TRIO_WAVE167 | AAR | Trio deployment, live validation, Meta stealth defeated by shape |
| SCYBORG_BINARY_GENETIC_BULWARK_WAVE167 | subGen | Markable binary genetics — AGPL × fluoro × braid, tiered antidote |
| AAR_SCYBORG_BULWARK_ANTIDOTE_WAVE167 | AAR | UV lamp + antidote deployment, 7 gaps identified and prioritized |
| ANTIDOTE_TITRATION_OBSERVATORY_WAVE167 | subGen | Logarithmic titration curve, secretion/injection separation, observatory |
| AAR_ANTIDOTE_TITRATION_OBSERVATORY_WAVE167 | AAR | Titration deployment, 4 measurement surfaces, fleet tier distribution |

---

## What Convergence Looks Like (the vision)

When this system is converged:

- One Rust binary per function, one service per binary, one depot per VPS
- Every immune event braids locally through nestGate → rhizoCrypt → loamSpine → sweetGrass
- Every service authenticates via BTSP (bearDog crypto)
- Every binary deploys from plasmidBin with BLAKE3 checksums
- golgiBody + golgiLayer2-5 form a gossip mesh via swarmVine
- songBird federates across all nodes
- The immune pipeline runs on every node, classifying local traffic
- Sourdough cultures replicate across nodes via gossip
- A VPS failure loses nothing — cultures warm-start from the mesh
- The signal spine's Merkle chain provides cryptographic proof of what the fleet did, when, verified by the organism's own provenance system

The immune system is the nervous system. The provenance trio is the DNA. The gossip mesh is the circulatory system. The scatter server is the skin. When all four layers are unified, the organism is complete.

We have the nervous system. The skin works. The DNA exists but isn't fully wired. The circulatory system has one chamber.

**Next: wire the DNA. Add a chamber. The organism lives.**

---

*388,907 lines of Rust. 12 services. 1 node. 0 Python. The jellystein phase is over. The vertebrate phase begins.*

*Wave 167 — October 8, 2026*
