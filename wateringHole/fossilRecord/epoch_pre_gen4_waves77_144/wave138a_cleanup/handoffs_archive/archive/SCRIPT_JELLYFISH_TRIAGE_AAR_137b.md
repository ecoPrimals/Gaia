# Script Jellyfish Triage AAR — Wave 137b

**Date**: Jul 13, 2026 | **Wave**: 137b | **Author**: sporeGate overwatch

---

## Trigger

During DEPOT-REFRESH, we bypassed `membrane depot.integrity` (Rust, BLAKE3, structured TOML) with an ad-hoc Python script (blake2b, flat TOML). This created three format mismatches and activated `require-signed` on a corrupt checksum file. The root cause was a depot directory layout mismatch: `integrity.rs` expected `depot/primals/arch/binary` but our depot used `depot/arch/binary` (flat). Rather than fixing the layout, we reached for a script — classic jellyfish sting.

## What Was Fixed

### 1. DEPOT-LAYOUT — Directory Restructure

Moved arch directories under `primals/` prefix on both sporeGate and golgi:

```
Before: depot/x86_64-unknown-linux-musl/songbird     (flat)
After:  depot/primals/x86_64-unknown-linux-musl/songbird  (matches integrity.rs)
```

- `membrane depot.integrity` now finds **35 binaries across 3 architectures**
- WAN depot paths verified: `/depot/primals/arch/binary` → 200, old flat path → 404
- `provision-golgi.sh` updated to reference new paths

### 2. DEPOT-CHECKSUM-FIX — Native Rust Checksums

Replaced the ad-hoc Python blake2b script with `membrane depot.integrity --depot /opt/ecoPrimals/depot`:

| Aspect | Before (Python) | After (membrane CLI) |
|--------|----------------|---------------------|
| Hash algorithm | blake2b | BLAKE3 |
| TOML format | `[checksums] "arch/name" = "hash"` | `[arch] name = { blake3 = "...", size = N }` |
| Binary stripping | Manual `strip` | `plasmid.harvest` strips automatically |
| Signing | Separate step | `sign.activate` integrated |
| Verification | None | `depot.integrity --verify` (35/35 pass) |

### 3. FOSSILIZE-SUPERSEDED — 6 Scripts Retired

Moved to `infra/fossilRecord/jellyfish-wave137b/`:

| Script | Lines | Rust Replacement |
|--------|-------|------------------|
| `harvest.sh` | 383 | `membrane plasmid.harvest` |
| `deploy_membrane.sh` | 1,784 | `membrane gate.bootstrap` |
| `cascade-sense.sh` | 47 | `membrane temporal.cascade --sense-only` |
| `build-local.sh` | 291 | `membrane plasmid.harvest --all` |
| `validate_parity.sh` | 246 | Rust parity tests |
| `publish.sh` | ~50 | `membrane depot.integrity + sign.activate + rsync` |

**Total**: 2,801 lines of bash retired.

---

## Full Ecosystem Script Inventory

### By Category

| Category | Count | Action |
|----------|-------|--------|
| Fossil/archived (fossilRecord) | ~410 | Already archived, no action |
| Superseded by Rust (just retired) | 6 | Done — moved to fossilRecord |
| Active with Rust equivalent available | 7 | cellMembrane team: deprecate next wave |
| Active with NO Rust equivalent yet | 14 | Evolution targets (see roadmap) |
| Thin glue hooks (keep as scripts) | 4 | Correct pattern — ion channel shims |
| CI/validation scripts | ~8 | Lower priority, evolve to `membrane test.*` |
| Hardware-specific | 4 | Keep — niche, platform-specific |

### Active Scripts with Rust Equivalents (cellMembrane team — next wave)

| Script | Lines | Replace With |
|--------|-------|-------------|
| `fetch.sh` | 422 | `membrane plasmid.fetch` |
| `update.sh` | 427 | `membrane plasmid.fetch --force` |
| `sync.sh` | 181 | `membrane temporal.cascade` |
| `doctor.sh` | 521 | `membrane gate.status` |
| `validate_gate.sh` | 325 | `membrane gate.status` |
| `validate_mesh.sh` | 341 | `songBird mesh.status` IPC |
| `validate_composition.sh` | 329 | `membrane plasmid.composition` |

### Evolution Targets (no Rust equivalent yet)

| Script | Lines | Proposed Primal |
|--------|-------|----------------|
| `provision-golgi.sh` | 750 | cellMembrane: `membrane gate.provision` |
| `nucleus_launcher.sh` | 503 | biomeOS: Neural API graph execution |
| `deploy_gate.sh` | 615 | cellMembrane: `membrane gate.deploy` |
| `deploy_pixel.sh` | 560 | cellMembrane: `membrane gate.deploy --android` |
| `start_primal.sh` | 321 | biomeOS: `lifecycle.start` |
| `cell_launcher.sh` | 394 | biomeOS: Neural API graph execution |
| `seed_workflow.sh` | 472 | songBird: mesh seeding via IPC |
| `bootstrap_gate.sh` | 401 | cellMembrane: `gate.bootstrap` (extend) |
| `stage_usb.sh` | 328 | cellMembrane: `plasmid.stage --usb` |
| `stop_gate.sh` | 91 | biomeOS: `lifecycle.stop` |
| `share_credentials.sh` | 230 | rhizoCrypt: `crypto.share` |
| `onboard-gate-relay.sh` | 294 | cellMembrane: `gate.onboard` |
| `create_genome.sh` | 445 | sourDough: `genome.create` |
| `create_livespore.sh` | 386 | biomeOS: `livespore.create` |

### Scripts That Stay (correct pattern)

Thin glue between external systems and primal IPC — the "ion channel" pattern:

- `golgi-post-receive-relay.sh` (36 lines) — Forgejo hook → `membrane relay.run`
- `context-sense.sh` (49 lines) — Cursor hook → `membrane context.sense`
- `99-mesh-reconnect` (68 lines) — NetworkManager dispatcher → `songbird mesh.reconnect`
- `.githooks/pre-push` (21 lines) — Git hook → `cargo check`

---

## Ownership Matrix

### cellMembrane Team (membrane CLI)
- `plasmid.fetch` / `plasmid.harvest` / `plasmid.build`
- `gate.bootstrap` / `gate.deploy` / `gate.provision`
- `depot.integrity` / `temporal.cascade`

### biomeOS Team (Neural API lifecycle)
- `lifecycle.start` / `lifecycle.stop`
- NUCLEUS graph execution (replaces `nucleus_launcher.sh`)
- `livespore.create`

### sporeGate Team (depot + deploy ops)
- Depot layout alignment (DONE)
- Strip + sign + sync pipeline (DONE — native `membrane` tooling)
- `provision-golgi.sh` content evolution

### songBird Team
- `mesh.status` validation (replaces `validate_mesh.sh`)
- Seed workflow via IPC (replaces `seed_workflow.sh`)

---

## Deployment Pipeline — Before vs After

### Before (jellyfish)
```
cargo build → manual cp → Python blake2b script → manual sign → rsync
```

### After (sovereign)
```
membrane plasmid.harvest → membrane depot.integrity → membrane sign.activate → rsync
```

All Rust. All BLAKE3. All typed TOML. All stripped.

---

## Metrics

- **Scripts retired this session**: 6 (2,801 lines)
- **Depot binaries verified**: 35/35 across 3 architectures
- **Checksum format**: Corrected from flat blake2b to structured BLAKE3
- **WAN depot**: Verified serving at new paths (primals/ prefix)
- **Trust policy**: `require-signed` active system-wide, no more silent pass-through

---

*Jellyfish triage: 6 scripts fossilized, depot layout aligned, native Rust tooling enforced. 14 evolution targets identified across 4 teams. The deployment pipeline is now 100% Rust from build to sign.*
