# Foreman Pipeline Specification

**Date**: Aug 12, 2026 | **Wave**: 157k | **Author**: sporeGate topology
**Status**: ACTIVE — partially implemented, convergence target for depot ops
**Predecessor**: G69 Depot Lineage (Phase 2 LIVE), CI-EVO-01 Harvest Scheduler (LIVE)
**Origin**: Depot divergence across 13 gates, 4 architectures, 15 primals, 3+ binary paths per gate. Manual rebuilds and ad-hoc SCP cannot scale.

---

## The Problem: Depot Entropy

Every gate has binaries in multiple locations. Every push overwrites with no history.
Every rebuild is manual. The foreman role exists in code but is only partially wired.

**Observed divergence (Wave 157k ortho sweep)**:
- eastGate depot: **Jun 4** binaries (2+ months stale)
- ironGate `/usr/local/bin/membrane`: **Jun 21** (nearly 2 months)
- sporeGate `membrane-cascade.service`: referenced `/opt/membrane/membrane` (stale Aug 10)
- golgiBody swarmvine: Aug 10 while source was Aug 12
- provenance.toml: missing swarmvine + membrane entries entirely
- Dual cascade timers: system + user, one with rsync shell script

This will only get worse as iosGate, graftGate, and grapheneGate need their own architecture binaries.

---

## Architecture: Foreman + Sub-Builders + CAS Archive

```
    ┌─────────────────────────────────────────────────────────┐
    │  RECEIVE                                                │
    │                                                         │
    │  Forgejo push webhook ─┐                                │
    │  Cascade timer (15m)  ─┼─→ harvest_queue.toml           │
    │  Manual harvest.request│                                │
    │  gossip cascade.notify ┘                                │
    └────────────────────────┬────────────────────────────────┘
                             │
    ┌────────────────────────▼────────────────────────────────┐
    │  IMPULSE                                                │
    │                                                         │
    │  harvest.schedule (10m timer) evaluates queue:           │
    │    • Debounce: 5m after last push                       │
    │    • Staleness: auto-promote after 24h dirty            │
    │    • Team signal: [harvest] commit tag → immediate      │
    │                                                         │
    │  Decision: { build_now: [...], waiting: [...] }         │
    └────────────────────────┬────────────────────────────────┘
                             │
    ┌────────────────────────▼────────────────────────────────┐
    │  BUILD                                                  │
    │                                                         │
    │  Foreman (sporeGate):                                   │
    │    ├─ Local harvest: x86_64-unknown-linux-musl          │
    │    │   (MEMBRANE_BUILD_AUTHORITY=1)                     │
    │    │                                                    │
    │    ├─ Sub-builder dispatch (manifest-driven):           │
    │    │   ├─ ironGate → x86_64-unknown-linux-gnu           │
    │    │   ├─ blueGate → x86_64-pc-windows-gnu              │
    │    │   └─ graftGate → aarch64-apple-darwin              │
    │    │   Transport: songBird mesh capability("build")     │
    │    │   Fallback: SSH JSON-RPC :7701                     │
    │    │                                                    │
    │    └─ Each builder:                                     │
    │        1. Clone/checkout from Forgejo                   │
    │        2. cargo build --release --target {triple}       │
    │        3. ELF/PE/Mach-O validation                      │
    │        4. BLAKE3 checksum                               │
    │        5. Update provenance (previous_blake3, gen++)    │
    │        6. Stage to local depot                          │
    └────────────────────────┬────────────────────────────────┘
                             │
    ┌────────────────────────▼────────────────────────────────┐
    │  PUSH                                                   │
    │                                                         │
    │  depot_sync --push:                                     │
    │    1. BLAKE3 diff: only push changed binaries           │
    │    2. Pre-push: record_lineage_event() → lineage.jsonl  │
    │    3. SCP → .{name}.new atomic rename                   │
    │    4. Push metadata (provenance, checksums, signatures)  │
    │    5. Disk pre-flight (warn 80%, block 90%)             │
    │                                                         │
    │  Targets:                                               │
    │    ├─ golgiBody WAN depot (depot.primals.eco)           │
    │    └─ BLAKE3SUMS regenerated per arch                   │
    │                                                         │
    │  Notification:                                          │
    │    └─ mesh depot.updated gossip event                   │
    └────────────────────────┬────────────────────────────────┘
                             │
    ┌────────────────────────▼────────────────────────────────┐
    │  ARCHIVE (G69 lineage — Phase 2+3 LIVE)                 │
    │                                                         │
    │  Phase 2 (LIVE):                                        │
    │    • provenance.toml: previous_blake3, generation       │
    │    • lineage.jsonl: append-only JSONL of every          │
    │      binary.evolve event (old→new hash, arch, gate)     │
    │                                                         │
    │  Phase 3 (LIVE — a38c70d):                              │
    │    • SCP old binary from remote → foreman CAS           │
    │      $DEPOT/cas/{arch}/{blake3} before overwrite        │
    │    • BLAKE3 hash IS the CAS key — dedup-aware           │
    │    • BLAKE3 verify on download — integrity guaranteed   │
    │    • Next: replicate to ironGate/westGate via mesh      │
    │                                                         │
    │  Phase 4 (FUTURE):                                      │
    │    • loamSpine spine per (primal, arch)                  │
    │    • Merkle-linked harvest event chain                   │
    │    • membrane depot.lineage CLI                          │
    └────────────────────────┬────────────────────────────────┘
                             │
    ┌────────────────────────▼────────────────────────────────┐
    │  CONSUME                                                │
    │                                                         │
    │  Consumer gates:                                        │
    │    1. Receive depot.updated gossip                       │
    │    2. plasmid.fetch from golgiBody WAN depot            │
    │    3. BLAKE3 verify on arrival                           │
    │    4. plasmid.refresh: atomic install to NUCLEUS         │
    │    5. biomeOS composition.orchestrate restart            │
    │    6. (Phase 1 target) deploy.result gossip feedback     │
    │                                                         │
    │  Gate cascade autonomy:                                 │
    │    • gate.quorum timer (15m) on each gate               │
    │    • Pull from depot, compare BLAKE3, install if drift  │
    │    • No foreman involvement needed                       │
    └─────────────────────────────────────────────────────────┘
```

---

## Role Definitions

### Foreman (sporeGate)

The foreman does NOT need to be a build authority in the traditional sense.
It orchestrates: receives signals, evaluates queue, dispatches builds,
pushes results, maintains lineage.

In practice, sporeGate ALSO builds `x86_64-unknown-linux-musl` because it has
the toolchain and it's the fastest path for the primary arch. This is correct —
the foreman can be a builder for its local arch while delegating cross-arch.

**Capabilities**: receive, impulse, build (local arch), push, archive, lineage
**Delegated**: cross-arch builds, CAS storage, spine records

### Sub-Builders

Each sub-builder runs `builder.serve` on `:7701` and registers the `build`
capability with songBird mesh. The foreman dispatches `plasmid.harvest` via
JSON-RPC with `{ local: true, push: false }` — the sub-builder builds locally
and the foreman collects via SCP.

| Gate | Target | Capability | Status |
|------|--------|-----------|--------|
| ironGate | x86_64-unknown-linux-gnu | build | CONFIGURED |
| ironGate | aarch64-unknown-linux-musl | build | **ACTIVE** (Wave 157k — first dispatch Aug 12) |
| blueGate | x86_64-pc-windows-gnu | build | CONFIGURED |
| graftGate | aarch64-apple-darwin | build | CONFIGURED |
| sporeGate | x86_64-unknown-linux-musl | local | ACTIVE |

### CAS Archive Targets

| Gate | Storage | Role |
|------|---------|------|
| ironGate | 14TB NFT braid | Binary CAS primary (hot) |
| westGate | 50.7TB ZFS | Binary CAS secondary (cold) |

Old binaries are content-addressed by BLAKE3. The same hash that validates
the binary IS the CAS key. No new addressing needed.

---

## Timers (sporeGate, as deployed)

| Timer | Interval | Service | Purpose |
|-------|----------|---------|---------|
| `membrane-cascade.timer` | 15m | `temporal.cascade --with-rebuild --with-push` | Sync repos + auto-harvest + push |
| `membrane-harvest-scheduler.timer` | 10m | `harvest.schedule` | Evaluate webhook queue + batch build |

The cascade timer covers the steady-state flow (sync → drift detect → rebuild → push).
The harvest scheduler covers the webhook-driven flow (push event → queue → batch build).

Both timers run with `MEMBRANE_BUILD_AUTHORITY=1` so drift-detected or queued primals
are built locally without requiring explicit operator action.

---

## Divergence Prevention Rules

### 1. Single Canonical Depot

`$ECOPRIMALS_ROOT/infra/plasmidBin/primals/{arch}/` is the ONLY source of truth.

All other paths are downstream copies:
- `~/.local/share/ecoPrimals/plasmidBin/primals/{arch}/` — service runtime
- `/usr/local/bin/` — CLI convenience
- `/opt/membrane/` — LEGACY (will be retired)
- golgiBody `/opt/ecoPrimals/plasmidBin/primals/{arch}/` — WAN distribution

**Rule**: Never build directly to a downstream path. Always build → depot → sync.

### 2. Single Push Path

`membrane plasmid.push` (BLAKE3-aware diff push via SCP) is the ONLY push mechanism.

Retired:
- ~~`depot-push-golgi.sh` (rsync musl-only)~~ — user cascade timer disabled
- ~~Manual SCP~~ — use `plasmid.push` or `--with-push` flag

### 3. Lineage Before Overwrite

Every binary replacement is recorded in `lineage.jsonl` before the old binary
is overwritten. This creates an append-only audit trail that survives even if
CAS archival (Phase 3) is not yet wired.

### 4. Provenance Tracking

Every harvest updates `provenance.toml` with:
- `commit` — source commit SHA
- `blake3` — current binary hash
- `previous_blake3` — hash of the binary being replaced
- `generation` — monotonic counter (0 = genesis)
- `built_at`, `target`, `builder` — provenance metadata

### 5. Consumer Autonomy

Gates pull on their own schedule via `gate.quorum` timer. The foreman pushes
to golgiBody; gates pull from golgiBody. No gate-to-gate binary transfer.

---

## Implementation Status

| Component | Status | Wave |
|-----------|--------|------|
| `temporal.cascade --with-rebuild --with-push` | LIVE | 157a |
| `harvest.schedule` timer | **DEPLOYED** | 157k |
| `MEMBRANE_BUILD_AUTHORITY=1` on cascade | **DEPLOYED** | 157k |
| `previous_blake3` + `generation` in provenance | **LIVE** | 157k |
| `lineage.jsonl` append-only log on push | **LIVE** | 157k |
| User cascade timer retired (dual push eliminated) | **DONE** | 157k |
| Sub-builder dispatch in sovereign.ci.trigger | LIVE | 157g |
| Sub-builder dispatch: ironGate aarch64-musl | **LIVE** (manual dispatch verified) | 157k |
| Sub-builder auto-dispatch in cascade | SPEC ONLY | — |
| CAS archival (SCP old binary to foreman before overwrite) | **LIVE** (G69 Phase 3 — `a38c70d`) | 157k |
| loamSpine lineage spines | SPEC ONLY (G69 Phase 4) | — |
| deploy.result gossip feedback | SPEC ONLY | — |

---

## Next Steps (ordered)

1. **Wire `harvest.schedule` → sub-builder fan-out**: When the scheduler builds,
   it should also dispatch to sub-builders for cross-arch binaries. Currently only
   `sovereign.ci.trigger` fans out.

2. **CAS archival (G69 Phase 3)**: Before overwriting on push, `content.put` the
   old binary to ironGate/westGate CAS. BLAKE3 is already the CAS key.

3. **deploy.result gossip**: Consumer gates emit `deploy.result` after `composition.orchestrate`
   so the foreman knows which gates have which generation.

4. **Retire `/opt/membrane/`**: Move all remaining references to the install depot path.
   `footprint-server.service` is the last user.

5. **Gate depot consistency validator**: Periodic check that all reachable gates'
   depot hashes match the canonical depot. Alert on drift via gossip.

---

*The foreman is a coordinator, not a dictator. It receives signals, evaluates
readiness, builds what it can, delegates what it can't, pushes to the distribution
point, and records lineage. Gates are autonomous consumers. The depot is a HEAD
pointer; CAS is the archive; the spine is the phylogenetic tree.*
