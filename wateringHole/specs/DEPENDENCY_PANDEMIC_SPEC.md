# G72: Dependency Pandemic — Stadial Shift

**Status**: ACTIVE
**Created**: Wave 157g (Aug 10, 2026)
**Owner**: Fleet-wide (overwatch coordinates, primals execute)
**Type**: Stadial/interstadial shift — biological pandemic evolution

---

## Thesis

Dependencies have become expensive to carry. The ecosystem started in Aug 2025 when
Rust hadn't stabilized the 2024 edition, tokio was the only viable async runtime, and
each primal pulled its own HTTP client, logging stack, and RPC framework because
primal compositions didn't exist yet. Since then:

- biomeOS Neural API routes inter-primal communication via `capability.call`
- songBird owns the HTTP mesh — primals don't need their own HTTP clients
- tarpc is the canonical RPC — tonic/prost already excised
- `rustls-rustcrypto` is the canonical TLS — no openssl, no ring
- redb is the canonical embedded KV — sled archived
- tracing is the canonical observability — env_logger is an outlier

The compositions that now exist have **closed the gaps** that originally required
heavy external deps. Primals will shed them as they evolve — a pandemic event where
the cost of carrying unnecessary surface exceeds the cost of removal.

This is not just cleanup. Minimizing the external surface means:
1. **Faster compilation** — fewer dependency trees, no duplicate symbol linkage
2. **More idiomatic Rust** — younger primals like swarmVine can integrate cleanly
   into compositions without inheriting archaic patterns from Aug 2025
3. **Manageable future debt** — as Rust evolves (2027 edition, eventual std async),
   a smaller external surface means smaller migration scope
4. **Cleaner excision of outdated code** — older primals (toadStool started Aug 2025)
   carry vestigial scaffolding that predates biomeOS, Tower Atomic, and the mesh

---

## Audit Results (Wave 157g)

### Tokio Landscape

- **664 Cargo.toml files** across 40 projects
- **~5,569 .rs files** reference tokio (~70% are tests)
- **All 16 primals** depend on tokio — primarily via tarpc
- **~47k `async fn`**, **~81k `.await`**, **~3k `tokio::spawn`**, **~127 `select!`**
- Rust 2024 edition does NOT include a std async runtime — tokio is still needed
  for concurrent servers, but NOT for tools, GPU springs, or sync clients

**Tokio cannot be fully eliminated** — tarpc requires `tokio1`, axum/hyper require
tokio, and the concurrent IPC server model (select! + spawn + async sync) is
architecturally correct for primals that serve connections.

**Tokio CAN be massively reduced** — the blast radius extends far beyond what's
genuinely needed.

### Dependency Fragmentation

| Purpose | Fragmentation | Canonical |
|---------|---------------|-----------|
| HTTP client | reqwest (3), ureq (5, 3 versions), hyper client (4) | songBird mesh / `capability.call` |
| HTTP server | axum 0.7 (5 projects) vs 0.8 (3 projects) | axum 0.8 |
| GPU/shader | wgpu 22 (toadStool) vs 28 (barraCuda, coralReef, springs) | wgpu 28 |
| YAML | serde_yaml vs serde_yaml_ng vs serde-saphyr | Pick one |
| Logging | tracing (30 projects) vs env_logger (4 outlier crates) | tracing |
| Time | chrono (9 projects) vs time (1 project) | chrono (entrenched) |
| Error | thiserror 1 (squirrel) vs 2 (everyone else) | thiserror 2 |
| tokio-serde | 0.8 (squirrel) vs 0.9 (everyone else) | 0.9 |
| tokio features | `["full"]` (3 projects) vs minimal (most) | Minimal |

### Superseded by Compositions

These direct dependencies are now unnecessary because primal compositions exist:

| Dep | Location | Superseded by |
|-----|----------|---------------|
| ureq | nestGate, loamSpine, healthSpring, hotSpring | `capability.call` → songBird |
| reqwest | bearDog ACME, toadStool edge OTA, projectNUCLEUS | `capability.call` → songBird |
| hyper client | petalTongue, rhizoCrypt | songBird `songbird-http-client` |
| prometheus | squirrel (optional) | biomeOS observability |
| jsonrpsee | nestGate (dual protocol) | tarpc + JSON-RPC (evaluate) |

---

## Tiers

### Tier 1 — Pandemic (immediate, low effort, high signal)

Each item is independently shippable. No coordination required.

| Item | Owner | Effort | Impact |
|------|-------|--------|--------|
| **pollster::block_on in GPU springs** | hotSpring, wetSpring, healthSpring | Hours each | Eliminates tokio from ~350 GPU binary files |
| **Trim tokio `["full"]`** | squirrel, sweetGrass, metalForge | Hours each | Compile time + binary size reduction |
| **Remove dead tokio deps** | groundSpring, rustChip | Minutes | Zero source usage, Cargo.toml only |
| **thiserror 1→2** | squirrel | Hours | Version alignment |
| **tokio-serde 0.8→0.9** | squirrel | Hours | Version alignment |
| **env_logger→tracing** | toadStool (3 crates), neuralSpring | Hours each | Logging standardization |

### Tier 2 — Consolidation (sprint, coordinated)

These require cross-primal coordination or testing.

| Item | Owner | Effort | Impact |
|------|-------|--------|--------|
| **HTTP client → songBird/capability.call** | nestGate, loamSpine, healthSpring, hotSpring, projectNUCLEUS | Days each | Eliminates ureq/reqwest from 6+ projects |
| **axum 0.7→0.8** | nestGate, petalTongue, rhizoCrypt, squirrel, bearDog | Days each | Eliminates duplicate tower/hyper trees |
| **wgpu 22→28 in toadStool** | toadStool | Sprint | Prevents duplicate wgpu_core symbols |
| **YAML crate unification** | biomeOS, toadStool, squirrel | Days | 3 YAML crates → 1 |
| **`tokio::sync` → `std::sync` audit** | bearDog, squirrel, songBird | Days each | Non-await modules don't need async locks |
| **tarpc feature trim** | squirrel, sweetGrass | Hours | `["full"]` → minimal features |

### Tier 3 — Evolution (ongoing, as compositions mature)

These emerge naturally as the mesh and compositions evolve.

| Item | Owner | Effort | Impact |
|------|-------|--------|--------|
| **Expand `neural-api-client-sync` pattern** | biomeOS | Sprint | Sync client crate for tools that don't need async |
| **Profile toadStool ~85 tokio files** | toadStool + overwatch | Sprint | Identify sync-wrapped-in-async patterns |
| **sourDough dep validator** | sourDough | Sprint | Detect unnecessary tokio imports fleet-wide |
| **reqwest elimination** | bearDog ACME, toadStool edge | Future | Route through songBird TLS gateway |
| **Fleet-wide archaic pattern excision** | All primals | Ongoing | Aug 2025 era patterns → modern idiomatic Rust |

---

## What We Are NOT Doing

- **Not replacing tokio with smol/async-std** — hotSpring audit already rejected
  this ("full rewrite with no functional benefit"). loamSpine explicitly removed
  async-std.
- **Not adding a runtime abstraction layer** — would touch every primal for
  theoretical benefit. Transport is already abstracted; executor abstraction has
  no current driver.
- **Not migrating chrono→time** — entrenched in 9 projects, low ROI, massive churn.
- **Not eliminating tarpc** — it's canonical and works. The `tokio1` requirement
  is the cost of having a good RPC framework.

---

## Measuring Progress

| Metric | Baseline (Wave 157g) | Target |
|--------|---------------------|--------|
| Projects with tokio `["full"]` | 3 (squirrel, sweetGrass, metalForge) | 0 |
| Direct HTTP client deps (ureq/reqwest) | 8 projects | 2 (bearDog ACME, toadStool edge — both optional) |
| axum version split | 0.7 (5) + 0.8 (3) | 0.8 only |
| wgpu version split | 22 (1) + 28 (3+) | 28 only |
| YAML crates | 3 | 1 |
| env_logger outliers | 4 crates | 0 |
| GPU springs needing tokio runtime | 3 (hotSpring, wetSpring, healthSpring) | 0 |
| Unused tokio deps (Cargo.toml only) | 2 (groundSpring, rustChip) | 0 |

---

## Relationship to Other Goals

- **G70 (Composition Graph)**: As compositions mature, more direct deps become
  vestigial. The graph executor replaces ad-hoc inter-primal HTTP/RPC.
- **G69 (Depot Lineage)**: Smaller binaries from dep reduction → faster depot
  cycles, less disk pressure on golgi.
- **Jelly String Elimination**: Deps that wrap sync ops in unnecessary async are
  the Rust equivalent of jelly strings — foreign patterns that should be native.
- **WASM push (38→48)**: Many of the 10 "irreducibly native" crates are native
  because of tokio. Reducing tokio surface may unlock more WASM targets.
- **swarmVine integration**: As the youngest primal (3 crates, 11 tokio files),
  swarmVine is already lean. Older primals shedding deps converges them toward
  swarmVine's clean patterns, not the other way around.

---

## Biological Metaphor

This is a **stadial/interstadial shift**. During the stadial (Aug 2025 – early 2026),
primals accumulated dependencies like organisms accumulate parasites in a resource-rich
environment — each dep solved an immediate problem. Now the environment has changed:
compositions exist, the mesh routes traffic, the Neural API orchestrates. The deps that
were adaptive are now metabolically expensive. The interstadial selects for lean primals
that integrate through the mesh rather than carrying their own copies of solved problems.

The primals will shed dependencies as they evolve. Young primals like swarmVine are
already born lean. Older primals like toadStool (Aug 2025) and bearDog carry the most
vestigial surface. The pandemic propagates through the fleet via:

1. **sourDough validators** — detect dep violations in CI
2. **Composition maturation** — as `capability.call` routing covers more surfaces,
   direct deps become dead code
3. **Compile pressure** — gates with limited resources (southGate, graftGate)
   benefit most from smaller builds
4. **WASM pressure** — every dep that touches OS APIs blocks WASM compilation

The target is not zero external deps — it's **zero unnecessary external deps**.
The irreducible set is: tokio (for concurrent servers), tarpc (for RPC), serde (for
serialization), axum (for HTTP servers that need it), ed25519-dalek + blake3 + rustls
(for crypto), redb (for embedded storage), wgpu + naga (for GPU compute), clap (for
CLIs), tracing (for observability). Everything else is either superseded by a primal
composition or a version fragmentation that should be unified.
