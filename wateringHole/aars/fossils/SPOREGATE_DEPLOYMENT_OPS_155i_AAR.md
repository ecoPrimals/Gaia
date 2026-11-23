# sporeGate Deployment Ops — Wave 155i AAR

**Date**: 2026-07-29
**Gate**: sporeGate (build authority, peptidoglycan anchor H1)
**Scope**: Depot refresh, membrane J6, Caddy routing fix, gate health improvement

---

## Summary

Wave 155i deployment session on sporeGate: rebuilt membrane with J6 (gate.configure/
gate.apply), full harvest of all primals including compute trio glibc targets, fixed
depot.primals.eco routing, regenerated BLAKE3 checksums. Gate health improved from
5/11 to 9/11 OK probes. All sporeGate-owned P1 items from the 155i rollup are
now resolved.

## What We Did

### 1. membrane Depot Binary Rebuild — J6 Operational (P1 #3 RESOLVED)

**Problem**: The deployed membrane binary predated cellMembrane's J6 completion
(`gate.configure` / `gate.apply`). The blurb listed "Rebuild membrane depot binary
with gate.configure/gate.apply" as P1 #3.

**Fix**: Pulled latest cellMembrane (`8d9bb58` — P0 glibc + P1 WG DNS fix), clean
rebuilt membrane-shadow, deployed locally + pushed to golgiBody depot.

**Result**: `membrane gate.configure` reports composition and service configs.
`membrane gate.apply` attempts systemd installation (requires sudo, as expected).
Binary size: 16,055,304 bytes.

### 2. Full Compute Trio Harvest — musl + gnu Targets

**Problem**: strandGate awaiting glibc depot rebuild for RTX 3090 compute workloads.
cellMembrane had shipped the `targets_for_primal()` auto-gnu fix, but the depot
binaries hadn't been rebuilt from latest source.

**Fix**: Harvested all three compute primals with both targets using
`ECOPRIMALS_ROOT` + `--local --force`:

| Primal | musl (KB) | gnu (KB) | Commit |
|--------|-----------|----------|--------|
| barraCuda | 11,410 | 11,529 | `ceca2b1b` |
| coralReef | 9,186 | 9,086 | `94ee28a1` |
| toadStool | 13,259 | 13,090 | `40d0ae30` |

All six binaries pushed to golgiBody via rsync.

**Result**: `depot.primals.eco/depot/x86_64-unknown-linux-gnu/` serves 3 glibc
binaries. strandGate compute trio unblocked.

### 3. Full Primal Fleet Refresh

**Problem**: Several depot binaries were 13-15 days stale. nestgate binary was from
Jul 14 (previously failed due to binary path mismatch, now fixed by code team).

**Fix**: Harvested all available primals from local gardens. 16 musl binaries fresh,
pushed to golgiBody.

**Stale → Fresh**:
- nestgate: Jul 14 → Jul 29 (commit `263e68a3`, 8,660KB)
- All other musl primals: refreshed from latest HEAD commits

**Result**: `depot.freshness` probe: "oldest 3h" (was "oldest 14d").

### 4. depot.primals.eco Routing Fix — /depot/ Prefix

**Problem**: `sovereignty.s3_content` probe returned 404. The probe constructs
`https://depot.primals.eco/depot/<arch>/<binary>` but Caddy's root was
`/opt/ecoPrimals/depot` with binaries under `primals/` subdirectory. The `/depot/`
prefix mapped to a nonexistent directory.

**Fix**: Added a `/depot/*` handler block with `uri strip_prefix /depot` pointing
root to `/opt/ecoPrimals/depot/primals/`. The default handler still serves from
`/opt/ecoPrimals/depot` for direct `/primals/` access and browse.

**Result**: Both URL patterns return 200:
- `depot.primals.eco/depot/x86_64-unknown-linux-musl/beardog` → 200 (probe path)
- `depot.primals.eco/primals/x86_64-unknown-linux-musl/beardog` → 200 (direct path)

### 5. BLAKE3 Checksums Regenerated

**Problem**: `depot.integrity` showed 14 hash mismatches — checksums.toml dated
Jul 16 (Wave 142b), binaries were freshly rebuilt.

**Fix**: Used `b3sum` to regenerate BLAKE3 hashes for all 19 binaries (16 musl +
3 gnu). Wrote new `checksums.toml`, pushed to both local depot and golgiBody.

**Result**: `depot.integrity`: "16 verified, 0 hash mismatch, 0 missing".

### 6. golgiBody Service Verification

Cascaded from golgiBody and verified all services:
- **Caddy**: Running at `/opt/membrane/caddy` (12 site blocks), port 443
- **step-ca**: Active on port 9443, `ca.primals.eco/health` returns 200
- **depot**: `depot.primals.eco/health` returns 200
- **RustDesk**: hbbs + hbbr operational

---

## Gate Health Improvement

| Probe | Before | After |
|-------|--------|-------|
| depot.integrity | DEGRADED (14 hash mismatch) | **OK** (16 verified, 0 mismatch) |
| depot.freshness | DEGRADED (oldest 14d) | **OK** (oldest 3h) |
| sovereignty.s3_content | DEGRADED (404 Not Found) | **OK** (serving 8163KB) |
| vcs.parity | DEGRADED (21 drifted) | **OK** (0 drifted) |
| primals.alive | OK (13/13) | OK (13/13) |
| sovereignty.s1_tls | OK | OK |
| sovereignty.s2_relay | OK | OK |
| sovereignty.s4_auth | OK | OK |
| service.crash-loop | OK | OK |
| mesh.reachability | DEGRADED | DEGRADED (code team: songBird) |
| rootpulse.ledger | DEGRADED | DEGRADED (code team: cellMembrane) |

**Score: 5/11 → 9/11 OK probes.**

---

## P0/P1 Rollup Reconciliation (Wave 155i Blurb)

| # | Priority | Issue | Status |
|---|----------|-------|--------|
| 1 | P0 | biomeOS BTSP session propagation | Code team (biomeOS) |
| 2 | P0 | biomeOS riboCipher transport | Code team (biomeOS) |
| 3 | P1 | Rebuild membrane depot binary | **RESOLVED (this session)** |
| 4 | P1 | Deploy step-ca on golgiBody | **RESOLVED (155h session)** |
| 5 | P1 | toadStool deployment model docs | Code team (toadStool) |
| 6 | P1 | hotSpring Forgejo pack corruption | eastGate admin |
| 7 | P1 | nestGate ghost methods | Code team (nestGate) |

All sporeGate-owned items are resolved. Remaining P0s are biomeOS code team work.

---

## Depot Manifest (Post-155i)

**golgiBody depot.primals.eco**:

| Target | Binaries | Total Size |
|--------|----------|------------|
| x86_64-unknown-linux-musl | 16 | ~178MB |
| x86_64-unknown-linux-gnu | 3 (barraCuda, coralReef, toadStool) | ~34MB |

BLAKE3 checksums verified: 19/19, 0 mismatches.

---

*sporeGate deployment ops, Wave 155i. Full depot refresh: 16 musl + 3 gnu binaries
from latest source. membrane J6 operational. Caddy depot routing fixed. Checksums
regenerated. Gate health 9/11. All sporeGate P1 items resolved. — sporeGate, Wave 155i*
