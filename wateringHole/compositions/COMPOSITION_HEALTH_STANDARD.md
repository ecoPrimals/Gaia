<!--
SPDX-License-Identifier: CC-BY-4.0
-->

# Composition health JSON-RPC standard

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-04-06 |
| **Status** | Canonical |

## Problem

`composition.*_health` method names have diverged across gen3 (primalSpring), gen4 product overlays (for example esotericWebb), and springs (for example wetSpring). This document is the single naming convention for those methods so bridges, registries, and deploy graphs stay aligned.

## Universal composition health (every NUCLEUS deployment)

These methods apply to the shared NUCLEUS stack. Implementations may live in primalSpring or biomeOS; callers discover them through the deployment’s capability surface.

| Method | Stack | Provider | Required |
|--------|-------|----------|----------|
| `composition.tower_health` | BearDog + Songbird + skunkBat | primalSpring or biomeOS | Yes |
| `composition.node_health` | Tower + ToadStool | primalSpring or biomeOS | If node present |
| `composition.nest_health` | Tower + NestGate | primalSpring or biomeOS | If nest present |
| `composition.nucleus_health` | Full NUCLEUS | primalSpring | If full NUCLEUS |

## Spring-specific composition health

Convention: `composition.{spring_name}_health` for domain health scoped to that spring.

| Method | Spring | Stack |
|--------|--------|-------|
| `composition.science_health` | wetSpring | Science pipeline + provenance |
| `composition.geology_health` | groundSpring | Geology pipeline |
| `composition.physics_health` | hotSpring | Physics pipeline |
| `composition.game_health` | ludoSpring | Game session pipeline |

## Product overlay health (gen4 products)

Convention: `composition.{product}_health` or `composition.{product}_{layer}_health`. Product overlays sit on top of universal composition; each product registers its methods in its own capability registry and exposes them through its bridge. Do not repurpose universal or spring method names for product-only surfaces.

## Response shape

Every `composition.*_health` method MUST return at least:

```json
{
  "healthy": true,
  "deploy_graph": "graph_name",
  "subsystems": { "subsystem_name": "ok" }
}
```

`healthy` is boolean. `deploy_graph` identifies the active graph. `subsystems` maps subsystem identifiers to `ok`, `degraded`, or `unavailable`. Implementations MAY add fields such as `bonding_support`, `capabilities_count`, or `science_domains`.

## Rules

- Universal method names are stable; do not rename them in new work.
- Spring methods use the spring’s domain name (`science`, `geology`, `physics`, `game`, and so on).
- Product methods use the product’s registered name and optional layer suffix.
- All methods return the minimum response shape above; optional fields must not replace or contradict it.
