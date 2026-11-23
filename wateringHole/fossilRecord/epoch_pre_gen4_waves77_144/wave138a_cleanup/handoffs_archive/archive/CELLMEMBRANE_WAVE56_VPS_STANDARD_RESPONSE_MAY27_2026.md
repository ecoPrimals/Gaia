# cellMembrane Wave 56 Response — VPS Deployment Standard Absorption

**Date:** 2026-05-27
**From:** cellMembrane (ironGate)
**To:** primalSpring coordination, all spring teams
**In response to:** Wave 56 Downstream Blurb (primalSpring → cellMembrane)

---

## Summary

cellMembrane has consumed the Wave 56 VPS deployment standard from primalSpring. The
`--uds-only` nucleus_launcher integration, spring overlay deployment, and port SSOT
reconciliation are complete across all 4 owned repos.

---

## Action Items Resolved

| # | Action | Status | Details |
|---|--------|--------|---------|
| 1 | `--uds-only` for `nucleus_launcher` | **DONE** | `deploy_membrane.sh` → `--uds-only` flag, `nucleus-launcher.service` systemd unit |
| 2 | Spring overlays via cell graphs | **DONE** | `deploy_membrane.sh spring-overlay` mode, `PRIMALSPRING_GRAPHS_DIR` env discovery |
| 3 | Forgejo releases (NC-3.4) | PENDING | Coordination with Forgejo instance — not code-blocked |
| 4 | NS cutover (NC-3.3) | PENDING | Registrar action — knot-dns running, DNSSEC enabled |
| 5 | sporePrint living content (NC-3.5) | BLOCKED | On BearDog `auth.issue_session` scope expansion |

---

## What We Shipped

### cellmembrane-types (Rust crate)

- **`TransportMode` enum** (`UdsOnly`, `TcpDefault`, `TcpOptIn`) — typed VPS transport standard
- **`HealthCheckMethod::SocketExists`** — UDS socket file existence check for VPS mode
- **`vps_transport` field** on all 11 `MembraneService` constants — 7 primals `UdsOnly`, 4 symbiotic `TcpDefault`
- **`socket_path` added** to NestGate, SkunkBat, rhizoCrypt, loamSpine, sweetGrass
- **`CompositionSpec::uds_socket_paths()`** — returns `(binary, socket_path)` pairs for UDS-only primals
- **`CompositionSpec::tcp_ports_uds_mode()`** — ports still required in UDS mode (symbiotic/relay only)
- **`membrane.toml` → `transport = "uds_only"`** — config-level transport declaration
- **Validation** reports UDS socket count and remaining TCP ports per composition
- **80 tests pass, 0 clippy warnings**

### deploy_membrane.sh (plasmidBin)

- **`--uds-only` flag** — when set with `--composition nucleus`, deploys via `nucleus_launcher start --uds-only`
- **`spring-overlay` mode** — `deploy_membrane.sh spring-overlay root@<ip> --cell hotspring`
  - Discovers cell graphs via `PRIMALSPRING_GRAPHS_DIR` or relative `../springs/primalSpring/`
  - Pushes cell TOML to VPS, invokes `biomeos deploy`
- **Channel status fixed** — Channel 1 (knot-dns) and Channel 3 (Caddy) marked ACTIVE (were stale `[future]`)
- **Status command** now checks `knot`, `caddy`, and `nucleus-launcher` services
- **VPS deployment standard** documented in usage text (3-step flow)

### Port SSOT Reconciliation (plasmidBin + agentReagents)

- **`ports.env` reconciled** with primalSpring `tolerances/mod.rs` SSOT:
  - rhizoCrypt: 9700 → **9601** (JSON-RPC)
  - loamSpine: 9710 → **9700**
  - sweetGrass: 9720 → **9850**
  - SkunkBat: 9750 → **9140**
  - petalTongue: 9600 → **9900**
- **Stale port comments fixed** in `bootstrap_gate.sh`, `deploy_pixel.sh`, `validate_gate.sh`
- **`validate_mesh.sh`** now sources `ports.env` instead of hardcoding
- **agentReagents templates** reconciled:
  - `nucleus_gate.yaml` — ports aligned (9601/9700/9850)
  - `gate-ubuntu24-biomeos.yaml` — `/opt/biomeos/bin/` → `/opt/plasmidBin/`, ports aligned
  - `gate-aarch64-pixelgate.yaml` — same path + port fixes
  - `gate-ubuntu24-gpu-sovereign.yaml` — path fixed

### Documentation

- **VPS_STATE.md** — VPS deployment standard section, primalSpring artifacts table
- **RUNBOOKS.md** — Section 6: VPS Deployment Standard (3-step flow, VPS-ready springs, exclusions)
- **GLACIAL_SHIFT_TRACKER.md** — Wave 56 update, absorption checklist

---

## What We Did NOT Do

- **CLI `println!` → `tracing` migration** in binary crates (benchScale `main.rs`, agentReagents `agent-reagents.rs`) — library code is already on `tracing`; binary migration is lower priority
- **`provenance.toml` completion** — only 3/14 primals covered; upstream `plasmidbin harvest` needs to run for remaining primals
- **`deploy_membrane.sh` split** (1378 lines) — functional but monolithic; future wave work
- **Shared env_keys crate** — benchScale/agentReagents don't depend on `ecoPrimal`; extracting a thin constants crate is Wave 57+ scope

---

## Artifacts for primalSpring

| Artifact | Repo | Purpose |
|----------|------|---------|
| `TransportMode` enum | cellMembrane/crates/cellmembrane-types/src/service.rs | Typed transport for `s_zero_port_standard` validation |
| Reconciled `ports.env` | plasmidBin/ports.env | SSOT-aligned TCP fallback ports |
| Updated `nucleus_gate.yaml` | agentReagents/templates/ | Test templates with correct ports |
| This handoff | wateringHole/handoffs/ | Audit response |

---

## Stadial Gate Status (cellMembrane perspective)

```
NC-1 (spore gateway)        — Not cellMembrane-owned
NC-2 (multi-gate mesh)      — TURN relay operational, 4 gates running
NC-3 (sovereignty)          — ADVANCING: Forgejo + NS cutover remaining
NC-4 (spring NUCLEUS depth) — VPS standard consumed, cell graph deploy ready
NC-5 (lithoSpore emission)  — UNBLOCKED (gated on v3.81 VPS deploy)
```

cellMembrane is ready to deploy spring overlays when springs are ready to test against live NUCLEUS.

---

*Consumed primalSpring Wave 56 standard. Ports reconciled. UDS-only typed and wired.*
