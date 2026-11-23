# cellMembrane Wave 150v — Sovereign Depot Auto-Build Pipeline

**Date:** 2026-07-23
**Primal:** cellMembrane
**Wave:** 150v
**Author:** eastGate overwatch
**Assignment:** Close the Forgejo-sovereign binary lifecycle gap

---

## Problem Statement

The depot pipeline has all the Rust building blocks but three critical
connections are missing. When a primal is pushed to Forgejo, the source
syncs to all gates within minutes — but the **binary stays stale**
indefinitely until someone manually runs a harvest.

Evidence: songBird shipped `songbird benchmark` on Jul 22. The depot
binary on golgiBody was still from Jul 15 (commit `78c14667`). All three
primalSpring gate teams attempted to use the new CLI and failed because
the depot never rebuilt.

### Root Cause

```
Forgejo push (golgiBody)
  → post-receive → relay.run (git sync to GitHub)    ← WORKING
  → cascade timer → git repo sync to gates           ← WORKING
  → ??? → sporeGate build → depot → gates            ← NOT CONNECTED
```

The `sovereign.ci.trigger` command exists in Rust, fully implemented. The
`run_harvest_pipeline` webhook handler exists. The `has_upstream_changes`
drift detection exists. None of them are called from any automated trigger
in the Forgejo-sovereign flow.

---

## Four-Phase Fix

### Phase 1: Reactive Trigger (Forgejo push → sporeGate build)

**What**: New post-receive hook on golgiBody dispatches `sovereign.ci.trigger`
on sporeGate via WireGuard SSH when a primal is pushed.

**Deliverable**: `gardens/cellMembrane/deploy/hooks/forgejo/golgi-post-receive-ci.sh`
(already written — see below).

**How it works**:
1. Forgejo fires post-receive hooks after push
2. Hook resolves repo name from `$GIT_DIR`
3. Checks `ecosystem_manifest.toml` to determine if repo is a primal
   (looks for `category = "primals"` in the manifest entry)
4. If primal: SSH to sporeGate (`10.13.37.2`) over WireGuard mesh
5. Runs `membrane sovereign.ci.trigger --primal <name> --commit <sha>`
6. Background-forked so Forgejo doesn't block

**Install** (on golgiBody, for each primal repo):
```bash
# Copy to each primal's hook directory
for repo in /opt/forgejo/data/gitea-repositories/ecoPrimals/*.git; do
    name=$(basename "$repo" .git)
    mkdir -p "$repo/hooks/post-receive.d"
    cp golgi-post-receive-ci.sh "$repo/hooks/post-receive.d/30-sovereign-ci"
    chmod +x "$repo/hooks/post-receive.d/30-sovereign-ci"
done
```

**Zero Rust changes required.** The existing `sovereign.ci.trigger` does:
harvest (force) → sandbox validate → refresh (atomic deploy + depot sync)
→ provenance publish. It already validates primal names against the
service registry and handles `--commit` for traceability.

**Key code reference**: `gardens/cellMembrane/crates/membrane-shadow/src/dispatch/sovereign.rs`

---

### Phase 2: Convergent Trigger (cascade drift detection)

**What**: After cascade syncs primal repos, compare each primal's local
HEAD against `provenance.toml` to detect commit drift. On builder gates,
auto-harvest drifted primals. On consumer gates, log and signal.

**Where**: `gardens/cellMembrane/crates/membrane-shadow/src/temporal/post_sync.rs`

**Implementation**:

Add a new function `detect_and_handle_commit_drift()` called from
`run_post_sync_phases()`, inserted between freshness publishing (line 66)
and `run_depot_staleness_and_fetch` (line 98).

```rust
/// Detect primals where source HEAD has advanced past depot provenance.
/// On builder gates: auto-harvest drifted primals.
/// On consumer gates: log drift warning.
async fn detect_and_handle_commit_drift(
    root: &std::path::Path,
    lines: &mut Vec<String>,
) -> Vec<String> {
    let depot_dir = match crate::plasmid::depot::resolve_depot(None) {
        Ok(d) => d,
        Err(_) => return Vec::new(),
    };
    let provenance = crate::plasmid::depot::load_provenance(&depot_dir).ok();
    let sources = crate::plasmid::harvest::load_sources(&depot_dir);

    let mut drifted = Vec::new();
    for name in crate::plasmid::nucleus_primals() {
        if let Some(source) = sources.get(name) {
            if crate::plasmid::drift::has_upstream_changes(
                name,
                source,
                provenance.as_ref(),
                &depot_dir,
            ).await {
                drifted.push(name.to_string());
            }
        }
    }

    if drifted.is_empty() {
        lines.push("  [drift] all primals current with depot".into());
    } else {
        lines.push(format!(
            "  [drift] {}/{} primals have source changes not in depot: [{}]",
            drifted.len(),
            crate::plasmid::nucleus_primals().len(),
            drifted.join(", ")
        ));

        let is_builder = is_build_authority();
        if is_builder {
            lines.push("  [drift] build authority — auto-harvesting drifted primals".into());
            // Harvest each drifted primal individually
            for primal in &drifted {
                let harvest_args = crate::plasmid::HarvestArgs {
                    primal: Some(primal.clone()),
                    force: true,
                    dry_run: false,
                    depot_dir: None,
                    target: None,
                    local: true,  // use local checkout, already synced
                };
                match crate::plasmid::harvest(&harvest_args).await {
                    Ok(o) => lines.push(format!("  [drift] {primal}: {}", o.message)),
                    Err(e) => lines.push(format!("  [drift] {primal}: FAIL — {e}")),
                }
            }
        }
    }
    drifted
}

fn is_build_authority() -> bool {
    std::env::var("MEMBRANE_BUILD_AUTHORITY")
        .is_ok_and(|v| matches!(v.as_str(), "1" | "true" | "yes"))
}
```

**Wire into `run_post_sync_phases()`** at line ~98, before
`run_depot_staleness_and_fetch`:

```rust
// After freshness, before depot staleness
if opts.mode == CascadeMode::Sync {
    let drifted = detect_and_handle_commit_drift(root, lines).await;
    if !drifted.is_empty() && is_build_authority() {
        // Builder already harvested — now sandbox + refresh
        let passed = run_post_cascade_sandbox(&drifted, lines).await;
        if !passed.is_empty() {
            if let Ok(pushed) = run_post_cascade_refresh(Some(&passed), lines).await {
                lines.push(format!("  [drift] {} rebuilt, {} pushed to depot", drifted.len(), pushed));
            }
        }
    }
}
```

**This supersedes `MEMBRANE_AUTO_REBUILD`**: The current auto-rebuild uses
weak presence-only staleness (`detect_stale_primals` in `depot.rs` — only
checks if a binary file exists + provenance has a commit field). Commit
drift detection is the strong check — a binary that exists but is 20
commits behind gets caught.

**Existing code leveraged**:
- `drift::has_upstream_changes` — `ls-remote` HEAD vs `provenance.toml` commit
- `run_post_cascade_harvest` — manifest-driven build
- `run_post_cascade_sandbox` + `run_post_cascade_refresh` — validate and deploy

**sporeGate env**: Set `MEMBRANE_BUILD_AUTHORITY=1` in sporeGate's
`membrane.env` or systemd unit override.

---

### Phase 3: Hard Enforcement (depot-only with crypto lineage)

**What**: Gates refuse to run binaries that don't chain back to the signed
depot. PostPrimordial primals (intercommunication stack) require full
provenance validation.

#### 3a. Classify primals as postPrimordial

**Where**: `gardens/cellMembrane/crates/cellmembrane-types/src/service/constants.rs`
(or `identity.rs`)

```rust
/// Primals in the intercommunication layer that MUST be deployed
/// exclusively from the signed depot. No local builds on consumer gates.
pub const POST_PRIMORDIAL_PRIMALS: &[&str] = &[
    "beardog",
    "songbird",
    "skunkbat",
    "nestgate",
    "cellmembrane",
    "biomeos",
];

pub fn is_post_primordial(primal: &str) -> bool {
    POST_PRIMORDIAL_PRIMALS.contains(&primal)
}
```

#### 3b. Enforce at `plasmid.refresh` and `gate.bootstrap`

**Where**: `gardens/cellMembrane/crates/membrane-shadow/src/plasmid/refresh.rs`
and `gardens/cellMembrane/crates/membrane-shadow/src/gate/verify.rs`

Before installing a binary, verify:
1. BLAKE3 matches signed `checksums.toml` — already exists as
   `VerifyIfPresent` trust policy; **promote to `RequireSigned` for
   postPrimordial primals**
2. `provenance.toml` commit exists for this primal
3. Binary `builder` field matches a known build authority gate (sporeGate)

For postPrimordial primals: **FAIL** if any check fails (hard block).
For other primals: **WARN** but allow (soft enforcement during transition).

```rust
fn validate_lineage(primal: &str, depot_dir: &Path) -> LineageResult {
    let is_critical = cellmembrane_types::is_post_primordial(primal);
    let trust = if is_critical {
        DepotTrustPolicy::RequireSigned
    } else {
        DepotTrustPolicy::VerifyIfPresent
    };

    let checksum_ok = verify_blake3(primal, depot_dir, trust);
    let provenance_ok = verify_provenance_commit(primal, depot_dir);
    let builder_ok = verify_builder_authority(primal, depot_dir);

    if is_critical && !(checksum_ok && provenance_ok && builder_ok) {
        LineageResult::Blocked(format!(
            "{primal} is postPrimordial — depot lineage validation FAILED"
        ))
    } else if !(checksum_ok && provenance_ok && builder_ok) {
        LineageResult::Warned(format!(
            "{primal} — lineage incomplete (soft enforcement)"
        ))
    } else {
        LineageResult::Verified
    }
}
```

#### 3c. Runtime validation scenario

**Where**: `springs/primalSpring/ecoPrimal/src/validation/scenarios/`

New scenario: `s_depot_lineage_enforcement.rs`
- For each installed primal on the gate:
  - Read provenance sidecar (`~/.local/share/ecoPrimals/provenance/<primal>.toml`)
  - Verify `build_commit` matches depot `provenance.toml`
  - Verify BLAKE3 matches depot `checksums.toml`
  - Verify `builder` is a recognized build authority (sporeGate)
- FAIL if any postPrimordial primal has broken lineage
- WARN for non-postPrimordial primals

---

### Phase 4: Build-Pending Mesh Signal

**What**: When cascade detects source drift, publish `depot.build_pending`
so consumer gates know binaries are stale and a rebuild is in progress.

**Where**: `gardens/cellMembrane/crates/membrane-shadow/src/plasmid/mod.rs`
(alongside existing `notify_mesh_depot_updated`)

```rust
pub async fn notify_mesh_build_pending(drifted: &[String]) {
    let payload = serde_json::json!({
        "event": "depot.build_pending",
        "primals": drifted,
        "timestamp": crate::utc_now_iso8601(),
    });
    // Publish via songBird mesh (same pattern as depot.updated)
    crate::mesh::publish("depot.build_pending", &payload).await;
}
```

**Consumer behavior**: `auto_fetch.rs` checks for `build_pending` state
before fetching. If pending, delay fetch until `depot.updated` arrives
(or 10-minute timeout). Prevents fetching stale binaries during the
window between source sync and builder completion.

---

## File Reference

| File | Role | Phase |
|------|------|-------|
| `deploy/hooks/forgejo/golgi-post-receive-ci.sh` | Reactive trigger | 1 |
| `deploy/hooks/forgejo/golgi-post-receive-relay.sh` | Existing relay (no change) | — |
| `crates/membrane-shadow/src/dispatch/sovereign.rs` | CI trigger (no change needed) | 1 |
| `crates/membrane-shadow/src/temporal/post_sync.rs` | Cascade drift detection | 2 |
| `crates/membrane-shadow/src/plasmid/drift.rs` | Upstream change detection (no change) | 2 |
| `crates/membrane-shadow/src/plasmid/depot.rs` | Weak staleness (superseded by drift) | 2 |
| `crates/cellmembrane-types/src/service/constants.rs` | PostPrimordial classification | 3 |
| `crates/membrane-shadow/src/plasmid/refresh.rs` | Lineage enforcement at deploy | 3 |
| `crates/membrane-shadow/src/gate/verify.rs` | Lineage enforcement at bootstrap | 3 |
| `crates/membrane-shadow/src/plasmid/mod.rs` | Build-pending mesh signal | 4 |
| `crates/membrane-shadow/src/plasmid/auto_fetch.rs` | Pending-aware fetch | 4 |

---

## Delivery Order

| Phase | Deliverable | Complexity | Dependencies |
|-------|------------|------------|--------------|
| **1** | `golgi-post-receive-ci.sh` deploy | **Low** (bash) | sporeGate SSH over WG |
| **2** | Cascade commit drift + auto-harvest | **Medium** (~100L Rust) | `drift.rs`, `post_sync.rs` |
| **3** | PostPrimordial enforcement | **Medium** (~150L Rust) | `cellmembrane-types`, `refresh.rs` |
| **4** | Build-pending mesh signal | **Low** (~50L Rust) | Phase 2 |

Phase 1 is deployable immediately with zero Rust changes. Phases 2–4 are
Rust evolution on eastGate, tested on sporeGate.

---

## Validation Criteria

After all phases:

- [ ] Push to any primal on Forgejo → sporeGate builds within minutes →
      golgiBody depot updated → gates auto-fetch
- [ ] Cascade on any gate detects commit drift and reports it
      (builder gates auto-fix, consumer gates log warning)
- [ ] No gate runs a postPrimordial binary that didn't come from the
      signed depot (hard enforcement)
- [ ] `s_depot_lineage_enforcement` scenario passes on all gates
- [ ] `sovereign.ci.status` reports 0 stale when all primals are current

---

## CONVERGENCE RULE

Code evolution for Phases 2–4 happens on **eastGate only**. Gate teams
deploy Phase 1 hook and set `MEMBRANE_BUILD_AUTHORITY=1` on sporeGate.
File AARs with findings. Do not modify cellMembrane Rust code on
non-eastGate machines.
