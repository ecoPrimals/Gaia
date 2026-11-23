# Thin Forgejo Relay — AAR (Wave 134b)

**Date**: Jul 8, 2026 | **Gate**: sporeGate | **Posture**: SOVEREIGNTY COMPLETE

## Objective

Evolve golgi's Forgejo from full-history forge to shallow relay (depth=1 bare repos), pushing full sovereignty to sporeGate. Free disk space on the constrained 9.7G VPS.

## Results

| Metric | Before | After |
|--------|--------|-------|
| Forgejo repos | 3.8G (40 repos, full history) | 410M (40 repos, depth=1) |
| Total disk used | 6.6G (69%) | 3.2G (34%) |
| Disk free | 2.7G | 6.1G |
| Space recovered | — | **3.4G** |
| Repos swapped | — | 40/40 (zero failures) |

### Top Savings

| Repo | Before | After | Saved |
|------|--------|-------|-------|
| bearDog | 971M | 5M | 966M |
| songBird | 751M | 5M | 746M |
| hotSpring | 738M | 197M | 541M |
| toadStool | 383M | 7M | 376M |
| rustChip | 315M | 1M | 314M |
| sporePrint | 118M | 3M | 115M |
| nestGate | 84M | 4M | 80M |

Note: `hotSpring` remains large (197M) at depth=1 — likely has binary assets in HEAD tree. Investigate separately.

## What Worked

1. **sporeGate mirror was 100% current** — all 40/40 repo HEADs matched golgi Forgejo before the swap. The mirror established in Wave 133b is healthy.

2. **Shallow-swap is atomic and safe** — `git clone --bare --depth=1 file://` + `mv` + `chown` pattern worked for all 40 repos with zero failures.

3. **Forgejo serves shallow bare repos** — `git ls-remote`, `git clone`, and `git push` all work against shallow Forgejo repos. No Forgejo configuration changes needed.

4. **cascade-sense HEAD tracking unaffected** — `git rev-parse HEAD` on shallow bare repos returns correct SHAs. `FORGEJO_REPO_ROOT` freshness logic works unchanged.

5. **Phase 1 quick wins** — 200M recovered from stale backup, journal vacuuming, and btmp truncation before touching repos.

## Divergences for Upstream

### SHALLOW-DIV-01: `git fetch` from shallow remote rejects ref updates

When a developer's local clone fetches from golgi's now-shallow Forgejo, git emits:

```
warning: rejected refs/remotes/origin/main because shallow roots are not allowed to be updated
```

**Impact**: Low. Fresh clones work fine. Existing clones with full history will see this warning but can still push. Workaround: `git remote set-url origin` to use sporeGate mirror or GitHub for full-history pulls.

**Recommendation**: Document that `git.primals.eco` is the relay surface (push target + shallow clone source). Full history is available from sporeGate's mirror or GitHub.

### SHALLOW-DIV-02: `hotSpring` remains large at depth=1

197M even with only HEAD state. Likely has binary assets (datasets, model files) committed directly rather than via LFS. LFS directory on golgi is 4K (unused).

**Recommendation**: `hotSpring` team should audit HEAD tree for large binaries and consider `.gitattributes` + LFS or moving assets to depot.

### SHALLOW-DIV-03: Monthly re-shallow maintenance required

Shallow bare repos accept pushes normally — new commits accumulate on top of the grafted root. Over months, history will grow again. A `forgejo-reshallow.timer` (monthly) has been installed on golgi to re-run the depth=1 clone-swap.

**Recommendation**: Monitor disk growth via `df` in cascade telemetry. If growth rate is high, increase timer frequency.

## Architecture (Post-Implementation)

```
golgi VPS (Thin Relay)
├── Forgejo bare repos: 410M (depth=1, HEAD state only)
├── pepti depot: ~800M (ecobins + checksums)
├── sporePrint: ~3M (Zola site)
├── Caddy + membrane + songBird + bearDog + RustDesk
└── Total: 3.2G of 9.7G (34%)

sporeGate (Sovereign Warehouse)
├── /opt/forgejo-mirror/: 3.7G (all 39 repos, FULL history)
├── /opt/ecoPrimals/depot/: ~800M (source-of-truth ecobins)
├── Development/ecoPrimals/: full source trees
└── Sovereign CI builder
```

Push flow: `developer -> golgi Forgejo (shallow) -> cascade -> sporeGate mirror (full)`
Clone flow: `developer -> golgi Forgejo (HEAD only)` or `sporeGate mirror (full history)`

## Changes Made

1. **Phase 1**: Deleted `/opt/membrane/backup-pre-wave79/` (134M), vacuumed journal to 20M (51M freed), truncated `/var/log/btmp`.
2. **Phase 2**: Fetched all 40 repos on sporeGate mirror from golgi, verified 40/40 HEADs match.
3. **Phase 3**: Stopped Forgejo, shallow-swapped all 40 bare repos (clone depth=1 + mv + chown), restarted Forgejo. 3.4G saved.
4. **Phase 4**: Validated `git ls-remote`, `git clone`, `git push`, and cascade HEAD tracking all work.
5. **Phase 5**: Updated `provision-golgi.sh` with shallow relay documentation, `forgejo-reshallow` script, and monthly timer. Installed timer on live golgi.

## Files Modified

- `provision/provision-golgi.sh` — Added shallow relay documentation, `forgejo-reshallow` maintenance script + timer, updated disk estimates
- `/usr/local/bin/forgejo-reshallow` (on golgi) — Monthly maintenance script
- `/etc/systemd/system/forgejo-reshallow.{service,timer}` (on golgi) — Systemd units for periodic re-shallowing

## Risks Monitored

- **Forgejo internal repack**: Forgejo may run its own GC/repack that partially defeats shallowing. The monthly timer mitigates this.
- **Push to shallow repo**: Tested and confirmed working. New commits land on the grafted root.
- **Cascade freshness**: Unaffected — reads `HEAD` from bare repo, doesn't need history.

---

*Wave 134b — golgi is now a true thin relay. 3.8G -> 410M. sporeGate holds full sovereignty. Monthly re-shallow timer armed.*
