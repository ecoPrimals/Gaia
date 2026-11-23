# CAC Handoff: rhizoCrypt — SessionTreeHash Primitive

**Date**: Jul 15, 2026 | **Wave**: 140a | **From**: eastGate overwatch
**Pattern**: Content-Addressed Convergence (Newton-Leibniz)
**Reference**: `whitePaper/gen5/foundations/CONTENT_ADDRESSED_CONVERGENCE.md`

---

## Extension: SessionTreeHash

### Context

rhizoCrypt already embodies the two-tier identity model that the CAC pattern
formalizes:

- **VertexId** = `BLAKE3(CBOR{parents, timestamp, agent, event_type, payload, metadata})`
  — temporal identity (who/when/how). Like a git commit SHA.
- **PayloadRef** = `BLAKE3(payload bytes)`
  — content identity (what). Like a git tree hash.

`dag.federate` uses VertexId to skip duplicates — if the exact same event
(same timestamp, same agent, same parents) is imported, it's deduplicated.
But it does NOT recognize when two sessions arrive at the same semantic state
via different event paths.

### The Gap

Two sessions can reach identical frontier content through different event
histories (different agents, different timestamps, different intermediate
vertices). Currently there is no way to detect this convergence — the
sessions look "divergent" because their vertex histories differ.

This is the Newton-Leibniz problem at the DAG layer: Newton and Leibniz
independently discovered the same calculus (same frontier payload) via
different paths (different vertex histories). The truth converged; only
the discovery metadata differed.

### Specification

Add a `session_content_hash()` method to `rhizocrypt/branch_ops.rs` or a
new `convergence.rs` module:

```rust
use crate::types::{ContentHash, PayloadRef, SessionId};
use crate::store::DagStore;
use crate::session::Session;

/// Content-addressed session state — the Newton-Leibniz hash.
///
/// Strips temporal metadata (timestamps, agents, parent links) from
/// frontier vertices, producing a hash that is identical when two
/// sessions reach the same semantic state via different event paths.
///
/// Analogous to git's `HEAD^{tree}` — identical content trees produce
/// identical hashes regardless of commit history.
pub async fn session_content_hash(
    session: &Session,
    store: &dyn DagStore,
) -> Result<ContentHash> {
    let mut frontier_payloads: Vec<PayloadRef> = Vec::new();

    for vid in &session.frontier {
        if let Some(vertex) = store.get_vertex(session.id, *vid).await? {
            if let Some(payload_ref) = &vertex.payload {
                frontier_payloads.push(payload_ref.clone());
            }
        }
    }

    // Canonical ordering — ensures identical sets produce identical hashes
    // regardless of iteration order
    frontier_payloads.sort_by(|a, b| a.hash.cmp(&b.hash));

    // BLAKE3 over CBOR-encoded sorted payload refs
    let cbor_bytes = ciborium_encode(&frontier_payloads)?;
    Ok(ContentHash::from_bytes(&cbor_bytes))
}
```

### Usage in dag.federate

Extend `dag.federate` to optionally compare session content hashes before
doing vertex-by-vertex import:

```rust
pub async fn federate(
    &self,
    session_id: SessionId,
    remote_session: &Session,
    remote_store: &dyn DagStore,
) -> Result<FederateResult> {
    // NEW: Check for Newton-Leibniz convergence first
    let local_hash = session_content_hash(&local_session, &self.dag_store).await?;
    let remote_hash = session_content_hash(remote_session, remote_store).await?;

    if local_hash == remote_hash {
        return Ok(FederateResult {
            converged: true,  // Content-identical despite different histories
            imported: 0,
            skipped: 0,
        });
    }

    // Existing vertex-by-vertex federation...
}
```

### RPC Surface

Add to `rhizo-crypt-rpc/src/service.rs`:

```rust
/// dag.content_hash — returns the Newton-Leibniz content hash of a session.
/// Two sessions with identical frontier payloads return the same hash
/// regardless of event history.
async fn dag_content_hash(&self, session_id: SessionId) -> Result<String> {
    let session = self.get_session(session_id)?;
    let hash = session_content_hash(&session, &*self.dag_store).await?;
    Ok(hash.to_hex())
}
```

### Properties

The SessionTreeHash satisfies the CAC equivalence relation:

1. **Reflexive**: `session_content_hash(S) == session_content_hash(S)`
2. **Symmetric**: If S1 converges with S2, then S2 converges with S1
3. **Transitive**: Guaranteed by deterministic BLAKE3 + canonical CBOR
4. **History-independent**: Only frontier payloads matter, not event path
5. **Provenance-preserving**: The vertex DAG still records full history;
   convergence detection is an overlay, not a replacement

### Relationship to Existing Primitives

| Primitive | Layer | What it hashes | Temporal? |
|-----------|-------|---------------|-----------|
| VertexId | Event | Full canonical vertex (time+agent+parents+payload) | YES |
| PayloadRef | Blob | Raw payload bytes | NO |
| MerkleRoot | Session snapshot | Ordered vertex IDs | YES (vertex order matters) |
| **SessionTreeHash** | Session state | Sorted frontier PayloadRefs | **NO** |

SessionTreeHash fills the gap: a session-level content identity that is
independent of event history, analogous to how `HEAD^{tree}` gives git
a content identity independent of commit history.

### Test Cases

```rust
#[tokio::test]
async fn newton_leibniz_convergence() {
    let store = InMemoryDagStore::new();
    let session_a = create_session(&store).await;
    let session_b = create_session(&store).await;

    // Different agents, different timestamps, same payload
    let payload = PayloadRef::from_bytes(b"calculus");
    append_vertex(&store, session_a, "newton", "1666", &payload).await;
    append_vertex(&store, session_b, "leibniz", "1676", &payload).await;

    let hash_a = session_content_hash(&get_session(&store, session_a), &store).await.unwrap();
    let hash_b = session_content_hash(&get_session(&store, session_b), &store).await.unwrap();

    assert_eq!(hash_a, hash_b, "Same content via different paths must converge");
}

#[tokio::test]
async fn different_content_diverges() {
    let store = InMemoryDagStore::new();
    let session_a = create_session(&store).await;
    let session_b = create_session(&store).await;

    append_vertex(&store, session_a, "newton", "1666", &PayloadRef::from_bytes(b"fluxions")).await;
    append_vertex(&store, session_b, "leibniz", "1676", &PayloadRef::from_bytes(b"differentials")).await;

    let hash_a = session_content_hash(&get_session(&store, session_a), &store).await.unwrap();
    let hash_b = session_content_hash(&get_session(&store, session_b), &store).await.unwrap();

    assert_ne!(hash_a, hash_b, "Different content must diverge");
}
```

---

*SessionTreeHash completes the fractal: git has tree hashes, depot has BLAKE3
checksums, cascade has TreeParity detection, and now rhizoCrypt has
SessionTreeHash. The same principle — content identity supersedes temporal
identity — applied at every layer of the sovereign mesh.*
