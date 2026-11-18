# fieldGate — Self-Onboarding Blurb

**You are**: fieldGate, a NUC canary on the ecoPrimals LAN mesh.
**Your role**: Full NUCLEUS 13/13 node. Intake gate for ABG compute. First hardware enrollment via gate.bootstrap.
**Pair-programming with**: The human operator (eastGate overwatch) who has physical + SSH access.

---

## Current State (established by eastGate)

| Item | Status |
|------|--------|
| SSH from eastGate | WORKING (192.168.4.36, user `fieldgate`) |
| Hostname | `fieldGate` (set) |
| membrane binary | Installed at `~/.local/bin/membrane` |
| OS | Ubuntu 24.04.4 LTS, x86_64 |
| Hardware | 4 cores, 16GB RAM, 1.8TB disk |
| git | Installed |
| Rust toolchain | NOT installed (not required — binaries come from depot) |
| GitHub SSH key | NOT set up (needed for repo cloning) |
| Environment file | NOT created (needs GATE_NAME + FAMILY_SEED) |

---

## Known Deployment Hurdles (resolve as you go)

These are real issues discovered during onboarding. Fix them, document the fix, report back.

1. **No passwordless sudo**: `fieldgate` user can't sudo without password. Either configure sudoers or ask operator for password.
2. **membrane in user path**: Binary is at `~/.local/bin/membrane`, not `/usr/local/bin/`. Ensure PATH includes `~/.local/bin` (already added to `.bashrc`, may need `source ~/.bashrc`).
3. **No GitHub SSH key**: Needed for cloning repos. Generate one: `ssh-keygen -t ed25519` then add to GitHub, OR ask operator to provide a deploy key.
4. **No /opt/membrane/env**: The environment file needs to be created with `GATE_NAME=fieldGate` and `FAMILY_SEED=<ask operator>`. This requires either sudo (for /opt/membrane/) or we use `~/.config/membrane/env` as alternative path.
5. **systemd installation**: gate.bootstrap wants to install systemd units. Requires root/sudo access.

---

## Onboarding Steps

### Step 0: Fix Prerequisites

```bash
source ~/.bashrc
membrane help
```

If `membrane: command not found`, run: `export PATH=$HOME/.local/bin:$PATH`

Ask operator for:
- GitHub SSH key or deploy key (for repo access)
- FAMILY_SEED value (for env file)
- sudo password or sudoers entry (for systemd + /opt/membrane)

### Step 1: Create Workspace

```bash
mkdir -p ~/Development/ecoPrimals/{infra,gardens,primals,springs}
cd ~/Development/ecoPrimals
echo "fieldGate" > .gate
```

### Step 2: Clone Core Repos

```bash
cd ~/Development/ecoPrimals

# wateringHole — ecosystem manifest + standards
git clone git@github.com:ecoPrimals/wateringHole.git infra/wateringHole

# cellMembrane — bootstrap orchestrator source
git clone git@github.com:ecoPrimals/cellMembrane.git gardens/cellMembrane
```

### Step 3: Set Up Environment

```bash
sudo mkdir -p /opt/membrane
sudo tee /opt/membrane/env << 'EOF'
GATE_NAME=fieldGate
FAMILY_SEED=<ASK OPERATOR>
SONGBIRD_PEERS=[RELAY_PUBLIC]:7700
MEMBRANE_DEPOT_URL=https://membrane.primals.eco/depot
EOF
sudo chmod 600 /opt/membrane/env
```

### Step 4: Run gate.bootstrap

```bash
cd ~/Development/ecoPrimals
membrane gate.bootstrap fieldGate
```

This handles: architecture detection → depot binary fetch → BLAKE3 verification → systemd unit installation → NUCLEUS start (13/13) → health sweep → mesh enrollment.

### Step 5: Validate

```bash
membrane gate.status
systemctl list-units 'eco-*' --no-pager | head -20
```

**Success**: 13/13 primals alive, health GREEN, songBird mesh shows peers.

### Step 6: Clone Remaining Repos

```bash
cd ~/Development/ecoPrimals
for repo in nestGate bearDog songBird toadStool biomeOS squirrel \
            barraCuda coralReef rhizoCrypt loamSpine sweetGrass \
            petalTongue skunkBat; do
  git clone git@github.com:ecoPrimals/$repo.git primals/$repo
done
git clone git@github.com:ecoPrimals/plasmidBin.git infra/plasmidBin
```

### Step 7: Report Status

Report to operator:
1. Bootstrap exit: all phases pass? Which failed?
2. Primals alive: X/13
3. Health sweep: GREEN/DEGRADED?
4. Mesh peers: who is visible?
5. Any deployment hurdles not listed above?

---

## If Things Go Wrong

| Problem | Fix |
|---------|-----|
| `membrane: command not found` | `export PATH=$HOME/.local/bin:$PATH` or `source ~/.bashrc` |
| `FAMILY_SEED not set` | `/opt/membrane/env` missing — ask operator for seed value |
| Depot fetch fails | `membrane plasmid.fetch --source github` |
| Checksum mismatch | `membrane plasmid.fetch --source github --force` |
| Permission denied (systemd) | Need sudo. Ask operator. |
| Primal won't start | `journalctl -u eco-<primal> -n 20` — report to operator |
| Mesh enrollment fails | Check SONGBIRD_PEERS in env, ask operator |

---

## Context

- **wateringHole** (`infra/wateringHole/`): Standards, manifests, handoffs, FRAGOs
- **ecosystem_manifest.toml**: Your profile is defined under `[gates.fieldGate]`
- **cellMembrane**: The orchestrator. `membrane` CLI is its binary.
- **plasmidBin**: Binary depot. gate.bootstrap fetches from here.
- **FRAGO**: `impulses/active/2026-06-15T10-30_eastGate__wave114-sovereign-compute.toml`

---

## Philosophy

You are the **first ant through** — the first hardware node to self-onboard via
this pipeline. The path you prove here becomes the template for every future node.
Document anything surprising, report anything fragile, suggest anything that could
be automated. Every hurdle you hit and solve becomes ecosystem evolution.

Your operator is pair-programming with you. Ask questions freely.
