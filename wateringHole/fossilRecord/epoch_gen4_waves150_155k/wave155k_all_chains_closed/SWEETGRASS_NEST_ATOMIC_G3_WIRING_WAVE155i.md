# sweetGrass — Nest Atomic G3 Wiring Handoff — Wave 155i

**Date**: Jul 29, 2026 | **Wave**: 155i | **From**: eastGate overwatch
**Team**: sweetGrass (Provenance Trio) | **Gate**: westGate
**Priority**: P0 for Nest Atomic
**Depends on**: loamSpine registry drift FIXED (commit `d79231a`)

---

## OBJECTIVE

Close the Provenance Trio triangle. Currently:

| IPC Path | Status |
|----------|--------|
| rhizoCrypt → loamSpine | **WIRED** (`PermanentStorageClient`) |
| rhizoCrypt → sweetGrass | **WIRED** (`ProvenanceNotifier`) |
| sweetGrass → loamSpine | **NOT WIRED** — this is the gap |

`braid.commit` packages the payload for loamSpine wire format but never
sends it. `anchoring.verify` does local witness check only (see comment
at `anchoring.rs:104`: "Full loamSpine ledger verification will be wired
in v0.8.0 via outbound trio clients").

---

## WORK ITEMS

### 1. Create `LedgerClient` module

New file: `crates/sweet-grass-service/src/ledger_client.rs`

JSON-RPC 2.0 client over UDS (Unix) / TCP (Windows) to loamSpine.

```rust
pub struct LedgerClient {
    socket_path: PathBuf,  // or TCP addr on Windows
}
```

Methods:
- `commit_braid(payload: serde_json::Value) -> Result<LedgerCommitResponse>`
  Calls loamSpine `braid.commit` JSON-RPC method
- `verify_certificate(cert_id: &str) -> Result<VerifyResponse>`
  Calls loamSpine `certificate.verify` JSON-RPC method

Socket resolution chain:
1. `LOAMSPINE_SOCKET` env var (explicit override)
2. `{BIOMEOS_SOCKET_DIR}/loamspine-{FAMILY_ID}.sock` (family-scoped)
3. `{BIOMEOS_SOCKET_DIR}/loamspine.sock` (standalone)

Requirements:
- `Clone + Send + Sync`
- Uses `tokio::net::UnixStream` (already in deps)
- JSON-RPC 2.0 wire format: `{"jsonrpc":"2.0","method":"...","params":...,"id":N}`
- Connection failures return `Err`, never panic
- No new crate dependencies

### 2. Add `ledger_client` to `AppState`

In `crates/sweet-grass-service/src/state.rs`:

```rust
pub ledger_client: Option<Arc<LedgerClient>>,
```

- Add `ledger_client: None` to all constructors (`new_memory`, `with_store`, `with_self_knowledge`)
- Add `with_ledger_client(mut self, client: LedgerClient) -> Self` builder

### 3. Wire in bootstrap Phase 4c

In `crates/sweet-grass-service/src/bootstrap.rs`:

After Phase 4b (crypto delegate), add Phase 4c:

```rust
// Phase 4c: Resolve loamSpine ledger client for Provenance Trio
app_state = resolve_ledger_client(app_state);
```

`resolve_ledger_client` should:
- Read `LOAMSPINE_SOCKET`, fall back to socket_dir patterns
- If path exists, create `LedgerClient::new(path)`, attach to AppState
- Log whether ledger client resolved or not
- Graceful: if no loamSpine found, continue without (standalone mode)

### 4. Wire `braid.commit` handler outbound

In `crates/sweet-grass-service/src/handlers/jsonrpc/braid.rs`:

After the existing payload packaging (lines 292-335 of `handle_braid_commit`):

```rust
// If loamSpine is available, forward the commit
if let Some(ref client) = state.ledger_client {
    match client.commit_braid(payload.clone()).await {
        Ok(commit_ref) => {
            response["committed"] = true.into();
            response["ledger_commit"] = serde_json::to_value(&commit_ref)?;
        }
        Err(e) => {
            tracing::warn!("loamSpine commit failed, braid is local-only: {e}");
        }
    }
}
```

On success, also populate `LedgerCommitRef` and `CertificateRef` on the
braid via store update (spine_id, entry_hash, index from response).

### 5. Wire `anchoring.verify` handler ledger proof

In `crates/sweet-grass-service/src/handlers/jsonrpc/anchoring.rs`:

After the local witness check (line 123):

```rust
// Cross-primal ledger verification via loamSpine
if let Some(ref client) = state.ledger_client {
    match client.verify_certificate(braid_id_str).await {
        Ok(result) => {
            response["ledger_verified"] = result.valid.into();
            response["verification_status"] = if result.valid {
                "ledger_verified"
            } else {
                verification_status
            }.into();
        }
        Err(e) => {
            tracing::debug!("loamSpine verify unavailable: {e}");
        }
    }
}
```

Update the doc comment at line 104 — replace "will be wired in v0.8.0"
with "loamSpine ledger verification wired via LedgerClient".

---

## EXISTING CODE REFERENCE

The `AnchorManager` and `TarpcAnchoringClient` in
`crates/sweet-grass-integration/src/anchor/mod.rs` provide tarpc-based
anchoring. The `LedgerClient` above uses simpler JSON-RPC 2.0 over UDS
(consistent with the rest of the service handler layer). The tarpc
integration layer can be used for higher-throughput scenarios later.

`CertificateRef` at `crates/sweet-grass-core/src/braid/types.rs:315`
already has all required fields including `cross_gate()` constructor.

The niche at `crates/sweet-grass-core/src/niche.rs` already lists
`spine.create` and `commit.session` in `CONSUMED_CAPABILITIES`.

---

## VALIDATION

After wiring:

```bash
cargo check --workspace --all-features
cargo clippy --all-features --all-targets -- -D warnings
cargo test --all-features
```

Then on westGate with loamSpine running:
1. `braid.create` → `braid.commit` → verify response contains `"committed": true`
2. `anchoring.verify` → verify response contains `"ledger_verified": true`
3. Without loamSpine running: verify graceful degradation (local-only, no crash)

---

## UPSTREAM STATUS (for sweetGrass team awareness)

| Primal | What Shipped | Impact |
|--------|-------------|--------|
| **loamSpine** | `certificate.verify/lifecycle/history` now in registry + niche (commit `d79231a`) | `LedgerClient::verify_certificate` can now be discovered via biomeOS |
| **biomeOS** | `nest.ingest_dataset` signal graph (commit `e843b9ca`) | Bulk ingestion pipeline defined — sweetGrass is step 5 |
| **rhizoCrypt** | DAG → loamSpine wired via `PermanentStorageClient` | sweetGrass receives provenance notifications that include DAG context |

---

*This handoff targets sweetGrass v0.8.0. When complete, the full Provenance
Trio triangle closes and Nest Atomic can track provenance end-to-end:
content → DAG → certificate → attribution braid.*
