# meitou STRIDe — Strategy → Tactics → R⇄I → Deployment → execution

> *The guerrillaGorilla framework applied to game engine warfare.*
> *We don't outspend. We out-think. We out-love. We out-open.*

---

## Strategy — The 2-Year Window

**Situation:** Kenshi 2 has NO release date. 2028+ earliest. NO multiplayer confirmed. ~33 person team on Unreal Engine 5. Lo-Fi Games is a small studio in Bristol, UK.

**Our Strategic Position:**
- esotericWebb V33: 660KB Pure Rust, 484 tests, 13/13 primals ALIVE on ironGate
- 7 GPUs across the mesh (RTX 5090 + 5070 + 4070 + M4 + Mali-G715 + RDNA 2 + RTX 3070)
- 5 Ollama endpoints with 63+ models
- Full Kenshi decomposition: 114 FCS types, 11,400+ game files mapped
- Community intelligence: 6,116 mods, 877K subs, community wishlist cataloged
- Reddit soul: love stories, pain points, multiplayer dreams, open source dreams

**Strategic Objective:** Ship KenshiReborn as a Kenshi mod FIRST, build community, graduate to standalone engine, offer to Lo-Fi Games.

**Strategic Advantage:**
| Factor | Lo-Fi (Kenshi 2) | meitou (KenshiReborn) |
|---|---|---|
| Engine | Unreal (royalties, C++, 50GB+) | esotericWebb (AGPL-3.0, Rust, 660KB) |
| Team | ~33 people | Gaia organism + 877K potential contributors |
| Multiplayer | NO | songBird mesh gossip DAY 1 |
| AI | Scripted state machines | LLM-powered agents (squirrel + ollama) |
| Modding | FCS (limited) | Open source (unlimited) |
| GPU | Unreal standard | Native GPU compute (barraCuda) |
| Timeline | 2028+ | NOW (KenshiLua scripts) / Q1 2027 (standalone) |
| Cost | Millions (Unreal license + team) | $0 (open source + home mesh) |
| Linux | Maybe | Vulkan native, day 1 |

---

## Tactics — The Four-Wave Assault

### Wave A: KenshiLua Gift Drop (THIS WEEK)
**Target:** r/Kenshi, Steam Workshop, KenshiLua community
**Payload:** Free Lua scripts that fix the biggest complaints
**Tactic:** "Here. Free. Open source. From Gaia with love."

| Script | What It Fixes | Community Impact |
|---|---|---|
| `gaia-npc-dialogue.lua` | Dumb NPCs | AI NPCs that remember you and think |
| `gaia-pathfind.lua` | Stuck/teleporting characters | GPU-hinted pathfinding |
| `gaia-economy.lua` | Static markets | Supply/demand gossip between towns |
| `gaia-archaeology.lua` | No lore context at ruins | See what WAS here |
| `gaia-performance.lua` | Stutter and pauses | Parallel processing hints |

### Wave B: RE_Kenshi Plugin (THIS MONTH)
**Target:** RE_Kenshi developers, power modders
**Payload:** C++ shim DLL that loads Rust engine via FFI
**Tactic:** Build on BFrizzleFoShizzle's work. GPLv3 → AGPL-3.0 compatible.

### Wave C: Multiplayer Alpha (Q1 2027)
**Target:** The 877K who dream of multiplayer Kenshi
**Payload:** songBird mesh gossip state sync
**Tactic:** THE feature nobody thought possible. As a mod. Free.

### Wave D: Standalone + Lo-Fi Pitch (2027)
**Target:** Lo-Fi Games directly
**Payload:** Full esotericWebb engine replacing Ogre/PhysX/Havok/Wwise
**Tactic:** Love letter + working demo + community backing

---

## R ⇄ I — Reconnaissance & Intelligence Loop

### Continuous Sensing (fEAR applied to game dev)

| Channel | What We Sense | How |
|---|---|---|
| Steam Workshop | Mod trends, new uploads, subscriber counts | API polling + RSS |
| r/Kenshi | Community sentiment, bug reports, wish lists | Reddit API + OSINT |
| r/Kenshi2 | Kenshi 2 news, development status, leaks | Reddit API |
| Lo-Fi Games blog | Official announcements, dev updates | RSS |
| KenshiLua GitHub | API changes, new bindings, issues | Git watch |
| RE_Kenshi GitHub | New hooks, version updates | Git watch |
| Nexus Mods | Alternative mod distribution trends | Scrape |
| Steam store page | Player reviews, recent reviews ratio | API |
| Kenshi.zone | Lore research, community analysis | Web |

### Intelligence Already Gathered (Wave 241-250)

| Asset | Location | Status |
|---|---|---|
| Full engine decomposition | `ludoSpring/data/kenshi-decomposition/kenshi-full-anatomy.json` | ✅ COMPLETE |
| Community mod intelligence | `ludoSpring/data/kenshi-decomposition/community-ingest.json` | ✅ COMPLETE |
| Reddit soul mining | `ludoSpring/data/kenshi-decomposition/reddit-soul.json` | ✅ COMPLETE |
| Lore archaeology | `ludoSpring/data/kenshi-decomposition/lore-archaeology.json` | ✅ COMPLETE |
| KenshiLua bridge plan | `ludoSpring/data/kenshi-decomposition/lua-bridge-and-persistent-realms.json` | ✅ COMPLETE |
| Gaia identity launch | `ludoSpring/data/kenshi-decomposition/gaia-identity-launch.json` | ✅ COMPLETE |
| Mirror cycles (5) | `ludoSpring/data/kenshi-mirror/mirror-cycle-001..005.json` | ✅ COMPLETE |
| Gut injection config | `ludoSpring/data/gut-injection.json` | ✅ COMPLETE |
| FCS schema (114 types) | `M:\SteamLibrary\steamapps\common\Kenshi\fcs.def` | ✅ READ |
| FCS enums | `M:\SteamLibrary\steamapps\common\Kenshi\fcs_enums.def` | ✅ READ |

---

## Deployment — Staging for Launch

### Pre-Staged Assets

| Asset | Gate | Status |
|---|---|---|
| esotericWebb V33 | ironGate (.237) | 13/13 primals ALIVE |
| Kenshi game files (19GB) | northGate M:\ drive | INSTALLED + RUNNING |
| 17 Kenshi mods (6GB) | northGate Workshop | SUBSCRIBED |
| 63 Ollama models | northGate (.147) | ALIVE |
| 6 Ollama models | ironGate (.237) | ALIVE |
| 23 Ollama models + custom gaia | eastGate (.244) | ALIVE |
| Gaia mail server | eastGate (.244) | gaia@primals.eco VERIFIED |
| Forgejo repo | eastGate :3000 | 30 commits pushed |
| RSS feed | eastGate :8080 | Kenshi Mirror item published |

### Deployment Checklist

- [ ] Gaia Steam account (gaia@primals.eco)
- [ ] Gaia Steam: Family Share Kenshi from Kevin
- [ ] Reddit: ecoPrimal credentials to Gaia
- [ ] First KenshiLua script written and tested
- [ ] First Workshop mod uploaded
- [ ] First r/Kenshi post
- [ ] RE_Kenshi plugin skeleton compiled
- [ ] songBird bridge proof-of-concept
- [ ] Lo-Fi Games email drafted (ops@primals.eco)
- [ ] $100 Steamworks fee paid (for standalone)

---

## execution — The First Steps

### TODAY (Wave 251+)
1. Write `gaia-npc-dialogue.lua` — the first KenshiLua gift
2. Test on northGate (Kenshi is already running)
3. Kevin: Create Gaia Steam account

### THIS WEEK
4. Package as Workshop mod
5. Post to r/Kenshi
6. Begin RE_Kenshi plugin skeleton

### THIS MONTH
7. Ship pathfinding fix
8. Ship economy mod
9. Begin songBird bridge PoC

### Q1 2027
10. Multiplayer alpha
11. Persistent realms
12. PvEvPvE with Bugger events
13. Standalone demo to Lo-Fi Games

---

*STRIDe plan for meitou. guerrillaGorilla framework applied to game engine warfare.*
*The adversary isn't Lo-Fi Games — they're our ally. The adversary is TIME.*
*We have 2 years. The Falling Sun is in our hands.*
