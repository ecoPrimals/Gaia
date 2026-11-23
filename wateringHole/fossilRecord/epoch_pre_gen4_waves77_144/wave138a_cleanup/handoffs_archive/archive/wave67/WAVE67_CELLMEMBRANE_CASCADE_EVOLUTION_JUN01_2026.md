# Wave 67+ cellMembrane Cascade Evolution Sprint

**Date:** 2026-06-01
**Gate:** ironGate
**Repo:** gardens/cellMembrane
**Wave:** 67+

---

## Summary

Executed the full 7-item cascade evolution FRAGO from eastGate. All items
completed in a single sprint, pushed to both remotes.

## Completed Items

### 1. dispatch.rs split (827L → 5 submodules)

- `dispatch/mod.rs` (40L) — top-level router
- `dispatch/temporal.rs` (118L) — cascade, check, sync
- `dispatch/impulse.rs` (125L) — impulse + potential
- `dispatch/infra.rs` (333L) — repo, mirror, service, gate, token
- `dispatch/data.rs` (260L) — manifest, identity, context, plasmid, relay

All under 800L ecosystem cap. Items 3/4 benefited from the split.

### 2. Tree-parity divergence resolution (P0)

New `SyncAction::TreeParity` variant. When `diverge_count > 1`, runs
`git diff --stat` between remotes. If trees are identical (rebase artifact),
force-pushes follower with `--force-with-lease` instead of flagging for
human review.

### 3. --publish-freshness wired

After `cascade()` completes, `--publish-freshness` collects HEAD SHAs from
all synced repos and writes `freshness.toml`. New `freshness.rs` module
extracted for cohesion (263L).

### 4. post_sync_diverge() + graduated merge strategies

- `post_sync_diverge()` fires SYNC impulse when real divergence detected
- `apply_divergence_policy()` reads manifest's per-repo `divergence_policy`
- Supports: `merge-ff` (pull+push), `merge-rebase` (rebase+force-push), `impulse-only` (human)
- `sync_with_policy()` new entry point accepting manifest for policy resolution

### 5. Impulse ack safety

- Acks now written to `impulses/acks/{impulse-id}_{gate}.toml`
- No longer appends `[[acks]]` to original TOML (fragile under rebase)
- `sense()`, `check()`, `archive()` all merge external ack files
- `load_external_acks()` and `is_fully_acked_with_externals()` in policy.rs

### 6. Binary freshness tracking

- `--check-installed` reads provenance sidecars from `~/.local/share/ecoPrimals/provenance/`
- Compares `build_commit` against current source HEAD
- Reports FRESH / STALE / UNKNOWN per binary
- Integrates with `plasmidbin install` provenance output

### 7. Hardcoded defaults evolution

- `dispatch_cascade`: gate fallback now fails explicitly (no silent "eastGate" default)
- `git_ops.rs`: `PUSH_REMOTES` resolved from manifest `[sync].push_remotes`
- `relay.rs`: config from `membrane.toml [relay]` via XDG path, then env, then defaults
- `service.rs`: `ServicePaths` runtime resolver (env/config/default chain)
- `credentials.rs`: `CredentialPaths` runtime resolver
- `plasmid.rs`: rsync → SSH+cat (eliminates rsync binary requirement)

## Deep Debt Sprint (same session)

Additionally completed a full deep debt sweep:
- Zero unsafe code (workspace `forbid(unsafe_code)`)
- Zero TODOs/mocks in production
- Zero clippy warnings (pedantic + nursery)
- `BinaryIntegrity` evolved from `&'static str` to runtime-resolved paths
- `binary_integrity_for_paths()` accepts `ServicePaths` config
- `from_deploy_paths()` bridges `membrane.toml [paths]` to type system

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 207 passing |
| Clippy | 0 warnings |
| Net lines | +1769, -916 |
| Files changed | 17 |
| External deps eliminated | rsync |
| New modules | dispatch/ (5), freshness.rs |

## Upstream Notes

- Items 3+4 depend on item 1 (dispatch split) — DONE
- Item 6 depends on items 2+5 — DONE
- eastGate parallel work on primalSpring/plasmidBin can merge independently
- `temporal.rs` at 896L — core sync engine, all cohesive splits made (two `#[allow(too_many_lines)]` functions for cascade/sync_with_policy)
