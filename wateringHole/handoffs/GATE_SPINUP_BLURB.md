# ecoPrimals Gate Spin-Up — Universal Bootstrap

**Wave**: 159 | **From**: overwatch (gate-agnostic)
**Purpose**: Bootstrap any gate through five phases: connectivity → sync → build → enrollment → RustDesk.
**Audience**: Gate hardware overwatch agents (Tier 1). Paste into a fresh Cursor IDE on any gate.

**This blurb is platform-adaptive.** It auto-detects Linux, macOS, and Windows and adjusts accordingly. After this blurb completes, the gate is connected, synced, running Tower Atomic, and reachable via RustDesk relay. Code team work (Tier 2) and ecosystem coordination (Tier 3) are separate concerns — they arrive via separate blurbs from overwatch.

**Wave 159 update**: All 16 primals compile for Windows. Windows depot has 16/16 binaries (rebuild pending). 5-target depot. 8 architecture families.

---

## PHASE 0: CONNECTIVITY — Forgejo Access

Forgejo (`git.primals.eco`) runs on golgiBody, a **public VPS**. You do NOT need WireGuard to access it. WireGuard is only needed later for inner membrane primal IPC.

### 0a: Platform Detection

```bash
# Run this to detect your platform
case "$(uname -s 2>/dev/null || echo Windows)" in
  Linux*)   PLATFORM="linux";;
  Darwin*)  PLATFORM="macos";;
  MINGW*|MSYS*|CYGWIN*) PLATFORM="windows";;
  *)        PLATFORM="unknown";;
esac
echo "Platform: $PLATFORM ($(uname -m 2>/dev/null || echo x86_64))"
```

### 0b: Prerequisites (platform-specific)

**Linux** (most gates — eastGate, sporeGate, westGate, ironGate, strandGate, southGate, biomeGate):
```bash
# Git and build tools should already be installed. If not:
sudo apt install -y git build-essential pkg-config libssl-dev curl
```

**macOS** (graftGate):
```bash
# Xcode CLI tools (if not already installed)
xcode-select --install
# Homebrew (macOS package manager — equivalent to apt)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

**Windows** (blueGate, swiftGate):
```powershell
winget install Git.Git
# Required: enable long paths (NTFS 260-char limit breaks fossilRecord)
git config --global core.longpaths true
# Required: disable credential manager prompts
$env:GIT_TERMINAL_PROMPT = 0
$env:GCM_INTERACTIVE = "never"
[Environment]::SetEnvironmentVariable("GIT_TERMINAL_PROMPT", "0", "User")
[Environment]::SetEnvironmentVariable("GCM_INTERACTIVE", "never", "User")
```

### 0c: Install Rust

All platforms — identical:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
# Hit 1 for default
source "$HOME/.cargo/env"  # or restart shell
rustc --version
```

### 0d: SSH Key + Forgejo

```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_ecoPrimal -C "$(hostname)@primals.eco"
cat ~/.ssh/id_ed25519_ecoPrimal.pub
# Register this public key in Forgejo: https://git.primals.eco → Settings → SSH/GPG Keys → Add Key
```

SSH config — add to `~/.ssh/config` (create if missing):
```bash
mkdir -p ~/.ssh
cat >> ~/.ssh/config << 'EOF'
Host forgejo git.primals.eco
    HostName git.primals.eco
    Port 2222
    User git
    IdentityFile ~/.ssh/id_ed25519_ecoPrimal
EOF
chmod 600 ~/.ssh/config
```

Verify: `ssh -T git@git.primals.eco` — should say "Hi \<user\>! You've successfully authenticated..."

If SSH isn't set up yet, HTTPS clone works immediately (read-only, zero config):
```bash
git clone https://git.primals.eco/ecoPrimals/bearDog.git primals/bearDog
```

---

## PHASE 1: SYNC — Clone All Repos

### What is ecoPrimals

ecoPrimals is a sovereign, AGPL-3.0 mesh operating system built in pure Rust. 16 primals (autonomous binaries) compose into **atomics**: Tower (security + discovery + defense), Node (Tower + compute), Nest (Tower + storage + provenance), and NUCLEUS (all 13 + swarmVine gossip + surfaces). biomeOS orchestrates via a Neural API with 27 signal graphs and semantic dispatch. All binaries ("genomeBins") are served from a single depot on golgiBody (`https://depot.primals.eco`). Gates are physical machines running compositions.

### Current State (Wave 159 — Sep 28, 2026)

| Fact | Value |
|------|-------|
| Wave | 159 (REWAKE — mesh expansion + primal-only bootstrap) |
| Primals | **16** (13 NUCLEUS + swarmVine + petalTongue + squirrel) |
| Tests | **~150K+** across 16 primals + gardens + springs |
| biomeOS | **v4.57+** — Neural API, 79 signal/deploy graphs, `capability.call` fleet-wide |
| BTSP | **16/16** — all primals ship bearDog ClientHello |
| Depot | **5 targets** (musl 18/18, gnu 14/14, windows 16/16, darwin 16/16, aarch64 15/15). BLAKE3 verified. |
| Gates | **3 ONLINE** (eastGate, sporeGate, golgiBody). northGate ENROLLING. House 2 OFFLINE. |
| Sites | **4 LIVE** — sporeprint (403), detroit (127), gorilla (20), guerillagorilla (alias) |
| G72 | **Tier 1 COMPLETE** (11/11 teams, ~155+ crates shed). Tier 2 queued. |
| SSH | **Tier 1 RETIRED** — sub-builder dispatch via `builder.serve` :9800 |
| Windows | **16/16 primals compile** — all `#[cfg(unix)]` gated. Depot rebuild pending. |
| P0 / P1 / P2 | **0 / 0 / 0** |

### Workspace Structure

```
ecoPrimals/
├── primals/        # 16 autonomous Rust binaries (Forgejo org: ecoPrimals/)
│   ├── bearDog          # Trust — crypto, BTSP, FIDO2, Ed25519 signing
│   ├── songBird         # Discovery — mesh, IPC, relay, drawbridge
│   ├── skunkBat         # Defense — anomaly detection, protocol audit
│   ├── nestGate         # Content-addressed storage — CAS, provenance
│   ├── rhizoCrypt       # Lineage DAG — content identity, federation
│   ├── loamSpine        # Certificate ledger — lifecycle, verification
│   ├── sweetGrass       # Attribution braids — provenance chains
│   ├── toadStool        # Compute dispatch — GPU, wgpu, hardware learning
│   ├── barraCuda        # Tensor math — linear algebra, GPU compute
│   ├── coralReef        # Shader compilation — WGSL, SPIR-V, PTX
│   ├── biomeOS          # Orchestrator — Neural API, signal graphs, NUCLEUS
│   ├── squirrel         # AI assistant — MCP, ML
│   ├── petalTongue      # Visualization — WASM, WebGL, rendering
│   ├── swarmVine        # Gossip — epidemic protocol, ant colony
│   ├── sourDough        # Factory — standards validator (advisory)
│   └── bingoCube        # (dormant)
├── gardens/        # Products and integration (Forgejo org: sporeGarden/)
│   ├── cellMembrane     # Deployment fabric — gate config, harvest, push
│   ├── esotericWebb     # Game engine on NUCLEUS
│   ├── lithoSpore       # pseudoSpore packaging
│   ├── projectFOUNDATION # Knowledge foundation layer
│   ├── projectNUCLEUS   # NUCLEUS product packaging
│   ├── helixVision      # Genomics + AlphaFold + rendering
│   └── (others)         # initioChem, metalForge, blueFish
├── springs/        # Science and domain apps (Forgejo org: syntheticChemistry/)
│   ├── primalSpring     # Scenario validation + composition experiments
│   ├── hotSpring        # Lattice QCD — GPU HMC simulations
│   ├── wetSpring        # Biodiversity + spectral analysis
│   └── (others)         # airSpring, groundSpring, healthSpring, ludoSpring, etc.
├── protists/       # Proto-karya (Forgejo org: protoKarya/)
│   └── tideGlass        # NF drug repurposing — GPS platform rebuild
└── infra/          # Infrastructure and documentation
    ├── wateringHole      # Standards, handoffs, blurbs (ecoPrimals/)
    ├── plasmidBin        # Depot binaries + enrollment scripts (ecoPrimals/)
    ├── sporePrint        # Public website (ecoPrimals/)
    ├── whitePaper        # Research papers (ecoPrimals/)
    └── (others)          # agentReagents, benchScale (syntheticChemistry/)
```

### 1a: Fix Naming Divergences (existing gates only — skip for fresh clones)

Older gate checkouts may have lowercase directories or GitHub remotes:

```bash
cd ~/Development/ecoPrimals

# Remove stale symlinks
for d in primals/* gardens/* springs/* infra/*; do
  [ -L "$d" ] && echo "REMOVING SYMLINK: $d → $(readlink $d)" && rm "$d"
done

# Fix case-mismatched directories
[ -d primals/beardog ] && [ ! -d primals/bearDog ] && mv primals/beardog primals/bearDog
[ -d primals/nestgate ] && [ ! -d primals/nestGate ] && mv primals/nestgate primals/nestGate
[ -d primals/songbird ] && [ ! -d primals/songBird ] && mv primals/songbird primals/songBird
[ -d primals/toadstool ] && [ ! -d primals/toadStool ] && mv primals/toadstool primals/toadStool

# Remove duplicates
[ -d primals/toadstool ] && [ -d primals/toadStool ] && rm -rf primals/toadstool
[ -d springs/barraCuda ] && rm -rf springs/barraCuda

# Fix branch names
for d in primals/* gardens/* springs/* infra/*; do
  [ -d "$d/.git" ] || continue
  (cd "$d" && branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
   [ "$branch" = "master" ] && git branch -m master main 2>/dev/null && echo "$(basename $d): master → main")
done
```

### 1b: Repoint Remotes + Clone Missing Repos

This script handles both existing gates (repoint GitHub → Forgejo) and fresh gates (clone everything):

```bash
cd ~/Development/ecoPrimals
mkdir -p primals gardens springs protists infra

# Detect SSH availability
if ssh -T git@git.primals.eco 2>&1 | grep -q "successfully authenticated"; then
  PROTO="ssh"
  forgejo_url() { echo "ssh://git@git.primals.eco:2222/$1/$2.git"; }
  echo "SSH authenticated — using SSH URLs"
else
  PROTO="https"
  forgejo_url() { echo "https://git.primals.eco/$1/$2.git"; }
  echo "SSH not available — using HTTPS (read-only)"
fi

clone_or_repoint() {
  local dir="$1" org="$2" name=$(basename "$1")
  local target=$(forgejo_url "$org" "$name")

  if [ ! -d "$dir/.git" ]; then
    [ -d "$dir" ] || mkdir -p "$(dirname "$dir")"
    echo "CLONING: $name → $dir"
    git clone "$target" "$dir"
    return
  fi

  local current=$(cd "$dir" && git remote get-url origin 2>/dev/null)
  if [ "$current" != "$target" ]; then
    (cd "$dir" && git remote set-url origin "$target")
    echo "REPOINTED: $name → $org ($PROTO)"
    if ! (cd "$dir" && git fetch origin 2>/dev/null && \
          git merge-base --is-ancestor HEAD origin/main 2>/dev/null); then
      echo "  SHALLOW ROOTS: $name — recloning from Forgejo..."
      rm -rf "$dir"
      git clone "$target" "$dir"
      echo "  RECLONED: $name"
    fi
  fi
}

# Primals (ecoPrimals org)
for p in bearDog songBird skunkBat nestGate rhizoCrypt loamSpine sweetGrass \
         toadStool barraCuda coralReef biomeOS squirrel petalTongue swarmVine \
         sourDough bingoCube; do
  clone_or_repoint "primals/$p" "ecoPrimals"
done

# Gardens (sporeGarden org)
for g in cellMembrane esotericWebb lithoSpore projectFOUNDATION projectNUCLEUS \
         helixVision initioChem metalForge blueFish; do
  clone_or_repoint "gardens/$g" "sporeGarden"
done

# Springs (syntheticChemistry org)
for s in primalSpring hotSpring wetSpring airSpring groundSpring healthSpring \
         ludoSpring neuralSpring rustChip; do
  clone_or_repoint "springs/$s" "syntheticChemistry"
done

# Protists (protoKarya org)
for t in tideGlass; do
  clone_or_repoint "protists/$t" "protoKarya"
done

# Infra (mixed orgs)
for i in wateringHole plasmidBin sporePrint whitePaper fossilRecord; do
  clone_or_repoint "infra/$i" "ecoPrimals"
done
for i in agentReagents benchScale; do
  clone_or_repoint "infra/$i" "syntheticChemistry"
done
```

### 1c: Pull Everything

```bash
cd ~/Development/ecoPrimals
for d in primals/* gardens/* springs/* protists/* infra/*; do
  [ -d "$d/.git" ] || continue
  name=$(basename "$d")
  echo "=== $name ==="
  (cd "$d" && git fetch origin 2>/dev/null && git pull --rebase origin main 2>/dev/null) || echo "SKIP: $name"
done
```

### 1d: Verify Sync

```bash
cd ~/Development/ecoPrimals
echo "=== Repos ==="
find primals gardens springs protists infra -maxdepth 2 -name '.git' -type d 2>/dev/null | wc -l

echo "=== Dirty repos ==="
for d in primals/* gardens/* springs/* protists/* infra/*; do
  [ -d "$d/.git" ] || continue
  dirty=$(cd "$d" && git status --porcelain 2>/dev/null | wc -l)
  [ "$dirty" -gt 0 ] && echo "$(basename $d): $dirty dirty files"
done

echo "=== Ecosystem posture ==="
head -5 infra/wateringHole/handoffs/ECOSYSTEM_BLURB.md
```

---

## PHASE 2: BUILD — Tower Atomic

Tower Atomic (bearDog + songBird + skunkBat + swarmVine) is the trust foundation — the shared electron cloud providing crypto, routing, defense, and gossip. Every gate needs it before any workload primals.

### 2a: Depot Pull (if your platform has depot binaries)

Current depot targets: `x86_64-unknown-linux-musl` (18/18), `x86_64-unknown-linux-gnu` (14/14), `x86_64-pc-windows-gnu` (16/16), `aarch64-unknown-linux-musl` (15/15), `aarch64-apple-darwin` (16/16).

**Linux (musl — most gates):**
```bash
ARCH=$(uname -m)
mkdir -p ~/.local/bin
for primal in beardog songbird skunkbat swarmvine; do
  curl -fsSL "https://depot.primals.eco/primals/${ARCH}-unknown-linux-musl/${primal}" \
    -o ~/.local/bin/${primal}
  chmod +x ~/.local/bin/${primal}
  echo "Downloaded: $primal"
done
export PATH="$HOME/.local/bin:$PATH"
```

**Windows:**
```powershell
$depotBase = "https://depot.primals.eco/primals/x86_64-pc-windows-gnu"
$binDir = "$env:USERPROFILE\.local\bin"
New-Item -ItemType Directory -Force -Path $binDir | Out-Null
foreach ($primal in @("beardog", "songbird", "skunkbat", "swarmvine")) {
    Invoke-WebRequest -Uri "$depotBase/$primal.exe" -OutFile "$binDir\$primal.exe"
    Write-Host "Downloaded: $primal.exe"
}
```

### 2b: Source Build (if depot has no binary for your platform)

If your platform is not in the depot (e.g., `aarch64-apple-darwin` for macOS), build from source:

```bash
cd ~/Development/ecoPrimals
mkdir -p ~/.local/bin

for primal in bearDog songBird skunkBat swarmVine; do
  echo "=== Building $primal ==="
  (cd "primals/$primal" && cargo build --release) || echo "FAILED: $primal — report in handoff"
  bin_name=$(echo "$primal" | tr '[:upper:]' '[:lower:]')
  src="primals/$primal/target/release/$bin_name"
  [ -f "$src" ] && cp "$src" ~/.local/bin/ && chmod +x ~/.local/bin/$bin_name
done

export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.${SHELL##*/}rc 2>/dev/null || true
```

Report any compilation failures — they are expected for first-ever platform builds and are valuable data.

### 2c: Build Full NUCLEUS (optional — after Tower validates)

```bash
cd ~/Development/ecoPrimals
for primal in nestGate rhizoCrypt loamSpine sweetGrass toadStool barraCuda \
              coralReef biomeOS squirrel petalTongue swarmVine sourDough; do
  echo "=== Building $primal ==="
  (cd "primals/$primal" && cargo build --release 2>&1 | tail -3) || echo "FAILED: $primal"
done
```

---

## PHASE 3: ENROLLMENT — Mesh + Validation

### 3a: Set Hostname

**Linux:** `sudo hostnamectl set-hostname YOUR_GATE_NAME`
**macOS:** System Settings → General → About → Name → YOUR_GATE_NAME
**Windows:** `Rename-Computer -NewName YOUR_GATE_NAME -Restart`

### 3b: WireGuard

**Linux:**
```bash
sudo apt install wireguard-tools  # or equivalent for your distro
wg genkey | sudo tee /etc/wireguard/privatekey | wg pubkey | sudo tee /etc/wireguard/publickey
sudo chmod 600 /etc/wireguard/privatekey
# Send public key to eastGate overwatch for registration on golgiBody
```

**macOS:**
```bash
brew install wireguard-tools
wg genkey | tee /tmp/wg-privatekey | wg pubkey > /tmp/wg-publickey
cat /tmp/wg-publickey
# Send public key to eastGate overwatch
```

**Windows:**
Install WireGuard from https://www.wireguard.com/install/. Generate keys in WireGuard GUI or PowerShell.

**All platforms — config** (overwatch assigns your mesh IP):

```ini
[Interface]
Address = ASSIGNED_IP/24
PrivateKey = YOUR_PRIVATE_KEY
ListenPort = 51821

[Peer]
# golgiBody (hub)
PublicKey = A2fvz3czkqRUuu2mzkSS6IVr/TCQcpsJX9HbDBa1FBc=
Endpoint = [RELAY_PUBLIC]:51820
AllowedIPs = 10.13.37.0/24
PersistentKeepalive = 25
```

Bring up: `sudo wg-quick up wg0` (Linux/macOS) or activate in WireGuard GUI (Windows).
Verify: `ping 10.13.37.1`

### 3c: Gate Enrollment

```bash
cd ~/Development/ecoPrimals/infra/plasmidBin
bash gate-enroll.sh
```

### 3d: Validate Tower

```bash
beardog &
sleep 2
songbird &
sleep 2
skunkbat &
sleep 2
swarmvine &
sleep 2

# Check processes
ps aux | grep -E "beardog|songbird|skunkbat|swarmvine" | grep -v grep
```

---

## PHASE 4: REPORT

File your bootstrap report as:
`infra/wateringHole/handoffs/[GATE_NAME]_BOOTSTRAP_AAR.md`

Report:
- Platform details (`uname -a` or `system_profiler SPHardwareDataType`)
- Rust toolchain version (`rustc --version`)
- Tower Atomic binary sizes (especially for new depot targets)
- Any compilation failures or platform-specific issues
- WireGuard status
- Repo sync status (count, any failures)

---

## KEY REFERENCES

| Document | Path |
|----------|------|
| Ecosystem posture | `infra/wateringHole/handoffs/ECOSYSTEM_BLURB.md` |
| Orthogonal review | `infra/wateringHole/ORTHOGONAL_DIMENSIONS_REVIEW.md` |
| Architecture standard | `infra/wateringHole/fossilRecord/wave150s_standards/ECOBIN_ARCHITECTURE_STANDARD.md` |
| Method naming | `infra/wateringHole/protocols/SEMANTIC_METHOD_NAMING_STANDARD.md` |
| G72 Dep Pandemic | `infra/wateringHole/specs/DEPENDENCY_PANDEMIC_SPEC.md` |
| Standards | `infra/wateringHole/STANDARDS_AND_EXPECTATIONS.md` |

## CONVERGENCE RULE

> **eastGate owns the codebase.** Gate teams are deployment validators.
> 1. **DO NOT** push code changes (except `wateringHole/handoffs/` AARs).
> 2. **Report** findings as handoffs.
> 3. **Pull from Forgejo regularly** to stay converged.
> 4. Bugs: document in handoff with file, line, proposed fix — eastGate ships it.

## PHASE 5: RUSTDESK — Remote Access Enrollment

RustDesk provides outer membrane human access via `relay.primals.eco` on golgiBody.

### 5a: Install RustDesk

**Linux:**
```bash
curl -fsSL https://github.com/rustdesk/rustdesk/releases/download/1.3.9/rustdesk-1.3.9-x86_64.deb -o /tmp/rustdesk.deb
sudo apt install -y /tmp/rustdesk.deb
```

**macOS:** Download from https://rustdesk.com/
**Windows:** `winget install RustDesk.RustDesk`

### 5b: Configure Relay (One Command — No Manual Key Entry)

RustDesk supports `--config` which applies the relay server, key, and all settings in a single encoded string. This eliminates the need to manually type the relay key.

**All platforms:**
```bash
# Linux:
pkexec rustdesk --config "[RUSTDESK_CONFIG_PURGED]"

# macOS:
sudo ./RustDesk --config "[RUSTDESK_CONFIG_PURGED]"

# Windows (admin cmd):
rustdesk.exe --config "[RUSTDESK_CONFIG_PURGED]"
```

This config string encodes the relay server (`relay.primals.eco` / golgiBody [RELAY_PUBLIC]), ports (21115-21117), and the relay public key. After applying, the device registers on the sovereign relay and can see all other gates. No manual key typing needed.

> **Source**: Config string from golgiBody relay setup. If the relay key rotates, regenerate with `rustdesk --get-id` on golgiBody and re-encode.
> **Ref**: `fossilRecord/.../RUSTDESK_CONFIG.md` (wave115 — original enrollment doc)

### 5c: Report RustDesk ID

After RustDesk starts with relay config, report your RustDesk ID in the bootstrap AAR. This ID is used by overwatch for remote access via `relay.primals.eco`.

---

## K-DERM MEMBRANE TOPOLOGY

```
Internet (extracellular)
    │
    ▼ [Cloudflare TLS]
golgiBody-ext ──── OUTER MEMBRANE (primals.eco)
    │               Zola static site, sporePrint, publications
    │
golgiBody ──────── PERIPLASM (Forgejo + depot + Caddy TLS + RustDesk relay)
    │               push receiver, depot server, relay.primals.eco
    │
    ▼ [WireGuard mesh]
CYTOPLASM ──────── INNER MEMBRANE (primal.eco)
    │               NUCLEUS dogfooded on all gates
    │               All IPC via UDS + songBird mesh + swarmVine gossip
    │               No SSH, no external HTTP, no NanoWire patterns
    │
PEPTIDOGLYCAN ──── nestgate.io (primal-served data surface)
                    petalTongue on sporeGate: /depot/, /cas/, /provenance/
```

**Inner membrane rule**: All gate-to-gate communication uses ecoPrimals compositions (songBird mesh, capability.call, gossip.inject, riboCipher framing). Forgejo is outside — public internet → golgiBody.

**Tower Atomic**: bearDog (crypto) + songBird (routing) + skunkBat (defense) + swarmVine (gossip) = shared electron cloud. Every gate runs Tower before any workload.

---

*Universal gate spin-up. Platform-adaptive. Wave 159. 16 primals. 3 gates + golgiBody online, northGate enrolling. 0/0/0. Windows 16/16 compile. SSH retired for dispatch. 5-target depot. 8 architecture families. The ecobin standard and G68 platform abstractions mean any chip + drive = mesh gate.*
