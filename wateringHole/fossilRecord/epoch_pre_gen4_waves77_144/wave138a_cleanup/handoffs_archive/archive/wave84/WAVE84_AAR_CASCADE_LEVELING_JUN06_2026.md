# Wave 84 AAR: Cascade System Leveling

**Date**: 2026-06-06  
**Author**: eastGate overwatch  
**Type**: After Action Review  
**Status**: Resolved — cascade system operational, cellMembrane evolves  

---

## Problem

The cascade system was being run manually via bash loops (`git fetch && git pull`
in each repo) despite cellMembrane having a fully typed, manifest-driven cascade
implementation in Rust (`membrane temporal.cascade`). Three issues compounded:

1. **Git operations had no timeout** — `git_output` and `git_success` in
   `git_ops.rs` called `tokio::process::Command::new("git")` without any
   timeout protection. A single stalled SSH connection (forgejo remote)
   caused the entire 38-repo cascade to hang indefinitely (8+ minutes,
   eventually killed).

2. **Workspace resolution required manual env** — `resolve_workspace_root()`
   only checked `ECOPRIMALS_ROOT` env var and walked up from the executable
   path. Since membrane is installed at `~/.local/bin/membrane`, it couldn't
   find the workspace. Every invocation required manual
   `ECOPRIMALS_ROOT=/home/eastgate/Development/ecoPrimals`.

3. **Default divergence policy was `flag`** — the ecosystem manifest's
   `divergence_policy = "flag"` caused tree-parity divergences (identical
   content, divergent history from rebase) to be flagged for manual review
   instead of being auto-resolved. Both `wateringHole` and `primalSpring`
   had tree-parity divergences that required human intervention.

## Root Cause

The cascade code was robust (typed Rust, DAG-based convergence, tree-parity
detection) but the operational envelope around it was fragile:
- No timeout on the I/O boundary (git SSH transport)
- No environment persistence (`.bashrc` lacked `ECOPRIMALS_ROOT`)
- Conservative default policy (`flag`) appropriate for multi-writer repos
  but too cautious for a single-writer ecosystem

## Resolution

### 1. Git operation timeout (cellMembrane `git_ops.rs`)

Added 60-second timeout to both `git_output` and `git_success`:

```rust
const GIT_OP_TIMEOUT: Duration = Duration::from_secs(60);
const SSH_CMD_WITH_TIMEOUT: &str =
    "ssh -o ConnectTimeout=10 -o ServerAliveInterval=5 \
     -o ServerAliveCountMax=3 -o BatchMode=yes";

fn git_command(repo_path: &Path, args: &[&str]) -> Command {
    let mut cmd = Command::new("git");
    cmd.arg("-C").arg(repo_path)
        .env("GIT_SSH_COMMAND", SSH_CMD_WITH_TIMEOUT)
        .args(args);
    cmd
}
```

`git_output` now wraps in `tokio::time::timeout(GIT_OP_TIMEOUT, ...)` and
returns `ShadowError::Parse` on timeout. `git_success` returns `false`.

### 2. CWD-based workspace resolution (cellMembrane `lib.rs`)

Added CWD walk-up as the first fallback before executable walk-up:

```rust
// Walk up from CWD
if let Ok(cwd) = std::env::current_dir() {
    let mut dir = Some(cwd);
    while let Some(d) = dir {
        if is_workspace(&d) { return Ok(d); }
        dir = d.parent().map(Path::to_path_buf);
    }
}
```

Running `membrane temporal.cascade` from anywhere inside `~/Development/ecoPrimals/`
now works without `ECOPRIMALS_ROOT`.

### 3. Environment persistence (`.bashrc`)

```bash
export ECOPRIMALS_ROOT="$HOME/Development/ecoPrimals"
export GATE_NAME="eastGate"
```

### 4. Divergence policy upgrade (ecosystem_manifest.toml)

```toml
divergence_policy = "merge-ff"
```

Changed from `"flag"` to `"merge-ff"`. This allows the cascade to auto-resolve
simple convergence (fast-forward merge) cases. Tree-parity resolution was already
implemented and bypasses policy entirely — it's safe because content is identical.

## Validation

After applying all fixes:
- Rebuilt and installed membrane binary
- Ran `membrane temporal.cascade` — **38/38 repos synced, 0 failures, ~59 seconds**
- Previous attempt hung indefinitely at 490+ seconds before manual kill

## Divergence Resolution

| Repo | Divergence | Resolution |
|------|-----------|------------|
| wateringHole | forgejo(+7,-8) — tree-parity | `git push --force-with-lease forgejo main` |
| primalSpring | forgejo(+4,-4) — tree-parity | `git pull --ff-only origin` then `push --force-with-lease forgejo` |

Both were rebase artifacts (same commit messages, different SHAs, identical tree content).

## Remaining Work (cellMembrane P2)

| Item | Priority | Notes |
|------|----------|-------|
| Webhook-driven cascade (replace timer-poll) | P3 | Forgejo webhooks on push → trigger selective rebuild |
| Parallel repo sync (tokio::spawn per repo) | P2 | Current cascade is sequential; 38 repos × 1.5s ≈ 57s could be <10s |
| Forgejo sourDough repo fix | P2 | Transient 500 on push — Forgejo data directory issue |
| `agentic` divergence policy implementation | P3 | Placeholder in code; would allow AI-mediated divergence resolution |

---

*"The cascade system is leveled. The membrane owns the sync. Manual git loops
are deprecated."*
