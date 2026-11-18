SPDX-License-Identifier: AGPL-3.0-or-later

# Capability domain registry

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-04-06 |
| **Status** | Canonical |
| **Purpose** | Single source of truth for `by_capability` domain names in deploy graphs across the ecoPrimals ecosystem. |

Deploy graphs use `by_capability` to route discovery at graph execution time. biomeOS resolves each capability domain name to the primal that implements that surface. This registry fixes the canonical string for each primal so springs and graphs do not drift.

**Companion artifact**: `capability_registry.toml` (this directory) is the method-level registry listing every `domain.operation` method, its description, domain, and canonical provider. It is sync-tested against `primalSpring/niche.rs` in CI.

## Canonical domains

| Domain | Primal | Description | Capabilities (examples) |
|--------|--------|-------------|------------------------|
| `orchestration` | biomeOS | Neural API orchestration | `capability.discover`, `graph.deploy`, `graph.list` |
| `security` | BearDog | Cryptographic identity + encryption | `crypto.sign`, `crypto.verify`, `crypto.encrypt` |
| `discovery` | Songbird | Peer discovery + mesh networking | `discovery.find_primals`, `discovery.announce` |
| `storage` | NestGate | Content-addressed persistent storage | `storage.store`, `storage.retrieve`, `storage.list` |
| `compute` | ToadStool | Hardware dispatch (GPU/NPU/CPU) | `compute.dispatch.submit`, `compute.dispatch.execute` |
| `math` | barraCuda | Pure math primitives (WGSL shaders) | `math.linalg`, `math.stats`, `math.spectral` |
| `shader_compile` | coralReef | Sovereign shader compilation | `shader.compile`, `shader.validate` |
| `ai` | Squirrel | AI model bridge | `ai.query`, `ai.list_providers`, `mcp.tools.list` |
| `visualization` | petalTongue | Grammar-based rendering | `visualization.render.dashboard`, `visualization.render.scene` |
| `provenance` | rhizoCrypt | Ephemeral DAG (present time) | `dag.create_session`, `dag.append_event`, `dag.dehydrate` |
| `ledger` | loamSpine | Immutable permanence (past time) | `commit.session`, `commit.entry`, `entry.verify` |
| `attribution` | sweetGrass | Semantic braids (PROV-O) | `braid.create`, `attribution.chain`, `braid.commit`, `provenance.graph` |
| `coordination` | primalSpring | Composition validation + deploy | `coordination.validate_composition`, `composition.nucleus_health` |

## Spring-specific capability domains

Springs define their own domain names for capabilities that belong to a spring, not to a shared primal (for example: `ecology` for wetSpring, `geology` for groundSpring, `physics` for hotSpring, `game` for ludoSpring). Those names are local to the spring; they still must not collide with the canonical table above when the same deploy graph spans multiple surfaces.

## What not to do

- Do not promote internal operation names to domain names when a registered domain already exists (for example, do not use `dag` instead of `provenance` for rhizoCrypt).
- Do not use `provenance` for sweetGrass; that domain is reserved for rhizoCrypt. sweetGrass is `attribution`.
- Do not invent new top-level domain strings in deploy graphs without adding them here first.

## Registering a new domain

1. Add a row to the canonical table in this file with domain, primal, short description, and representative capability IDs.
2. Update any deploy graphs or biomeOS routing tables that should resolve the new domain, and cross-reference this document in review so reviewers can confirm the name is registered.
