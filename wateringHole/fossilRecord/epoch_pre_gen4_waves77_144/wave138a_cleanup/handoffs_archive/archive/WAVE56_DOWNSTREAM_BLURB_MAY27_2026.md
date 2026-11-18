# Wave 56 Downstream Blurb — Springs, cellMembrane, Projects

**Date:** May 27, 2026
**From:** primalSpring coordination
**To:** cellMembrane, projectNUCLEUS, projectFOUNDATION, all spring teams

---

## What primalSpring Shipped (Waves 55b–56)

- **VPS deployment standard** documented and tooled
- **`nucleus_launcher --uds-only`** — zero-TCP-port mode for VPS deployments
- **Cell graph `vps_standard` tagging** — 6 spring cells VPS-ready, 3 desktop-only
- **Env var centralization** complete — all access through `env_keys.rs`
- **12 primordial scripts archived** to `fossilRecord/`
- **Desktop scripts marked** with VPS-exclusion headers
- **797 lib tests**, 56 scenarios, 93 experiments, zero clippy warnings

---

## cellMembrane Team

You have everything needed for VPS deployment standardization:

### Artifacts to Consume

| Artifact | Location | Purpose |
|----------|----------|---------|
| Spring cell graphs | `graphs/cells/{spring}_cell.toml` | Deploy topologies (6 VPS-ready, all `spawn=false`) |
| Cell manifest | `graphs/cells/cells_manifest.toml` | Index with `vps_standard` field |
| Launch profiles | `config/primal_launch_profiles.toml` | Per-primal CLI/env wiring |
| Seed fingerprints | `validation/seed_fingerprints.toml` | Crypto tier 0 bootstrap |

### Action Items

| # | Action | Priority |
|---|--------|----------|
| 1 | Use `--uds-only` when invoking `nucleus_launcher` from `deploy_membrane.sh` | HIGH |
| 2 | Deploy spring overlays via `biomeos deploy graphs/cells/{spring}_cell.toml` | HIGH |
| 3 | Forgejo releases alongside GitHub (NC-3.4 sovereignty) | MEDIUM |
| 4 | NS cutover for knot-dns (NC-3.3) | MEDIUM |
| 5 | sporePrint living content via NestGate `content.put` (NC-3.5, blocked on bearDog scope) | LOW |

### VPS Deployment Flow

```
1. deploy_membrane.sh / plasmidbin deploy  →  NUCLEUS base (13 primals, UDS-only)
2. biomeos deploy graphs/cells/{spring}_cell.toml  →  spring overlay (spawn=false)
3. Spring uses CompositionContext::from_live_discovery()  →  UDS tiers 2-4
```

No `desktop_nucleus.sh`, no `cell_launcher.sh`, no TCP ports on the standard path.

---

## projectNUCLEUS Team

| Action | Priority | Notes |
|--------|----------|-------|
| No blocking items | — | Deep debt resolved. `primalspring checksums` and `primalspring registry` subcommands replace all shell validation scripts. |
| Consume `--uds-only` in deployment tooling | MEDIUM | Align NUCLEUS deployment scripts with zero-port standard |

---

## projectFOUNDATION Team

| Action | Priority | Notes |
|--------|----------|-------|
| Thread 10 spore ingest workload | — | **DELIVERED** (`nucleus-spore-ingest.toml`) — thank you |
| No blocking items | — | Era 3 evidence pipeline is gated on NC-1 live deploy, not primalSpring code |

---

## Spring Teams (All)

### Per-Gate Status

| Gate | Springs | NUCLEUS Depth | Action |
|------|---------|---------------|--------|
| **eastGate** | airSpring, groundSpring | Full NUCLEUS | **Operational** — no action |
| **ironGate** | healthSpring, ludoSpring | Full NUCLEUS | **Operational** — NestComposition facade when ready |
| **southGate** | wetSpring, neuralSpring | Node Atomic | **7/13 health** — stabilize, investigate Songbird/biomeOS/BearDog |
| **biomeGate** | hotSpring | Node Atomic | **9/13** — elevate to full NUCLEUS (hardware gated) |

### What Springs Need to Do for postPrimordial

1. Ensure your spring cell graph (`graphs/cells/{spring}_cell.toml`) has `spawn=false` for all primals
2. Test `biomeos deploy` with your cell graph against a live NUCLEUS
3. Run your domain workload through `CompositionContext::from_live_discovery()`, not harness
4. Column U: emit a pseudoSpore via NUCLEUS ingest (gated on v3.81 VPS deploy)

### What Springs Do NOT Need to Do

- No shell script changes
- No new primalSpring dependency — everything is in `CompositionContext`
- No TCP port allocation — VPS is UDS-only

---

## Stadial Gate Readiness

```
NC-1 (spore gateway)        COMPLETE  — code done, v3.81 needs VPS deploy
NC-2 (multi-gate mesh)      IN PROGRESS — southGate ops stabilization
NC-3 (cellMembrane sovereignty) ADVANCING — Forgejo + NS cutover remaining
NC-4 (spring NUCLEUS depth) MIXED     — east/iron OK, south/biome partial
NC-5 (lithoSpore emission)  GATED     — on NC-1 live deploy

Stadial entry requires: NC-1 (2+ springs), NC-2 (3+ gates), NC-4 (all 4 gates)
```

---

*primalSpring is ready. We validate as gates come online.*
