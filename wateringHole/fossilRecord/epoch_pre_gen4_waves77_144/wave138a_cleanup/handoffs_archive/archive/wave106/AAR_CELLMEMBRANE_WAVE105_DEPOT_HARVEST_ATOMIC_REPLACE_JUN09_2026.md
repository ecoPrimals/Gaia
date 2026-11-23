# AAR: plasmid.harvest "Text File Busy" Failure + Remaining cellMembrane Work

**Date**: 2026-06-09 (Wave 105)
**From**: eastGate overwatch
**To**: cellMembrane
**Priority**: P2 (depot harvest reliability), P1 (WAN depot now SHIPPED — validate deployment)

---

## AAR: `membrane plasmid.harvest` Exit Code 1

### Incident

During Wave 104 revalidation, `membrane plasmid.harvest beardog` and
`membrane plasmid.harvest biomeos` both exited with code 1. Both ran for
~9.5 minutes before failing.

### Root Cause

The harvest attempts to overwrite a depot binary that is currently running
as a NUCLEUS primal process. Linux returns `ETXTBSY` ("Text file busy")
when writing to an executable that is mapped into a running process. The
harvest command does not stop the target primal before overwriting, nor does
it use atomic rename (write to temp → rename over original).

### Impact

Operator must manually: stop primal → copy binary → strip → restart primal
→ update checksum. This was done successfully for both bearDog and biomeOS,
but it should be zero-touch.

### Recommendation

**Option A (quick, recommended)**: Atomic rename in harvest — write to
`primals/<triple>/<name>.new`, then `rename(2)` over the original. `rename`
is atomic on the same filesystem and succeeds even when the original is
running. The running process keeps its old fd; next restart picks up the
new binary.

**Option B (thorough)**: Stop-before-harvest — harvest sends
`lifecycle.shutdown` (JSON-RPC) or `SIGTERM` to the running primal, waits
for exit, writes the binary, restarts. More correct but adds complexity and
downtime.

**Option C (hybrid)**: Try direct write; on `ETXTBSY`, fall back to atomic
rename. Log a warning that restart is needed to pick up the new binary.

### Evidence

| Primal | Old Size | New Size | Reason |
|--------|----------|----------|--------|
| bearDog | 12,878,064 | 11,243,648 | Wave 145 pure Rust crypto (aws-lc-rs eliminated) |
| biomeOS | 16,660,352 | 15,930,616 | v4.16 deep debt (error chains, hardcoding elim) |

Both binaries were manually rebuilt, deployed, checksum-updated, committed, and pushed.

---

## Status Update: cellMembrane Recent Evolution

cellMembrane has shipped significant work since Wave 103. Acknowledging:

### SHIPPED (Wave 104-105)

1. **WAN depot distribution** (`plasmid.fetch --source wan`) — P1 RESOLVED
   - HTTPS-based binary fetching from outer membrane (Caddy)
   - `caddy.depot.provision` sets up file_server on golgiBody-ext
   - WAN gates no longer need SSH access for depot binaries
   - **This resolves the sole remaining P1 blocker** (flockGate WAN depot)

2. **Cascade conflict auto-resolve** — P2 RESOLVED
   - Auto-discards dirty regenerable metadata (checksums.toml, provenance.toml, freshness.toml) before ff-only pull
   - Eliminates recurring operator intervention on ~every 2nd cascade
   - Exactly matches the recommendation from `wave104-cross-deployment-readiness.toml [aar.cascade_conflicts]`

3. **Cascade depot staleness reporting** — rebuild suggestions in cascade output
4. **Deep debt elimination** — sha2/hmac crates replace hand-rolled, zero `#[allow]`, typed phases
5. **Env var consolidation** — 39 typed `ENV_*` constants, zero custom string literals
6. **depot.rs extraction** — harvest.rs 811→644 lines, clean module boundary

### REMAINING WORK

| ID | Priority | Description | Status |
|----|----------|-------------|--------|
| CM-HARVEST-ATOMIC | P2 | Atomic rename in plasmid.harvest (this AAR) | **ALREADY SHIPPED** (stage_to_depot uses .new + rename(2), refresh SCPs to .new + mv) |
| CM-WAN-VALIDATE | P2 | Validate plasmid.fetch --source wan on flockGate | **DEPLOYED** — validated from ironGate, 13/13 OK over HTTPS. Awaiting flockGate team. |
| CM-AARCH64-SWEEP | P2 | Cross-compile remaining 11/14 primals for aarch64 | **COMPLETE** — 14/14 built, zero C-dep violations, checksums committed |
| CM-SOURDOUGH-SEGV | LOW | `sourdough validate depot` segfaults — investigate | KNOWN |
| CM-CADDY-PROVISION | P2 | Deploy caddy.depot.provision on golgiBody (production) | **DEPLOYED** — `/depot/` route live on membrane.primals.eco |

### Dependency Map

```
CM-WAN-VALIDATE (validate plasmid.fetch on flockGate)
  └→ flockGate NUCLEUS deployment (first WAN gate with binaries)
       └→ WAN covalent mesh validation
            └→ Stadial criterion 4 (remote covalent over WAN)

CM-AARCH64-SWEEP (cross-compile 11 remaining primals)
  └→ grapheneGate bootstrap (Pixel trust anchor)
  └→ ARM VPS deployment
  └→ ecoBin universal portability

CM-HARVEST-ATOMIC (atomic rename in harvest)
  └→ Zero-touch depot refresh across all gates
       └→ Autonomous gate self-healing
```

---

## AAR: aarch64 Sweep Overwrote x86_64 Checksums (Upstream Cascade Failure)

### Incident

During the Wave 105 aarch64 cross-compile sweep (commit `c46cc1c`), the
sweep tooling wrote `checksums.toml` with **only** the `[aarch64-unknown-linux-musl]`
section, destroying the existing `[x86_64-unknown-linux-musl]` section (14 entries).
This was committed and pushed upstream, then cascaded to all gates.

### Root Cause

The harvest/sweep pipeline treats `checksums.toml` as a single-target file.
When the aarch64 sweep completed, it regenerated `checksums.toml` from its
local build output — which was only aarch64 binaries. The existing x86_64
section was not read, preserved, or merged. The file was overwritten wholesale.

This is a **data-destructive single-writer assumption** in a multi-target
depot. The pipeline was designed when only one target triple existed. The
aarch64 sweep is the first time two target sections needed to coexist.

### Impact

- All 14 x86_64 checksum entries were silently lost
- Any downstream gate running `plasmid.verify` against x86_64 binaries
  would fail checksum validation (entries missing)
- Detected during eastGate revalidation — 14/14 MISMATCH
- Ad-hoc fix applied: x86_64 checksums regenerated from local binaries and
  both sections restored to `checksums.toml`

### Recommendation

**The pipeline must be multi-target aware.** Specific fixes:

1. **Read-modify-write**: Harvest/sweep must read existing `checksums.toml`,
   parse all `[target]` sections, update only the section being built, and
   write back the complete file. Never overwrite the entire file from a
   single target's output.

2. **Section-level locking**: If multiple gates build for different targets
   concurrently, a TOML merge strategy is needed (similar to the cascade
   conflict auto-resolve already shipped for freshness.toml).

3. **Validation gate**: Before committing, verify that all known target
   sections are present. A simple check: count `[` headers in checksums.toml
   and ensure none were lost.

4. **Test**: Add a regression test — run harvest for target A, then target B,
   verify target A's entries survive.

### Evidence

```
# Before aarch64 sweep (commit 55cde48):
[x86_64-unknown-linux-musl]
barracuda = { blake3 = "09cf8bc...", size = 11545120 }
beardog = { blake3 = "1605e2c...", size = 11243648 }
... (14 entries)

# After aarch64 sweep (commit c46cc1c):
[aarch64-unknown-linux-musl]
barracuda = { blake3 = "64c2435...", size = 13840880 }
... (13 entries, x86_64 section GONE)

# After manual restore:
[x86_64-unknown-linux-musl]  ← restored from local binary hashes
... (14 entries)
[aarch64-unknown-linux-musl]
... (13 entries)
```

### Classification

**Upstream cascade failure** — destructive metadata loss propagated through
cascade to all gates. Not caught by cascade conflict auto-resolve because
the sweep was the sole writer (no conflict, just data loss). Severity: P2
(data recoverable from local binaries, but would be P1 if gates relied on
checksums for automated verification without local fallback).

---

## AAR: Post-Primordial Deployment Violation — Local Rebuilds (Wave 105b)

### Incident

During Wave 105, eastGate manually rebuilt bearDog and biomeOS from local source
and deployed them to the local depot, bypassing the post-primordial deployment
standard. This created a divergence between the VPS-authoritative depot (peptidoglycan)
and the local depot.

When commit `64e275e` correctly updated checksums.toml to match the VPS depot (the
authority), all 14 local checksums showed MISMATCH because the local binaries were
ad-hoc rebuilt, not VPS-fetched.

### Root Cause

**The local rebuilds were the violation, not the checksums.** Post-primordial deployment
mandates: peptidoglycan/VPS builds, plasmidBin is the single depot authority, all gates
FETCH from plasmidBin — no local `cargo build --release` for deployment.

### Resolution

1. Stopped all locally-rebuilt NUCLEUS primals
2. Fetched all 13 server binaries from VPS depot (`membrane.primals.eco/depot/`)
3. Verified 13/13 BLAKE3 checksums match VPS authority (sourdough is CLI-only, not on VPS)
4. Restarted NUCLEUS from VPS-fetched binaries — 23 JSON-RPC sockets alive
5. **Local depot is now in sync with VPS authority**

### Post-Primordial Standard (reinforced)

- **DO NOT** `cargo build --release` for deployment on any gate
- **DO** `membrane plasmid.fetch` or `curl` from VPS depot
- **peptidoglycan builds** → plasmidBin checksums → all gates fetch
- Local builds are for development/testing ONLY, never deployed to `plasmidBin/primals/`
- `checksums.toml` always reflects the VPS/peptidoglycan authority

### Classification

Self-inflicted divergence from post-primordial standard. Corrected by re-fetching
from VPS authority. No upstream cascade failure — the checksums were correct.

---

## Ecosystem Snapshot (Wave 105b, Jun 9 2026)

- **Mesh**: ironGate INITIALIZED (port 7700 listening). eastGate↔strandGate 17h+ stable.
- **Transport**: 11/11 non-exempt COMPLETE
- **Depot x86_64**: eastGate local and VPS DIVERGED — checksums represent VPS, not local. Needs resolution.
- **Depot aarch64**: 14/14 built. 6/13 running on Pixel 8 (grapheneGate).
- **WAN depot**: DEPLOYED + VALIDATED (4/5 PASS from flockGate, blocked on VPS songbird relay)
- **grapheneGate**: FIRST DEPLOY — 6/13 primals on Pixel 8, bearDog BTSP production mode LIVE
- **Cascade**: 38/38 synced, zero failures
- **NUCLEUS**: Restarted from local depot (29 JSON-RPC alive after primals went down)
- **P1 blockers**: **ZERO**
- **NEW P2**: CM-DEPOT-DIVERGENCE (inner/outer depot binaries differ, checksums conflict)
- **Sovereignty**: S1-S3 GRADUATED, S4 gate ending today
- **primalSpring**: Wave 105b — grapheneGate deploy, cast safety fixes, 887 tests
