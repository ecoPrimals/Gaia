# Nest Atomic + AlphaFold Provenance Ingestion — Wave 155i

**Date**: Jul 29, 2026 | **Wave**: 155i | **From**: eastGate overwatch
**Purpose**: Coordinate Nest Atomic stand-up on westGate and AlphaFold data
ingestion pipeline from northGate through full Provenance Trio backtracking.

---

## SUMMARY

Move from Tower Atomic (LIVE on 5+ gates) to Nest Atomic: content-addressed
storage with full provenance. First dataset target: ~1TB AlphaFold PDB/mmCIF
protein structure data currently on northGate, ingested into westGate's
nestGate CAS with rhizoCrypt DAG events, loamSpine certificates, and
sweetGrass attribution braids.

```
northGate (AlphaFold PDB/mmCIF)
    ↓ content.replicate.pull / USB staging
westGate nestGate CAS (content.put, BLAKE3)
    ↓ dehydration.trigger
rhizoCrypt (dag.session → dag.event)
    ↓ PermanentStorageClient
loamSpine (session.commit → certificate.mint)
    ↓ ProvenanceNotifier         ↑ braid.commit (G3 wiring)
sweetGrass (contribution.record → CertificateRef)
```

---

## WHAT'S ALREADY DONE (Wave 155h-i)

| Item | Status | Detail |
|------|--------|--------|
| loamSpine registry drift | **FIXED** | `certificate.verify/lifecycle/history` registered in capability_registry.toml + niche.rs. 1,285 tests pass. Commit `d79231a`. |
| biomeOS `nest.ingest_dataset` | **CREATED** | Signal graph: `dag.session.create` → `content.put` → `dag.event.append` → `dag.dehydration.trigger` → `contribution.record_session`. Commit `e843b9ca`. |
| rhizoCrypt → loamSpine IPC | Already wired | `PermanentStorageClient` |
| rhizoCrypt → sweetGrass IPC | Already wired | `ProvenanceNotifier` |
| sweetGrass `CertificateRef` type | Shipped (155d) | `id`, `issuing_gate`, `sealed`, `minting_authority`, `content_hash` |
| nestGate CAS + ZFS tier migration | Code ready | `migrate_dataset_to_tier`, dry-run, `SubstrateTiers` detection |
| nestGate `content.replicate.pull` | In capability registry | Cross-gate federation method exists |

---

## TEAM HANDOFFS

### 1. sweetGrass Team — Wire sweetGrass → loamSpine (G3 Convergence)

**Priority**: P0 for Nest Atomic
**Reference**: `SWEETGRASS_NEST_ATOMIC_G3_WIRING_WAVE155i.md` (companion handoff)

The Provenance Trio gap: `braid.commit` packages the braid payload for
loamSpine wire format but never actually calls loamSpine. `anchoring.verify`
does local witness check only — no ledger proof.

**What to wire** (v0.8.0 scope):

1. Create `LedgerClient` — JSON-RPC 2.0 over UDS to loamSpine socket.
   Methods: `commit_braid(payload) → LedgerCommitRef`, `verify_certificate(cert_id) → VerifyResult`.
   Socket discovery: `LOAMSPINE_SOCKET` → `{BIOMEOS_SOCKET_DIR}/loamspine-{FAMILY_ID}.sock`.

2. Add `ledger_client: Option<Arc<LedgerClient>>` to `AppState`.
   Wire in bootstrap Phase 4c after crypto delegate.

3. `braid.commit` handler: forward packaged payload to loamSpine when
   `ledger_client` is `Some`. Populate `LedgerCommitRef` + `CertificateRef`
   on the braid from the response.

4. `anchoring.verify` handler: call `ledger_client.verify_certificate()` for
   ledger proof. Update the v0.8.0 comment at `anchoring.rs:104`.

5. Graceful degradation: if loamSpine unavailable, braids stay local-only.

**Key files**:
- `crates/sweet-grass-service/src/bootstrap.rs` (Phase 4c)
- `crates/sweet-grass-service/src/state.rs` (new field)
- `crates/sweet-grass-service/src/handlers/jsonrpc/braid.rs` (commit handler)
- `crates/sweet-grass-service/src/handlers/jsonrpc/anchoring.rs` (verify handler)
- `crates/sweet-grass-integration/src/anchor/mod.rs` (existing client reference)

### 2. Gate Teams — Tower Health Validation

**Priority**: P1 (Tower must be stable before Nest Atomic)

| Gate | Action | Owner |
|------|--------|-------|
| **westGate** | Validate `tower.health` signal graph via biomeOS live dispatch. Confirm bearDog + songBird + nestGate responsive. | westGate team |
| **strandGate** | Same — `tower.health` + `tower.mesh_status` validation. Confirm Compute Trio healthy. | strandGate team |
| **northGate** | Assess Tower Atomic status. Deploy bearDog + songBird + nestGate if not running. northGate is on WG mesh (10.13.37.8) but Tower status unclear. Required for cross-gate AlphaFold federation. | northGate team / overwatch |

**biomeOS signal graph**: `tower_health.toml` (shipped Wave 155d).
Run: `biomeos dispatch tower.health --gate <gate_name>`

### 3. westGate Hardware Team — ZFS Pool

**Priority**: P1 (unblocks tiered storage for Nest Atomic CAS)

westGate has 5×14TB HDDs (raw, unformatted). nestGate's `tier_migration.rs`
needs a ZFS pool to profile CAS across storage tiers.

```bash
# On westGate — adjust device names after lsblk inspection
sudo zpool create nestpool raidz2 /dev/sdX /dev/sdY /dev/sdZ /dev/sdA /dev/sdB
sudo zfs create nestpool/cas
sudo zfs create nestpool/archive
sudo zfs set compression=lz4 nestpool/cas
sudo zfs set atime=off nestpool/cas
```

After pool creation, set `NESTGATE_ZFS_ALLOW_MUTATIONS=true` and validate
`nestgate tier-migrate --dry-run`.

### 4. Validation — E2E Nest Atomic Pipeline (after items 1-3)

Validation sequence on westGate:

1. `nest.store` signal graph with a small test PDB file
2. Verify BLAKE3 CAS dedup (store same file twice, confirm single entry)
3. Verify rhizoCrypt creates DAG session + events
4. Verify `dag.dehydration.trigger` commits to loamSpine
5. Verify sweetGrass receives provenance notification + `CertificateRef` populated
6. Verify `nest.verify` confirms integrity of stored content

### 5. AlphaFold Ingestion (after validation)

**Two paths depending on northGate Tower status**:

**Path A — Cross-gate federation** (preferred):
- northGate Tower running → `content.replicate.pull` from westGate
- Uses `nest.ingest_dataset` signal graph for bulk ingestion
- Full provenance from source gate through CAS → DAG → certificate → braid

**Path B — USB/network staging** (if northGate Tower not ready):
- Stage AlphaFold data on USB or rsync to westGate first
- Ingest locally via `nest.store` on westGate
- Provenance still traces (source metadata in `.meta.json` sidecar)
- Mark source as `"origin": "northGate", "transfer": "staged"`

**Dataset metadata**:
- Format: PDB / mmCIF
- Source: AlphaFold Protein Structure Database
- Size: ~1TB
- Origin gate: northGate (Windows, NVMe)
- Target: westGate nestGate CAS (BLAKE3)

---

## SEQUENCING

```
[DONE] loamSpine registry drift → certificate.verify discoverable
[DONE] biomeOS nest.ingest_dataset signal graph → pipeline defined
  ↓
[NOW]  sweetGrass G3 wiring → braid.commit forwards to loamSpine
[NOW]  Tower health validation → westGate + strandGate confirmed
[NOW]  westGate ZFS pool creation → tiered storage ready
  ↓
[NEXT] northGate Tower assessment → cross-gate federation possible
[NEXT] E2E validation → small PDB ingestion test
  ↓
[THEN] Bulk AlphaFold ingestion → ~1TB through Nest Atomic pipeline
```

---

## DEPENDENCIES

| Dependency | Status | Blocks |
|------------|--------|--------|
| Tower Atomic stable on westGate | LIVE | Nest Atomic |
| sweetGrass → loamSpine IPC | NOT WIRED | E2E provenance |
| loamSpine `certificate.verify` advertised | FIXED (155i) | `nest.verify` dispatch |
| `nest.ingest_dataset` signal graph | CREATED (155i) | Bulk ingestion |
| westGate ZFS pool | NOT PROVISIONED | Tiered CAS storage |
| northGate Tower | UNCLEAR | Cross-gate federation |

---

*Wave 155i. Nest Atomic pipeline wiring begins. G3 convergence target:
sweetGrass → loamSpine closes the Provenance Trio triangle. First data
target: ~1TB AlphaFold protein structures from northGate into westGate
CAS with full provenance backtracking.*
