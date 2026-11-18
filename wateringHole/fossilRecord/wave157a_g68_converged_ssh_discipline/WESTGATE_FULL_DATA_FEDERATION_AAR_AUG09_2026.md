# AAR: westGate Data Federation — Provenance Trio, Jelly Strings, and Remaining Debt

**Gate**: westGate (192.168.4.155) | **Wave**: 155f→157a | **Date**: Aug 9, 2026
**From**: westGate hardware team
**To**: eastGate overwatch, all teams
**Scope**: Full retrospective — Aug 2–9, 2026 (7 sessions)

---

## Executive Summary

westGate went from a bare data landing zone to a **fully braided scientific database** with 153 datasets (3.3 TB raw data, 1.5 TB CAS), inline provenance on all ingress, convergence tiering between NVMe and HDD, and vine-bat gossip validation. Along the way we discovered and fixed **critical API surface mismatches** between what the pipeline assumed and what primals actually implement, identified **bearDog as a health-only stub** with no signing, and mapped the full jelly string inventory that still needs evolution into primal-native capabilities.

**By the numbers**: 989,500+ files braided. 153 datasets. 14/14 services. Vine-bat operational. 3 P0 upstream issues documented.

---

## 1. What We Built — Provenance Trio Extensions

### 1.1 Chunked Spine Braiding (Sessions 1–3)

**Problem**: Large datasets (AlphaFold: 1.5 TB, 989K files across 228 subdirectories) can't be braided atomically — memory, crash risk, and time.

**Solution**: Split into independent rhizoCrypt sessions per chunk/subdirectory, all committed to one loamSpine.

```
Dataset (1.5 TB, 228 chunks)
  ├── chunk/AF-A0A0A0MRZ7-F1-model_v4/
  │     └── rhizoCrypt session → DAG events → Merkle root
  │           └── loamSpine entry (DataAnchor)
  ├── chunk/AF-A0A0K2S2Z6-F1-model_v4/
  │     └── rhizoCrypt session → DAG events → Merkle root
  │           └── loamSpine entry (DataAnchor)
  └── ... × 228 chunks
        └── sweetGrass braid (composite hash over all chunk roots)
```

**Pattern proved**: crash-resumable via `.native_braid_state` file per dataset. Workers can restart and pick up from last committed chunk. Spine provides cryptographic proof that all chunks belong to the same dataset strand.

### 1.2 Middle-Out Parallel Braiding (Session 4)

**Problem**: Single-worker braiding of 228 chunks takes days on spinning disks.

**Solution**: Multiple workers claim different chunks via file-based atomic locks (`.claims/`), all committing to the same spine. Workers can start from opposite ends and "meet in the middle."

```
Worker 0/3: chunks 0, 3, 6, 9...
Worker 1/3: chunks 1, 4, 7, 10...
Worker 2/3: chunks 2, 5, 8, 11...
           ↓ all commit to ↓
        Single loamSpine instance
```

### 1.3 Convergence Tiering (Session 5)

**Problem**: NVMe warm CAS filled to 88% because nestGate has no warm→cold drain.

**Insight from overwatch**: "Tiering IS provenance." DAG collapse, dedup, and tier drain are structurally identical convergence operations.

**Built**: `convergence_drain.py` — walks warm CAS buckets, verifies existence on cold, evicts or replicates, records the drain in the provenance chain (rhizoCrypt DAG event + loamSpine DataAnchor + sweetGrass braid seal). Runs on a 30-minute systemd timer.

**Result**: 88% → 12% warm tier. 1,054.7 GB freed. Process is idempotent and crash-safe.

### 1.4 Inline Braiding / Atomic Ingress (Sessions 3–5)

**Problem**: Download-first, braid-later left data unprovenanced for hours/days.

**Solution**: `alphafold_full_sync.sh` calls `native_braid.py --incremental` after **every rsync phase**. No data exists on disk without a corresponding braid.

**Correction from overwatch**: "No more data ingress without braids!" — eliminated the download-then-braid pattern entirely.

---

## 2. Successes

| Achievement | Detail |
|-------------|--------|
| 989,500+ files braided | AlphaFold structures (228 chunks), AlphaFold (7 chunks), SRA FASTQ (5 chunks) |
| 153 datasets on CAS | 3.3 TB raw data, 1.5 TB CAS content-addressed |
| Inline braiding | Every rsync phase braids atomically before next |
| Convergence drain | NVMe 88%→12%, 1 TB freed, recorded in prov chain |
| 14/14 services | Full NUCLEUS including swarmVine vine-bat |
| Vine-bat loop | gossip.spread → skunkBat 8-check validate → ingest/reject |
| Depot redeploy | 17 binaries from golgi, no local builds |
| NG-05 federation | nestGate TCP + songBird 26 caps registered |
| Pipeline API fix | content.ingest→content.put, correct param names |

## 3. Failures and What We Learned

### 3.1 Phantom API Surface (P0)

`native_braid.py` was designed around three nestGate methods that **don't exist**:

| Assumed Method | Reality | Impact |
|---------------|---------|--------|
| `content.ingest(directory)` | Does not exist in nestGate v0.5.0 | All braiding silently failed |
| `content.stat(hash)` | Does not exist | Monitoring broken |
| `content.put(content_hash, source_path)` | Params are `hash`, `content_base64` | Every CAS write failed |

**Root cause**: Pipeline was written against an aspirational API (Rust walks directory, hashes, CAS stores). The actual nestGate surface is simpler: `content.put` takes base64-encoded data and a BLAKE3 hash. Python must walk directories and hash files.

**Lesson**: Never code against an API you haven't tested with a live primal. The capability registry TOML and the actual RPC surface diverged significantly.

### 3.2 BearDog Health-Only Stub (P0)

BearDog v0.9.0 returns its health check response for **every method call**, including completely fabricated method names. It has no Ed25519 signing surface.

```
crypto.sign_ed25519 → {"primal":"beardog","status":"alive","version":"0.9.0"}
nonexistent_xyz     → {"primal":"beardog","status":"alive","version":"0.9.0"}
```

**Impact**: loamSpine `session.commit` requires `crypto.sign_ed25519` for commit signatures. All spine commits fail. We made this non-fatal (commits deferred) so CAS + DAG still records data, but **no braids currently have cryptographic spine signatures**.

**Lesson**: A primal that returns 200 OK for every method is worse than one that errors — it masks missing capabilities.

### 3.3 BearDog Socket Name Mismatch

BearDog creates `beardog-default.sock` instead of `beardog-westgate-tower-155f.sock`. Every other primal uses the `{name}-{family_id}.sock` convention. LoamSpine looks for the family-id variant and fails silently.

**Fix**: Persistent symlink in `songbird-register.sh`.

**Lesson**: Socket naming conventions must be enforced at the platform level (toadStool template), not worked around per-gate.

### 3.4 BiomeOS FD Leak (P1, ongoing)

The auto-discovery health check loop opens Unix domain sockets and never closes them. After 4 `capability.call` invocations, FDs jump from 14 to 58,613.

```
Fresh start:    14 FDs
After 4 calls:  58,613 FDs
Result:         capability.call times out, all routing broken
```

**Workaround**: Direct primal socket calls work at 0.2ms. Pipeline bypasses biomeOS entirely.

**Impact**: The Neural API cannot be used for any real workload. `capability.resolve` works (identifies correct socket), but `capability.call` (forward request to primal) is unusable.

### 3.5 sweetGrass Parameter Mismatch

`braid.create` expects `data_hash` + `strand_id`. Pipeline was sending `content_hash` without `strand_id`. Every braid creation was failing with a parameter error.

**Fix**: Corrected to `data_hash`, added `strand_id`, moved metadata into `metadata` object.

---

## 4. Jelly Strings — Python Glue That Needs Primal Evolution

These are places where Python orchestration code reimplements what should be primal-native capability. Each is a candidate for evolution into biomeOS routing or direct primal methods.

### 4.1 Directory Walking + Hashing (HIGH)

**Current**: Python `os.scandir()` + `blake3.blake3()` per file + `base64.b64encode()` + `content.put` RPC per file.

**Should be**: `nestGate content.ingest(directory)` — Rust walks, hashes, CAS stores with dedup. Single RPC, zero Python I/O.

**Blocker**: Method doesn't exist in nestGate. Needs nestGate team to implement.

**Impact**: Python reads every file twice (once to hash, once to base64-encode). For 1.5 TB of data, this doubles the I/O and memory pressure. The base64 encoding alone inflates payload by 33%.

### 4.2 Chunk Coordination (MEDIUM)

**Current**: File-based atomic locks (`.claims/chunk.claim`) with OS-level `O_CREAT|O_EXCL`. State tracked in `.native_braid_state` JSON on cold ZFS.

**Should be**: rhizoCrypt session-level coordination or biomeOS task graph. Workers register with a coordinator, receive chunk assignments, report completion. No filesystem locking.

**Blocker**: No coordination primitive exists in any primal. biomeOS graph executor could serve this role.

### 4.3 NVMe Staging (MEDIUM)

**Current**: Python `shutil.copy2()` or `subprocess.run(["rsync", ...])` to copy from cold HDD to NVMe before processing.

**Should be**: nestGate tier-aware `content.ingest` that automatically stages to the fastest available tier. Or cellMembrane transport that understands tier topology.

**Blocker**: Tiering is not a primal concept yet. Convergence Tiering pattern (subGen doc) proposes how this could work.

### 4.4 Provenance Chain Orchestration (MEDIUM)

**Current**: Python calls 5 primals in sequence: `content.put` → `dag.event.append_batch` → `dag.dehydration.trigger` → `session.commit` → `braid.create`.

**Should be**: biomeOS Neural API graph execution. Define a provenance graph: `CAS → DAG → Merkle → Spine → Braid`, dispatch it, get a receipt. Single `capability.call` with a graph descriptor.

**Blocker**: biomeOS graph executor exists (55 graphs, 1.2ms/exec on eastGate per primalSpring exp118) but `capability.call` is broken by FD leak. Also, graph definitions for provenance chain don't exist yet.

### 4.5 Convergence Drain (LOW→MEDIUM)

**Current**: `convergence_drain.py` — Python walks warm CAS buckets, checks cold existence, copies/evicts. Records in prov chain.

**Should be**: nestGate-native drain operation triggered by cellMembrane backpressure signal. Or a rhizoCrypt convergence operation that treats warm→cold as a DAG collapse.

**Blocker**: No tier-aware operations in nestGate. The Convergence Tiering subGen doc proposes this architecture but it's not implemented.

### 4.6 BearDog Signing (CRITICAL)

**Current**: Pipeline calls `beardog sign` directly, and loamSpine calls `crypto.sign_ed25519` internally. Both fail because bearDog is a health-only stub.

**Should be**: BearDog implements Ed25519 sign/verify. loamSpine uses it for commit signatures. Pipeline uses it for braid signatures.

**Blocker**: BearDog binary lacks signing surface. Depot binary needs rebuild with actual crypto ops.

---

## 5. Technical Debt Inventory

### Primal API Surface

| Primal | Issue | Severity |
|--------|-------|----------|
| nestGate | No `content.ingest`, no `content.stat` | HIGH |
| nestGate | `content.put` requires base64 (no file path ingest) | MEDIUM |
| bearDog | Health-only stub, no Ed25519 sign/verify | CRITICAL |
| bearDog | Socket named `beardog-default.sock` not family-id | LOW |
| loamSpine | `session.commit` hard-fails on bearDog sign failure | MEDIUM |
| sweetGrass | `braid.create` param names undocumented | LOW |
| biomeOS | FD leak in auto-discovery loop (58K FDs after 4 calls) | HIGH |
| biomeOS | `capability.call` unusable for production workloads | HIGH |

### Pipeline Debt

| Item | Current | Target |
|------|---------|--------|
| File hashing | Python blake3 + base64 | nestGate native ingest |
| Chunk coordination | Filesystem locks | biomeOS task graph or rhizoCrypt sessions |
| NVMe staging | Python rsync/shutil | nestGate tier-aware ingest |
| Prov chain | 5 sequential RPCs | biomeOS graph: single dispatch |
| Convergence drain | Python timer script | nestGate/cellMembrane native drain |
| Error handling | Non-fatal wrappers everywhere | Primals handle gracefully |

### Infrastructure Debt

| Item | Status |
|------|--------|
| songBird depot binary pre-seam | P0 — gates get broken gossip.inject |
| skunkBat + swarmVine not in depot | Built from source on westGate/ironGate |
| bearDog depot binary has no signing | P0 — all spine commits unsigned |
| biomeOS FD leak | P1 — workaround: direct socket calls |
| southGate mesh enrollment | Deferred — not discoverable on LAN |
| 12 datasets need browser auth | Blocked on user registration |

---

## 6. Topology Lessons — What the Hardware Taught Us

### Storage Topology

```
T0: RAM (ZFS ARC)           ← read cache, automatic
T1: NVMe (1.8 TB)           ← ephemeral hot workspace (braid here, drain after)
T2: SSD (L2ARC)             ← warm read cache, automatic
T3: HDD pool (63.7 TB ZFS)  ← cold archive (data rests here forever)
```

**Never work on spinners.** All braiding must happen on NVMe. The convergence drain pattern treats NVMe as an ephemeral workspace, not permanent storage.

### Primal Topology

The provenance chain has a strict dependency order that was discovered through failures:

```
nestGate (CAS)  ──┐
loamSpine (spine) ─┤── bearDog (crypto) must be live for commits
rhizoCrypt (DAG) ──┘
sweetGrass (attribution) ← riboCipher prefix required
       ↑
   biomeOS (routing) ← FD leak blocks all forwarding
       ↑
   songBird (discovery) ← mesh + capability.resolve works
       ↑
   swarmVine (gossip) ← vine-bat pre-accept via skunkBat
```

### Interaction Topology

```
Python orchestration          → JELLY (should be biomeOS graphs)
Direct primal UDS calls       → WORKS (0.2ms)
biomeOS capability.call       → BROKEN (FD leak)
biomeOS capability.resolve    → WORKS (7ms, correct socket mapping)
biomeOS health.liveness       → WORKS (0.4ms)
songBird ipc.register         → WORKS (persistent via systemd)
songBird capability.resolve   → WORKS (via mesh)
swarmVine gossip.inject       → WORKS (vine-bat validated)
convergence_drain.py          → WORKS (timer, prov-chain recorded)
```

---

## 7. What Works Right Now

1. **Data lands → braids inline** (alphafold_full_sync.sh, daily timer)
2. **CAS dedup** (content.exists check before content.put)
3. **DAG events** (rhizoCrypt dag.event.append_batch, 500/batch)
4. **Convergence drain** (warm→cold every 30 min, prov-chain recorded)
5. **Vine-bat gossip** (8-check pre-accept, cross-gate TCP :7800)
6. **Direct primal calls** (bypass biomeOS, 0.2ms)
7. **songBird mesh** (1 peer: ironGate, capability.resolve works)
8. **14/14 services** (full NUCLEUS)

## 8. What Doesn't Work

1. **biomeOS capability.call** (FD leak → timeout)
2. **Spine commit signatures** (bearDog has no sign surface)
3. **nestGate content.ingest** (doesn't exist — Python walks+hashes instead)
4. **Fleet depot deploy** (songBird, skunkBat, swarmVine, bearDog stale/missing)
5. **southGate mesh** (not discoverable)

---

## 9. Recommended Next Steps

### For biomeOS team
- Fix FD leak in auto-discovery loop (close sockets after health probes)
- Build provenance graph templates (CAS→DAG→Spine→Braid single dispatch)

### For nestGate team
- Ship `content.ingest(directory)` — Rust-native directory walk + BLAKE3 + CAS
- Ship `content.stat(hash)` — metadata without fetching content
- Consider tier-aware operations (stage to NVMe, drain to cold)

### For bearDog team
- Implement Ed25519 sign/verify surface
- Fix socket naming to use family-id convention
- Push updated binary to golgi depot

### For sporeGate overwatch
- Rebuild songBird, skunkBat, swarmVine, bearDog for depot
- Regenerate BLAKE3SUMS

### For all gates
- Apply `LimitNOFILE=65536` to biomeOS + songBird systemd units
- Create bearDog socket symlink until naming fix ships

---

*westGate: 989K+ files braided, 14/14 services, vine-bat operational. The provenance trio works — the glue around it needs to evolve into primal-native capability. Data is sovereign; the plumbing is still Python.*
