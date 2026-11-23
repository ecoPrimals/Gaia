# Wave 79c Gate Blurbs — Remaining Work by Level

**Date**: 2026-06-05  
**From**: eastGate overwatch  
**Purpose**: Copy-paste blurbs for teams with pending action, organized by level  
**Context**: 10G backbone install across LAN gates this weekend (Jun 7-8)

---

## Level 1: Primals (P0 — blocks mesh.init)

---

### toadStool (biomeGate)

**Wave 79c status**: VPS binary rolled back (pre-refresh backup running)  
**Blocking**: 13/13 ALIVE → mesh.init → stadial gate entry

```
Error: Setup("No Akida devices found. Check lspci output.")
```

The HEAD build hard-fails on VPS at startup without Akida NPU hardware.
The pre-refresh binary runs fine in IPC-only mode.

**Action**: Add `--headless` or `--no-hardware` flag that skips the NPU
probe and starts the IPC server in pure-compute mode. The systemd unit
calls `toadstool server --socket /run/membrane/toadstool.sock` — this
path must work without hardware enumeration.

**Test**: `toadstool server --socket /tmp/test.sock --headless` starts
without error on a machine with no Akida/GPU.

**Deploy path**: Once fixed, rebuild musl-static and notify eastGate.
VPS refresh is now one command:
```bash
./deploy_membrane.sh refresh root@[RELAY_PUBLIC]
```

---

### coralReef (strandGate)

**Wave 79c status**: VPS binary rolled back  
**Blocking**: 13/13 ALIVE → mesh.init → stadial gate entry

```
Error: Cannot read ./specs/amd/amdgpu_isa_rdna2.xml
```

The HEAD build requires GPU ISA spec files at startup, even in `server`
mode. The shader compiler should only need specs when actually compiling.

**Action**: Lazy-load GPU ISA specs on first compile request, or add
`--headless` flag that skips spec loading. The IPC server must start
cleanly without GPU spec files on disk.

**Test**: `coralreef server --socket /tmp/test.sock` starts without
error when `./specs/` directory doesn't exist.

---

### squirrel (eastGate)

**Wave 79c status**: VPS binary rolled back  
**Blocking**: 13/13 ALIVE → mesh.init → stadial gate entry

```
error: unrecognized subcommand 'server'
```

The HEAD build only has CLI subcommands (`text-generation`,
`code-generation`, `list-models`, etc). The IPC `server` mode that
provides JSON-RPC over UDS was removed or never merged to main.

**Action**: Restore `server` subcommand (or add `ipc` subcommand) that
starts UDS JSON-RPC service mode at a given socket path.

**Test**: `squirrel server --socket /tmp/test.sock` starts UDS listener
and responds to `health.check`.

---

### skunkBat (eastGate)

**Wave 79c status**: ALIVE via TCP (localhost:9140), no UDS socket  
**Priority**: P1 (not blocking mesh.init, breaks UDS-only audit)

skunkBat is the only primal without `/run/membrane/skunkbat.sock`.
The binary has `--bind` and `--port` but no `--socket` flag for UDS.

**Action**: Add `--socket <PATH>` flag matching the pattern used by
bearDog, songBird, and all other primals. When `--socket` is provided,
TCP should be optional.

---

## Level 2: Primals (P1 — blocks full surface)

---

### cellMembrane (ironGate)

**Wave 79c status**: Caddy proxy PARTIALLY LIVE  
**Blocking**: auth.primal.eco, api.primal.eco, nestgate.io content

Three Caddy endpoints on golgiBody-ext return 503/placeholder because
the backends are on golgiBody inner (loopback/UDS only). DNS + TLS
are live for all three.

**Action**: Deploy cross-node forwarders (socat or SSH tunnel) from
golgiBody-ext to golgiBody inner for:

| Endpoint | Inner Backend |
|----------|---------------|
| auth.primal.eco | bearDog UDS → TCP bridge |
| api.primal.eco | biomeOS UDS → TCP bridge |
| nestgate.io | Forgejo 127.0.0.1:3000 |

See FRAGO `wave79c-cross-node-proxy` for options.

**10G note**: The 10G backbone install (Jun 7-8) doesn't affect the VPS
cross-node proxy — that's ext↔inner on the same DO private network.
But it will enable LAN gates to mesh directly at wire speed.

---

## Level 3: Primals (P2 — blocks stadial graduation)

---

### songBird (southGate)

**Wave 79c status**: All functional code LIVE, mesh.primal.eco proxied  
**Issue**: 73% test coverage vs 90% stadial target

songBird has the largest quantitative coverage gap. All critical code is
solid (SB-TLS-01, BD-TRUST-01, deep debt pass), but the 90% gate
requires a dedicated sprint.

**Action**: Coverage sprint targeting `songbird-tls`, `songbird-stun`,
and `songbird-discovery` crates.

**10G note**: Once mesh.init fires and LAN gates mesh at 10Gbps,
Songbird federation paths become testable under real load — additional
coverage opportunities from integration test scenarios.

---

## Level 4: Springs (P2 — parity gaps)

---

### Springs with missing `domain_profile.toml`

| Spring | Status |
|--------|--------|
| hotSpring (biomeGate) | Has nested compchem profiles, no root profile |
| ludoSpring (ironGate) | Missing — composition-only spring |
| neuralSpring (southGate) | Missing |

**Action**: Create root `domain_profile.toml` for `litho emit-pseudospore`
and ecosystem classification. Template available in any current spring
(e.g., `wetSpring/domain_profile.toml`).

---

### Lagging Springs (Tier 2-3 freshness)

| Spring | Gap | Action |
|--------|-----|--------|
| airSpring (eastGate) | Wave 60→79 (7d behind) | Trust pattern absorption when convenient |
| groundSpring (eastGate) | Wave 63→79 (6d behind) | Trust pattern absorption when convenient |

These are not blocking any gate or mesh work. Evolve on demand.

---

## Teams with NO pending work (current, no action needed)

- **bearDog** (southGate) — v0.9.0, ALIVE via UDS, BD-TRUST-01 resolved
- **biomeOS** (southGate) — ALIVE via UDS, 90%+ coverage
- **nestGate** (ironGate) — v0.5.0, ALIVE via UDS
- **rhizoCrypt** (strandGate) — v0.14.2, ALIVE via UDS
- **loamSpine** (strandGate) — ALIVE via UDS
- **sweetGrass** (strandGate) — v0.7.51, localhost fix RESOLVED, ALIVE via UDS
- **petalTongue** (ironGate) — ALIVE (health probe silent but socket active)
- **barraCuda** (strandGate) — ALIVE via UDS

---

## Weekend 10G Backbone Context

All LAN gates (eastGate, strandGate, westGate incoming) get 10Gbps
backbone Jun 7-8. This enables:

1. **LAN mesh at wire speed** — sub-ms latency between gates
2. **mesh.init with real bandwidth** — once 3 headless fixes land
3. **westGate enrollment** — FRAGO P1, joins mesh from day one at full speed
4. **WAN relay via golgiBody** — VPS stays the internet-facing peptidoglycan

Critical path: **3 headless fixes → redeploy → mesh.init → stadial**

---

*"The backbone is the spine. The mesh is the nervous system. Three primals need their headless mode."*
