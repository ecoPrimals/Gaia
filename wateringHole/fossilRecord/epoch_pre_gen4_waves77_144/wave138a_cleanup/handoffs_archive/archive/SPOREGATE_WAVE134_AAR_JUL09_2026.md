# sporeGate Wave 134 AAR — Jul 9, 2026

**Gate**: sporeGate | **Waves**: 134b–134f | **Posture**: CONVERGED

## Summary

Full sovereign CI sweep, thin-relay hardening, and WAN dispatch unblocking completed in a single session. sporeGate is fully converged for Wave 134f — all operator tasks resolved, pepti depot current, drawbridge live.

## Completed

### Thin Forgejo Relay (134b)

Evolved golgi's Forgejo from full-history forge to shallow depth=1 relay.

| Metric | Before | After |
|--------|--------|-------|
| Forgejo repos on golgi | 3.8G (40 repos, full history) | 410M (40 repos, depth=1) |
| Total disk used | 6.6G (69%) | 3.2G (34%) |
| Disk freed | — | 3.4G |

- 40/40 repos shallow-swapped (zero failures)
- sporeGate mirror verified 40/40 HEADs match before swap
- Monthly `forgejo-reshallow.timer` deployed on golgi
- `provision-golgi.sh` updated with shallow relay pattern

### Pepti Depot Rebuild (134c–134f)

Full sovereign CI sweep — all 15 binaries rebuilt for both triples.

| Build | Count | Failures |
|-------|-------|----------|
| Initial full sweep | 30/30 | 0 |
| Incremental (bearDog `ddabf6a` + membrane `1be2b7f`) | 4/4 | 0 |
| **Total** | **34 builds** | **0 failures** |

Binaries in depot: barracuda, beardog, biomeos, coralreef, loamspine, membrane, nestgate, nucleus_launcher, petaltongue, rhizocrypt, skunkbat, songbird, sourdough, squirrel, sweetgrass, toadstool.

### WAN-DISPATCH-01 Unblocking (134c–134f)

- Deployed songBird `e5941eeb` (drawbridge auto-advertise) on sporeGate
- Fixed ironGate JupyterHub bind (`127.0.0.1` → `0.0.0.0`)
- Reloaded ironGate UFW (rules were in config but not loaded in iptables)
- flockGate confirmed: **10/10 HTTP 200** through drawbridge (142ms p50)

### Operator Tasks on golgi

| Task | Status |
|------|--------|
| cellMembrane Forgejo bare repo (unpacker error) | Fixed — re-shallowed to `ad4e532`, then to `1be2b7f` |
| sovereign-ci.log permissions | Fixed — `0666` + `/etc/logrotate.d/sovereign-ci` |
| cellMembrane synced to `1be2b7f` (composition lifecycle) | Done |
| bearDog synced to `ddabf6a` (bind-error fix + docs) | Done |
| Checksums regenerated and synced | Done |

### Code Convergence

| Repo | Merged From | Resolution |
|------|-------------|------------|
| cellMembrane | GitHub `65aa790` (composition profiles) | Conflict in `plasmid_dispatch.rs` — kept `dispatch_staleness()` extraction + added `dispatch_composition()` route |
| bearDog | GitHub `ddabf6a` (bind-error fix + docs) | Fast-forward merge |
| wateringHole | Multiple remotes | Resolved `heads/eastGate.toml` conflict (took GitHub/overwatch for bearDog SHA) |

## Divergences for Upstream

### SHALLOW-DIV-01: Merge commits can't push to shallow Forgejo

When a local merge commit references parents from different histories, `git push` to golgi's shallow bare repo fails with `unresolved deltas left after unpacking`. Fast-forward pushes work fine.

**Workaround**: Re-shallow from sporeGate mirror via rsync. For routine cascade/CI workflow (linear commits), this doesn't occur.

**Recommendation**: cellMembrane `temporal.cascade` should detect shallow push failures and auto-reshallow from the sovereign mirror.

### SHALLOW-DIV-02: UFW rules can exist in config but not in iptables

ironGate had `8000/tcp ALLOW 192.168.4.0/22` in `ufw status` but the rule was absent from iptables `ufw-user-input` chain. `ufw reload` fixed it.

**Root cause**: Unknown — possibly added after last `ufw enable` without reload, or Docker iptables interference.

**Recommendation**: Add `ufw reload` to gate provisioning scripts and cascade health checks.

### SHALLOW-DIV-03: Blurb state lag

Overwatch blurbs consistently showed items as "pending" or "next" that were already completed on sporeGate. This is expected given parallel execution, but creates noise.

**Recommendation**: sporeGate should push `heads/sporeGate.toml` updates more frequently so overwatch can read convergence state before drafting blurbs.

## Architecture (Post-134f)

```
sporeGate (Sovereign Warehouse + CI)
├── /opt/forgejo-mirror/: 3.7G (40 repos, full history)
├── /opt/ecoPrimals/depot/: 16 binaries × 2 triples + checksums.toml
├── songBird e5941eeb: drawbridge :7780 + federation :7700
├── Services: songbird-gateway (active), membrane-beardog (active)
└── WireGuard: 10.13.37.2 ↔ flockGate

golgi VPS (Thin Relay)
├── Forgejo: 410M (40 repos, depth=1)
├── pepti depot: 305M (synced from sporeGate)
├── Services: forgejo, caddy-tls, cascade-sense, petaltongue, nestgate, hbbs, hbbr
├── forgejo-reshallow.timer: monthly maintenance
└── Disk: 39% used (5.7G free)
```

## What's Next (not sporeGate)

| Item | Owner | Blocked On |
|------|-------|------------|
| DNS cutover: primals.eco → bearDog ACME TLS | Overwatch | 7-day Caddy shadow period |
| capability.call("jupyter") full protocol pass | songBird team | P2 http.request path bug |
| ironGate full cascade refresh | SSH operator | Physical/SSH access |
| strandGate enrollment | Hardware team | Physical access (house 2) |

---

*Wave 134 — sporeGate CONVERGED. 34 builds, 0 failures. Thin relay live. WAN dispatch unblocked. Depot 100% current.*
