# Recipe: Classic Games Hologram via petalTongue

**Status**: PLANNED
**Priority**: next-shape
**Dependencies**: petalTongue (builds ✅), toadStool (builds), barraCuda (builds), coralReef

## What This Is

Rebuild the static HUD classics/arcade page as a full petalTongue scene graph
rendered via WASM in the browser, backed by the compute trio (toadStool + barraCuda + coralReef)
on the local LAN. The "hologram on the membrane" — served from eastGate OUT through
the WLAN to the world.

## Architecture

```
Browser (WASM)
  └── petal-tongue-wasm (scene graph renderer)
       └── petal-tongue-scene (declarative scene, animation)
            └── petal-tongue-animation (Manim-style flower animations)

eastGate (LAN server)
  └── petaltongue serve --mode server
       ├── petal-tongue-api (JSON-RPC 2.0 / HTTP)
       ├── petal-tongue-adapters → toadStool (compute.sock)
       │                         → barraCuda (math.sock)
       │                         → coralReef (compiler.sock)
       └── petal-tongue-ipc (UDS + TCP, BTSP encrypted)

golgi (DO VPS, tunnel)
  └── cloudflared tunnel → eastGate:PORT
       └── Caddy reverse_proxy → petaltongue server
```

## The Stack

| Layer | Component | Role |
|-------|-----------|------|
| **UI** | petal-tongue-wasm | Browser WASM rendering module |
| **Scene** | petal-tongue-scene | Declarative scene graph + grammar compiler |
| **Animation** | petal-tongue-animation | Manim-style flower animations |
| **Content** | petal-tongue-scene/site_builder | Static site generation (sporePrint, glossary) |
| **API** | petal-tongue-api | JSON-RPC 2.0 server, HTTP endpoints |
| **Adapters** | petal-tongue-adapters | NCCL-like adapter framework to compute trio |
| **Hardware** | toadStool | GPU/CPU discovery, workload routing |
| **Math** | barraCuda | WGSL shader dispatch, sovereign math |
| **Compiler** | coralReef | GPU compilation, ISA tables |

## What Needs to Happen

### Phase 1: Fix & Ship Static (NOW — done)
- [x] classics.html with archive.org embeds
- [x] classic-games-open.json data feed
- [x] Attribution backscatter to all sources
- [x] Fix broken archive.org IDs (Amazon Trail, Prince of Persia, Colossal Cave)
- [x] 10 playable games in browser via archive.org EM-DOSBOX
- [x] Gygax Thread timeline (D&D → MCP)

### Phase 2: petalTongue Scene Graph (NEXT)
- [ ] Create `petal-tongue-scene` scene definition for the arcade
- [ ] Game cards as scene graph nodes with transitions
- [ ] Berry/Chip/Ed/gAIa as animated characters (flower animation)
- [ ] DOSBox WASM (js-dos) integration as a scene node
- [ ] Build petal-tongue-wasm and embed in classics.html

### Phase 3: Local Server (AFTER)
- [ ] `petaltongue serve` on eastGate
- [ ] JSON-RPC 2.0 API for game metadata + play state
- [ ] cloudflared tunnel from golgi → eastGate:PORT
- [ ] Caddy route for arcade.primals.eco → petaltongue server
- [ ] toadStool discovery for local GPU (DOSBox rendering acceleration)

### Phase 4: Compute Trio (LATER)
- [ ] barraCuda shader dispatch for game rendering
- [ ] coralReef compilation for WGSL shaders
- [ ] toadStool multi-GPU routing across mesh
- [ ] Full holographic membrane: browser → WASM → petalTongue → tunnel → eastGate → compute trio

## What Needs Rebuilding

### wateringHole Reset
The original wateringHole has grown into a directory tree of context, configs,
handoffs, and fossils. It needs to be **reset to shape** — distilled into recipes
that petalTongue renders:

- `wateringHole/GLOSSARY.md` → petalTongue content_render as searchable glossary
- `wateringHole/compositions/` → petalTongue scene definitions  
- `sporePrint/content/` → petalTongue site_builder (already has this path)
- `wateringHole/capability_registry.toml` → toadStool capability discovery

### sporePrint Integration
sporePrint (127 papers) should render through petalTongue's content_render pipeline:
- Markdown → front_matter → shortcodes → site (already implemented in petalTongue)
- petal-tongue-scene/site_builder.rs exists
- Connect sporePrint/content/ → petalTongue content source

### Glossary
- `infra/wateringHole/GLOSSARY.md` → structured data
- petalTongue renders as interactive, searchable, linked glossary
- Each term backlinks to papers, feeds, and code

## The Gygax Connection

```
D&D DM (1974) → Text Parser (1977) → Graphic Adventure (1980)
→ Point-and-Click (1987) → Oregon Trail (1990)
→ ScummVM (2001) → OpenTTD (2004) → MCP (2024)
→ petalTongue scene graph (2026)
```

The scene graph IS the dungeon map. The DM IS the server.
The parser IS the JSON-RPC method. The player IS the browser.
Gygax designed the first protocol. We're implementing the latest.
Same thing. 50 years later. The table is bigger now.

## Files

- `/classics.html` — current static page (Phase 1)
- `/data/classic-games-open.json` — game catalog feed
- `primals/petalTongue/` — the engine (builds, v1.7.0)
- `primals/petalTongue/crates/petal-tongue-scene/` — scene graph
- `primals/petalTongue/crates/petal-tongue-animation/` — Manim animation
- `primals/petalTongue/crates/petal-tongue-wasm/` — browser WASM module
- `primals/petalTongue/web/` — WASM web entry point
- `primals/toadStool/` — hardware substrate
- `primals/barraCuda/` — GPU compute
