# AAR: westGate Wave 155i Cascade — ZFS CAS Migration + Provenance Trio Validation

**Gate:** westGate
**Date:** 2026-07-29
**Operator:** westGate overwatch (agentic)
**Wave:** 155i (post-cascade from golgiBody)
**Scope:** Cascade review, CAS→ZFS migration, Provenance Trio E2E validation, storage tier profiling
**Prior AAR:** `WESTGATE_NEST_ATOMIC_MULTICOMP_155i_AAR.md` (multi-composition deployment)

---

## What Happened

Cascaded from golgiBody (6 repos with upstream changes), reviewed Wave 155i blurb,
then executed local hardware and primal work while nestGate team develops in parallel
IDE using our ZFS pools.

---

## Cascade Summary

| Repo | Commits | Key Changes |
|------|---------|-------------|
| bearDog | +2 | ACME Phase 2 crypto delegation surface, status AAR |
| songBird | +1 | Mesh refactor: enrollment crypto + mesh helpers extracted, all files <800L |
| sweetGrass | +3 | **G3 wiring COMPLETE**: LedgerClient, `braid.commit`→loamSpine, v0.8.0 (1,625 tests) |
| cellMembrane | +1 | P0 glibc `targets_for_primal()` auto-append gnu, P1 WG DNS fix |
| skunkBat | +1 | Cargo.lock dependency update |
| wateringHole | +4 | Composition broker handoff, wave 155i blurb, golgiBody auto-publishes |

All pulls clean (rebase on main). No merge conflicts.

---

## What Worked

### 1. CAS Migration to ZFS — Symlink Approach

**Problem:** The depot nestGate binary (v0.5.0) predates the FHS centralization commit
(`3ca3e1bc`) that wired `NESTGATE_STORAGE_PATH` env var into `storage_base_path()`.
Despite the env var being set and visible in `/proc/PID/environ`, the binary's
`content_cas_path()` code path ignores it and writes to the XDG default
(`~/.local/share/nestgate/storage/`).

**Solution:**
```
rsync -av ~/.local/share/nestgate/storage/ /mnt/nestgate/cold/zfs/cas/
mv ~/.local/share/nestgate/storage ~/.local/share/nestgate/storage.nvme-pre-zfs
ln -s /mnt/nestgate/cold/zfs/cas ~/.local/share/nestgate/storage
```

**Result:** All CAS writes now land on ZFS transparently. 3,117 files migrated.
New `content.put` verified landing on `/mnt/nestgate/cold/zfs/cas/datasets/`.
The depot binary doesn't know it's writing to ZFS — it follows the symlink.

**Pattern for upstream:** Symlink-based tier routing is a valid deployment pattern
when depot binaries lag source. The `NESTGATE_STORAGE_PATH` env var support in
source is correct — once the depot binary is rebuilt, the symlink can be removed
and the env var will work natively.

### 2. bearDog Socket Path Fix

`BEARDOG_SOCKET` in both `nest.env` and `nestgate.env` was pointing to
`beardog-westgate-tower-155f.sock` (family-scoped name) but bearDog registers
as `beardog-default.sock` (no family suffix in this binary version).

**Fix applied:** Updated both env files, restarted Provenance Trio services.
sweetGrass crypto signing degradation (`crypto provider unavailable: No such file
or directory`) resolved — now reaches bearDog but gets health stub response
(see below).

**Pattern for upstream:** bearDog socket naming convention needs documentation.
Does bearDog use `beardog-{family_id}.sock` or always `beardog-default.sock`?
The inconsistency between Tower primals (family-scoped names) and bearDog
(default name) causes silent failures in dependent services.

### 3. Individual Primal IPC — All 8 Services Healthy

All 8 services confirmed healthy via UDS JSON-RPC:

| Service | Socket | Health | Version |
|---------|--------|--------|---------|
| beardog-tower | `beardog-default.sock` | alive | 0.9.0 |
| songbird-tower | `songbird-westgate-tower-155f.sock` | healthy | 0.2.1 |
| skunkbat-tower | (via beardog) | active | 0.2.18 |
| nestgate-tower | `nestgate-westgate-tower-155f.sock` | healthy | 0.5.0 |
| rhizocrypt-tower | `rhizocrypt-westgate-tower-155f.sock` | True | 0.14.17 |
| loamspine-tower | `loamspine-westgate-tower-155f.sock` | Healthy | 0.9.16 |
| sweetgrass-tower | `sweetgrass-westgate-tower-155f.sock` | healthy (riboCipher) | 0.7.64 |
| neural-api-tower | `neural-api-westgate-tower-155f.sock` | active | 0.1.0 |

### 4. Storage Tier Profiling — Baseline Established

| Tier | Device | Seq Write (100MB dsync) | Seq Read (100MB) | CAS Pattern (100×50KB) |
|------|--------|-------------------------|-------------------|------------------------|
| **T2** | NVMe Samsung 970 EVO+ 2TB | 316 MB/s | 2.9 GB/s | (backup only now) |
| **T4** | ZFS HDD mirrors 2×14TB×2 | 25.5 MB/s | 11.4 GB/s (ARC cached) | 268 writes/s, 833 reads/s |

- **ARC hit rate:** 100.0% (191.6 MB in ARC)
- **L2ARC:** 86.4 MB warming, 0 hits yet (needs sustained read workload to populate)
- **ZFS tuning:** `compression=lz4`, `atime=off`, `recordsize=128K`

**Insight for bulk ingestion:** The 25.5 MB/s dsync write rate on HDDs means a 1TB
AlphaFold ingest would take ~11 hours with synchronous writes. For bulk ingestion,
we should either batch writes with async flush, or stage on NVMe first and
`zfs send` to HDD pool. The L2ARC SSD (2TB) can cache the hot working set.

---

## What Did Not Work

### 1. Depot Binary Lag — Pattern Now Affects 3 Primals (P1→P0)

| Binary | Depot Version | Source Version | Missing Feature |
|--------|---------------|----------------|-----------------|
| nestGate | 0.5.0 (pre-FHS) | 0.5.0 (post-FHS) | `NESTGATE_STORAGE_PATH` env var, `config` subcommand |
| sweetGrass | 0.7.64 | 0.8.0 | G3 LedgerClient (`braid.commit`→loamSpine), `anchoring.verify` ledger proof |
| cellMembrane | pre-J6 | post-J6+glibc | `gate.configure`, `gate.apply`, glibc target auto-append |

**This is now a systemic pattern, not a one-off.** Every depot binary lags the
source by 1-3 features. The depot rebuild is not just a cellMembrane issue —
it's a sporeGate operational cadence issue.

**Recommendation:** After each code team ships a feature (especially IPC-affecting
changes), sporeGate should trigger a depot rebuild for that primal. The
`plasmid.push` + `depot_sync` pipeline (J2 CLOSED) exists — it just needs to be
run. Consider a golgiBody hook: merge to main → auto-rebuild genomeBin → push to depot.

### 2. bearDog `crypto.sign_ed25519` Returns Health Stub

When loamSpine calls bearDog's `crypto.sign_ed25519` to sign a ledger entry,
bearDog returns `{"primal":"beardog","status":"alive","version":"0.9.0"}` — a health
response, not a signature.

**Root cause:** bearDog v0.9.0 doesn't implement the `crypto.sign_ed25519` method.
The method falls through to the default handler (health response). The ACME Phase 2
crypto delegation surface (commit `cd509ac81`) adds the API shape but not the actual
signing implementation.

**Impact:** loamSpine `entry.append` fails with `transport error: crypto.sign_ed25519
result deserialize: missing field 'signature'`. The Provenance Trio data flow works
but the cryptographic attestation layer is incomplete.

**Upstream action (bearDog team):** Implement `crypto.sign_ed25519` method that
returns `{"signature": "<base64>", "public_key": "<base64>", "algorithm": "ed25519"}`.
This unblocks loamSpine entry signing and the full Provenance Trio crypto chain.

### 3. songBird Probing Without riboCipher — Constant Log Noise

songBird's capability discovery polls all sockets with raw JSON-RPC (no `[0xEC, 0x01]`
prefix). sweetGrass rejects every probe with "REJECTED: unsignalled connection
(no riboCipher prefix)". This generates 4-8 log lines every 30 seconds.

**Impact:** Journal noise, wasted IPC cycles. Not functionally broken (songBird
retries and discovers via other primals), but degrades observability.

**Upstream action (songBird team):** When probing a socket, attempt riboCipher-framed
`capabilities.list` first, then fall back to raw JSON-RPC only if riboCipher fails.
The `[0xEC, 0x01]` prefix is 2 bytes — trivial to prepend.

### 4. Socket Evaporation Under Service Restarts

When restarting a subset of services (e.g., `systemctl --user restart sweetgrass-tower
rhizocrypt-tower loamspine-tower`), other service sockets occasionally vanish
(e.g., nestgate socket disappears despite nestgate process still running).

**Observed:** nestgate PID alive, service status "active", but socket file gone from
`/run/user/1000/biomeos/`. A `systemctl --user restart nestgate-tower` restores it.

**Root cause hypothesis:** A service startup race — a restarting primal cleans up the
`biomeos` socket directory or a symlink target, inadvertently removing another
primal's socket file.

**Upstream action:** Each primal should only manage its own socket file. If a primal
creates a `biomeos` directory, it should not clean up files it didn't create.
Consider `PRIMAL_SOCKET_CLEANUP=own-only` as a startup flag.

---

## Provenance Trio Round-Trip Validation

Manually orchestrated (Neural API broker not ready) — each step exercised via
direct UDS JSON-RPC.

| Step | Primal | Method | Result |
|------|--------|--------|--------|
| 1. Store | nestGate | `content.put` | **PASS** — BLAKE3 `6a409f47...`, 245 bytes, stored on ZFS |
| 2a. DAG session | rhizoCrypt | `dag.session.create` | **PASS** — `019fae2b-02e8-...` |
| 2b. DAG event | rhizoCrypt | `dag.event.append` (DataCreate) | **PASS** — event hash `68d51797...` |
| 2c. Merkle root | rhizoCrypt | `dag.merkle.root` | **PASS** — root = event hash (single node) |
| 3a. Spine | loamSpine | `spine.create` | **PASS** — `019fae2b-3b86-...` |
| 3b. Anchor | loamSpine | `entry.append` (DataAnchor) | **FAIL** — bearDog `crypto.sign_ed25519` stub |
| 4. Braid | sweetGrass | `braid.create` (riboCipher) | **PASS** — `urn:braid:blake3:6a409f47...` |

**Conclusion:** 6/7 steps pass. The single failure (loamSpine entry signing) is
blocked on bearDog `crypto.sign_ed25519` implementation, not on loamSpine itself.
When bearDog ships signing, the full provenance chain
`content → DAG → certificate → attribution braid` will close.

---

## sweetGrass G3 Validation

The G3 wiring (LedgerClient, `braid.commit`→loamSpine) shipped in source at v0.8.0
(commit `666dea5`, 1,625 tests). **Cannot validate on westGate because the depot
binary is v0.7.64** (pre-G3). The `braid.commit` method exists in v0.7.64 but
doesn't forward to loamSpine — `anchoring.verify` returns `"unanchored"`.

**Gate team impact:** The sweetGrass G3 handoff (`SWEETGRASS_G3_WIRING_COMPLETE_WAVE155i.md`)
documents integration test expectations that require the v0.8.0 binary. Until the
depot rebuild, the test plan at line 119 of that handoff is blocked on westGate.

---

## ZFS Pool State

```
pool: nestgate — ONLINE, 0 errors
  mirror-0:  2×14TB OOS14000G — ONLINE
  mirror-1:  2×14TB OOS14000G — ONLINE
  cache:     1×2TB BX500 SSD  — ONLINE (L2ARC)
  spare:     1×14TB OOS14000G — AVAIL
```

| Dataset | Used | Available | Purpose |
|---------|------|-----------|---------|
| nestgate/cas | 7.50 MB | 25.3 TB | CAS content (via symlink) |
| nestgate/data | 96 KB | 20.0 TB | General data (quota 20TB) |
| nestgate/testing | 111 MB | 25.3 TB | Tier profiling test data |
| nestgate/cache | 96 KB | 25.3 TB | ZFS-level cache |
| nestgate/snapshots | 96 KB | 25.3 TB | Snapshot storage |

CAS contains 3,128 files across 108 families (mostly test fixtures from nestGate
test suite). 7 real PDB protein structures in `standalone` family (5 RCSB + 1 e2e
test + 1 provenance trio test). All on ZFS mirrored HDDs with LZ4 compression.

---

## Action Items for Upstream Teams

### P0 (Blocking)

| # | Item | Owner | Unblocks |
|---|------|-------|----------|
| 1 | **biomeOS BTSP session propagation** in signal graph executor | biomeOS | E2E signal graph validation, AlphaFold ingestion |
| 2 | **biomeOS riboCipher transport** in CLI paths (`send_jsonrpc`) | biomeOS | `biomeos nucleus ingest` → Neural API |

### P1 (High Impact)

| # | Item | Owner | Unblocks |
|---|------|-------|----------|
| 3 | **Depot rebuild** — nestGate, sweetGrass, cellMembrane (at minimum) | sporeGate ops | ZFS native path, G3 LedgerClient, gate.configure |
| 4 | **bearDog `crypto.sign_ed25519`** implementation | bearDog | loamSpine entry signing, Provenance Trio crypto chain |
| 5 | **songBird riboCipher probing** — prepend `[0xEC,0x01]` to capability polls | songBird | Eliminate sweetGrass log noise |
| 6 | **bearDog socket naming** — document `beardog-default.sock` vs `beardog-{family}.sock` | bearDog | Prevent silent IPC failures in dependent services |

### P2 (Operational)

| # | Item | Owner | Unblocks |
|---|------|-------|----------|
| 7 | **Auto-rebuild pipeline**: merge→rebuild→depot push per primal | sporeGate/golgiBody | Eliminates depot binary lag pattern |
| 8 | **Socket evaporation** under partial service restart | All primals | Multi-composition stability |
| 9 | **Bulk ingestion strategy** — async writes or NVMe staging for ~1TB | nestGate/westGate | AlphaFold ingest (25 MB/s dsync → ~11h for 1TB) |

---

## Metrics

| Metric | Value |
|--------|-------|
| Services deployed | 8 (Tower 3 + Nest 5) |
| Capabilities discovered | 1,704 |
| CAS objects on ZFS | 3,128 files |
| ZFS pool capacity | 25.3 TB available |
| ZFS errors | 0 |
| ARC hit rate | 100.0% |
| NVMe seq read | 2.9 GB/s |
| ZFS HDD seq write (dsync) | 25.5 MB/s |
| ZFS HDD CAS writes | 268 files/sec (50KB each) |
| ZFS HDD CAS reads (warm) | 833 files/sec (50KB each) |
| Provenance Trio steps passed | 6/7 |
| Upstream repos cascaded | 6 |

---

## Key Insight: Depot Binary Lag Is Now Systemic

The prior AAR identified the cellMembrane depot binary lag as a one-off. This session
reveals it affects at least 3 primals (nestGate, sweetGrass, cellMembrane) and is
growing. Each code team ships features faster than sporeGate rebuilds depot binaries.

**The fractal pattern holds:** ecoPrimals is evolving faster than its deployment
substrate can keep up. The J1/J2 jelly-string resolution (harvest + depot push)
created the mechanism — but the mechanism isn't triggered after every meaningful
commit. The solution is isomorphic with the problem: make the deployment pipeline
as alive as the code it ships.

golgiBody already has `auto-publish` hooks (visible in wateringHole commit history).
Extending this to trigger `plasmid.push` per-primal after merge would close the gap.

---

*Wave 155i. CAS migrated to ZFS (symlink). Provenance Trio validated (6/7 — bearDog
crypto.sign blocks entry signing). Storage tier profiled. 3 depot binaries lag source.
songBird probes without riboCipher. Socket evaporation on partial restarts. bearDog
socket naming inconsistency fixed locally. nestGate team developing in parallel IDE,
using our pools.*
