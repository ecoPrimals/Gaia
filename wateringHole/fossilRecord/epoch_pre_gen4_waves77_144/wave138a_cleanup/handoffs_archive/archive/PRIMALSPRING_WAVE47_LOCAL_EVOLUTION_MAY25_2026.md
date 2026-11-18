# primalSpring Wave 47 — Local Evolution Handoff

**Date**: May 25, 2026
**Scope**: Method coverage push, plasmidBin Rust elevation, root doc cleanup, upstream absorption

---

## Method Coverage: 70% → 100%

| Before | After |
|--------|-------|
| 324/458 (70%) | 458/458 (100%) |
| 49 scenarios | 52 scenarios |
| 784 tests | 787 tests |

### New scenarios
- **`s_coordination_api`** — exercises `coordination.*` and `neural_api.*` methods through structural checks + live dispatch
- **`s_health_lifecycle_surface`** — exercises `health.*`, `lifecycle.*`, `graph.waves`, `graph.capabilities`, and per-primal version/status methods
- **`s_crypto_identity_surface`** — exercises `crypto.*`, `genetic.*`, `auth.*`, and `identity.*` methods when bearDog available

### Coverage graph
- `graphs/coverage/method_coverage_sweep.toml` — deploy graph referencing all remaining ecosystem methods for coverage detection

### Bug fix
- `tools/check_method_coverage.sh`: search regex `[a-z]+\.` didn't match methods with underscores or digits (e.g. `neural_api.*`, `crypto.sign_ed25519`). Fixed to `[a-z][a-z0-9_.]+`.

### Ionic bond extension
- `bonding.modify_scope` added to `s_ionic_bond` live RPC phase

---

## plasmidBin Rust Elevation: `nucleus_launcher`

New binary: `ecoPrimal/src/bin/nucleus_launcher/` — Rust replacement for
`plasmidBin/nucleus_launcher.sh`.

| Feature | Status |
|---------|--------|
| CLI args (clap) | `--family-id`, `--composition`, `--node-id`, `--dark-forest`, `--dry-run`, `--validate` |
| Dependency-ordered startup | Uses `AtomicType::required_primals()` + `STARTUP_ORDER` |
| Health checks | TCP JSON-RPC health.check probe |
| Registry seeding | Songbird `ipc.register` via TCP |
| Composition validation | `validate_composition_ctx()` integration |
| Socket nucleation | Reuses `SocketNucleation` from library |
| Binary discovery | Reuses `discover_binary()` from library |

Zero unsafe, zero clippy, feature-parity dry-run confirmed.

---

## Root Doc Cleanup

- `CONTEXT.md`: 353 → 254 lines. Compressed Wave 39-42 historical detail, Wave 17-22 garden/infra sections, and Wave 20 PM items into summary lines with fossilRecord reference.
- `PRIMAL_GAPS.md`: Updated biomeOS (v3.75 mesh dispatch), toadStool (S274 yield), petalTongue (WS-4 WASM), loamSpine (benchScale), songbird (zero-debt gate).

## Upstream Absorption

| Primal | What |
|--------|------|
| biomeOS v3.75 | Songbird mesh dispatch replaces `relay.allocate` → cross-gate `capability.call` transparent |
| toadStool S274 | `GuestLoadPolicy` yield-to-owner enforced in `check_quota()` |
| petalTongue WS-4 | 8 new `wasm_bindgen` client-side rendering functions |
| loamSpine | benchScale roundtrip harness (51 validations, 43 methods), RFC 3161 TSA |
| songbird | Wave 47 zero-debt gate clear |

## Debris Sweep

- Zero TODO/FIXME/HACK/STUB markers in source
- Zero .bak/.orig/.tmp files
- Zero stale experiment references
- Zero outdated version numbers in docs
- `KNOWN_DEBT` port collision is intentional (NestGate:9500 / SweetGrass:9850 capability alias)
- `tools/nucleus_launcher.sh` retained (desktop launcher; Rust binary is plasmidBin replacement)

---

## Metrics

| Metric | Value |
|--------|-------|
| Lib tests | 787 (all passing) |
| Scenarios | 52 (10 tracks, 3 tiers) |
| Methods | 458/458 (100% exercised) |
| Clippy | 0 warnings (pedantic + nursery) |
| Binaries | 3 (UniBin + IPC server + nucleus_launcher) |
| CONTEXT.md | 254 lines (was 353) |
