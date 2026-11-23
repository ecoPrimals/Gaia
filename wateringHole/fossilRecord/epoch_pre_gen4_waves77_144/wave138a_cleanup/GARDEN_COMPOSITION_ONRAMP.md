# Garden Composition Onramp — Building gen4 Products

**Version:** 1.0.0
**Date:** April 27, 2026
**Audience:** Garden product teams (esotericWebb, blueFish, helixVision, future gardens)
**Status:** Active
**License:** AGPL-3.0-or-later

---

## Purpose

Gardens are gen4 products — tools that real people use. They compose primals
via biomeOS graphs and IPC. They never import primal source code. They never
implement math. They inherit proven science from springs and proven
infrastructure from primals.

This document is the operational starting point for any garden team. It
answers: "I want to build a product on ecoPrimals. What do I do?"

For the conceptual foundation, see `PRIMAL_SPRING_GARDEN_TAXONOMY.md` and
`DEPLOYMENT_AND_COMPOSITION.md`. This document is the procedural counterpart.

---

## The Garden Contract

A garden MUST:

1. **Consume primals as binaries** — via `plasmidBin` fetch, never source import
2. **Compose via deploy graphs** — TOML DAGs executed by biomeOS Neural API
3. **Degrade gracefully** — absent optional primals reduce features, never crash
4. **File gaps back** — capability mismatches, missing methods, wire surprises → wateringHole handoffs
5. **Respect scyBorg** — AGPL-3.0 (code) + ORC (mechanics) + CC-BY-SA (creative)

A garden MUST NOT:

- `cargo add` any primal crate
- Implement math that a primal already exposes
- Assume specific primals — route by capability, not name
- Require the full NUCLEUS — define minimum viable composition

---

## Step 1: Fetch Binaries from plasmidBin

```bash
# From your garden workspace
git clone https://github.com/ecoPrimals/plasmidBin.git
cd plasmidBin

# Fetch all binaries from latest GitHub Release
cargo run -p plasmidbin -- fetch --all

# Validate binary integrity (BLAKE3 checksums + metadata)
cargo run -p plasmidbin -- doctor
```

After fetch, `plasmidBin/primals/{triple}/` contains ecoBin binaries for
every primal. The Rust CLI auto-detects your host architecture.

**Cross-architecture:** The fetch command auto-detects your target triple.
For explicit targets, specify `--arch aarch64` (not yet supported; build
from source via `plasmidbin build`).

---

## Step 2: Define Your Deploy Graph

Your deploy graph IS your architecture. It declares what capabilities your
product needs, in what order they start, and how they degrade.

**Minimum viable graph** (`graphs/mygarden_deploy.toml`):

```toml
[graph]
name = "mygarden_deploy"
description = "My Garden — minimum viable composition"
version = "1.0.0"
coordination = "sequential"

# Phase 0: biomeOS substrate (already running)
[[graph.node]]
name = "biomeos_neural_api"
binary = "biomeos"
order = 0
required = true
spawn = false
health_method = "graph.list"
by_capability = "orchestration"

# Phase 1: Tower Atomic (security + discovery)
[[graph.node]]
name = "beardog"
binary = "beardog_primal"
order = 1
required = true
depends_on = ["biomeos_neural_api"]
health_method = "health.liveness"
by_capability = "security"
capabilities = ["crypto.sign", "crypto.verify", "crypto.encrypt"]

[[graph.node]]
name = "songbird"
binary = "songbird_primal"
order = 2
required = true
depends_on = ["biomeos_neural_api"]
health_method = "health.liveness"
by_capability = "discovery"
capabilities = ["discovery.find_primals", "discovery.announce"]

# Phase 2: Domain primals (your product needs)
[[graph.node]]
name = "petaltongue"
binary = "petaltongue"
order = 3
required = true
depends_on = ["beardog", "songbird"]
health_method = "health.liveness"
by_capability = "visualization"
capabilities = ["render.scene", "render.text", "interaction.poll"]

# Phase 3: Optional enrichment (graceful degradation)
[[graph.node]]
name = "squirrel"
binary = "squirrel"
order = 4
required = false
depends_on = ["beardog"]
health_method = "health.liveness"
by_capability = "ai"
capabilities = ["inference.query", "inference.models"]
fallback = "skip"

# Provenance trio (optional — record when available)
# IMPORTANT: rhizoCrypt requires FAMILY_SEED env var when using family-scoped
# sockets, or BTSP gate rejects all connections. composition_nucleus.sh handles
# this automatically from BEARDOG_FAMILY_SEED.
[[graph.node]]
name = "rhizocrypt"
binary = "rhizocrypt"
order = 5
required = false
depends_on = ["beardog"]
health_method = "health.liveness"
by_capability = "dag"
fallback = "skip"

[[graph.node]]
name = "loamspine"
binary = "loamspine"
order = 6
required = false
depends_on = ["beardog"]
health_method = "health.liveness"
by_capability = "ledger"
fallback = "skip"

[[graph.node]]
name = "sweetgrass"
binary = "sweetgrass"
order = 7
required = false
depends_on = ["beardog"]
health_method = "health.liveness"
by_capability = "attribution"
fallback = "skip"
```

**Key decisions:**
- `required = true` means "product cannot function without this"
- `required = false` + `fallback = "skip"` means "use when available, degrade when absent"
- `by_capability` routes via Neural API — your product never hardcodes `beardog_primal`

See `DEPLOYMENT_AND_COMPOSITION.md` §BYOB for the full schema reference and
the `[[nodes]]` format for multi-gate / multi-architecture deployments.

---

## Step 3: Implement the PrimalBridge

Your product communicates with primals through a bridge layer — thin IPC
wrappers that route by capability and handle degradation.

**Pattern** (from esotericWebb):

```rust
pub struct PrimalBridge {
    socket_dir: PathBuf,
    available: HashMap<String, PathBuf>,
}

impl PrimalBridge {
    pub fn discover(socket_dir: &Path) -> Self {
        let mut available = HashMap::new();
        // Scan socket directory for live primals
        if let Ok(entries) = std::fs::read_dir(socket_dir) {
            for entry in entries.flatten() {
                if let Some(name) = entry.file_name().to_str() {
                    if name.ends_with(".sock") {
                        let primal = name.trim_end_matches(".sock").to_string();
                        available.insert(primal, entry.path());
                    }
                }
            }
        }
        Self { socket_dir: socket_dir.to_path_buf(), available }
    }

    pub fn has_capability(&self, cap: &str) -> bool {
        self.available.contains_key(cap)
    }

    pub fn call(&self, capability: &str, method: &str, params: serde_json::Value)
        -> Result<serde_json::Value, BridgeError>
    {
        let sock = self.available.get(capability)
            .ok_or(BridgeError::CapabilityUnavailable(capability.to_string()))?;
        send_jsonrpc(sock, method, params)
    }

    pub fn call_optional(&self, capability: &str, method: &str, params: serde_json::Value)
        -> Option<serde_json::Value>
    {
        self.call(capability, method, params).ok()
    }
}
```

**Degradation:** use `call_optional` for provenance, AI, and any
non-essential enrichment. Use `call` (which returns `Result`) for
required capabilities and handle the error in your product logic.

---

## Step 4: Define Your Niche YAML

The niche declaration tells biomeOS what your product IS, not just what
it needs.

```yaml
niche:
  id: "my-garden"
  name: "My Garden Product"
  version: "1.0.0"
  deploy_graph: "graphs/mygarden_deploy.toml"
  description: "A gen4 product that does X for users"

organisms:
  primals:
    beardog:
      type: "beardog"
      required: true
      role: "security"
    petaltongue:
      type: "petaltongue"
      required: true
      role: "visualization"
    squirrel:
      type: "squirrel"
      required: false
      role: "ai"

interactions:
  - from: "my-garden"
    to: "petaltongue"
    type: "capability_call"
    config:
      capabilities: ["render.scene", "interaction.poll"]
  - from: "my-garden"
    to: "squirrel"
    type: "capability_call"
    config:
      capabilities: ["inference.query"]
      optional: true

customization:
  options:
    provenance_enabled:
      type: boolean
      default: true
      description: "Record provenance when trio is available"
```

---

## Step 5: Launch and Validate

```bash
cd plasmidBin

# Start individual primals
cargo run -p plasmidbin -- start beardog
cargo run -p plasmidbin -- start songbird
cargo run -p plasmidbin -- start petaltongue

# Or launch a full composition
cargo run -p plasmidbin -- launch --composition full

# Deploy your graph via biomeOS
biomeos deploy --graph graphs/mygarden_deploy.toml

# Run your product
cargo run --release --bin my-garden
```

**Validation checklist:**
- [ ] Product starts with `required` primals only
- [ ] Product degrades gracefully when optional primals absent
- [ ] `biomeos validate --graph graphs/mygarden_deploy.toml` passes
- [ ] All method calls use semantic naming (`domain.verb`)
- [ ] Zero primal source imports (`cargo tree` shows no primal crates)
- [ ] scyBorg triple license applied (AGPL + ORC + CC-BY-SA where applicable)

---

## Step 6: File Gaps Back

As you build, you will discover missing capabilities, wire surprises, and
degradation edge cases. This is expected — it's the evaporation phase of
the ecosystem cycle.

**How to file:**
1. Document the gap in your product's `EVOLUTION_GAPS.md`
2. Create a wateringHole handoff: `handoffs/<PRODUCT>_<VERSION>_<GAP>_HANDOFF_<DATE>.md`
3. Reference the blocking primal and the specific method/capability

**What makes a good gap report:**
- What you called (method, params)
- What you expected (response shape, behavior)
- What you got (actual response, error, silence)
- Which primal/capability
- Severity: blocks product vs reduces features vs cosmetic

---

## Inheritance from Springs

Gardens don't validate science — springs do. But gardens inherit the
validation confidence:

```
hotSpring proved: barraCuda f64 GPU math matches Python baselines
                  ↓
primalSpring proved: barraCuda composition works via IPC
                  ↓
Your garden inherits: GPU math is correct when called via capability
```

**What this means for you:**
- Trust `stats.mean` returns correct values (springs proved it)
- Trust `crypto.sign` produces valid signatures (springs proved it)
- Your job is to compose correctly, not to re-validate math
- If you find a discrepancy, file it — you've discovered a gap

---

## Reference Implementations

| Garden | Status | Deploy Graphs | Primals Consumed |
|--------|--------|---------------|-----------------|
| **esotericWebb** V7 | Active | 4 fragment graphs + full | 7 domains, all degrading |
| **blueFish** | Seed (v0.1.0) | 6 tiered graphs (tower→full) | 10 domains planned, neutron-heavy |
| **helixVision** | Seed (v0.1.0) | 5 tiered graphs (tower→full) | 11 domains planned, electron-heavy |
| **initioChem** | Seed (v0.1.0) | 6 tiered graphs (tower→full) | 8 domains planned, proton-heavy |

See `esotericWebb/` for the canonical gen4 product pattern:
- `config/primal_launch_profiles.toml`
- `graphs/*.toml`
- `niches/*.yaml`
- `src/bridge/` (PrimalBridge)

---

## Related Documents

- `DEPLOYMENT_AND_COMPOSITION.md` — Full composition architecture (BYOB schema, niche YAML, launch profiles)
- `PRIMAL_SPRING_GARDEN_TAXONOMY.md` — The three layers: primals, springs, gardens
- `EVOLUTION_STATUS_WAVE66.md` — The water cycle: how capabilities flow
- `PROVENANCE_TRIO_INTEGRATION_GUIDE.md` — Wiring the provenance trio
- `COMPOSITION_TICK_MODEL_STANDARD.md` — Temporal requirements for real-time products
- `INTERACTION_EVENT_TAXONOMY.md` — Input event types across modalities
- `primalSpring/wateringHole/PLASMINBIN_DEPOT_PATTERN.md` — Binary depot pattern

---

**Gardens are the ocean. Everything flows here. Build products, not infrastructure.**
