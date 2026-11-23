> **SUPERSEDED** — This gate-specific blurb is retained as historical reference.
> The universal replacement is `GATE_SPINUP_BLURB.md` (platform-adaptive, all gates).
> graftGate Tower Atomic was successfully built from this blurb (Aug 11, 2026).

# graftGate Bootstrap Blurb — Wave 157i

**Date**: Aug 11, 2026 | **Wave**: 157i | **From**: eastGate overwatch
**Gate**: graftGate (M4 Mac Mini, Apple Silicon, `aarch64-apple-darwin`)
**Network**: iPhone XS USB tethering (ecoPrimal user) → LAN later
**Purpose**: First apple-darwin gate. Self-builds depot binaries. 12th gate in mesh.

**Prerequisites already done**: macOS setup, named graftGate, Remote Login (SSH) enabled, xcode-select CLI tools installed, RustDesk installed + permissions granted, Cursor installed.

**This blurb picks up from here.** Four phases: connectivity → sync → build → enrollment.

---

## PHASE 0: CONNECTIVITY — Forgejo Access

Forgejo (`git.primals.eco`) runs on golgiBody, a **public VPS**. No WireGuard needed.

### Install Homebrew (macOS package manager)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

After it finishes, run what it tells you (adds brew to PATH):

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

Verify: `brew --version`

### Install Rust

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

Hit `1` for default. Then:

```bash
source "$HOME/.cargo/env"
rustc --version
```

### SSH Key + Forgejo

```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_ecoPrimal -C "graftGate@primals.eco"
cat ~/.ssh/id_ed25519_ecoPrimal.pub
```

Register the public key in Forgejo: `https://git.primals.eco` → Settings → SSH/GPG Keys → Add Key.

SSH config — create `~/.ssh/config`:

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

Verify:

```bash
ssh -T git@git.primals.eco
# Should return: "Hi <user>! You've successfully authenticated..."
```

If SSH isn't set up yet, HTTPS works immediately for read-only:

```bash
git clone https://git.primals.eco/ecoPrimals/bearDog.git primals/bearDog
```

---

## PHASE 1: SYNC — Pull All Repos

### What is ecoPrimals

ecoPrimals is a sovereign, AGPL-3.0 mesh operating system built in pure Rust.
16 primals (autonomous binaries) compose into **atomics**: Tower (security +
discovery + defense), Node (Tower + compute), Nest (Tower + storage +
provenance), and NUCLEUS (all 13 + swarmVine gossip + surfaces). biomeOS
orchestrates via a Neural API with 27 signal graphs and semantic dispatch.
All binaries ("genomeBins") are served from a single depot on golgiBody
(`https://depot.primals.eco`). Gates are physical machines running compositions.

### Current State (Wave 157i — Aug 11, 2026)

| Fact | Value |
|------|-------|
| Wave | 157i (PANDEMIC RESPONDS) |
| Primals | **16** (13 NUCLEUS + swarmVine + petalTongue + squirrel) |
| Tests | **~150K+** across 16 primals + gardens + springs |
| biomeOS | **v4.57+** — Neural API, 27 signal graphs, `capability.call` fleet-wide |
| BTSP | **16/16** — all primals ship bearDog ClientHello |
| Depot | **49+ binaries** (18 musl + 16 gnu + 15 windows). BLAKE3 verified. **No apple-darwin yet — graftGate self-builds.** |
| Gates | **6 NUCLEUS** (westGate, strandGate, blueGate, sporeGate, southGate, ironGate). All 157e deployed. |
| Gossip | **6/16 primals LIVE** (4-gate cross-gate mesh) |
| P0 / P1 / P2 | **0 / 0 / 1** (petalTongue port) |
| G72 | **Tier 1 COMPLETE** (9/9 teams, ~114 crates shed). Tier 2 queued. |
| Glacial goals | 67+ tracked (17 COMPLETE, 21 ACTIVE, 24 GLACIAL) |

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
│   ├── initioChem       # Computational chemistry
│   ├── metalForge       # Metal fabrication
│   └── blueFish         # (placeholder)
├── springs/        # Science and domain apps (Forgejo org: syntheticChemistry/)
│   ├── primalSpring     # Scenario validation + composition experiments
│   ├── hotSpring        # Lattice QCD — GPU HMC simulations
│   ├── wetSpring        # Biodiversity + spectral analysis
│   └── (others)         # airSpring, groundSpring, healthSpring, etc.
├── protists/       # Proto-karya (Forgejo org: protoKarya/)
│   └── tideGlass        # NF drug repurposing — GPS platform rebuild
└── infra/          # Infrastructure and documentation
    ├── wateringHole      # Standards, handoffs, blurbs (ecoPrimals/)
    ├── plasmidBin        # Depot binaries + enrollment scripts (ecoPrimals/)
    ├── sporePrint        # Public website (ecoPrimals/)
    ├── whitePaper        # Research papers (ecoPrimals/)
    └── (others)          # agentReagents, benchScale (syntheticChemistry/)
```

### Clone All Repos

graftGate is a fresh gate — clone everything from scratch:

```bash
mkdir -p ~/Development/ecoPrimals/{primals,gardens,springs,protists,infra}
cd ~/Development/ecoPrimals

# Detect SSH vs HTTPS
if ssh -T git@git.primals.eco 2>&1 | grep -q "successfully authenticated"; then
  PROTO="ssh"
  url() { echo "ssh://git@git.primals.eco:2222/$1/$2.git"; }
  echo "Using SSH"
else
  PROTO="https"
  url() { echo "https://git.primals.eco/$1/$2.git"; }
  echo "Using HTTPS (read-only — set up SSH later for push)"
fi

# Primals (ecoPrimals org)
for p in bearDog songBird skunkBat nestGate rhizoCrypt loamSpine sweetGrass \
         toadStool barraCuda coralReef biomeOS squirrel petalTongue swarmVine \
         sourDough bingoCube; do
  [ -d "primals/$p" ] || git clone "$(url ecoPrimals $p)" "primals/$p"
done

# Gardens (sporeGarden org)
for g in cellMembrane esotericWebb lithoSpore projectFOUNDATION projectNUCLEUS \
         helixVision initioChem metalForge blueFish; do
  [ -d "gardens/$g" ] || git clone "$(url sporeGarden $g)" "gardens/$g"
done

# Springs (syntheticChemistry org)
for s in primalSpring hotSpring wetSpring airSpring groundSpring healthSpring \
         ludoSpring neuralSpring rustChip; do
  [ -d "springs/$s" ] || git clone "$(url syntheticChemistry $s)" "springs/$s"
done

# Protists (protoKarya org)
for t in tideGlass; do
  [ -d "protists/$t" ] || git clone "$(url protoKarya $t)" "protists/$t"
done

# Infra (mixed orgs)
for i in wateringHole plasmidBin sporePrint whitePaper; do
  [ -d "infra/$i" ] || git clone "$(url ecoPrimals $i)" "infra/$i"
done
for i in agentReagents benchScale primalSpring; do
  [ -d "infra/$i" ] || git clone "$(url syntheticChemistry $i)" "infra/$i" 2>/dev/null
done
```

### Verify Sync

```bash
cd ~/Development/ecoPrimals
echo "=== Repo count ==="
find primals gardens springs protists infra -maxdepth 1 -name '.git' -prune -o -type d -mindepth 1 -maxdepth 1 -print 2>/dev/null | wc -l

echo "=== Read ecosystem blurb ==="
head -5 infra/wateringHole/handoffs/ECOSYSTEM_BLURB.md
```

---

## PHASE 2: BUILD — First `aarch64-apple-darwin` Binaries

graftGate **self-builds** — there are no apple-darwin binaries in the depot yet.
This gate creates them. Start with Tower Atomic (bearDog + songBird + skunkBat).

### Build Tower Atomic

```bash
cd ~/Development/ecoPrimals

# bearDog (trust foundation)
cd primals/bearDog && cargo build --release && cd ../..
echo "bearDog: $(ls -lh primals/bearDog/target/release/beardog | awk '{print $5}')"

# songBird (discovery + mesh)
cd primals/songBird && cargo build --release && cd ../..
echo "songBird: $(ls -lh primals/songBird/target/release/songbird | awk '{print $5}')"

# skunkBat (defense)
cd primals/skunkBat && cargo build --release && cd ../..
echo "skunkBat: $(ls -lh primals/skunkBat/target/release/skunkbat | awk '{print $5}')"
```

This is the **proof of `aarch64-apple-darwin`** — the first apple-darwin primal
binaries in the ecosystem's history. Record the binary sizes.

### Install Tower Binaries

```bash
mkdir -p ~/.local/bin
for primal in beardog songbird skunkbat; do
  src=$(find primals -name "$primal" -path "*/release/$primal" -type f 2>/dev/null | head -1)
  if [ -n "$src" ]; then
    cp "$src" ~/.local/bin/
    chmod +x ~/.local/bin/$primal
    echo "Installed: $primal"
  fi
done

# Add to PATH if not already there
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zprofile
export PATH="$HOME/.local/bin:$PATH"
```

### Validate Tower

```bash
# Start bearDog and verify
beardog &
sleep 2
# Check if it's listening
lsof -i -P | grep beardog

# Start songBird
songbird &
sleep 2
lsof -i -P | grep songbird

# Start skunkBat
skunkbat &
sleep 2
lsof -i -P | grep skunkbat
```

### Build Remaining NUCLEUS Primals (optional — after Tower validates)

```bash
cd ~/Development/ecoPrimals
for primal in nestGate rhizoCrypt loamSpine sweetGrass toadStool barraCuda \
              coralReef biomeOS squirrel petalTongue swarmVine sourDough; do
  echo "=== Building $primal ==="
  (cd "primals/$primal" && cargo build --release 2>&1 | tail -3) || echo "FAILED: $primal"
done
```

Note: some primals may need macOS-specific fixes (first apple-darwin builds).
Report any compilation failures in the handoff — these are expected and valuable.

---

## PHASE 3: ENROLLMENT — Mesh + Depot

### WireGuard (when ready for mesh — not required for building)

Install WireGuard for macOS:

```bash
brew install wireguard-tools
```

Generate keys:

```bash
wg genkey | tee /tmp/wg-privatekey | wg pubkey > /tmp/wg-publickey
cat /tmp/wg-publickey
# Send this public key to eastGate overwatch for registration on golgiBody
```

Create config (overwatch will assign your mesh IP):

```bash
sudo mkdir -p /etc/wireguard
sudo tee /etc/wireguard/wg0.conf << 'WGEOF'
[Interface]
Address = ASSIGNED_IP/24
PrivateKey = CONTENTS_OF_PRIVATEKEY
ListenPort = 51821

[Peer]
# golgiBody (hub)
PublicKey = A2fvz3czkqRUuu2mzkSS6IVr/TCQcpsJX9HbDBa1FBc=
Endpoint = [RELAY_PUBLIC]:51820
AllowedIPs = 10.13.37.0/24
PersistentKeepalive = 25
WGEOF
```

Bring up the tunnel:

```bash
sudo wg-quick up wg0
ping -c 3 10.13.37.1
```

macOS note: WireGuard also has a Mac App Store GUI app if you prefer that over CLI.

### Gate Enrollment

Once WireGuard is up and Tower Atomic is running:

```bash
cd ~/Development/ecoPrimals/infra/plasmidBin
bash gate-enroll.sh
```

### Push apple-darwin Binaries to Depot

Once Tower Atomic compiles and validates, push the binaries to golgi to create
the new `aarch64-apple-darwin` depot directory:

```bash
# SCP binaries to golgi (requires SSH access to golgiBody)
for primal in beardog songbird skunkbat; do
  scp ~/.local/bin/$primal golgi:/opt/ecoPrimals/plasmidBin/primals/aarch64-apple-darwin/
done
```

This makes apple-darwin binaries available fleet-wide for future macOS gates.

---

## PHASE 4: REPORT

File your bootstrap report as:
`infra/wateringHole/handoffs/GRAFTGATE_BOOTSTRAP_AAR.md`

Report:
- macOS version and M4 chip details (`system_profiler SPHardwareDataType`)
- Rust toolchain version (`rustc --version`, `cargo --version`)
- Tower Atomic binary sizes (first apple-darwin binaries — record for depot)
- Any compilation failures (expected — first darwin builds)
- Any macOS-specific issues (launchd, sandboxing, Gatekeeper, SIP)
- WireGuard status (if enrolled)
- Depot push status (if completed)

---

## Key Standards

| Standard | Path |
|----------|------|
| Ecosystem posture | `infra/wateringHole/handoffs/ECOSYSTEM_BLURB.md` |
| Orthogonal review | `infra/wateringHole/ORTHOGONAL_DIMENSIONS_REVIEW.md` |
| Architecture | `infra/wateringHole/fossilRecord/wave150s_standards/ECOBIN_ARCHITECTURE_STANDARD.md` |
| Method naming | `infra/wateringHole/protocols/SEMANTIC_METHOD_NAMING_STANDARD.md` |
| G72 Dep Pandemic | `infra/wateringHole/specs/DEPENDENCY_PANDEMIC_SPEC.md` |

## Convergence Rule

> **eastGate owns the codebase.** graftGate is a gate team — deployment
> validator and self-builder for the apple-darwin target.
>
> 1. **DO NOT** push code changes (except wateringHole handoffs/AARs).
> 2. **Report compilation failures** — these are first-ever darwin builds.
> 3. **File findings** as `infra/wateringHole/handoffs/GRAFTGATE_*.md`.
> 4. **Pull from Forgejo regularly** to stay converged.

## K-Derm Three-Layer Model

```
OUTER MEMBRANE — Human access (RustDesk → relay.primals.eco)
PEPTIDOGLYCAN  — LAN topology fabric (NAT, DNS, switches)
INNER MEMBRANE — Primal IPC (WireGuard wg0 + songBird :7700 + BTSP)
```

Forgejo is OUTSIDE the inner membrane — public internet → golgiBody.
WireGuard is only for primal-to-primal IPC and mesh enrollment.
graftGate connects to LAN via ethernet/WiFi once iPhone tether is no longer needed.

---

*graftGate — M4 Mac Mini. First `aarch64-apple-darwin` gate. Apple tree graft: foreign scion onto primal rootstock. Wave 157i.*
