# Neural API as Deployment Authority — Wave 137a

**Date**: Jul 12, 2026
**From**: eastGate overwatch
**To**: cellMembrane, biomeOS, all primal teams
**Priority**: HIGH — this replaces ad-hoc patterns with the canonical routing layer

---

## Context

The Neural API has been **live on eastGate for 23 days** (PID 2644486, musl binary,
riboCipher enforced since Wave 113). NUCLEUS is operational with 24 healthy sockets.
biomeOS v4.33 has 8,446 tests, 320+ capability translations across 27 domains, and
171 route table entries. primalSpring has 99 neural/routing tests, all passing.

**The infrastructure is built. We are not using it operationally.**

Current deployments still flow through:
- Manual `cargo build` / `plasmid.harvest` / `plasmid.fetch`
- Manual `systemctl restart` or process management
- Manual Caddy config editing
- Manual `membrane content.rebuild`

**Every one of these ad-hoc patterns has a Neural API equivalent that should replace it.**

---

## Phase 1: Make Neural API the Operational Path (NOW)

### 1.1 cellMembrane: Wire `membrane deploy` to Neural API

cellMembrane already has `plasmid.harvest`, `plasmid.fetch`, `temporal.cascade`,
`content.rebuild`. Add:

```
membrane deploy.composition <gate> <tier>    → capability.call → composition.deploy
membrane deploy.graph <gate> <graph.toml>    → capability.call → graph.execute
membrane lifecycle.status                    → capability.call → lifecycle.status
membrane deploy.resurrect <primal>           → capability.call → lifecycle.resurrect
```

This means `membrane` becomes the **CLI front-end** for the Neural API on any gate.
The routing goes through songBird mesh for cross-gate operations.

### 1.2 biomeOS: Activate LifecycleManager as Primary Supervisor

Currently: systemd manages primal processes directly.
Target: **systemd manages biomeOS only**. biomeOS LifecycleManager manages all 13 primals.

```
systemd → biomeos neural-api (one service)
              └── LifecycleManager
                    ├── bearDog (germination → active → resurrection)
                    ├── songBird
                    ├── nestGate
                    ├── ...all 13 primals
                    └── monitoring loop (10s health, exponential backoff resurrection)
```

Benefits:
- Dependency-aware restart order (bearDog before songBird before mesh)
- Composition health aggregation (tower_health, nest_health, nucleus_health)
- Graph-based deployment (rollback on failure)
- Hot-reload single primals without full restart (`composition.reload`)

### 1.3 All Primals: Use `capability.call` Instead of Direct Socket Paths

Ad-hoc pattern (current):
```rust
let socket = format!("/run/user/{}/biomeos/beardog.sock", uid);
let response = send_jsonrpc(&socket, "crypto.encrypt", params);
```

Neural API pattern (target):
```rust
let response = capability_call("crypto", "encrypt", params);
// Neural API routes to bearDog via translation table
// Works cross-gate via songBird mesh
// Weighted routing, circuit breaker, L4 adaptive
```

320+ translations already exist. Every primal method has a semantic capability name.

---

## Phase 2: Neural API Absorbs Ad-Hoc Operations

| Ad-Hoc Pattern | Neural API Replacement | Status |
|-----------------|----------------------|--------|
| `membrane content.rebuild` | `capability.call("content", "rebuild", ...)` | Translation exists |
| `membrane plasmid.fetch` | `capability.call("depot", "fetch", ...)` | Translation exists |
| `membrane temporal.cascade` | `signal.dispatch("cascade", ...)` | Signal graph needed |
| Manual Caddy config | `capability.call("gateway", "configure", ...)` | songBird drawbridge evolves |
| Manual systemctl restart | `lifecycle.resurrect` / `composition.reload` | LifecycleManager ready |
| Manual gate enrollment | `niche.deploy` with tier template | Templates exist (tower.toml, nest.toml) |
| Manual depot sync | `graph.execute` with depot sync graph | Graph template needed |

---

## Phase 3: Cross-Gate Neural API Mesh

The Neural API already supports cross-gate routing via songBird mesh:
- `capability.call` on eastGate can route to sporeGate's primals
- songBird `http.proxy` proxies JSON-RPC over mesh
- `topology.primals` discovers primals on all meshed gates

**Requirement**: Neural API must be running on every gate with NUCLEUS.

| Gate | Neural API | Action |
|------|-----------|--------|
| eastGate | **LIVE** (23 days) | Promote to systemd user service |
| sporeGate | Unknown | Deploy from pepti, start as service |
| golgiBody | Unknown | Thin-relay composition — Neural API may not be needed |
| ironGate | Unknown | Deploy from pepti, start as service |
| southGate | Unknown | Deploy from pepti, start as service |
| flockGate | Unknown | Deploy from pepti, fix mesh gap first |

---

## Validation Checklist

- [ ] `biomeos doctor` on eastGate — **DONE** (24/24 healthy, 1 expected miss: network.sock)
- [ ] primalSpring 99 neural/routing tests — **DONE** (all passing)
- [ ] `capability.call` round-trip through Neural API — pending (riboCipher signal required)
- [ ] `graph.execute nucleus_complete.toml` on eastGate — pending
- [ ] `lifecycle.status` returns all 13 primals — pending
- [ ] `composition.health` returns aggregated tier health — pending
- [ ] Cross-gate `capability.call` via songBird — pending (requires FLOCKGATE-MESH fix or LAN test)

---

## Key Insight

biomeOS is the most mature component in the ecosystem (v4.33, 8,446 tests, 88% coverage,
26 crates, 0 unsafe, 0 C deps, 0 debt markers). The Neural API has **320+ capability
translations, 171 route entries, L4 adaptive routing, composition tier awareness,
lifecycle management, and graph-based deployment**.

All of this is running. None of it is the operational deployment path.

**Wave 137a goal: every ad-hoc deployment pattern gets a Neural API equivalent.
Wave 138+: ad-hoc patterns deprecated. Neural API is the sole deployment authority.**
