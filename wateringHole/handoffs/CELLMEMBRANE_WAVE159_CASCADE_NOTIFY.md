# sporeGate → cellMembrane Team — Wave 159 Tasking

**Date**: Sep 27, 2026 | **Wave**: 159 | **From**: sporeGate topology
**To**: cellMembrane parallel IDE
**Priority**: P1 — unlocks NanoWire Tier 2 (SSH retirement for `gate.pull` + `gate.check`)

---

## Context: What sporeGate Just Completed

1. **Cascade timers LIVE** — `membrane-cascade.timer` (15min) + `membrane-harvest-scheduler.timer` (10min) both active on sporeGate, syncing 15/17 repos autonomously
2. **dnsmasq LAN entries** completed — northGate `192.168.4.147`, southGate IP corrected to `.149`, WG aliases added
3. **sporePrint build hook hardened** — `chown` guard + narrow sudoers rule so root-owned artifacts never block Zola builds again
4. **Caddyfile VC synced to live** — detroit + gorilla vhosts, port fixes, all 20 vhosts converged
5. **OUTER_MEMBRANE_TOPOLOGY.md** current — routing table, GSC state, resolved issues all updated

---

## Task 1: `cascade.notify` Gossip Event (PRIMARY)

### What It Is

A swarmVine gossip event that fires when a gate completes a `temporal.cascade` sync. When gate A syncs a repo, it gossips `cascade.notify` to all mesh peers. Peers that are stale on that repo can then pull autonomously — no SSH dispatch needed.

### Why It Matters

This is the **single unlock** for NanoWire Tier 2. Currently `gate.pull` (R-01) and `gate.check` (R-02) use SSH to run `membrane temporal.cascade` on remote gates. With `cascade.notify`:

```
CURRENT:  sporeGate --SSH--> golgiBody: "cd /root && membrane temporal.cascade"
TARGET:   sporeGate syncs → gossips cascade.notify → golgiBody hears → pulls autonomously
```

### Where the Code Lives

| Component | File | What to Do |
|-----------|------|------------|
| `gate.pull` (SSH call site) | `crates/membrane-shadow/src/gate/mod.rs:~203` | Add `--mesh` flag that uses gossip instead of SSH |
| Temporal cascade (post-sync) | `crates/membrane-shadow/src/temporal/post_sync.rs` | Add `cascade.notify` gossip emit after successful sync |
| swarmVine gossip | `primals/swarmVine/src/` | Add `CascadeNotify` event type if not present |
| songBird federation | `primals/songBird/` | Relay the gossip event to mesh peers via `:7700` |

### Event Shape (Proposed)

```rust
/// Gossip event: a gate completed temporal.cascade on one or more repos
pub struct CascadeNotify {
    /// Gate that synced
    pub gate: String,
    /// Repos that were updated (with new HEAD SHAs)
    pub repos: Vec<RepoSyncResult>,
    /// Timestamp
    pub synced_at: chrono::DateTime<chrono::Utc>,
}

pub struct RepoSyncResult {
    pub name: String,
    pub head_sha: String,
    pub status: SyncStatus, // Synced, AlreadyCurrent, Failed
}
```

### Shadow Validation Pattern

Per NanoWire retirement checklist:

1. Add `--mesh` flag to `gate.pull`
2. Both SSH and mesh paths run during shadow period
3. Compare results — mesh must match SSH output
4. Once shadow passes, SSH path becomes `--legacy` fallback
5. After one full wave with no `--legacy` usage, remove SSH code

### Acceptance

- `membrane gate.pull --mesh` sends `cascade.notify` gossip instead of SSH
- golgiBody (or any mesh peer) receives the gossip and triggers `temporal.cascade` locally
- Shadow comparison: mesh result matches SSH result for same set of repos
- `membrane gate.check --mesh` uses `cascade.status` RPC instead of SSH

---

## Task 2: `gate.pull` → Mesh Path (R-01)

Currently in `gate/mod.rs`:

```rust
pub async fn pull(config: &ShadowConfig) -> Result<SyncResult> {
    // ...
    let cmd = format!("cd {root} && membrane temporal.cascade --source {source} 2>&1");
    let output = ssh::exec(config, &cmd).await?;
    Ok(parse_sync_output(&output))
}
```

Target:

```rust
pub async fn pull(config: &ShadowConfig, use_mesh: bool) -> Result<SyncResult> {
    if use_mesh {
        // Gossip cascade.notify → peer pulls autonomously
        // Then query cascade.status to verify
        let notify = CascadeNotify { gate: config.gate_name.clone(), /* ... */ };
        swarmvine::gossip::emit(notify).await?;
        // Wait for acknowledgment via cascade.status
        let status = mesh::query_cascade_status(config).await?;
        Ok(status)
    } else {
        // Legacy SSH path
        let cmd = format!("cd {root} && membrane temporal.cascade --source {source} 2>&1");
        let output = ssh::exec(config, &cmd).await?;
        Ok(parse_sync_output(&output))
    }
}
```

---

## Task 3: Transport Abstraction Audit (Ongoing)

While working in cellMembrane, note any remaining `ssh::exec` or `ssh::exec_raw_on` call sites that could be retired with mesh equivalents. The NanoWire checklist has 18 sites in 16 files — Tier 2 (R-01 through R-05) is the current target.

**Proven pattern** from sub-builder dispatch: TCP JSON-RPC on well-known port, `call_tcp` from foreman, manifest-driven endpoint resolution.

---

## sporeGate State for Reference

- **15 primals running** on sporeGate (all since Sep 20, stable 7 days)
- **songBird mesh**: sporeGate `:7700` + golgiBody `:7700` both active
- **WireGuard**: 3 peers FRESH (sporeGate, eastGate, northGate), 6 STALE (House 2 offline)
- **Cascade timer**: firing every 15min, syncing 15/17 repos, publishing freshness heads
- **Harvest scheduler**: firing every 10min, evaluating build queue
- **dnsmasq**: all House 1 gates have LAN entries + WG aliases

---

*cellMembrane Wave 159 tasking. Primary: wire `cascade.notify` gossip event to unlock NanoWire Tier 2 SSH retirement. Secondary: `gate.pull --mesh` path with shadow validation. sporeGate infrastructure ready — timers active, DNS converged, hooks hardened.*
