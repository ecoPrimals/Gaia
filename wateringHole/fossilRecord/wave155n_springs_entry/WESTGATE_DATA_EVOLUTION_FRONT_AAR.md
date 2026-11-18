# AAR: Data Federation Evolution Front — Ad-Hoc to Primal Compositions

**Gate**: westGate
**Wave**: 155f
**Date**: Aug 3, 2026
**Author**: westGate overwatch team
**Scope**: Full review of data federation systems — what's ad-hoc, what's composable, what worked, what failed, what evolves upstream

---

## Executive Summary

westGate is the first gate with live data systems: 1+ TB across 130+ datasets
with real cryptographic provenance (DAG sessions, Merkle roots, Ed25519
signatures, attribution braids). This creates a new evolution front for the
ecoPrimals mesh — one where the patterns developed for data federation become
the patterns for inter-gate data serving, and eventually for federated
scientific collaboration across sovereign meshes.

The data federation campaign succeeded at the **storage and provenance layer**
but ran entirely through ad-hoc Python scripts that bypass biomeOS. The
architectural target — declarative DataManifests driving registered signal
graphs with governed `content.fetch` — is roughly half-built: schema and graph
TOMLs on one side, `content.fetch` handler on another, with the glue
(registration, governance runtime, script migration) still missing.

This AAR catalogs the gap, documents what worked and failed, and specifies
what needs to evolve upstream so the rest of the mesh can absorb and
disseminate what westGate has pioneered.

---

## 1. The Ad-Hoc / Composition Inventory

### What Runs Today (7 scripts, 0 signal dispatches)

Every byte of data on westGate was acquired through direct Python → UDS socket
calls. biomeOS was never involved in orchestration.

| Script | Role | Provenance | Governance | biomeOS |
|--------|------|-----------|------------|---------|
| `bulk_ingest.py` | Core provenance pipeline for local files | Full chain (fixed Wave 155f) | None | Bypassed |
| `manifest_download.py` | Manifest-driven curl + provenance | Full chain | Hardcoded rate | Bypassed |
| `revalidate_data.py` | Re-hash + re-provenance existing data | Full chain | None | Bypassed |
| `alphafold_bulk_download.py` | Async aiohttp for 214M structures | None | Concurrency cap | Bypassed |
| `alphafold_full_sync.sh` | rsync for AlphaFold proteomes | None | rsync bwlimit | Bypassed |
| `metered_download.sh` | Sequential rate-limited curl | None | 50 MB/s limit | Bypassed |
| `pdb_ingest.py` | Early PDB per-structure fetcher | Stubs | None | Bypassed |

### What's Specified (TOML exists, not wired to runtime)

| Artifact | Location | Status |
|----------|----------|--------|
| DataManifest schema | `wateringHole/schemas/data_manifest.toml` | Complete |
| 3 DataManifest files | `wateringHole/manifests/*.toml` | Complete |
| `nest.declare_dataset` signal graph | `biomeOS/graphs/signals/nest_declare_dataset.toml` | TOML complete, **not registered** |
| `nest.acquire_file` signal graph | `biomeOS/graphs/signals/nest_acquire_file.toml` | TOML complete, **not registered** |
| `nest.complete_dataset` signal graph | `biomeOS/graphs/signals/nest_complete_dataset.toml` | TOML complete, **not registered** |
| Bandwidth governance spec | `wateringHole/specs/BANDWIDTH_GOVERNANCE_SPEC.md` | Spec complete, **no runtime** |
| `topology.bandwidth.*` capability entries | `cellMembrane/config/capability_registry.toml` | Registered, **no implementation** |

### What's Landed in Primals (working, not integrated)

| Capability | Location | Status |
|------------|----------|--------|
| `content.fetch` UDS handler | `nestGate/code/.../content_handlers/fetch.rs` | Working handler, **not in signal graphs or scripts** |
| `nest.store/commit/retrieve/verify` | biomeOS signal_tools + capability_registry | Registered + dispatchable |
| `nest.sync/federate` | biomeOS signal_tools + capability_registry | Registered, untested at scale |
| `braid.partial_update/complete` | biomeOS signal_tools + capability_registry | Registered + tested |
| `content.replicate/replicate.pull` | nestGate capability_registry | Documented, untested at scale |

### The Gap

The scripts and the compositions share the same *logic* (BLAKE3 → CAS → DAG →
spine → dehydrate → sign → braid), but the scripts execute it via direct UDS
socket calls while the compositions define it as signal graphs. The bridge
(`manifest_download.py`) proves the pattern works but still bypasses biomeOS
dispatch. Closing this gap means:

1. Registering the 3 federation signal graphs so `signal.dispatch` can route them
2. Updating `nest_acquire_file` to use `content.fetch` instead of `content.put`
3. Implementing `topology.bandwidth.*` so governance is real, not hardcoded
4. Migrating scripts to call `signal.dispatch` instead of direct RPC

---

## 2. What Worked

### Proven Patterns

| Pattern | Evidence |
|---------|----------|
| Download-once, serve-at-10G economics | 1 TB acquired via 1 Gbps WAN; available to all gates at 10 Gbps LAN; zero egress cost |
| Provenance is free | BLAKE3 at 10-16 GB/s; the full 5-step chain adds <100ms per file |
| Manifest-first URL validation | Caught dozens of "200 OK returning HTML" before they polluted CAS |
| ZFS persistence | Data survived a hard reboot; pool re-imported in one command |
| L2ARC + raidz1 | Read cache accelerates hot data; raidz1 gives 50 TB usable with parity |
| Credential vault on golgiBody | GPG-encrypted bundle; any gate can recover API keys for re-acquisition |
| Trust tiers (T1/T2/T3) | Differentiates validated primary sources from derived data |
| rsync for bulk mirrors | PDB mmCIF (257K files), AlphaFold proteomes — resumable, idempotent |
| ENA over SRA Toolkit | Simpler, faster, more reliable for FASTQ retrieval |
| Systemd timers for persistence | AlphaFold sync survives reboots; runs daily at 03:00 |
| NCBI API key for rate limits | 3→10 req/s for Entrez; unlocked NF Data Portal via Synapse |
| Batch parallelism when metered | Large background + small foreground = good throughput without saturation |

### Revalidation Results

The revalidation campaign re-ingested all existing data through the real
provenance chain (replacing the stub `health.check` provenance from the
initial campaign):

- **130 datasets processed** (< 10 GB): 130/130 OK (100% pass rate)
- **1,314 DAG events** created with real `DataCreate` event types
- **130 braids** created with real session IDs and Merkle roots
- Large datasets (> 10 GB) processing in background: sra_fastq, alphafold_structures, pdb_mmcif

Every dataset now has a genuine Merkle root, not a stub. The provenance chain
is cryptographically verifiable end-to-end.

---

## 3. What Failed

### P0: Bandwidth Saturation

Six parallel unmetered downloads (curl, rsync, aiohttp) saturated the 1 Gbps
residential fiber, killing internet for all devices on the home network and
forcing a hard reboot of westGate.

**Root cause**: No bandwidth governance. Shell flags (`--limit-rate`,
`--bwlimit`) are per-process band-aids; there was no system-level budget.

**Fix required**: `topology.bandwidth.{budget,request,release,pressure}` as a
primal capability. The signal graphs already define `check_bandwidth` and
`release_bandwidth` nodes — they just need a runtime behind them.

**Broader lesson**: The same mechanism that prevents westGate from starving the
home network also prevents consumer gates from starving westGate during
`content.replicate.pull`. No gate can starve another. No operation can starve a
gate. The mesh self-regulates.

### P1: Not Using biomeOS

The entire data federation campaign bypassed biomeOS. This means:
- No signal graph routing (no audit trail of what composed what)
- No governance hooks (bandwidth, rate limits, backpressure)
- No self-healing (if a step fails, the script stops; no retry composition)
- No cross-gate awareness (other gates can't observe data acquisition in progress)

This is the single largest architectural debt from the campaign. The scripts
work, but they're jelly — they don't compose, they don't federate, and they
don't self-heal.

### P2: Cloudflare/Registration Walls

12 datasets blocked on human browser interaction: DepMap, HMDB, Bgee,
DisGeNET, EPA CompTox, EcoCyc, OMIM, DrugBank, PharmGKB, AmeriFlux,
Copernicus ERA5 license, Bgee. These are NEEDS-USER blockers, not engineering
blockers.

### P2: Silent URL Rot

Multiple sources returned 200 OK with HTML error pages instead of data. S3
buckets deleted, version paths rotated, FTP structures changed. The manifest
schema's `expected_hash` field is the fix — `content.fetch` already validates
this — but the ad-hoc scripts didn't always check Content-Type.

### P2: Cross-Gate Replication Untested

`content.replicate.pull` and `nest.sync` exist as RPC methods and signal
graphs but have never been validated at scale over the 10G trunk. The
`federation_test.py` harness exists but hasn't been run between real gates.

### P2: Socket Evaporation (biomeOS v4.50)

The biomeOS prune cycle can delete other primals' UDS sockets. This is a known
P2 bug that blocks native workflow adoption. Until fixed, scripts that bypass
biomeOS are actually more reliable — which creates a perverse incentive to
stay ad-hoc.

---

## 4. Data Tiering Architecture

### Hardware Storage Tiers (westGate)

| Tier | Hardware | Size | Role |
|------|----------|------|------|
| 0 | Ryzen 5700X L3 cache | 32 MB | CPU cache |
| 1 | DDR4 RAM / ZFS ARC | 64 GB | Hot read cache |
| 2 | Samsung 970 EVO NVMe | 2 TB | Active datasets, CAS hot tier |
| 3 | Crucial BX500 SSD (L2ARC) | 2 TB | ZFS read cache for cold data |
| 4 | 5x14TB HDD raidz1 | 50 TB | Bulk CAS, cold archive |

ZFS manages tiers 0-4 transparently via ARC/L2ARC. The evolution needed is at
the federation layer: knowing what to promote when a gate announces intent.

### Data Trust Tiers

| Tier | Policy | Examples |
|------|--------|----------|
| T1 Primary | Fetch, hash, consume directly | NCBI, PDB, UniProt, NOAA, PhysioNet |
| T2 Secondary | Revalidate against T1 before serving | ChEMBL, AlphaFold, TCGA |
| T3 Derived | Reproduction target only; not served proactively | Published figures, enrichments |

### LAN Serving Model

The 10G backbone connects westGate to every compute gate:

```
WAN (1 Gbps) → westGate → 10G trunk → CRS310 → {eastGate, northGate, biomeGate}
                                     → Omada  → {ironGate, southGate, strandGate}
```

When strandGate needs AlphaFold data for a pipeline:

1. `strandGate` dispatches `nest.declare_dataset` with manifest
2. biomeOS routes to westGate via songBird mesh
3. westGate checks `topology.bandwidth.budget` for egress capacity
4. westGate serves via `content.replicate.push` at 10 Gbps
5. strandGate verifies: `dag.verify` + `certificate.verify` + `braid.resolve`
6. Data available locally on strandGate — no further WAN traffic

The same pattern extends to WAN gates (flockGate) and future neighborhood
nodes — different bandwidth budgets, same trust verification chain.

---

## 5. Upstream Evolution Roadmap

### P0: Bandwidth Governance

| Deliverable | Owner | Description |
|-------------|-------|-------------|
| `topology.bandwidth.budget` | sporeGate topology | Current capacity and allocation |
| `topology.bandwidth.request` | sporeGate topology | Reserve bandwidth before transfers |
| `topology.bandwidth.release` | sporeGate topology | Return allocation when done |
| `topology.bandwidth.pressure` | sporeGate topology | Backpressure on latency/loss |

Recommended first implementation: Option A (cellMembrane CLI) from the
bandwidth governance spec.

### P1: Signal Graph Registration

| Deliverable | Owner | Description |
|-------------|-------|-------------|
| Register `nest.declare_dataset` | biomeOS team | Add to capability_registry + signal_tools |
| Register `nest.acquire_file` | biomeOS team | Add to capability_registry + signal_tools |
| Register `nest.complete_dataset` | biomeOS team | Add to capability_registry + signal_tools |

### P1: Wire `content.fetch` into Compositions

| Deliverable | Owner | Description |
|-------------|-------|-------------|
| Update `nest_acquire_file.toml` | biomeOS team | Add `content.fetch` node, keep `content.put` as fallback |
| `manifest_download.py` → `signal.dispatch` | westGate | Call biomeOS instead of direct RPC |

### P1: Cross-Gate Replication Test

| Deliverable | Owner | Description |
|-------------|-------|-------------|
| `federation_test.py` on LAN | westGate + strandGate | Validate replicate.pull at 10G |
| Scale to 10 GB subset | westGate + strandGate | Prove economics at meaningful data volume |

### P2: Remaining Gaps

| Deliverable | Owner |
|-------------|-------|
| Fix socket evaporation (v4.50 prune cycle) | biomeOS team |
| Data catalog query API (sweetGrass graph traversal) | sweetGrass team |
| Download queue service (rate limits, Content-Type validation, resume) | nestGate team |
| Auto-import ZFS pool on boot | sporeGate infra |

---

## 6. Conceptual: What If the Source Orgs Ran Nest Atomics?

The user asked: "what if the orgs we were getting this data from were also
running a nest atomic? And rather than storing PB of data on a cloud they have
a subset and the source data is federated?"

This is the endgame vision:

- EBI runs a nest atomic for AlphaFold. westGate doesn't download 15 TB of
  CIF files — it does `content.replicate.pull` against EBI's nestGate.
  Provenance transfers with the data (DAG session, Merkle root, braid).

- NCBI runs a nest atomic for GenBank. Updates are federated via DAG event
  append — new genome assemblies arrive as DAG deltas, not full re-downloads.

- Each org holds its source data; consumer gates hold validated subsets.
  No cloud stores petabytes. The source data is federated across sovereign
  meshes.

This is the same architecture that makes westGate → strandGate work at 10G,
just applied at internet scale. The DataManifest becomes the shared language:
"I want these CIDs. You have them. Let's negotiate bandwidth and transfer
with cryptographic provenance."

The shared braid tracks data movement across all gates — not just within the
LAN mesh but across organizations. This is the `nest.federate` signal graph
at its full expression.

---

## 7. Action Items

1. **Register 3 federation signal graphs** in biomeOS (smallest change, largest unlock)
2. **Wire `content.fetch`** into `nest_acquire_file.toml`
3. **Implement bandwidth governance** runtime (cellMembrane Option A)
4. **Run `federation_test.py`** across 10G trunk (westGate ↔ strandGate)
5. **Complete revalidation** of large datasets (sra_fastq, alphafold_structures, pdb_mmcif)
6. **Update DATA_FEDERATION_STATUS.md** with evolution front and tiering architecture
7. **File upstream** for socket evaporation fix and data catalog API

---

*westGate is a sovereign scientific data root serving 1 TB at 10 Gbps with
zero egress cost. The scripts that built it are jelly strings — they work but
they don't compose. The signal graphs that replace them are primal
compositions — they compose, they federate, and they self-heal. The evolution
from one to the other is the data federation evolution front, and westGate is
the first gate to explore it.*
