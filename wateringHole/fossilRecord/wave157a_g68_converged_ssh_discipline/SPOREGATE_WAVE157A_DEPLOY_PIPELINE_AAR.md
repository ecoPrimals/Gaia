# AAR: Wave 157a sporeGate Deploy Pipeline

**Date**: Aug 8, 2026 | **Gate**: sporeGate | **Author**: eastGate overwatch
**Scope**: Full audit of what works, what needs evolution in deployment and primals

---

## WHAT WORKS

### Primals — 13/13 ALIVE (first time at full health)

| Primal | Version | Status | Notes |
|--------|---------|--------|-------|
| biomeOS | 4.57.0 | ALIVE | Stage 2 routing infra (riboCipher pool, auto-transition, TOML caps) |
| bearDog | 0.9.0 | ALIVE | Sovereign cryptography |
| rhizoCrypt | 0.14.17 | ALIVE | CAS/provenance |
| squirrel | 0.1.0 | ALIVE | Agent routing |
| barracuda | — | ALIVE | ComputeDispatch P0 (−10K LOC) |
| coralReef | — | ALIVE | GPU compiler |
| loamSpine | — | ALIVE | Spine operations |
| nestGate | — | ALIVE | Content gateway |
| petalTongue | — | ALIVE | Web + IPC dual-port |
| skunkBat | — | ALIVE | Protocol negotiation |
| songBird | — | ALIVE | Mesh orchestration |
| sweetGrass | — | ALIVE | Ledger |
| toadStool | — | ALIVE | Hardware abstraction (socket fix ephemeral) |

### Cascade Timer — OPERATIONAL

- systemd user timer: 15min cycle, persistent across reboots
- G68 membrane binary (`60b0f8b`) with DIV-7 fixes
- `synced=15 failed=0` — zero drift across all repos
- Auto-publishes `heads/sporeGate.toml` to Forgejo
- Auto-detects drift, auto-harvests drifted primals, stages to local depot

### Depot — CURRENT

- **golgi musl**: 17/17 binaries (15 primals + membrane + nucleus_launcher)
- **golgi Windows**: 14/15 (squirrel cross-arch pending)
- All binaries at Forgejo HEAD as of Aug 7
- blueGate established as primary Windows builder

### G68 Platform Substrate — 14/15 PROD-CLEAN

- sourDough scanner v2 (`1cbac92`) with prod/test split
- Only toadStool has real production violations (24 L3 device backends)

---

## WHAT NEEDS EVOLUTION

### 1. DEPLOYMENT — currently manual scripting, should be `membrane` commands

**Current process** (manual, error-prone, ~10 min):
```
1. Stop NUCLEUS target
2. Kill straggler processes
3. Unlink old binaries (handles "text file busy")
4. Copy depot binaries to install dir
5. Restart NUCLEUS target
6. Fix toadstool socket permissions
7. Verify health
```

**membrane already has these commands** (unused):
```
plasmid.harvest --push          # build + stage + push to VPS
plasmid.push                    # push local depot to VPS
plasmid.depot_sync --push       # sync depot to VPS
temporal.cascade --with-harvest --with-rebuild --with-restart
                                # full autonomous cycle
caddy.depot.provision           # WAN binary distribution
```

**Evolution needed**:
- Wire `temporal.cascade --with-harvest --with-rebuild` into the systemd timer
- Test `plasmid.push` for local→golgi automated sync
- The cascade already harvests locally; adding `--with-rebuild` would auto-deploy
- The cascade timer ExecStart just needs the extra flags

**Risk**: auto-deploy without human verification could deploy broken binaries. Consider a `--with-sandbox` gate that validates health before promoting.

### 2. SOCKET PERMISSIONS — ephemeral fix

**Problem**: toadStool socket created as `srw-rw---- root:root`. Our fix (`chgrp sporegate`) reverts on service restart.

**Permanent fix options**:
- Add `Group=sporegate` to `/etc/systemd/system/membrane-toadstool.service`
- biomeGate ships B1/B2 socket permissions fix (toadStool creates socket with group-connectable mode)
- Add `ExecStartPost=/bin/chmod 660 /run/membrane/toadstool.sock && /bin/chgrp sporegate /run/membrane/toadstool.sock` to the service unit

**Recommendation**: Add `ExecStartPost` now as a gate-local fix. Let biomeGate ship the proper fix upstream.

### 3. GATE MESH CONNECTIVITY — only blueGate reachable

| Gate | SSH | WG (10.13.37.x) | Status |
|------|-----|-----------------|--------|
| sporeGate | local | .2 | Active (self) |
| blueGate | OK | — | Windows builder, reachable |
| golgi | OK (root@[RELAY_PUBLIC]) | .1 (root@) | VPS, reachable |
| ironGate | unreachable | .3 unreachable | LAN gate, needs WG or local route |
| westGate | unreachable | .4 unreachable | LAN gate |
| strandGate | unreachable | .5 unreachable | GPU gate |
| flockGate | unreachable | .6 unreachable | WAN gate |
| southGate | unreachable | .7 unreachable | Portability gate |

WireGuard peers only go through golgi (.1) as hub. LAN gates (.3-.7) are not directly routed. This means:
- **Cannot remotely deploy to any gate except golgi and blueGate**
- **Cannot verify health on other gates**
- Gate teams must self-deploy from golgi depot

**Evolution needed**:
- Establish WG peer routes for LAN gates (ironGate, westGate, strandGate)
- Or: use golgi as a jump host for SSH ProxyJump
- Or: transition to Tower Atomic (songBird mesh) for gate-to-gate communication
- Long-term: `membrane gate.deploy <gate>` that routes through the mesh

### 4. CELLMEMBRANE BOOTSTRAP — solved but fragile

The cascade timer runs the depot membrane binary. When cellMembrane advances, the old binary can't self-update. We fixed this manually (rebuilt + staged `60b0f8b`).

**Evolution needed**:
- `temporal.cascade --self-update` flag that checks cellMembrane drift and rebuilds membrane before running the cascade
- Or: the cascade should detect that its own binary is stale and fire an impulse

### 5. TOADSTOOL MUSL VFIO REGRESSION

`akida-driver/src/mmio.rs:191` — `VFIO_DEVICE_GET_REGION_INFO` is `u64` but musl `libc::ioctl` expects `i32`. S363 introduced this regression.

**Owner**: toadStool team. **Fix**: `as i32` cast or `c_ulong` type alias. Non-blocking for deployment (pre-S363 binary deployed).

### 6. SQUIRREL WINDOWS CROSS-ARCH

Fails on blueGate with `typenum`/`scopeguard`/`memchr` errors. Other 14 primals build fine.

**Owner**: eastGate team. **Note**: squirrel builds fine for musl on sporeGate. The Windows issue is in the dependency graph's cross-compilation, not squirrel code itself.

### 7. GOLGI PUSH AUTOMATION

Cascade stages locally but doesn't push to golgi. `plasmid.push` and `plasmid.depot_sync --push` exist but aren't wired into the cascade.

**Evolution needed**:
- Add `--push` flag handling to cascade timer
- Or: separate systemd timer for periodic `plasmid.depot_sync --push`

---

## DEPLOYMENT TAKEOVER — FOCUS AREAS

For new gate deployments to be self-service, these need to converge:

### Phase 1: sporeGate self-deploy (immediate)
- [x] Cascade timer fires and detects drift
- [x] Auto-harvest + local depot staging
- [ ] Wire `--with-rebuild` into cascade timer (auto-deploy after harvest)
- [ ] Make toadStool socket fix permanent (ExecStartPost or upstream)
- [ ] Test `plasmid.push` for golgi sync

### Phase 2: Gate deployment from golgi (near-term)
- [ ] Establish WG routes to LAN gates (or ProxyJump via golgi)
- [ ] Test `membrane plasmid.harvest --push` from sporeGate → golgi
- [ ] Each gate team runs `plasmid.depot_sync` to pull from golgi
- [ ] Document gate-local deploy procedure

### Phase 3: Autonomous mesh deploy (future)
- [ ] songBird mesh.publish broadcasts depot freshness
- [ ] Gates auto-pull from golgi when freshness heads diverge
- [ ] Tower Atomic replaces WG for gate connectivity
- [ ] `membrane gate.deploy <gate>` via mesh routing

---

## METRICS

| Metric | Value |
|--------|-------|
| sporeGate health | **13/13 ALIVE** |
| biomeOS version | **4.57.0** (Stage 2) |
| Cascade timer | **OPERATIONAL** (G68 membrane, synced=15) |
| Golgi depot | musl 17/17, Windows 14/15 |
| G68 prod-clean | **14/15** |
| Gate connectivity | **2/7** (sporeGate + blueGate, golgi via SSH) |
| Active impulses | **0** (7 resolved) |
| Deploy automation | **partial** — cascade syncs + harvests, but deploy + push manual |

---

*Wave 157a AAR — 13/13 ALIVE on sporeGate (first time). Cascade timer operational with G68 membrane. Deployment works but is manual scripting; membrane already has `plasmid.harvest --push`, `plasmid.depot_sync`, and `temporal.cascade --with-rebuild --with-restart` that should be wired in. Gate mesh limited to blueGate + golgi. toadStool socket fix ephemeral. Deployment takeover requires: cascade with `--with-rebuild`, permanent socket fix, gate WG routes, and eventual mesh deploy via Tower Atomic.*
