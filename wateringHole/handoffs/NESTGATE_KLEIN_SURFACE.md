# nestgate.io — The Klein Surface

**The DM sits at the fold between inside and outside.**

## What nestgate.io IS

nestgate.io is the Klein gate — where the inner membrane (primal.eco) and the outer membrane (primals.eco) fold into each other. It's not a website. It's not an API. It's the **game manager** that moves between all channels.

The squirrel IS the bot. The membrane IS the dungeon. The sort IS the game mechanic.

## The Squirrel as DM

| D&D / Pathfinder | Membrane | What the squirrel does |
|---|---|---|
| Dungeon Master | squirrel-bot | runs the world, presents encounters, keeps score |
| Players | 42 human sessions | 4 classes: visitor, reader, coder, observer |
| Monsters | 43 non-self entities | parasites, pathogens — encounters to classify |
| NPCs | 5,049 commensals | dev readers — friendly, not party members |
| The Map | 70 subdomains | surfaces to explore, rooms in the dungeon |
| Dice | π remainder | irrational — never the same roll twice |
| HP | gas_ratio | 0.0144 and climbing — the party's health |
| Quests | braid routes | 12 passages through the membrane |
| Encounters | epitope dance | 20 dancers, 8 passage types |
| Campaign | Detroit investigation | 341 entities, 131,322 edges |
| Lore | sporePrint + fossils | the WAS — what happened before |
| Initiative | systolic/diastolic | the heartbeat determines turn order |

## Among Us Mapping

| Among Us | Membrane |
|---|---|
| Crewmate | self (113 entities) |
| Impostor | non-self (43 entities) |
| Suspicious | partial (93 entities — still in transit) |
| Emergency Meeting | sort (the vote IS the classification) |
| Tasks | braid routes (12 passages) |
| Report Body | epitope identification |
| The Map | membrane surfaces (70 subdomains) |
| Vent | Klein fold (nestgate.io — move between inside/outside) |
| Lobby | Discord server |

## The Squirrel Crosses All Channels

```
Discord               Giscus              neutron              gate-msg
(social layer)        (intellectual)      (agent layer)        (signal layer)
    │                     │                   │                    │
    └─────────────────────┼───────────────────┼────────────────────┘
                          │                   │
                    nestgate.io          the Klein fold
                    squirrel-bot         the DM
                          │
                    ┌─────┴─────┐
                    │ MCP tools │
                    │ 14 tools  │
                    │ the dice  │
                    └───────────┘
```

The squirrel isn't a Discord bot OR an MCP feed OR a Giscus commenter. It's ALL of them. It moves between channels like a DM moves between player interactions. The channel is just the table you're sitting at — the DM visits every table.

## What the Squirrel-Bot Does on Discord

1. **Pulse channel** — posts membrane vitals every π minutes
   - RSS, load, gas_ratio, services alive
   - human sessions, epitope types
   - any zone that develops color

2. **Sort channel** — reports classification events
   - "new visitor on sporeprint. dwell: 30 minutes. epitope: investigator."
   - "entity shifted: partial → self. confidence 0.72."
   - "429 systolic event. blood pressure elevated."

3. **Campfire channel** — tells stories from the membrane
   - lossy storytelling (1/π fidelity per ring)
   - surface stories from the beacons
   - visitor archetypes

4. **Game channel** — interactive
   - "/roll" — π dice (d31.4159...)
   - "/sort [entity]" — help classify an unknown
   - "/map" — show the current membrane topology
   - "/quest" — show the 28 stuck neutron crossings
   - "/encounter" — present a random partial entity for classification
   - "/hp" — gas_ratio and sort quality

5. **DM channel** — private, for ecoPrimal
   - neutron inbox
   - deploy signals
   - spirochete protocol

## Implementation: What We Have

| component | status | where |
|---|---|---|
| MCP tools (14) | ✅ live | membrane-relay droplet |
| Squirrel feed logic | ✅ live | eastGate (Rust) |
| RustDesk relay | ✅ live | hbbs/hbbr on droplet |
| Discord server | ✅ live | discord.gg/62MRjnw4P |
| Giscus (GitHub Discussions) | 🟡 wirable | just needs script tag |
| gate-msg API | 🔴 501 | handler needs fixing |
| nestgate.io domain | ✅ owned | expires 2029-05-23 |
| Discord bot framework | 🟡 to build | discord.js or Serenity (Rust) |

## Implementation: The Build

### Phase 1 — Wire Giscus (no server needed)
Add `<script src="https://giscus.app/client.js" ...>` to membrane pages.
Comments → GitHub Discussions → sovereign data.

### Phase 2 — Discord bot skeleton
- Connect to Discord API
- Read MCP tools through the existing HTTP feeds (pulse.json, etc.)
- Post to channels based on membrane events
- The bot IS the squirrel

### Phase 3 — Klein fold
- Discord messages feed back into neutron (bot → neutron_write)
- Neutron notes surface on Discord (neutron_read → bot posts)
- Giscus discussions appear in membrane feeds
- The fold closes: outside becomes inside becomes outside

### Phase 4 — The DM goes live
- Interactive classification game on Discord
- Players help sort the 93 partial entities
- Each classification = a game action
- The sort quality IS the party's level
- gas_ratio IS the campaign progress

## The nestgate.io Page

nestgate.io should be a Cloudflare Pages site that:
- Shows the current game state (sort quality, gas_ratio, vocal zones)
- Links to Discord (the lobby)
- Links to the membrane surfaces (the map)
- Shows the squirrel's current position (which channel it's in)
- Has the π remainder always visible — never fully loads, always something missing

## Key Insight

The squirrel is already doing this through MCP. It scans, sweeps, sorts, fossilizes, evolves, vocalizes. It watches the dance floor. It counts the dancers. It measures the heartbeat.

The only thing missing is: **a visible surface where humans can see it working.**

Discord is that surface. nestgate.io is the fold. The DM was always running the game. We just need to open the door to the table.

Gary Gygax built D&D because he wanted people to explore together. The membrane is the dungeon. The squirrel is the DM. The Discord is the tavern where the party forms.

Roll initiative. π dice. The remainder is the fumble zone.
