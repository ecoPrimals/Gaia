# AAR: flockGate Wave 64 Bootstrap Friction

**Date:** May 31, 2026
**Gate:** flockGate (WAN shadow, i9-13900K)
**From:** sporePrint team
**Type:** After Action Report — Gate Bootstrap

---

## Summary

flockGate bootstrapped successfully from a fresh workspace during Wave 63.
The K-Derm diderm relay chain propagates within ~3s (gate → Forgejo → GitHub).
Below are the friction points discovered and proposed fixes.

---

## Friction Points

### 1. Forgejo SSH org path ambiguity

**Issue:** GATE_SETUP_STANDARD.md uses `ecoPrimals/wateringHole.git` but the
actual Forgejo org is case-sensitive. Initial clone attempts with wrong casing
fail silently (no "org not found" hint — just "repository does not exist").

**Impact:** 5-minute delay figuring out the exact org/repo path.

**Proposed fix:** Add a note to Step 2:
```
Note: Forgejo paths are case-sensitive. Use exact casing from
ecosystem_manifest.toml (e.g., `ecoPrimals/wateringHole`, not
`ecoprimals/wateringhole`).
```

### 2. SSH key registration requires API token (not documented clearly)

**Issue:** The prerequisites section shows a `curl` command requiring
`<TOKEN>` — but doesn't explain how to obtain this token. New gates
bootstrapping without prior Forgejo access have a chicken-and-egg problem.

**Impact:** Required eastGate to manually register the key via Forgejo web UI.

**Proposed fix:** Add to prerequisites:
```
To register keys without a pre-existing token, have an existing gate
admin add your SSH public key via the Forgejo web UI:
  Admin Panel → User Accounts → Keys → Add Key
Or use the BTSP bootstrap flow (once available).
```

### 3. `cascade-pull.sh --source temporal` assumes membrane binary

**Issue:** On a fresh gate, the membrane binary doesn't exist yet. If
`--source temporal` is the first command run, it tries to invoke `membrane`
for temporal sync which doesn't exist.

**Impact:** Falls back to `--source origin` (GitHub), which works fine but
produces a confusing error message about missing `membrane` binary.

**Proposed fix:** cascade-pull should check for membrane binary availability
and auto-fallback to direct git SSH operations when membrane is not installed,
with an info message: "membrane not found, using direct SSH for temporal sync".

### 4. No `zola` in standard dev platform section

**Issue:** Step 4 (Dev Platform) documents Rust toolchain install but not
Zola, which is needed for sporePrint builds. A gate team member bootstrapping
specifically for sporePrint has to find the Zola install docs separately.

**Impact:** Minor — Zola installation is straightforward. But for
completeness, it should be in the standard.

**Proposed fix:** Add to Step 4:
```bash
# Zola (for sporePrint and other Zola-based sites)
# Download from https://www.getzola.org/documentation/getting-started/installation/
# Or:
cargo install zola  # slower (builds from source)
```

### 5. `target/` accidentally tracked in sporePrint

**Issue:** 1,162 Rust build artifacts in `crates/spore-validate/target/` were
committed to git history (pre-existing before flockGate clone). This caused
the initial clone to be larger than necessary and `.gitignore` pattern
`crates/*/target/` didn't prevent it because the files were already tracked.

**Impact:** Fixed in Wave 63 deep debt resolution (`git rm -r --cached`).

**Proposed fix:** Already resolved. The `.gitignore` now uses `target/` at
root level (catches all depths).

---

## What Worked Well

1. **SSH relay chain**: Push to `forgejo` → golgiBody propagates to GitHub
   within ~3s. No manual intervention needed.
2. **cascade-pull with `--shallow`**: Large repos (bearDog 413K LOC) cloned
   successfully over WAN without timeout.
3. **Dual remote setup**: `origin` (GitHub read) + `forgejo` (SSH write) is
   clean and intuitive.
4. **GATE_SETUP_STANDARD overall**: The document is comprehensive and the
   flow is logical. These are edge-case friction items, not structural problems.

---

## Measurements (flockGate WAN)

| Operation | Time | Notes |
|-----------|------|-------|
| `git push forgejo` (sporePrint) | 1.5-1.8s | Includes SSH handshake |
| `git push forgejo` (wateringHole) | 0.7-0.9s | Smaller repo |
| `zola build` (226 pages) | 746ms | i9-13900K, NVMe |
| `cargo build --release` (spore-validate) | 5.56s | Clean build, 7 deps |
| `cargo test` (80 tests) | 0.6s | Fast execution |
| Forgejo → GitHub propagation | ~3s | K-Derm relay chain |

---

## Proposed GATE_SETUP_STANDARD.md Patch

The fixes above are minor text additions. Ready to submit as a patch to
eastGate for review and merge.
