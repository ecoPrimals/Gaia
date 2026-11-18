# Depot Pipeline Divergences — Build → golgi → Gate Deployment

**Date**: Aug 3, 2026 | **Wave**: 155p/156a | **From**: eastGate overwatch (sporeGate)
**Purpose**: Inventory all divergences in the build-to-deployment pipeline as we scale
from ad-hoc single-gate updates to routine multi-gate deployment.

---

## Pipeline Overview (Current State)

```
 Source (Forgejo)          sporeGate                    golgi VPS               Gate
 ┌──────────┐   manual   ┌──────────────┐   manual    ┌───────────┐   manual  ┌─────────┐
 │ git push │──cascade──→│ git pull      │──harvest──→│ depot.    │──fetch──→│ plasmid │
 │          │   pull     │ plasmid.      │──push────→│ primals.  │          │ .fetch  │
 │          │            │ harvest       │            │ eco       │          │         │
 └──────────┘            │ --local       │            │           │          │ NUCLEUS │
                         │ --all         │            │ checksums │          │ restart │
                         │ --force       │            │ .toml     │          │         │
                         └──────────────┘            └───────────┘          └─────────┘
                           ↓ copy                       ↕ HTTPS
                         /opt/depot/                  depot.primals.eco
                         NUCLEUS restart
```

**Every arrow is manual.** 6 operator steps for a full deploy cycle.

---

## Divergences (CI-DIV Series)

### CI-DIV-01: `staleness` vs `status` Disagree on Drift

**Observed**: After overnight primal changes, `plasmid.staleness` reports 13/13 current
while `plasmid.status` reports 9/13 drifted.

**Root cause**: Two different detection algorithms:

| Command | Method | What It Checks |
|---------|--------|----------------|
| `plasmid.staleness` | Local-only (`detect_stale_primals`) | Binary exists + provenance has a commit. **Does NOT compare commits.** |
| `plasmid.status` | Network (`has_upstream_changes_lenient`) | `git ls-remote HEAD` on Forgejo/GitHub vs provenance commit. |

`staleness` only flags a primal as stale if the binary is missing or provenance has
no commit at all. It never detects commit drift — a primal built at commit `abc123`
with source now at `def456` shows as "current."

**Impact**: Operators using `staleness` to decide if a rebuild is needed will miss all
drift. Only `status` catches real drift, but it requires network access.

**Fix**: `detect_stale_primals` should compare `provenance_commit` against local source
HEAD (`git rev-parse --short HEAD` in the local source dir) when `ECOPRIMALS_ROOT`
points to a workspace. This would make staleness detect drift locally without network.

### CI-DIV-02: `ECOPRIMALS_ROOT` Not Set on sporeGate

**Observed**: `plasmid.harvest --local` fails with "primal not found in ecosystem
manifest" because the default `ECOPRIMALS_ROOT` is `/opt/ecoPrimals` (VPS path).
sporeGate's workspace is at `/home/sporegate/Development/ecoPrimals`.

**Impact**: Every harvest invocation requires the operator to prefix with
`ECOPRIMALS_ROOT=/home/sporegate/Development/ecoPrimals`.

**Fixed** (Aug 3): Added `export ECOPRIMALS_ROOT=...` to `~/.bashrc`.

**Remaining fix**: Have `membrane` auto-detect workspace from `git rev-parse --show-toplevel`
ancestry, or add `ecoprimals_root` to `membrane.toml` config (persistent, portable).

### CI-DIV-03: Four Depot Paths Coexist (Corrected)

**Observed**: Four separate depot directories exist on sporeGate:

| Path | Purpose | Updated By |
|------|---------|------------|
| `$ECOPRIMALS_ROOT/infra/plasmidBin/` | Harvest writes here | `plasmid.harvest` |
| `~/.local/share/ecoPrimals/plasmidBin/` | NUCLEUS services read from here | `plasmid.refresh` / manual |
| `/opt/depot/` | Legacy (was manually copied to) | Manual `cp` |
| `/opt/ecoPrimals/plasmidBin/` | Default VPS path (`depot_sync` reads) | VPS deploys |

NUCLEUS systemd units point to `~/.local/share/ecoPrimals/plasmidBin/primals/{target}/`.
Harvest writes to `infra/plasmidBin/`. No automated sync between them. Operator must:
stop NUCLEUS → atomic copy (cp to .new, mv) → start NUCLEUS. Direct `cp` fails with
"Text file busy" even after `systemctl stop` (lingering processes).

**Impact**: After harvest, operator must manually copy to the correct install path AND
do a clean stop (pkill lingering processes) before overwriting.

**Fix**: `plasmid.harvest --with-restart` should: stop NUCLEUS → atomic install from
harvest depot to NUCLEUS install dir → start NUCLEUS → verify health.

### CI-DIV-04: membrane Binary Not in Harvest Cycle

**Observed**: `membrane` depot binary is from Jun 21 (42 days old). The harvest cycle
builds all 13 primals but does NOT build `membrane` itself. The `membrane` binary in
`~/.local/bin/` is at `d350601` (current HEAD), but the depot copy is stale.

**Impact**: Gates fetching from depot get an old `membrane`. New shadow functions,
pipeline improvements, and bug fixes don't propagate.

**Fix**: Add `membrane` (cellMembrane) to the harvest cycle. Needs careful staging —
can't replace a running binary. Build + stage, then swap + restart on next cycle.

### CI-DIV-05: Silent Manifest Parse Failure

**Observed** (Aug 2): `steamGate.mobility = "portable"` caused the entire
`ecosystem_manifest.toml` to fail TOML parsing. The `resolve_local_source_dir` function
uses `if let Ok(manifest)` which silently falls through to "not found."

**Impact**: A single invalid field in any gate's config silently breaks `--local`
harvest for ALL primals. No error message indicates the manifest failed to parse.

**Fixed**: Changed `"portable"` → `"mobile"`. But the silent failure pattern remains.

**Fix**: `resolve_local_source_dir` should log a warning when `load_from_workspace`
returns `Err`, not silently fall through.

### CI-DIV-06: No Webhook/Auto-Trigger

**Observed**: The entire harvest→push→deploy cycle is operator-initiated. No Forgejo
webhook fires when a primal pushes new code. The operator must notice drift, decide
to rebuild, and run the commands.

**Impact**: Depot staleness grows silently. Yesterday we found 40-day-old binaries.
As more gates depend on fresh depot builds, manual triggers become a bottleneck.

**Fix**: Forgejo push webhook → sporeGate → `plasmid.harvest --primal <changed>` →
`plasmid.push` → mesh notification to gates. The `webhook.test` shadow function
exists but isn't wired to Forgejo.

### CI-DIV-07: No Push Notification to Gates

**Observed**: After `plasmid.push` updates the golgi depot, downstream gates have no
way to know new binaries are available. Each gate must manually run `plasmid.fetch`
or `plasmid.auto_fetch`.

**Impact**: Gates run stale binaries indefinitely until an operator notices.

**Fix**: After depot push, songBird `mesh.publish` should notify all online gates.
The `auto_fetch` mechanism exists but depends on mesh notification delivery.
The WARN in yesterday's harvest (`mesh.publish depot.updated failed`) shows this
path exists but isn't reliable.

### CI-DIV-08: Cross-Target Builds Only musl

**Observed**: Harvest only builds `x86_64-unknown-linux-musl`. The golgi depot has
some `x86_64-unknown-linux-gnu` binaries (from a previous manual build) but they're
stale. No `x86_64-pc-windows-gnu` or `aarch64-unknown-linux-musl` builds.

**Impact**:
- GPU primals (barraCuda, coralReef, toadStool) need `gnu` target for CUDA `dlopen`
- blueGate needs `windows-gnu` target (J12 sub-builder)
- grapheneGate needs `aarch64` target

**Fix**: Multi-target harvest: `--target x86_64-unknown-linux-musl,x86_64-unknown-linux-gnu`
for GPU primals. Windows via J12 dispatch. aarch64 via cross-compile or dedicated builder.

### CI-DIV-09: NUCLEUS Restart Not in Pipeline

**Observed**: After harvest + copy, operator must manually
`sudo systemctl restart membrane-nucleus.target`. No automated restart.

**Impact**: New binaries sit in depot without being loaded until manual restart.

**Fix**: `plasmid.harvest --with-restart` flag exists in the help text. Wire it to
automatically restart NUCLEUS after successful harvest + install. Add health check
after restart to verify all services came up clean.

### CI-DIV-10: Dry-Run Doesn't Test `--local` Path

**Observed** (Aug 2): `plasmid.harvest --primal beardog --local --dry-run` passed
but the actual build failed. Dry-run exits before calling `resolve_local_source_dir`.

**Impact**: Dry-run gives false confidence. Can't validate `--local` path without
actually building.

**Fix**: Dry-run should still resolve the local source directory (test that the
manifest parses, the local_path exists, etc.) before reporting "would build."

---

## Priority for Multi-Gate Deployment

As we move to deploying across ironGate, biomeGate, strandGate routinely:

| Priority | Divergence | Impact | Effort | Status |
|----------|-----------|--------|--------|--------|
| **P1** | CI-DIV-02: ECOPRIMALS_ROOT | Blocks every harvest | 5 min | **RESOLVED** (bashrc) |
| **P1** | CI-DIV-03: Four depot paths | Split-brain risk | 2h | **RESOLVED** (`--with-restart`) |
| **P1** | CI-DIV-01: staleness vs status | False "current" reports | 2h | **RESOLVED** (drift detection) |
| **P2** | CI-DIV-04: membrane not harvested | Stale tooling on gates | 2h | **RESOLVED** (manual rebuild + depot push) |
| **P2** | CI-DIV-05: Silent parse failure | One bad field breaks all | 30 min | **RESOLVED** (warning log) |
| **P2** | CI-DIV-08: Cross-target builds | GPU primals need gnu | 1h | **PARTIAL** (blueGate sub-builder proven E2E) |
| **P2** | CI-DIV-09: NUCLEUS restart | Manual step easy to forget | 1h | **RESOLVED** (`--with-restart`) |
| **P3** | CI-DIV-06: No webhook trigger | Manual bottleneck | 4h | **RESOLVED** (git hooks + Caddy + UDS listener) |
| **P3** | CI-DIV-07: No gate notification | Gates run stale | 2h | OPEN |
| **P3** | CI-DIV-10: Dry-run incomplete | False confidence | 1h | **RESOLVED** (validates --local path) |

---

## Current Pipeline Metrics

| Metric | Value |
|--------|-------|
| Full harvest time | 33.5 min (13 primals, musl, LTO) |
| Push to golgi | 48 sec (16 binaries, ~165 MB) |
| Operator steps per deploy | 6 (pull, set env, harvest, copy, restart, push) |
| Time since last depot rebuild | 1 day (previously 40 days) |
| Primals currently drifted | 10/13 (overnight changes) |
| Cross-target coverage | 1/4 targets |
| Gates auto-notified on update | 0 |

---

*10 divergences documented. **9/10 resolved** (Aug 3, 2026). Remaining: CI-DIV-07
(gate notification via mesh.publish — P3). blueGate sub-builder E2E proven. golgi
post-receive hooks evolved to use harvest scheduler (CI-EVO-01). Caddy → UDS webhook
listener deployed as systemd service. CI-DIV-08 partial: blueGate windows-gnu
sub-builder proven, multi-target in scheduled pipeline pending.*
