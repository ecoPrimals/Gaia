# projectFOUNDATION — Primal & Spring Evolution Handoff

**Date**: May 16, 2026
**From**: projectFOUNDATION (sporeGarden/gardens)
**To**: All primal teams, all delta springs, primalSpring (upstream audit)
**Context**: Post-Wave 18, post-CATHEDRAL split. projectFOUNDATION has
completed deep debt resolution, expanded CI to 11 gates, written 6 CPU
parity baselines (32 test cases), created spring-oriented provenance
folders, and resolved all composition gaps that were locally solvable.

---

## 1. What projectFOUNDATION Has Proven

### The Validation Pipeline (Python → Rust → NUCLEUS)

```
Published results (papers, databases)
        ↓
Python / NumPy / SciPy baselines (benchmarks/barracuda_cpu_parity/)
        ↓
Rust implementation (spring validation binaries)
        ↓
NUCLEUS composition dispatch (toadStool execute + provenance trio)
        ↓
Parity check + gap report → validation/<spring>/<YYYY-MM-DD>/
```

This pipeline is operational for 4 threads (2, 5, 6, 7) with 80/89
targets passing. Thread 1 (WCM, 27 targets) is blocked on RPC stack.

### Composition Patterns Validated on irongate

| Pattern | Evidence |
|---------|----------|
| 12-node foundation validation graph | `graphs/foundation_validation.toml` — 4 phases, 13 primals |
| Provenance trio end-to-end | DAG session → events → Merkle root → loamSpine seal → sweetGrass braid |
| toadStool dispatch with `trusted_directories` | All 29 workloads use `Standard` isolation |
| BLAKE3 content addressing | `deploy/fetch_sources.sh` + `backfill_hashes.sh` wire data → NestGate |
| Spring-oriented provenance export | `validation/<spring>/<YYYY-MM-DD>/` with `provenance.toml` |
| CPU parity baselines | 6 scripts, 32 cases: variance, mean, matmul, linalg.solve, Verlet MD, spectral |

### CI Pipeline (11 gates)

| Gate | What it catches |
|------|-----------------|
| Shellcheck (5 scripts) | Shell bugs in deploy/ and deploy/lib/ |
| TOML syntax (all files) | Parse errors in any .toml |
| Target schema | Missing keys, non-numeric expected_value/tolerance |
| Thread index completeness | Missing source/target file references |
| BLAKE3 hash coverage | Trends hash backfill progress (never-fail threshold) |
| Workload integrity | Missing metadata, missing command, isolation_level=None |
| CPU parity benchmarks | All 6 Python baselines (32 cases) |
| Graph structural validation | Node names, dependency ordering, capability routing |
| Target count reconciliation | meta.total_targets matches actual [[targets]] count |
| Gate naming consistency | Catches ironGate/irongate drift |

---

## 2. What Primals Need to Evolve

### toadStool

| Item | Priority | Detail |
|------|----------|--------|
| Environment variable expansion | P1 | `${VAR}` in TOML `command`/`args` fields passed literally — workloads need absolute paths |
| Data dependency declaration | P2 | A `[data.inputs]` section in workload TOML for content-addressed data via NestGate |
| Native `--archive` flag | P2 | Currently provenance trio is called by external wrapper; a `[provenance]` TOML section could internalize it |
| WASM runtime smoke test | P3 | Registered but never exercised in a live composition |

### rhizoCrypt

| Item | Priority | Detail |
|------|----------|--------|
| Document `dag.session.create` response schema | P0 | We infer `result.session_id` — unclear if `id` or `session_id` is canonical |
| Document `dag.session.complete` response schema | P0 | We check both `merkle_root` and `root` fields — which is canonical? |
| Accept hex strings for hashes | P2 | Shell integration requires Python one-liners to convert hex ↔ `[u8; 32]` |

### loamSpine

| Item | Priority | Detail |
|------|----------|--------|
| Document `entry.append` with `SessionCommit` | P0 | Response format undocumented — we can't distinguish partial vs full commit |
| Accept hex strings for `data_hash` | P2 | Same hex ↔ byte array ergonomics issue as rhizoCrypt |
| RootPulse method parity | P2 | `COMPOSITION_GAPS.md` Gap RP-1 through RP-5 still open |

### sweetGrass

| Item | Priority | Detail |
|------|----------|--------|
| Document BTSP requirement on TCP port | P1 | Port 9800 requires BTSP handshake; HTTP endpoint works but is dynamic |
| Consistent transport | P2 | Other primals accept plain JSON-RPC on their TCP ports |

### NestGate

| Item | Priority | Detail |
|------|----------|--------|
| `content.put` method | P1 | Referenced in signal graphs but not in current NestGate IPC surface |
| Unified blob listing | P2 | No `storage.list` to enumerate stored artifacts |

### songBird

| Item | Priority | Detail |
|------|----------|--------|
| Cross-gate dispatch | P3 | Foundation validated on single-gate; multi-gate routing not exercised |

### biomeOS

| Item | Priority | Detail |
|------|----------|--------|
| Signal dispatch for `nest.store` | P0 | Foundation pipeline is ready for signal adoption when Rust elevation lands |
| `nest.commit` signal | P1 | Provenance commit sequence should collapse to single dispatch |

---

## 3. What Springs Should Absorb

### All Springs

1. **Dated provenance folders**: Export validation results to
   `projectFOUNDATION/validation/<spring>/<YYYY-MM-DD>/` with:
   - `results.json` (from `ValidationResult::to_json()`)
   - `provenance.toml` (run metadata — see `PROVENANCE_FOLDER_CONVENTION.md`)
   - `braid.json` (sweetGrass attribution, if provenance trio available)

2. **Signal adoption**: Use `ctx.dispatch("nest.store", ...)` instead of
   the 4-call manual sequence when biomeOS v3.56+ is available. See
   `wateringHole/SIGNAL_ADOPTION_STANDARD.md`.

3. **Expression coverage**: All 10 threads have expression documents.
   The upstream blurb (Wave 18) incorrectly claimed threads 3, 4, 8, 9
   "need expression." What they need is **spring validation runs**.

### Per-Spring Actions

| Spring | Thread | Action |
|--------|--------|--------|
| hotSpring | 2 | Maintain 12/12 PASS; add provenance stamps |
| groundSpring | 6, 7 | Maintain 36/36 + 18/18 PASS; add provenance stamps |
| wetSpring | 4, 5 | Complete B7 pipeline (4 targets pending); validate thread 4 enviro targets |
| airSpring | 4, 6 | Coordinate with wetSpring on thread 4; maintain ag PASS |
| healthSpring | 1, 3, 8 | Unblock WCM (RPC stack); validate immunology + health targets |
| neuralSpring | 5-ML | Provide ML surrogate validation data for B3/B4/B6 |
| ludoSpring | 9 | Grow gaming targets; expose 6 IPC methods for esotericWebb |
| primalSpring | 10 | Co-own provenance thread; exp107 results → dated folders |

---

## 4. NUCLEUS Composition Patterns for Downstream

### The Foundation Validation Graph

```toml
# graphs/foundation_validation.toml — 12 nodes
# Phase 0: biomeOS substrate
# Phase 1: Tower Atomic (bearDog + songBird + skunkBat)
# Phase 2: Node Atomic (toadStool + barraCuda + coralReef[optional])
# Phase 3: Nest Atomic (NestGate + rhizoCrypt + loamSpine + sweetGrass)
# Phase 4: Visualization (petalTongue[optional])
# Phase 5: AI (squirrel[optional])
```

This graph is deployed via:
```bash
cargo run -p primalspring --bin primalspring_unibin -- certify \
  --graph graphs/compositions/foundation_validation.toml
```

### Neural API / Signal Dispatch from biomeOS

The foundation validation bash pipeline uses the 4-call manual sequence:
```bash
rpc_nestgate "storage.store" → rpc_rhizocrypt "dag.event.append"
→ rpc_loamspine "entry.append" → rpc_sweetgrass "braid.create"
```

The target Rust elevation (Phase C) will collapse this to:
```rust
ctx.dispatch("nest.store", json!({ "content": data, "author": "foundation" }))?;
ctx.dispatch("nest.commit", json!({ "session_id": session }))?;
```

biomeOS decomposes these signals into the full provenance graph.

### Atomic Instantiation Pattern

Foundation validation exercises three NUCLEUS atomics:

| Atomic | Primals | Foundation use |
|--------|---------|----------------|
| Tower | bearDog + songBird + skunkBat | Trust boundary, discovery, audit |
| Node | toadStool + barraCuda + coralReef | Workload dispatch, tensor math, shader compilation |
| Nest | NestGate + rhizoCrypt + loamSpine + sweetGrass | Storage, DAG, ledger, attribution |

On irongate, all 13 primals run locally via Unix Domain Sockets.
The `discover_port()` function attempts UDS discovery first, falls back
to env vars, then to default ports — with `DISCOVERY_FALLBACK_COUNT`
tracking to warn when discovery is bypassed.

---

## 5. Corrected Thread Status (for upstream blurb refresh)

| Thread | Expression | Targets | Validated | Status |
|--------|-----------|---------|-----------|--------|
| 1 WCM | ABG_WHOLE_CELL_REBUILD.md | 27 | 0/27 | **BLOCKED** — RPC stack |
| 2 Plasma | PLASMA_QCD_SOVEREIGN_GPU.md | 12 | 12/12 | **PASS** |
| 3 Immunology | IMMUNO_DRUG_DISCOVERY.md | 12 | 12/12 | **PASS** (targets validated) |
| 4 Env Genomics | ENVIRONMENTAL_GENOMICS.md | 12 | 8/12 | **ACTIVE** — 4 pending |
| 5 LTEE | LTEE_EVOLUTIONARY_DYNAMICS.md | 18 | 14/18 | **ACTIVE** — 4 pending (B7) |
| 5-ML | ML_SURROGATES.md | 12 | 12/12 | **PASS** |
| 6 Agricultural | MEASUREMENT_SCIENCE.md | 36 | 36/36 | **PASS** |
| 7 Anderson | MEASUREMENT_SCIENCE.md | 23 | 23/23 | **PASS** |
| 8 Human Health | SOVEREIGN_HEALTH.md | 11 | 11/11 | **PASS** (targets validated) |
| 9 Gaming | GAMING_CREATIVE_SCIENCE.md | 13 | 13/13 | **PASS** (seeded) |
| 10 Provenance | PROVENANCE_ECONOMICS.md | 8 | 5/8 | **ACTIVE** — 3 pending |

**Total**: 184 targets, 146 validated (79%), 38 pending.
**Expressions**: All 10 threads have expression documents (authored May 12, 2026).

---

## 6. What We Learned for Ecosystem Evolution

1. **`trusted_directories` is the correct isolation model** — not `None`
   isolation, not `/tmp` override. toadStool's implementation works well.

2. **The provenance trio RPC surface needs documentation** — every caller
   currently guesses at response field names (`session_id` vs `id`,
   `merkle_root` vs `root`). A wire format spec would prevent each
   spring from implementing its own field-name fallback logic.

3. **Signal dispatch is the right abstraction** — the 4-call manual
   sequence works but is error-prone. `nest.store` and `nest.commit`
   collapse the complexity. Springs should adopt when biomeOS supports it.

4. **Python benchmarks are useful but transitional** — the 6 CPU parity
   baselines provide ground truth, but the target state is Rust-only
   validation. The `foundation` UniBin (Phase B/C) replaces them.

5. **Expression documents prevent stale claims** — the upstream blurb
   said 4 threads "need expression" when they all had them. Thread
   expressions should be the source of truth for what exists vs what's pending.

6. **CI gates catch drift early** — target count reconciliation caught
   3 mismatches, shellcheck caught portability issues, graph validation
   ensures composition integrity.

---

## References

- `validation/handbacks/DEEP_AUDIT_FINDINGS_MAY16_2026.md` — full audit
- `validation/COMPOSITION_GAPS.md` — primal gap inventory (updated May 16)
- `validation/PROVENANCE_FOLDER_CONVENTION.md` — dated folder template
- `specs/FOUNDATION_VALIDATE_ELEVATION_REVIEW.md` — Rust elevation plan
- `wateringHole/SIGNAL_ADOPTION_STANDARD.md` — signal migration guide
