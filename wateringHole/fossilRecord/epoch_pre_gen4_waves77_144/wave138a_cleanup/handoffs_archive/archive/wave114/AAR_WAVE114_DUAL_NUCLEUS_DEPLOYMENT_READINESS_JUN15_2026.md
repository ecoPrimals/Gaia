# AAR + FRAGO: Wave 114 — Dual-NUCLEUS Deployment Readiness

**Date**: 2026-06-15
**Team**: primalSpring / eastGate overwatch
**Commit**: `108fa13` (primalSpring)
**Status**: Launcher & profiles READY — awaiting depot + physical ops

---

## What Was Shipped (primalSpring)

### 1. Dual-NUCLEUS Profile Architecture

eastGate now supports **two concurrent NUCLEUS instances** via family-isolated profiles:

| Profile | Family ID | Transport | Fed Port | Purpose |
|---------|-----------|-----------|----------|---------|
| `--profile shared` | eastgate-shared | UDS-only | :7700 | Production NUCLEUS for airSpring/groundSpring teams |
| `--profile primalspring` | primalspring-test | TCP + UDS | :7701 | Interaction testing (scenario probes, riboCipher sweeps) |

**Isolation**: Different `family_id` → separate PID files, socket namespaces, federation ports.
No cross-contamination between shared (production) and testing instances.

### 2. Gate-Specific Profiles

| Profile | Gate | Arch | Transport | Notes |
|---------|------|------|-----------|-------|
| `--profile fieldgate` | fieldGate (NUC) | x86_64-musl | UDS-only | LAN depot from eastGate, degraded-tolerant |
| `--profile graphenegate` | grapheneGate (Pixel) | aarch64-musl | TCP-only | SELinux UDS blocked, SONGBIRD_STATE_DIR set |

### 3. Manifest Enhancement

- `transport: "tcp_enabled"` in `[composition]` — no more manual `--tcp` flag
- `allow_degraded: true` in `[validation]` — flows into LaunchConfig automatically
- `Stop` command reads `family_id` from profile (so `--profile X stop` works)
- Profile aliases: `shared`, `primalspring`, `fieldgate`, `graphenegate`, `pixel`

### 4. Interaction Quality (from Wave 113 carry)

- `ProbeResult` enum: Healthy / Reachable / Unreachable (distinguishes -32601)
- `s_ribocipher_acceptance` scenario (61st scenario): acceptance sweep
- Socket manifest compliance check in `s_socket_discovery`
- NUCLEUS capability probes via neuralAPI `capability.call`

---

## Deployment Issues — ASSIGNED: cellMembrane/ironGate

### P1: Depot Divergence

| Issue | Detail | Action |
|-------|--------|--------|
| **aarch64 depot absent** | pepti has no aarch64 target installed | Install `aarch64-unknown-linux-musl` target, run `plasmid.harvest --targets aarch64` |
| **Depot freshness** | x86_64 depot was rebuilt from HEAD (14:05Z) but grapheneGate needs aarch64 | Add cross-compile to standard harvest pipeline |
| **Stale binary detection** | grapheneGate field test showed bearDog from Jun 10 vs launcher from Jun 13 (riboCipher mismatch) | Harvest gate: refuse `--targets` if source older than freshness HEAD |

### P2: fieldGate Onboarding Dependencies

| Issue | Detail | Action |
|-------|--------|--------|
| **Physical ops** | NUC needs cable + power + base OS | Manual — then `gate.bootstrap --profile canary-fieldmouse` |
| **LAN depot path** | fieldgate_canary.toml points to `eastgate.local` — needs mDNS or static IP | Configure eno1 /30 static |
| **Depot serving** | eastGate needs to expose plasmidBin over LAN (http or scp) | `python -m http.server` or rsync daemon on eastGate |

### P3: Freshness Multi-Writer (carry)

| Issue | Detail | Action |
|-------|--------|--------|
| **golgiBody still auto-publishing** | freshness.toml races between ironGate + golgiBody | Designate single writer (golgiBody only) or implement freshness.mesh |

---

## What Works Today (validated)

```
# On eastGate — both of these run concurrently, fully isolated:
nucleus_launcher --profile shared start          # production (13/13 UDS-only)
nucleus_launcher --profile primalspring start     # testing (13/13 TCP+UDS)

# On grapheneGate (once aarch64 depot arrives):
nucleus_launcher --profile graphenegate start     # Tower (3/3 TCP-only)

# On fieldGate (once NUC is powered + OS'd):
nucleus_launcher --profile fieldgate start        # Full (13/13 degraded-OK)
```

---

## Overwatch Assignment

| Team | Assigned Items |
|------|---------------|
| **cellMembrane/ironGate** | aarch64 depot, harvest freshness gate, fieldGate physical, LAN depot serving |
| **primalSpring/eastGate** | Co-NUCLEUS evolution, interaction testing, overwatch monitoring |
| **ops** | NUC cable + power |

---

## Next Steps (primalSpring)

- Evolve co-NUCLEUS deployment for projects on eastGate
- Run interaction test suite against live `--profile primalspring` instance
- Validate riboCipher acceptance as upstream primals ship server-side fixes
- Monitor fieldGate + grapheneGate deploys once deps unblock

---

*Filed by primalSpring overwatch, eastGate. Assigns depot + divergence to cellMembrane/ironGate.*
