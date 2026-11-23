# coralReef — Wave 22 Stadial Gate Resolution

**Date**: May 17, 2026
**Primal**: coralReef (shader compiler)
**Version**: 0.2.0 (previously 0.1.0)
**Tests**: 3181
**Grade**: A++ (upgraded from A+)
**Debt Level**: CLEARED

---

## Audit Items Resolved

### Version Alignment (CRITICAL)

**Problem**: Manifest said `0.1.0`, README used "Phase 10 Sprint 12" — no
semver alignment.

**Resolution**:
- Workspace `Cargo.toml`: `0.1.0` → `0.2.0`
- `genomebin/manifest.toml`: `0.1.0` → `0.2.0`
- `infra/plasmidBin/manifest.toml`: `latest = "0.1.0"` → `latest = "0.2.0"`
- `README.md`: now shows `0.2.0 — Phase 10, Sprint 12`

**Rationale for 0.2.0** (not 1.0.0): Significant Phase 10 evolution (RayQuery,
tensor GEMM, full image ops, subgroup ops, function inlining) but no public
API stability guarantee yet. `0.2.0` correctly signals "matured past initial
prototype" without overpromising.

### ecobin_grade A+ → A++

**Problem**: Ecosystem manifest said `A+`, genomebin manifest said `A++`.

**Resolution**: Updated ecosystem manifest to `A++`. The `A+` was stale — it
predated Sprint 11 (full image ops: Sample/Store/Query/Gather/Atomic) and
Sprint 12 (RayQuery, function inlining). coralReef now meets `A++` criteria:
zero unsafe, zero C, full clippy pedantic, deny.toml sovereign, BTSP Phase 3,
Wire Standard L3, 3181 tests.

### `build_from_source = true`

**Verified intentional**: coralReef depends on `naga` 28.0.0, `nak-ir-proc`
(proc macro), and `amd-isa-gen` (build-time codegen) — all require source
compilation. No pre-built naga binaries exist. `musl-static` build works.

### Method Count / Namespace

**Actual method count**: 16 served + 3 consumed = 19 total wire surface.

The ecosystem registry reported "11 methods" — this was the `shader.*` subset
only. Full count:
- shader.compile.* (6 methods)
- health.* (4 methods)
- identity.get (1)
- capability.list (1)
- btsp.negotiate (1)
- auth.* (3 methods)

**Namespace expansion reviewed**: `shader.validate` and `shader.optimize`
considered and deferred — validation is available via `compile` with
`validate: true`, and optimization is not a separable service.

### Provided vs Consumed Drift

**Problem**: `genomebin/manifest.toml` listed `capability.register` and
`ipc.heartbeat` in `provided` — but coralReef only CALLS these methods on
the ecosystem registry (Songbird). It does NOT serve them.

**Resolution**: Moved to `consumed` list. Also added `health.version` to
`provided` (was served but not listed).

### Stability Tiers

All 16 served methods annotated as **Stable** in `STADIAL_READINESS.md`.
Rationale: the wire contract for all methods has been frozen since Sprint 9
and tested by primalSpring, hotSpring, and benchScale.

### Degradation Behavior

Documented in `STADIAL_READINESS.md`:
- coralReef is **stateless** — restart recovers immediately
- Downstream (barraCuda, toadStool, hotSpring) degrade gracefully via cache
- No data loss, no state corruption when coralReef is unavailable

### Downstream Pairing

Documented in `STADIAL_READINESS.md`:
- **barraCuda**: compilation target (coralReef compiles → barraCuda executes)
- **hotSpring**: VFIO sovereign GPU pipeline validation
- **toadStool**: hardware dispatch (Compute Trio wire contract)

---

## Composition Gaps

**None owned** (hardware code extracted to toadStool per Wave 8).

---

## Stadial Pairing Confirmed

| Partner | Role | Validation Status |
|---------|------|------------------|
| barraCuda | Compilation target | Wire contract frozen, 93/93 corpus |
| hotSpring | GPU dispatch validation | Cross-spring validated |
| toadStool | Hardware dispatch | Compute Trio contract frozen |

---

## Files Modified

- `Cargo.toml` (workspace version → 0.2.0)
- `genomebin/manifest.toml` (version, tests, provided/consumed, description)
- `README.md` (version line)
- `STATUS.md` (date, version, grade, method listing)
- `STADIAL_READINESS.md` (new — full stadial checklist + stability tiers)
- `infra/plasmidBin/manifest.toml` (coralReef entry: version, grade, capabilities)
