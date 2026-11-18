# FRAGO: Bidirectional Relay — GitHub → Forgejo Reverse Sync

**Date**: Jul 4, 2026 19:10 EDT  
**Wave**: 132e  
**Gate**: golgi (cellMembrane team)  
**From**: eastGate overwatch  
**Priority**: P1 — causes silent divergence across gates  
**Type**: Infrastructure gap — relay chain is unidirectional

---

## Situation

flockGate's IDE agents pushed songBird and bearDog Tower HTTP evolution to **GitHub (origin)** but NOT to **Forgejo (sovereign)**. golgi's relay chain (`membrane relay.run`) is unidirectional:

```
Forgejo → post-receive hook → relay.run → mediate() → ship_extracellular() → GitHub
```

There is **no reverse path**. When a gate pushes to GitHub directly (bypassing Forgejo), the changes become invisible to all gates that pull from Forgejo — including sporeGate (the builder).

**Impact**: sporeGate cellMembrane team was blocked for hours — they couldn't see the Tower HTTP gateway code they needed to build and deploy. Overwatch manually pushed from eastGate to resolve.

---

## Root Cause

1. flockGate's git config has `origin` = GitHub. IDE agents default to `git push origin main`
2. `relay.run` only fires on Forgejo post-receive hooks — no periodic GitHub → Forgejo check
3. `cascade-sense.sh` (15min timer) only handles wateringHole, not all primal repos
4. No alert when GitHub and Forgejo diverge for a primal repo

---

## Required Fix: `relay.absorb()` — Reverse Sync

Add a new stage to the relay chain that detects when GitHub is ahead of Forgejo and pulls changes back in:

### Option A: Extend `cascade-sense.sh` to all repos (quick fix)

On golgi, the 15min timer should iterate all repos in `ecosystem_manifest.toml` and for each:

```bash
cd $repo_path
git fetch github main --quiet
git fetch forgejo main --quiet
# If github is ahead of forgejo, pull github → push forgejo
ahead=$(git rev-list --count forgejo/main..github/main 2>/dev/null || echo 0)
if [ "$ahead" -gt 0 ]; then
    git checkout main
    git merge github/main --ff-only
    git push forgejo main
    log "REVERSE-SYNC: $repo_name — $ahead commits absorbed from GitHub → Forgejo"
fi
```

### Option B: Add `relay.absorb()` to Rust relay module (proper fix)

In `membrane-shadow/src/relay.rs`, add:

```rust
/// Stage 0 (pre-mediate): Absorb extracellular → inner.
/// Detects when GitHub is ahead of Forgejo and syncs back.
/// This handles the case where a gate pushed to GitHub directly.
pub async fn absorb_extracellular(config: &RelayConfig, repo_paths: &[&str]) -> Vec<String> {
    // For each repo:
    // 1. git fetch github/origin
    // 2. git fetch forgejo
    // 3. If github ahead of forgejo: merge --ff-only, push forgejo
    // 4. Log absorptions
}
```

Wire into `relay.run()` as stage 0, before `mediate()`.

### Option C: Fix at source — flockGate push hook (preventive)

Add a git post-push hook or alias on flockGate that ensures every `git push origin` also does `git push forgejo`:

```bash
# ~/.config/git/hooks/post-push (or alias)
git push forgejo main 2>/dev/null || true
```

---

## Recommended Approach

**Do both B and C**:
- **B** (absorb) catches any future case where a gate pushes to GitHub directly — defensive
- **C** (push hook) prevents the divergence from happening — preventive

Option A is acceptable as an interim if B takes time.

---

## Immediate Resolution (already done)

Overwatch (eastGate) manually pushed songBird and bearDog from our local (which had pulled from GitHub) to Forgejo:

```bash
cd songBird && git push forgejo main  # 05e2204..906fe88 (3 commits)
cd bearDog && git push forgejo main   # 7ea894f..ff18b17 (2 commits)
```

Sovereign CI triggered on sporeGate. Binaries should now build.

---

## Divergence Detection (future)

The `unify_freshness()` cycle should compare `heads/<gate>.toml` with actual Forgejo HEADs and alert when they diverge. This already exists conceptually but doesn't check GitHub vs Forgejo parity.

Add to the cascade-sense timer:

```bash
# After relay, verify parity
for repo in $(list_ecosystem_repos); do
    gh_head=$(git ls-remote github main | cut -f1)
    fg_head=$(git ls-remote forgejo main | cut -f1)
    if [ "$gh_head" != "$fg_head" ]; then
        echo "[DIVERGENCE] $repo: GitHub=$gh_head Forgejo=$fg_head" >> "$LOG"
    fi
done
```

---

## Acceptance

1. `relay.run` (or cascade timer) absorbs GitHub-ahead commits into Forgejo automatically
2. sporeGate never sees stale code again (within 15min of any push)
3. flockGate push hook ensures Forgejo gets every push
4. Divergence logged and detectable in cascade-sense output

---

*Sovereign means Forgejo is truth. But truth must absorb all paths of entry.*
