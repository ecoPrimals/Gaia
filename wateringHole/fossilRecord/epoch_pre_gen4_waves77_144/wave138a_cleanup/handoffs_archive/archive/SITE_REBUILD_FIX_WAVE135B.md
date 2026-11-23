# HANDOFF: sporePrint Site Rebuild Fix (Wave 135b)

**Priority**: P1 — site not updating since DNS cutover
**Owner**: sporeGate/golgi team
**Date**: Jul 9, 2026

---

## Problem

sporePrint source changes pushed to Forgejo are pulled by `cascade-sense.timer`
on golgi, but the static site (`/opt/ecoPrimals/sporePrint/public/`) is never
rebuilt. Caddy serves stale HTML.

**Root cause**: No `zola build` step exists in the golgi cascade pipeline.

## Fix (two options)

### Option A: Update membrane binary (recommended, zero config)

The latest cellMembrane (`be276dd+`) now auto-rebuilds sporePrint after cascade
if `config.toml` exists and `zola` is on PATH. Deploy the new membrane binary:

```bash
# On sporeGate — build latest membrane
cd /opt/ecoPrimals/gardens/cellMembrane
git pull origin main
cargo build --release -p membrane-shadow
strip target/release/membrane

# Deploy to golgi
scp target/release/membrane golgi:/opt/membrane/membrane
ssh golgi 'cp /opt/membrane/membrane /usr/local/bin/membrane'
```

Then ensure Zola is installed on golgi:

```bash
ssh golgi 'apt-get install -y zola || cargo install zola'
```

After next cascade cycle (≤15 min), the site auto-rebuilds.

### Option B: Immediate manual fix (while waiting for deploy)

```bash
ssh golgi 'cd /opt/ecoPrimals/infra/sporePrint && zola build'
```

This immediately regenerates `public/` from current source.

### Option C: Add ExecStartPost (if membrane deploy is delayed)

Edit cascade-sense.service to chain a Zola build:

```bash
ssh golgi 'cat >> /etc/systemd/system/cascade-sense.service.d/zola.conf << EOF
[Service]
ExecStartPost=/bin/sh -c "cd /opt/ecoPrimals/infra/sporePrint && zola build 2>/dev/null || true"
EOF
systemctl daemon-reload'
```

## Verification

After any fix:
```bash
curl -s https://primals.eco | grep -o '<title>.*</title>'
# Should reflect latest sporePrint content
```

## Architecture Note

cellMembrane's `content.rebuild` command can also be called explicitly:
```bash
membrane content.rebuild
```

The auto-rebuild in cascade is silent-skip if Zola is not installed (non-content
gates like ironGate won't be affected). It runs unconditionally on each cascade
because Zola is fast (sub-second for unchanged content).
