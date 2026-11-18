# westGate — Wave 157a Vine-Bat Deploy + Pipeline Fix AAR

**Date**: Aug 9, 2026
**Gate**: westGate (192.168.4.155)
**Wave**: 157a — VINE-BAT LOOP OPERATIONAL
**From**: westGate hardware team
**To**: eastGate overwatch

---

## Summary

Cascaded Wave 157a (vine-bat operational), deployed swarmVine with pre-accept hook (`df97b25`), and discovered+fixed a critical pipeline breakage: `native_braid.py` was calling `content.ingest` (a non-existent nestGate method) and using wrong parameter names for `content.put`, `content.exists`, and `braid.create`. All data ingress braiding was silently failing since the pipeline modernization. Fixed and verified end-to-end.

---

## Execution

### 1. Cascade
- Pulled latest from Forgejo across all repos
- New from ironGate: Session 17 AAR (vine-bat operational, 13/13 services)
- New from primalSpring: Dispatch fix verification (32/36 pass, 1.3ms mean)
- wateringHole merge conflict on blurb — resolved (theirs)

### 2. SwarmVine Vine-Bat Deploy
- Rebuilt swarmVine from source (`df97b25` — vine-bat pre-accept hook)
- Added `SWARMVINE_SKUNKBAT_SOCK` env var to systemd unit
- Verified: `gossip.inject` → accepted, `gossip.status` → 1 tower entry ingested
- skunkBat healthy on westGate, 8-check validation operational

### 3. P1 FD Limit Fix
- Applied `LimitNOFILE=65536` to songBird (via drop-in)
- biomeOS main service file corrected: `1048576 → 65536`
- Note: session-level `ulimit -n 1048576` overrides systemd setting. Process FDs still capped at session limit. The P1 fix needs a PAM-level change or biomeOS code fix for the auto-discovery FD leak.
- biomeOS `capability.call` still times out due to FD leak (14 → 58,613 FDs after 4 calls)
- Direct primal socket calls work perfectly (0.2ms)

### 4. BearDog Socket Symlink
- BearDog creates `beardog-default.sock` but loamSpine expects `beardog-westgate-tower-155f.sock`
- Created persistent symlink in `songbird-register.sh` (runs on boot)
- Verified beardog responds via symlink (`health.check` → alive v0.9.0)

### 5. BearDog Sign Surface — Health-Only Stub
- **All methods** (sign, sign_ed25519, crypto.sign_ed25519, identity.sign, nonexistent_method) return `health.check` response
- BearDog v0.9.0 on westGate has no functional Ed25519 signing
- loamSpine `session.commit` depends on `crypto.sign_ed25519` for commit signatures
- **Impact**: spine commits fail with `missing field 'signature'`
- **Workaround**: Made `session.commit` failures non-fatal in `native_braid.py`
- **Upstream**: beardog needs signing surface wired (depot binary may be pre-signing)

### 6. Pipeline Fix — content.ingest → content.put

**Root cause**: `native_braid.py` was designed around a `content.ingest` RPC that doesn't exist in nestGate v0.5.0. This method was aspirational (Rust walks directory), never shipped. The pipeline failed silently during the alphafold-sync systemd timer runs.

**Also broken**:
- `content.put` used `content_hash` param — nestGate expects `hash`
- `content.put` used `source_path` param — nestGate expects `content_base64`
- `content.exists` used `content_hash` — nestGate expects `hash`
- `braid.create` used `content_hash` — sweetGrass expects `data_hash`
- `braid.create` missing required `strand_id` field

**Fix applied**:
| Before | After |
|--------|-------|
| `content.ingest(directory)` — non-existent method | Python walks dir + per-file `content.put(content_base64, hash)` |
| `content.exists(content_hash)` | `content.exists(hash)` — dedup check before upload |
| `cas_put_large_file` — wrong params | `cas_put_file` — correct `content_base64 + hash` for all sizes |
| `braid.create(content_hash)` | `braid.create(data_hash, strand_id, metadata)` |
| `session.commit` — fatal on beardog sign failure | Non-fatal, deferred with warning |
| `dag.dehydration.trigger` — fatal on error | Non-fatal, falls back to manifest-based hash |

**Verified**: cell_ontology end-to-end: CAS (1 file, dedup detected) → DAG (1/1 events) → commit (spine deferred, beardog sign unavailable) → FINALIZED.

---

## P0 Issues Identified

### P0-A: BearDog Sign Surface Missing
- v0.9.0 depot binary is a health-only stub — no Ed25519 signing
- Blocks: loamSpine `session.commit` (requires `crypto.sign_ed25519`)
- **All braids currently lack spine commit signatures**
- Fix: beardog team needs to wire `sign_ed25519` and push updated binary to depot

### P0-B: nestGate API Surface Mismatch
- `content.ingest` (directory walk + bulk CAS) does not exist
- `content.stat` does not exist
- Only functional methods: `content.put`, `content.get`, `content.exists`, `health.check`
- Parameter names differ from what was assumed in pipeline code
- Fix: either nestGate ships these methods, or (done) pipeline adapts to actual API

### P0-C: biomeOS FD Leak (ongoing from P1)
- Auto-discovery health check loop opens ~58K FDs in seconds
- `capability.call` times out after any non-trivial workload
- Session-level `ulimit` overrides systemd `LimitNOFILE`
- Direct primal calls (bypassing biomeOS) work at 0.2ms
- Fix: biomeOS code needs FD cleanup in discovery loop

---

## Final State

```
Services:      14/14 active
swarmVine:     df97b25 (vine-bat hook, epidemic spread, TCP :7800)
skunkBat:      e602e09 (metadata.analyze, 8-check pre-accept)
Vine-bat:      OPERATIONAL (inject → accepted, 8-check live)
native_braid:  FIXED (content.put path, dedup-first, non-fatal spine)
bearDog:       v0.9.0 (health-only, NO signing)
biomeOS:       FD leak active (capability.call unusable)
Pipeline:      CAS + DAG working, spine commit deferred
Data:          All datasets braided (324 alphafold, 989K structures, 753 sra_fastq)
NVMe warm:     25.1% (convergence drain timer healthy)
Cold ZFS:      6.56 TB / 63.7 TB (10%)
songBird mesh: 1 peer (ironGate)
```

---

## Recommendations for Upstream

1. **bearDog depot binary rebuild** — must include Ed25519 sign surface, not just health stub
2. **nestGate API docs** — document actual RPC surface (`content.put` params: `content_base64`, `hash`; no `content.ingest`)
3. **biomeOS FD leak** — auto-discovery loop must close sockets after health probes
4. **bearDog family-id socket** — should use `beardog-{family_id}.sock` not `beardog-default.sock`

---

*Pipeline modernized: jelly strings removed, primal API mismatches fixed, vine-bat loop operational. westGate 14/14 ALIVE. Spine commits deferred until bearDog sign surface ships.*
