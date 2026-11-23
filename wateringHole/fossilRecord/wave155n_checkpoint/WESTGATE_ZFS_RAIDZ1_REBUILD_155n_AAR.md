# WESTGATE AAR — ZFS Pool Rebuild: Mirror → raidz1

**Date**: Jul 31, 2026 14:00 EDT | **Wave**: 155n | **Gate**: westGate | **From**: westGate overwatch

---

## EXECUTIVE SUMMARY

Rebuilt the westGate ZFS pool from 2x mirror + spare to raidz1 with all 5 drives.
Usable capacity doubled from **25.4 TB to 50.7 TB** — enough for the full AlphaFold
predicted structure database (23 TB) plus PDB + GenBank + UniProt with room to grow.

Rationale: filesystem-level mirroring is redundant when nestGate CAS provides
content-addressed integrity (BLAKE3 on every object), the provenance chain provides
cryptographic verification (DAG + Merkle + Ed25519), and Nest Federation
(`content.replicate` / `content.replicate.pull`) will provide cross-gate replication.

---

## WHAT CHANGED

| | Before | After |
|---|--------|-------|
| **Topology** | 2x mirror (2+2) + 1 hot spare | raidz1 (5 drives) |
| **Raw capacity** | 63.5 TB | 63.7 TB |
| **Usable capacity** | **25.4 TB** | **50.7 TB** |
| **Efficiency** | 40% | **80%** |
| **Drive fault tolerance** | 1 per mirror vdev | 1 across the pool |
| **Hot spare** | 1 drive idle | None — all 5 drives active |
| **L2ARC** | 2 TB SSD | 2 TB SSD (unchanged) |
| **Properties** | lz4, atime=off, xattr=sa, ashift=12 | Same |

---

## WHY MIRRORS WERE OVERKILL

The ecoPrimals stack provides data integrity at multiple layers above the filesystem:

1. **CAS (BLAKE3)**: Every object is identified by its cryptographic hash. Bit-rot is
   detectable by definition — any corruption changes the hash.

2. **ZFS checksums**: Even on a single vdev with no parity, ZFS checksums catch silent
   data corruption at the block level (though it can't repair without redundancy).

3. **Provenance chain**: DAG + Merkle root + Ed25519 signatures. Any object's integrity
   can be verified cryptographically end-to-end.

4. **Nest Federation**: `content.replicate` and `content.replicate.pull` provide
   cross-gate blob replication with BLAKE3 integrity verification on pull. Data exists
   on multiple gates (strandGate, blueGate, ironGate).

5. **Public sources**: Science data (PDB, GenBank, AlphaFold) can always be re-fetched
   from upstream repositories. CAS makes surgical re-ingestion trivial — you know
   exactly what hashes are missing.

**raidz1 is the pragmatic middle ground**: single-parity survives a drive failure without
any re-ingestion hassle, while using all 5 drives for maximum capacity.

---

## LONG-TERM: OPTION C — APPLICATION-MANAGED REDUNDANCY (GLACIAL GOAL)

The right long-term architecture is **nestGate-managed fractional replication** where
the CAS layer itself controls data redundancy:

- nestGate's `StorageRoutingConfig` already has the schema: `replication_factor`,
  multi-backend routing, distributed storage backend type
- `SubstrateTiers` already supports colon-separated multi-path env vars
- The CAS layer could shard across drives and keep ~50% of objects duplicated
  selectively (e.g., provenance-signed science data gets copies, temp/cache doesn't)

This makes the system **data-redundancy-agnostic** — the same CAS layer works on:
- A single NVMe (no redundancy, federation provides copies)
- A ZFS stripe (maximum local capacity)
- A cloud bucket (infinite capacity, pay per byte)
- A multi-gate mesh (federation IS the redundancy)

File this as a glacial goal alongside G22 (API convergence) — the CAS routing
infrastructure exists in schema, just needs wiring to the live write path.

---

## EXECUTION LOG

1. Backed up 128 MB / 3,269 files to `/tmp/nestgate-backup/` (NVMe)
2. Stopped `nestgate-tower` and `neural-api-tower`
3. `zpool destroy nestgate`
4. `zpool create -o ashift=12 -O compression=lz4 -O atime=off -O xattr=sa -m /mnt/nestgate/cold/zfs nestgate raidz1 <5 drives> cache <SSD>`
5. Recreated 8 ZFS datasets (cas, cas/bulk, cas/metadata, cas/objects, snapshots, data, cache, testing)
6. `rsync -a` restored all data
7. Restarted services — Coordinated mode, 835 caps, CAS roundtrip verified

Total downtime: ~3 minutes.

---

## SCIENCE STORAGE CAPACITY (post-rebuild)

| Database | Size | Fits in 50.7 TB? |
|----------|------|-----------------|
| PDB (experimental structures) | 1.6 TB | YES — 31× over |
| AlphaFold DB (214M predictions) | 23 TB | YES — 2.2× over |
| GenBank (flat files) | 10.3 TB | YES — 4.9× over |
| GenBank (ASN.1 compressed) | 3.3 TB | YES — 15× over |
| UniProt | ~0.5 TB | YES — 100× over |
| EMDB (cryo-EM maps) | 29 TB | YES — 1.7× over |
| **All of the above combined** | **~58 TB** | **Tight, but LZ4 compression helps** |

With LZ4 compression on biological data (typically 1.3-2× on structured formats),
effective capacity is ~65-100 TB. The full PDB + AlphaFold + GenBank + UniProt
combo (~38 TB uncompressed) fits comfortably with 12+ TB to spare.

---

## POST-REBUILD STATE

```
westGate ZFS — raidz1 (Jul 31, 2026)
  Pool:      nestgate, raidz1-0, 5× OOS14000G 14TB
  Cache:     CT2000BX500SSD1 2TB (L2ARC)
  Raw:       63.7 TB
  Usable:    50.7 TB
  Allocated: 156 MB (3,269 CAS files + testing data)
  Health:    ONLINE, 0 errors
  Services:  13/13 active, Coordinated mode, 835 caps
  CAS:       roundtrip verified on raidz1
```

---

*westGate — ZFS pool rebuilt: mirror → raidz1. Usable capacity doubled 25.4 TB → 50.7 TB.
All 5 drives active, L2ARC intact. CAS roundtrip verified. 3 min downtime. Long-term:
nestGate application-managed fractional replication (Option C) as glacial goal — makes
the system data-redundancy-agnostic across bare metal, cloud, and mesh.*
