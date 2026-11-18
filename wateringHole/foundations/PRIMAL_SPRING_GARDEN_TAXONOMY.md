# Primal / Spring / Garden Taxonomy

**Purpose:** Authoritative reference for the three entity layers in the ecoPrimals
ecosystem — their roles, ownership boundaries, interaction contracts, and the
co-evolution loop that drives ecosystem progress.

**Last Updated:** May 12, 2026 (Added fossilRecord as ecosystem memory layer)

---

## The Three Layers

The ecoPrimals ecosystem is organized into three layers. Each layer has a
distinct role, and the boundaries between them are enforced by convention and
tooling (zero compile-time coupling, JSON-RPC IPC, wateringHole handoffs).

```
gen2: Primals        — capability providers (what the ecosystem CAN do)
gen3: Springs        — validation and evolution environments (proving it WORKS)
gen4: Gardens        — user-facing products (making it USEFUL)
     fossilRecord   — geological archive (HOW we got here)
```

| Layer | Directory / Repo | Role | Examples |
|-------|-----------------|------|----------|
| **Primal** (gen2) | `primals/` | Self-contained Rust binary providing domain primitives via IPC | BearDog, Songbird, barraCuda, biomeOS |
| **Spring** (gen3) | `springs/` | Validation environment: composes primals, validates science, surfaces gaps | ludoSpring, hotSpring, wetSpring, primalSpring |
| **Garden** (gen4) | `gardens/` | User-facing product: composes primals into tools people use | esotericWebb, blueFish, helixVision, initioChem |
| **fossilRecord** | `ecoPrimals/fossilRecord` | Canonical archive: superseded handoffs, closed audits, evolution history | 3,831+ documents from 10 sources |

---

## What Each Layer Owns

### Primals

A primal owns a **domain** and exposes its capabilities as **primitives**
via JSON-RPC IPC. Primals have self-knowledge only — they never import
another primal's code.

**Primals own:**
- Primitives (atomic domain operations)
- IPC surface (JSON-RPC method handlers)
- Health protocol (`health.liveness`, `health.readiness`, `health.check`)
- Capability registration with biomeOS
- The canonical implementation of their domain's math/logic

**Primals do NOT own:**
- Validation of their own correctness in composition (that's a spring's job)
- User experience (that's a garden's job)
- Cross-domain coordination patterns (that's biomeOS + wateringHole)

### Springs

A spring is a **validation and evolution environment**. It composes primals
and validates that their composition solves real scientific or engineering
problems. Springs are where gaps in primals are discovered and fed back
to the ecosystem.

**Springs own:**
- Numbered experiments with counted checks
- Deploy graphs (TOML) for the compositions they validate
- `ValidationHarness` / `ValidationResult` with pass/fail/skip exit codes
- Science baselines (Python → Rust parity, published paper reproduction)
- Gap discovery and wateringHole handoff authorship
- Faculty anchors (academic publications driving the science)

**Springs do NOT own:**
- User-facing products or interfaces
- Primal source code (zero compile-time coupling)
- The definitive implementation of any primitive (that's the primal's job)

**Evolution pipeline:**
```
Python baseline → Rust validation → barraCuda CPU → barraCuda GPU
→ fused TensorSession → sovereign dispatch → primal composition
→ ecosystem co-evolution
```

### Gardens

A garden is a **user-facing product** that composes primals into tools
people actually use. Gardens follow the BYOB model (Bring Your Own
Binaries), consuming pre-built primal binaries from plasmidBin.

**Gardens own:**
- User experience and product design
- `PrimalBridge` (JSON-RPC client wrapping capability calls)
- Graceful degradation when optional primals are absent
- Product-level deploy graphs and niche YAML
- Domain-specific composition logic

**Gardens do NOT own:**
- Primal source code
- Validation of primal correctness (they surface usability gaps, not bugs)
- Science baselines or experiments

---

## Interaction Contracts

### Primal → Spring

Springs consume primal IPC to validate correctness. Every spring call to a
primal is honest: if the primal isn't running, the check is **skipped**
(exit 2), not faked.

- Springs call primal methods via JSON-RPC (discovered by capability)
- Springs validate return values against known baselines
- Springs report pass/fail/skip with provenance
- Springs surface gaps as wateringHole handoffs

### Primal → Garden

Gardens consume primals via BYOB/plasmidBin. They never see primal source.
When a primal is absent, gardens **degrade gracefully** — the product
continues with reduced functionality.

- Gardens call primal methods via `PrimalBridge`
- Gardens handle `ConnectionRefused` / timeout as non-fatal
- Gardens surface usability gaps (not correctness bugs)

### Spring → Primal (Co-evolution Loop)

This is the primary feedback mechanism driving ecosystem improvement:

```
Spring validates composition
→ discovers gap (missing method, wrong tolerance, protocol mismatch)
→ files wateringHole handoff with gap details
→ primal team evolves primitive
→ tags release → plasmidBin
→ spring re-validates → gap resolved (or new gap surfaces)
```

### Garden → Spring

Gardens surface usability gaps that springs then validate for feasibility:

```
Garden discovers usability gap (e.g. missing session lifecycle)
→ files EVOLUTION_GAPS.md or wateringHole handoff
→ spring validates whether the gap is solvable with existing primals
→ if yes: spring experiments demonstrate the solution
→ if no: spring surfaces the underlying primal gap upstream
```

### Spring ↔ Spring

Springs **never import each other**. They coordinate exclusively through:

- wateringHole handoffs
- Shared barraCuda primitives (both consume the same math)
- primalSpring deploy graph patterns (templates and conventions)
- Cross-spring experiment references in baseCamp

---

## The Co-Evolution Loop

This is the cycle that makes the ecosystem self-improving:

```
┌─────────────────────────────────────────────────┐
│  Spring or Garden discovers a gap                │
│  (missing method, protocol mismatch, tolerance)  │
└──────────────────┬──────────────────────────────┘
                   ▼
┌──────────────────────────────────────────────────┐
│  wateringHole handoff filed                       │
│  (gap details, reproduction steps, proposed fix)  │
└──────────────────┬───────────────────────────────┘
                   ▼
┌──────────────────────────────────────────────────┐
│  Primal team evolves the primitive                │
│  (new method, fixed tolerance, protocol update)   │
└──────────────────┬───────────────────────────────┘
                   ▼
┌──────────────────────────────────────────────────┐
│  Release tagged → plasmidBin updated              │
└──────────────────┬───────────────────────────────┘
                   ▼
┌──────────────────────────────────────────────────┐
│  Spring re-validates composition                  │
│  Garden re-composes with updated binary           │
│  → gap resolved OR new gap surfaces → loop        │
└──────────────────────────────────────────────────┘
```

**Communication channel:** wateringHole handoffs are the sole structured
coordination mechanism between layers. No layer directly modifies another
layer's code.

---

## Tools (gen2.5)

Between primals and gardens, the ecosystem has a class of entities that are
**standalone Rust crates or binaries consumed by primals, springs, or infrastructure**.
They are not long-running IPC services (no sockets, no health endpoints, no capability
registration) and they are not end-user products. They solve bounded problem domains
without the full IPC/discovery surface that primals carry.

```
gen2:   Primals — capability providers (IPC daemons)
gen2.5: Tools   — domain crates / CLIs consumed by other layers
gen3:   Springs — validation environments
gen4:   Gardens — user-facing products
```

| Tool | Location | Domain | Role |
|------|----------|--------|------|
| **bingoCube** | `primals/` | Crypto commitment | Human-verifiable visual/audio patterns from BLAKE3 + ChaCha20 boards. Nautilus reservoir computing. |
| **benchScale** | `infra/` | Lab substrate | Pure Rust VM provisioning and distributed system testing harness. |
| **agentReagents** | `infra/` | VM image builder | Template-driven VM images for gate provisioning. Depends on benchScale. |
| **rustChip** | `sort-after/` | NPU characterization | BrainChip Akida register-level driver, models, and benchmarks. Extracted from toadStool metalForge. |
| **sourDough** | `primals/` | Scaffolding / Meta | Scaffolds new primals with ecosystem DNA. CLI tool, not a daemon. |

**What applies to tools:** Tier 1 (Build Quality), Tier 6 (Responsibility), Tier 7 (Workspace
Dependencies), Tier 8 (Presentation). Same code quality bar as primals.

**What does not apply:** Tier 2 (UniBin — no daemon), Tier 3 (IPC — no sockets), Tier 4
(Discovery — no registration), Tier 5 (Semantic Naming — no RPC methods), Tier 9
(Deployment/Mobile — no binary distribution).

**Where they live:** `primals/` when consumed as Rust crate deps by primals; `infra/` when
infrastructure-only. The boundary is grey and evolves with the ecosystem.

**Tools own:**
- A bounded domain implementation (math, hardware interface, template engine, etc.)
- Their own test suite and quality gates
- README, CHANGELOG, CONTEXT.md, deny.toml (same surface as primals)

**Tools do NOT own:**
- IPC surface or health protocols
- Capability registration with biomeOS
- User experience or product interfaces

---

## Key Distinctions

| Aspect | Springs | Gardens |
|--------|---------|---------|
| **Failure mode** | Honest pass/fail/skip exit codes (0/1/2) | Graceful degradation for users |
| **Deploy graphs** | For testing and validation | For production deployment |
| **State management** | `ValidationHarness` | `PrimalBridge` |
| **Gap type discovered** | Correctness bugs, protocol mismatches, missing capabilities | Usability gaps, UX issues, missing convenience methods |
| **Binary consumption** | Compile-time library link + IPC probe | BYOB from plasmidBin (pure IPC) |
| **Science** | Reproduces published papers, baseline parity | Exercises composed science in product context |

---

## Validated Pipeline (April 20, 2026)

The full NUCLEUS → Spring → Garden pipeline has been validated end-to-end:

```
NUCLEUS certification (primalSpring)
  guidestone: 84/86 (6 layers, 13 primals, 11 capabilities)
  exp094:     15/18 composition parity
  graphs:     17/17 deploy graphs parse clean
          ↓
Spring science validation (ludoSpring)
  Tier 1:     152/152 local math (no IPC)
  Tier 2:     18/19 tower, 3/6 barraCuda composition
  Tier 3:     30/31 full NUCLEUS composition, 11/11 pipeline
  Structural: 14/14 deploy graph tests
          ↓
Garden composition (esotericWebb)
  Product graphs: 8/8 valid TOML (Webb)
  Proto sketches: 7/7 valid (ludoSpring → Webb)
  IPC flows:      game.* ✓, visualization.* ✓, compute.* ✓
```

Each spring may produce its own garden. For example:
- ludoSpring → esotericWebb (CRPG composition)
- hotSpring → MILC results garden for physicists
- wetSpring → environmental sensor dashboard

The pattern is standard; the domain science differs.

---

## How to Read Other Documents

- **GLOSSARY.md**: Definitions of all ecosystem terms including Primal, Spring, Garden
- **COMPOSITION_PATTERNS.md**: Deploy graph formats, socket discovery, niche YAML
- **SPOREGARDEN_DEPLOYMENT_STANDARD.md**: BYOB model for gardens
- **SPRING_INTEROP_LESSONS.md**: Practical interop learnings from the first compositions
- **PRIMALSPRING_COMPOSITION_GUIDANCE.md**: primalSpring-specific composition capabilities
