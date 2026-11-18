# Cascade Topology — Push via Pepti Hub

**Date**: Jun 19 2026 | **From**: eastGate overwatch
**Problem**: Gates need individual SSH keys on Forgejo to push directly. Fragile, doesn't scale.
**Solution**: Gates push to **pepti** (build authority), pepti syncs bidirectionally to GitHub + Forgejo.

---

## Model: Pepti as Cascade Hub

```
                    ┌─────────────┐
                    │   GitHub    │ (public mirror)
                    └──────▲──────┘
                           │ push (pepti → github)
                    ┌──────┴──────┐
      ┌────────────►│    pepti    │◄────────────┐
      │  push       │ (hub, VPS)  │   push      │
      │             └──────┬──────┘             │
      │                    │ push (pepti → forgejo)
      │             ┌──────▼──────┐             │
      │             │   Forgejo   │             │
      │             │ (git.primals.eco)         │
      │             └─────────────┘             │
      │                                         │
 ┌────┴────┐   ┌──────────┐   ┌──────────┐  ┌──┴───────┐
 │sporeGate│   │ eastGate │   │flockGate │  │ ironGate │
 │  (LAN)  │   │  (LAN)   │   │  (WAN)   │  │  (LAN)   │
 └─────────┘   └──────────┘   └──────────┘  └──────────┘
```

**Flow**:
1. Gate commits locally
2. Gate pushes to pepti via SSH (one key per gate, pepti accepts all)
3. pepti post-receive hook pushes to Forgejo + GitHub
4. Other gates pull from pepti (or Forgejo/GitHub)

---

## Why Pepti

- Already the **build authority** (depot, fresh binaries)
- Has SSH keys on GitHub + Forgejo already
- Reachable by all gates: LAN gates via 192.168.4.x or WG 10.13.37.4, WAN gates via WG
- Single point of key management — add a gate's pubkey to pepti once, done
- Bidirectional: pepti also pulls from GitHub/Forgejo (external contributors)

---

## Setup Per Gate

Each gate needs ONE thing: its SSH pubkey added to pepti's `authorized_keys`.

```bash
# On the gate (generate key if needed):
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N "" -C "<gatename>-cascade"

# Send pubkey to pepti (any gate with pepti access can do this):
ssh root@10.13.37.4 "echo '$(cat ~/.ssh/id_ed25519.pub)' >> /home/git/.ssh/authorized_keys"

# Set remote on the gate's repo:
git remote set-url origin ssh://git@10.13.37.4:2222/ecoPrimals/<repo>.git
# OR if pepti uses standard SSH:
git remote set-url origin git@10.13.37.4:/srv/git/ecoPrimals/<repo>.git
```

---

## Pepti Post-Receive Hook (syncs upstream)

On pepti, each bare repo gets a post-receive hook:

```bash
#!/bin/bash
# /srv/git/ecoPrimals/<repo>.git/hooks/post-receive
# Triggered after any push to pepti

REPO_NAME=$(basename "$PWD" .git)

# Push to Forgejo
git push forgejo main 2>/dev/null || true

# Push to GitHub
git push github main 2>/dev/null || true

echo "CASCADE: $REPO_NAME synced to forgejo + github"
```

---

## Git Identity Per Gate

Gates use their own identity (no shared accounts):

| Gate | Name | Email |
|------|------|-------|
| eastGate | eastGate Developer | eastgate@primals.eco |
| sporeGate | sporeGate Overwatch | sporegate@primals.eco |
| flockGate | flockGate Team | flockgate@primals.eco |
| ironGate | ironGate Compute | irongate@primals.eco |
| BiomeOS (primals) | BiomeOS Developer | biome@biomeos.net |

Each gate sets its own `git config user.name` and `user.email` locally.
Commits are attributed to the gate that made them. SweetGrass tracks braids.

---

## Migration Path

1. **pepti**: Create bare repos or mirror existing ones. Add post-receive hooks.
2. **Each gate**: Generate SSH key, send pubkey to pepti, set pepti as origin.
3. **Verify**: Push from gate → appears on Forgejo + GitHub within seconds.
4. **Keep Forgejo direct** as fallback: Gates that already have Forgejo keys keep them.
   Pepti hub is the recommended path but not exclusive.

---

## What This Fixes

- No more "need SSH key for every gate on Forgejo" fragility
- Gates can push immediately after enrollment (just need pepti key auth)
- Bidirectional: pepti pulls from GitHub too (external PRs cascade in)
- Single key management point scales to N gates
- Attribution preserved per gate (SweetGrass commit braids)
- Robust: if pepti is down, gates still commit locally and push when restored

---

## Immediate Action (sporeGate cellMembrane team)

1. Fix pepti SSH→forgejo (existing P0 blocker)
2. Set up bare repos on pepti for primal repos that teams are pushing to:
   - `loamSpine`, `sweetGrass`, `skunkBat`, `bearDog`, `songbird` (Tower primals on flockGate)
   - `cellMembrane`, `wateringHole` (already working)
3. Add flockGate + sporeGate pubkeys to pepti `authorized_keys`
4. Wire post-receive hooks for bidirectional sync

Once done: all 4 gates push freely through pepti hub. No more key fragility.
