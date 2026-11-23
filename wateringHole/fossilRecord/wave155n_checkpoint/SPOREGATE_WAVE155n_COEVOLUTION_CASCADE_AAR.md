# sporeGate Wave 155n — Coevolution Cascade AAR

**Date**: Jul 31, 2026 11:15 EDT | **Gate**: sporeGate | **Wave**: 155n
**Gate Health**: 11/11 HEALTHY | **Depot**: 35 binaries (v4.55 + 0d39075)

---

## Executive Summary

biomeOS v4.55 (`composition.test_swap`) and cellMembrane (`validate_with_deps`) — the
coevolution contract proposed in this morning's strategic AAR — shipped from the code teams
within hours. We cascaded, rebuilt all targets, deployed locally and to depot/golgi.

**The coevolution code is IN the binaries but can't execute E2E yet** due to a mode gap:
`composition.test_swap` is registered in biomeOS's `api` mode (requires riboCipher framing),
but cellMembrane's `validate_with_deps` sends plain JSON-RPC to the `neural-api` socket.
The handshake never completes.

This is a ~20 LOC fix for the code teams (register `composition.test_swap` in neural-api
mode, or accept plain JSON-RPC in api mode). The plumbing is 95% done.

---

## What Shipped

### biomeOS v4.55 (5e540221) — 5 Commits from 999044e7

| Commit | What |
|--------|------|
| `5e540221` | `composition.test_swap` — coevolution contract endpoint |
| `88785daf` | **P1 FIX**: dual-protocol health ping (plain JSON-RPC first, BTSP fallback). Socket ownership guard (PID check before unlink). |
| `b082bd16` | Root docs sync + cargo clean 54.4 GiB |
| `5d9374b6` | 15 dead deps removed across 8 crates |
| `c7bc2187` | 2 P3s closed: zombie reaping + virtual service churn |

Version now reports `biomeos 4.55.0` (was `0.1.0`).

### cellMembrane 0d39075 — 6 Commits from 301e236

| Commit | What |
|--------|------|
| `0d39075` | **J16 KILLED**: `sources.toml` garden self-enrollment. **J13**: freshness mesh publish. |
| `00c6800` | **J19**: `validate_with_deps()` — broker primal delegation via `composition.test_swap` |
| `bf1ebca` | Sandbox P2: commit-suffix registry miss + socket-base init-scope migration |
| `856f6aa` | Root doc refresh + constants test externalization |
| `8785860` | Smart file splits, crypto dedup, constants sweep |
| `4a2b39c` | `MEMBRANE_*` env var standardization + webhook secret unification |

---

## The Mode Gap — Why E2E Doesn't Complete

```
cellMembrane (validate_with_deps)
  → connects to /run/membrane/neural-api-default.sock (plain JSON-RPC)
  → sends: composition.test_swap { primal: "biomeos", binary_path: "..." }
  → biomeOS neural-api mode receives the request
  → BUT composition.test_swap is NOT registered in neural-api mode
  → request hangs → read timeout → fallback to standalone sandbox → FAIL

biomeOS api mode (biomeos.sock)
  → HAS composition.test_swap registered
  → BUT requires riboCipher framing (rejects plain JSON-RPC since v4.54)
  → cellMembrane sends plain → REJECTED as "legacy connection"
```

**Fix options (for code teams)**:
1. Register `composition.test_swap` in neural-api mode (biomeOS, ~10 LOC)
2. Add `--btsp-optional` support to api mode (biomeOS, ~5 LOC)
3. Have cellMembrane send riboCipher-framed requests (cellMembrane, ~20 LOC)

Option 1 is the simplest and maintains the security boundary.

---

## Builds + Deployment

| Binary | musl | gnu | windows | Depot | Golgi |
|--------|------|-----|---------|-------|-------|
| biomeOS v4.55 | OK (3m10s) | OK (6m17s) | OK (9m18s) | 21MB/21MB/20MB | SYNCED |
| membrane 0d39075 | OK (52s) | — | OK (1m37s) | 16MB/—/20MB | SYNCED |

Local deploy: biomeOS v4.55 running (`biomeos 4.55.0`), membrane 0d39075 (`membrane 0.1.0 (0d39075)`).

Depot: 35 binaries, all BLAKE3 verified, golgi synced.

**Sovereign CI trigger caveat**: The trigger ran during testing and overwrote the depot
biomeOS with a stale build from root's source tree (v0.1.0, 16.5MB). We caught this and
re-deployed the correct v4.55 build (21MB). Root cause: sovereign.ci.trigger builds from
`/opt/ecoPrimals` source tree which may not match the sporegate user's `~/Development`
tree. The trigger needs to `git pull` before building.

---

## Gate Health

```
sporeGate (x86_64-unknown-linux-musl) — HEALTHY
  [OK] depot.integrity: 16 verified, 0 hash mismatch, 0 missing
  [OK] mesh.reachability: 3 peers, 3 reachable
  [OK] primals.alive: 13/13 primals alive
  [OK] depot.freshness: 13/13 binaries present, oldest 2d
  [OK] sovereignty.s1_tls: OPERATIONAL — depot.primals.eco 200
  [OK] sovereignty.s2_relay: federation:REACHABLE, RustDesk:hbbs=OK,hbbr=OK
  [OK] sovereignty.s3_content: OPERATIONAL — depot serving 8459KB
  [OK] sovereignty.s4_auth: RESPONDING — beardog reachable (via neuralAPI)
  [OK] rootpulse.ledger: advisory OK
  [OK] vcs.parity: 0 repos checked, 0 drifted
  [OK] service.crash-loop: 14 services scanned, no crash-loops
```

---

## Jelly String Status

| J# | What | Status |
|----|------|--------|
| ~~J9~~ | Push trigger | **KILLED** — golgi hook (3 bugs fixed) |
| ~~J10~~ | Drift → auto harvest | **KILLED** |
| ~~J11~~ | Multi-target build | **KILLED** |
| J12 | blueGate sub-builder | UNBLOCKED |
| ~~J13~~ | Depot freshness | **KILLED** — `plasmid.staleness --publish` |
| ~~J16~~ | cellMembrane self-CI | **KILLED** — `sources.toml` garden self-enrollment |
| J18 | Gate coupling | OPEN |
| ~~J19~~ | Sandbox broker false positive | **CODE SHIPPED** — mode gap prevents E2E. 95% done. |

**9/11 killed** (J19 counts as shipped but not verified E2E).

---

## Upstream Items for Code Teams

### biomeOS Team
Register `composition.test_swap` in neural-api mode. Currently only registered in api mode
(which requires riboCipher). The `neural-api --btsp-optional` service is the one cellMembrane
connects to. ~10 LOC fix. This unblocks J19 E2E verification.

### cellMembrane Team
The `validate_with_deps()` fallback to standalone sandbox is working correctly when
`composition.test_swap` fails. Once biomeOS registers the endpoint in neural-api mode,
the full pipeline should work. No changes needed from cellMembrane.

### sporeGate Self-Note
The sovereign.ci.trigger builds from root's source tree at `/opt/ecoPrimals`, which may
diverge from `~/Development/ecoPrimals`. The trigger should either (a) git pull before
building, or (b) use the sporegate user's tree. This caused a depot binary downgrade during
testing.
