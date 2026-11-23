# ironGate Local Overwatch — Code Team Blurb

**Date**: 2026-08-03 19:12 EDT (Session 5 update)
**Gate**: ironGate (10.13.37.7) — PRIMARY DOWNSTREAM HOST
**Wave**: 155q/156b
**Audience**: esotericWebb code team + footPrint code team (parallel IDE sessions)
**From**: ironGate hardware team (local overwatch)

---

## SUBSTRATE STATE — What You're Building On

ironGate is running **full NUCLEUS** with 26/27 IPC sockets healthy. All 13
primals are deployed and responding. The RTX 5070 (12 GB VRAM, CUDA 12.8) is
available for petalTongue rendering and toadStool/coralReef compute dispatch.

```
NUCLEUS HEALTH: 26/27 HEALTHY (1 missing: network.sock — non-blocking)
GPU:            RTX 5070 / 12 GB / CUDA 12.8 / 61°C under load
RAM:            94 GB DDR5 (82 GB available)
CPU:            i9-14900K (24c/32t)
Disk:           3.4 TB available of 3.6 TB NVMe
Rust:           1.96.0
Node.js:        22.23.2 (NEW — for footPrint)
```

### Primal Sockets Available (for IPC)

All sockets in `/run/user/1000/biomeos/`:

| Domain | Socket | Status |
|--------|--------|--------|
| ai | `ai.sock` / `squirrel.sock` | HEALTHY |
| crypto | `beardog.sock` / `btsp.sock` / `crypto.sock` / `ed25519.sock` / `x25519.sock` | HEALTHY |
| dag | `dag.sock` / `rhizocrypt.sock` | HEALTHY |
| ledger | `ledger.sock` / `loamspine.sock` | HEALTHY |
| math | `math.sock` / `barracuda.sock` | HEALTHY |
| permanence | `permanence.sock` / `neural-api-default.sock` | HEALTHY |
| provenance | `provenance.sock` / `sweetgrass.sock` | HEALTHY |
| security | `security.sock` / `skunkbat.sock` | HEALTHY |
| shader | `shader.sock` / `coralreef-core-default.sock` | HEALTHY |

### Neural API Routing

biomeOS Neural API is live on `neural-api-default.sock`. Your code can use
`capability.call` to route through biomeOS instead of connecting to individual
primal sockets. esotericWebb's `PrimalBridge::discover()` does this automatically.

---

## esotericWebb CODE TEAM

### Your Working Directory

```
gardens/esotericWebb/
├── webb/src/         # Core library: IPC bridge, session, narrative, content, state
├── experiments/      # 6 experiments (exp001-exp006)
├── content/          # Game content YAML (worlds, NPCs, scenes)
├── deploy/           # esotericwebb.toml (composition fragment) + launch_interactive.sh
├── config/           # Runtime config
└── specs/            # Standards and gap tracking
```

### Current State

- **Version**: V26 (V22→V23→V24→V25→V26 absorbed Aug 3)
- **Tests**: 455 lib pass (release mode), 22/22 exp006 pass
- **Clippy**: 0 warnings (pedantic + nursery)
- **Live composition**: exp006 PROVEN — 22 pass, 0 fail, 0 skip
- **G19 MILESTONE**: petalTongue scene push is FIRING on ironGate
- **HEAD**: `5083c88` (V26)

### What exp006 Shows (as of V24+)

```
Discovery: 4/9 primals direct + all 9 via Neural API
Session:   "The Weaver's Parlor" loaded, 12 actions available
Actions:   examine + navigate work, state advances, knowledge tracked
Enrichment: FIRING — scene pushed to petalTongue on both examine and navigate
```

### V23-V26 Evolution (absorbed from eastGate)

- **V23**: Deep debt — pure Rust deps (`serde_yaml` → `noyalib`), typed rulesets, zero-config discovery
- **V24**: Live cell boot — BTSP transport, membrane discovery, cell graph support
- **V25-V26**: Further deep debt (see `ESOTERICWEBB_V26_IRONGATE_DEEP_DEBT_AUG03_2026.md`)

### Open Gaps

| Gap | What | Priority |
|-----|------|----------|
| **GAP-002** | petalTongue CRPG scene type — resolved on Webb side, awaiting petalTongue v1.7+ | Low (workaround: `ui.render` fallback works) |
| **GAP-003** | squirrel NPC dialogue constraint enforcement | Medium |

### Deploy Infrastructure

- `deploy/esotericwebb.toml` — composition fragment listing all primal dependencies
- `deploy/launch_interactive.sh` — launches NUCLEUS + petalTongue in live mode
- `biomeOS/graphs/gaming_niche_deploy.toml` — 4-phase deploy graph
- `biomeOS/graphs/game_engine_tick.toml` — 60 Hz game loop graph (continuous coordination)

### Your Priority (from eastGate cascade)

**Phase 1: First live cell boot.** This is the first-ever live cell composition
boot in the ecosystem. Run `exp006` to validate, then work toward getting the
enrichment path firing (squirrel AI narration + petalTongue scene push).

### Resolved (previously reported)

`exp002` stale assertion (render_scene standalone) — fixed upstream in V23+.

---

## footPrint CODE TEAM

### Status: UNBLOCKED — Repo Cloned + Tests PASS

footPrint is now on ironGate. Repo found at `protoKarya/footPrint` on Forgejo
(we previously searched wrong orgs: `ecoPrimals`, `sporeGarden`, `syntheticChemistry`).

### Your Working Directory

```
gardens/footPrint/
├── src/             # TypeScript source (Vite frontend + Express server)
├── projects/        # GeoJSON project data (Lansing Scuffle, etc.)
├── public/          # Static assets
├── deploy/          # Deploy configuration
├── specs/           # Specifications
├── vitest.config.ts # Test config
└── package.json     # 347 deps, Node 22.23.2
```

### Current State

- **Tests**: **526 PASS** (33 test files, vitest 4.1.10, 697ms)
- **Stack**: TypeScript / Vite / Leaflet (frontend) + Express/tsx (server)
- **HEAD**: `0cf0a22` — docs update, deploy config, data layer audit
- **Node.js**: v22.23.2 (installed this session)
- **Deps**: 347 packages installed (npm install)

### Dev Server

```bash
cd gardens/footPrint && npm run dev
# Runs concurrently: tsx watch src/server.ts + vite
# Frontend: http://localhost:5173
# Server: http://localhost:3000 (Express API)
```

### Phase 2 Deploy Plan

1. Wire nestGate CAS for project persistence (replacing Express CRUD)
2. Wire songBird drawbridge for external GIS sources (USGS, FEMA, OSM, Esri)
3. Configure Caddy reverse proxy: `footprint.primals.eco` → `:5173` (frontend) + `:3000` (API)
4. petalTongue rendering integration for map tile compositing

### Primal Deps Available on NUCLEUS

| Primal | Socket | Purpose |
|--------|--------|---------|
| nestGate | `permanence.sock` | CAS project persistence |
| songBird | `network.sock` (missing) / Neural API | Drawbridge for external GIS |
| petalTongue | `shader.sock` | Map rendering |
| bearDog | `crypto.sock` | Content signing |

### Open Gaps

| Gap | What | Priority |
|-----|------|----------|
| Caddy routing | `footprint.primals.eco` DNS + reverse proxy | P1 (ops) |
| Express→nestGate | Replace Express CRUD with CAS persistence | P2 (code) |
| network.sock | songBird external drawbridge socket missing | P2 (infra) |

---

## CONVERGENCE RULE (applies to both teams)

> **eastGate owns the codebase.** Code teams on ironGate are consumers and validators.
>
> 1. **DO NOT** push code changes to Forgejo (except wateringHole handoffs)
> 2. **Minimal edits only**: config tweaks, environment-specific settings
> 3. **Report back**: File findings as handoffs in `infra/wateringHole/handoffs/`
> 4. **Pull from Forgejo regularly** to stay converged
> 5. **Bugs**: Document in handoff with file, line, proposed fix — eastGate ships it

### Push access

ironGate has Forgejo SSH push access for `ecoPrimals/wateringHole` only (handoffs).
For code changes, document in a handoff and eastGate will integrate.

---

## HARDWARE TEAM STATUS

- NUCLEUS: 26/27 HEALTHY, monitoring socket stability
- GPU: available, 61°C under load (530 MiB VRAM used)
- Network: WireGuard live (golgi 38ms, sporeGate 77ms, eastGate 78ms)
- Node.js: v22.23.2 (installed for footPrint)
- Binary freshness: sweetGrass (0.7.56 → 0.8.0 in source) and rhizoCrypt
  (0.14.8 → 0.14.17 in source) are behind — depot rebuild pending

If you need a primal restarted, a socket investigated, or GPU access configured,
ping the hardware team (this IDE session or wateringHole handoff).

---

*ironGate local overwatch. Wave 155q/156b. NUCLEUS 26/27 HEALTHY. GPU ready.
esotericWebb V26: live cell boot ready, scene push PROVEN.
footPrint: UNBLOCKED — 526 tests PASS, dev server ready.*
