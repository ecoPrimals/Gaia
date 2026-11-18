# AAR: Nanowire → Primal Builder Evolution

**Date**: Aug 4, 2026 | **Wave**: 156b | **From**: eastGate overwatch (sporeGate)
**Status**: Phase 1 PROVEN (nanowire/SSH), Phase 2 SPEC (primal-based)

---

## What Worked

### Phase 1: Nanowire Sub-Builder (SSH Dispatch)

The current pattern is direct SSH invocation — sporeGate shells into blueGate and runs
`membrane.exe plasmid.harvest`. This is codified in `sovereign.rs`:

```rust
const SUB_BUILDERS: &[SubBuilder] = &[SubBuilder {
    gate: "blueGate",
    target: "x86_64-pc-windows-gnu",
    ssh_host: "blueGate",
    membrane_bin: "membrane.exe",
}];
```

**Proven:**
- blueGate built squirrel as a 24MB PE binary in 80s over SSH dispatch
- `sovereign.ci.trigger --primal beardog --dry-run` correctly resolves `sub_builders: [blueGate:OK]`
- SSH + WG mesh provides reliable transport (10.13.37.12)

### Root Cause Fix: Clone Path Permissions

The clone-based harvest was silently failing because `/tmp/membrane-harvest/` was owned
by `root` from a previous harvest run (membrane ran as root at some point). The
`try_clone()` function suppresses stderr (`Stdio::null()`), so the "Permission denied"
never surfaced. Fixed by `chown` + cleanup.

**Divergence noted**: `git_success()` swallows all errors. Consider logging stderr on
failure to catch permission/auth issues earlier.

## What Diverges

### SSH Dispatch Limitations

| Issue | Impact |
|-------|--------|
| **Hardcoded registry** | Adding a gate requires recompiling membrane |
| **SSH key management** | Each gate needs SSH access to every sub-builder |
| **No capability discovery** | sporeGate must know which targets each gate supports |
| **Sequential dispatch** | Sub-builders run one at a time in the loop |
| **No retry/failover** | If blueGate is down, windows-gnu simply fails |
| **No progress streaming** | sporeGate waits for full SSH command completion |
| **Result transport** | stdout parsing for structured results is fragile |

### The Pattern Name

- **Nanowire**: Direct SSH-based command dispatch. Fast, proven, brittle.
- **Primal Builder**: Capability-advertised, mesh-routed build requests. Resilient, evolvable.

## Phase 2 Spec: Primal-Based Builder Pattern

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         MESH (WireGuard)                        │
│                                                                 │
│  sporeGate                                                      │
│  ┌──────────────┐   harvest.request    ┌──────────────────┐     │
│  │ sovereign.ci  │────(songBird)───────▶│ builder primal    │     │
│  │ .trigger      │                      │ on ANY gate       │     │
│  │               │◀───(songBird)───────│ (self-registered) │     │
│  │               │   harvest.complete   └──────────────────┘     │
│  └──────────────┘                                               │
│                                                                 │
│  blueGate (windows-gnu)   biomeGate (GPU)   ironGate (musl)     │
│  ┌──────────────────┐     ┌─────────────┐   ┌──────────────┐   │
│  │ builder primal    │     │ builder      │   │ builder      │   │
│  │ caps: [win-gnu]   │     │ caps: [cuda] │   │ caps: [musl] │   │
│  │ advertises on     │     │ advertises   │   │ advertises   │   │
│  │ mesh startup      │     │ on mesh      │   │ on mesh      │   │
│  └──────────────────┘     └─────────────┘   └──────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Key Concepts

1. **Capability Advertisement**: Each gate runs a builder primal that announces its
   toolchain capabilities on mesh startup:
   ```json
   {
     "method": "builder.advertise",
     "params": {
       "gate": "blueGate",
       "targets": ["x86_64-pc-windows-gnu"],
       "toolchain_version": "1.87.0",
       "available": true
     }
   }
   ```

2. **Build Request Routing**: `sovereign.ci.trigger` publishes a `harvest.request`
   to the mesh. Any gate with matching capabilities picks it up:
   ```json
   {
     "method": "harvest.request",
     "params": {
       "primal": "beardog",
       "target": "x86_64-pc-windows-gnu",
       "commit": "abc12345",
       "requestor": "sporeGate"
     }
   }
   ```

3. **Build Completion Signal**: When a builder finishes, it publishes:
   ```json
   {
     "method": "harvest.complete",
     "params": {
       "primal": "beardog",
       "target": "x86_64-pc-windows-gnu",
       "gate": "blueGate",
       "status": "ok",
       "blake3": "...",
       "depot_pushed": true
     }
   }
   ```

4. **Foreman Pattern**: sporeGate acts as foreman — it tracks outstanding requests,
   matches them against advertised capabilities, and handles timeouts/failover.
   But any gate could be foreman; the pattern is symmetric.

### Evolution Path (Nanowire → Primal)

**Phase 2a** — Manifest-driven sub-builder registry (no recompile to add gates):
- Move `SUB_BUILDERS` from a `const` to `ecosystem_manifest.toml`:
  ```toml
  [sub_builders.blueGate]
  target = "x86_64-pc-windows-gnu"
  ssh_host = "blueGate"
  membrane_bin = "membrane.exe"

  [sub_builders.biomeGate]
  target = "x86_64-unknown-linux-gnu"
  ssh_host = "10.13.37.3"
  membrane_bin = "membrane"
  ```
- Still SSH-based, but no recompile needed.
- **Effort**: Small — move const to config, parse in manifest loader.

**Phase 2b** — Harvest request over mesh (replace SSH with songBird):
- `sovereign.ci.trigger` publishes `harvest.request` via songBird mesh broadcast
- Builder gates listen for requests matching their capabilities
- Results flow back via `harvest.complete` mesh message
- SSH fallback retained for gates not yet on mesh
- **Effort**: Medium — needs songBird pub/sub for build domain.

**Phase 2c** — Full capability advertisement + foreman:
- Gates advertise capabilities on startup
- Foreman tracks capability registry, routes requests optimally
- Parallel dispatch to multiple builders
- Retry/failover on builder failure
- Progress streaming via mesh
- **Effort**: Large — new primal or significant membrane subsystem.

### Isomorphic Deployment Benefit

The primal builder pattern is isomorphic: the same membrane binary on every gate
can both *request* and *fulfill* builds. A gate that today is a consumer can
tomorrow be a builder by simply installing the target toolchain. No SSH keys,
no config changes, no recompile.

This is the same pattern as the outer membrane / inner membrane duality:
- **Nanowire** (SSH) = outer membrane access (user-facing, direct, fragile)
- **Primal builder** = inner membrane routing (capability-based, mesh-routed, resilient)

## Immediate Actions

| ID | Action | Status |
|----|--------|--------|
| NW-01 | bearDog sovereign.ci.trigger with blueGate dispatch | RUNNING |
| NW-02 | Fix git_success() error suppression (log stderr on failure) | SPEC |
| NW-03 | Move SUB_BUILDERS to ecosystem_manifest.toml (Phase 2a) | **DONE** |
| NW-04 | Document nanowire SSH dispatch as BTSP transport variant | SPEC |
| NW-05 | Prove biomeGate as second sub-builder (linux-gnu) | PENDING |

### NW-03 Implementation Detail

The hardcoded `const SUB_BUILDERS` in `sovereign.rs` has been replaced with
`load_sub_builders()`, which reads from the manifest's `[sub_builders]` section:

```rust
fn load_sub_builders() -> Vec<ResolvedSubBuilder> {
    // Read from ecosystem_manifest.toml [sub_builders] section
    // Falls back to hardcoded blueGate if manifest unavailable
}
```

**Manifest TOML** (already present):
```toml
[sub_builders."x86_64-pc-windows-gnu"]
gate = "blueGate"
ssh_host = "blueGate"
membrane_bin = "membrane.exe"
```

**To add biomeGate** (NW-05), just add to manifest:
```toml
[sub_builders."x86_64-unknown-linux-gnu"]
gate = "biomeGate"
ssh_host = "10.13.37.3"
membrane_bin = "membrane"
```

No recompile needed. Tests pass (33/33).

## Convergence With Existing Work

- **Harvest Scheduler (CI-EVO-01)**: Already handles `harvest.request` / `harvest.queue`
  locally. Phase 2b extends this to mesh-routed requests.
- **BTSP Transport Signal**: The `0xEC 0x01` prefix works for mesh messages.
  `harvest.request` and `harvest.complete` are natural JSON-RPC payloads.
- **Neural API**: Capability-based routing is the same pattern as the neural API
  proposal — build capabilities are just another capability namespace.
- **Provenance Chain**: Build completion carries BLAKE3 hash, maintaining the
  provenance chain regardless of which gate built the binary.
