# Wave 80 Blurbs — Primals → Springs → Gates

**Date**: 2026-06-06  
**From**: eastGate overwatch  
**Purpose**: Copy-paste blurbs for teams with pending action  
**Context**: Cross-node proxy COMPLETE (5/5 Caddy endpoints LIVE). 10G backbone installed. squirrel/coralReef/skunkBat RESOLVED. primalspring_primal deprecated. Full pipeline validated. 1 headless fix remains (toadStool).

---

## Primals (P0 — blocks mesh.init)

---

### toadStool (biomeGate)

Wave 80: Your VPS binary is rolled back to pre-refresh backup (working in
IPC-only mode). The HEAD build hard-fails without Akida NPU:

```
Error: Setup("No Akida devices found. Check lspci output.")
```

**Action**: Add `--headless` or `--no-hardware` flag that skips NPU probe
and starts the IPC server in pure-compute mode. The systemd unit calls
`toadstool server --socket /run/membrane/toadstool.sock` — must work
without hardware enumeration.

**Test**: `toadstool server --socket /tmp/test.sock --headless` starts
clean on a machine with no Akida/GPU.

**Deploy**: Rebuild musl-static, notify eastGate. VPS refresh is one command:
`./deploy_membrane.sh refresh root@[RELAY_PUBLIC]`

**Blocking**: 13/13 ALIVE → mesh.init → stadial gate entry.

---

### ~~coralReef~~ (strandGate) — RESOLVED

Root cause: workspace `cargo build` was building `amd-isa-gen` tool (needs
`./specs/`) instead of the `coralreef` server binary. Fixed via
`default-members` in workspace `Cargo.toml`. Server binary never required
spec files at startup. Rebuilt and harvested — checksum unchanged.

---

### ~~squirrel~~ (eastGate) — RESOLVED

Root cause: wrong binary was deployed (CLI-only variant). The correct
`squirrel` binary with `server` subcommand exists at commit `5dea2cc6`.
Rebuilt from correct binary — checksum unchanged.

---

### ~~skunkBat~~ (eastGate) — RESOLVED

v0.2.6 ships `--socket` flag with implicit `--no-tcp` (ecosystem
convention). VPS binary rebuilt and harvested. Systemd unit update:
`ExecStart=/opt/membrane/skunkbat server --socket /run/membrane/skunkbat.sock`

---

## Primals (P2 — coverage)

---

### songBird (southGate)

Wave 80: All functional code LIVE, mesh.primal.eco proxied, deep debt
pass absorbed. 73% test coverage vs 90% stadial target.

**Action**: Coverage sprint targeting `songbird-tls`, `songbird-stun`,
and `songbird-discovery` crates. With 10G backbone live, federation
paths are now testable under real LAN load — integration test
opportunities.

---

## Primals (current — no action needed)

bearDog, biomeOS, nestGate, rhizoCrypt, loamSpine, sweetGrass,
petalTongue, barraCuda — all ALIVE via UDS, no pending work.

---

## Springs

---

### Missing `domain_profile.toml` (3 springs)

| Spring | Gate | Status |
|--------|------|--------|
| hotSpring | biomeGate | Has nested compchem profiles, no root profile |
| ludoSpring | ironGate | Missing — composition-only spring |
| neuralSpring | southGate | Missing |

**Action**: Create root `domain_profile.toml` for `litho emit-pseudospore`
and ecosystem classification. Template available in any current spring
(e.g., `wetSpring/domain_profile.toml`).

**Priority**: P2 — not blocking mesh or gates, needed for stadial graduation.

---

### Lagging Springs (Tier 2-3 freshness)

| Spring | Gate | Gap | Action |
|--------|------|-----|--------|
| airSpring | eastGate | Wave 60→80 | Trust pattern absorption when convenient |
| groundSpring | eastGate | Wave 63→80 | Trust pattern absorption when convenient |

**Priority**: P3 — evolve on demand, not blocking any gate or mesh work.

---

## Gates

---

### westGate — Enrollment (P1)

10G backbone is INSTALLED. westGate enrollment is unblocked on the
network side. skunkBat UDS support (P1 above) is the only primal
dependency.

**FRAGO**: `wave73-westgate-skunkbat-enrollment`

**Steps** (once hardware arrives):
1. Clone ecoPrimals tree
2. Install plasmidBin: `cargo install --path infra/plasmidBin`
3. `nucleus_launcher start --family-id westgate --federation-port 7700 --peers east-gate@192.168.1.144:7700,strand-gate@192.168.1.132:7700`
4. mesh.init auto-exchanges trust via BD-TRUST-01 (zero operator)
5. Verify: `discovery.peers` returns 2+ peers

10G backbone enables LAN mesh at wire speed — sub-ms latency between gates.

---

### cellMembrane — Infrastructure (P1)

Wave 80 status: Cross-node proxy COMPLETE, 5/5 Caddy endpoints LIVE.
All sovereign infrastructure functional.

**Remaining**:
- auth.primal.eco / api.primal.eco serve raw JSON-RPC over socat bridge
  — HTTP adapter or Caddy L4 plugin needed for proper HTTP-wrapped
  JSON-RPC if browser/curl clients expected
- Cloudflare → sovereign content cutover (after mesh.init proof)

---

### golgiBody VPS — mesh.init (blocks stadial)

**Ready once 3 headless fixes land**:
```bash
ssh root@[RELAY_PUBLIC] "/opt/membrane/songbird mesh.init \
  --peers east-gate@<eastGate-IP>:7700,strand-gate@<strandGate-IP>:7700"
```

This triggers BD-TRUST-01 auto trust seeding. 13/13 ALIVE + mesh.init
= stadial gate entry. 10G backbone enables the LAN legs at wire speed.

---

## Critical Path Summary

```
1 headless fix (toadStool NPU)
  → redeploy all 13 via deploy_membrane.sh refresh
    → 13/13 ALIVE
      → mesh.init with gate peers
        → 3-gate mesh proof (east+strand+VPS)
          → stadial gate entry
            → westGate enrollment (4th gate)
```

**S4 Auth 7-day gate**: Started Jun 2, ends ~Jun 9.

---

*"Five endpoints live. Twelve primals ready. One toadstool needs its headless mode. The glacier waits for no one."*
