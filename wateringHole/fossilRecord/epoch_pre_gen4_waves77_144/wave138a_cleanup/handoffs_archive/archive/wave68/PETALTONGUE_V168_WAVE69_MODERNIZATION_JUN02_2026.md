# petalTongue v1.6.8 — Wave 69 Deep Debt + Modernization Pass

**Date**: June 2, 2026
**Scope**: Error typing evolution, dependency narrowing, dead code elimination, idiomatic Rust modernization
**Commit**: `8e03e97` (modernization pass) on main
**Tests**: 6,208 passing, 0 failures
**Clippy**: 0 first-party warnings
**Fmt**: clean

---

## Changes Delivered

### 1. Error Typing Evolution

| File | Before | After |
|------|--------|-------|
| `platform_dirs.rs` | Manual `DirError` struct + `impl Display` + `impl Error` | `#[derive(thiserror::Error)]` single-line |
| `headless/error.rs` | `IoError(String)` + manual map_err | `Io(#[from] std::io::Error)` + `ScenarioLoad(String)` |
| `src/error.rs` | `Other(String)` via manual `From<io::Error>` | `Io(#[from] std::io::Error)` typed variant |

### 2. Tokio Dependency Narrowing (6 crates)

| Action | Crates |
|--------|--------|
| **Removed from production deps** | `petal-tongue-graph`, `petal-tongue-animation`, `petal-tongue-adapters`, `petal-tongue-telemetry` |
| **Moved to dev-deps only** | `petal-tongue-entropy`, `petal-tongue-cli` |
| **Narrowed features** | `petal-tongue-api`: `[net, io-util, time, rt]` instead of full workspace set |

### 3. Dead Code Elimination

- `VizEntry`: Added `Serialize`, removed `#[expect(dead_code)]` from 3 fields
- `VizRegistry::get()`: Removed dead_code marker, wired into `build_scene`/`build_animation`
- `VizRegistry::list()`: New method returning all entries
- `ContentDirectState.nav`: Wired `/api/nav` JSON endpoint
- New `/api/viz` listing endpoint using `VizRegistry::list()`

### 4. ProcStats Non-Linux Evolution

- `cpu_count()`: `std::thread::available_parallelism()` instead of hardcoded `1`
- `total_memory()`: Reads `PETALTONGUE_TOTAL_MEMORY_BYTES` env fallback

### 5. Idiomatic Rust Pass

- `.to_string()` on string literals → `.to_owned()` across 15+ production files
- Covers: `viz_data/`, IPC handlers, WASM compilers, headless, socket_path

### 6. Prior Wave 69 Work (same session)

- TRUE PRIMAL: Removed `nestgate` backend alias, env fallback, deprecated `NESTGATE_SOCKET`
- Dep trim: `tarpc/unix`, `egui_extras`, `rustix` 0.38→1.x
- IPC evolution: `grammar_placeholder` → `identity_grammar`, texture slot registration

---

## Quality Gates

- `cargo fmt --check` — clean
- `cargo clippy --workspace` — 0 warnings (first-party)
- `cargo test --workspace` — 6,208 passed, 0 failed
- 25 files changed, 133 insertions, 116 deletions

## Root Docs Updated

- `README.md`: Test count → 6,208+, error handling quality note updated
- `START_HERE.md`: Updated date to June 2, 2026 (Wave 69)
- `CONTEXT.md`: Wave 69 status block, test count corrected
- `CHANGELOG.md`: Wave 69 entry added
- `sporeprint/validation-summary.md`: Date, test count, Wave 69 note, removed stale nestgate alias mention

## Remaining Backlog

- aarch64 musl cross-compile for headless
- Audio backend wire protocols (via `audio.play` capability discovery)
- Overlay mode (display capability Phase 2)
- Egui texture resolution (`TextureResolver` with `egui::Shape::image`)
- `crypto.sign` delegation to security provider (currently local BLAKE3)
- Phase 3 self-hosted sporePrint

## Debris Review

- `showcase/`: Fossilized stub (pointer to `fossilRecord/showcase_wave49/`)
- No stale scripts, no archive directories, no `.bak` files
- 3× `TBD` in `specs/NEURAL_API_INTEGRATION_SPECIFICATION.md` (resource limits, permissions, audit logging) — spec-level items, not code debt
- Zero TODO/FIXME/HACK in production Rust code

---

**For primalSpring audit**: Zero blocking items. Maintenance mode, stable.
