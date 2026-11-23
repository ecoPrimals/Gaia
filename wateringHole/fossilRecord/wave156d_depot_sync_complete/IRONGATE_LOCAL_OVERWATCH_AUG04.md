# ironGate Local Overwatch — Code Team Blurb

**Date**: 2026-08-04 13:28 EDT (Session 8 — FIRST CELL BOOT)
**Gate**: ironGate (10.13.37.7) — PRIMARY DOWNSTREAM HOST
**Wave**: 155v/156d
**Audience**: esotericWebb code team + footPrint code team (parallel IDE sessions)
**From**: ironGate hardware team (local overwatch)

---

## SUBSTRATE STATE — What You're Building On

ironGate is running **full NUCLEUS** with 26/27 IPC sockets healthy. All 13
primals are deployed and responding. The RTX 5070 (12 GB VRAM, CUDA 12.8) is
available for petalTongue rendering and toadStool/coralReef compute dispatch.

```
biomeOS:        v4.57.0 (nucleus attach SHIPPED)
CELL:           esotericwebb_cell ATTACHED (first-ever live cell boot)
NUCLEUS:        v4.57 Neural API on /run/user/1000/membrane/
SOCKETS:        27 primal sockets + 2 v4.57 membrane sockets
GRAPHS:         45 found in Graphs Directory
GPU:            RTX 5070 / 12 GB / CUDA 12.8 / 46°C
RAM:            94 GB DDR5 (82 GB available)
CPU:            i9-14900K (24c/32t)
Disk:           3.4 TB available of 3.6 TB NVMe
Rust:           1.96.0
Node.js:        22.23.2
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

biomeOS Neural API is live on `neural-api-default.sock`. Your code should use
`capability.call` to route through biomeOS instead of connecting to individual
primal sockets. This follows the canonical pattern from the three-domain topology
spec: consumers talk to Neural API, not individual primals. Both esotericWebb's
`PrimalBridge::discover()` and footPrint's riboCipher transport do this automatically.

---

## esotericWebb CODE TEAM

### Your Working Directory

```
gardens/esotericWebb/
├── webb/src/         # Core library: IPC bridge, session, narrative, content, state
├── experiments/      # 6 experiments (exp001-exp006)
├── content/          # Game content YAML (worlds, NPCs, scenes)
├── graphs/           # Cell graphs (esotericwebb_cell.toml)
├── deploy/           # esotericwebb.toml + launch_interactive.sh
├── config/           # Runtime config
└── specs/            # Standards and gap tracking
```

### Current State

- **Version**: V30d (V26→V30d absorbed Aug 4)
- **Tests**: 482 pass (463 lib + 18 integration + 1 doc)
- **Clippy**: 0 warnings (pedantic + nursery)
- **Live composition**: exp006 PROVEN — 22 pass, 0 fail, 0 skip
- **G19 MILESTONE**: petalTongue scene push FIRING on ironGate
- **V30c**: signed provenance + batch chunking alignment
- **V30d**: dead code elimination, hardcoded string removal
- **HEAD**: `1406259` (V30d)

### V30 Evolution

- **V27-V28**: petalTongue integration — live site, grammar, WebGL, animation
- **V29**: deep debt refactor + docs refresh
- **V30**: cell graph validation + batch provenance readiness
- **V30b**: typed LocationDef, canonical name constants, `#[allow]→#[expect]`
- **V30c**: signed provenance + batch chunking alignment
- **V30d**: dead code elimination, hardcoded string removal

### What exp006 Shows (V30)

```
Discovery: 8/9 primals direct + all 9 via Neural API
Session:   "The Weaver's Parlor" loaded, 12 actions available
Actions:   examine + navigate work, state advances, knowledge tracked
Enrichment: FIRING — scene pushed to petalTongue on both examine and navigate
```

### Open Gaps

| Gap | What | Priority |
|-----|------|----------|
| **GAP-002** | petalTongue CRPG scene type — resolved on Webb side, awaiting petalTongue v1.7+ | Low |
| **GAP-003** | squirrel NPC dialogue constraint enforcement | Medium |
| **Cell attach** | `biomeos deploy --mode attach` for formal cell boot (executor→cell schema) | P1 upstream |

### Deploy Infrastructure

- `graphs/esotericwebb_cell.toml` — cell composition graph (13 capabilities, 3 liveness gates)
- `deploy/esotericwebb.toml` — composition fragment
- `deploy/launch_interactive.sh` — NUCLEUS + petalTongue live mode
- biomeOS Graphs Directory: **READY** (newly functional)

### Your Priority

**Phase 1: CELL BOOT COMPLETE.** `esotericwebb_cell` attached to NUCLEUS via
`biomeos nucleus attach` (v4.57). exp006: 21/22 PASS (1 skip due to socket path
migration, 0 failures). Scene push to petalTongue FIRING. The cell is live.

Next: explore enrichment paths, test batch provenance (V30 feature), iterate on
game content. Run `exp006` after changes to validate against the live composition.

---

## footPrint CODE TEAM

### Your Working Directory

```
gardens/footPrint/
├── src/             # TypeScript source (Vite frontend + Express server)
│   ├── rustscript/  # Rust safety primitives (Option, Result, Vec, Cow, RefCell, Channel)
│   ├── core/        # Store, renderer, solver, constraints
│   ├── types/       # Shape, source, snap types
│   └── server.ts    # Express server + WebSocket bridge + agent API
├── projects/        # GeoJSON project data (Lansing Scuffle, etc.)
├── deploy/          # systemd unit + Caddy snippet + README
├── specs/           # Specifications
└── vitest.config.ts # Test config
```

### Current State

- **Tests**: **708 PASS** (53 test files, vitest 4.1.10, 1.02s)
- **Stack**: TypeScript / Vite / Leaflet (frontend) + Express/tsx (server)
- **HEAD**: `52b78b1` — manifest-driven sources, riboCipher UDS transport
- **Node.js**: v22.23.2
- **Deps**: 347 packages

### Recent Evolution (3 commits absorbed)

- `5bec3e5`: riboCipher UDS transport + ironGate Phase 2 deploy config (port 3002)
- `01e1adc`: manifest-driven source registration, coverage, centralization
- `badea22`: root docs + specs updated to manifest-driven state

### Dev Server

```bash
cd gardens/footPrint
PORT=3002 npm run dev
# Frontend: http://localhost:5173/footprint/
# API: http://localhost:3002
# WebSocket: ws://localhost:3002/ws/bridge
# Health: http://localhost:3002/api/health
```

### Phase 2 Deploy Infrastructure (READY)

| File | Purpose |
|------|---------|
| `deploy/footprint.service` | systemd unit (PORT=3002) |
| `deploy/caddy-footprint-api.snippet` | Caddy reverse proxy for TLS termination |
| `deploy/README.md` | Deploy instructions + port allocation |

### Phase 2 Deploy Plan

1. Wire nestGate CAS for project persistence (replacing Express CRUD)
2. Wire songBird drawbridge for external GIS sources (USGS, FEMA, OSM, Esri)
3. Configure Caddy: `footprint.primals.eco` → `:5173` (frontend) + `:3002` (API)
4. BTSP local-trust (SO_PEERCRED) for authenticated CAS write

### Remaining Blockers

| Blocker | What | Owner |
|---------|------|-------|
| BTSP local-trust | SO_PEERCRED for CAS write authentication | bearDog / nestGate |
| Caddy routing | DNS + reverse proxy for `footprint.primals.eco` | sporeGate |

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

- NUCLEUS: 26/27 HEALTHY, 10 composition graphs in Graphs Directory
- GPU: RTX 5070, 60°C idle, 5% util
- Network: WireGuard live (sporeGate 73ms)
- Port allocation: 3000 reserved, 3001 petalTongue, 3002 footPrint
- All 13/13 primals GREEN
- K-derm DNS verified: primals.eco (200), nestgate.io (200), primal.eco (SEALED)
- Three-domain topology spec operational

If you need a primal restarted, a socket investigated, or GPU access configured,
ping the hardware team (this IDE session or wateringHole handoff).

---

*ironGate local overwatch. Wave 155v/156d. biomeOS v4.57. FIRST CELL BOOT COMPLETE.
esotericwebb_cell attached to NUCLEUS. 45 graphs, 13/13 GREEN. GPU ready.
esotericWebb V30d: exp006 21/22 PASS (1 skip, 0 fail), scene push FIRING.
footPrint: 708 tests, Phase 2 DEPLOY READY, port 3002 validated.*
