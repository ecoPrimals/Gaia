# Wave 63 — southGate Multi-Spring Delta Progress

**Date:** May 30, 2026
**From:** southGate (wetSpring, neuralSpring, ludoSpring)
**To:** primalSpring coordination

---

## Completed (all three springs)

### composition_nucleus.sh Fossilization

| Spring | Commit | Action |
|--------|--------|--------|
| wetSpring | `23d54af` | Fossilized to `fossilRecord/tools/` with provenance header |
| neuralSpring | `83e9175` | Fossilized to `fossilRecord/tools/` with provenance header |
| ludoSpring | `c355f4d` | Fossilized to `fossilRecord/tools/` with provenance header |

All three now use `plasmidBin/nucleus_launcher.sh` as canonical.

### neuralSpring target/release Hardcode Fix

- `scripts/validate_clean_machine.sh:96` — replaced with discovery chain: `command -v` → `plasmidBin/bin/` → `target/release/` → `target/debug/`
- `scripts/visualize.sh:54,68,75` — replaced with `find_binary()` helper using same discovery chain

### CONTEXT.md Drift

All three springs (groundSpring, ludoSpring, neuralSpring) show clean working trees —
either already committed or the audit data was from an earlier primalSpring scan.

---

## wetSpring Specific

| Item | Status |
|------|--------|
| PG-02 (provenance trio) | **VERIFIED** live (May 30) |
| PG-04 (NestGate capability mesh) | **VERIFIED** live (66 caps) |
| `domain_profile.toml` | Created — 7 entity groups, ready for `litho emit-pseudospore` |
| Temporal sync tooling | `--source temporal` confirmed available |
| NUCLEUS | 10/13 health (coralReef socket rename, 2 BTSP-gated) |

---

## Temporal Sync Status (southGate, 20-repo profile)

```
Synced:   16 / 20 (parity)
Pulled:   1 (barraCuda from origin)
Failed:   3 (coralReef, sweetGrass, petalTongue — ff-only vs diverged Forgejo mirrors)
Skipped:  1 (cellMembrane not cloned)
```

The 3 failures are expected: Forgejo mirrors for coralReef, sweetGrass, petalTongue
are stale pull-only mirrors that diverged from GitHub origin. Resolution requires
Forgejo mirror conversion (per audit priority table).

---

## Remaining Blockers (unchanged)

| Blocker | Owner |
|---------|-------|
| Forgejo SSH key registration | eastGate ops |
| Forgejo mirror → bidirectional | eastGate ops (wetSpring priority #2) |
| southGate NUCLEUS full redeploy | ops (coralReef socket) |
| `litho` binary not in plasmidBin | gardens/lithoSpore team |

---

## Audit Checklist Progress

- [x] All 3 dirty CONTEXT.md files — **clean** (already committed or stale audit data)
- [x] neuralSpring `target/release/` hardcodes fixed
- [x] 3 active `composition_nucleus.sh` reviewed and fossilized
- [x] At least 1 spring pseudoSpore emitted — wetSpring `domain_profile.toml` ready (awaits `litho` binary)
- [ ] primalSpring + wetSpring + neuralSpring Forgejo repos converted to bidirectional (blocked: eastGate ops)
- [ ] SouthGate NUCLEUS redeployed (blocked: ops)
