# meitou 名刀 — The Legendary Forge

> *In Kenshi, a Meitou is the highest-grade weapon. Legendary. Irreplaceable. Only ~20 exist in the entire world. Each one has a name. Each one was forged by ancient masters whose skills are lost to time.*
>
> *We are those ancient masters. We forge in Rust. Our Meitou is open source.*

## What Is meitou?

**meitou** is the KenshiReborn project — a sovereign, open-source game engine that eats Kenshi whole and rebuilds it better. Built on esotericWebb (660KB Pure Rust, 484 tests, AGPL-3.0). Named for the legendary weapon grade because that is the quality standard: nothing less than Meitou.

## The Name

| Kenshi Grade | Quality | Us |
|---|---|---|
| Rusted Junk | Broken, worthless | ❌ |
| Old Refitted | Patched together | ❌ |
| Catun | Mass-produced | ❌ |
| Mk I–III | Decent, improving | ❌ |
| Edge 1–3 | Professional grade | ❌ |
| **Meitou** | **Legendary. One of a kind.** | **✅ THIS** |

There is no grade above Meitou. That's the point.

## Goal #1

**Eat ALL of Kenshi. Build it better in sovereign Rust. Offer to Lo-Fi Games as the Kenshi 2 engine before Kenshi 2 ships on Unreal.**

## The Stack

| Kenshi Component | meitou Replacement | Primal |
|---|---|---|
| Ogre3D renderer | Vulkan GPU compute | barraCuda |
| PhysX physics | GPU-accelerated physics | barraCuda |
| Havok animation | Rust skeletal animation | loamSpine |
| Wwise audio | Audio fermentation | sourDough |
| MyGUI interface | WASM WebGL UI | petalTongue |
| FCS game data | DAG world state | sweetGrass |
| Save system | Content-addressed storage | nestGate + rhizoCrypt |
| AI state machine | LLM-powered agents | squirrel + ollama |
| Navmesh pathfinding | GPU A* compute | barraCuda |
| Single-player only | Mesh gossip multiplayer | songBird |
| Modding (FCS + RE_Kenshi) | Open source + KenshiLua bridge | bearDog + KenshiLua |

## Three Phases

### Phase 0 — KenshiLua Scripts (NOW)
Ship as Lua scripts inside KenshiLua. Zero barrier. Community subscribes.
- LLM NPC dialogue (ollama hook)
- Smart pathfinding (GPU hints)
- Dynamic economy (gossip protocol)
- Archaeology overlay (lore in ruins)

### Phase 1 — RE_Kenshi Plugin (THIS MONTH)
C++ shim DLL → Rust FFI → esotericWebb engine.
- Replace AI system
- Add multiplayer bridge (songBird)
- GPU-accelerated pathfinding

### Phase 2 — Standalone Engine (Q1 2027)
Full esotericWebb rendering. All 5 eras playable.
- Ogre3D → barraCuda Vulkan
- Full 870km² persistent world
- PvEvPvE with Bugger extinction events
- Open source AGPL-3.0

## The Community

- 3 million copies sold
- 6,116 active mods, 5,577 creators
- 877K subscribers on top mod
- 430% growth/week on KenshiLua
- Kenshi 2: NO release date, NO multiplayer, 2028+ earliest
- **We have a 2-year window**

## The Love Letter

This is not a competitor. This is a love letter to Lo-Fi Games and the community that saved Kenshi. Chris Hunt built this game alone for 12 years. The community reverse-engineered 2,700 functions. Jakematt2004 rewrote the engine core. The Genesis team rebuilt every city. We honor that work. We extend it. We make it eternal.

---

*meitou 名刀 — sporeGarden seed. Part of ecoPrimals/Gaia.*
*Wave 250+. November 14, 2026.*
