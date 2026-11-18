# Scene Format Reference for petalTongue

**Version**: 1.0.0
**Date**: April 2, 2026
**Audience**: Any primal or spring sending game scenes, narrative scenes, or soundscapes to petalTongue
**Status**: Active Standard

---

## Overview

petalTongue renders three scene-oriented DataBinding variants via `visualization.render`, `visualization.render.scene`, or `visualization.render.dashboard`:

| Variant | Channel Type | Use Case |
|---------|-------------|----------|
| **GameScene** | `game_scene` | 2D tilemaps, sprites, entities, RPGPT narrative |
| **Soundscape** | `soundscape` | Layered audio synthesis (ambient, game audio, sonification) |
| **Audio Synthesize** | IPC: `audio.synthesize` | On-demand PCM/WAV generation from soundscape definitions |

All scene JSON is sent inside the `scene` or `definition` field of the DataBinding payload.

---

## GameScene Format

### Tilemap/Sprite Scene (2D Game World)

Used by **ludoSpring** for game rendering and **primalSpring** for spatial compositions.

```json
{
  "channel_type": "game_scene",
  "id": "dungeon_level_1",
  "label": "Dungeon Level 1",
  "scene": {
    "tilemap": {
      "dimensions": [16, 12],
      "tile_size": [16.0, 16.0],
      "origin": [0.0, 0.0],
      "tiles": [
        {"tile_type": 0, "color": [0, 0, 0, 0], "solid": false},
        {"tile_type": 1, "color": [0, 0, 0, 0], "solid": true}
      ],
      "palette": [[0, 128, 0, 255], [64, 64, 64, 255], [0, 0, 200, 255]]
    },
    "sprites": [
      {
        "id": "chest_01",
        "position": [24.0, 8.0],
        "size": [8.0, 8.0],
        "tint": [255, 200, 50, 255],
        "z_order": 5,
        "visible": true,
        "label": "Treasure Chest",
        "texture_id": null,
        "rotation": 0.0
      }
    ],
    "entities": [
      {
        "id": "hero",
        "entity_type": "player",
        "position": [16.0, 16.0],
        "velocity": [2.0, 0.0],
        "health": 0.85,
        "color": [0, 200, 255, 255],
        "size": [2.0, 2.0],
        "label": "Warrior"
      },
      {
        "id": "goblin_1",
        "entity_type": "enemy",
        "position": [30.0, 20.0],
        "velocity": [0.0, 0.0],
        "health": 0.3,
        "color": [200, 50, 50, 255],
        "size": [1.5, 1.5],
        "label": "Goblin Scout"
      }
    ],
    "camera_center": [20.0, 16.0],
    "camera_zoom": 1.5
  }
}
```

### Field Reference: Tilemap

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `dimensions` | `[u32, u32]` | Yes | `[columns, rows]` |
| `tile_size` | `[f64, f64]` | Yes | Width and height of each tile in world units |
| `origin` | `[f64, f64]` | Yes | World position of top-left corner |
| `tiles` | `Tile[]` | Yes | Flat array of tiles, length = cols * rows |
| `palette` | `[u8; 4][]` | Yes | RGBA colors indexed by `tile_type` |

### Field Reference: Tile

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `tile_type` | `u32` | Yes | — |
| `color` | `[u8; 4]` | No | `[0,0,0,0]` (uses palette) |
| `solid` | `bool` | No | `false` |

### Field Reference: Sprite

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `id` | `String` | Yes | — |
| `position` | `[f64, f64]` | Yes | — |
| `size` | `[f64, f64]` | Yes | — |
| `tint` | `[u8; 4]` | No | `[255,255,255,255]` |
| `z_order` | `i32` | No | `0` |
| `visible` | `bool` | No | `true` |
| `label` | `String?` | No | `null` |
| `texture_id` | `String?` | No | `null` (color fallback) |
| `rotation` | `f64` | No | `0.0` |

### Field Reference: GameEntity

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `id` | `String` | Yes | — |
| `entity_type` | `String` | Yes | — |
| `position` | `[f64, f64]` | Yes | — |
| `velocity` | `[f64, f64]` | No | `[0.0, 0.0]` |
| `health` | `f64?` | No | `null` (no health bar) |
| `color` | `[u8; 4]` | No | `[255,255,255,255]` |
| `size` | `[f64, f64]` | No | `[1.0, 1.0]` |
| `label` | `String?` | No | `null` |

**Entity type icons** (rendered as text glyphs when no texture available):

| `entity_type` | Icon | Color hint |
|---------------|------|------------|
| `player` | ◆ | Blue tones |
| `enemy` | ▲ | Red tones |
| `npc` | ● | Green tones |
| `item` | ★ | Yellow tones |
| `projectile` | • | White |
| Other | ■ | As specified |

---

## Narrative Scene Format (RPGPT / esotericWebb)

petalTongue auto-detects narrative scenes by the presence of `description`, `node`, or `npcs` fields. No `tilemap` or `sprites` fields needed.

### Dialogue Scene

Used by **esotericWebb** for CRPG narrative and **ludoSpring** for DialogueTree/NarrationStream channel types.

```json
{
  "channel_type": "game_scene",
  "id": "tavern_scene",
  "label": "The Rusty Anchor",
  "scene": {
    "scene_type": "dialogue_tree",
    "node": "tavern_entrance",
    "description": "You push open the heavy oak door. Warm light and the smell of roasting meat greet you. A bard plays a melancholy tune in the corner.",
    "npcs": [
      {"name": "Innkeeper", "status": "friendly", "health": 1.0},
      {"name": "Mysterious Stranger", "status": "present"},
      {"name": "Wounded Guard", "status": "friendly", "health": 0.4}
    ],
    "turn": 3,
    "is_ending": false,
    "choices": [
      "Talk to the innkeeper",
      "Approach the mysterious stranger",
      "Help the wounded guard",
      "Order a drink and listen"
    ]
  }
}
```

### Combat Scene

```json
{
  "channel_type": "game_scene",
  "id": "goblin_ambush",
  "label": "Goblin Ambush",
  "scene": {
    "scene_type": "combat_grid",
    "description": "Three goblins emerge from the underbrush!",
    "entities": [
      {"id": "hero", "entity_type": "player", "position": [3.0, 2.0], "label": "Hero"},
      {"id": "goblin_1", "entity_type": "enemy", "position": [5.0, 4.0], "label": "Goblin"},
      {"id": "goblin_2", "entity_type": "enemy", "position": [6.0, 3.0], "label": "Goblin"},
      {"id": "goblin_3", "entity_type": "enemy", "position": [4.0, 5.0], "label": "Goblin Archer"}
    ],
    "npcs": [],
    "turn": 1
  }
}
```

### Field Reference: Narrative Scene

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `scene_type` | `String` | No | Auto-detected |
| `node` | `String` | No | `""` |
| `description` | `String` | No | `""` |
| `npcs` | `NPC[]` or `String[]` | No | `[]` |
| `turn` | `u32` | No | `0` |
| `is_ending` | `bool` | No | `false` |
| `choices` | `String[]` | No | `[]` |
| `entities` | `Object[]` | No | `[]` (for combat grid) |
| `terrain` | `Object[]` | No | `[]` (for combat grid) |

**`scene_type` values** (explicit or auto-detected):

| Value | Rendering |
|-------|-----------|
| `dialogue_tree` / `dialogue` | Description + NPC list + choices |
| `combat_grid` / `combat` | Grid with positioned entities |
| `exploration_map` / `exploration` | Map-style (future) |
| `narration` / `narration_stream` | Scrollable text narrative |

**Auto-detection** when `scene_type` is omitted:
- Has `terrain` or positioned entities → `combat`
- Has `choices` or `npcs` → `dialogue`
- Otherwise → `narration`

### NPC Object

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `name` | `String` | Yes | — |
| `status` | `String` | No | `"present"` |
| `health` | `f64?` | No | `null` (no bar) |

**NPC status rendering**:

| Status | Color |
|--------|-------|
| `hostile` | Red |
| `friendly` | Green |
| `dead` | Gray |
| Other | Light gray |

---

## Soundscape Format

Used for ambient audio, game audio synthesis, and data sonification.

```json
{
  "channel_type": "soundscape",
  "id": "forest_ambient",
  "label": "Forest Ambience",
  "definition": {
    "name": "Forest at Dusk",
    "duration_secs": 60.0,
    "layers": [
      {
        "id": "wind",
        "waveform": "white_noise",
        "frequency": 200.0,
        "amplitude": 0.3,
        "duration_secs": 60.0,
        "pan": -0.5,
        "fade_in_secs": 3.0,
        "fade_out_secs": 5.0,
        "offset_secs": 0.0
      },
      {
        "id": "birdsong",
        "waveform": "sine",
        "frequency": 800.0,
        "amplitude": 0.6,
        "duration_secs": 10.0,
        "pan": 0.7,
        "offset_secs": 5.0
      },
      {
        "id": "creek",
        "waveform": "triangle",
        "frequency": 400.0,
        "amplitude": 0.4,
        "duration_secs": 60.0,
        "pan": 0.0
      }
    ],
    "master_amplitude": 0.8,
    "sample_rate": 44100
  }
}
```

### Field Reference: Soundscape

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `name` | `String` | Yes | — |
| `duration_secs` | `f64` | Yes | — |
| `layers` | `SoundLayer[]` | Yes | — |
| `master_amplitude` | `f64` | No | `0.8` |
| `sample_rate` | `u32` | No | `44100` |

### Field Reference: SoundLayer

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `id` | `String` | Yes | — |
| `waveform` | `String` | Yes | — |
| `frequency` | `f64` | Yes | Hz |
| `amplitude` | `f64` | Yes | `0.0` to `1.0` |
| `duration_secs` | `f64` | Yes | — |
| `pan` | `f64` | No | `0.0` (center) |
| `fade_in_secs` | `f64` | No | `0.0` |
| `fade_out_secs` | `f64` | No | `0.0` |
| `offset_secs` | `f64` | No | `0.0` |

**Waveform types**: `sine`, `square`, `sawtooth`, `triangle`, `white_noise`

**Pan**: `-1.0` = full left, `0.0` = center, `1.0` = full right

---

## Audio Synthesis via IPC

petalTongue exposes `audio.synthesize` for on-demand stereo PCM generation:

```json
{
  "jsonrpc": "2.0",
  "method": "audio.synthesize",
  "params": {
    "definition": {
      "name": "alert_tone",
      "duration_secs": 0.5,
      "layers": [
        {"id": "beep", "waveform": "sine", "frequency": 880.0, "amplitude": 0.7, "duration_secs": 0.5}
      ]
    },
    "format": "wav_base64"
  },
  "id": 1
}
```

**Format options**:

| Format | Returns |
|--------|---------|
| `metadata` (default) | `sample_rate`, `channels`, `duration_secs`, `num_samples`, `layers` |
| `wav_base64` | All metadata + `wav_base64` (base64-encoded 16-bit stereo WAV) |

---

## Consumer Guidance

### ludoSpring

Map your 15 `GameChannelType` variants to `DataBinding` types:

| GameChannelType | DataBinding | Notes |
|-----------------|-------------|-------|
| `DialogueTree` | `game_scene` with `scene_type: "dialogue_tree"` | Include `choices`, `npcs`, `description` |
| `CombatGrid` | `game_scene` with `scene_type: "combat_grid"` | Include positioned `entities` |
| `ExplorationMap` | `game_scene` with tilemap + entities | Full tilemap scene |
| `NpcStatus` | `game_scene` with `npcs` array | Health bars rendered automatically |
| `NarrationStream` | `game_scene` with `scene_type: "narration"` | Description text only |
| `CharacterSheet` | `game_scene` with `scene_type: "dialogue"` | NPC-as-character view |
| `HealthBar` / `Gauge` | `gauge` DataBinding | Standard gauge rendering |
| `GameAudio` | `soundscape` DataBinding | Full synthesis |
| `Inventory` | `bar` DataBinding | Category/quantity chart |

Wire `interaction.poll` into your game tick loop to close the SAME DAVE sensor loop.

### esotericWebb

Evolve scene payloads to include richer fields:

```json
{
  "node": "scene_7",
  "scene_type": "dialogue_tree",
  "description": "The path forks ahead...",
  "npcs": [
    {"name": "Old Hermit", "status": "friendly", "health": 0.6}
  ],
  "choices": ["Take the left path", "Take the right path", "Ask the hermit"],
  "turn": 5,
  "is_ending": false
}
```

Call `interaction.poll` in the narrative loop and map `InputEvent` to `PlayerInput` for bidirectional play.

### primalSpring

Standardize grammar/dashboard payload shapes between experiments. Use `visualization.render.scene` for spatial compositions and `visualization.render.dashboard` for multi-panel layouts.

---

## Related Documents

| Document | Location |
|----------|----------|
| Visualization Integration Guide | `wateringHole/petaltongue/VISUALIZATION_INTEGRATION_GUIDE.md` |
| Grammar of Graphics Architecture | `petalTongue/specs/GRAMMAR_OF_GRAPHICS_ARCHITECTURE.md` |
| Semantic Method Naming Standard | `wateringHole/SEMANTIC_METHOD_NAMING_STANDARD.md` |
| Universal IPC Standard V3 | `wateringHole/UNIVERSAL_IPC_STANDARD_V3.md` |
| Capability-Based Discovery | `wateringHole/CAPABILITY_BASED_DISCOVERY_STANDARD.md` |
