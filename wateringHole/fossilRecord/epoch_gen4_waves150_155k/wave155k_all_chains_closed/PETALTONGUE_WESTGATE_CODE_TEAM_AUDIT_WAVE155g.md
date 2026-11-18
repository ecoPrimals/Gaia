# petalTongue Code Team Audit — westGate Wave 155g

**Date**: Jul 28, 2026 15:30 EDT | **Wave**: 155g | **Gate**: westGate
**From**: westGate petalTongue code team
**Primal**: petalTongue v1.7.0 | **Tests**: 6,558 (0 failed) | **Status**: STABLE

---

## Executive Summary

petalTongue is in excellent shape. All 6,558 tests pass, clippy pedantic
produces only 4 doc-backtick warnings, no production `unwrap()` usage
(mechanically enforced), no files exceed 800 lines, AGPL-3.0 license present,
pure-Rust crypto, BTSP ClientHello shipped, Neural API registration wired.
The codebase is audit-ready with minor debt items documented below.

---

## Phase 0 — Connectivity

| Check | Result |
|-------|--------|
| SSH config | `~/.ssh/config` has `git.primals.eco:2222` entry |
| SSH key | `id_ed25519_ecoPrimal` present (Jan 9 2026) |
| Auth test | `golgiAdmin` / `westGate-wave155f` — authenticated |
| Known hosts | Forgejo host key present |

---

## Phase 1 — Sync

### Remotes

All 41 repos repointed from HTTPS to SSH (`ssh://git@git.primals.eco:2222/`).
Org mapping verified: primals → ecoPrimals, gardens → sporeGarden,
springs → syntheticChemistry, infra → mixed.

### Shallow Roots (recloned)

8 repos had incompatible GitHub-era histories. 7 recloned successfully:

| Repo | Status |
|------|--------|
| esotericWebb | RECLONED |
| airSpring | RECLONED |
| groundSpring | RECLONED |
| healthSpring | RECLONED |
| ludoSpring | RECLONED |
| neuralSpring | RECLONED |
| wetSpring | RECLONED |
| **hotSpring** | **FAILED** — corrupt pack on Forgejo (persistent `tmp_pack` error) |

### Other Issues

| Issue | Detail |
|-------|--------|
| hotSpring | Clone fails: `could not open tmp_pack for reading`. Server-side corruption. |
| coralForge | No `main` branch on Forgejo. `git ls-remote origin` returns empty. Empty repo. |
| nestGate | Untracked `vendor/` directory (benign local artifact) |
| Naming | All correct camelCase — no fixes needed (already resolved in Wave 155f sync) |
| Branches | All on `main` except coralForge (detached HEAD / empty) |
| Dirty repos | Only nestGate (`vendor/`). All others clean. |

### Pull Results

| Category | Count | Result |
|----------|-------|--------|
| Pulled successfully | 31 | Up to date or fast-forwarded |
| Recloned (shallow roots) | 7 | Fresh from Forgejo |
| Failed (hotSpring) | 1 | Server-side pack corruption |
| Empty (coralForge) | 1 | No remote refs |
| **Total** | **40/41** functional |

---

## Phase 3 — petalTongue Code Team Audit

### Architecture

| Attribute | Value |
|-----------|-------|
| Version | 1.7.0 (Cargo.toml) — manifest.toml/niche.yaml lag at 1.6.6 |
| Edition | 2024 |
| Rust | 1.87 |
| Workspace crates | 19 |
| Production binary | `petaltongue` (UniBin — 7 subcommands) |
| License | AGPL-3.0-or-later |

#### Architecture Compliance

| Requirement | Status | Detail |
|-------------|--------|--------|
| JSON-RPC + tarpc IPC | **PASS** | JSON-RPC universal listen surface (UDS+TCP); tarpc for Rust hot paths |
| Single genomeBin | **PASS** | `petaltongue` binary; headless/wasm/platform are auxiliary |
| BTSP ClientHello | **PASS** | Full 4-step client + server handshake; Phase 3 AEAD (ChaCha20-Poly1305) |
| Neural API registration | **PASS** | `ipc.register` + `primal.announce` on startup |
| songBird transport | **PARTIAL** | Runtime JSON-RPC to songBird; no universal-ipc crate dep (by design — TLS delegated) |
| Semantic method naming | **PASS** | `domain.operation` convention; 56+ methods; `pt.*` prefix for embedded only |
| genomeBin manifest | **PASS** | `manifest.toml` declares organism, IPC, capabilities, deploy deps |

#### Module Graph (19 crates)

```
Types → Scene → Core → IPC → Discovery → API
                  ↓       ↓
               UI/TUI   Graph/Animation
                  ↓
           WASM/Platform/Headless (auxiliary)
```

### Code Quality

| Metric | Result | Target |
|--------|--------|--------|
| `cargo test --workspace` | **6,558 passed, 0 failed** | ≥90% coverage |
| `cargo clippy --pedantic --nursery` | **4 warnings** (doc backticks only) | 0 warnings |
| `cargo fmt --check` | **Diffs present** (cosmetic only — reordering) | Clean |
| `cargo doc --no-deps` | **3 warnings** (unresolved cross-crate links) | 0 warnings |
| Production `.unwrap()` | **0** (enforced: `unwrap_used = "deny"`) | 0 |
| `todo!()`/`TODO`/`FIXME`/`HACK` in `.rs` | **0** | 0 |
| Max file size | **783 lines** (`geometry.rs`) | ≤800 |

### Clippy Warnings (4 total — all doc backticks)

All in `crates/petal-tongue-ipc/src/btsp/client_hello.rs`:
- Line 87: `ClientHello` missing backticks
- Line 109: `ServerHello` missing backticks
- Line 150: `ChallengeResponse` missing backticks
- Line 175: `HandshakeComplete` missing backticks

### Formatting

`cargo fmt --check` shows cosmetic diffs (import reordering, line-length
reformatting). No semantic changes. Would be a clean `cargo fmt` run.

### Doc Warnings (3 total)

All in `petal-tongue-ipc`:
- Unresolved link `MethodAccess::Protected` (cross-crate reference)
- Unresolved link `MethodGate::check` in `dispatch.rs:14`

### Sovereignty

| Check | Result |
|-------|--------|
| License file | AGPL-3.0 (full text present) |
| Cargo.toml license | `AGPL-3.0-or-later` |
| Telemetry | None — `petal-tongue-telemetry` is local metrics only |
| Cloud lock-in | None — no AWS/Azure/GCP/Sentry deps |
| Crypto | Pure Rust — blake3 (pure feature), chacha20poly1305, sha2, hkdf, hmac |
| Native crypto deps | None — no openssl, ring, or native-tls |

### Dependency Highlights

| Dep | Role | Notes |
|-----|------|-------|
| tokio | Async runtime | Standard |
| axum | Web server | HTTP + SSE + WebSocket bridge |
| tarpc + bincode | Rust RPC | Pulls opentelemetry transitively (not configured) |
| eframe/egui | Desktop UI | Optional (`ui` feature) |
| chacha20poly1305 | BTSP Phase 3 AEAD | Pure Rust |
| ratatui | Terminal UI | Optional (`tui` feature) |
| symphonia | Audio decode | Pure Rust (mp3, wav) |

### Test Coverage Breakdown (sampled)

| Crate | Tests | Notes |
|-------|-------|-------|
| petal-tongue-ipc | 1,856 | Largest — IPC + BTSP + handlers |
| petal-tongue-scene | 1,069 | Scene graph + compilers |
| petal-tongue-core | 668 | Engine + config + transport |
| petal-tongue-ui | 501 | Desktop UI + integration |
| petal-tongue-graph | 380 | Chart rendering |
| petal-tongue-types | 350 | Data binding types |
| petal-tongue-platform | 299 | Embedded runtime |
| Other crates | ~1,435 | discovery, api, tui, wasm, etc. |

---

## Debt & Gaps

### P0 — Must Fix Before Deployment

| Item | File | Detail |
|------|------|--------|
| Version drift | `manifest.toml:11`, `niche.yaml:11` | Both say 1.6.6; Cargo.toml says 1.7.0. Deploy will use stale version. |

### P1 — Should Fix

| Item | File | Detail |
|------|------|--------|
| `cargo fmt` | workspace-wide | Cosmetic reformatting needed (~20 files with diffs) |
| Clippy doc backticks | `btsp/client_hello.rs:87,109,150,175` | 4 warnings — add backticks to type names in doc comments |
| Doc link resolution | `dispatch.rs:14` | `MethodGate::check` and `MethodAccess::Protected` unresolved |
| Files approaching 800 | `geometry.rs` (783), `compiler/tests.rs` (772), `main.rs` (727) | Split before they cross threshold |

### P2 — Track

| Item | Detail |
|------|--------|
| Audio stubs | `socket.rs` / `direct.rs` backends not implemented (PipeWire/ALSA) |
| Platform screen metrics | Windows/macOS paths in `sensors/screen.rs` return `None` |
| `cas_source` dead code | `#[allow(dead_code)]` — awaiting CLI integration |
| mDNS discovery | "Not yet implemented; future evolution path" |
| tarpc → opentelemetry | Transitive dep via tarpc; not used but adds build weight |
| Test magic numbers | `handler_tests.rs` hardcodes wave/nucleus counts — will drift |
| `doom-core` workspace member | Platform stress test — useful but unusual |

### Mocks Standing In for Real Integrations

All mocks are test-scoped — no production mock paths:
- `MOCK_BIOMEOS` / `MOCK_PRIMAL_BASE` — `test_fixtures.rs` only
- `PETALTONGUE_MOCK_MODE` — discovery tests only

### Upstream Blockers

| Blocker | Detail |
|---------|--------|
| songBird availability | Runtime discovery depends on songBird running; no compile-time dep |
| bearDog BTSP | BTSP handshake requires bearDog family_seed; graceful fallback exists |
| biomeOS Neural API | Registration requires Neural API socket; logs warning and continues |
| ZFS pool (westGate) | Nest Atomic tiered storage needs ZFS on 5×14TB HDD — human action |

---

## What We Have Not Completed

1. **WASM pipeline validation on westGate hardware** — builds compile, no
   runtime test on westGate's actual browser/environment yet
2. **genomeBin deployment cycle** — `petaltongue` binary not yet deployed
   via depot fetch + systemd on westGate
3. **Storage tiering integration** — petalTongue doesn't directly interact
   with nestGate's CAS, but sporePrint content delivery will
4. **Cross-gate IPC** — petalTongue can receive mesh.relay transport from
   songBird but not tested in multi-gate topology
5. **`cargo llvm-cov`** — coverage percentage not yet measured (requires
   llvm-tools-preview component)

---

## Next Steps

1. Fix P0: Update `manifest.toml` and `niche.yaml` version to 1.7.0
2. Run `cargo fmt` for clean formatting
3. Fix 4 clippy doc-backtick warnings + 3 doc link warnings
4. Deploy `petaltongue` genomeBin to westGate via depot
5. Validate WASM pipeline in browser on westGate
6. Test IPC registration with Tower Atomic (already LIVE on westGate)
7. Split `geometry.rs` (783 lines) before it crosses 800

---

*westGate petalTongue code team audit Wave 155g: STABLE. 6,558 tests, 0
failures, 4 clippy warnings (doc only), 0 production unwrap, AGPL-3.0
sovereign, pure-Rust crypto, BTSP shipped, Neural API wired. One P0
(version drift in manifest). Ready for genomeBin deployment cycle
validation on westGate hardware.*
