# Wave 84 — Blurbs by Level

**Date**: 2026-06-06  
**Author**: eastGate overwatch  
**Type**: Blurb — copy/paste by level  
**Wave 84 status**: Cascade system LEVELED. membrane temporal.cascade is sole sync
interface (38/38 repos, 60s git timeout, merge-ff policy). cellMembrane zero-touch
pipeline LIVE on VPS (30-min timer). primalSpring excised. Peptidoglycan FRAGO RESOLVED.
New FRAGO: wave84-temporal-inner-membrane-adoption.

---

## cellMembrane (ironGate) — Cascade Evolution + Temporal Membrane Ownership

**This is the primary Wave 84 action item.**

cellMembrane now owns the temporal inner membrane — cascade sync, deployment
pipeline, and freshness tracking for the entire ecosystem.

### What Was Leveled (overwatch, Wave 84)

Three fixes applied to `membrane-shadow` and committed to cellMembrane:

1. **`git_ops.rs`**: `git_output` and `git_success` now have 60-second
   `tokio::time::timeout` + `GIT_SSH_COMMAND` with `ConnectTimeout=10`,
   `ServerAliveInterval=5`, `ServerAliveCountMax=3`. Previous cascade hung
   indefinitely on stalled SSH.

2. **`lib.rs`**: `resolve_workspace_root()` now walks up from CWD before
   executable path. Running `membrane` from inside ecoPrimals works without
   `ECOPRIMALS_ROOT`.

3. **`ecosystem_manifest.toml`**: Default `divergence_policy` upgraded
   from `"flag"` to `"merge-ff"`. Tree-parity (rebase artifact) auto-resolves.

### New Gaps for cellMembrane

| Gap ID | Description | Priority |
|--------|-------------|----------|
| CM-CASCADE-01 | Sequential cascade ~59s (38 repos). Target <10s with tokio::spawn parallel | P2 |
| CM-FORGEJO-01 | sourDough repo returned 500 on push (transient, check Forgejo data dir) | P2 |
| CM-WEBHOOK-01 | Cascade timer-polled (30-min). Webhook-driven reduces push-to-VPS latency | P3 |
| CM-FRESHNESS-01 | freshness.toml not published after cascade by default | P2 |

### Evolution Path

1. **Parallel repo sync** — `tokio::spawn` per repo in `cascade.rs`. Each
   repo's fetch/check/push is independent. With 38 repos and ~1.5s each,
   parallel should yield <5s total.

2. **Freshness tracking** — `cascade_with_opts` already has `publish_freshness`
   flag but it's opt-in. Make it default for `Sync` mode.

3. **Webhook cascade** — Forgejo push webhooks fire to a local listener
   that triggers selective cascade + rebuild for the changed repo only.
   Reduces push-to-VPS latency from 30 minutes to ~2 minutes.

4. **`agentic` divergence policy** — placeholder exists in
   `apply_divergence_policy`. Wire to an agent resolver for complex
   divergence cases (multi-writer repos like sporePrint).

### Reference

- AAR: `handoffs/WAVE84_AAR_CASCADE_LEVELING_JUN06_2026.md`
- FRAGO: `impulses/active/2026-06-06T22-00_eastGate__wave84-temporal-inner-membrane-adoption.toml`
- Archived: `handoffs/archive/wave84/` (5 fossilized Wave 82c/83 handoffs)

---

## PRIMALS — Transport Injection Gap

All 13 primals at full parity. Zero P0/P1 gaps. Mountain is clear.

### New Gap: Transport Injection (P2, non-blocking)

0/14 primals have transport injection. All still self-bind via
`TcpListener::bind` or `UnixListener::bind`. The target is transport
ignorance — primals receive a transport channel from the launcher/Tower.

| Primal | TCP refs | UDS refs | Status |
|--------|---------|---------|--------|
| songBird | 267 | 1174 | Exempt (transport provider) |
| toadStool | 101 | 631 | Orchestrator — needs abstraction |
| bearDog | 90 | 341 | Crypto — TLS transport self-binding |
| squirrel | 68 | 505 | Metrics — needs UDS-first default |
| rhizoCrypt | 37 | 84 | Discovery — transport self-binding |
| biomeOS | 28 | 1655 | UDS-heavy already, minimal TCP debt |
| petalTongue | 23 | 355 | WASM path may diverge |
| barraCuda | 15 | 33 | GPU dispatch — minimal transport |
| coralReef | 10 | 100 | Low TCP debt |
| loamSpine | 10 | 137 | Low TCP debt |
| sweetGrass | 9 | 159 | Low TCP debt |
| skunkBat | 3 | 44 | Nearly clean |
| nestGate | 0 | 0 | Transport-free |
| sourDough | 0 | 12 | Nearly clean |

This is Phase 2 of the transport evolution FRAGO (wave79). songBird leads
the ipc.resolve structured endpoint evolution. Non-blocking for stadial.

---

## SPRINGS — No Action

All springs at parity. No new work.

---

## GATES — Temporal Membrane Adoption

All gates must set environment for membrane cascade:

```bash
export ECOPRIMALS_ROOT="$HOME/Development/ecoPrimals"
export GATE_NAME="<gate>"
```

Then use `membrane temporal.cascade` for all sync operations.
Manual git fetch/pull loops are deprecated.

| Gate | Status |
|------|--------|
| eastGate | Environment set, cascade operational |
| ironGate | cellMembrane team — evolves cascade |
| strandGate | Set env, use membrane CLI |
| southGate | Set env, use membrane CLI |
| flockGate | WAN — cascade via peptidoglycan relay |
| westGate | Hardware-gated, deploy from plasmidBin via membrane |

---

*"The cascade is leveled. The membrane owns the sync. The glacier advances."*
