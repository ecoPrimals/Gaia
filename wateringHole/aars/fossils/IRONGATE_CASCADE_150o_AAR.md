# ironGate Cascade AAR — Wave 150o

**Date**: Jul 20, 2026 10:09 EDT
**Gate**: ironGate (10.13.37.7)
**Team**: ironGate hardware + deployment
**Scope**: Full cascade from VPS, Forgejo-first remote swap, test suite validation

---

## Pre-Cascade State

ironGate at Wave 142b (Jul 16). primalSpring 10 commits behind, cellMembrane 23
commits behind. All three key repos still had `origin=GitHub`, `forgejo=Forgejo`
(pre-150k layout). GitHub SSH rejecting (`Permission denied (publickey)`).

---

## Actions Taken

### 1. Forgejo-First Remote Swap

Per Wave 150k standard, swapped remotes on all three repos:

| Repo | Before | After |
|------|--------|-------|
| primalSpring | origin=GitHub, forgejo=Forgejo | origin=Forgejo, github=GitHub |
| wateringHole | origin=GitHub, forgejo=Forgejo | origin=Forgejo, github=GitHub |
| cellMembrane | origin=GitHub, forgejo=Forgejo | origin=Forgejo, github=GitHub |

GitHub SSH was failing — Forgejo is now the sole push target from ironGate.
golgiBody handles GitHub mirroring via push mirrors.

### 2. Repository Pulls

| Repo | From | To | Commits |
|------|------|----|---------|
| primalSpring | 2774faf (142b) | ff32f32 (150n) | +10 |
| cellMembrane | f4da0ae (141b) | 77a82ea (150n) | +23 |
| wateringHole | already at parity | — | 0 |

Key upstream changes absorbed:
- CAC validation scenario + composition-access-control
- Subdomain URL standard (`prefix.primals.eco`)
- Clippy pedantic+nursery clean (0 warnings)
- Dimensional review formatting
- Known debt recalibrations (149b, 150b, 150k, 150n)
- OS Atheism Phase 2 transport abstraction (cellMembrane)
- Mesh registry: southGate 10.13.37.9 allocated (cellMembrane)
- Portable-atomic + CAC impulse dedup + sporePrint health (cellMembrane)

### 3. Known Debt Calibration

| Scenario | eastGate expects | ironGate actual | Action |
|----------|-----------------|-----------------|--------|
| graphenegate-readiness | 14 failures | 0 | Cleared (deploy_pixel.sh present locally) |
| composition-access-control | 15 failures | 15 | Kept (live composition wiring not present) |
| cascade-provenance-match | 0 | 2 | Added (checksums.toml format mismatch) |
| bootstrap-readiness | 0 | 1 | Added (depot path not configured) |

### 4. Head Re-Publish

`heads/ironGate.toml` refreshed with 19 repo HEADs (was stale since Jul 16).

---

## Post-Cascade State

| Metric | Value |
|--------|-------|
| primalSpring scenarios | **171** |
| Test suite | **1,206 passed / 0 failed / 2 ignored** |
| Remotes | **Forgejo-first** (origin=Forgejo, github=GitHub) |
| Wave | **150o** |
| Head published | **Jul 20 13:55Z** |
| cellMembrane | **77a82ea** (current with mesh registry + portable-atomic) |

---

## Recurring Pattern: Known Debt Divergence

Every cascade requires recalibrating `KNOWN_DEBT` in `mod.rs` because eastGate
and ironGate have different deployment contexts:

- `graphenegate-readiness`: fails on eastGate (no deploy_pixel.sh), passes on ironGate
- `sporeprint-pure-primal-parity`: fails on eastGate (composition graph), passes on ironGate
- `cascade-provenance-match`: passes on eastGate, fails on ironGate (checksums format)
- `bootstrap-readiness`: passes on eastGate, fails on ironGate (depot path)

**Recommendation**: Gate-aware debt — `KNOWN_DEBT` should branch on
`detect_local_gate()` or `GATE_NAME` env var, so each gate carries its own
expected failure set. This would eliminate the per-cascade manual recalibration.

---

## ironGate Runtime Status (unchanged)

- 13/13 NUCLEUS primals, JupyterHub, songBird drawbridge, GPU compute
- WireGuard mesh: 10.13.37.7, 5-gate active, handshakes fresh
- `lab.primals.eco` → 401 (auth expected, healthy)
- 26 UDS sockets under `/run/membrane/`
