# primalSpring Wave 49 — Covalent Mesh Evolution

**Date**: May 25, 2026
**Type**: Local evolution + ecosystem coordination
**From**: Wave 48 (spring sound-offs, 4 gates operational)
**To**: Wave 49 (cross-gate verification, Plasmodium collective)

---

## What Happened (Wave 48 → 49)

### Local Debt Resolved

- **`nucleus_launcher --federation-port`** — Rust binary now passes the
  Songbird federation port on spawn; Phase 1 banner shows federation status
- **ludoSpring duplicate Gate Deployment** — removed stale Wave 48 template
- **16-file doc rebaseline** — all docs now reference 53 scenarios, 789 tests,
  Wave 49; binary name `primalspring_unibin` → `primalspring` everywhere;
  deploy graph count 94→95; TOWER_STABILITY + CAPABILITY_ROUTING_TRACE
  fossilized; SOVEREIGNTY_INFRASTRUCTURE_STATUS ACME + primal.announce resolved
- **sporeprint README** — bash→Rust tooling section updated
- **Niche YAML** — version 0.8.0 → 0.9.28

### New Scenario: `s_covalent_mesh`

Scenario 53 — validates the live covalent mesh:

1. **Structural** — `discovery.peers`, `capability.call`, `route.register`
   all in capability registry; covalent graph parses
2. **Discovery** — calls `discovery.peers` via Songbird; checks peer count
   and gate IDs (skips gracefully without federation)
3. **Cross-gate dispatch** — calls `capability.call` with explicit `gate`
   targeting ironGate, southGate, biomeGate (skips without mesh)

This scenario becomes the live validation gate for Plasmodium collective.

---

## Next Steps (Wave 49+)

| Step | Owner | Blocking? |
|------|-------|-----------|
| Verify cross-gate `discovery.peers` on 4 live gates | all springs | **YES** |
| Run `s_covalent_mesh` with live federation on eastGate | primalSpring | YES |
| Cross-gate `capability.call` smoke test (gate parameter) | primalSpring | YES |
| Fix loamSpine Tokio runtime panic (upstream) | loamSpine | No |
| Expand to westGate/northGate/strandGate | springs on those gates | No |
| `biomeos plasmodium status` (3+ gates meshed) | biomeOS | After above |

---

## Verification Commands

```bash
# On any gate with federation enabled:
curl -s -X POST http://127.0.0.1:7700 \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"discovery.peers"}' | jq .result

# Run the covalent mesh scenario:
cargo run --release --bin primalspring -- validate --scenario covalent-mesh

# Start NUCLEUS with federation (Rust launcher):
nucleus_launcher --family-id <family> --federation-port 7700
```
