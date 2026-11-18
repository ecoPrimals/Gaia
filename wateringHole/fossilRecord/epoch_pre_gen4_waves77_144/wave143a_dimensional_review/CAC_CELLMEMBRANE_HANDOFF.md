# CAC Handoff: cellMembrane — Content-Addressed Convergence Fixes

**Date**: Jul 15, 2026 | **Wave**: 140a | **From**: eastGate overwatch
**Pattern**: Content-Addressed Convergence (Newton-Leibniz)
**Reference**: `whitePaper/gen5/foundations/CONTENT_ADDRESSED_CONVERGENCE.md`

---

## Fix 1: TreeParity for Heads Auto-Publish Divergence (P1)

### Problem

`heads/*.toml` files are auto-published by multiple gates (eastGate cascade,
golgiBody auto-publish). Each publication creates a new commit in wateringHole.
When two gates publish nearly simultaneously, commits diverge even though
content is often identical (only timestamps differ). This triggers DIVERGE
flags and merge conflicts that require manual resolution every cascade.

### Root Cause

In `temporal/sync_engine.rs` and `temporal/mod.rs`, the agentic policy path
for wateringHole reaches the divergence handler BEFORE checking tree parity.
The `detect_tree_parity()` function exists and works for other repos, but
wateringHole's `divergence_policy = "agentic"` dispatches to the agentic
resolver which does not call tree-parity detection first.

### Fix

In `crates/membrane-shadow/src/temporal/mod.rs`:

Before dispatching to the agentic resolver for a DIVERGE classification,
check tree parity first. If trees match, the divergence is Newton-Leibniz
equivalent — resolve via TreeParity flow, not agentic flag.

```rust
// In the diverge classification path:
// BEFORE:
SyncAction::Diverge { positions } => {
    // dispatches to agentic resolver → flags for human review
}

// AFTER:
SyncAction::Diverge { positions } => {
    // Check tree parity FIRST — content identity supersedes temporal
    if let Some((leader, followers)) = detect_tree_parity(local_path, &positions).await {
        // Newton-Leibniz: same content, different history → auto-resolve
        return sync_tree_parity(local_path, repo_path, &leader, &followers, push_target).await;
    }
    // Only reach agentic resolver for REAL content divergence
    // (existing code)
}
```

In `crates/membrane-shadow/src/temporal/sync_engine.rs`:

The `sync_converge` function's match on `SyncAction::TreeParity` already
handles the resolution correctly (reset to leader, push followers). Ensure
this path is reachable from the diverge handler above.

### Test

After the fix, this sequence should NOT produce a DIVERGE flag:
1. eastGate publishes `heads/eastGate.toml` and pushes to forgejo
2. golgiBody publishes `heads/golgiBody.toml` and pushes to forgejo
3. eastGate runs `membrane temporal.cascade`
4. If only `heads/*.toml` differ between local and forgejo → TreeParity → auto-resolve

---

## Fix 2: Content-Hash Impulse Deduplication (P2)

### Problem

Diverge impulses can be created independently by multiple gates detecting
the same event. For example, both eastGate and sporeGate detect wateringHole
divergence and each create `DIVERGE: wateringHole` impulses with the same
semantic content but different timestamps.

### Root Cause

In `crates/membrane-shadow/src/impulse/sync.rs`, `post_sync_diverge()`
creates a new impulse file unconditionally. No check for existing
content-equivalent impulses.

### Fix

Before creating an impulse, compute a content hash of the semantic fields
(repo path + diverge type + remote positions — excluding temporal metadata)
and check active impulses for a match.

In `crates/membrane-shadow/src/impulse/sync.rs`:

```rust
pub async fn post_sync_diverge(
    workspace_root: &Path,
    args: &SyncDivergeArgs,
) -> Result<SyncImpulseFile> {
    // --- NEW: Content-hash deduplication ---
    let content_key = format!(
        "diverge:{}:{}",
        args.repo_path,
        classify_diverge_type(&args.positions)
    );
    let content_hash = blake3::hash(content_key.as_bytes()).to_hex().to_string();

    let active = active_dir(workspace_root);
    if active.exists() {
        for entry in std::fs::read_dir(&active).into_iter().flatten().flatten() {
            let name = entry.file_name().to_string_lossy().to_string();
            if name.contains("diverge-") && name.contains(
                args.repo_path.rsplit('/').next().unwrap_or(&args.repo_path)
            ) {
                tracing::debug!(
                    existing = %name,
                    "skipping duplicate diverge impulse (CAC dedup)"
                );
                // Return a sentinel indicating skip, or read the existing impulse
                // to return it. The key point: don't create a second impulse.
                return Err(ShadowError::Config(format!(
                    "CAC dedup: content-equivalent impulse already exists: {name}"
                )));
            }
        }
    }
    // --- END dedup ---

    // ... existing impulse creation code ...
}
```

A more sophisticated version would parse each existing impulse and compare
the `payload.repo` + `payload.diverge_type` fields instead of relying on
filename patterns. But the filename check is sufficient for the common case
and avoids TOML parsing overhead.

### Alternative: Broader dedup

For non-sync impulses (FRAGO, etc.), a general dedup model would hash
`content.subject + content.body` (excluding `meta.created` and `from.gate`).
This is a future evolution — the sync impulse dedup above addresses the
immediate problem.

---

## Relationship to CAC Pattern

Both fixes apply the same principle: **content identity supersedes temporal
identity for convergence**.

| Fix | Temporal Identity | Content Identity | Resolution |
|-----|-------------------|------------------|------------|
| TreeParity for heads | Commit SHA (from auto-publish) | Tree hash of wateringHole | Auto-resolve if trees match |
| Impulse dedup | Impulse creation timestamp + gate | repo + diverge_type hash | Skip if content-equivalent exists |

See `whitePaper/gen5/foundations/CONTENT_ADDRESSED_CONVERGENCE.md` for the
full pattern specification.
