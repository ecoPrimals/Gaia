# AAR: sporeGate/golgi Ops — Waves 143b–147e

**Date**: Jul 17, 2026 | **Gate**: eastGate (overwatch) + sporeGate (ops) + golgiBody (VPS)
**Scope**: sporePrint P0 resolution, footPrint NUCLEUS deployment, primalSpring
overwatch, cascade-sense hardening, ecosystem convergence observations.

---

## 1. sporePrint Root 404 — P0 Resolution (Wave 143b)

### Root Cause (NOT transient)

The P0 was flagged repeatedly as "transient" across Waves 141a–145b. Investigation
proved it was **real and reproducible**: 321 genuine HTTP 404 responses logged in
Caddy access logs with `"size":0`.

**Two independent root causes**:

1. **Caddy `file_server` without `try_files`** — Caddy's `file_server` directive
   was not consistently resolving directory requests (`/`) to `index.html`. Added
   `try_files {path} {path}/index.html /index.html` to the sporePrint handle block.
   This is the direct fix.

2. **`cascade-sense` broken** — The service was failing every 15 minutes with TOML
   parse errors in `ecosystem_manifest.toml`. This meant the zola-rebuild drop-in
   (`ExecStartPost`) never fired, so sporePrint auto-rebuilds were dead.

### Manifest Enum Drift Pattern

The `ecosystem_manifest.toml` on golgi had **three** enum mismatches vs the
membrane binary's schema across Waves 143b–147e:

| Wave | Line | Field | Value | Expected |
|------|------|-------|-------|----------|
| 143b | 918 | `bind_mode` | `"tcp"` | `"tcp_only"` |
| 143b | 932 | `mobility` | `"portable"` | `"mobile"` |
| 147e | 917 | `zone` | `"house1"` | `"backbone"` |

**Pattern**: The manifest evolves faster than the golgi deployment. When new
gates are added (northGate → house1 zone, blueGate → tcp bind mode), the
manifest uses intuitive values that don't match the membrane binary's strict
enum variants. Each mismatch silently kills cascade-sense.

### Recommendation for cellMembrane team

- **ENUM-STRICT-01**: `membrane temporal.cascade` should validate the manifest
  TOML against the schema on startup and emit a clear error message identifying
  the field, value, and valid variants. Currently the error is a raw TOML parse
  panic with line numbers.
- **ENUM-STRICT-02**: Consider `#[serde(other)]` fallback on enums that gate
  operators might extend, or add `"house1"` / `"tcp"` / `"portable"` as valid
  aliases.
- **ENUM-STRICT-03**: The `zone` enum should include physical locations like
  `"house1"`, `"house2"` — these are distinct from network topology zones.
  Currently `"backbone"` is being used for all house1 gates, which loses
  semantic precision.

### Status

**FIXED AND HOLDING.** All 3 surfaces (root, /footprint/, live) returning 200.
cascade-sense running successfully with auto-rebuild.

---

## 2. footPrint NUCLEUS Deployment (Wave 147e)

### cellMembrane Handoff

cellMembrane shipped deploy-ready artifacts: systemd service unit, Caddy config
generation, and flagged the binary as "in depot". The handoff was clear and
well-structured.

### Gap: Binary vs Node.js Reality

The service unit expected a compiled binary at `/opt/membrane/footprint-server`.
In reality, footPrint is a **TypeScript Express.js application** (73 .ts files,
272-line server, Express 5.2, Vite, Leaflet, Turf.js).

**Resolution**: Created a Node.js wrapper script at `/opt/membrane/footprint-server`:

```bash
#!/bin/bash
NODE=$(command -v node || echo "/home/sporegate/.nvm/versions/node/v22.23.1/bin/node")
export PORT="${FOOTPRINT_BIND##*:}"
cd /opt/membrane/footprint
exec "$NODE" server.js "$@"
```

The service unit was adapted for Node.js (added `PATH` to node binary, removed
`--socket` CLI args that Express doesn't support).

### Deployment Topology

```
primals.eco/footprint/          → golgi Caddy → static client (local files)
primals.eco/footprint/api/*     → golgi Caddy → WireGuard → sporeGate:8090 (Express)
primals.eco/footprint/ws        → golgi Caddy → WireGuard → sporeGate:8090 (WebSocket)
primals.eco/footprint/ext/*     → [NOT WIRED] → songBird drawbridge (future)
```

Caddy routes use `uri strip_prefix /footprint` to forward `/api/*` and `/ws`
to the Express server, which expects paths at root.

### Verification

| Endpoint | Status | Notes |
|----------|--------|-------|
| `/footprint/` (client) | **200** | Static Vite build from golgi |
| `/footprint/api/projects` | **200** `[]` | API proxy via WireGuard to sporeGate |
| `/footprint/ws` | Proxy working | Express returns 404 on non-upgrade GET (expected) |
| `/` (sporePrint root) | **200** | Unaffected |

### footPrint Transition Decision: TypeScript → Rust

**Current state**: footPrint is a protist (TypeScript composition). It serves:
- Express API server (project persistence, cache management, agent bridge)
- Vite-built Leaflet/Turf.js client (GIS, CAD-like drawing)
- WebSocket agent bridge (petalTongue integration target)

**Why Rust transition is NOT immediate priority**:

1. **Client-heavy**: 73 TypeScript files, mostly client-side Leaflet/Turf.js
   mapping code. The server is only 272 lines of Express. Rewriting the client
   in Rust (WASM) is a major effort with no clear benefit — Leaflet and Turf.js
   are mature JS libraries with no Rust equivalents at parity.

2. **Protist status is correct**: footPrint is a composition (protist), not a
   primal. Protists are allowed external dependencies. The boundary is:
   primals = pure Rust, protists = compositions using primals + external libs.

3. **The server IS a transition candidate**: The 272-line Express server could
   be absorbed into a primal (songBird drawbridge or a new `footprint-server`
   primal), serving the same API surface in pure Rust. This would eliminate the
   Node.js runtime dependency on sporeGate.

4. **Node.js is a jellyfish sting**: The wrapper script + nvm dependency on
   sporeGate is fragile. If node is updated/removed, the service breaks. This
   is the same "script in deployment chain" pattern we triaged in Wave 137.

**Recommended evolution path**:

| Phase | What | Who |
|-------|------|-----|
| **Now** | Node.js wrapper is functional — leave as-is | — |
| **Near-term** | Extract API server into a Rust binary (songBird composition endpoint or standalone) | songBird + petalTongue teams |
| **Near-term** | Move project persistence from Express filesystem to nestGate CAS | nestGate team |
| **Future** | Client could use petalTongue's RustScript bridge for type-safe server calls | petalTongue team |
| **Not planned** | Full Leaflet/Turf.js rewrite in Rust/WASM | — (no ecosystem benefit) |

---

## 3. primalSpring Overwatch — Waves 143b–147c

### KNOWN_DEBT Calibrations

Each cascade brought upstream changes that required eastGate-specific calibration.
Pattern: upstream develops on ironGate/flockGate where different deployment
artifacts exist, then clears debt items that still fail on eastGate.

| Wave | Action | Scenario | Reason |
|------|--------|----------|--------|
| 143b | Added (1) | `footprint-drawbridge-live` | Composition URL not in manifest |
| 143b | Added (3) | `tideglass-composition-routing` | tideGlass not registered |
| 145a | — | All stable | No changes needed |
| 147a | Cleared | `footprint-drawbridge-live` | Upstream registered URL |
| 147a | Cleared | `tideglass-composition-routing` | Upstream registered tideGlass |
| 147c | Re-added (2) | `graphenegate-readiness` | Upstream set to 1, eastGate needs 2 |
| 147c | Re-added (1) | `sporeprint-pure-primal-parity` | Upstream cleared, eastGate still fails |

### Standing eastGate KNOWN_DEBT (Wave 147c)

```rust
const KNOWN_DEBT: &[(&str, u32)] = &[
    ("graphenegate-readiness", 2),
    ("sporeprint-pure-primal-parity", 1),
];
```

### Recommendation for primalSpring team

- **DEBT-GATE-AWARE**: Consider per-gate KNOWN_DEBT overrides. The constant
  re-calibration between gates is friction. A `known_debt.toml` per gate head
  would allow each gate to declare its expected debt without conflicting with
  upstream.

---

## 4. Ecosystem Evolution Observations (Waves 143b–147e)

### Phase 2 Transport — 14/14 COMPLETE

All 14 primals shipped platform-agnostic transport abstractions. The `#[cfg]`
exclusion fences from Phase 1 evolved into trait + backend patterns. Notable
deliveries during our watch:

- bearDog: raw UDS → `TransportEndpoint` dispatch
- nestGate: `TransportStream` + `TransportListener` (Sessions 117–118)
- songBird: Final `IpcStream` cleanup
- squirrel: `TransportEndpoint` + `SecretStore`

### gate.enroll — Automated Mesh Enrollment

cellMembrane shipped `gate.enroll` (7 phases, 753 lines, 8 tests). Codifies
the northGate manual enrollment into a repeatable command. Hub-side peer
addition (`hub.peer`) eliminates operator SSH.

### Credential Boundary Clarification

Guidance issued (Wave 145b): squirrel caches, bearDog stores. `PlatformBackend`
in squirrel should NOT grow native credential variants. bearDog owns HSM,
Keystore, DPAPI backends. squirrel accesses them via `SecurityProvider` IPC.

### northGate Enrollment

6th mesh node enrolled (10.13.37.8, Windows 11, RTX 5090). 34-repo divergence
audit complete — ~1,250 commits behind from June baseline. Repos syncing.
Forgejo-first remote standard enforced for future enrollments.

---

## 5. Standing Issues

| Issue | Severity | Owner | Notes |
|-------|----------|-------|-------|
| cascade-sense manifest enum drift | P2 | cellMembrane | Recurs each time manifest adds new gates/fields |
| footPrint Node.js wrapper | P2 | songBird + petalTongue | Jellyfish sting — server should evolve to Rust |
| sporeGate head staleness | P2 | sporeGate ops | Must manually re-publish after each wave |
| `primals.eco/footprint/ext/*` not wired | P2 | songBird | Drawbridge route for external API proxy |
| KNOWN_DEBT per-gate divergence | P3 | primalSpring | Constant re-calibration between gates |

---

*AAR authored by sporeGate/golgi ops team. Pushed to wateringHole for upstream
overwatch and team handoff.*
