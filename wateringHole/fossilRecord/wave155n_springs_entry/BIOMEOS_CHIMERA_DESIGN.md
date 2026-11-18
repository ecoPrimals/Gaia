# biomeOS Chimera Design — Tower Atomic Process Collapse

**Date**: Jul 23, 2026 | **Wave**: 150w | **From**: eastGate overwatch
**Status**: Design document — informed by stress/pen test scenario analysis

---

## What Is the Chimera?

The biomeOS chimera is the end-state Tower Atomic: a **single process**
where bearDog's cryptography, songBird's routing, and skunkBat's defense
share memory instead of communicating over UDS JSON-RPC sockets.

```
BEFORE (current):                      AFTER (chimera):

  ┌─bearDog─┐  ┌─songBird─┐            ┌─ biomeOS Chimera ─────────┐
  │ crypto   │  │ routing   │            │                           │
  │ BTSP     │  │ dispatch  │            │  crypto   ← fn call       │
  │ keys     │  │ mesh      │            │  routing  ← fn call       │
  └──UDS─────┘  └──UDS──────┘            │  defense  ← fn call       │
       ↑              ↑                  │  registry ← shared memory │
  ┌─skunkBat─┐       │                  │                           │
  │ defense   │       │                  │  UDS server (external)    │
  │ method    │       │                  │  TCP server (mesh)        │
  │ gate      │       │                  └───────────────────────────┘
  └──UDS──────┘───────┘
```

## Why Collapse?

### Evidence from Composition Cost Map

| Current Path | UDS Hops | Cost (LAN) | Chimera Cost | Savings |
|-------------|----------|-----------|-------------|---------|
| capability.call (local) | 2 | ~0.30ms | ~0.01ms | **97%** |
| capability.call (remote) | 4 + TCP | ~0.60ms + RTT | ~0.02ms + RTT | **97% IPC** |
| BTSP session setup | 3 | ~0.45ms | ~0.03ms | **93%** |
| enrollment.verify | 1 | ~0.15ms | ~0.005ms | **97%** |
| Full secured remote call | 7 + TCP | ~1.05ms + RTT | ~0.05ms + RTT | **95% IPC** |

On LAN (0.17ms RTT), IPC overhead is **3.5× the network cost**. The
chimera eliminates this, making network RTT the sole latency factor.

### Evidence from Stress Test Findings

The stress scenarios identified these UDS-related vulnerabilities that
the chimera inherently solves:

1. **No connection pooling** (`tower-stress-concurrent-dispatch`):
   Per-request UDS connect/disconnect creates contention. In-process,
   this becomes a function call — no connect overhead.

2. **No rate limiting on bearDog** (`tower-stress-btsp-storm`):
   External UDS connections to bearDog are unbounded. In-process,
   handshake is a function call gated by the chimera's own admission
   control.

3. **bearDog death kills crypto** (`tower-stress-failover-resilience`):
   Separate process means separate failure domain. In-process, crypto
   module failure is a panic that kills the whole chimera — but it also
   eliminates the "dead socket, no retry" problem.

4. **Socket filesystem trust** (`tower-pen-uds-spoof`): UDS sockets
   are spoofable via symlink replacement. In-process, there is no socket
   to spoof — crypto is a direct function call.

### Evidence from Pen Test Findings

Security improvements from chimera architecture:

| Pen Test Finding | Current Risk | Chimera Mitigation |
|-----------------|-------------|-------------------|
| UDS socket spoofing | Any local process can impersonate bearDog | No external socket for crypto — can't spoof |
| No peer credential check | SO_PEERCRED not verified | N/A — in-process |
| TOCTOU symlink race | Between discover and connect | No discover step |
| No identity probe | Trust-on-connect | N/A — in-process identity is self |
| Enrollment replay | No timestamp window | Same code, but can add in-memory replay cache trivially |

## Architecture Requirements

### R1: Shared Crypto Module (bearDog → library)

Extract bearDog's core crypto into a Rust library crate:

```
beardog-crypto-lib/
├── src/
│   ├── btsp/        # Session create/verify/negotiate
│   ├── ed25519.rs   # Signing + verification
│   ├── x25519.rs    # Key exchange
│   ├── chacha.rs    # ChaCha20-Poly1305 AEAD
│   ├── hmac.rs      # HMAC-SHA256 (enrollment)
│   └── vault.rs     # CredentialStore trait
```

**Key constraint**: This library must have **zero tokio dependency** at
the crypto core. Async is only needed for I/O (vault file reads). The
handshake state machine should be sync, callable from any async runtime.

bearDog continues to exist as a standalone binary for backward
compatibility (wraps the library with UDS server). The chimera links
the library directly.

### R2: Shared Routing Module (songBird → library)

Extract songBird's dispatch core:

```
songbird-routing-lib/
├── src/
│   ├── registry.rs     # ServiceRegistry (capability → provider)
│   ├── dispatch.rs     # capability.call resolution
│   ├── mesh.rs         # BeaconMesh peer management
│   ├── enrollment.rs   # mesh.enroll protocol
│   └── transport.rs    # TCP mesh client/server
```

The `ServiceRegistry` becomes an in-memory table shared with the crypto
and defense modules. Provider resolution is a HashMap lookup, not a
UDS round-trip.

### R3: Shared Defense Module (skunkBat → library)

Extract skunkBat's defense core:

```
skunkbat-defense-lib/
├── src/
│   ├── method_gate.rs    # Access control
│   ├── threat.rs         # ThreatDetector
│   ├── federation.rs     # Threat broadcast
│   └── advisory.rs       # Security advisory
```

The `MethodGate` becomes a pre-dispatch filter in the chimera's
request pipeline — a function call before routing, not a separate
UDS hop.

### R4: Unified IPC Server

The chimera exposes ONE UDS socket and ONE TCP port:

| Interface | Protocol | Purpose |
|-----------|----------|---------|
| `chimera.sock` | NDJSON JSON-RPC | Local primal communication |
| `:7700` | NDJSON JSON-RPC | Mesh federation (inter-gate) |
| `:7780` | HTTP | Drawbridge gateway |

Capability symlinks (`security.sock`, `network.sock`, etc.) all point
to `chimera.sock`. External primals (nestGate, footPrint, etc.) see no
difference — their UDS calls still work.

### R5: Backward Compatibility

The chimera must support a **degraded mode** where bearDog/songBird/
skunkBat run as separate processes. This is needed for:
- Development (work on bearDog without rebuilding the chimera)
- Debugging (isolate which module has a bug)
- Gradual rollout (gate-by-gate migration)

Implementation: trait-based dispatch. The chimera's `CryptoProvider`
trait has two implementations:
1. `InProcessCrypto` — direct function call (chimera mode)
2. `UdsCrypto` — UDS JSON-RPC call (compatibility mode)

Selected at startup via `CHIMERA_MODE=unified|split` environment variable.

### R6: Shared Memory for Hot Paths

The chimera's critical advantage is shared-memory access:

| Data | Current (3 processes) | Chimera |
|------|----------------------|---------|
| Session store | bearDog's internal HashMap, queried via UDS | Shared `Arc<DashMap>` |
| Service registry | songBird's internal table | Shared `Arc<DashMap>` |
| Threat state | skunkBat's ThreatDetector | Shared `Arc<RwLock>` |
| Peer topology | songBird's BeaconMesh | Shared `Arc<RwLock>` |

Zero-copy access to session tokens, peer state, and capability tables
eliminates serialization overhead entirely.

## Migration Strategy

### Phase 0: Library Extraction (no behavioral change)

Extract `beardog-crypto-lib`, `songbird-routing-lib`,
`skunkbat-defense-lib` from existing crates. Each primal's binary
wraps its own library. All tests pass. No deployment change.

**Effort**: Medium. Mostly moving code, ensuring no circular deps.
**Risk**: Low. Pure refactoring.

### Phase 1: Chimera Binary (opt-in, single gate)

Create `biomeos-chimera` binary that links all three libraries. Deploy
on one gate (eastGate) alongside separate-process fallback. Run shadow
benchmarks comparing chimera vs separate.

**Effort**: Medium. Need unified IPC server, startup orchestration.
**Risk**: Medium. New binary, new failure modes.

### Phase 2: Shadow Validation (all gates)

Run chimera on all gates with `membrane tower.shadow` comparing chimera
latency/throughput against separate-process baseline. Collect data for
30 days.

**Effort**: Low. Deployment + monitoring.
**Risk**: Low. Shadow mode, not production.

### Phase 3: Cutover

Replace separate-process Tower Atomic with chimera on all gates. Keep
`CHIMERA_MODE=split` as emergency fallback.

**Effort**: Low. Configuration change.
**Risk**: Medium. Production traffic on new architecture.

## Performance Targets

| Metric | Current (separate) | Chimera Target | Improvement |
|--------|-------------------|----------------|-------------|
| LAN latency (p50) | 0.55ms | <0.10ms | >5× |
| LAN latency (p99) | 0.72ms | <0.20ms | >3.5× |
| BTSP session setup | ~1.8ms (3 hops) | <0.1ms | >18× |
| Capability dispatch (1000 req/s) | ~600ms/s IPC overhead | <1ms/s | >600× |
| Jitter (LAN) | 0.018ms | <0.005ms | >3.5× |
| Memory (3 processes) | ~3 × RSS | ~1 × RSS | 3× less |

## Open Questions

1. **Panic propagation**: In separate processes, bearDog panic doesn't
   kill songBird. In chimera, a panic in the crypto module kills
   everything. Use `catch_unwind` at module boundaries? Or accept
   crash-and-restart as simpler?

2. **Independent update**: Currently bearDog can be updated without
   touching songBird. Chimera requires coordinated updates. Is the
   sovereign depot pipeline sufficient for atomic updates?

3. **HSM isolation**: grapheneGate's TPM/HSM integration may require
   process isolation for key material. Does the chimera support a
   "crypto-out-of-process" mode for HSM gates?

4. **Resource accounting**: Three processes have separate memory/CPU
   limits (via cgroups). The chimera is one process — harder to
   attribute resource usage per module.

5. **biomeOS integration**: The chimera IS biomeOS at its core. Does
   the chimera binary become `biomeos` rather than a separate entity?
   This affects the primal taxonomy.

## Dependencies on Stress/Pen Test Results

The chimera design is informed by — but not blocked on — the stress and
pen test results. Key dependencies:

| Stress/Pen Scenario | Chimera Impact |
|---------------------|---------------|
| `s_tower_stress_uds_hop_cost` | Quantifies exact savings; validates chimera targets |
| `s_tower_stress_concurrent_dispatch` | Tests whether contention is UDS-bound or logic-bound |
| `s_tower_stress_btsp_storm` | Determines if bearDog saturation is CPU or IPC limited |
| `s_tower_pen_uds_spoof` | Validates chimera's security improvement claim |
| `s_tower_pen_cipher_downgrade` | Same code path in chimera — no change needed |
| `s_tower_stress_failover_resilience` | Chimera changes failure domain — new failure modes |

## Deliverable

The chimera is a **Phase 3** deliverable (after Phase 2 shadow mode
proves Tower Atomic at parity). The library extraction (Phase 0) can
begin immediately as it's pure refactoring with no behavioral change.

---

*The chimera is the convergence of the Tower Atomic trio into a single
evolutionary organism — the namesake of biomeOS. It represents the
transition from composition-of-processes to composition-of-modules,
collapsing IPC overhead while preserving the capability-routing model
that makes Tower Atomic superior to WireGuard's single-tunnel approach.*
