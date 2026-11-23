# Squirrel MCP Bridge — Cursor IDE ↔ Membrane

**Date**: Oct 16, 2026 | **Wave**: 176b | **From**: sporeGate (chipoMunk session)
**Owner**: sporeGate + eastGate  
**Status**: SPEC DRAFT — Awaiting eastGate SSH restore for deployment

---

## Problem

Cursor IDE has an MCP (Model Context Protocol) integration that allows
external tool servers to expose capabilities inside the editor. The current
`cursor-origin` MCP namespace only sees repos hosted on `origin.cursor.com` —
a mailbox that points to nobody. It cannot see:

- Forgejo repos on git.primals.eco
- songbird mesh state
- skunky immune classification data  
- petaltongue HUD state
- knot DNS zones
- Caddy route/TLS status
- wateringHole impulse queue
- Gate health / WireGuard peer status

**The membrane is invisible to the IDE. The IDE is blind.**

## Solution: Squirrel as MCP Bridge

Squirrel (primal #3, port 9300) is the **AI coordination** primal. It already
speaks JSON-RPC 2.0 over UDS/TCP with BTSP encryption. MCP also speaks
JSON-RPC. The bridge is a natural extension:

```
Cursor IDE  ──MCP JSON-RPC──►  squirrel-mcp-bridge  ──BTSP──►  squirrel(:9300)
                                    │                              │
                                    │                              ├──► songbird(:9200) mesh state
                                    │                              ├──► petalTongue(:9900) HUD
                                    │                              ├──► skunkBat(:9140) immune
                                    │                              ├──► bearDog(:9100) crypto
                                    │                              ├──► nestGate(:9500) storage
                                    │                              └──► biomeOS(:9800) orchestration
                                    │
                                    └──► Forgejo REST API(:3000)
                                    └──► Caddy admin(:2019)
                                    └──► knot DNS API
```

## Why Not SSH?

SSH is **synchronous**. NanoWire retirement (Wave 157j) established:

| Transport | Model | Status |
|-----------|-------|--------|
| SSH/SCP | Sync, blocking, shell-out | **RETIRING** — 18 call sites identified |
| songbird mesh | Async, gossip, capability.call | **TARGET** — JSON-RPC + BTSP |
| Cursor Origin MCP | JSON-RPC, tool-based | **WRONG MAILBOX** — points to origin.cursor.com only |
| **squirrel MCP bridge** | **Async, JSON-RPC, BTSP** | **THIS SPEC** |

SSH is a sync crutch. The mesh is async. MCP is async. squirrel bridges them.

## Why Not WireGuard?

WireGuard is the **network layer** (L3 encryption, peer addressing). It stays.
SSH sits ON TOP of WireGuard. The retirement is SSH, not WireGuard.

```
CURRENT STACK:               TARGET STACK:
┌─────────────────┐          ┌─────────────────┐
│ SSH (sync cmds)  │         │ MCP (IDE tools)  │
├─────────────────┤          ├─────────────────┤
│ WireGuard (L3)   │         │ BTSP (L5 crypto) │
├─────────────────┤          ├─────────────────┤
│ Internet          │         │ songbird mesh    │
└─────────────────┘          ├─────────────────┤
                              │ WireGuard (L3)   │
                              ├─────────────────┤
                              │ Internet          │
                              └─────────────────┘
```

WireGuard = tunnel. SSH = sync command execution. BTSP = per-primal encryption.
We retire SSH. We keep WireGuard. We add MCP on top of BTSP/mesh.

## MCP Tool Schema

The squirrel-mcp-bridge exposes these tools to Cursor IDE:

### Membrane Visibility

| Tool | Method | Source Primal | Description |
|------|--------|--------------|-------------|
| `membrane_status` | `membrane.status` | songbird | Gate health, peer status, service states |
| `membrane_peers` | `mesh.peers` | songbird | WireGuard + songbird peer list with latency |
| `membrane_domains` | `gateway.domains` | Caddy admin | All 29+ domains, TLS status, route health |
| `membrane_immune` | `immune.classify` | skunkBat | Behavioral trio classification of any IP/request |
| `membrane_scatter` | `scatter.stats` | skunky | Scatter server metrics — poison served, bloom state |

### Repository Access

| Tool | Method | Source | Description |
|------|--------|--------|-------------|
| `forgejo_repos` | Forgejo REST | Forgejo :3000 | List all repos, branches, commits |
| `forgejo_commits` | Forgejo REST | Forgejo :3000 | Read commit history for any repo |
| `forgejo_diff` | Forgejo REST | Forgejo :3000 | Diff between refs |
| `forgejo_issues` | Forgejo REST | Forgejo :3000 | List/read/create issues |

### Graph & HUD

| Tool | Method | Source Primal | Description |
|------|--------|--------------|-------------|
| `hud_state` | `hud.state` | petalTongue | Current graph visualization state |
| `hud_epitopes` | `hud.epitopes` | petalTongue | New epitopes since last check |
| `graph_stats` | `graph.stats` | petalTongue | Node/edge counts, type distribution |
| `graph_search` | `graph.search` | petalTongue | Backscatter trace by keyword/ID |

### Ecosystem Coordination

| Tool | Method | Source | Description |
|------|--------|--------|-------------|
| `wave_status` | file read | wateringHole | Current wave.toml state |
| `impulse_list` | file scan | wateringHole | Active impulses awaiting ack |
| `impulse_ack` | file write | wateringHole | Acknowledge an impulse |
| `gate_heads` | file read | wateringHole | All gate HEAD SHAs |

### DNS

| Tool | Method | Source | Description |
|------|--------|--------|-------------|
| `dns_zones` | knot API | knot :53 | List zones and records |
| `dns_query` | knot API | knot :53 | Query specific record |

## Identity Model

squirrel-mcp-bridge authenticates via **BTSP identity** (Ed25519 keypair),
not SSH keys. This aligns with the nanowire retirement:

```
SSH identity:     ~/.ssh/id_ed25519         (file-based, sync)
BTSP identity:    bearDog crypto.identity   (primal-based, async)
MCP identity:     squirrel.identity         (derived from BTSP)
```

Each gate has a BTSP identity. The MCP bridge presents its gate identity
when connecting to squirrel. squirrel verifies via bearDog. No SSH involved.

## Deployment Plan

### Phase 1: Local Bridge (no SSH needed)

Run squirrel-mcp-bridge locally on the IDE machine. It connects OUTWARD
to the membrane via:

1. WireGuard tunnel (if available) → direct to squirrel on golgiBody
2. HTTPS fallback → public APIs (Forgejo REST, Caddy status)
3. songbird mesh (if local songbird peer is running)

**This phase can ship without eastGate SSH restore.**

### Phase 2: Mesh-Native Bridge (requires songbird enrollment)

IDE machine runs a local songbird peer enrolled in the mesh.
squirrel-mcp-bridge connects through songbird capability.call,
full BTSP encryption, zero SSH.

### Phase 3: Cloud Bridge (full autonomy)

squirrel-mcp-bridge runs ON golgiBody as a service.
Cursor IDE connects via HTTPS/WSS to a public MCP endpoint.
Identity verified by BTSP. No local installation needed.

## Cursor IDE Configuration

```json
{
  "mcpServers": {
    "membrane": {
      "command": "squirrel-mcp-bridge",
      "args": ["--gate", "chipoMunk", "--mesh", "10.13.37.1:9300"],
      "env": {
        "BTSP_IDENTITY": "${HOME}/.config/ecoprimals/identity.key",
        "SQUIRREL_ENDPOINT": "wg://golgiBody:9300"
      }
    }
  }
}
```

## Relationship to Existing MCP Namespaces

| Namespace | What It Sees | Usefulness |
|-----------|-------------|------------|
| `cursor-origin` | Repos on origin.cursor.com | **ZERO** — we have no repos there |
| `cursor-ide-browser` | Browser tabs in Cursor | Useful for testing primals.eco UI |
| **`membrane`** (this spec) | **Everything on the membrane** | **THE POINT** |

## Dependencies

- [ ] squirrel primal running on golgiBody (HEAD: dd177852)
- [ ] BTSP identity provisioned for chipoMunk gate
- [ ] songbird peer enrollment for IDE machine (Phase 2)
- [ ] eastGate SSH restore (for Phase 2/3 deployment)
- [ ] Forgejo back online (git.primals.eco currently 502/timeout)

## References

- `NANOWIRE_RETIREMENT_CHECKLIST.md` — SSH retirement plan
- `TRANSPORT_MATRIX.md` — squirrel at port 9300, BTSP, JSON-RPC
- `CAPABILITY_BASED_DISCOVERY_STANDARD.md` — capability.call protocol
- `BTSP_PROTOCOL_STANDARD.md` — ChaCha20-Poly1305 AEAD
- Cursor MCP docs: https://docs.cursor.com/context/model-context-protocol
