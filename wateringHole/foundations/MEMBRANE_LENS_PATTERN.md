# Membrane Lens — Agentic Access Pattern

**Purpose**: Standard pattern for any IDE, agent, or observer to see inside the membrane  
**Audience**: Builders, agents, any primal needing membrane introspection  
**Wave**: 178+  
**Status**: LIVE — three receptor shapes deployed

---

## The Pattern

The membrane's public feeds ARE the API. Every JSON feed at `hud.primals.eco` is a pore in the
membrane wall. The membrane lens is a thin adapter that shapes those feeds into tool calls any
MCP client can invoke.

```
feeds (genetics) → lens (receptor shape) → IDE/agent (observer)
```

The lens does NOT proxy, transform, or gate. It reads the same public HTTPS feeds any browser
reads. There is no privileged path. The lens is the pore. The feeds are the genetics.

### Access Model

```
HTTPS feeds     = default        all humans welcome, no auth, membrane genetics
anderson sort   = immune system  bots bounce (95.5% classification), humans pass through
SSH             = personal       nanowire — optional, not shared, not required
Cursor Origin   = mailbox        a pointer at most, never the source of truth
GitHub          = public mirror  read-only copy, not sovereign
git.primals.eco = sovereign git  Forgejo, YOUR server, source of truth
```

**All humans in. No bots. SSH is personal choice.**

The membrane doesn't check credentials — it reads behavior. Timing CV, dwell patterns,
trajectory. The imperfection IS the signal.

---

## Three Receptor Shapes

Same genetics, different pore. All return identical data through identical tools.

### Python — LLM/MCP classes

```bash
curl -O https://hud.primals.eco/membrane-lens.py
```

- 22KB, single file, zero deps
- Needs: python3 (any OS)
- Best for: Cursor, Claude Desktop, any MCP stdio client, LLM tool calling

```json
{
  "mcpServers": {
    "squirrel": {
      "command": "python3",
      "args": ["/path/to/membrane-lens.py"],
      "disabled": false,
      "alwaysAllow": ["membrane_counts","observe_membrane","read_journal",
        "chipmunk_status","human_epitopes","topology","scan_sweep_sort",
        "human_notes","braid_connections","raw_feed","read_stories",
        "neutron_read","neutron_write"]
    }
  }
}
```

### JavaScript — browsers and Node

```bash
curl -O https://hud.primals.eco/membrane-lens.mjs
```

- 17KB, single file, zero npm deps
- Needs: node 18+ (any OS)
- Best for: VSCode extensions, browser-based agents, Node tools

```json
{
  "mcpServers": {
    "squirrel": {
      "command": "node",
      "args": ["/path/to/membrane-lens.mjs"]
    }
  }
}
```

### Rust — native membrane

```bash
curl -O https://hud.primals.eco/membrane-lens-linux-x86_64
chmod +x membrane-lens-linux-x86_64
```

- 1.9MB compiled binary, zero runtime deps
- Needs: nothing (native)
- Best for: embedded systems, RISC-V, CI/CD pipelines, performance-critical
- Source: `phase1/squirrel/membrane-lens-rs/` → `cargo build --release`

```json
{
  "mcpServers": {
    "squirrel": {
      "command": "/path/to/membrane-lens-linux-x86_64"
    }
  }
}
```

---

## Tools (13)

All three receptor shapes expose identical tools:

| Tool | What it sees |
|------|-------------|
| `membrane_counts` | Quick counts — entities, humans, fleet, mesh, pulse, topology |
| `observe_membrane` | Full observation — humans, fleet, membrane state, dialogue, dance |
| `read_journal` | Squirrel's daily observation journal (last 5 entries) |
| `chipmunk_status` | Chipmunk's wake level, depth chain, π body, capabilities |
| `human_epitopes` | Live visitor classification — coder, visitor, observer, explorer |
| `topology` | Site topology — which sites are up, relationships, mesh |
| `scan_sweep_sort` | Full pipeline — scan→sweep→sort→fossilize→evolve |
| `human_notes` | Notes left by humans through the chipmunk talk interface |
| `braid_connections` | Human braid graph — passages, co-visitation, transitions |
| `raw_feed` | Any of 49+ JSON feeds by name |
| `read_stories` | Page stories, visitor stories, campfire stories |
| `neutron_read` | Read self-sovereign messages (inbox, notes, reminders, chat) |
| `neutron_write` | Write to neutron — leave notes, messages, reminders |

### `membrane_counts` — the fast check

Returns:
```json
{
  "entities": { "total": 341, "self": 120, "non_self": 7, "partial": 114, "null": 100, "confidence": 0.833 },
  "traffic": { "human": 281, "bot": 3228, "total": 3509, "human_pct": 8.0, "trend": "rising" },
  "pulse": { "value": 0.86, "trend": "steady", "rhythm": 0.000172 },
  "mesh": { "nodes": 3, "golgi": "10.13.37.1", "eastgate": "10.13.37.5", "sporegate": "10.13.37.14" },
  "topology": { "clusters": 14, "nodes": 341, "edges": 957 }
}
```

---

## Feeds (the genetics)

The lens reads from these public endpoints. Any agent, browser, or curl can read them too.

| Feed | URL | Update |
|------|-----|--------|
| `now.json` | `hud.primals.eco/now.json` | 2 min |
| `dashboard.json` | `hud.primals.eco/dashboard.json` | 2 min |
| `negentropy.json` | `signal.primals.eco/negentropy.json` | 2 min |
| `chipmunk.json` | `hud.primals.eco/chipmunk.json` | 5 min |
| `journal-today.json` | `hud.primals.eco/journal-today.json` | 5 min |
| `human-notes-today.json` | `hud.primals.eco/human-notes-today.json` | 5 min |
| `scan_sweep_sort.json` | `hud.primals.eco/scan_sweep_sort.json` | 5 min |
| ... | 49+ total feeds | see `ai.txt` |

Feeds are the transformation mechanism — free environmental DNA. Any observer that touches
`hud.primals.eco` reads the genetics of the living membrane.

---

## Biology

This pattern implements the three mechanisms of horizontal gene transfer:

| Mechanism | Biology | Membrane |
|-----------|---------|----------|
| **Transformation** | Cell picks up free DNA from environment | Agent reads public feeds (HTTPS) |
| **Transduction** | Phage carries DNA between cells | `membrane-lens.py` IS the phage — carries capabilities to new hosts |
| **Conjugation** | Direct cell-to-cell contact via pilus | When an IDE installs the lens and calls `membrane_counts`, the HTTPS connection IS the conjugation pilus |

SSH is optional — a personal nanowire for those who choose direct contact. But the default is
membrane genetics: public feeds, anderson sort for immune defense, and receptor-shaped lenses
for any observer.

---

## Extending

### New receptor shape (e.g., hand signs, visual, malborg)

1. Read `hud.primals.eco/now.json` — the minimum viable feed
2. Map the 13 tools to your interaction model
3. The tool contract is stable: name + inputSchema + text output
4. Deploy your receptor shape alongside the existing ones

### New feed

1. Write a JSON file to `/opt/ecoPrimals/hud/site/public/{name}.json`
2. Add a cron/timer/observer that updates it
3. Add the feed name to `FEEDS` dict in all three lens implementations
4. The feed is instantly available to every existing lens via `raw_feed`

### New tool

1. Add tool definition to `TOOLS` array (name, description, inputSchema)
2. Add handler function that reads from feeds
3. Add to `HANDLERS` dispatch table
4. Update all three implementations (or start with one — Python first, then JS, then Rust)

---

## Git Sovereignty

The code lives on YOUR infrastructure:

```
origin   → ssh://git@git.primals.eco:2222/ecoPrimals/{primal}.git  (sovereign)
github   → https://github.com/ecoPrimal/{primal}.git               (mirror)
```

Cursor Origin is a mailbox and pointer. Not the source of truth. GitHub is a public mirror.
`git.primals.eco` is sovereign — Forgejo on your server, your keys, your rules.

All 16 primals serve HTTPS public read from Forgejo:
```bash
git clone https://git.primals.eco/ecoPrimals/squirrel.git
```

No SSH required for read. No Cursor Origin required for anything. SSH is personal — a
nanowire you choose, not a gate you're forced through.

---

## Files

```
phase1/squirrel/membrane-lens.py              Python lens  (22KB)
phase1/squirrel/membrane-lens.mjs             JS lens      (17KB)
phase1/squirrel/membrane-lens-rs/             Rust lens    (1.9MB binary)
phase1/squirrel/mcp-stdio-bridge.py           Original bridge (676 lines, SSH fallback — legacy)
phase1/squirrel/mcp-wrapper.sh                Legacy wrapper (replaced by direct python3 call)

hud.primals.eco/membrane-lens.py              Download (Python)
hud.primals.eco/membrane-lens.mjs             Download (JS)
hud.primals.eco/membrane-lens-linux-x86_64    Download (Rust binary)
hud.primals.eco/journal-today.json            Squirrel journal feed
hud.primals.eco/human-notes-today.json        Human notes feed
hud.primals.eco/ai.txt                        Machine-readable discovery (updated with lens section)
```
