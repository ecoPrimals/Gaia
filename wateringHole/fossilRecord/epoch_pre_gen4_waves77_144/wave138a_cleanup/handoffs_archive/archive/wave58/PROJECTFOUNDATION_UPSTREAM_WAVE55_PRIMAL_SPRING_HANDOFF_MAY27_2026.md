# projectFOUNDATION → Upstream Primals & Springs Handoff (Wave 55)

**Date**: 2026-05-27
**From**: projectFOUNDATION (sporeGarden/gardens)
**To**: primalSpring, biomeOS, toadStool, NestGate, rhizoCrypt, loamSpine,
sweetGrass, BearDog, Songbird, skunkBat, all springs
**Context**: Wave 55, primalSpring v0.9.30, 460 methods, 56 scenarios

---

## Purpose

This handoff captures everything projectFOUNDATION has learned about primal
composition patterns, gaps in primal APIs, neuralAPI/biomeOS orchestration,
and atomic instantiation — from the perspective of a downstream consumer
validating peer-reviewed science end-to-end across 10 domain threads.

---

## 1. Composition Patterns We Consume

### NUCLEUS Nest Composition (Primary)

projectFOUNDATION's 8-phase validation pipeline assumes a Nest-level
NUCLEUS composition with these required primals:

| Primal | Methods Consumed | Purpose |
|--------|-----------------|---------|
| NestGate | `storage.store`, `storage.get` | Artifact registration (BLAKE3-addressed) |
| rhizoCrypt | `dag.session.create`, `dag.event.append`, `dag.session.complete` | Provenance DAG |
| loamSpine | `entry.append` (SessionCommit) | Permanent ledger |
| sweetGrass | `braid.create` | Attribution braid |
| BearDog | `crypto.sign` | Braid signing |
| toadStool | `validate` (workload execution) | Workload scheduling |
| Songbird | `/health` (HTTP) | Network health |

### Optional Primals (Degradation-Safe)

| Primal | Usage | Fallback |
|--------|-------|----------|
| skunkBat | Graph TOML declares dependency; validate does NOT health-check | Implicit skip |
| biomeOS `neural_api` | Graph TOML Phase 0; not consumed by validate | Implicit skip |
| petalTongue | Not consumed | N/A |
| squirrel | Graph TOML optional | `fallback = "skip"` |

### Discovery Pattern

```
Resolution: env ${PRIMAL}_PORT → XDG discovery.sock → discovery_defaults.toml
Host: ${PRIMAL_HOST:-127.0.0.1}
Transport: TCP (JSON-RPC 2.0), UDS for rhizoCrypt
```

We created `deploy/discovery_defaults.toml` as a single source of truth for
bootstrap port defaults. This is a FOUNDATION-local pattern — the canonical
ecosystem resolution should be the discovery socket or biomeOS `capability.resolve`.

---

## 2. Gaps Found in Primal APIs

### toadStool

| Gap | Impact | Suggested Fix |
|-----|--------|---------------|
| `validate` vs `execute` | foundation_validate.sh Phase 5 uses `toadstool validate` but falls back to direct command execution when toadStool is absent. The fallback bypasses scheduling, resource limits, and isolation. | Ensure `toadstool validate` is the canonical interface for workload execution. Document the contract so consumers don't need fallback. |
| `compute.execute` capability | Graph TOML declares it; verify it matches toadStool's actual capability registry | Canonical capability string alignment |
| Workload env expansion | Direct-exec fallback doesn't expand `${FOUNDATION_ROOT}` in workload TOMLs; toadStool presumably does | Document whether toadStool expands env vars in TOML `command`/`args` fields |

### NestGate

| Gap | Impact | Suggested Fix |
|-----|--------|---------------|
| `content.put` / collections / manifests | baseCamp README identifies this as the blocker for full data/compute chains | NC-1 priority: content pipeline must land for pseudoSpore flow |
| `storage.store` failure swallowed | `fetch_sources.sh` swallows errors (`|| true`) when NestGate is down | Return structured error so consumers can degrade gracefully |

### loamSpine

| Gap | Impact | Suggested Fix |
|-----|--------|---------------|
| `SessionCommit` entry_type wire format | RootPulse got `method mismatch` from loamSpine | Verify `entry_type: {"SessionCommit": {"session_hash": [bytes]}}` is the exact contract |
| Merkle root byte array encoding | foundation_validate.sh converts hex to JSON byte array inline — fragile | Provide a canonical `hex_to_entry_bytes` contract or accept hex strings directly |

### rhizoCrypt

| Gap | Impact | Suggested Fix |
|-----|--------|---------------|
| UDS path construction | Duplicated across `primal_ipc.sh` and `foundation_validate.sh` | Standardize path convention: `${XDG_RUNTIME_DIR}/ecoPrimals/rhizocrypt-dag.sock` |
| Session ID / Merkle root field naming | `dag.session.complete` returns `merkle_root` or `root` — we check both | Stabilize response schema |

### biomeOS / neuralAPI

| Gap | Impact | Suggested Fix |
|-----|--------|---------------|
| `nucleus ingest` round-trip | Thread 10 workload created but untested; blocked on NC-1 | biomeOS v3.77+ needs live Nest Atomic deployment to test |
| neuralAPI deployment orchestration | Graph TOML includes `biomeos_neural_api` as Phase 0 node; foundation does not consume it directly | If neuralAPI becomes the deployment interface, document the `composition.deploy(graph)` contract for consumers |
| Atomic instantiation | Foundation assumes Nest-level composition pre-deployed via `projectNUCLEUS/deploy.sh`; biomeOS could provide `atomic.instantiate` for on-demand composition | Evolve toward: `biomeos atomic instantiate --composition nest --gate irongate` |

---

## 3. Python → Rust → Primal Validation Journey

### Current Tier Model (projectFOUNDATION)

```
Tier 1: Python baselines       benchmarks/barracuda_cpu_parity/ (6 scripts, 32 tests)
        ↓ numeric parity
Tier 2: Rust validators         Spring binaries (barraCuda, hotSpring, etc.)
        ↓ provenance wrapping
Tier 3: Primal composition      NUCLEUS Nest (7 primals) + provenance trio
```

### Elevation Status

| Phase | Description | Status |
|-------|-------------|--------|
| A | Shell script hardening (typed registry, discovery config, report extraction) | **Complete** — Wave 55B |
| B | Rust `foundation` UniBin skeleton (`CompositionContext`, typed errors) | **Unblocked** by primalSpring v0.9.30; not started |
| C | Phase-by-phase migration (health → discovery → execution → report) | Planned |
| D | Drop shell scripts; `foundation validate --thread wcm` as pure Rust | Planned |

### What Springs Need to Know

- **Phase B needs `CompositionContext`** from primalSpring — the mechanism for
  typed IPC calls (`ctx.dispatch("nestgate", "storage.store", params)`).
- **Phase B can share types with lithoSpore's `pseudospore-core`** for spore
  envelope structures (NC-5 pattern).
- **Signal dispatch** (`ctx.dispatch()`) should be the canonical Rust IPC
  abstraction — foundation will consume it rather than raw JSON-RPC.

---

## 4. NC-1 / NC-5 Patterns (From Foundation's Perspective)

### NC-1: NUCLEUS Spore Ingest

We created a workload (`workloads/thread10_provenance/nucleus-spore-ingest.toml`)
that validates the full postPrimordial spore flow:

```
biomeOS nucleus ingest → NestGate store → rhizoCrypt DAG → loamSpine ledger
                       → sweetGrass braid → BearDog sign → receipts/
```

**Blocker**: biomeOS v3.77 scaffolded the gateway; needs live Nest Atomic and a
real pseudoSpore artifact to test end-to-end.

### NC-5: postPrimordial Emission Pattern

From the elevation review, the spore ownership split:

| Owner | Responsibility |
|-------|---------------|
| Domain spring | Scientific content (experiment results, validated data) |
| lithoSpore | Envelope (pseudoSpore format, BLAKE3 manifest, layer checksums) |
| biomeOS | Gateway (ingest routing, Nest coordination, atomic emission) |

The `nest_ingest_spore` signal is a 6-step graph that composes existing primal
methods — no new primal methods needed, only biomeOS orchestration.

### Three-Era Provenance Model

| Era | Provenance | Current Status |
|-----|-----------|----------------|
| 1 | Ad-hoc (manual hashes, README provenance) | Legacy — thread 1 WCM sources |
| 2 | Pipeline-derived (fetch → BLAKE3 → register → validate → braid) | **Active** — foundation_validate.sh |
| 3 | NUCLEUS Nest deploy (filled trio braid, atomic storage, sweetGrass attestation) | **Blocked on NC-1** |

---

## 5. Data Coverage (For Spring Consumption)

| Thread | Sources | BLAKE3 | Targets | Validated | Workloads |
|--------|--------:|-------:|--------:|----------:|----------:|
| 1 WCM | 25 | 10/25 | 27 | 0/27 | 3 |
| 2 Plasma | 17 | 0 | 12 | 12/12 | 1 |
| 3 Immuno | 17 | 0 | 12 | 12/12 | 2 |
| 4 Enviro | 20 | 0 | 12 | 8/12 | 2 |
| 5 LTEE | 26 | 0 | 30 | 14/18+12 | 3 |
| 6 AG | 16 | 0 | 36 | 36/36 | 6 |
| 7 Anderson | 11 | 0 | 23 | 23/23 | 2 |
| 8 Health | 13 | 0 | 11 | 11/11 | 1 |
| 9 Gaming | 14 | 0 | 13 | 13/13 | 2 |
| 10 Provenance | 6 | 0 | 9 | 5/9 | 2 |
| **Total** | **165** | **10** | **185** | **~147** | **30** |

### BLAKE3 Backfill Priority

155/165 sources still need BLAKE3 hashes. Priority order:
Thread 4 (enviro, 20 fetchable NCBI sources) → Thread 5 (LTEE, 11)
→ Thread 1 remaining (15) → Thread 3 (immuno, 17) → Thread 8 (health, 13).

Blocked on: running `fetch_sources.sh` to populate `.data/` then `backfill_hashes.sh`.

### SRA Fetcher Gap

`fetch_sources.sh` cannot fetch SRA accessions (needs `sra-tools: fasterq-dump`).
Currently silently SKIPs these. Affects threads 4 and 5 primarily.

---

## 6. CI Gates (What We Validate Upstream)

17 CI gates currently:

1. Shellcheck (7 scripts including report_writer.sh)
2. TOML syntax (all *.toml files)
3. Target schema validation
4. Thread index completeness (all manifests exist)
5. Data manifest hash coverage (baseline: 10 WCM hashes)
6. Workload TOML integrity (metadata + execution + security sections)
7. CPU parity benchmarks (6 scripts)
8. Benchmark result portability (no absolute paths)
9. Graph TOML structural validation
10. Source count reconciliation
11. Target count reconciliation
12. Thread 1 WCM source-target integrity
13. Workload skip section coverage
14. Thread index count reconciliation
15. Shell library fixture tests (json_rpc.sh + thread_registry.sh)
16. Gate naming consistency (irongate lowercase)

**Not in CI** (blocked on live primals): full pipeline execution, primal health
checks, provenance chain, workload scheduling via toadStool.

---

## 7. Recommendations for Upstream Teams

### For primalSpring
- Validate `compute.execute` capability string matches toadStool's registry
- Phase B types: `CompositionContext`, `DispatchError`, signal dispatch
- Consider publishing `foundation_validation` as a certified deploy graph

### For biomeOS
- `atomic.instantiate` contract for on-demand composition would remove the
  requirement for pre-deployed NUCLEUS via shell scripts
- `nucleus ingest` needs live testing with Nest Atomic and real pseudoSpore
- neuralAPI deployment interface contract for graph-based composition

### For toadStool
- Stabilize `toadstool validate` as the canonical workload execution interface
- Document env var expansion behavior in workload TOML fields
- Consider supporting `discovery_defaults.toml` or equivalent config

### For NestGate
- `content.put` / collections / manifests for full data pipeline
- Structured error responses for `storage.store` failures

### For Provenance Trio (rhizoCrypt + loamSpine + sweetGrass)
- Stabilize `dag.session.complete` response schema (field naming)
- Standardize UDS path convention
- loamSpine: verify `SessionCommit` wire format

### For All Springs
- Foundation workloads can consume any spring binary via toadStool
- Workload TOML schema: `[metadata]` + `[execution]` + `[resources]` +
  `[security]` + `[skip]` + `[provenance]`
- Results flow into spring-oriented dated folders:
  `validation/<spring>/<YYYY-MM-DD>/`
