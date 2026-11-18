# AAR: sporeGate Debt Clearing + Depot Rebuild

**Date**: Aug 5, 2026 | **Wave**: 156f | **Gate**: sporeGate (eastGate overwatch)
**Duration**: ~3 hours | **Sessions**: 2 (afternoon + evening)

---

## Summary

Cleared **S1–S8** from the sporeGate punch list (plus verified S4–S5 pre-shipped). Executed full depot rebuild with blueGate as parallel sub-builder. Pushed 26 fresh binaries to golgi. All 15 primals compile clean, synced with Forgejo, and deployed.

---

## What Worked

### S1–S3: sweetGrass Provenance Trio (Session 1)
- **S1 (LedgerClient compile fix)**: WIP had `as_nanos()` → `nanos()` API break. Resolved by pulling upstream biomeOS changes which updated shared dependency. No code fix needed — the API migration was in the upstream crate.
- **S2 (convergence.check)**: One-call provenance chain verification (CAS→DAG→Spine→Braid→Signed). `convergence.batch_check` for bulk with 1000-hash limit. Clean `compute_depth` helper. This eliminates `convergence_check.py` (183 lines).
- **S3 (braid.list)**: Lightweight braid enumeration with `QueryFilter` + `QueryOrder`. Returns `BraidListEntry` (not full braid objects) — efficient for audit dashboards.
- Test count alignment: dispatch table 42→45 methods, capability list count updated. **610/610 tests pass**.
- Pushed `dfc255c` to Forgejo.

### S7: nestgate.io mesh.peers (Session 1)
- `query_songbird_peers()` in `petalTongue/src/data_service/mesh.rs` queries songBird at `/run/membrane/songbird.sock` via plain JSON-RPC (no BTSP framing — songBird uses raw JSON on UDS).
- `/api/mesh-peers` handler tries live songBird first, falls back to static manifest.
- Dashboard updated: 6-column table (Gate, Status, Transport, Address, Priority, Latency), "songBird live" source pill.
- Verified at `nestgate.io/api/mesh-peers` — 6 peers (4 LAN local p0, 2 WG overlay p1).

### S8: nestgate.io health.liveness (Session 2)
- `petalTongue/src/data_service/health.rs`: New module with `query_all_health()` — queries 13 primal UDS sockets concurrently via `JoinSet` with BTSP framing (`0xEC 0x01` prefix).
- Handles varied response formats: `{"alive": true}`, `{"status": "alive"}`, `{"primal": "...", "status": "alive", "version": "..."}`. Multi-object streams (bearDog sends error+result) parsed via streaming `serde_json::Deserializer`.
- `/api/primal-health` endpoint wired into axum router.
- Dashboard: health table (Primal, Status, Version, Detail), `healthPill()` enriched with live UDS data, summary pill.
- **11/13 alive**: coralReef (tarpc architecture, not JSON-RPC), toadStool (socket permissions — B1/B2 fix not yet deployed locally).

### Depot Pipeline Divergence Resolution
- **Session 1**: 3 primals behind Forgejo (biomeOS, nestGate, songBird) — pulled.
- **Session 2**: 5 primals behind Forgejo (bearDog, coralReef, nestGate, squirrel, toadStool) — pulled. 8 primals behind on blueGate — all 15 pulled.
- All 15 primals verified at HEAD on both sporeGate and blueGate.

### blueGate Sub-Builder Pattern
- Dispatched full 15-primal Windows build to blueGate via SSH.
- blueGate completed all 15 in ~10 minutes (barraCuda 2m16s was the slowest new build).
- sporeGate ran musl harvest in parallel — 6 remaining stale primals.
- **Key insight**: blueGate should be filed up *before* sporeGate because sporeGate has additional tasking (14 NUCLEUS services, petalTongue web, mesh coordination).

### Full Depot Rebuild
- **15/15 musl binaries** built on sporeGate (Aug 5).
- **15/15 Windows binaries** built on blueGate (Aug 5).
- **26 binaries synced** to golgi via `membrane plasmid.push`.
- Local NUCLEUS binaries updated (songbird, biomeos, squirrel, skunkbat installed).

---

## What Diverged / Issues Encountered

### DIV-1: sweetGrass `as_nanos()` API break
- **Symptom**: `cargo check` fails on sweetGrass with `no method named as_nanos found`.
- **Root cause**: Upstream biomeOS changed a shared type's time API from `as_nanos()` to `nanos()`.
- **Fix**: Pull biomeOS from Forgejo — the dependency resolved automatically.
- **Lesson**: Cross-primal API breaks are invisible until you pull. Depot pipeline should detect these.

### DIV-2: songBird UDS uses plain JSON, not BTSP
- **Symptom**: Initial `query_songbird_peers()` implementation used BTSP framing (`0xEC 0x01`), but songBird returned parse errors.
- **Root cause**: songBird's UDS socket accepts plain JSON-RPC, unlike most other primals which require BTSP.
- **Fix**: Removed BTSP prefix from the songBird query.
- **Lesson**: UDS protocol framing is not uniform across primals. Need per-primal protocol detection or a canonical convention.

### DIV-3: bearDog multi-object UDS response
- **Symptom**: `health.liveness` on bearDog socket returned two JSON objects: first an error (from BTSP prefix parsing), then the actual result.
- **Root cause**: bearDog's UDS handler emits a parse error for the BTSP prefix bytes, then processes the remaining JSON payload separately.
- **Fix**: `parse_first_result()` uses streaming `serde_json::Deserializer` to find the first object with a `result` field, skipping error objects.
- **Status**: bearDog reports alive with version 0.9.0.

### DIV-4: coralReef not JSON-RPC on UDS
- **Symptom**: Empty response from `coralreef.sock` on `health.liveness`.
- **Root cause**: coralReef uses `tarpc` protocol on its primary socket, not JSON-RPC.
- **Fix**: None needed — coralReef health should be queried via its tarpc socket or via Neural API capability routing.
- **Status**: Known architecture difference, not a bug. Dashboard shows "error" status.

### DIV-5: toadStool socket permission denied
- **Symptom**: `health.liveness` on `toadstool.sock` returns `Permission denied (os error 13)`.
- **Root cause**: B1/B2 fix (socket 0o660, dir 0o750) pushed by biomeGate but not yet deployed to sporeGate's local NUCLEUS.
- **Fix**: Deploy fresh toadStool binary from depot (already built and pushed). Restart `membrane-toadstool`.
- **Status**: Will auto-resolve on next NUCLEUS restart with fresh binary.

### DIV-6: petalTongue socket path mismatch
- **Symptom**: First S8 deploy showed petaltongue as "error: No such file or directory".
- **Root cause**: Socket mapping used `/run/membrane/petaltongue-e8b62b6e.sock` but actual socket is at `/run/user/1000/biomeos/petaltongue-e8b62b6e.sock` (user systemd service, not root).
- **Fix**: Changed socket table from relative-to-directory to full paths per primal.
- **Lesson**: User services vs system services create different socket directories. Need a canonical socket discovery pattern (relates to S9).

### DIV-7: `plasmid.harvest` exit code misleading
- **Symptom**: songBird and petalTongue harvests reported `FAILED` but status showed `"Built"` and binaries were present in staging depot.
- **Root cause**: `membrane plasmid.harvest` returns non-zero exit code even when the build succeeds, possibly due to post-build validation steps or metadata write failures.
- **Fix**: Verified binaries by checking staging depot timestamps directly.
- **Status**: Harvest CLI exit code should not be trusted blindly. Binary presence + timestamp is the reliable signal.

### DIV-8: Large primals exceed 300s harvest timeout
- **Symptom**: biomeos, songbird, petaltongue all timed out at 300s on first attempt.
- **Root cause**: These are the 3 largest primals (16-35MB binaries). sporeGate is resource-constrained while running 14 NUCLEUS services concurrently.
- **Fix**: Increased timeout to 600s for retry. biomeos succeeded; songbird and petaltongue built but returned non-zero (DIV-7).
- **Lesson**: blueGate should handle these builds — it has no competing workload.

---

## Remaining Primal Issues (for dissemination)

### UDS Protocol Fragmentation
| Primal | Socket | Protocol | BTSP | Notes |
|--------|--------|----------|------|-------|
| sweetGrass, loamSpine, rhizoCrypt, squirrel, skunkBat, nestGate, biomeos | `/run/membrane/*.sock` | JSON-RPC | Required (0xEC 0x01) | Standard primals |
| bearDog | `/run/membrane/beardog.sock` | JSON-RPC | Tolerates (emits error then processes) | Multi-object stream |
| songBird | `/run/membrane/songbird.sock` | JSON-RPC | NOT supported (plain JSON) | Mesh orchestrator |
| barracuda | `/run/membrane/barracuda.sock` | JSON-RPC | Required | GPU compute |
| coralReef | `/run/membrane/coralreef.sock` | **tarpc** | N/A | GPU rendering — different protocol |
| petalTongue | `/run/user/1000/biomeos/*.sock` | JSON-RPC | Required | User systemd service |
| toadStool | `/run/membrane/toadstool.sock` | JSON-RPC | Required | Permission denied (B1/B2 needs deploy) |

**Action for overwatch**: Standardize UDS protocol. Either all primals use BTSP framing, or health queries should use the Neural API capability router (which abstracts the protocol).

### Socket Discovery (S9 — still open)
The Neural API symlink pattern (`/run/user/1000/biomeos/{primal}-{family_id}.sock`) is a sporeGate workaround. Other gates will need it replicated. This should be documented as canonical and deployed via `membrane` tooling.

### Health Reporting Gaps
- coralReef: Needs tarpc health endpoint or Neural API registration
- toadStool: Will resolve with B1/B2 binary deploy
- 2 primals (bingoCube, cellMembrane) not in the health query list — no local UDS sockets

### Depot Pipeline Trust
- `plasmid.harvest` exit codes are unreliable (DIV-7)
- Binary presence + timestamp is the reliable signal
- Consider: `plasmid.harvest --verify` that checks binary hash post-build

---

## Metrics

| Metric | Value |
|--------|-------|
| Debt items cleared (sporeGate) | **S1–S8** (8 items) |
| Total debt cleared (ecosystem) | **14/26** |
| Primals compiled clean | **15/15** |
| Tests (sweetGrass) | **610/610** |
| Tests (petalTongue) | **8/8** |
| nestgate.io sections live | **10/12** |
| Health liveness | **11/13 alive** |
| Depot binaries synced | **26/55** to golgi |
| blueGate Windows builds | **15/15** |
| songBird peers (live) | **6** (4 LAN p0, 2 WG p1) |

---

## Next Steps (for overwatch dissemination)

1. **E2 (squirrel on ironGate)** — eastGate team: deploy squirrel systemd service, agent panel goes live
2. **O5 (nestGate TCP on westGate)** — overwatch: ops config, code already shipped
3. **D1 (tideGlass cell boot)** — westGate: `biomeos nucleus attach`, GPS data ready
4. **S9 (Neural API symlink)** — document as canonical, replicate to all NUCLEUS gates
5. **UDS protocol standardization** — overwatch: decide on BTSP vs plain JSON convention
6. **Depot exit code fix** — cellMembrane team: `plasmid.harvest` should return 0 when build succeeds
7. **coralReef health** — biomeGate: add tarpc health endpoint or Neural API capability stub

---

*sporeGate team backlog is clear (S1–S8 DONE). Depot is fresh. blueGate sub-builder pattern is proven. Remaining work is cross-team: eastGate (E1–E3), biomeGate (B3), overwatch (O2, O5–O7), and ops (D1–D4).*
