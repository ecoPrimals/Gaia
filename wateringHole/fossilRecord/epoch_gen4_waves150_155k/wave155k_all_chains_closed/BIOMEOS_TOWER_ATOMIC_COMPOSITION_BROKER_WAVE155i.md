# biomeOS — Tower Atomic Composition Broker — Wave 155i

**Date**: Jul 29, 2026 | **Wave**: 155i | **From**: eastGate overwatch
**Team**: biomeOS (eastGate) | **Priority**: P0 for all multi-composition deployments
**Triggered by**: westGate Nest Atomic multi-composition AAR (`WESTGATE_NEST_ATOMIC_MULTICOMP_155i_AAR.md`)

---

## THE PROBLEM

westGate deployed Nest Atomic (8 services: Tower + Nest) — the first
multi-composition deployment. Individual primals all work (health checks,
capability ads, CAS storage, DAG events, certificates, braids). biomeOS
Neural API auto-discovered 1,704 capabilities on first boot.

**What broke**: Inter-primal communication across composition boundaries.

When nestGate enforces BTSP (`FAMILY_ID` set), direct JSON-RPC from CLI
tools or other primals fails with `-32604 BTSP authentication required`.
The signal graph executor starts but `validate_envelope` fails because
outbound calls lack BTSP sessions.

**Root cause**: biomeOS Neural API dispatches signal graph nodes via raw
JSON-RPC — it doesn't perform BTSP handshakes with target primals. In
Tower Atomic (3 co-trusted primals), this worked because bearDog/songBird/
skunkBat share transport-level trust. In multi-composition (7+ primals),
the trust boundary is real and BTSP is required.

---

## WHAT NEEDS TO EVOLVE

### N1 (P0): riboCipher Transport Framing

**Where**: `biomeos-types` or CLI transport layer

CLI tools (`biomeos nucleus ingest`) use `send_jsonrpc()` which writes raw
JSON. The Neural API rejects this: "legacy connection (no riboCipher signal)
— unsignalled connections dropped per Wave 113 policy."

**Fix**: Prepend `[0xEC, 0x01]` riboCipher signal prefix before JSON payload.
Export `write_ribocipher_jsonrpc()` from `biomeos-types` so all CLI-to-Neural-API
paths use the correct transport framing.

### N2 (P0): BTSP Session Propagation in Signal Graph Executor

**Where**: Neural API signal graph executor

When dispatching a signal graph node to a primal, the executor must:

1. Obtain a BTSP session from bearDog (`auth.issue_session`)
2. Perform BTSP handshake with the target primal
3. Execute the capability method within the authenticated session

The `connect_with_btsp()` pattern exists in `nestgate-rpc` — it already
handles the full handshake. The executor needs to adopt this pattern (or
an equivalent from the biomeOS transport layer) when the target primal
requires BTSP.

**Pattern**:
```
Signal Graph Node dispatch:
  1. Discover target primal via capability routing
  2. Check: does target require BTSP? (from capability_registry transport field)
  3. If yes: connect_with_btsp(beardog_socket, target_socket, family_id)
  4. If no: raw JSON-RPC connect
  5. Execute method within session
```

### N3: Neural API as Composition Broker (Architecture)

**The design principle**: In multi-composition deployments, primals should
NOT talk to each other directly. The Neural API brokers all cross-primal
calls:

```
CORRECT: CLI → Neural API → signal graph → primal A → primal B
WRONG:   CLI → primal A (auth fail)
```

This means the Neural API becomes the central trust broker — it holds
the BTSP session tokens and propagates them through the signal graph
execution chain. This is consistent with the neuralAPI's role as the
semantic dispatch layer.

**Signal graphs already define this topology** — the `by_capability`
routing in each TOML node specifies which primal handles each step.
The executor just needs to add BTSP-aware transport.

---

## TOWER ATOMIC INTEGRATION

The user's key insight: **biomeOS needs to work across all atomics and
compositional systems**, not just as a signal graph orchestrator that
assumes co-trusted transport.

Currently:
- Tower Atomic signal graphs (`tower.health`, `tower.mesh_status`, etc.)
  work because Tower primals share transport trust
- Nest Atomic signal graphs (`nest.store`, `nest.verify`, etc.) define
  the right topology but fail at the BTSP boundary
- Node Atomic signal graphs (`node.compute`, etc.) will have the same
  issue when deployed

**Target state**: biomeOS is composition-aware. Signal graph execution
adapts transport based on the target primal's security requirements.
The executor is the trust bridge between compositions.

---

## WHAT THE WESTGATE AAR PROVED WORKS

| Component | Status |
|-----------|--------|
| Depot binary fetch | Seamless — 11 binaries in 6 seconds |
| Tower as foundation | Stable — `After=beardog-tower.service` ordering sufficient |
| Individual primal IPC | All working — health, capabilities, CAS, DAG, certificates, braids |
| CAS on NVMe | Fast and correct — BLAKE3, dedup, byte-perfect round-trips |
| biomeOS auto-discovery | 1,704 capabilities from 17 socket endpoints — self-assembling |
| ZFS pool | ONLINE — 25.4TB + 2TB L2ARC, all 5 tiers operational |

**What did NOT work is the inter-composition boundary** — the trust
handoff between Tower security layer and Nest storage layer.

---

## SEQUENCING

```
[NOW]  N1: riboCipher transport fix in CLI paths (trivial)
[NOW]  N2: BTSP session propagation in signal graph executor (critical path)
  ↓
[THEN] Re-run nest.ingest_spore on westGate — should work end-to-end
[THEN] E2E Nest Atomic validation with signal graph dispatch
  ↓
[THEN] AlphaFold bulk ingestion via nest.ingest_dataset signal graph
```

---

## OTHER UPSTREAM ITEMS FROM AAR

| ID | Item | Owner | Priority |
|----|------|-------|----------|
| N3 | Rebuild membrane binary with gate.configure/gate.apply | cellMembrane/sporeGate | P1 |
| N4 | ZoneLabel::House1 in cellMembrane topology enum | cellMembrane | P2 |
| N5 | nestGate NESTGATE_STORAGE_PATH respect in standalone mode | nestGate | P2 |
| N6 | Tier migration wiring (NVMe→ZFS) via SubstrateTiers | nestGate | P3 |

---

*biomeOS is the nervous system. It discovered 1,704 capabilities on first boot.
Now it needs to carry trust tokens through the neural pathways — BTSP session
propagation in signal graph execution is the bridge between Tower security and
Nest storage. This is the composition broker pattern.*
