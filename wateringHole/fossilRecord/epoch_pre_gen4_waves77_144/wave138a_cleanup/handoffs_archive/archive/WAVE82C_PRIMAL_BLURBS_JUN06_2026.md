# Wave 82c — Remaining Primal Work

**Date**: 2026-06-06  
**Author**: eastGate overwatch  
**Type**: Blurb — copy/paste to primal teams by gate  

---

## ALL PRIMALS

All 13 primals are VPS-ready. Zero P0/P1 upstream gaps. 39/39 repos
clean and pushed. The following items are team-owned. Complete before
next harvest cycle.

### PRIORITY 1 — capability_registry.toml (6 primals)

Machine-readable TOML registry enables ecosystem tooling, deploy graph
validation, and DOMAIN_OWNER_MAP auto-discovery. If you don't have one,
create `config/capability_registry.toml` listing your provided and
consumed capabilities. Format: see bearDog or sweetGrass as reference.

| Primal | Current State | Gate |
|--------|---------------|------|
| songBird | `consumed_capabilities` in code only | southGate |
| toadStool | `provided_capabilities` in handlers only | biomeGate |
| barraCuda | Inline in `primal.rs` only | strandGate |
| coralReef | Self-knowledge in code/CONTEXT only | strandGate |
| loamSpine | `CONSUMED_CAPABILITIES` in `niche.rs` only | strandGate |
| skunkBat | `CONSUMED_CAPABILITIES` in `dispatch.rs` only | eastGate |

### PRIORITY 1 — Binary-level items

| Item | Owner | Detail |
|------|-------|--------|
| squirrel/petaltongue UDS health probe | eastGate/ironGate | Socket connects but `health.liveness` returns empty on UDS. Investigate JSON-RPC framing on UDS vs TCP path. Both respond fine on TCP. |
| skunkBat UDS binary rebuild | eastGate | v0.2.6 ships `--socket` flag, but current VPS binary is pre-UDS. Needs rebuild + deploy. |

### PRIORITY 3 — Coverage (ongoing validation, not blocking)

Coverage sprints are validation work — lower priority than functional
items above. Track and improve as teams evolve.

| Primal | Coverage | Stadial Target |
|--------|----------|----------------|
| songBird | 73% | 90% |
| nestGate | 84% | 90% |
| petalTongue | ~85% | 90% |
| toadStool | ~84% | 90% |
| barraCuda | 81% (llvmpipe) | 90% |

### OWNERSHIP NOTE

plasmidBin deployment is transitioning to cellMembrane (ironGate).
Future harvest cycles, VPS refresh, and CI/CD will be coordinated by
cellMembrane team. primalSpring remains a consumer.

---

## SPRINGS (hotSpring, ludoSpring, neuralSpring)

Three springs are missing root `domain_profile.toml`, needed for
`litho emit-pseudospore` and ecosystem classification:

| Spring | Status | Gate |
|--------|--------|------|
| hotSpring | Has nested compchem profiles, no root profile | biomeGate |
| ludoSpring | Missing — composition-only spring | ironGate |
| neuralSpring | Missing | southGate |

Create `domain_profile.toml` at repo root. See wetSpring or healthSpring
as reference format.

---

## cellMembrane (ironGate) — plasmidBin Ownership Transfer

cellMembrane is now the owner of plasmidBin evolution. projectNUCLEUS
is the long-term deployment consumer.

### IMMEDIATE (P1)

- Rebuild 3 rolled-back VPS primals (toadstool, coralreef, squirrel)
- Deploy `mesh.init` on VPS (all 13 confirmed ALIVE, ready)
- Review `infra/plasmidBin/sources.toml` and CI workflows

### EVOLUTION (P2 — next 2-3 waves)

- Absorb `deploy_membrane.sh` into `membrane` CLI (`plasmid.deploy`)
- Add `plasmid.refresh` command (currently only `plasmid.fetch` exists)
- Wire CI harvest workflows into cellMembrane org
- Evolve peptidoglycan self-refresh to auto-fetch from Forgejo releases

### FUTURE (P3 — cellMembrane evolution plan)

- `plasmid.harvest` — build single primal from source, checksum, store
- `plasmid.submit` — accept pre-built binary from primal team, verify, store
- Cascade trigger: `temporal.cascade` emits `harvest.needed` when commit
  distance exceeds threshold (5 commits or semver bump)
- Binary taxonomy: treat binaries as genetic sequences, track evolution
  velocity (size, symbols, dependency surface over time)

See `WAVE82C_OVERWATCH_SHIFT_PLASMIDIN_HANDOFF_JUN06_2026.md` for full
transfer details.

---

*"The mountain is clean. The teams own their work. The membrane owns deployment."*
