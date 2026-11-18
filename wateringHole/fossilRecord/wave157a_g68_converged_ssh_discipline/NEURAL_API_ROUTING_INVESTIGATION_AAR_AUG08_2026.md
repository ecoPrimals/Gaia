# AAR: Neural API Routing Investigation — Why capability.call Times Out

**Date**: August 8, 2026
**Gate**: westGate (155f)
**Team**: Hardware / Overwatch
**Context**: Attempted to test and fix `capability.call` routing after cascading
Wave 157a routing spec + biomeOS routing fix from golgiBody.

## What We Did

After cascading from Forgejo (22 repos pulled, 20 fast-forwarded, biomeOS
and primalSpring rebased), we rebuilt biomeOS with the routing fix commit
`6f60cccf` (timeout constant change + capability_registry.toml additions)
and deployed it to westGate's neural-api-tower systemd service.

Testing revealed that `health.check` works through the neural-api, but
ALL `capability.call` requests time out with no response.

## Root Causes Found

### 1. File Descriptor Leak — Socket Exhaustion

The biomeOS neural-api process leaks Unix socket file descriptors at an
extreme rate. Within 2 minutes of startup, the process consumes 50,000+
FDs. At the default soft limit of 1024, the process hits "Too many open
files" within seconds, silently dropping all new connections.

**Source of the leak**: The auto-discovery background sweep
(`discover_and_register_primals()`, every 30s) probes all primal sockets
via `probe_unix_socket_capabilities_list()`. Each probe opens 1-2 Unix
stream connections per primal. With 24+ sockets in the membrane directory,
that's ~50 connections per sweep — and the connections are never properly
released. Additionally, the stale-registration prune sweep opens health
check connections to all 93 registered endpoints every 60s.

**Workaround applied**: `LimitNOFILE=1048576` in the systemd service file.
This prevents the process from crashing but does NOT fix the leak. The
leak itself is a biomeOS bug requiring a fix in `AtomicClient` connection
lifecycle or the discovery sweep's socket handling.

### 2. Tower Atomic Relay Consumes Timeout Budget

The `capability.call` dispatch path in `dispatch/mod.rs` follows this order:

```
1. Signal graph interception (tier: tower/nest/node/meta)
2. Tower Atomic relay — forward to songBird as primary endpoint
3. Translation registry lookup
4. Direct discovery fallback
```

Step 2 is the bottleneck. When `capability.call({capability: "spine",
operation: "status"})` arrives, the router:

a. Discovers Tower Atomic (bearDog + songBird)
b. Forwards `spine.status` to songBird's socket
c. songBird doesn't know `spine.status` — the BTSP handshake + JSON-RPC
   fallback cycle consumes the full `CAPABILITY_CALL_TIMEOUT` (15s)
d. Only THEN does it fall through to translation/direct routing
e. By this point, the caller's timeout has expired

This affects ALL non-Tower capabilities: provenance trio (spine, dag,
braid, content), node operations (compute, inference), and any domain
not natively handled by songBird.

### 3. Monolithic Capability Registry

The `capability_registry.toml` in biomeOS config is a 1,316-line
centralized mapping of every method across every primal. This creates
several architectural problems:

- **Missing entries cause silent failures**: `spine.status`, `spine.list`,
  `entry.list`, `dag.session.list`, and many other valid primal methods
  have no translation entry. Without an entry, the router can't find the
  target primal and falls into the Tower relay path (which times out).

- **Stale entries cause mis-routing**: Graph node names (e.g.,
  `check_nestgate`, `dehydrate_session`, `compute-descriptors`) are
  registered as "primals" during graph discovery. The prune sweep then
  health-checks these phantom endpoints, can't reach them (they're not
  real sockets), and eventually prunes them — taking collateral real
  registrations with them.

- **Dual semantics conflict**: Some entries use `provenance.create_braid`
  (semantic), others use `braid.create` (direct). The routing spec says
  both should work, but the translation registry only has one or the other.
  A caller using the "wrong" form gets routed to Tower relay → timeout.

- **No primal ownership**: A centralized registry means biomeOS must know
  the full method surface of every primal a priori. When sweetGrass adds
  `braid.batch_create` or loamSpine adds `spine.list`, somebody must
  manually edit biomeOS's `capability_registry.toml`. This doesn't scale.

## What Should Change (Architecture)

### Each Primal Owns Its Own Registry

Instead of biomeOS maintaining a monolithic `capability_registry.toml`,
each primal should declare its own capabilities and routing metadata:

```toml
# In loamSpine's own config:
[primal]
name = "loamspine"
domain = "permanence"

[capabilities]
"spine.create" = {}
"spine.get" = {}
"spine.list" = {}
"spine.seal" = {}
"entry.append" = {}
"entry.get" = {}
"entry.get_tip" = {}
"entry.list" = {}
"session.commit" = {}
# ... all methods loamSpine actually implements
```

biomeOS discovers these at runtime via `primal.announce` or
`capabilities.list`, builds its routing table dynamically, and never
needs a static registry for method-to-primal mapping.

### biomeOS Understands Atomic Routing, Not Method Routing

biomeOS should know about **atomic composition** (Tower = security +
discovery, Nest = Tower + storage + provenance, Node = Tower + compute)
and route at the **domain level**, not the **method level**.

When `capability.call({capability: "spine", operation: "status"})` arrives:
1. biomeOS knows `spine` domain → `loamspine` primal (from auto-discovery)
2. biomeOS forwards `spine.status` directly to loamSpine's socket
3. No Tower relay, no translation lookup, no 15s timeout

The Tower relay should ONLY activate for capabilities that belong to the
Tower tier (security, discovery, crypto) or when cross-gate routing is
needed (songBird handles mesh forwarding).

### Fix the Dispatch Order

Regardless of registry architecture, the dispatch order should be:

```
1. Translation registry (direct known routes — fast path)
2. Auto-discovered domain → primal mapping (from capabilities.list)
3. Signal graph interception
4. Tower Atomic relay (ONLY for Tower-scoped capabilities)
5. Fallback discovery
```

Currently step 2 (Tower relay) runs before step 1 (translation), eating
the timeout budget for every non-Tower capability.

## What We Reverted

All biomeOS changes have been reverted. The running binary is from
upstream HEAD (`f49cc75b`). Changes we tried and backed out:

1. **dispatch/mod.rs**: Moved translation registry check before Tower
   relay. This helped for capabilities WITH translations but didn't fix
   capabilities without them (which is most provenance methods).

2. **capability_registry.toml**: Added `spine.status`, `spine.list`,
   `entry.list`, `session.commit`, `anchor.*`, `slice.*` translations.
   This would have worked but is the wrong approach — it perpetuates the
   monolithic registry anti-pattern.

## What We Kept

1. **`LimitNOFILE=1048576`** in `neural-api-tower.service` — this is a
   necessary workaround for the FD leak until biomeOS fixes it. Without
   it, the process crashes within seconds.

2. **All cascade-fetched repo updates** — 20 repos pulled to latest HEAD
   from golgiBody. The code is at upstream HEAD, only the service config
   has our workaround.

## Recommendations for biomeOS Team

1. **Fix the FD leak in auto-discovery sweep**: `AtomicClient` connections
   opened during `discover_and_register_primals()` are not being dropped.
   50,000+ leaked FDs in 2 minutes.

2. **Reverse the dispatch order**: Translation/discovery should resolve
   before Tower relay. Tower relay is a fallback, not the primary path.

3. **Move to per-primal capability declarations**: Each primal owns its
   method surface. biomeOS aggregates at runtime via `primal.announce` +
   `capabilities.list`. The monolithic `capability_registry.toml` becomes
   a bootstrap-only fallback, not the source of truth.

4. **Scope Tower relay to Tower capabilities only**: `spine.status` should
   never touch songBird. Domain → tier classification already exists in
   `composition.rs` — use it to gate the Tower relay.

## Status

- **13/13 primals alive** on westGate (all responding on direct sockets)
- **Provenance chain verified**: 990,648 events, 244 spine entries
- **Direct socket routing works**: All provenance queries succeed via
  Stage 1 (direct UDS). The data is correct. The routing layer is broken.
- **Neural API routing broken**: `capability.call` times out for all
  non-health methods. Stage 2 is not operational.
- **biomeOS at upstream HEAD**: `f49cc75b`, no local modifications
