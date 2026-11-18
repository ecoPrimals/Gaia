# projectFOUNDATION — Wave 63+ Deep Debt Resolution

**Date**: May 30, 2026
**From**: projectFOUNDATION team
**To**: primalSpring coordination, upstream primals teams
**Phase**: Wave 63+ — architectural debt cleared, typed evolution

---

## Summary

Following the Wave 63 sporePrint pipeline delivery, projectFOUNDATION completed
a comprehensive deep debt resolution pass. All identified architectural debt has
been resolved, resulting in a cleaner, faster, and more idiomatically Rust
codebase ready for Phase C production parity.

---

## What Was Delivered

### Architectural Evolution

| Change | Before | After |
|--------|--------|-------|
| CLI async model | `#[tokio::main]` on all 7 commands | Only `validate` uses tokio runtime; 6 commands run synchronously |
| Observation types | `Vec<(String, f64)>` raw tuples | `Vec<Observation<'a>>` — zero-copy borrowed IDs |
| Fetch results | `Vec<(String, bool)>` | `Vec<FetchStatus>` typed struct |
| Provenance IDs | 4 separate `Option<&str>` params | `ProvenanceIds<'a>` struct |
| Domain convention table | Inline string literals | Uses `primal_names::slugs::*` constants |
| Fetcher magic strings | Inline URLs, user agent, extension | `domains::NCBI/UNIPROT`, `USER_AGENT`, `DEFAULT_FILE_EXTENSION` |
| Process output capture | `from_utf8_lossy().into_owned()` (always copies) | `String::from_utf8()` (zero-copy for valid UTF-8) |

### Metrics

| Metric | Wave 63 | Wave 63+ |
|--------|------:|------:|
| Workspace lines | 7,491 | 8,001 |
| Tests | 137 | 150 |
| Binary (release) | 3.2 MB | 3.2 MB |
| `unused_async` suppressions | 6 | 0 |
| Hardcoded primal strings | 7 inline | 0 (all via `primal_names::slugs`) |
| Production unsafe blocks | 0 | 0 |
| Production mocks | 0 | 0 |
| Max file size | 566 lines | 450 lines |

### Quality Gates (all green)

- `cargo fmt --check` — clean
- `cargo clippy --workspace -- -D warnings` — zero warnings
- `cargo clippy --workspace --tests -- -D warnings` — zero warnings (test targets allow unwrap/expect)
- `cargo test --workspace` — 150 tests, all passing
- Release binary — 3.2 MB, zero C dependencies
- No `todo!()`, `unimplemented!()`, or `panic!()` in production
- No mocks outside `#[cfg(test)]` targets

---

## Phase C Remaining Work

These items require upstream primal availability or cross-repo coordination:

| Item | Blocked On |
|------|-----------|
| NestGate artifact registration (`backfill --write`) | NestGate RPC endpoint |
| toadStool workload dispatch (replace native exec) | toadStool composition running |
| Full `ProvenanceSession` trio (DAG + spine + braid) | rhizoCrypt + loamSpine + sweetGrass |
| sporePrint notify trigger (`publish` → `repository_dispatch`) | sporePrint CI pipeline |
| Bidirectional Forgejo mirror | projectNUCLEUS scope (Forgejo instance) |
| Database-specific async fetch (NCBI/UniProt/KEGG) | Tokio-native ureq or reqwest eval |

---

## Asks for Upstream Teams

### primalSpring

- **Validate composition**: foundation binary is ready for inclusion in primalSpring
  validation compositions as a validation-gate primal
- **Confirm primal_names parity**: foundation uses `primal_names::slugs` from
  `foundation-core` — verify alignment with canonical `primal_names` in primalSpring

### NestGate / toadStool teams

- **Phase C coordination**: When NestGate content-put and toadStool workload-dispatch
  RPC endpoints are stable, foundation can wire the last two execution phases

### sporePrint team

- **repository_dispatch webhook**: foundation `publish` command needs a trigger target
  to signal sporePrint to rebuild after gallery pages are generated

---

## Bash Pipeline Status

The `deploy/` scripts remain the production-canonical pipeline until Phase C cuts
over. They will be retained as fossil record in the repo after cutover. The Rust
binary already covers all Phase 1-8 logic except NestGate/toadStool RPC dispatch
(which degrades gracefully when those primals are unavailable).
