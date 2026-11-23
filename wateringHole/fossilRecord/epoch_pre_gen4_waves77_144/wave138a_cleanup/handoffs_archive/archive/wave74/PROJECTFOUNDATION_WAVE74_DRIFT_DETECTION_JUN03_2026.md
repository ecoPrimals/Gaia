# projectFOUNDATION — Wave 74 Handoff

**Date**: June 3, 2026
**Wave**: 74
**Owner**: ironGate
**Upstream**: primalSpring (composition validation)
**Lateral**: guideStone (cross-gate parity boundary)

## Delivered This Wave

### 1. Automated Drift Detection (P2)

New `check-versions` subcommand in the foundation UniBin:

```bash
foundation check-versions --eco-root ../../ --json
```

- Parses `lineage/SPRING_VERSIONS.toml` against actual `Cargo.toml` versions
- Reports per-entry: OK, DRIFTED, or UNREADABLE
- JSON output mode for CI/machine consumption
- Human-readable tracing output for interactive use
- New `foundation-core::versions` module: `VersionManifest`, `DriftEntry`, `DriftReport`

**Live test result**: 2 drifted (airSpring 0.8.7→0.10.0, neuralSpring V-tag mismatch),
7 unreadable (primals not on local filesystem), 2 OK (hotSpring, primalSpring).

### 2. GuideStone Boundary Specification (P2)

New `specs/GUIDESTONE_BOUNDARY_SPEC.md` defines validation ownership:

| Layer | Validates | Owner |
|-------|-----------|-------|
| FOUNDATION | Scientific truth (paper vs code) | projectFOUNDATION |
| guideStone | Substrate parity (cross-gate reproducibility) | primalSpring |
| NUCLEUS | Deployment health (composition alive?) | projectNUCLEUS |

Shared interface: lineage record schema, `SPRING_VERSIONS.toml` as mutual reference.
No code changes needed in FOUNDATION until guideStone is implemented upstream.

### 3. Ecosystem Health Dashboard Data (P3)

New `foundation-ipc::dashboard` module:
- `EcosystemHealth` struct aggregating spring + primal health
- `from_manifest()` builder, `with_drift()` enrichment
- JSON-RPC method: `foundation.ecosystem_health`
- Ready for server-side exposure when petalTongue/sporePrint query it

### 4. Deep Debt: Constant Centralization

- **`methods` module**: All RPC method names centralized (12 methods across 5 domains)
- **`paths` module**: Project-relative path conventions (7 paths)
- **`urls` module**: Gallery URL constants
- **`primal_names::slugs::DISCOVERY`**: Meta-primal for family resolution
- **`env_keys::DEFAULT_GATE`**: Eliminates last hardcoded "irongate"
- All `#[allow]` → `#[expect(reason)]` with documented rationale
- IPC timeout deduplicated (client references `transport::DEFAULT_TIMEOUT`)

## Metrics

| Metric | Wave 73 | Wave 74 |
|--------|---------|---------|
| Tests | 154 | **170** |
| Lines | ~8,100 | **8,391** |
| Subcommands | 7 | **8** |
| Clippy warnings | 0 | 0 |
| Binary size | 3.2MB | 3.2MB |
| Hardcoded literals in prod | ~15 | **0** |
| New modules | — | 4 (`versions`, `methods`, `paths`, `urls`) |

## Repository State

- Zero TODO/FIXME in codebase
- Zero `unsafe` in production code
- Zero `.unwrap()` in production code
- Zero `Box<dyn Error>` in production code
- Zero mocks in production code
- All files < 453 lines
- `cargo clean` performed (1.7GB freed)

## Phase C Remaining

1. Wire `SourceFetcher` into pipeline Phase 3 (database-specific fetch)
2. NestGate registration in Phase 4
3. toadStool dispatch in Phase 5
4. Full `ProvenanceSession` trio in Phases 2/7
5. `foundation backfill --write` TOML mutation
6. sporePrint notify trigger from `publish`
7. Signal adoption (`ctx.dispatch()`) for provenance
8. Bash pipeline deprecation after Phase C validation

## For Upstream (primalSpring)

- **guideStone spec** ready for review: defines what guideStone validates vs FOUNDATION
- **Drift detection** flagged airSpring and neuralSpring version mismatches — these
  springs may need lineage count re-verification at next wave
- **Dashboard data model** ready for petalTongue consumption when JSON-RPC server
  is wired

## For Lateral (gate teams)

- `SPRING_VERSIONS.toml` is the shared reference for version synchronization
- Cross-gate parity is guideStone's domain, not FOUNDATION's
- FOUNDATION will consume cross-gate provenance passively when available
