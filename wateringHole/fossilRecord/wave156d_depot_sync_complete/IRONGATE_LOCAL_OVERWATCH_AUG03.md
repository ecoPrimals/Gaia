# ironGate Local Overwatch — Code Team Blurb

**Date**: 2026-08-05 09:30 EDT (Session 13 — Data Flow Wiring)
**Gate**: ironGate (10.13.37.7) — PRIMARY DOWNSTREAM HOST
**Wave**: 156d
**Audience**: esotericWebb code team + footPrint code team (parallel IDE sessions)
**From**: ironGate hardware team (local overwatch)

---

## SUBSTRATE STATE — What You're Building On

ironGate is running **full NUCLEUS v4.57+** with **live CAS on 12.7 TB ext4**.
nestGate v0.5.0 running with BLAKE3 content-addressed storage.
9 cross-primal providers registered. songBird federation to westGate configured.
**footPrint → squirrel bridge WIRED.** petalTongue scene passthrough LIVE.

```
biomeOS:        v4.57.0 (nucleus attach SHIPPED)
CELL:           esotericwebb_cell ATTACHED (exp006: 19/22 PASS, 0 fail)
SQUIRREL:       signal.dispatch + signal.plan LIVE
NESTGATE:       v0.5.0 — CAS on 12.7 TB ext4 (sdc1), family 9b32f3a8
PROVIDERS:      9 registered (rhizoCrypt, bearDog, nestGate, nestGate-tcp,
                petalTongue, sweetGrass, loamSpine, toadStool, songBird)
SONGBIRD:       v0.2.1 — federation ENABLED, 1 peer (westGate LAN)
NUCLEUS:        v4.57 Neural API on /run/user/1000/membrane/
SOCKETS:        4 membrane + 27 biomeos
GPU:            RTX 5070 / 12 GB / CUDA 12.8
RAM:            94 GB DDR5 (78 GB available)
CPU:            i9-14900K (24c/32t)
Disk (NVMe):    3.3 TB available of 3.6 TB
Disk (CAS):     12 TB available of 12.7 TB ext4 (/mnt/nestgate)
Rust:           1.96.0
Node.js:        22.23.2
```

### What Changed Since Session 12

- **footPrint → squirrel bridge WIRED** — petal-bridge.ts routes `agent.*` to
  squirrel UDS, `visualization.*` to petalTongue UDS. 708 tests PASS.
- **tideGlass PetalTongueClient ACTIVATED** — dead_code removed, client created
  from discovery, dispatch loop forwards viz scenes to petalTongue. 83 tests PASS.
- **petalTongue scene passthrough ADDED** — handle_render_scene now accepts both
  SceneGraph and declarative `{ scene, data, format }` from springs. Build clean.
- **tideGlass cloned** — `springs/tideGlass/` from protoKarya/tideGlass on golgiBody

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

- **Version**: V31b (V30d→V31b absorbed Aug 4)
- **HEAD**: `5902a6f` — capability parity + cell graph alignment for biomeOS v4.57
- **Tests**: 465 lib pass
- **Live composition**: exp006 19/22 PASS, 0 fail, 3 skip (socket migration)
- **G19**: petalTongue scene push FIRING on ironGate

### What's New for You (Session 13)

**petalTongue now accepts your scene JSON directly.** The `visualization.render.scene`
handler has passthrough mode for declarative `{ "scene": "...", "data": {...} }` format.
No need to convert to full SceneGraph — your scene push via cell graph will land.

Scenes submitted with declarative format get stored with `label: "spring:<slug>"` and
the raw data as `data_source` on the root node. The render pipeline can inspect this
for scene-specific rendering.

### Your Priority

**Phase 1 DONE, G18 DONE, CAS LIVE, passthrough LIVE.** Next steps:
1. Test scene push with declarative format to petalTongue
2. Wire `signal_plan` into enrichment pipeline
3. Explore LLM provider setup for live AI narration
4. Continue game content iteration

---

## footPrint CODE TEAM

### Your Working Directory

```
gardens/footPrint/
├── src/             # TypeScript source (Vite frontend + Express server)
│   ├── agent/       # Agent bridge (server-bridge.ts, protocol.ts)
│   ├── rustscript/  # Rust safety primitives
│   ├── core/        # Store, renderer, solver, constraints
│   ├── petal-bridge.ts   # NEW: dual-socket relay (squirrel + petalTongue)
│   └── server.ts    # Express server + WebSocket bridge + agent API
├── projects/        # GeoJSON project data
├── deploy/          # systemd unit + Caddy snippet + README
└── specs/           # Specifications
```

### Current State

- **Tests**: **708 PASS** (53 test files, vitest 4.1.10, 1.04s)
- **Server**: LIVE on :3002 (`status: ok, version: 2.0.0`)
- **Agent bridge**: WebSocket at `/ws/bridge` — READY
- **HEAD**: `a498566`

### What's New for You (Session 13)

**petal-bridge.ts now routes `agent.*` methods to squirrel.** The bridge connects
two UDS sockets simultaneously:

| Method prefix | Target | Socket |
|---------------|--------|--------|
| `agent.*`, `bridge.*` | squirrel | `/run/user/1000/biomeos/squirrel.sock` |
| everything else | petalTongue | `/run/membrane/petaltongue.sock` |

Method translation:
- `agent.query` / `agent.stream` → squirrel `ai.query`
- `agent.cancel` → squirrel `ai.cancel`
- `agent.status` → squirrel `health.check`
- `agent.capabilities` → squirrel `capabilities.list`

**The agent panel chat now reaches squirrel.** When the browser connects to `/ws`
and sends `agent.query`, it goes through Express → petal-bridge → squirrel UDS.
Squirrel responds with a valid JSON-RPC response.

**LLM backend needed for real AI responses.** Without `AI_PROVIDER_SOCKETS`, squirrel
returns "No providers available". To activate:
```bash
export AI_PROVIDER_SOCKETS="http://localhost:11434"  # e.g. Ollama
```

### Your Priority

**Phase 2 DEPLOYED, squirrel bridge WIRED, CAS LIVE.** Next steps:
1. Restart footPrint server to pick up petal-bridge changes
2. Test agent panel in browser — status dot should turn green when squirrel connects
3. Wire CAS persistence into project save/load
4. Set up LLM provider for live AI agent responses

### Remaining Blockers

| Blocker | What | Owner | Status |
|---------|------|-------|--------|
| ~~BTSP local-trust~~ | ~~SO_PEERCRED for CAS write~~ | — | **CLEARED** (rhizoCrypt G63) |
| ~~G18 dispatch~~ | ~~Signal dispatch infra~~ | — | **CLEARED** (Session 10) |
| ~~CAS not running~~ | ~~nestGate not started~~ | — | **CLEARED** (Session 12) |
| ~~squirrel→bridge~~ | ~~petal-bridge squirrel routing~~ | — | **CLEARED** (Session 13) |
| petalTongue UDS | petalTongue needs live/server mode for UDS | hw team | **PENDING** |
| westGate federation | nestGate TCP + content capability | westGate hw | **BLOCKED** |
| LLM provider | AI_PROVIDER_SOCKETS for squirrel | footPrint team | Next code task |

---

## KEY DATES

| When | What |
|------|------|
| Session 8 | FIRST CELL BOOT — esotericWebb attached to NUCLEUS |
| Session 9 | Depot sync validated, 6/8 blockers cleared |
| Session 10 | G18 signal dispatch LIVE — 7 providers, cross-primal dispatch |
| Session 12 | NUCLEUS STORAGE LIVE — 12.7 TB CAS, federation configured |
| Session 13 (now) | **DATA FLOW WIRING** — squirrel bridge, tideGlass→petalTongue, passthrough |
| Next | Code teams restart server, test agent panel, wire CAS persistence |
