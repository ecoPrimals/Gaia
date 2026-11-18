# AAR: grapheneGate Full Deployment — Wave 107 (11/13 LIVE)

**Date**: 2026-06-10
**Team**: primalSpring + grapheneGate team on eastGate
**Device**: Pixel 8a (44251JEKB04957), GrapheneOS, aarch64
**Composition**: `--composition full` (all 13 NUCLEUS primals)
**Result**: **11/13 primals LIVE on TCP**, 2 blocked by fatal UDS bind paths

---

## Executive Summary

Second-generation grapheneGate deployment. Compared to Wave 105b first deploy (6/13),
this session achieved **11/13 primals running** on the Pixel 8a via TCP-only transport.
The remaining 2 failures (coralReef, biomeOS) expose a specific class of bug: **fatal
UDS bind in code paths that bypass `PRIMAL_BIND_MODE` checks**. All 11 running primals
respond on TCP JSON-RPC or HTTP, confirming the TCP-only fallback infrastructure works
when it reaches the transport layer.

---

## What Worked

### 1. Full 13/13 Binary Depot (aarch64-unknown-linux-musl)

All 13 primals built and staged in `plasmidBin/primals/aarch64-unknown-linux-musl/`.
Total depot size ~148MB. USB push at 120-330 MB/s. Complete push takes <2 seconds.

### 2. `PRIMAL_BIND_MODE` Environment Variable

The env-based transport selection (`tcp_only`, `fallback`) works for primals that check
it early in their transport resolution. coralReef's log explicitly shows:

```
PRIMAL_BIND_MODE=tcp_only — skipping UDS, binding TCP only
```

This confirms the primalSpring `BindMode` infrastructure propagates correctly into
primal codebases that adopted it.

### 3. `deploy_pixel.sh --composition full`

The deploy script's 6-phase flow (verify → push → generate → start → forward → probe)
handles all 13 primals. Phases 1-3 are reliable. Phase 4 correctly launches all processes.
The script's per-primal startup blocks allow targeted env overrides.

### 4. TCP JSON-RPC Health on 11 Primals

| Primal | Port | Protocol | Health Response |
|--------|------|----------|-----------------|
| beardog | 9100 | JSON-RPC | `{"primal":"beardog-tunnel","status":"alive","version":"0.9.0"}` |
| songbird | 9200 | HTTP | `200 OK` |
| skunkbat | 9140 | JSON-RPC | `{"status":"alive"}` |
| toadstool | 9400 | JSON-RPC | `{"status":"alive"}` |
| barracuda | 9740 | JSON-RPC | `{"status":"alive"}` (degraded: no GPU) |
| nestgate | 9500 | JSON-RPC | `{"status":"alive"}` (TCP via `NESTGATE_SOCKET=""` workaround) |
| rhizocrypt | 9602 | JSON-RPC | `{"status":"alive"}` (note: JSON-RPC on 9602, not 9601) |
| loamspine | 9700 | JSON-RPC | `{"status":"alive"}` |
| sweetgrass | 9850 | BTSP-gated | Process alive, rejects unauthenticated TCP (expected) |
| squirrel | 9300 | JSON-RPC | `{"alive":true,"version":"0.1.0"}` |
| petaltongue | 9900 | BTSP-gated | Process alive, PT-09 enforcement rejects plain JSON-RPC |

### 5. BTSP Enforcement on TCP

sweetGrass and petalTongue correctly enforce BTSP (Bear Trust Security Protocol) on
TCP connections. This is correct security behavior — unauthenticated JSON-RPC should
be rejected on TCP. On x86_64 gates these primals use UDS (which is implicitly
authenticated by filesystem permissions). On grapheneGate, BTSP TCP enforcement
becomes the authentication layer. This is the intended design.

### 6. NestGate `NESTGATE_SOCKET=""` Workaround

NestGate's isomorphic IPC wraps `io::Error` in multiple custom error types, preventing
`is_platform_constraint()` from downcasting. Setting `NESTGATE_SOCKET=""` bypasses
the UDS bind entirely (empty path → abstract namespace no-op), allowing the TCP
JSON-RPC path to succeed. This is a workaround, not a fix — nestGate should respect
`PRIMAL_BIND_MODE=tcp_only` at the isomorphic IPC level.

---

## What Didn't Work

### 1. coralReef: Fatal tarpc UDS Bind (CRASHED)

**Symptom**: coralReef starts, binds TCP JSON-RPC on 9730 successfully, then crashes
when tarpc tries to bind a UDS at `/data/local/tmp/biomeos/sockets/biomeos/coralreef-core-{family}-tarpc.sock`.

**Root Cause**: coralReef has two server paths:
- **JSON-RPC TCP** (newline-delimited): Respects `TRANSPORT_ENDPOINT` and `PRIMAL_BIND_MODE`.
  Log shows `"PRIMAL_BIND_MODE=tcp_only — skipping UDS, binding TCP only"`. Works.
- **tarpc** (binary RPC): Always binds a UDS regardless of `PRIMAL_BIND_MODE`. The bind
  fails with `EACCES` (Android SELinux) and the error is fatal — `process::exit(1)`.

**Fix Required** (coralReef team):
- When `PRIMAL_BIND_MODE=tcp_only`, skip tarpc server entirely (tarpc is UDS-only
  by design and has no TCP transport).
- Alternatively, make tarpc bind failure non-fatal when `PRIMAL_BIND_MODE != uds_only`.

**Severity**: P2 — coralReef's JSON-RPC TCP works perfectly; only tarpc (used for
high-performance binary RPC in local compositions) is blocked.

### 2. biomeOS: Fatal UDS Bind (CRASHED)

**Symptom**: biomeOS (Neural API) starts, logs configuration, then crashes on
`Failed to bind Unix socket: Permission denied (os error 13)`.

**Root Cause**: biomeOS's Neural API server unconditionally binds a UDS at
`/data/local/tmp/biomeos/biomeos/neural-api-{family}.sock` before starting TCP.
The UDS bind failure is fatal and not gated by `PRIMAL_BIND_MODE`.

Unlike coralReef (where the JSON-RPC TCP path works independently), biomeOS's server
architecture ties UDS and TCP together — if UDS fails, the entire server exits.

**Fix Required** (biomeOS team):
- Check `PRIMAL_BIND_MODE` before UDS bind. When `tcp_only`, skip UDS entirely.
- When `fallback`, catch UDS bind errors and continue with TCP-only.
- biomeOS v4.18's "native fallback" (referenced in docs) does not appear to be wired
  into the Neural API server's actual bind path.

**Severity**: P2 — biomeOS is the NUCLEUS orchestrator. Without it, grapheneGate runs
as a composition without orchestration. All other primals function independently.

### 3. NestGate: `is_platform_constraint()` Downcast Failure

**Symptom**: NestGate logs `"This is a real error, not a platform constraint"` despite
`PRIMAL_BIND_MODE=fallback` being set.

**Root Cause**: NestGate's isomorphic IPC wraps the `io::Error` from `bind()` in:
```
InternalErrorDetails → anyhow::Error → anyhow::Context → ...
```
The `is_platform_constraint()` function calls `error.downcast_ref::<std::io::Error>()`
which fails because the raw `io::Error` is buried inside a string-formatted error chain,
not preserved as a downcastable type.

**Fix Required** (nestGate team):
- Check `PRIMAL_BIND_MODE` directly in `is_platform_constraint()` before attempting
  `io::Error` downcast: `if is_bind_mode_tcp_only() { return true; }`.
- Or: preserve the raw `io::Error` through the error chain (use `#[source]` or
  `.context()` without consuming the error).
- **Workaround deployed**: `NESTGATE_SOCKET=""` bypasses UDS entirely.

### 4. ADB Port Forwarding Collision

**Symptom**: `adb forward tcp:9850 tcp:9850` fails with `Address already in use`.

**Root Cause**: Port 9850 was already bound locally (possibly from a previous deploy
or another service). The deploy script's Phase 5 doesn't check for local port conflicts.

**Fix Required** (plasmidBin):
- `deploy_pixel.sh` should check local port availability before forwarding.
- Use `--skip-forward` and let user handle port conflicts manually if needed.
- Not critical: ADB forwards work for 12/13 ports.

---

## Deployment Topology Learnings

### Android SELinux Substrate Model

GrapheneOS enforces a **restrictive SELinux policy** for ADB shell processes:
- UDS `bind()` → **DENIED** (in most paths, including `/data/local/tmp/`)
- UDS `connect()` → context-dependent (sometimes works for abstract sockets)
- TCP `bind()` → **ALLOWED** on `0.0.0.0:*` and `127.0.0.1:*`
- File create in `/data/local/tmp/` → **ALLOWED**
- File create in `/run/` → **DENIED** (read-only filesystem)

This means:
1. **TCP-only is the correct transport** for grapheneGate. UDS will never work reliably.
2. BTSP becomes the authentication layer (replaces filesystem permission checks of UDS).
3. Abstract namespace sockets (`\0name`) work inconsistently — some primals succeed
   (bearDog), some fail (nestGate with `--abstract`).

### Transport Tier Taxonomy (Refined)

| Tier | Transport | Auth | Where |
|------|-----------|------|-------|
| Tier 1 | UDS (filesystem) | Implicit (uid/gid) | x86_64 Linux gates |
| Tier 2 | UDS (abstract namespace) | Implicit (SELinux label) | Android with relaxed policy |
| Tier 3 | TCP + BTSP | Explicit (handshake) | grapheneGate, cross-gate mesh |
| Tier 4 | TCP unauthenticated | None | Development/debug only |
| Tier 5 | TCP fallback (PRIMAL_BIND_MODE) | Depends on primal | Mixed environments |

grapheneGate operates at **Tier 3** for primals that enforce BTSP (sweetGrass,
petalTongue) and **Tier 5** for primals that accept unauthenticated JSON-RPC on TCP.

### `PRIMAL_BIND_MODE` Adoption Matrix

| Primal | Reads env? | Respects tcp_only? | UDS skip works? | Status |
|--------|:----------:|:------------------:|:----------------:|--------|
| beardog | Yes | Yes | Yes | WORKS |
| songbird | N/A | N/A | HTTP-only | WORKS |
| skunkbat | Yes | Yes (`--no-uds`) | Yes | WORKS |
| toadstool | Yes | Yes | Yes | WORKS |
| barracuda | Yes | Yes (`--no-unix`) | Yes | WORKS |
| coralreef | **YES** | **Partial** (JSON-RPC yes, tarpc no) | No | BLOCKED |
| nestgate | Yes | **No** (error wrapping) | Workaround | WORKAROUND |
| rhizocrypt | Yes | Yes | Yes | WORKS |
| loamspine | Yes | Yes | Yes | WORKS |
| sweetgrass | Yes | Yes | Yes (BTSP-gated) | WORKS |
| biomeos | **No** | **No** | No | BLOCKED |
| squirrel | Yes | Yes | Yes | WORKS |
| petaltongue | Yes | Yes | Yes (BTSP-gated) | WORKS |

**10/13 fully respect `PRIMAL_BIND_MODE=tcp_only`.**
**1/13 partially (coralReef: JSON-RPC yes, tarpc no).**
**1/13 workaround (nestGate: env hack bypasses UDS).**
**1/13 blocked (biomeOS: doesn't check env at bind time).**

---

## Fixes Deployed (deploy_pixel.sh)

1. **nestgate**: Removed `--abstract` flag. Set `NESTGATE_SOCKET=""` + `NESTGATE_JSONRPC_TCP=1`
   + `--enable-http --listen 0.0.0.0:PORT`. Result: TCP-only, no UDS attempted.

2. **coralreef**: Added `PRIMAL_BIND_MODE=tcp_only` + `TRANSPORT_ENDPOINT` to TCP.
   JSON-RPC TCP works but tarpc crash is still fatal. Needs code fix.

3. **biomeos**: Added `PRIMAL_BIND_MODE=tcp_only` + `TRANSPORT_ENDPOINT`. Still crashes
   because Neural API server doesn't check env before UDS bind. Needs code fix.

---

## Upstream Action Items

### P2: coralReef — Make tarpc Bind Non-Fatal on tcp_only

**Owner**: coralReef team
**Issue**: tarpc server `bind()` failure calls `exit(1)`. When `PRIMAL_BIND_MODE=tcp_only`,
tarpc should be skipped entirely (tarpc is UDS-only, no TCP transport exists).
**Acceptance**: coralReef runs on grapheneGate with JSON-RPC TCP, tarpc gracefully disabled.

### P2: biomeOS — Respect PRIMAL_BIND_MODE in Neural API Server

**Owner**: biomeOS team
**Issue**: Neural API server always attempts UDS bind before TCP. Fatal on Android SELinux.
`PRIMAL_BIND_MODE=tcp_only` is not checked.
**Acceptance**: `biomeos neural-api --port 9800 --bind 0.0.0.0` starts TCP-only when
`PRIMAL_BIND_MODE=tcp_only`, without attempting UDS.

### P3: nestGate — Fix is_platform_constraint() Error Chain

**Owner**: nestGate team
**Issue**: `is_platform_constraint()` can't downcast `io::Error` from wrapped error chain.
**Workaround**: `NESTGATE_SOCKET=""` deployed in `deploy_pixel.sh`.
**Acceptance**: `PRIMAL_BIND_MODE=tcp_only` respected without env hacks.

### P3: plasmidBin — deploy_pixel.sh Port Conflict Check

**Owner**: cellMembrane (plasmidBin)
**Issue**: Phase 5 ADB port forwarding fails silently on port collisions.
**Acceptance**: Pre-check local port availability, skip or warn on conflict.

---

## Metrics

| Metric | Wave 105b | Wave 107 | Delta |
|--------|-----------|----------|-------|
| Primals running | 6/13 | **11/13** | **+5** |
| TCP health responding | 4/13 | **9/13** | **+5** |
| BTSP-enforced (alive but gated) | 0 | **2/13** | +2 |
| Binary depot complete | 13/13 | 13/13 | = |
| deploy_pixel.sh issues | 1 | 0 | -1 |
| UDS-blocked primals | 7/13 | **2/13** | **-5** |

### Composition Assessment

**11/13 = FULL NUCLEUS (near-complete)**

Missing coralReef degrades compute-layer provenance (reef graph analysis).
Missing biomeOS degrades orchestration (no NUCLEUS supervision on device).
All other capabilities are live: security (bearDog), federation (songBird),
trust (skunkBat), compute (toadStool+barraCuda), storage (nestGate+rhizoCrypt),
provenance (loamSpine+sweetGrass), UI (petalTongue), search (squirrel).

---

## Next Steps

1. **Upstream fixes** — File coralReef tarpc + biomeOS UDS bind issues as P2.
2. **13/13 validation** — After fixes, redeploy and validate full NUCLEUS on grapheneGate.
3. **Mesh integration** — grapheneGate as mesh peer (Tier 3 TCP + BTSP) connecting
   to eastGate hub via hotspot/WAN relay.
4. **Deployment matrix update** — Mark `graphenegate-aarch64-tcp-standalone` as
   `validated` with `primals = 11`.
5. **BTSP handshake validation** — Verify sweetGrass + petalTongue accept BTSP
   handshake over TCP (not just reject unauthenticated connections).

---

*Dissemination: overwatch → all gates via wateringHole temporal.cascade*
