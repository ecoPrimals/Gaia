<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Systemd Templates — Gate Automation

Templates for automating ecosystem tasks on covalent gates.

## cascade-pull

Periodic git pull of all ecosystem repos, driven by `ecosystem_manifest.toml`
and filtered by gate profile.

### Quick Install

```bash
mkdir -p ~/.config/systemd/user

# Copy units
cp cascade-pull.service cascade-pull.timer ~/.config/systemd/user/

# Configure for this gate
cat > ~/.config/cascade-pull.env << 'EOF'
ECOPRIMALS_ROOT=/home/eastgate/Development/ecoPrimals
CASCADE_GATE=eastGate
CASCADE_PARALLEL=8
EOF

# Enable
systemctl --user daemon-reload
systemctl --user enable --now cascade-pull.timer
```

### Gate-Specific Configuration

Edit `~/.config/cascade-pull.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `ECOPRIMALS_ROOT` | (auto-detect) | Workspace root |
| `CASCADE_GATE` | `eastGate` | Gate name from `ecosystem_manifest.toml` |
| `CASCADE_PARALLEL` | `8` | Max concurrent git pulls |

### Monitoring

```bash
# Timer status
systemctl --user list-timers cascade-pull.timer

# Last run logs
journalctl --user -u cascade-pull.service --since today

# Manual trigger
systemctl --user start cascade-pull.service
```

### Comparison with forgejo-sync

| Aspect | `cascade-pull` | `forgejo-sync` |
|--------|----------------|----------------|
| Scope | All 36 repos (filtered by gate) | 6 non-mirror repos |
| Direction | GitHub/Forgejo -> local | GitHub -> Forgejo server |
| Location | Any gate | ironGate only |
| Manifest | `ecosystem_manifest.toml` | Hardcoded in script |
| Freshness | `freshness.toml` drift detection | None |

Both can coexist. `forgejo-sync` keeps Forgejo mirrors current; `cascade-pull`
keeps local gate workspaces current.
