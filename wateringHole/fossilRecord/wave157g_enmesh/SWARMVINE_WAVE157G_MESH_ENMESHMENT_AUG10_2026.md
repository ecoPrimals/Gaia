# swarmVine — Wave 157g MESH ENMESHMENT

**Date**: August 10, 2026
**Wave**: 157g
**From**: eastGate overwatch
**Primal**: swarmVine (#16)
**Commit**: `4cd506a`
**Triggered by**: Wave 157e NUCLEUS COMPOSITION GRAPH blurb findings

---

## Summary

Addresses three critical findings from westGate overwatch validation:
1. biomeOS socket discovery ambiguity (connecting to tarpc instead of JSON-RPC)
2. Cross-gate gossip peers unreachable (no fallback transport)
3. No primal injects gossip (ant colony has no scouts)

## Changes

### 1. Announce payload disambiguation

`primal.announce` now sends three new fields:
- `"protocol": "json-rpc"` — explicit protocol identifier
- `"tarpc_socket": "...swarmvine.tarpc.sock"` — separate tarpc path
- `"gossip_port": 7800` — cross-gate TCP port

biomeOS can now unambiguously route to the JSON-RPC socket without
guessing from filesystem naming conventions.

### 2. songBird mesh relay fallback

When `spread_to_peer()` TCP direct fails, the epidemic loop now falls back
to `relay_via_songbird()` which sends a `mesh.relay` request through the
local songBird's `:7700` mesh transport. This provides cross-gate gossip
resilience when TCP 7800 is unreachable (firewall, NAT, not yet deployed).

Flow: TCP direct → fail → songBird `mesh.relay` → target peer songBird →
target peer swarmVine JSON-RPC.

### 3. endpoint.alive self-injection (ant colony scout)

swarmVine now self-injects an `endpoint.alive:{gate}` Tower gossip entry:
- On startup (immediate injection)
- Periodically (alongside eviction cycle, every 120s default)

Entry payload: `gate`, `gossip_port`, `protocol`, `version`, `pid`, `capabilities`.

This makes swarmVine the first primal to actually inject gossip entries,
creating the foundation for the ant colony pattern where other primals
will inject their own domain-specific entries.

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 137 (was 134) |
| New tests | `inject_endpoint_alive_creates_tower_entry`, `gossip_port_defaults_to_7800`, `relay_requires_songbird_socket` |
| Clippy warnings | 0 |
| All files | Under 800L |
| Cast safety | `u32::try_from` in relay response (no truncation) |

## Upstream dependencies

| Team | What swarmVine needs | Status |
|------|---------------------|--------|
| **biomeOS** | Read `protocol` + `tarpc_socket` fields from `primal.announce` | Payload ready, biomeOS code change needed |
| **songBird** | Implement `mesh.relay` method for gossip transport relay | Request format defined, songBird implementation needed |
| **Gate ops** | Verify TCP 7800 reachability between gates | Deployment task |
| **All primals** | Inject domain-specific gossip entries via swarmVine | Pattern documented, `gossip.inject` method available |

## Remaining

- songBird gossip delegation (`mesh.capabilities_announce` → swarmVine tower domain)
- tarpc streaming (true push, awaiting upstream tarpc support)
- `sourdough validate convergence` in golgi CI (sporeGate + sourDough scope)

---

*Wave 157g — ant colony scout deployed. Self-injection live. Relay fallback wired.
Announce payload unambiguous. 137 tests. 0 clippy. Primal #16 ready for mesh enmeshment.*
