# hotSpring Upstream Feedback — Graceful Ops & ecoBin Freshness

**Date**: May 14, 2026  
**From**: hotSpring team (downstream consumer of compute trio)  
**For**: primalSpring (ecosystem), toadStool/barraCuda/coralReef (compute trio)  
**Registry**: 427-method capability registry  

---

## Summary

hotSpring shipped local compute-trio integration (systemd units, upgrade
scripts, IPC auto-reconnect, stale socket cleanup) and identified three
upstream gaps that affect all downstream springs doing daemon management.

---

## Upstream Asks and Responses

### 1. ecoBin Pipeline Freshness

**Ask**: Springs can't tell if their local ecoBin matches the latest source.
`fetch.sh --release latest` should query GitHub API, each ecoBin should
embed build info, and a `doctor.sh --freshness` mode should report staleness.

**Response**:

| Item | Status | Details |
|------|--------|---------|
| `fetch.sh` GitHub API | **Already done** | `resolve_release_tag()` queries `api.github.com/repos/ecoPrimals/plasmidBin/releases/latest` — no local git dependency |
| `doctor.sh --freshness` | **Done** (May 14) | Compares local blake3 hashes against `checksums.toml` from the latest GitHub Release. Reports CURRENT/STALE per-primal. |
| `health.version` method | **Registered** (May 14) | Added to `capability_registry.toml` and `ipc/methods.rs`. Wire contract defined in `CAPABILITY_WIRE_STANDARD.md` (GD-01). Returns `version`, `build_hash`, `session`, `compiled_at`, `rust_version`. |
| Build hash embedding | **Upstream to primals** | Each primal's `build.rs` should embed `env!("GIT_HASH")` or equivalent. toadStool is the reference implementer. |

### 2. Graceful Drain / Hot Reload

**Ask**: `health.drain` method for graceful shutdown (stop accepting work,
wait for in-flight, return "ready to shutdown"). `health.version` for
post-upgrade verification. Eventually SIGUSR1 re-exec for zero-downtime.

**Response**:

| Item | Status | Details |
|------|--------|---------|
| `health.drain` registered | **Done** (May 14) | Added to `capability_registry.toml` (owner: `all`). Wire contract with request/response examples in `CAPABILITY_WIRE_STANDARD.md` (GD-01). |
| `health.version` registered | **Done** (May 14) | Same as above. |
| Upgrade sequence doc | **Done** (May 14) | Reference drain→stop→swap→start→verify sequence in `CAPABILITY_WIRE_STANDARD.md`. |
| Implementation in toadStool | **Upstream** | toadStool team owns implementing the actual drain logic. Wire contract is now defined. |
| SIGUSR1 re-exec | **Future** | Terminal architecture for zero-downtime. Can wait — drain+restart covers the 95% case. |

### 3. Socket Permissions Standardization

**Ask**: toadStool S259 added `TOADSTOOL_SOCKET_MODE`. All primals should
adopt `{PRIMAL}_SOCKET_MODE` as a convention.

**Response**:

| Item | Status | Details |
|------|--------|---------|
| Convention documented | **Done** (May 14) | `CAPABILITY_WIRE_STANDARD.md` Section SP-01: `{PRIMAL}_SOCKET_MODE` env var, octal string, default `0600`. |
| toadStool | **Done** (S259) | First adopter |
| barraCuda, coralReef | **Upstream** | Creates at user umask currently. Adopting SP-01 is one-line change. |

---

## What hotSpring Shipped (Local Solves)

All items are local to hotSpring and do NOT need upstream changes:

- `scripts/boot/barracuda.service` and `coralreef.service` — systemd units
  with stale socket cleanup, sandboxing, auto-restart
- `upgrade-toadstool.sh` — backup + rollback on failed binary upgrade
- `primal_bridge.rs` — IPC `call()` auto-reconnects once on connection
  errors (daemon restart survivability)
- 595 lib tests pass clean

---

## Remaining Upstream Work (Primal Teams)

| Item | Owner | Priority |
|------|-------|----------|
| Implement `health.drain` in toadStool | toadStool team | HIGH |
| Implement `health.version` in toadStool | toadStool team | HIGH |
| Embed build hash in all primal binaries | All primal teams | MEDIUM |
| Adopt `{PRIMAL}_SOCKET_MODE` in barraCuda | barraCuda team | LOW |
| Adopt `{PRIMAL}_SOCKET_MODE` in coralReef | coralReef team | LOW |
| SIGUSR1 re-exec (zero-downtime) | Ecosystem | FUTURE |

---

## Cross-References

- `CAPABILITY_WIRE_STANDARD.md` — SP-01 (socket mode), GD-01 (graceful drain)
- `capability_registry.toml` — `health.drain`, `health.version` (427 methods)
- `primalSpring/ecoPrimal/src/ipc/methods.rs` — `health::DRAIN`, `health::VERSION`
- `plasmidBin/doctor.sh --freshness` — ecoBin staleness report
- `fossilRecord/wateringHole/TOADSTOOL_S214_PG46_BTSP_PHASE3_HANDOFF_MAY01_2026.md` — original `TOADSTOOL_SOCKET_MODE` shipping note
