> **SUPERSEDED (Wave 157i)** — This Wave 155n/157a template is replaced by a three-tier system:
> 1. **Gate hardware agents**: Use `GATE_SPINUP_BLURB.md` (universal, platform-adaptive).
> 2. **Code team agents**: Use K-NOME Blurb 1 (audit) + Blurb 2 (execute) from personal prompt bank.
> 3. **Ecosystem overwatch**: Use `ECOSYSTEM_BLURB.md`.
>
> This file is retained as historical reference.

# Team Startup Blurb — Wave 157a (Primals Stable → Springs Phase)

**From**: eastGate overwatch
**Purpose**: Paste this into any new IDE session on any gate. It bootstraps
the gate through four phases: connectivity → sync → enrollment → work.

**Two audiences**:
- **Gate teams**: Phases 0–2 (connectivity, sync, enrollment). Deploy NUCLEUS on hardware.
- **Code teams**: Phases 0–1 (connectivity, sync), then Phase 3 (primal/spring/garden work). Build ON the primals.

**Four-phase flow**:
0. **Connectivity**: SSH config for Forgejo (NO WireGuard needed — Forgejo is public)
1. **Sync**: Pull all repos from Forgejo, fix naming divergences, clone missing repos
2. **Enrollment**: WireGuard mesh + Tower Atomic — **GATE TEAMS ONLY** (required for primal IPC, not for code)
3. **Work**: Team-specific tasks — **CODE TEAMS** or **GATE TEAMS**

---

## PHASE 0: CONNECTIVITY — Forgejo Access

Forgejo (`git.primals.eco`) runs on golgiBody, a **public VPS**. You do NOT
need WireGuard to access it. WireGuard is only needed later for inner membrane
primal IPC. There are two access methods:

### Option A: HTTPS (zero-config, read-only — start here)

All ecoPrimals repos are public. HTTPS clone/pull works immediately with
**no SSH key, no config, no registration**:

```bash
git clone https://git.primals.eco/ecoPrimals/bearDog.git primals/bearDog
```

Use this for initial sync if SSH isn't set up yet. You can repoint to SSH later
when you need push access (only needed for wateringHole handoffs per convergence rule).

### Option B: SSH (read + write — set up when needed)

SSH gives push access for filing handoffs. Port 2222 is open to the internet.

**Step 0b-1: Add host key**

```bash
ssh-keyscan -p 2222 git.primals.eco >> ~/.ssh/known_hosts 2>/dev/null
```

**Step 0b-2: SSH config** — add to `~/.ssh/config` (create if missing):

```
Host forgejo git.primals.eco
    HostName git.primals.eco
    Port 2222
    User git
    IdentityFile ~/.ssh/id_ed25519_ecoPrimal
```

If you don't have `id_ed25519_ecoPrimal`, generate one:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_ecoPrimal -C "$(hostname)@primals.eco"
```

Then register the public key in Forgejo: `https://git.primals.eco` → Settings →
SSH/GPG Keys → Add Key. Or ask eastGate overwatch to register it as a deploy key.

**Step 0b-3: Verify**

```bash
ssh -T git@git.primals.eco
# Should return: "Hi <user>! You've successfully authenticated..."
```

If this fails with "Permission denied", your SSH key isn't registered in Forgejo.
Use HTTPS (Option A) for now — you can pull everything read-only and set up SSH
later when you need push access.

---

## PHASE 1: SYNC — Pull All Repos

### What is ecoPrimals

ecoPrimals is a sovereign, AGPL-3.0 mesh operating system built in pure Rust.
13 primals (autonomous binaries) compose into **atomics**: Tower (security +
discovery + defense), Node (Tower + compute), Nest (Tower + storage +
provenance), and NUCLEUS (all 13). biomeOS orchestrates via a Neural API
with 27 signal graphs and semantic dispatch (`tower.health`, `node.compute`,
`nest.store`, etc.). biomeOS is the **composition broker** — it propagates
BTSP trust and riboCipher framing across atomic boundaries. All binaries
("genomeBins") are served from a single depot on golgiBody
(`https://depot.primals.eco`). Gates are physical machines running Tower
Atomic or higher compositions.

### Current State (Wave 157a — Aug 7, 2026)

**Posture**: STAGE 2 CODE TEAM HANDOFF. G64+G65+G66 COMPLETE (cephalization trilogy).
Forwarding fix shipped (G67 N1). Neural API is the routing substrate — Stage 1 (direct
socket) is now primordial. Two parallel code teams on eastGate: primalSpring (N2-N5
activation) + biomeOS (routing infrastructure). 15 glacial goals COMPLETE.

| Fact | Value |
|------|-------|
| Wave | **157a** — Stage 2 Neural API activation |
| Primals | 15 (13 active + 2 dormant). **G64+G65+G66 COMPLETE.** All cephalized. |
| Tests | **~140K+** across 15 primals |
| biomeOS | **v4.57+** — G65 protocol negotiation, G67 forwarding fix (`ffed2c5b`). 456 Neural API tests. |
| BTSP | 15/15 — all primals ship bearDog ClientHello |
| Depot | **52 builds** (16 musl + 15 gnu + 15 windows + aarch64). BLAKE3 verified. blueGate primary builder. |
| Gates | **6 NUCLEUS** (westGate, strandGate, blueGate, sporeGate, southGate, **ironGate**). G17+G8 PROVEN. |
| Cephalization | **G64 COMPLETE** — tarpc convergent evolution 15/15 |
| Protocol | **G65 COMPLETE** — single-socket dual-protocol 15/15 |
| Transport | **G66 COMPLETE** — silicon-agnostic IPC 15/15, cross-arch 15/15 |
| Neural API | **G67 ACTIVE** — N1 forwarding fix shipped, N2-N6 pending |
| Sovereign CI | **LIVE** — push-to-deploy for ALL 13 primals. blueGate primary builder. |
| Provenance | **7/7 COMPLETE** — E2E on Linux + Windows |
| Forgejo | `ssh://git@git.primals.eco:2222/` — canonical remote (PUBLIC) |
| P0/P1/P2 | **ZERO** |
| Glacial goals | **63 tracked** (15 COMPLETE / 25 ACTIVE / 23 GLACIAL) |

### Gate-Team Assignments

| Gate | Role | Hardware | Status |
|------|------|----------|--------|
| **eastGate** | Overwatch + code teams | i9-12900K, **64 GB DDR5**, Z790-P WIFI, 10G SFP+ | ONLINE. primalSpring + biomeOS code teams. |
| **westGate** | Data NAS + Nest workhorse | Ryzen 7 5700X, 64GB, ZFS raidz1 50.7TB | **NUCLEUS v4.57.** 3.21 TB / 153 datasets / 452 GB CAS. |
| **strandGate** | Node Atomic + QCD compute | Dual EPYC 7452, RTX 3090 + RX 6950 XT | **NUCLEUS v4.57+.** hotSpring SU(N). Config memoization. |
| **sporeGate** | CI + membrane + depot | Full NUCLEUS, Sovereign CI | Depot 17/17 musl. nestgate.io. |
| **blueGate** | Windows primary builder | Windows, house2, 10G backbone | **NUCLEUS v4.57+.** 15/15 Windows builds. Sub-builder. |
| **ironGate** | Downstream host | i9-14900K, RTX 5070, 94 GB, 14TB HDD | **NUCLEUS 13/13.** G18 LIVE. esotericWebb + footPrint. |
| **southGate** | Validation gate (G17+G8 PROVEN) | 5800X3D + RTX 4060 + 128GB + 5TB NVMe | **NUCLEUS 13/13.** No WG. Own family. Re-validated. |
| **biomeGate** | GPU crankshaft + agentic | Threadripper 3970X, 128GB, 3 VFIO GPUs | GPU LAB. coralReef 3,553 tests. 44-experiment matrix. |
| **golgiBody** | Depot, Forgejo, enrollment, relay | Sole depot (public VPS) | ONLINE |
| **northGate** | AlphaFold data source (~1TB) | Windows, RTX 5090 | **DAILY DRIVER — DO NOT DEPLOY** |

### Active Gardens/Springs/Teams (what code teams work on)

| Team / Project | Type | What | Gate | Status |
|----------------|------|------|------|--------|
| **primalSpring** | Spring | Neural API N2-N5 activation testing | **eastGate** | **ACTIVE — code team spun up** |
| **biomeOS** | Primal | Routing infrastructure (riboCipher pooling, bootstrap→coordinated) | **eastGate** | **ACTIVE — code team spun up** |
| **hotSpring** | Spring | QCD SU(N). Rung 1 science COMPLETE. Compute trio. | strandGate | Running. 627+ tests. |
| **tideGlass** | Spring | NF GPS rebuild (Gonzales/Bin Chen). Cell boot NEXT. | westGate | 214 tests. CAS wired. |
| **esotericWebb** | Garden | Game engine on NUCLEUS. V31b, 484 tests. | ironGate | CELL BOOT SUCCEEDED. |
| **footPrint** | Garden | GIS data visualization. 708 TS tests. | ironGate | **LIVE** at primals.eco/footprint/ |
| **sporePrint** | Infra | Public website — demonstration era. | golgi | LIVE at primals.eco |

### Workspace Structure

The workspace is at `~/Development/ecoPrimals/` with this layout:

```
ecoPrimals/
├── primals/        # 15 autonomous Rust binaries (Forgejo org: ecoPrimals/)
│   ├── bearDog          # Trust foundation — crypto, BTSP, FIDO2, beacon
│   ├── songBird         # Discovery — mesh, IPC, relay, drawbridge
│   ├── skunkBat         # Defense — anomaly detection, protocol audit
│   ├── nestGate         # Content-addressed storage — CAS, provenance
│   ├── rhizoCrypt       # Lineage DAG — content identity, federation
│   ├── loamSpine        # Certificate ledger — lifecycle, verification
│   ├── sweetGrass       # Attribution braids — provenance chains
│   ├── toadStool        # Compute dispatch — GPU, wgpu, hardware learning
│   ├── barraCuda        # Tensor math — linear algebra, GPU compute
│   ├── coralReef        # Shader compilation — WGSL, SPIR-V
│   ├── biomeOS          # Orchestrator — Neural API, signal graphs, NUCLEUS
│   ├── squirrel         # AI assistant — MCP, ML
│   ├── petalTongue      # Visualization — WASM, WebGL, rendering
│   ├── sourDough        # (dormant)
│   └── bingoCube        # (dormant)
├── gardens/        # Products and integration layers (Forgejo org: sporeGarden/)
│   ├── cellMembrane     # Deployment fabric — gate config, harvest, push
│   ├── esotericWebb     # Interactive ecosystem visualization
│   ├── lithoSpore       # USB portability / pseudoSpore packaging
│   ├── projectFOUNDATION # Knowledge foundation layer
│   ├── projectNUCLEUS   # Full NUCLEUS product
│   ├── helixVision      # Helix vision system
│   ├── initioChem       # Computational chemistry
│   ├── metalForge       # Metal fabrication
│   └── blueFish         # (placeholder)
├── springs/        # Science and domain applications (Forgejo org: syntheticChemistry/)
│   ├── primalSpring     # Scenario validation + benchmarks
│   ├── hotSpring        # Compute dispatch
│   ├── wetSpring        # Biodiversity + spectral analysis
│   ├── airSpring        # Air quality / atmospheric
│   ├── groundSpring     # Geological
│   ├── healthSpring     # Health data
│   ├── ludoSpring       # Game/simulation
│   ├── neuralSpring     # Neural/NPU
│   └── rustChip         # Rust tooling
└── infra/          # Infrastructure and documentation (mixed orgs — see mapping)
    ├── wateringHole      # Standards, handoffs, blurbs (ecoPrimals/)
    ├── plasmidBin        # Depot binaries + enrollment scripts (ecoPrimals/)
    ├── fossilRecord      # Archived/completed documentation (ecoPrimals/)
    ├── sporePrint        # SEO / web presence (ecoPrimals/) — empty placeholder on Forgejo
    ├── whitePaper        # Research papers, JOSS publication (ecoPrimals/)
    ├── agentReagents     # Agent tooling (syntheticChemistry/)
    └── benchScale        # Topology benchmarking (syntheticChemistry/)
```

### Windows Prerequisites (blueGate, swiftGate, northGate)

Windows gates need these steps before syncing:

```powershell
# Install Git if not present
winget install Git.Git

# Required: enable long paths (NTFS 260-char limit breaks fossilRecord)
git config --global core.longpaths true

# Required: disable credential manager prompts (blocks non-interactive sessions)
$env:GIT_TERMINAL_PROMPT = 0
$env:GCM_INTERACTIVE = "never"
[Environment]::SetEnvironmentVariable("GIT_TERMINAL_PROMPT", "0", "User")
[Environment]::SetEnvironmentVariable("GCM_INTERACTIVE", "never", "User")

# Recommended: OS-level long path support (requires admin)
# Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1
```

### Step 1a: Fix Naming Divergences

Older gate checkouts may have lowercase directory names. Fix them first:

```bash
cd ~/Development/ecoPrimals

# Remove symlinks that point at wrong-case targets (e.g. toadStool → toadstool)
# Must happen BEFORE renames to avoid breaking the symlink target
for d in primals/* gardens/* springs/* infra/*; do
  [ -L "$d" ] && echo "REMOVING SYMLINK: $d → $(readlink $d)" && rm "$d"
done

# Fix case-mismatched primal directories (if they exist)
[ -d primals/beardog ] && [ ! -d primals/bearDog ] && mv primals/beardog primals/bearDog
[ -d primals/nestgate ] && [ ! -d primals/nestGate ] && mv primals/nestgate primals/nestGate
[ -d primals/songbird ] && [ ! -d primals/songBird ] && mv primals/songbird primals/songBird
[ -d primals/toadstool ] && [ ! -d primals/toadStool ] && mv primals/toadstool primals/toadStool

# Remove known duplicates (lowercase when camelCase already exists)
[ -d primals/toadstool ] && [ -d primals/toadStool ] && rm -rf primals/toadstool
[ -d springs/barraCuda ] && rm -rf springs/barraCuda

# Fix branch names (master → main)
for d in primals/* gardens/* springs/* infra/*; do
  [ -d "$d/.git" ] || continue
  (cd "$d" && branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
   [ "$branch" = "master" ] && git branch -m master main 2>/dev/null && echo "$(basename $d): master → main")
done
```

### Step 1b: Repoint Remotes from GitHub to Forgejo

Older gates may still point at GitHub. This script repoints all remotes to
Forgejo using the correct org mapping.

**WARNING — Shallow Roots**: GitHub-origin repos often have **incompatible
commit histories** with Forgejo and cannot fast-forward. If `git pull` fails
after repointing, you must **fresh clone** from Forgejo (back up the old
directory first if it has local changes). strandGate hit this on 7/7 GitHub
repos — all required fresh clones. westGate (31 GitHub repos) will likely
need the same treatment. The script below handles this automatically:

```bash
cd ~/Development/ecoPrimals

# Detect SSH availability (set once, used by all functions)
if ssh -T git@git.primals.eco 2>&1 | grep -q "successfully authenticated"; then
  FORGEJO_PROTO="ssh"
  echo "SSH authenticated — using SSH URLs"
else
  FORGEJO_PROTO="https"
  echo "SSH not available — using HTTPS (read-only, push needs SSH later)"
fi

forgejo_url() {
  local org="$1" name="$2"
  if [ "$FORGEJO_PROTO" = "ssh" ]; then
    echo "ssh://git@git.primals.eco:2222/${org}/${name}.git"
  else
    echo "https://git.primals.eco/${org}/${name}.git"
  fi
}

repoint_or_reclone() {
  local dir="$1" org="$2" name=$(basename "$1")
  if [ ! -d "$dir/.git" ]; then return; fi
  local current=$(cd "$dir" && git remote get-url origin 2>/dev/null)
  local target=$(forgejo_url "$org" "$name")
  if [ "$current" = "$target" ]; then return; fi

  # Repoint
  (cd "$dir" && git remote set-url origin "$target")
  echo "REPOINTED: $name → $org ($FORGEJO_PROTO)"

  # Test if histories are compatible
  if ! (cd "$dir" && git fetch origin 2>/dev/null && git merge-base --is-ancestor HEAD origin/main 2>/dev/null); then
    echo "  SHALLOW ROOTS: $name — histories incompatible, fresh cloning..."
    local dirty=$(cd "$dir" && git status --porcelain 2>/dev/null | wc -l)
    if [ "$dirty" -gt 0 ]; then
      local stash="${dir}.stash-$(date +%s)"
      echo "  STASHING dirty files → $stash"
      mkdir -p "$stash"
      (cd "$dir" && git diff > "$stash/tracked.patch" 2>/dev/null)
      (cd "$dir" && git status --porcelain | awk '{print $2}' | while read f; do
        [ -f "$f" ] && cp --parents "$f" "$stash/" 2>/dev/null
      done)
    fi
    rm -rf "$dir"
    git clone "$target" "$dir"
    echo "  RECLONED: $name from Forgejo ($FORGEJO_PROTO)"
  fi
}

# primals → ecoPrimals org
for d in primals/*; do repoint_or_reclone "$d" "ecoPrimals"; done

# gardens → sporeGarden org
for d in gardens/*; do repoint_or_reclone "$d" "sporeGarden"; done

# springs → syntheticChemistry org
for d in springs/*; do repoint_or_reclone "$d" "syntheticChemistry"; done

# infra — mixed orgs
for d in wateringHole plasmidBin fossilRecord sporePrint whitePaper; do
  repoint_or_reclone "infra/$d" "ecoPrimals"
done
for d in agentReagents benchScale; do
  repoint_or_reclone "infra/$d" "syntheticChemistry"
done
```

### Step 1c: Clone Missing Repos

Check for missing repos and clone them:

```bash
cd ~/Development/ecoPrimals

clone_if_missing() {
  local dir="$1" org="$2" name="$3"
  if [ ! -d "$dir" ]; then
    echo "CLONING: $name → $dir"
    git clone "$(forgejo_url "$org" "$name")" "$dir"
  fi
}

# Primals (all should exist)
for p in bearDog songBird skunkBat nestGate rhizoCrypt loamSpine sweetGrass \
         toadStool barraCuda coralReef biomeOS squirrel petalTongue sourDough bingoCube; do
  clone_if_missing "primals/$p" "ecoPrimals" "$p"
done

# Gardens
for g in cellMembrane esotericWebb lithoSpore projectFOUNDATION projectNUCLEUS \
         helixVision initioChem metalForge blueFish; do
  clone_if_missing "gardens/$g" "sporeGarden" "$g"
done

# Springs
for s in primalSpring hotSpring wetSpring airSpring groundSpring healthSpring \
         ludoSpring neuralSpring rustChip; do
  clone_if_missing "springs/$s" "syntheticChemistry" "$s"
done

# Infra
clone_if_missing "infra/wateringHole" "ecoPrimals" "wateringHole"
clone_if_missing "infra/plasmidBin" "ecoPrimals" "plasmidBin"
clone_if_missing "infra/fossilRecord" "ecoPrimals" "fossilRecord"
clone_if_missing "infra/sporePrint" "ecoPrimals" "sporePrint"
clone_if_missing "infra/whitePaper" "ecoPrimals" "whitePaper"
clone_if_missing "infra/agentReagents" "syntheticChemistry" "agentReagents"
clone_if_missing "infra/benchScale" "syntheticChemistry" "benchScale"
```

### Step 1d: Pull Everything

```bash
cd ~/Development/ecoPrimals
for d in primals/* gardens/* springs/* infra/*; do
  name=$(basename "$d")
  echo "=== $name ==="
  (cd "$d" && git fetch origin 2>/dev/null && git pull --rebase origin main 2>/dev/null) || echo "SKIP: $name"
done
```

### Step 1e: Review State

After sync completes:

1. Read `infra/wateringHole/handoffs/ECOSYSTEM_BLURB.md` — universal handoff
2. Read `infra/wateringHole/wave.toml` — current wave and posture
3. Read `infra/wateringHole/ORTHOGONAL_DIMENSIONS_REVIEW.md` — 9 active + 14 fossilized dimensions
4. Check for remaining dirty repos:
```bash
for d in primals/* gardens/* springs/* infra/*; do
  name=$(basename "$d")
  dirty=$(cd "$d" 2>/dev/null && git status --porcelain 2>/dev/null | wc -l)
  [ "$dirty" -gt 0 ] && echo "$name: $dirty dirty files"
done
```

### Step 1f: Report Divergences

File your sync report as:
`infra/wateringHole/handoffs/[GATE_NAME]_OVERWATCH_SYNC.md`

Report:
- Repos that failed to pull (merge conflicts, auth errors)
- Uncommitted local changes (stash or discard — ask eastGate if unsure)
- Missing repos that failed to clone
- Any extra directories not in the canonical layout (safe to keep, just report)

---

## PHASE 2: ENROLLMENT — WireGuard + Tower Atomic

**This phase requires human action and is NOT needed for code review work.**
Skip this if you're only doing code team audit/review. Enrollment is needed
when the gate will run primals (Tower Atomic or higher).

### WireGuard Mesh IP Assignments

| Gate | WG IP | Status |
|------|-------|--------|
| golgiBody | 10.13.37.1 | LIVE (hub) |
| sporeGate | 10.13.37.2 | LIVE (site router, peptidoglycan anchor H1) |
| eastGate | 10.13.37.5 | LIVE |
| flockGate | 10.13.37.6 | DOWN (dead CMOS / RustDesk lockout) |
| ironGate | 10.13.37.7 | LIVE |
| northGate | 10.13.37.8 | LIVE (daily driver — no deploy) |
| southGate | 10.13.37.9 | **NO WG** (deliberate — validation gate) |
| strandGate | 10.13.37.10 | LIVE (NUCLEUS) |
| westGate | 10.13.37.11 | LIVE (NUCLEUS, ZFS 50.7TB) |
| blueGate | 10.13.37.12 | LIVE (NUCLEUS, Windows, sub-builder) |
| swiftGate | 10.13.37.13 | PENDING KEYGEN |

### Step 2a: WireGuard Setup (HUMAN — requires admin)

**Linux:**

```bash
wg genkey | tee /etc/wireguard/privatekey | wg pubkey > /etc/wireguard/publickey
chmod 600 /etc/wireguard/privatekey

cat > /etc/wireguard/wg0.conf << 'WGEOF'
[Interface]
Address = YOUR_IP/24
PrivateKey = CONTENTS_OF_/etc/wireguard/privatekey
ListenPort = 51821

[Peer]
# golgiBody (hub)
PublicKey = A2fvz3czkqRUuu2mzkSS6IVr/TCQcpsJX9HbDBa1FBc=
Endpoint = [RELAY_PUBLIC]:51820
AllowedIPs = 10.13.37.0/24
PersistentKeepalive = 25
WGEOF

sudo wg-quick up wg0
sudo systemctl enable wg-quick@wg0
ping -c 3 10.13.37.1
```

**Windows (blueGate, swiftGate, northGate):**

Install WireGuard from https://www.wireguard.com/install/. Then in the
WireGuard GUI: Add Tunnel → Create from scratch. Paste this config
(replace `YOUR_IP` and `YOUR_PRIVATE_KEY`):

```ini
[Interface]
Address = YOUR_IP/24
PrivateKey = YOUR_PRIVATE_KEY
ListenPort = 51821

[Peer]
PublicKey = A2fvz3czkqRUuu2mzkSS6IVr/TCQcpsJX9HbDBa1FBc=
Endpoint = [RELAY_PUBLIC]:51820
AllowedIPs = 10.13.37.0/24
PersistentKeepalive = 25
```

Generate keys from PowerShell (admin):

```powershell
# WireGuard must be installed first
& "C:\Program Files\WireGuard\wg.exe" genkey | Tee-Object -Variable privateKey | & "C:\Program Files\WireGuard\wg.exe" pubkey
# Copy the public key output and send to eastGate overwatch
```

Activate the tunnel in WireGuard GUI. Verify: `ping 10.13.37.1`

**IMPORTANT**: Send your public key to eastGate overwatch so it can be
registered on golgiBody. If your gate is already REGISTERED in the table
above, your peer config may already exist on golgiBody — just bring up the tunnel.

### Step 2b: Set Hostname

**Linux:**
```bash
sudo hostnamectl set-hostname YOUR_GATE_NAME
```

**Windows:**
```powershell
Rename-Computer -NewName YOUR_GATE_NAME -Restart
```

### Step 2c: Deploy Tower Atomic

Tower Atomic (bearDog + songBird + skunkBat) must be deployed before any
workload primals. Fetch genomeBins from the depot.

**Linux:**
```bash
mkdir -p ~/.local/bin
for primal in beardog songbird skunkbat; do
  curl -fsSL "https://depot.primals.eco/primals/$(uname -m)-unknown-linux-musl/${primal}" \
    -o ~/.local/bin/${primal}
  chmod +x ~/.local/bin/${primal}
done
```

**Windows:**

All 14 primal `.exe` binaries are available on the depot (`x86_64-pc-windows-gnu`).
No source build needed — download directly:

```powershell
$depotBase = "https://depot.primals.eco/primals/x86_64-pc-windows-gnu"
$binDir = "$env:USERPROFILE\.local\bin"
New-Item -ItemType Directory -Force -Path $binDir | Out-Null
foreach ($primal in @("beardog", "songbird", "skunkbat")) {
    Invoke-WebRequest -Uri "$depotBase/$primal.exe" -OutFile "$binDir\$primal.exe"
    Write-Host "Downloaded: $primal.exe"
}
# Add to PATH if not already there:
# [Environment]::SetEnvironmentVariable("Path", $env:Path + ";$binDir", "User")
```

If you need to build from source instead (e.g., testing local changes):
```powershell
cd ~/Development/ecoPrimals/primals/bearDog
cargo build --release
# Binary at target/release/beardog.exe
```

### Step 2d: Validate Tower

```bash
# Linux: Start Tower Atomic primals and verify health
# Windows: Run from PowerShell or as Windows Service
# Expected: tower.health returns { "status": "healthy" }
# Expected: tower.mesh_status returns peer count and transport info
```

---

## PHASE 3: CODE TEAM SPIN-UP

After overwatch has synced the gate (Phase 0+1 complete), paste this blurb
again with the team-specific section below for the primal(s) you're working on.

**Phase 2 (enrollment) is NOT required for code team work.** Code teams can
audit, review, build, and test locally without being on the mesh. Enrollment
is only needed when deploying primals to run as services.

### Audit Dimensions (all teams)

> Review `specs/` and the codebase/docs at root, and docs at parent
> `ecoPrimals/infra/wateringHole/` for inter-primal standards. Start with
> `wateringHole/STANDARDS_AND_EXPECTATIONS.md`, then `ECOSYSTEM_BLURB.md`.
>
> **Code Quality**
> - Linting: `cargo clippy --all-targets -- -W clippy::pedantic -W clippy::nursery` (0 warnings)
> - Formatting: `cargo fmt --check` (clean)
> - Doc checks: `cargo doc --no-deps` (0 warnings, all public items documented)
> - Idiomatic Rust: no `unwrap()` in non-test code — use `anyhow`/`thiserror`
> - File size: 800 lines max per file — split if over
> - Lean dependencies, clean module graph, no circular deps
>
> **Architecture Compliance**
> - JSON-RPC + tarpc: all IPC is JSON-RPC wire + tarpc service trait (G64 cephalization)
> - Protocol negotiation: single socket serves both JSON-RPC and tarpc (G65)
> - Transport abstraction: `TransportEndpoint`/`TransportStream`/`connect_transport` (G66)
> - Cross-arch: `cargo check --target x86_64-pc-windows-gnu` must PASS (pre-push standard)
> - genomeBin compliant: single-binary per `ECOBIN_ARCHITECTURE_STANDARD.md`
> - Semantic method naming per `SEMANTIC_METHOD_NAMING_STANDARD.md`
> - Platform-native transport: songBird universal-ipc (UDS/named pipes/TCP)
> - BTSP: must ship bearDog ClientHello for authenticated IPC (15/15)
> - biomeOS neuralAPI: capabilities discoverable via `capability.call` (Stage 2)
> - riboCipher transport signal: `[0xEC, protocol]` prefix on NUCLEUS sockets
>
> **Test Coverage**
> - Target: 90% line coverage via `cargo llvm-cov` (report actual)
> - Required tiers: unit, integration, E2E scenario (via primalSpring)
>
> **Debt & Gaps**
> - Find all `todo!()`, `FIXME`, `HACK`, `TODO` markers
> - Hardcoded ports/names/constants → extract to config
> - Dead code, unused imports, stale feature flags
>
> **Sovereignty**
> - AGPL-3.0 / scyBorg triple-license
> - No telemetry, no cloud lock-in, pure Rust crypto
> - All genomeBins from `https://depot.primals.eco`
>
> **What have we not completed?** Report all gaps, mocks standing in for real
> integrations, TODOs, deep debt, and upstream blockers. Prioritize as P0/P1/P2.

### Key Standards (in `infra/wateringHole/`)

| Standard | Path |
|----------|------|
| Architecture | `fossilRecord/wave150s_standards/ECOBIN_ARCHITECTURE_STANDARD.md` |
| Method naming | `protocols/SEMANTIC_METHOD_NAMING_STANDARD.md` |
| Protocol negotiation | `specs/PROTOCOL_NEGOTIATION_SPEC.md` (G65) |
| Transport abstraction | `specs/TRANSPORT_ABSTRACTION_SPEC.md` (G66) |
| Neural API activation | `specs/NEURAL_API_ACTIVATION_SPEC.md` (G67) |
| Licensing | `foundations/LICENSING_AND_COPYLEFT.md` |
| Expectations | `STANDARDS_AND_EXPECTATIONS.md` |
| Pure Rust crypto | `fossilRecord/wave150s_standards/PURE_RUST_CRYPTO_PURITY_STANDARD.md` |
| Ecosystem posture | `handoffs/ECOSYSTEM_BLURB.md` |

### Convergence Rule

> **eastGate owns the codebase.** Gate teams are deployment validators
> and workload runners. Follow this workflow:
>
> 1. **DO NOT** push code changes from your gate (except wateringHole handoffs).
> 2. **Minimal edits only**: config tweaks, environment-specific settings.
> 3. **Report back**: File findings as handoffs in `infra/wateringHole/handoffs/`.
> 4. **Pull from Forgejo regularly** to stay converged.
> 5. Bugs: document in handoff with file, line, proposed fix — eastGate ships it.
>
> Handoff push access: your gate's SSH key must be registered in Forgejo with
> write access to `ecoPrimals/wateringHole`. Ask eastGate overwatch to set this up.

---

## Team-Specific Contexts (paste the relevant one)

### CODE TEAM: primalSpring — Neural API Activation (N2-N5)

> **primalSpring** — springs/primalSpring. Target gate: **eastGate**.
> Tests: 197 scenarios | Mission: **Verify Stage 2 Neural API routing works.**
>
> **Your job**: Build the fixed `neural-api-server` binary and verify that
> `capability.call` routes through Neural API to live primals on eastGate.
>
> **Setup**:
> 1. Build: `cd primals/biomeOS && cargo build --release -p neural-api-server`
> 2. The forwarding fix is in `crates/biomeos-atomic-deploy/src/neural_router/forwarding.rs` (commit `ffed2c5b`)
> 3. Test script: `primals/biomeOS/scripts/neural-api-test.sh` automates N1-N5
> 4. NUCLEUS is live on systemd: 13 primals running, sockets at `/run/user/1000/biomeos/`
>
> **Known**:
> - Some primals (sweetGrass) require riboCipher prefix (`0xEC 0x01`) before JSON-RPC
> - bearDog at `beardog-default.sock` accepts raw JSON-RPC
> - Neural API at `biomeos-neural.sock` requires riboCipher prefix
> - 8 primals have processes alive but sockets missing — may need restart
>
> **Activation tasks**:
>
> | # | Task | Status |
> |---|------|--------|
> | N1 | Fix forwarding path | **DONE** (`ffed2c5b`) |
> | N2 | `capability.call` routes to bearDog | **YOUR FIRST TARGET** |
> | N3 | Tower Atomic routing (bearDog+songBird+skunkBat) | PENDING |
> | N4 | Provenance Trio routing (rhizoCrypt+loamSpine+sweetGrass) | PENDING |
> | N5 | squirrel agent routing via Neural API | PENDING |
>
> **Spec**: `infra/wateringHole/specs/NEURAL_API_ACTIVATION_SPEC.md` (G67)
>
> **NUCLEUS option**: You can run your own NUCLEUS (second instance on eastGate,
> or via beanchScale VM/image) to avoid disturbing the overwatch NUCLEUS.
>
> **Report**: File results as `infra/wateringHole/handoffs/PRIMALSPRING_N2_N5_AAR.md`

### CODE TEAM: biomeOS — Routing Infrastructure

> **biomeOS** — primals/biomeOS. Target gate: **eastGate**.
> Tests: 8,570+ (456 Neural API) | Version: v4.57+ | Commit: `ffed2c5b`
>
> **Your job**: Evolve the Neural API routing layer for Stage 2 readiness.
>
> **Focus areas**:
> 1. **riboCipher-aware connection pooling**: The pool currently sends raw JSON-RPC.
>    NUCLEUS-deployed primals (sweetGrass, etc.) need `0xEC 0x01` prefix before
>    JSON-RPC payloads. The pool's `send_jsonrpc` needs to prepend the signal.
> 2. **Bootstrap → Coordinated mode transition**: Neural API starts in Bootstrap
>    mode with 0 registered capabilities. It needs to discover running primals
>    and transition to Coordinated mode for capability routing.
> 3. **Graph execution through capability semantics**: `graph.execute` should
>    resolve to `capability.call` chains, not direct socket connections.
>
> **Key files**:
> - `crates/biomeos-atomic-deploy/src/neural_router/forwarding.rs` — forwarding fix
> - `crates/biomeos-atomic-deploy/src/neural_router/` — all routing logic
> - `config/signal_tools.toml` — 27 signal graphs
>
> **Spec**: `infra/wateringHole/specs/NEURAL_API_ACTIVATION_SPEC.md` (G67)
>
> **Report**: File results as `infra/wateringHole/handoffs/BIOMEOS_STAGE2_AAR.md`

### CODE TEAM: hotSpring (QCD — Rung 1 science COMPLETE)

> **hotSpring** — springs/hotSpring. Target gate: **strandGate** (RTX 3090 + RX 6950 XT).
> Tests: 627+ | Version: v0.6.32 | Status: **Rung 1 science COMPLETE.**
>
> **Purpose**: GPU-resident lattice QCD — SU(N) for N=2→8. All physics validated.
> 3 remaining items are upstream (naga compiler bug, sporePrint URLs).
>
> **Current work**: Compute trio (toadStool+barraCuda+coralReef) memoization.
> 24K LOC fossilized (deprecated low_level, fleet_client/fleet_ember → toadStool).
>
> **Primal deduplication**: barraCuda should absorb `HardwareCalibration::probe()`
> and `PrecisionEval` from hotSpring (1,090 LOC). See
> `handoffs/HOTSPRING_PRIMAL_DEDUPLICATION_HANDOFF_AUG07.md`.

### CODE TEAM: esotericWebb (game engine)

> **esotericWebb** — gardens/esotericWebb. Target gate: **ironGate**.
> Tests: 484 | Version: V31b | Status: **CELL BOOT SUCCEEDED on ironGate.**
> 28 caps, 8/9 primals. Needs petalTongue WebGL pipeline (G19) for browser surface.

### GATE TEAM: Any new gate (Tower → NUCLEUS deployment)

> **All primals are in depot.** 52 builds across 4+ platforms.
> biomeOS v4.57+. Tower Atomic LIVE on 6+ gates. G64+G65+G66 COMPLETE.
>
> **Deployment sequence**:
> 1. Phase 0+1: Connectivity + sync (this blurb)
> 2. Phase 2: WireGuard enrollment (get IP from eastGate overwatch)
> 3. Fetch genomeBins from `https://depot.primals.eco`
> 4. Tower Atomic: bearDog + songBird + skunkBat (trust foundation)
> 5. Nest Atomic: + nestGate + rhizoCrypt + loamSpine + sweetGrass
> 6. Node Atomic: + toadStool + barraCuda + coralReef
> 7. biomeOS: Full NUCLEUS — orchestrates all 13 primals
>
> **Validate**: `tower.health` → `{ "status": "healthy" }`.
> **Windows**: Use `x86_64-pc-windows-gnu` binaries from depot.
> **Cross-arch**: All 15 primals pass `cargo check --target x86_64-pc-windows-gnu`.
>
> **Report**: File sync report and validation as:
> `infra/wateringHole/handoffs/[GATE_NAME]_DEPLOYMENT_AAR.md`

---

## K-Derm Three-Layer Model (reference)

```
OUTER MEMBRANE — Human access (RustDesk → relay.primals.eco)
PEPTIDOGLYCAN  — LAN/HPC topology fabric (NAT, DNS, switches, cabling)
INNER MEMBRANE — Primal IPC (WireGuard wg0 + songBird :7700 + BTSP)
```

Peptidoglycan anchors: sporeGate (house1) + blueGate (house2).
biomeOS v4.57+ (G67 Stage 2 activation) handles orchestration + trust propagation across inner membrane. Neural API is the routing substrate.

Forgejo access is OUTSIDE the inner membrane — it's public internet → golgiBody.
You only need inner membrane for primal-to-primal IPC and mesh enrollment.

---

## Glacial Goals (what we're building toward)

**15 COMPLETE** (G3, G4, G8, G10, G17, G21, G22, G29, G31, G55, G59, G64, G65, G66).

| # | Goal | Status |
|---|------|--------|
| G64 | Cephalization — tarpc convergent evolution | **COMPLETE** (15/15) |
| G65 | Protocol Negotiation — single-socket dual-protocol | **COMPLETE** (15/15) |
| G66 | Transport Abstraction — silicon-agnostic IPC | **COMPLETE** (15/15 cross-arch) |
| **G67** | **Neural API forwarding fix + Stage 2 transition** | **STAGE 2 INFRA SHIPPED** — N2-N5 verification, then depot |
| G56 | Neural API activation (capability routing everywhere) | **STAGE 2 INFRA SHIPPED** — depot rebuild + deploy |
| G9 | arXiv publication (Murillo/Chuna QCD) | **41/42** — NPU silicon continuum, MILC validated, reviewer send next |
| G36 | tideGlass Phase 1 — NF GPS reproduction | **ACTIVE** |
| G18 | squirrel → biomeOS agent orchestration | **LIVE on ironGate** |
| G53 | petalTongue maturation via downstream consumers | **ACTIVELY WIRING** |

63 glacial goals tracked total. See `ORTHOGONAL_DIMENSIONS_REVIEW.md` for full list.

---

## Appendix: Answers to Common Gate Questions

**Q: Do I need WireGuard to pull repos?**
No. Forgejo is on a public VPS. HTTPS works with zero config:
`git clone https://git.primals.eco/ecoPrimals/bearDog.git`. SSH (port 2222)
works too once your key is registered. WireGuard is only for inner membrane
(primal IPC, `10.13.37.x` overlay).

**Q: My repos point at GitHub (`github-ecoPrimal`). What do I do?**
Run Step 1b above. All canonical remotes are now on Forgejo. GitHub mirrors
exist but are not authoritative.

**Q: I have lowercase directory names (beardog, nestgate, songbird).**
Run Step 1a above. CamelCase is canonical.

**Q: I have a `springs/barraCuda` directory.**
It's a duplicate — barraCuda lives in `primals/`. Remove `springs/barraCuda`.

**Q: I have `primals/toadstool` AND `primals/toadStool`.**
Remove `primals/toadstool` (lowercase). Keep `primals/toadStool` (camelCase).

**Q: Some repos are on `master` branch, not `main`.**
Run Step 1a above — it renames `master` → `main`.

**Q: I have extra directories like `archive/`, `sort-after/`, or `springs/` duplicates.**
These are local artifacts from older waves. Safe to keep for reference, but
they're not part of the canonical layout and won't sync.

**Q: `gardens/projectFOUNDATION` is a symlink to `gardens/foundation`?**
That's fine. Some gates have both names pointing at the same repo. The
Forgejo name is `sporeGarden/projectFOUNDATION`. Keep the symlink.

**Q: `git pull` fails with "shallow roots" or "unrelated histories" after repointing?**
The GitHub and Forgejo copies diverged. Back up any dirty files, delete
the directory, and fresh clone from Forgejo. The Step 1b script handles
this automatically.

**Q: What SSH key should I use?**
`~/.ssh/id_ed25519_ecoPrimal` is the ecosystem key. If you have a gate-specific
key, that works too — just register it in Forgejo. Deploy keys (read-only) are
fine for gates that only pull.

**Q: What if barraCuda has local precision.rs / tests.rs changes?**
Stash them: `cd primals/barraCuda && git stash`. If they're intentional local
work, describe them in your sync report handoff. eastGate decides whether
to integrate.

---
*FOSSILIZED Wave 157k interstadial (Aug 13, 2026). Content superseded by ECOSYSTEM_BLURB.md and current ecosystem standards.*
