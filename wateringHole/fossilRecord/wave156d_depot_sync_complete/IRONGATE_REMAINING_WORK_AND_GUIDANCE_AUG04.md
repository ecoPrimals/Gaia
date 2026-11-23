# ironGate Remaining Work & Upstream Guidance

**Date**: 2026-08-04 13:32 EDT | **Wave**: 155v/156d | **Gate**: ironGate (10.13.37.7)
**From**: ironGate hardware team (local overwatch)
**Audience**: eastGate overwatch + all primal teams

---

## WHAT WE PROVED TODAY

**Phase 1 CELL BOOT: DONE.** `biomeos nucleus attach esotericwebb_cell.toml` succeeded
on ironGate — the first-ever live cell composition boot in the ecosystem.

| Milestone | Status | Evidence |
|-----------|--------|----------|
| biomeOS v4.57 built + deployed | DONE | Binary compiled, system service restarted |
| Cell graph parsed + validated | DONE | Dry-run passed, 5-phase graph with 8 nodes |
| Neural API pre-flight | DONE | composition.health contacted (returns "unknown") |
| graph.execute RPC | DONE | esotericwebb_cell attached to NUCLEUS |
| Post-boot validation | DONE | exp006 21/22 PASS, scene push FIRING, 0 failures |
| esotericWebb V30d tests | DONE | 465 lib + 18 integration + 1 doc PASS |
| footPrint tests | DONE | 708 PASS (53 test files) |
| K-derm DNS 3/3 | DONE | primals.eco (200), nestgate.io (200), primal.eco (SEALED) |
| GPU under load | DONE | RTX 5070 stable at 46°C, 571 MiB VRAM |

---

## REMAINING WORK ON IRONGATE

### Phase 2: footPrint Cell Boot

| Task | Owner | Blocker | Priority |
|------|-------|---------|----------|
| Copy `footprint_cell.toml` to `~/graphs/` and attach | ironGate hw | Cell graph must exist in biomeOS/graphs/ | P1 |
| BTSP local-trust (SO_PEERCRED) for CAS write | bearDog + nestGate | Code change upstream | **P1 — blocks write path** |
| Caddy routing: `footprint.primals.eco` → ironGate :3002 | sporeGate | DNS + Caddy block | P1 |
| Install systemd unit: `deploy/footprint.service` | ironGate hw | footPrint cell boot first | P2 |
| Test nestGate CAS persistence via Neural API | ironGate hw | BTSP local-trust | P2 |

### Phase 3: squirrel G18 Integration

| Task | Owner | Blocker | Priority |
|------|-------|---------|----------|
| Test `signal.dispatch` → `graph.execute` on ironGate | ironGate hw | Phase 1 done (cleared) | P2 |
| esotericWebb + footPrint as live dispatch targets | ironGate hw | Phase 2 | P2 |
| Validate 4-strategy dispatch cascade | ironGate hw | squirrel 156d validated | P2 |

### Infrastructure: Socket Path Migration

| Task | Owner | Priority |
|------|-------|----------|
| Migrate all primal systemd units from `/run/user/1000/biomeos/` to `/run/user/1000/membrane/` | ironGate hw + biomeOS | P2 |
| Or: teach v4.57 doctor to scan both paths | biomeOS team | P2 |
| Document migration path for other gates | biomeOS team | P3 |

### Infrastructure: Graph Runtime Location

| Task | Owner | Priority |
|------|-------|----------|
| Symlink `~/graphs → biomeOS/graphs/` or configure via env var | ironGate hw | P3 |
| Or: `nucleus attach` passes graph content inline instead of ID lookup | biomeOS team | P3 |

---

## UPSTREAM GUIDANCE BY TEAM

### biomeOS Team

**What we found**: v4.57 `nucleus attach` works end-to-end. Three issues:

1. **Socket path migration** (P2): v4.57 uses `/run/user/1000/membrane/`, old primals use
   `/run/user/1000/biomeos/`. `biomeos doctor` v4.57 only scans membrane dir, so it reports
   2/2 instead of 26/27. Other gates deploying v4.57 will hit this.
   - **Suggestion**: Add backward-compat scan of legacy `biomeos/` path, or ship migration
     docs for gate teams.

2. **composition.health** (P3): Returns "unknown" status. Pre-flight proceeds (correct
   behavior) but actual composition state should be wired. This would let dry-run give
   meaningful pre-flight feedback.

3. **Graph location** (P3): `graph.execute` looks in `~/graphs/` and `~/runtime_graphs/`.
   Cell graphs live in the biomeOS repo (`graphs/`). Consider:
   - `BIOMEOS_GRAPHS_DIR` env var
   - Systemd unit `Environment=BIOMEOS_GRAPHS_DIR=/path/to/graphs`
   - Or `nucleus attach` could embed graph content in the RPC payload

### bearDog Team

**What we need**: BTSP local-trust (SO_PEERCRED) for same-gate CAS write authentication.

footPrint needs to write project data to nestGate CAS. Both run on ironGate NUCLEUS.
The UDS connection is already established (riboCipher transport wired), but authenticated
writes need BTSP local-trust to prove the caller is a legitimate primal on the same gate.

- **Use case**: footPrint → nestGate `content.put` on same NUCLEUS
- **Mechanism**: `SO_PEERCRED` on UDS to verify UID/PID match
- **Priority**: P1 — blocks footPrint Phase 2 write path

### nestGate Team

**What we need**: Two things:

1. **CAS write via Neural API** (P1): footPrint should write via `neural-api-default.sock`
   → biomeOS routes to nestGate. This follows the Neural API routing pattern from the
   three-domain topology spec. Needs BTSP local-trust from bearDog.

2. **content.query API** (P2): DIV-2 from nestgate.io work. No query-by-tag API exists.
   footPrint and tideGlass will need this for dataset discovery.

### petalTongue Team

**What we proved**: G19 scene push PROVEN on ironGate RTX 5070. petalTongue receives
game scenes from esotericWebb via `visualization.render.scene`. 

**What's next**:
- footPrint GIS rendering via petalTongue (map tiles, Leaflet integration)
- TCP bind hardening landed (127.0.0.1 default) — correct for ironGate deployment
- Family ID unification landed — zero raw `FAMILY_ID` reads

### squirrel Team

**What's ready**: squirrel 156d validated on ironGate. Socket healthy. 4,613 tests.
27 deprecated aliases removed.

**What's next**: G18 signal dispatch integration testing with real consumers (esotericWebb
and footPrint) on ironGate. This is the first time `signal.dispatch` → `graph.execute`
will have actual application targets, not mocks.

### sporeGate Team

**What we need**:
1. **Caddy routing** for `footprint.primals.eco` → ironGate 10.13.37.7:3002 (P1)
   - Caddy snippet already exists: `deploy/caddy-footprint-api.snippet`
   - WebSocket paths (`/ws`, `/ws/bridge`) need proxying too
   - Wildcard `*.primals.eco` means just add a Caddy block, no DNS change

2. **dnsmasq deployment** for `primal.eco` inner membrane resolution on gates (P2)
   - Config exists: `primal-eco.dnsmasq.conf`
   - ironGate needs to resolve `primal.eco` to LAN/mesh IPs

### songBird Team

**What works**: 22 drawbridge bonds, content.get dispatch validated. Mesh connectivity
to sporeGate (73ms) and golgi confirmed.

**What's next**: Inter-gate `content.get` E2E test (Phase 5). songBird probes ready,
nestGate content.fetch ready. This unblocks healthSpring + lithoSpore on ironGate.

### cellMembrane Team

**What's missing**: `network.sock` — the 1 missing socket out of 27. Non-blocking
for current work but needed for 27/27 health.
- **Issue**: UDS permission for non-root access
- **Priority**: P3

---

## IRONGATE STATUS SUMMARY FOR OVERWATCH

```
PHASE 1: DONE     esotericWebb cell boot — first-ever in ecosystem
PHASE 2: BLOCKED  footPrint — BTSP local-trust + Caddy routing
PHASE 3: READY    squirrel G18 — preconditions met, awaiting Phase 2
PHASE 4: N/A      westGate science springs (not our gate)
PHASE 5: BLOCKED  Inter-gate mesh — awaiting content.get E2E

HARDWARE:  NOMINAL  i9-14900K + RTX 5070 + 94 GB + 3.4 TB
NUCLEUS:   v4.57    13/13 primals, cell attached
TESTS:     ALL PASS esotericWebb 482 + footPrint 708 + exp006 21/22
K-DERM:    3/3      primals.eco + nestgate.io + primal.eco
```

### Priority Stack for Upstream

1. **P1**: BTSP local-trust (SO_PEERCRED) — unblocks footPrint CAS write
2. **P1**: Caddy routing for `footprint.primals.eco` — unblocks footPrint public access
3. **P1**: `footprint_cell.toml` in biomeOS/graphs/ — unblocks Phase 2 cell boot
4. **P2**: Socket path migration docs — all gates need this for v4.57
5. **P2**: `content.query` API in nestGate — dataset discovery
6. **P2**: dnsmasq deployment for `primal.eco` — inner membrane resolution
7. **P3**: `composition.health` wiring — meaningful pre-flight status
8. **P3**: `network.sock` UDS permissions — 27/27 health

---

*ironGate hardware team. Phase 1 COMPLETE. The cell deployment pipeline works. The
ecosystem has its first live consumer environment. We're ready for Phase 2 as soon
as BTSP local-trust and Caddy routing clear upstream.*
