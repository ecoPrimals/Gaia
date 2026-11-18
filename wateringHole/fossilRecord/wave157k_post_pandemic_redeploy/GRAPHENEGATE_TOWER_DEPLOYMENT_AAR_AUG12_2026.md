> **FOSSILIZED** — aarch64 depot REBUILT (15/15). Tower Atomic 4-primal deployment validated on Android. Findings absorbed into ortho review.

# grapheneGate Tower Deployment AAR — Wave 157k

**Date**: Aug 12, 2026 16:35 EDT | **Wave**: 157k | **From**: eastGate overwatch
**Device**: Pixel 8a (akita), GrapheneOS Android 16, ADB serial 44251JEKB04957
**Composition**: Tower Atomic (corrected model — 4 primals)

---

## Result: TOWER ATOMIC DEPLOYED + VERIFIED

All 4 Tower primals started, responded to JSON-RPC health checks, and are operational.

| Primal | Port | Status | Transport | Notes |
|--------|------|--------|-----------|-------|
| beardog | 9100 | **ALIVE** | abstract socket + TCP | `--abstract` (SELinux-safe) |
| songbird | 9200 (IPC) + 7700 (fed) | **ALIVE** | TCP (`--listen`) | PID file dir required `XDG_RUNTIME_DIR` override |
| skunkbat | 9140 | **ALIVE** | TCP only | `--no-uds` (SELinux blocks UDS) |
| swarmvine | 7800 | **ALIVE** | TCP (`--disable-tarpc`) | Cross-compiled on eastGate for this deploy |

### swarmVine Cross-Compile

swarmVine was not in the depot. Cross-compiled on eastGate:
- Target: `aarch64-unknown-linux-musl`
- Linker: `aarch64-linux-gnu-gcc`
- Binary: 2.3MB
- Pushed via ADB, verified `gossip.status` → 1 tower entry, 0 peers

### SELinux Observations

Android SELinux blocks regular UDS socket creation even in `/data/local/tmp`:
- beardog: `--abstract` works (Linux abstract namespace bypasses SELinux)
- skunkbat: `--no-uds` works (TCP-only fallback)
- songbird: `--listen` works (TCP IPC instead of UDS)
- swarmvine: `--disable-tarpc` + TCP transport works

**All 4 primals need explicit Android transport config.** Regular UDS fails.

---

## Blockers for Full NUCLEUS

### Missing Binaries (aarch64-unknown-linux-musl)

| Primal | Owning Team | Issue |
|--------|------------|-------|
| **biomeOS** | biomeOS (eastGate) | Not in aarch64 depot. Substrate primal — may need Android-specific adaptations. |
| **cellMembrane** | cellMembrane (sporeGate) | Not in aarch64 depot. Topology/sovereignty primal. |

### Stale Binaries (Jun 10 depot, pre-Wave 157k)

12 primals on device are from Jun 10 (Wave 108). Multiple bug fixes since then:
- songBird: `--node-id` RESOLVED, `content.locate` functional, deep-debt 8,500+ tests
- toadStool: wgpu28 correct in source
- Others: various fixes since Jun 10

**Owner: sporeGate** — depot rebuild from current HEADs required before fleet redeploy.

### No biomeOS = No Graph-Driven Orchestration

Without biomeOS, primals run standalone (no `composition.orchestrate`, no `primal.list`,
no capability routing). Tower Atomic is the maximum feasible composition until biomeOS
has an aarch64 binary.

---

## Recommended Actions

| # | Action | Owner | Priority |
|---|--------|-------|----------|
| 1 | Build biomeOS for `aarch64-unknown-linux-musl` | biomeOS (eastGate) | HIGH |
| 2 | Build cellMembrane for `aarch64-unknown-linux-musl` | cellMembrane (sporeGate) | MEDIUM |
| 3 | Depot rebuild (all primals, current HEADs) | sporeGate | HIGH (BLOCKING fleet) |
| 4 | Add `--no-uds` / `--abstract` to all primals | ironGate (primal workhorse) | MEDIUM |
| 5 | Android deploy script update for Tower 4-primal model | primalSpring (eastGate) | LOW |

---

## Device State After Deploy

```
$ adb shell pgrep -la 'beardog|songbird|skunkbat|swarmvine'
13672 beardog server --abstract --port 9100
13778 songbird server --port 7700 --listen 127.0.0.1:9200
13862 skunkbat server --port 9140 --no-uds
13891 swarmvine --gate-id grapheneGate --gossip-port 7800 ...
```

13 primal binaries on device (12 from depot + 1 cross-compiled swarmvine).
4 running (Tower Atomic). 2 missing entirely (biomeOS, cellMembrane).
