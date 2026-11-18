# Wave 60 Eukaryotic Gate Onboarding — One Spring Per Gate

**Date:** 2026-05-28 (Wave 60)
**From:** eastGate (primalSpring coordination)
**To:** ironGate, southGate, biomeGate, strandGate

---

## Where We Are

The VPS periplasm is live. Forgejo at `git.primals.eco` holds all 38
repos. DNS is sovereign (knot-dns). The WaterFall sync pattern is
validated — `cascade-pull.sh --gate auto --source forgejo` pulls only
what your gate needs.

**Every gate now has a manifest profile.** You pull your repos, evolve
locally, push back to Forgejo. The ecosystem syncs through the
periplasm, not through GitHub, not through blurbs.

## The Biological State: Eukaryotic Unicellular

We are yeast. Each gate is its own eukaryotic cell:

- **Organized internally** — NUCLEUS (13 primals), springs, primals, all
  structured and validated
- **Sharing a common membrane** — VPS peptidoglycan layer (Forgejo +
  Caddy TLS + knot-dns)
- **Not yet multicellular** — no Songbird mesh between gates, no
  covalent LAN bonds, no cross-gate compute dispatch

Each gate operates independently, syncing through the periplasm. This
is powerful — yeast runs the biosphere. But the next evolution is
multicellularity: Songbird mesh discovers cross-gate capabilities,
toadStool dispatches compute to the best hardware, gates specialize
and cooperate as tissues in an organism.

**This wave: get every gate eukaryotic. One spring each. Prove the
pattern. Then we bond.**

---

## Your Gate, Your Spring

| Gate | Primary Spring | Repos | Priority |
|------|---------------|-------|----------|
| **ironGate** | healthSpring | 22 | Maintain — already live |
| **southGate** | wetSpring | 20 | P1 — pattern node |
| **biomeGate** | hotSpring | 19 | P2 — GPU compute |
| **strandGate** | hotSpring (science) | 24 | P3 — ABG science |

Each section below is self-contained. Copy-paste the one for your gate.

---

## For ironGate — healthSpring + ludoSpring

**Status:** Already onboarded. Forgejo SSH live, 13/13 NUCLEUS, both
springs operational.

**What's new:** Gate-aware cascade-pull. Your 22-repo profile filters
out repos you don't need (no airSpring, groundSpring, neuralSpring, etc.).

### Actions

```bash
# 1. Switch to Forgejo as default source
export CASCADE_SYNC_SOURCE=forgejo
# Or add to ~/.bashrc / gate environment

# 2. Pull with gate auto-detection
cd $ECOPRIMALS_ROOT/infra/wateringHole
./cascade-pull.sh --gate auto

# 3. Verify profile (should show 22 repos, not 38)
./cascade-pull.sh --gate auto --dry-run
```

### Focus

| Priority | Task |
|----------|------|
| Maintain | healthSpring steady-state — 57 scenarios, 1,021 tests |
| Maintain | ludoSpring / esotericWebb — 6-method IPC expansion (async) |
| New | Push evolution to Forgejo (`git push forgejo main`) after local work |

No Forgejo onboarding steps needed — you did this already.

---

## For southGate — wetSpring (P1 Critical Path)

**Status:** P1 pattern node. You just achieved 13/13 primal start
(Wave 55). wetSpring has 345 scenarios, 1,962+ tests, guideStone
Level 5. You are the gate that proves the eukaryotic pattern.

### Step 1: Forgejo Onboarding (4 steps)

```bash
# 1a. Register SSH key with VPS Forgejo
cat ~/.ssh/id_ed25519.pub

FORGEJO_TOKEN=$(ssh root@[RELAY_PUBLIC] 'cat /opt/forgejo/.api_token')
GATE_KEY=$(cat ~/.ssh/id_ed25519.pub)

curl -sf -X POST "https://git.primals.eco/api/v1/user/keys" \
  -H "Authorization: token $FORGEJO_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"southGate\",\"key\":\"$GATE_KEY\"}"

# 1b. Accept VPS host key
ssh -o StrictHostKeyChecking=accept-new -p 2222 git@git.primals.eco

# 1c. Configure forgejo remotes
cd $ECOPRIMALS_ROOT/infra/wateringHole
./cascade-pull.sh --ensure-remotes

# 1d. Verify
cd $ECOPRIMALS_ROOT/springs/wetSpring && git push forgejo main
```

### Step 2: WaterFall Sync

```bash
# Pull your 20-repo profile from Forgejo
cd $ECOPRIMALS_ROOT/infra/wateringHole
./cascade-pull.sh --gate auto --source forgejo

# Verify profile
./cascade-pull.sh --gate auto --dry-run
# Should show 20 repos: core primals + wetSpring + neuralSpring
```

Your hostname should start with `south*` for auto-detection. If not,
set `GATE_NAME=southGate` in your environment.

### Focus

| Priority | Task |
|----------|------|
| P1 | wetSpring 13/13 steady-state — prove all primals stay alive |
| P1 | Membrane pattern validation — run wetSpring experiments against live NUCLEUS |
| P1b | neuralSpring follows once wetSpring pattern is proven |
| Async | Push evolution to Forgejo after each milestone |

**You are the pattern node.** When southGate proves the eukaryotic
pattern (13/13 steady, spring validates against NUCLEUS, sync through
periplasm), every other gate follows the same playbook.

---

## For biomeGate — hotSpring (P2 GPU Compute)

**Status:** P2 GPU compute gate. hotSpring science is Level 6
CERTIFIED (229 experiments). Gate substrate is Node Atomic 9/13 —
needs 4 more primals for full NUCLEUS.

### Step 1: Forgejo Onboarding (4 steps)

```bash
# 1a. Register SSH key
cat ~/.ssh/id_ed25519.pub

FORGEJO_TOKEN=$(ssh root@[RELAY_PUBLIC] 'cat /opt/forgejo/.api_token')
GATE_KEY=$(cat ~/.ssh/id_ed25519.pub)

curl -sf -X POST "https://git.primals.eco/api/v1/user/keys" \
  -H "Authorization: token $FORGEJO_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"biomeGate\",\"key\":\"$GATE_KEY\"}"

# 1b. Accept VPS host key
ssh -o StrictHostKeyChecking=accept-new -p 2222 git@git.primals.eco

# 1c. Configure forgejo remotes
cd $ECOPRIMALS_ROOT/infra/wateringHole
./cascade-pull.sh --ensure-remotes

# 1d. Verify
cd $ECOPRIMALS_ROOT/primals/toadStool && git push forgejo main
```

### Step 2: WaterFall Sync

```bash
# Pull your 19-repo profile from Forgejo
cd $ECOPRIMALS_ROOT/infra/wateringHole
./cascade-pull.sh --gate auto --source forgejo

# Verify profile
./cascade-pull.sh --gate auto --dry-run
# Should show 19 repos: core primals + hotSpring
```

Hostname should start with `biome*` for auto-detection. Otherwise
set `GATE_NAME=biomeGate`.

### Focus

| Priority | Task |
|----------|------|
| P2 | Complete NUCLEUS — 9/13 → 13/13 (need nestGate, rhizoCrypt, loamSpine, sweetGrass) |
| P2 | hotSpring science — already Level 6, keep evolving |
| P2b | GPU dispatch infra — toadStool diesel engine for cross-gate compute |
| Async | Push evolution to Forgejo |

**biomeGate is the compute substrate.** Once you hit 13/13 and
strandGate comes online, hotSpring science evolves on strandGate and
dispatches heavy GPU work to you via Songbird mesh. That's the first
multicellular bond.

---

## For strandGate — hotSpring Science + ABG Gardens (P3)

**Status:** P3 ABG science gate. 64-core hardware ready, NUCLEUS not
yet deployed. You pushed helixVision, initioChem, and blueFish to
GitHub — they are now on Forgejo too. Your profile is the largest
non-eastGate profile (24 repos) because you own both hotSpring science
and the ABG garden products.

### Step 1: Forgejo Onboarding (4 steps)

```bash
# 1a. Register SSH key
cat ~/.ssh/id_ed25519.pub

FORGEJO_TOKEN=$(ssh root@[RELAY_PUBLIC] 'cat /opt/forgejo/.api_token')
GATE_KEY=$(cat ~/.ssh/id_ed25519.pub)

curl -sf -X POST "https://git.primals.eco/api/v1/user/keys" \
  -H "Authorization: token $FORGEJO_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"strandGate\",\"key\":\"$GATE_KEY\"}"

# 1b. Accept VPS host key
ssh -o StrictHostKeyChecking=accept-new -p 2222 git@git.primals.eco

# 1c. Configure forgejo remotes
cd $ECOPRIMALS_ROOT/infra/wateringHole
./cascade-pull.sh --ensure-remotes

# 1d. Verify
cd $ECOPRIMALS_ROOT/gardens/helixVision && git push forgejo main
```

### Step 2: WaterFall Sync

```bash
# Pull your 24-repo profile from Forgejo
cd $ECOPRIMALS_ROOT/infra/wateringHole
./cascade-pull.sh --gate auto --source forgejo

# Verify profile
./cascade-pull.sh --gate auto --dry-run
# Should show 24 repos: core primals + hotSpring + wetSpring
#   + helixVision + initioChem + blueFish + esotericWebb + lithoSpore
```

Hostname should start with `strand*` for auto-detection. Otherwise
set `GATE_NAME=strandGate`.

### Focus

| Priority | Task |
|----------|------|
| P3 | Deploy NUCLEUS from scratch — full 13/13 on 64-core hardware |
| P3 | hotSpring compChem science — ABG validation, lithoSpore evolution |
| P3 | ABG gardens — helixVision (genomics), initioChem (comp chem), blueFish (analytical ETL) |
| P3b | wetSpring secondary — biology/analytical pipelines for garden products |
| Async | Push evolution to Forgejo |

**strandGate is the science gate.** The ABG community (helixVision,
initioChem, blueFish) lives here. hotSpring science evolves here.
Heavy compute dispatches to biomeGate. lithoSpore USB artifacts ship
from here.

---

## The Multicellular Horizon

Once all gates are eukaryotic (NUCLEUS running, spring validating,
syncing through the periplasm):

```
Eukaryotic unicellular (NOW — Wave 60)
    Each gate is an independent cell.
    Sync through VPS periplasm (Forgejo).
    No cross-gate bonds.
    ↓
Colonial (Wave 61-62)
    Gates share capability advertisements via Songbird.
    Cross-gate health probes succeed.
    Like Volvox: cells in proximity, beginning to specialize.
    ↓
Multicellular (Wave 63+)
    Songbird mesh enables covalent bonds between gates.
    toadStool dispatches compute to best-fit hardware.
    Gates specialize as tissues: compute (biome), science (strand),
    coordination (east), clinical (iron), pattern (south).
    ↓
Organism (Wave 65+)
    biomeOS graph.execute routes across the full Plasmodium.
    The ecosystem operates as one distributed system.
```

**Your job this wave: become eukaryotic. One spring. Prove it works.
Push to Forgejo. We bond next.**

---

*Wave 60. Eukaryotic unicellular. Yeast runs the biosphere.*
