# AAR: eastGate Live NUCLEUS Execution — Wave 114
**Date**: 2026-06-16T01:11Z  
**From**: primalSpring overwatch (eastGate)  
**Classification**: FRAGO — disseminate to all primal teams  

---

## Summary

Executed `nucleus_launcher --profile primalspring start --allow-degraded --tcp` on eastGate.
**All 11 primals spawn and run** from the x86_64-musl depot. Health probes report only
4/11 reachable due to **riboCipher signal incompatibility** — the primals are alive but
reject the `[0xEC, 0x01]` prefix our probes now send.

---

## Execution Data

| Metric | Result |
|--------|--------|
| Binary discovery | **13/13** found (4-tier search, `ECOPRIMALS_PLASMID_BIN` set) |
| Processes spawned | **11/11** |
| Processes confirmed running (`ps`) | **11/11** (all alive) |
| Health probe: ALIVE | **4/11** (beardog, petaltongue via UDS; coralreef, nestgate via TCP) |
| Health probe: UNREACHABLE | **7/11** (riboCipher rejection) |
| Songbird federation | **DOWN** (TLS handshake failure — see below) |
| Registry seeding | **0/10** (Songbird unreachable) |
| Validation suite (`--structural-only`) | **30 pass, 8 fail** |
| `bootstrap-readiness` scenario | **ALL PASS** (7/7 checks, 3 advisory skips) |
| `ribocipher-signal-acceptance` | **ALL PASS** (structural green, live gracefully skipped) |

---

## Root Cause Analysis

### RC-1: riboCipher Signal Incompatibility (BLOCKING)

**What**: primalSpring (Wave 111) began prepending `[0xEC, 0x01]` to all outbound IPC
connections per the riboCipher transport convergence standard. Upstream primals have NOT
shipped server-side acceptance of this prefix.

**Evidence from logs**:
- `beardog.log`: `BTSP frame too large: 3959520034 bytes` — interprets `0xEC01` as frame length
- `squirrel.log`: `stream did not contain valid UTF-8` — rejects `0xEC 0x01` as text
- `songbird.log`: separate issue (TLS handshake, see RC-2)

**Impact**: Health probes, registry seeding, and capability discovery all fail. Primals
are running and serving on their sockets but cannot be reached by riboCipher-compliant clients.

**Fix required per primal**: Add a 2-byte prefix consumer at connection accept:
```rust
// At socket accept, before JSON-RPC parsing:
let mut prefix = [0u8; 2];
stream.read_exact(&mut prefix)?;
if prefix == [0xEC, 0x01] {
    // riboCipher clear tier — proceed with JSON-RPC
} else {
    // Legacy client — unread the bytes (or reject)
}
```

### RC-2: Songbird TLS Handshake Failure (SEPARATE)

**What**: Songbird attempts a TLS handshake on startup (likely federation or upstream
registry call) but connects to port 80 instead of 443.

**Evidence**: `songbird.log`:
```
Server responded with HTTP instead of TLS (got 'HTTP/1.1 400 Bad Request')
```

**Impact**: Songbird starts but cannot establish federation, so mesh registration fails.

**Fix**: Verify Songbird's federation/upstream URL configuration. This may be a
stale config pointing to HTTP instead of HTTPS, or a missing port override.

---

## Validation Failures Breakdown (8 scenarios)

| Scenario | Failures | Root Cause | Owner |
|----------|----------|------------|-------|
| `full-nucleus` | 7 capabilities unresolvable | CompositionContext can't discover (Songbird down) | songbird team |
| `dark-forest-gate` | 3 (token, federation, ports) | beardog rejects riboC probe; Songbird down | beardog, songbird |
| `socket-discovery` | 28 orphan sockets | Stale sockets from prior launches + rollback | primalSpring (cleanup) |
| `wan-ipc-tolerance` | 3 samples fail | Probes rejected (riboCipher) | all primals |
| `gate-expansion-readiness` | 1 (VPS cells) | VPS cell manifest not populated | cellMembrane |
| `btsp-cross-primal` | 3 (auth session) | beardog BTSP handshake fails on riboC prefix | beardog |
| `cascade-provenance-match` | 2 (checksums, provenance) | Depot missing `checksums.toml` and `provenance.toml` | cellMembrane/pepti |
| `graphenegate-readiness` | 7 UDS coverage gaps | Socket naming includes family suffix, not matching base pattern | primalSpring (naming evolution) |

---

## Shipped by primalSpring (This Session)

| Deliverable | Detail |
|-------------|--------|
| `nucleus_launcher validate` subcommand | Runs scenario suite against live/structural NUCLEUS. `--scenario <id>` and `--structural-only` flags. |
| `s_bootstrap_readiness` (scenario 62) | Pre-deployment infrastructure validation (fieldGate first-ant hurdles codified). |
| Live execution validation | Confirmed all 11 primals spawn from depot on eastGate. |
| riboCipher incompatibility diagnosis | Full log evidence and per-primal fix pattern documented. |

---

## FRAGO: Action Items for Teams

### Priority 1 — riboCipher Server-Side Acceptance (ALL PRIMAL TEAMS)

Every primal must ship a 2-byte prefix consumer at connection accept. Without this,
no riboCipher-compliant client (including the launcher's health probes) can reach the primal.

| Primal | Status | Urgency |
|--------|--------|---------|
| beardog | BTSP frame length misparse | P1 — blocks auth for entire mesh |
| songbird | TLS config issue (separate) | P1 — blocks federation + discovery |
| rhizocrypt | Rejects prefix | P1 |
| barracuda | Rejects prefix | P2 |
| loamspine | Rejects prefix | P2 |
| toadstool | Rejects prefix | P2 |
| squirrel | Invalid UTF-8 rejection | P2 |
| sweetgrass | Rejects prefix | P2 |
| coralreef | **PASSES** (no health method, accepts connection) | ✅ |
| nestgate | **PASSES** (no health method, accepts connection) | ✅ |
| petaltongue | **PASSES** (UDS, accepts riboCipher) | ✅ |

### Priority 2 — Depot Completeness (cellMembrane/pepti)

- [ ] Generate and include `checksums.toml` in depot artifacts
- [ ] Generate and include `provenance.toml` for build traceability
- [ ] Ensure depot has biomeOS binary (binary path discovery fallback)

### Priority 3 — Songbird Federation Config (songbird team)

- [ ] Investigate TLS handshake connecting to port 80 instead of 443
- [ ] Verify federation URL env var (`SONGBIRD_FEDERATION_URL` or equivalent)
- [ ] Confirm Songbird can start federation without upstream TLS dependency

### Priority 4 — primalSpring Local (self)

- [x] Stale socket cleanup (41 orphans from dual-launch)
- [ ] Socket naming evolution: family-suffixed sockets (`{primal}-{family}.sock`) need
      pattern matching in `s_socket_discovery` and `s_graphenegate_readiness`

---

## Exit Criteria Update (Wave 114)

| # | Criterion | Status |
|---|-----------|--------|
| 1 | fieldGate (NUC): 13/13 alive + mesh | **✅ DONE** |
| 2 | grapheneGate (Pixel): aarch64 depot + 13/13 | BLOCKED (harvest) |
| 3 | flockGate (WAN): relay depot + 13/13 | TODO |
| 4 | RustDesk relay + ABG member connects | TODO |
| 5 | pepti fresh harvest (x86 + aarch64) | **✅ x86 DONE** / aarch64 TODO |

**New finding**: Even with depot complete, primals will NOT pass health checks until
riboCipher acceptance is shipped. This is a **soft blocker** for exit criteria 2-4 if
launcher health is used as the "alive" validator.

**Workaround**: Use `--skip-preflight --no-rollback` + manual `ps` confirmation until
primals ship server-side acceptance. Or temporarily disable riboCipher prefix in health
probes (not recommended — masks the real convergence gap).

---

## Recommendation

Ship riboCipher acceptance across all primals as P1 before Friday deadline. The fix is
mechanical (2 lines at connection accept). Without it, the launcher cannot validate any
gate as "13/13 ALIVE" even though all processes are running.

---

*Filed by primalSpring overwatch on eastGate — Jun 16, 2026 01:16Z*
