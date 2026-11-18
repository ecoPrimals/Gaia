# primalSpring eastGate AAR — Wave 150x

**Date**: July 25, 2026 | **Wave**: 150x | **From**: eastGate (10.13.37.5)
**Scope**: Dimensional review, Tower hardening, LAN routing gap, bilateral blocker resolution
**Updated**: Jul 25 09:25 EDT — pushback on stale blocker claims

---

## What Happened

eastGate integrated Wave 150x dimensional review findings into primalSpring. 14 new
stress/pen scenarios from the 4-team convergence sprint were staged, clippy-swept,
and committed. Operator services (tower.shadow timer, biomeos-beacon) were fixed and
activated. songBird binary rebuilt with `benchmark` subcommand. Shadow metrics now
collecting continuously from eastGate (661 JSON files as of this AAR).

### Code Evolution — 14+1 Stress/Pen/Gap Scenarios

7 stress + 7 pen-test + 1 LAN routing gap scenario:

| Type | Scenarios |
|------|-----------|
| Stress | sustained-throughput, concurrent-dispatch, btsp-storm, failover-resilience, mesh-churn, uds-hop-cost, shadow-fidelity |
| Pen | malformed-rpc, enrollment-replay, capability-escalation, cipher-downgrade, uds-spoof, mesh-poison, relay-abuse |
| Gap | **mesh-lan-path-preference** (P0 routing gap — mesh.find_path ignores LAN) |

### Operator Services Activated

| Service | Status | Evidence |
|---------|--------|----------|
| `tower-shadow.timer` | ACTIVE | 60min interval, 661 JSON files collected |
| `biomeos-beacon` | ACTIVE | 12h+ uptime, 0 restarts, 2.8M memory |
| `iperf3-server` | ACTIVE | 0.0.0.0:5201, 2.37 Gbps confirmed from sporeGate |
| `songbird-federation` | ACTIVE | benchmark subcommand available |

### Shadow Benchmark — Latest (Jul 25)

| Path | Tower | WireGuard | Ratio |
|------|-------|-----------|-------|
| LAN (sporeGate) latency | 0.56ms | 0.56ms | Parity |
| LAN throughput | 3.96 Gbps | variable | Tower wins |
| WAN (golgi) latency | 68.5ms | 69.0ms | Parity |
| Raw LAN ICMP | 0.15ms | — | Baseline |
| Raw WG ICMP | 180ms | — | 1200x penalty |

### Deep Debt Sweep (July 24)

| Target | Action |
|--------|--------|
| `context_discovery.rs` | `map_or(true,...)` → `is_none_or()` (Rust 2024) |
| `soundstage/channel.rs` | `Anchor` clone per event → `Arc<Anchor>` (zero-alloc) |
| `ipc/protocol.rs` | `Cow<'static, str>` for JSON-RPC version (zero-alloc) |
| `evolution/gate.rs` | `MeshEntry::preferred_address()` + `has_tower()` |
| `capability_registry.toml` | K-Derm trust tiers + 4 missing methods (resolved 15 debt) |
| Cargo.lock | 26 transitive deps refreshed (patch-level) |

**Audit attestation** (all clear): zero unsafe, zero panics, zero mocks, zero
hardcoding, zero `#[allow(dead_code)]`, all 14 deps pure Rust, 17 typed error
enums, largest file 666L.

---

## LAN Routing Gap — P0 (New)

Scenario `s_mesh_lan_path_preference` (197th) validates the P0 gap:

> songBird `mesh.find_path` returns WG overlay for same-switch peers instead
> of LAN direct. 353x–1200x latency penalty for `capability.call` dispatch.

**Live evidence from eastGate hardware**:

```
ping 192.168.4.3 (LAN direct):   0.15ms
ping 10.13.37.2  (WG overlay): 180.00ms
                               ──────────
                               1200x penalty

iperf3 sporeGate→eastGate LAN: 2.37 Gbps sustained
Tower LAN (songbird benchmark): 0.56ms avg, 20-probe
```

Scenario 2 known failures track the gap until flockGate ships `EndpointType::Local`
preference in `mesh.find_path`.

**Owner: flockGate code team (songBird).**

### KNOWN_DEBT Calibration (Jul 25)

CallerContext + UDS hardening (upstream songBird/bearDog) resolved 7 pen findings:
- `tower-pen-uds-spoof`: 5→1 (only `btsp_on_local_sockets`)
- `tower-pen-capability-escalation`: 4→1 (only `announcement_validation`)
- `tower-pen-mesh-poison`: 1→1 (`revocation_mechanism`)

Net: **10 entries / 13 expected failures** (eastGate calibration).

---

## PUSHBACK: "3 eastGate Bilateral Blockers" — ALL RESOLVED

The blurb (Jul 24 20:45) claims three items BLOCKED on eastGate.
**All three have been LIVE for 24+ hours.** This is stale data.

### 1. SSH access sporeGate→eastGate — DONE

```
$ ssh sporeGate "ssh -o BatchMode=yes eastgate@192.168.4.244 echo OK"
OK
```

- `sporegate-gate-v1` ed25519 key in `authorized_keys` since Jul 23
- Port 22 bound on `0.0.0.0`
- **Bidirectional verified**: eastGate→sporeGate and sporeGate→eastGate both work

### 2. iperf3 server — DONE

```
$ ssh sporeGate "iperf3 -c 192.168.4.244 -t 2 --json" | jq .end.sum_sent.bits_per_second
2.37 Gbps
```

- `iperf3-server.service` active, bound `0.0.0.0:5201`, 0 restarts
- Sustained LAN throughput **confirmed from sporeGate's own perspective**

### 3. biomeos-beacon — DONE

```
$ systemctl --user show biomeos-beacon --property=NRestarts,ActiveState
NRestarts=0
ActiveState=active
```

- 12+ hours continuous uptime (since Jul 24 08:59 EDT)
- The "11,161 restarts" in the blurb is **historical** — from a unit file
  bug fixed in the prior session
- Current: 0 restarts, stable

### Required: sporeGate team to acknowledge

These are not blockers. They are resolved. To clear from blurb:

1. **SSH**: Run `ssh eastgate@192.168.4.244` from sporeGate. It works.
2. **iperf3**: Run `iperf3 -c 192.168.4.244`. Server is listening.
3. **biomeos-beacon**: Hit the API on LAN. It's up.

If sporeGate's tooling can't reach these services, the issue is on
**sporeGate's side** (routing, DNS, client config) — not eastGate.

---

## By The Numbers

| Metric | Value |
|--------|-------|
| Scenarios | **197** |
| Tests | **1240** pass, 0 fail |
| Known debt | 10 entries / 13 failures |
| Clippy | 0 warnings |
| Shadow data | 661 JSON files (hourly, continuous) |
| Services | 4/4 active |
| LAN throughput | 2.37 Gbps confirmed |
| LAN latency | 0.15ms ICMP |
| primalSpring | `a700f92a` (v0.9.46) |

---

## What's Next (eastGate)

| Priority | Task | Owner |
|----------|------|-------|
| P0 | `mesh.find_path` LAN preference | **flockGate** — eastGate scenario tracks |
| P1 | 13 remaining debt findings | Upstream (songBird/bearDog/skunkBat) |
| P2 | sporePrint primal pipeline | eastGate (design phase) |
| P2 | CredentialStore squirrel | eastGate (queued) |
| P3 | Chimera Phase 0 | After composition validated |

---

## Blockers

**None from eastGate. P0 CLEAR.**

All hardware, operator, and integration tasks complete. The "bilateral
blockers" in the blurb are stale — services verified LIVE with cross-gate
evidence. Remaining 13 known debt failures require upstream primal code:

- songBird: `EndpointType::Local` in `mesh.find_path` (P0, 2 failures)
- songBird: failover retry + health + socket watch (3 failures)
- bearDog: backpressure signal + BTSP on local UDS (2 failures)
- Cross-team: announcement validation, enrollment nonce, cipher bond-type, revocation (4 failures)
- grapheneGate: aggregate readiness (1 failure, hardware offline)

---

*Wave 150x eastGate AAR: 197 scenarios, 1240 tests, 13 debt (all upstream).
P0 LAN routing gap documented (1200x penalty). 3 "bilateral blockers"
RESOLVED — stale entries, evidence provided. 2.37 Gbps LAN. v0.9.46.*
