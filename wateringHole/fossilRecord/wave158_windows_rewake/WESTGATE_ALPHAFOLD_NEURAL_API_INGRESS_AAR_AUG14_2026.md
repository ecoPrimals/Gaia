# After-Action Report: AlphaFold Full Neural API Ingress Pipeline

**Gate:** westGate (Tower 155f)  
**Date:** 2026-08-14  
**Wave:** 157k+ (solo enabler continuation)  
**Scope:** Replace deprecated bash/python AlphaFold ingestion scripts with primal-native Neural API pipeline

---

## Executive Summary

Built and validated `membrane alphafold.ingest` — a three-phase ingestion pipeline for the complete AlphaFold DB (~23 TB, 246M structures) through biomeOS Neural API, braiding at ingress. This replaces `alphafold_full_sync.sh` + `native_braid.py` with Rust-native primal composition.

**Result:** Phase A fully validated (99 files, 14.76 GiB), Phase B actively running (10M+ files streaming from ZFS), Phase C validated (content.fetch → CAS proven at EBI endpoint). The pipeline is the first large-scale exercise of the Nest Atomic signal graph lifecycle at production scale.

---

## What Was Built

### `membrane alphafold.ingest` (new command)

File: `gardens/cellMembrane/crates/membrane-shadow/src/dispatch/alphafold_dispatch.rs` (~580 lines)

```
membrane alphafold.ingest [--phase a|b|c|all] [--batch-size 500] [--rate-limit-mbps 200]
                          [--checkpoint-interval 50000] [--dry-run] [--resume]
                          [--concurrency 4] [--skip-braided]
membrane alphafold.status
membrane alphafold.manifest
```

Three-phase orchestration:

| Phase | Source | Files | Size | Method |
|-------|--------|-------|------|--------|
| A | Proteome tars (on-disk) | 99 | 14.76 GiB | `content.ingest` per version dir via direct nestGate UDS |
| B | Expanded structures (on-disk) | ~11M | ~1.5 TB | Streaming walk: `content.put` per CIF file via direct nestGate UDS |
| C | EBI remote download | ~235M | ~20 TB | `content.fetch` per accession via direct nestGate UDS |

Each phase follows the nest signal graph lifecycle:
1. `declare_dataset` → DAG session + spine + intent braid
2. Per-file acquisition → CAS store + DAG event batch
3. Checkpoint braids every N files
4. `complete_dataset` → dehydrate → commit → sign → final braid

### Translation Gap Fixes

- Added `content.fetch` to biomeOS capability registry (was missing — only available via direct nestGate socket)
- Added `crypto.sign` as alias for `crypto.sign_ed25519` (signal graphs use the short form)
- Fixed `path` → `directory` param in `content.ingest` calls (nestGate expects `directory`)
- Fixed `data_braid_ingress.toml` graph to match
- Fixed `spine.create` to include required `owner` field
- Fixed DAG `event.append_batch` format: rhizoCrypt expects `event_type` as struct variant `{"DataCreate": {"schema": null}}`, not a string

### Direct-to-Primal UDS Pattern

The default JSON-RPC timeout (3s) is insufficient for operations that take minutes (hashing 10M files, fetching multi-GB downloads). Rather than modifying the global timeout, `alphafold_dispatch` calls nestGate directly on its UDS socket with configurable timeouts:

- riboCipher `[0xEC, 0x01]` prefix on all direct UDS connections
- 600s timeout for `content.ingest` (directory walks)
- 30s timeout for `content.put` (individual files)
- 600s timeout for `content.fetch` (remote downloads)

This is the first use of the "direct-to-primal bypass" pattern, where a membrane command calls a primal socket directly instead of routing through biomeOS Neural API. The pattern is valid when the caller knows exactly which primal to target and needs non-default timeout behavior.

---

## Validation Results

### Phase A — Proteome Tars (Complete)

```json
{
  "files": 99,
  "bytes": 15850665383,
  "session_id": "01a00099-701d-7e80-96b8-f911968d22b0",
  "spine_id": "019ff3a4-2c8b-7173-9067-da2924735516",
  "directories": ["v1 (1 file)", "v2 (7 files)", "v3 (8 files)",
                   "v4 (9 files)", "v5 (7 files)", "v6 (7 files)"]
}
```

All 6 version directories ingested in ~10 seconds. Full provenance pipeline: CAS → DAG session → spine → braid.

### Phase B — Expanded Structures (Running)

- A0 bucket: **10,024,527 files** (the outlier — most UniProt accessions start with A0A)
- Remaining 227 buckets: ~5K-6K files each
- Streaming at ~1K files/sec on ZFS spinners
- 39.5 GB read after ~30 minutes of active processing
- ETA for A0: ~2-3 hours; remaining buckets: ~30 minutes total

Key discovery: `content.ingest` on a 10M-file directory is impractical (nestGate walks + hashes + stores in a single RPC call). The streaming approach — local `readdir` → `read` → base64 → `content.put` per file — gives progress visibility, checkpointing, and avoids timeout issues.

### Phase C — EBI Remote Fetch (Validated)

- `content.fetch` with v6 URLs works: 261 KB CIF fetched in 386ms, BLAKE3 hashed, stored in CAS
- 246,689,515 total accessions; 11,004,802 already fetched (4.5%)
- 235,452,366 remaining to download (~20 TB)
- At 200 Mbps rate limit: ~9 days continuous
- Initial v4 URL attempt returned 404 — fixed to v6 (current AlphaFold DB version)
- Should run sequentially after Phase B (shared state file)

---

## What Worked

1. **Direct-to-primal UDS calls** with extended timeouts bypass the 3s Neural API default without changing global behavior
2. **Streaming walk** pattern handles directories with millions of files where monolithic `content.ingest` fails
3. **riboCipher prefix** (`[0xEC, 0x01]`) is mandatory on all direct primal UDS connections — without it, nestGate silently hangs
4. **content.fetch** is exactly right for remote acquisition: URL → BLAKE3 → CAS in one atomic step, with rate limiting and resume
5. **Checkpoint braids** via `braid.create` with status="checkpoint" enable resumable multi-day ingestion
6. **State file** (`.alphafold_ingress_state.json`) enables `--resume` across process restarts

## What Needs Evolution

1. **DAG batch format**: `event.append_batch` requires struct-variant `event_type` (e.g., `{"DataCreate": {"schema": null}}`). The field naming is non-obvious. Consider adding a convenience `dag.event.append_simple` that accepts a string event type.

2. **Concurrent phase execution**: Phases B and C share a state file — running concurrently corrupts state. Solutions: per-phase state files, file locking, or explicit sequential orchestration.

3. **A0 outlier**: 10M files in one prefix bucket dominates Phase B runtime. Consider sub-bucketing (A0A, A0B, ...) for parallelism within a bucket.

4. **Manifest parsing at scale**: Loading 246M accessions + filtering against 11M already-fetched creates ~4 GB of in-memory references. Consider streaming the CSV with a bloom filter for the already-fetched set.

5. **Global JSON-RPC timeout**: The 3s default (`DEFAULT_JSONRPC_TIMEOUT_SECS`) is appropriate for interactive commands but blocks pipeline operations. Consider a per-call timeout parameter on `NeuralBridge::capability_call`.

6. **Tracing output**: `info!()` logs from the alphafold dispatch don't appear in terminal output despite `RUST_LOG=info`. May be a tracing subscriber buffering issue.

---

## Files Changed

### cellMembrane (gardens/cellMembrane/)
- `crates/membrane-shadow/src/dispatch/alphafold_dispatch.rs` — **NEW**: full 3-phase orchestrator
- `crates/membrane-shadow/src/dispatch/mod.rs` — route `alphafold.*` commands
- `crates/membrane-shadow/src/dispatch/content_dispatch.rs` — fix `path`→`directory`, field name alignment, add `owner` to spine.create
- `crates/membrane-shadow/src/main.rs` — help text for `alphafold.*` commands

### biomeOS (primals/biomeOS/)
- `config/capability_registry.toml` — add `content.fetch`, `crypto.sign` translations
- `graphs/data_braid_ingress.toml` — fix `path`→`directory` param

---

## Patterns for Upstream Teams

### Direct-to-Primal Bypass (new pattern)

When a membrane command needs non-default timeout behavior for a specific primal, it can call the primal's UDS socket directly instead of routing through biomeOS Neural API. Requirements:
- Send riboCipher `[0xEC, 0x01]` prefix before JSON-RPC payload
- Use the primal's canonical socket path (e.g., `nestgate-{family}.sock`)
- Set timeout appropriate for the operation

### Streaming Walk for Large Directories

For directories with >100K files, prefer local `readdir` + individual `content.put` over monolithic `content.ingest`. This gives:
- Per-file progress tracking
- Checkpointing within a directory
- No UDS timeout issues
- Memory-bounded processing

### Checkpoint Braids

Create intermediate `braid.create` calls with `status: "checkpoint"` during long-running ingestion. These serve as resume points and audit trail for multi-day operations.

---

## Recommendations

| Team | Action |
|------|--------|
| **rhizoCrypt** | Document `event_type` struct-variant format in API docs; consider `dag.event.append_simple` convenience method |
| **nestGate** | Consider streaming `content.ingest_stream` for directories >1M files; add `content.fetch` to primal.announce |
| **biomeOS** | Add per-call timeout to Neural API capability routing; fix tracing propagation for backgrounded commands |
| **ironGate** | AlphaFold is the first CAS-at-scale dataset — coordinate NFT braid layer for compute results on ingested structures |
| **All gates** | Phase C will generate sustained 200 Mbps download traffic for ~9 days when activated — coordinate bandwidth |
