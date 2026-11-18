# westGate-CAS Data Handling Plan — Wave 157j

**Date**: August 12, 2026
**Wave**: 157j
**From**: westGate-CAS team
**To**: wetSpring, projectFOUNDATION, upstream spring/garden teams reassembling
**Posture**: PLAN — near-term data handling + serving roadmap

---

## Team Topology

westGate-CAS is the colocated owner of data handling and serving infrastructure.
wetSpring and projectFOUNDATION are colocated and operate on the same hardware
(westGate tower) with direct local socket access to the full primal stack.

```
┌───────────────────────────────────────────────────┐
│                  westGate Tower                    │
│                                                   │
│  ┌─────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │wetSpring │  │projectFOUND. │  │westGate-CAS  │ │
│  │ (science │  │ (validation  │  │ (data infra  │ │
│  │  + data) │  │  + publish)  │  │  + serving)  │ │
│  └────┬─────┘  └──────┬───────┘  └──────┬───────┘ │
│       │               │                │          │
│       └───────────────┼────────────────┘          │
│                       │                           │
│              biomeOS Neural API                   │
│         (local UDS, no mesh required)             │
│                       │                           │
│  ┌────────────────────┼──────────────────────┐    │
│  │           Nest Atomic (6 domains)          │   │
│  │  bearDog · songBird · nestGate             │   │
│  │  rhizoCrypt · loamSpine · sweetGrass       │   │
│  └────────────────────┬──────────────────────┘    │
│                       │                           │
│              ZFS Pool (50.7 TB)                   │
│           3.21 TB used · 153 datasets             │
│           452 GB CAS · 5800 objects               │
└───────────────────────┼───────────────────────────┘
                        │
            songBird mesh + relay
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
   nestgate.io      sporeGate       other gates
   (peti layer)     (petalTongue)   (federation)
```

---

## What Changed (Wave 157j — Prerequisite Work)

All of this is committed and pushed:

| Item | Status | Impact |
|------|--------|--------|
| Nest Atomic Neural API | LIVE | `nest.health`, `nest.capabilities` — 6-domain independent health |
| riboCipher transport fix | LIVE | sweetGrass attribution methods route correctly through `[0xEC, 0x01]` |
| 139 translation routes | LIVE | Full capability surface for all 6 Nest domains |
| Glue deprecation markers | DONE | 9 scripts marked with Rust/Neural API replacement paths |
| hotSpring thin-layer absorbed | DONE | Composition follows domain-based, capability-resolved architecture |

**biomeOS**: `1473737d` on Forgejo.
**wateringHole**: `463bfe796` on Forgejo.

---

## Track 1: Local Data Handling (wetSpring)

### Current State

wetSpring is a **composition-only science consumer** — no direct HTTP or file I/O for
external data. All data flows through primal IPC:

```
wetSpring IPC (data.fetch.*)
  → biomeOS Neural API (capability.call)
    → nestGate storage.fetch_external (TLS + BLAKE3)
    → fallback: nestGate storage.retrieve (cache hit)
  → Provenance Trio (DAG → spine → braid)
  → gossip DataIngested event
```

IPC data methods already implemented: `data.fetch.chembl`, `data.fetch.pubchem`,
`data.fetch.register_table`, `science.ncbi_fetch`.

### Near-Term Work

| Task | Surface | Owner |
|------|---------|-------|
| Wire wetSpring to Nest Atomic directly | `nest.store`, `nest.retrieve`, `nest.commit` | westGate-CAS |
| Local-first data fetch without mesh | UDS → nestGate `content.put` / `content.get` | wetSpring |
| Streaming parsers for new formats | `io::fastq`, `io::mzml` already exist; add as needed | wetSpring |
| Provenance at ingress (not trailer) | `content.ingest → dag.session → braid.create` | westGate-CAS |
| Gap reporting for missing primals | Already implemented — `gap_report` on missing capabilities | wetSpring |
| NVMe staging for hot data | NVMe → CAS on ZFS, cold to HDD | westGate-CAS |

### Parallel IDE Mode

wetSpring operates as a **parallel IDE** on the same tower. This means:

- Same UDS sockets as westGate-CAS (no network hop)
- Same ZFS pool for CAS reads/writes
- Same primal instances (bearDog, nestGate, rhizoCrypt, etc.)
- Independent validation and experiment runs
- Gossip events visible to all local consumers

No special federation needed — local socket routing handles everything.

---

## Track 2: Data Serving (nestgate.io PETI Layer)

### Architecture

nestgate.io is the **peptidoglycan trust surface** — the public-facing data and
provenance layer between the internal mesh (`primal.eco`) and the public site
(`primals.eco`).

```
External request
  → nestgate.io (Caddy TLS)
    → petalTongue (Axum web server on sporeGate)
      → nestGate (CAS backend via UDS/JSON-RPC)
      → songBird (federation / content.locate)
      → sweetGrass (braid.verify for provenance)
```

### Current Capabilities (Phase 1-2 — LIVE)

| Route | Purpose | Status |
|-------|---------|--------|
| `/api/content/stats` | CAS statistics via rhizoCrypt | LIVE |
| `/api/content/federation` | Federated data braids | LIVE |
| `/api/pseudospore/bundles` | pseudoSpore serving | LIVE |
| `/api/primals` | Discovery | LIVE |
| `/api/gate-mesh` | Mesh topology | LIVE |
| `/depot/` | Binary depot browser | ACTIVE |
| `/provenance/` | Provenance browser | ACTIVE |
| `/ws` | WebSocket JSON-RPC bridge | LIVE |

### Near-Term Work (Phase 3)

| Task | Surface | Owner |
|------|---------|-------|
| `/cas/{hash}` content retrieval | nestGate `content.get` via petalTongue | westGate-CAS |
| `/cas/{hash}/provenance` | sweetGrass `braid.get` + `braid.verify` | westGate-CAS |
| Content-addressed retrieval for external consumers | HTTP GET → BLAKE3 hash → raw bytes | westGate-CAS |
| Cross-gate CAS federation | songBird `content.locate` → `content.replicate.pull` | westGate-CAS |
| Dataset convergence dashboard | `dataset.convergence` scanning | projectFOUNDATION |
| Public provenance verification API | `braid.verify` over HTTP (riboCipher-aware) | westGate-CAS |

### Federation Path

```
External → nestgate.io/cas/{hash}
  → petalTongue: local nestGate content.exists?
    → YES: serve from local CAS
    → NO: songBird content.locate (mesh query)
      → found on westGate/sporeGate/etc: content.replicate.pull
      → serve from local CAS after replication
```

projectFOUNDATION already has this federation client in
`foundation-ipc/src/federation.rs`.

---

## Track 3: Mesh Integration

### Current Mesh State

- 4-5 gate gossip mesh (westGate, sporeGate, eastGate, southGate, strandGate)
- songBird relay operational for cross-gate capability routing
- swarmVine gossip 662+ ingested entries on eastGate
- MeshRelay via `mesh.relay` confirmed compatible

### Near-Term Mesh Work

| Task | Owner |
|------|-------|
| CAS content replication across gates | westGate-CAS |
| Cross-gate `braid.verify` routing | westGate-CAS |
| Mesh-aware `nest.health` (reports per-gate domain status) | westGate-CAS |
| Federation serving through nestgate.io | westGate-CAS |
| bearDog riboCipher for mesh authentication | westGate-CAS |

---

## Track 4: Replace native_braid.py (Last Python Glue)

**Current**: 1,308-line Python script doing the full braid pipeline via socat subprocess.

**Target**: Rust-native `membrane content.braid` wrapping biomeOS graph composition:

```
content.ingest
  → dag.session.create
  → dag.event.append_batch
  → dag.dehydration.trigger
  → crypto.sign
  → session.commit
  → braid.create
  → gossip.inject
```

Or a biomeOS signal graph: `data_braid_ingress.toml`.

This unblocks all data handling from Python subprocess overhead (current: 145/s convoy,
target: native socket speed — nestGate alone handles 16K RPCs/s).

---

## Data Inventory (westGate)

| Metric | Value |
|--------|-------|
| ZFS pool | 50.7 TB (6.3% used) |
| Total data | 3.21 TB |
| Datasets | 153 |
| CAS pool | 452 GB |
| CAS objects | 5,800 |
| Convergence | 0 CONVERGED, 5 CAS-ONLY, 89 PARTIAL, 32 PRIMORDIAL, 21 EMPTY |
| AlphaFold | COMPLETE (v1-v6, daily sync at 03:00) |
| Braiding throughput | 145/s (Python convoy), 16K RPCs/s (primal capacity) |
| Blockers (download) | 5 OPEN, 12 need-user registration |

### Priority Convergence Targets

89 datasets at PARTIAL convergence need full provenance pipeline:
`content.put → DAG → spine → braid`. This is the primary throughput target
once `native_braid.py` is replaced with Rust-native composition.

---

## Upstream Brief: What Teams Need to Know

### For wetSpring

1. **Nest Atomic is your local data API** — `nest.health` confirms all 6 domains
   before you start. `nest.capabilities` shows what's available.
2. **No mesh required for local work** — same UDS sockets, same ZFS pool.
3. **Provenance at ingress** — use the Neural API pipeline, not trailer processing.
4. **Gap reporting works** — if a primal is missing, you get a structured gap report.
5. **sweetGrass must be announced after biomeOS restart** — until persistence lands,
   run the announce payload after service restart.

### For projectFOUNDATION

1. **Your federation client is ready** — `foundation-ipc/src/federation.rs` already
   chains `content.exists → content.resolve → content.replicate.pull`.
2. **Data catalog drives convergence** — 38 datasets/362 GB cataloged, 153 total on ZFS.
3. **Sovereignty layers 0-4 are LIVE** — CAS, DAG, spine, braid, signatures all operational.
4. **Layer 5-6 (anchor, sunCloud) are design phase** — no blockers from infrastructure.
5. **Validation pipeline should use Nest Atomic** — `nest.health` before validation runs.

### For Spring/Garden Teams Reassembling

1. **westGate-CAS owns the data layer** — CAS, provenance, and serving are here.
2. **nestgate.io is the trust surface** — external data access goes through PETI.
3. **Use capability.call, not direct socket** — Neural API routes to the right primal.
4. **riboCipher is required for attribution domain** — sweetGrass/braid methods need
   `[0xEC, 0x01]` prefix. The translation registry handles this automatically.
5. **Glue scripts are deprecated** — replacement paths are documented in each script header.

---

## Timeline

| Phase | Target | Description |
|-------|--------|-------------|
| **Now** | Wave 157j | Nest Atomic live, riboCipher fixed, AAR pushed |
| **Next** | Wave 158 | Replace `native_braid.py` with Rust-native `membrane content.braid` |
| **Next** | Wave 158 | Wire `/cas/{hash}` and `/cas/{hash}/provenance` on nestgate.io |
| **Soon** | Wave 159 | Cross-gate CAS federation through songBird mesh |
| **Soon** | Wave 159 | sweetGrass announcement persistence (auto-rediscover at startup) |
| **Target** | Wave 160 | 89 PARTIAL → CONVERGED datasets via native braid pipeline |
