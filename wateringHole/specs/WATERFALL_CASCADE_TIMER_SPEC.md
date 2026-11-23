# WaterFall Cascade Timer Activation Spec (Phase A)

**Date**: Aug 7, 2026 | **Wave**: 157a | **Author**: eastGate overwatch
**Status**: ACTIVATION SPEC — ready for sporeGate gate team
**Predecessor**: `infra/whitePaper/waterFall/05_IMPLEMENTATION.md`

---

## Purpose

Activate autonomous `membrane temporal.cascade` on sporeGate (sync_mediator).
This replaces the manual `git fetch` loop that overwatch runs in IDE sessions
on eastGate. The cascade engine is production Rust code in cellMembrane — it
just needs a systemd timer to run it.

**biomeOS Neural API is the how.** The cascade engine invokes a sequence of
capability calls — `temporal.check`, `temporal.classify`, `temporal.sync`,
`impulse.post`, `freshness.publish` — that are routed through the Neural API.
Today these are inline in cellMembrane. Once the sync composition graphs are
materialized (Phase C), the Neural API orchestrates them as composition
graphs, same as it does for rootPulse operations.

---

## What Already Works

All of this is production code in `gardens/cellMembrane/crates/membrane-shadow/src/temporal/`:

| Feature | Status |
|---------|--------|
| `membrane temporal.cascade --gate sporeGate --publish-freshness` | Production |
| Manifest-driven repo list (`ecosystem_manifest.toml`) | Production |
| Temporal sync (fetch all, measure, pull leader, push followers) | Production |
| Divergence policy engine (`merge-ff`, `flag`, `impulse-only`, `agentic`) | Production |
| SYNC impulse auto-fire (`diverge_impulse = true`) | Production |
| Freshness publish (`heads/sporeGate.toml`) | Production |
| `--parallel N` concurrent repos | Production |
| `--dry-run` | Production |
| `potential.sense` auto-trigger after sync | Production |

---

## Systemd Units

### Timer

```ini
# ~/.config/systemd/user/membrane-temporal-cascade.timer
[Unit]
Description=WaterFall cascade — ecosystem temporal sync (qS → wF)

[Timer]
OnBootSec=5min
OnUnitActiveSec=15min
RandomizedDelaySec=60
Persistent=true

[Install]
WantedBy=timers.target
```

### Service

```ini
# ~/.config/systemd/user/membrane-temporal-cascade.service
[Unit]
Description=WaterFall cascade run
After=network-online.target

[Service]
Type=oneshot
ExecStart=%h/Development/ecoPrimals/target/release/membrane temporal.cascade --gate sporeGate --publish-freshness --parallel 4
WorkingDirectory=%h/Development/ecoPrimals
Environment=ECOPRIMALS_ROOT=%h/Development/ecoPrimals
TimeoutStartSec=300
```

### Activation

```bash
systemctl --user daemon-reload
systemctl --user enable --now membrane-temporal-cascade.timer
systemctl --user status membrane-temporal-cascade.timer
```

### Verification

```bash
# Check timer is scheduled
systemctl --user list-timers membrane-temporal-cascade

# Manual trigger
systemctl --user start membrane-temporal-cascade.service

# Check output
journalctl --user -u membrane-temporal-cascade.service --since "5 min ago"

# Verify freshness was published
cat infra/wateringHole/heads/sporeGate.toml | head -10
```

---

## Manifest Config (already in place)

From `infra/wateringHole/ecosystem_manifest.toml`:

```toml
[sync]
divergence_policy = "merge-ff"
push_to_followers = true
push_target = "all"
diverge_impulse = true

[topology.roles]
sync_mediator = "sporeGate"
```

No manifest changes needed. The config is production-ready.

---

## What the Timer Produces

Every 15 minutes, the cascade:

1. Fetches all remotes for all repos in the manifest
2. Classifies drift (converge/diverge/parity) per repo
3. Fast-forwards where possible (`merge-ff` policy)
4. Fires SYNC impulses to `infra/wateringHole/impulses/active/` on divergence
5. Publishes freshness to `infra/wateringHole/heads/sporeGate.toml`
6. Runs `potential.sense` to show pending impulses

**Output locations**:
- `infra/wateringHole/heads/sporeGate.toml` — per-repo HEAD SHAs + deploy status
- `infra/wateringHole/impulses/active/*.toml` — divergence impulses
- `journalctl --user -u membrane-temporal-cascade` — cascade log

---

## Owner

**sporeGate gate team.** This is a gate-ops task: create two systemd user
unit files, enable the timer. No code changes. primalSpring team on eastGate
can validate by checking that `heads/sporeGate.toml` updates autonomously.

---

## Future: Other Gates

Once proven on sporeGate, every NUCLEUS gate should run this timer with its
own `--gate` identity. The cascade is gate-local — each gate senses from its
own perspective and publishes its own `heads/<gate>.toml`. songBird
`mesh.publish` will eventually broadcast these across the mesh (Phase D).

---

*Phase A of overwatch cascade automation. sporeGate runs the timer. Overwatch
reads the outputs (impulses + freshness) instead of pulling repos manually.*
