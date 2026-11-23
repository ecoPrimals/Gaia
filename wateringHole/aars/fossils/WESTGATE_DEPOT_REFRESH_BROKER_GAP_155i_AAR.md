# AAR: westGate Wave 155i — Depot Refresh + Composition Broker Gap

**Gate:** westGate
**Date:** 2026-07-29
**Operator:** westGate overwatch (agentic)
**Wave:** 155i (post-cascade from golgiBody — composition broker shipped)
**Scope:** Cascade review, depot binary refresh, sweetGrass G3 live validation, biomeOS graph dispatch attempt, Provenance Trio re-validation
**Prior AARs:** `WESTGATE_CASCADE_REVIEW_ZFS_PROVENANCE_155i_AAR.md`, `WESTGATE_NEST_ATOMIC_MULTICOMP_155i_AAR.md`

---

## Context

eastGate overwatch shipped the composition broker (biomeOS v4.45, commit `48cf9c33`)
resolving both P0s: riboCipher framing in CLI paths and BTSP session propagation in
signal graph executor. This cascade pulled the latest code and attempted to validate
E2E signal graph dispatch on westGate hardware.

---

## Cascade Summary

10 repos pulled from golgiBody. All clean rebase on main.

| Repo | Commits | Key Changes |
|------|---------|-------------|
| barraCuda | +4 | RTX 3090 profiling, DF64 framing, deprecation sweep |
| biomeOS | +4 | **COMPOSITION BROKER SHIPPED**: riboCipher framing + BTSP executor, 35 E2E tests, connection pool IO, v4.45 |
| coralReef | +1 | Deep debt: 463 `.expect()` eliminated, PTX macro modernization (-363L net) |
| songBird | +1 | P0 FIXED: Windows platform gate → TCP fallback, 2 test monoliths split |
| toadStool | +3 | S346: security fail-closed, unsafe containment (hw-safe crate), doctor fix |
| cellMembrane | +1 | Deep debt: sandbox fail-closed, registry-driven tower status |
| sporePrint | +1 | Wave 155i ecosystem state update |
| wateringHole | +31 | Cascade handoffs, auto-publishes, blueGate/strandGate AARs |
| whitePaper | +7 | JOSS publication prep, Valve/inkfish contact drafts |
| primalSpring | +1 | benchScale file renames (colons → underscores) |

---

## What Worked

### 1. sweetGrass G3 LedgerClient — LIVE on westGate

The depot refresh delivered sweetGrass **v0.8.0** (was v0.7.64). The G3 LedgerClient
now fires `braid.commit` → loamSpine forwarding:

```
sweetgrass[992181]: method gate: unauthenticated call (permissive) method="braid.commit"
sweetgrass[992181]: loamSpine commit unavailable, braid is local-only:
                    ledger error: UUID parsing failed
```

The forwarding path is **operational** — sweetGrass reaches loamSpine and attempts the
commit. The failure is a wire-format issue: the `braid_id` (`urn:braid:blake3:...`) is
passed to loamSpine's `entry.append` which expects a UUID. The LedgerClient should
extract/generate a UUID, not pass the URN directly.

**Impact:** G3 wiring validated on live hardware. The sweetGrass ↔ loamSpine integration
works at the transport layer; only the braid_id→UUID mapping needs fixing (P2, sweetGrass).

### 2. membrane `gate.configure` — WORKING

Depot membrane binary updated from `07c16a5` to `8d9bb58`. The `gate.configure` command
now generates correct systemd unit templates for all 13 primals:

```
gate.configure: unknown — 13 services (full, systemd)
```

This unblocks agentic deployment via `gate.configure` + `gate.apply` (J6 CLOSED).

### 3. Provenance Trio — 6/7 (Confirmed with Corrected Wire Format)

Full round-trip with corrected `entry.append` params (`data_hash` as `[u8; 32]` inside
`DataAnchor` variant, not as top-level hex string):

| Step | Primal | Method | Result |
|------|--------|--------|--------|
| 1 | nestGate | `content.put` | **PASS** — BLAKE3 hash, stored on ZFS |
| 2a | rhizoCrypt | `dag.session.create` | **PASS** — UUID v7 session |
| 2b | rhizoCrypt | `dag.event.append` | **PASS** — DataCreate event |
| 2c | rhizoCrypt | `dag.merkle.root` | **PASS** — root = event hash |
| 3a | loamSpine | `spine.create` | **PASS** — UUID v7 spine |
| 3b | loamSpine | `entry.append` | **FAIL** — bearDog `crypto.sign_ed25519` stub |
| 4 | sweetGrass | `braid.create` (riboCipher) | **PASS** — v0.8.0 G3 |

The `entry.append` failure is now cleanly isolated:
```
transport error: crypto.sign_ed25519 result deserialize: missing field `signature`
```
bearDog returns its health response instead of a signature. This is a P1 for the bearDog
team — the API shape exists (ACME Phase 2 crypto delegation surface) but the signing
implementation doesn't.

### 4. All 8 Services Stable — Socket Evaporation Pattern Reproduced and Resolved

After cascade and service restarts, 4 sockets evaporated (nestgate, songbird,
rhizocrypt, loamspine). Targeted restart restored all 15 sockets across both socket
directories (`/run/user/1000/biomeos/` and `/run/user/1000/membrane/`).

### 5. ZFS Pool Healthy — Zero Errors, 3,211 CAS Objects

```
pool: nestgate — ONLINE, 0 errors
  mirror-0:  2×14TB — ONLINE
  mirror-1:  2×14TB — ONLINE
  cache:     1×2TB BX500 SSD — ONLINE (L2ARC)
  spare:     1×14TB — AVAIL
```

- CAS objects: 3,211 files (up from 3,119 at blurb time)
- Compression ratio: 1.50x
- ARC hit rate: 99.98% (1,123,747 hits / 194 misses)
- L2ARC: 0 hits yet (needs sustained read workload)

---

## What Did Not Work

### 1. biomeOS Graph Dispatch — Depot Binary Lag (P1)

The depot biomeOS binary is **v0.1.0**. The composition broker shipped at **v4.45**
(commit `48cf9c33`). The depot binary can:
- ✓ Load 70 signal graphs
- ✓ Register 163 capabilities from live sockets
- ✓ Accept riboCipher framing on UDS
- ✗ Dispatch signal graphs (socket resolution bug in old executor)

Error on `graph.dispatch`:
```
Internal error: Primal 'biomeos-westgate-tower-155f' not found:
socket /run/membrane/biomeos-westgate-tower-155f-westgate-tower-155f.sock does not exist
```

Three issues in the old executor:
1. Uses `/run/membrane/` instead of `SOCKET_DIR` (`/run/user/1000/biomeos/`)
2. Doubles the family ID in socket path construction
3. Falls back to toadStool forwarding (not deployed on westGate)

**Fix:** biomeOS depot rebuild with v4.45. The composition broker E2E tests (35 tests)
validate the correct socket resolution path. Until the rebuild, individual IPC works
but orchestrated signal graphs through the Neural API are blocked.

### 2. sweetGrass G3 `braid.commit` → loamSpine UUID Format Mismatch (P2)

The LedgerClient forwards the `braid_id` (`urn:braid:blake3:HASH`) as the spine entry
identifier. loamSpine's `entry.append` expects a UUID, not a URN. Result:
```
UUID parsing failed: invalid character: found `u` at 1
```

The transport works. The data format doesn't match. sweetGrass should derive a UUID v5
from the braid_id or use the explicitly provided `uuid` field from the commit params.

### 3. Neural API RPC Ping Failures

After restart, the Neural API fails to ping several sockets it discovers:
```
🔴 RPC ping failed: /run/user/1000/biomeos/permanence.sock - RPC ping failed (0ms)
🔴 RPC ping failed: /run/user/1000/biomeos/storage.sock - RPC ping failed (0ms)
🔴 RPC ping failed: /run/user/1000/biomeos/dag.sock - RPC ping failed (0ms)
```

These are alias sockets (e.g., `permanence.sock` is loamSpine's capability socket,
`storage.sock` is nestGate's). The RPC ping fails instantly (0ms) suggesting the
sockets exist but don't respond to the old biomeOS ping format. The capability
registration still works via the family-scoped sockets (`nestgate-westgate-tower-155f.sock`).

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Repos cascaded | 10 |
| Services running | 8/8 |
| Sockets active | 15 (14 biomeos + 1 membrane) |
| Capabilities registered | 163 |
| Signal graphs loaded | 70 |
| CAS objects on ZFS | 3,211 |
| ZFS pool capacity | 25.3 TB available |
| ZFS errors | 0 |
| ZFS compression | 1.50x |
| ARC hit rate | 99.98% |
| Provenance Trio | 6/7 |
| sweetGrass version | **0.8.0** (G3 LedgerClient LIVE) |
| membrane build | 8d9bb58 (gate.configure WORKING) |
| biomeOS version | 0.1.0 (v4.45 NOT in depot) |

---

## Depot Binary Lag — Status After This Wave

| Binary | Depot | Source | Feature Gap | Severity |
|--------|-------|--------|-------------|----------|
| biomeOS | 0.1.0 | 4.45 | Composition broker, riboCipher dispatch, BTSP executor | **P1 — blocks E2E signal graphs** |
| sweetGrass | **0.8.0** | 0.8.0 | **CURRENT** ✓ | Resolved this cascade |
| nestGate | 0.5.0 | 0.5.0 | Same version, but depot binary pre-FHS (no NESTGATE_STORAGE_PATH) | P2 — mitigated by symlink |
| membrane | 0.1.0 (8d9bb58) | 0.1.0 | **CURRENT** ✓ (gate.configure works) | Resolved this cascade |

**sweetGrass and membrane now current.** biomeOS is the critical remaining gap.

---

## Action Items

### P1 (High Impact)

| # | Item | Owner | Unblocks |
|---|------|-------|----------|
| 1 | **biomeOS depot rebuild** — v4.45 composition broker | sporeGate | E2E signal graph dispatch, `nest.ingest_dataset`, AlphaFold pipeline |
| 2 | **bearDog `crypto.sign_ed25519`** — implement real signing | bearDog | Provenance Trio 7/7, loamSpine entry signing |
| 3 | **sweetGrass G3 braid_id→UUID** — LedgerClient UUID derivation | sweetGrass | `braid.commit` → loamSpine E2E |

### P2 (Operational)

| # | Item | Owner | Unblocks |
|---|------|-------|----------|
| 4 | Socket evaporation under partial restart | All primals | Multi-composition stability |
| 5 | Neural API RPC ping → alias sockets | biomeOS | Clean startup logs |
| 6 | `SOCKET_DIR` / `BIOMEOS_SOCKET_DIR` documentation | biomeOS | Gate deployment guides |

---

## Key Insight: The Composition Broker Shipped But Can't Run Here

The ecosystem pattern is clear: **code ships faster than deployment can absorb it**.
biomeOS v4.45 has 35 E2E tests validating the exact composition broker pattern we need
on westGate. The source is correct, tested, and merged. But the depot binary is the
pre-broker v0.1.0 and the graph dispatch executor uses hardcoded `/run/membrane/` paths
instead of the `SOCKET_DIR` env var that the new version respects.

The previous AAR identified depot binary lag as systemic (affecting 3 primals). This
cascade **resolved 2 of 3** (sweetGrass 0.8.0, membrane 8d9bb58) but the critical one
(biomeOS) remains. The biomeOS depot rebuild is the single-point blocker between
"all primals work individually" and "orchestrated signal graphs work end-to-end."

The auto-publish hooks on golgiBody already trigger — but they publish handoffs, not
rebuilt binaries. The gap is the same: merge → rebuild → depot push per primal.

---

*Wave 155i cascade. 10 repos pulled. sweetGrass G3 LIVE (v0.8.0). membrane gate.configure
WORKING. Provenance Trio 6/7 (bearDog crypto.sign P1). biomeOS graph dispatch BLOCKED
(depot 0.1.0 vs source v4.45). ZFS 25.3TB, 3,211 CAS objects, 99.98% ARC hit rate. Socket
evaporation reproduced and resolved. Two of three depot binary lags resolved — biomeOS
remains. E2E signal graphs READY when biomeOS depot binary is rebuilt.*
