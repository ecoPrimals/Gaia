# Deployment Validation Standard

**Status**: Ecosystem Standard
**Version**: v1.2.0
**Date**: May 26, 2026
**Authority**: wateringHole (ecoPrimals Core Standards)
**Driven by**: plasmidBin v2026.03.25 live validation, benchScale IPC compliance testing

---

## Purpose

This standard defines the requirements for a primal to be **deployment-valid** —
meaning it can be fetched from plasmidBin, started by `plasmidbin start`, and
validated by `benchscale validate ipc` or equivalent probes without any source
code, Rust toolchain, or primal-specific knowledge on the consumer's machine.

Deployment validity is the **runtime complement** to the build-time standards in
`UNIBIN_ARCHITECTURE_STANDARD.md` and `PRIMAL_IPC_PROTOCOL.md`. A primal can
pass all build checks and still be deployment-invalid if its runtime behavior
diverges from the contract.

---

## The Deployment Contract

A primal binary fetched from plasmidBin MUST satisfy all of the following
when started by an orchestrator (`plasmidbin start`, biomeOS, benchScale):

### 1. Health Triad (MANDATORY)

Every primal MUST respond to the standard health triad over its **primary
JSON-RPC transport** (UDS or TCP, newline-delimited):

```json
{"jsonrpc":"2.0","method":"health.liveness","params":{},"id":1}
→ {"jsonrpc":"2.0","result":{"status":"healthy"},"id":1}

{"jsonrpc":"2.0","method":"health.readiness","params":{},"id":2}
→ {"jsonrpc":"2.0","result":{"status":"healthy","version":"X.Y.Z","primal":"name"},"id":2}

{"jsonrpc":"2.0","method":"health.check","params":{},"id":3}
→ {"jsonrpc":"2.0","result":{"status":"healthy","version":"X.Y.Z","primal":"name"},"id":3}
```

**Method names are exact.** `toadstool.health`, `dag.health`, and
`compute.health` are NOT substitutes for `health.liveness`. Primal-prefixed
health methods MAY exist alongside the standard triad but do not replace it.

**Response format:**
- `health.liveness`: MUST return `{"status":"healthy"}` (or `"alive":true`).
  This is the keepalive — it answers "are you running?"
- `health.readiness`: MUST include `version` and `primal` name. Answers
  "are you ready to serve requests?"
- `health.check`: MUST include `version` and `primal` name. MAY include
  `uptime_secs`, `active_connections`, or domain-specific metrics.

**benchScale validation:**
```bash
benchscale validate ipc 127.0.0.1:<port>
# Reports COMPLIANT only when all 3 methods return valid JSON-RPC results
```

### 2. Socket-First, Port-Fallback (MANDATORY)

Primals MUST create a filesystem socket at startup:
```
$XDG_RUNTIME_DIR/biomeos/<primal>.sock
```

TCP ports are **fallback** for cross-gate, Docker, mobile, and testing.
When songBird is live, the entire ecosystem runs port-free on UDS.

`plasmidbin start` passes `--tcp-port` only when the caller explicitly
requests it. Without `--tcp-port`, the primal MUST still be reachable
via its UDS socket.

**Stale socket hygiene (May 18, 2026):** Primals MUST `unlink()` their
socket before `bind()` on startup. Primals SHOULD write a `{name}.pid`
file alongside the socket so consumers can verify liveness via `kill(pid, 0)`
without incurring connect overhead. On graceful shutdown, primals MUST
remove both the socket and PID file. See `CAPABILITY_BASED_DISCOVERY_STANDARD.md`
§5-6 for the consumer-side connect-probe and negative caching patterns.

### 3. CLI Convergence (MANDATORY)

Per `UNIBIN_ARCHITECTURE_STANDARD.md` v1.1, the `server` subcommand MUST
accept `--port <PORT>` to bind TCP newline-delimited JSON-RPC.

Primals that use different flags MUST alias `--port`:

| Current Flag | Required Alias | Primal |
|-------------|----------------|--------|
| `--jsonrpc-port` | `--port` | loamSpine |
| `--http-address ADDR:PORT` | `--port PORT` | sweetGrass |
| `--listen ADDR:PORT` | `--port PORT` | bearDog (already has both) |

`plasmidbin start` absorbs current differences as a compatibility shim.
As primals converge, the shim shrinks to a single generic case.

### 4. Standalone Startup (MANDATORY)

Per `UNIBIN_ARCHITECTURE_STANDARD.md` v1.1, primals MUST start without
`FAMILY_ID`, `NODE_ID`, or any other identity variables. Default to
`standalone` or generate a transient identity.

**Violation found:** bearDog v0.9.0 hard-fails with
`NODE_ID or BEARDOG_NODE_ID must be set` — this blocks zero-config deployment.

### 5. Capability Advertisement (RECOMMENDED)

Primals SHOULD respond to `capabilities.list` with their full capability set:

```json
{"jsonrpc":"2.0","method":"capabilities.list","params":{},"id":1}
→ {"jsonrpc":"2.0","result":{"capabilities":["crypto.sign","crypto.verify",...]},"id":1}
```

This enables automated validation: `metadata.toml` declares capabilities,
the running primal confirms them.

---

## Transport Discovery Matrix

Live validation (April 13, 2026 — Phase 40 NUCLEUS Complete) confirmed **ALL 13
primals support UDS with newline-delimited JSON-RPC**. 19/19 exp094 PASS.

| Primal | Newline TCP | HTTP TCP | UDS (filesystem) | UDS (abstract) | tarpc | Methods |
|--------|------------|----------|------------------|----------------|-------|---------|
| bearDog | 9100 ✓ | — | ✓ beardog-{family}.sock | — | — | 100 |
| songBird | — | 9200 (HTTP discovery) | ✓ songbird-{family}.sock | — | — | 79 |
| toadStool | — | — | ✓ toadstool-{family}.sock (BTSP auto-detect) | — | ✓ | 163 |
| barraCuda | — | — | ✓ math-{family}.sock (JSON-RPC via BTSP guard) | — | ✓ | 32 |
| coralReef | — | — | ✓ shader.sock | — | — | 10 |
| squirrel | — | — | ✓ squirrel-{family}.sock | @squirrel | — | 30 |
| nestGate | — | — | ✓ nestgate-{family}.sock | — | — | 30 |
| rhizoCrypt | — | 9701 (HTTP JSON-RPC) | ✓ rhizocrypt-{family}.sock | — | 9700 ✓ | 28 |
| sweetGrass | — | 9720 (REST + /jsonrpc) | ✓ sweetgrass-{family}.sock | — | ✓ | 32 |
| loamSpine | — (TCP opt-in via --listen) | — | ✓ loamspine-{family}.sock | — | ✓ | 34 |
| petalTongue | — | ✓ (web mode) | ✓ petaltongue-{family}.sock (--socket flag) | — | — | — |
| biomeOS | — | ✓ (API mode) | ✓ biomeos.sock | — | — | — |

**Standard requirement:** Every primal MUST have newline-delimited JSON-RPC
on at least one of: filesystem UDS or TCP. HTTP-wrapped JSON-RPC does not
satisfy this (it requires HTTP framing, breaking raw stream clients).

**Current compliance (April 13, 2026):**
- PASS: **ALL 13 primals** now have UDS filesystem sockets with JSON-RPC support.
- Key resolutions: rhizoCrypt UDS (LD-06, S37), loamSpine UDS-first (LD-09, v0.9.16),
  petalTongue `--socket` flag (v1.6.6), barraCuda JSON-RPC via BTSP guard line (LD-10),
  ToadStool BTSP auto-detect (LD-04), squirrel filesystem socket alongside abstract.

---

## plasmidBin Integration Requirements

### metadata.toml Transport Declaration

Each primal's `metadata.toml` SHOULD declare its transport surfaces so
`plasmidbin start` and `plasmidbin fetch` can make informed decisions:

```toml
[genomeBin.server]
tcp_port_env = "BEARDOG_PORT"
tcp_port_default = 9100
tcp_protocol = "jsonrpc-newline"     # or "http", "tarpc"
socket_flag = "--socket"
port_flag = "--port"                 # MUST be "--port" per UniBin v1.1
listen_flag = "--listen"             # optional full addr:port form
```

The `tcp_protocol` field tells orchestrators what wire format to expect,
enabling benchScale to choose the right validation method.

### Checksum Hygiene

Binaries MUST be built with `--remap-path-prefix` and `strip = true` per
`SECRETS_AND_SEEDS_STANDARD.md`. `plasmidbin harvest` warns when binaries
contain build-machine paths.

---

## Validation Flow

The standard validation flow for any plasmidBin deployment:

```
1. Clone plasmidBin
2. cargo run -p plasmidbin -- fetch --all
   → downloads arch-matched binaries from GitHub Releases
   → verifies BLAKE3 checksums against checksums.toml

3. cargo run -p plasmidbin -- start <primal> --tcp-port <PORT>
   → maps generic flags to per-primal CLI
   → starts binary, waits 2s, checks liveness

4. benchscale validate ipc 127.0.0.1:<PORT>
   → probes health.liveness, health.readiness, health.check
   → reports COMPLIANT or NON-COMPLIANT

5. For full composition validation:
   cargo run -p plasmidbin -- launch --composition full
   → starts all primals, probes each health
   → optionally probe cross-primal capabilities
```

---

## Per-Primal Fix Path

Based on live validation April 5, 2026 (plasmidBin v2026.03.25):

| Primal | Deployment Status | Required Fix |
|--------|------------------|--------------|
| bearDog | ✓ TCP COMPLIANT | Fix standalone startup (NODE_ID hard-fail) |
| songBird | ✓ UDS HEALTHY | Add `--port` for newline TCP (currently HTTP-only on TCP) |
| toadStool | ✓ UDS HEALTHY | Implement `health.liveness/readiness/check` (currently `toadstool.health` only). Create filesystem socket (not just family-scoped). |
| squirrel | ✓ Abstract HEALTHY | Create filesystem socket alongside abstract `@squirrel`. |
| sweetGrass | ✓ HTTP HEALTHY | Add `--port` alias. Add newline JSON-RPC on TCP (currently HTTP-only). |
| rhizoCrypt | ⚠ tarpc REACHABLE | Add `--port` alias (currently `--tarpc-port`). Expose health triad on JSON-RPC 9701. |
| loamSpine | ✓ UDS HEALTHY | ~~Runtime nesting crash~~ **RESOLVED** (v0.9.16 — `mdns-sd`). `--port` alias implemented. |
| nestGate | — (not started) | Wire `--port` to TCP listener. Add `server` alias for `daemon`. |
| biomeOS | — (not started) | Add TCP-only mode (currently forces UDS when port specified). |
| petalTongue | — (not started) | Verify health triad on all transports. |

---

## Related Standards

- `PRIMAL_IPC_PROTOCOL.md` — Wire framing, transport tiers, health triad definition
- `UNIBIN_ARCHITECTURE_STANDARD.md` — `--port` convention, standalone startup
- `CAPABILITY_BASED_DISCOVERY_STANDARD.md` — Socket paths, symlinks, discovery tiers
- `ECOSYSTEM_COMPLIANCE_MATRIX.md` — Build-time compliance (Tiers 1–9)
- `SECRETS_AND_SEEDS_STANDARD.md` — Build hygiene for binary distribution
- `ECOBIN_ARCHITECTURE_STANDARD.md` — musl-static, PIE, portability

---

## Version History

### v1.0.0 (April 5, 2026)

**Initial Standard — Runtime Deployment Validation**

- Driven by first end-to-end plasmidBin validation: clone → fetch → start → probe
- 10 binaries fetched from GitHub Releases, 10 checksums verified
- 7 primals started, 5 healthy, 1 partial, 1 crash
- Transport diversity documented (5 patterns across 10 primals)
- Per-primal fix paths defined
- benchScale `validate ipc` established as the deployment acceptance test
