# sporeGate: Build Mesh + Topology Update

**Wave**: 155b | **From**: eastGate overwatch
**Context**: Track B Fleet Convergence — compositions fixed, blueGate joining as builder

---

## WHAT CHANGED

### 1. Composition Profiles Fixed (ecosystem_manifest.toml)

`compute` and `nest` compositions were missing Tower Atomic base primals.
Every running gate needs bearDog (crypto) + songBird (mesh) + skunkBat (audit).

**Before:**
```toml
[compositions.compute]
primals = ["toadStool", "barraCuda", "coralReef", "biomeOS"]

[compositions.nest]
primals = ["nestGate", "rhizoCrypt", "loamSpine", "sweetGrass"]
```

**After:**
```toml
[compositions.compute]
primals = ["bearDog", "songBird", "skunkBat", "toadStool", "barraCuda", "coralReef", "biomeOS"]

[compositions.nest]
primals = ["bearDog", "songBird", "skunkBat", "nestGate", "rhizoCrypt", "loamSpine", "sweetGrass"]
```

Now aligned with `ports.env` `COMP_NODE` and `COMP_NEST`. The `MembraneComposition`
ladder tier (`Tower` for compute, `Nest` for nest) still controls trust/firewall.
The manifest profile controls what primals to deploy.

### 2. blueGate Joins as Distributed Builder

blueGate manifest entry has `build_authority = true` and `composition = "tower"`.
It runs Tower Atomic (3 primals) + build toolchain.

**Foreman pattern**: sporeGate is primary build authority. blueGate is a distributed
builder under sporeGate's foreman. When cascade detects drift, build authority gates
auto-harvest. blueGate builds from its own workspace (all repos cloned from Forgejo).

New profile: `profiles/tower-builder.toml` — Tower Atomic + `build.authority = true`,
`build.foreman = "sporeGate"`.

`deploy_gate.sh` now supports `--build-authority` flag to set `MEMBRANE_BUILD_AUTHORITY=1`
in `tower.env`.

### 3. Checksum Verification Fix (cellMembrane)

`gate/verify.rs` had its own `ChecksumEntry` struct that couldn't parse plain-string
format in `checksums.toml` (e.g. `beardog = "hash"`). Now uses the shared
`checksum::ChecksumEntry` which handles both `"hash"` and `{ blake3 = "hash", size = N }`.

All 5 enrolling gates pass 12/13 bootstrap phases in dry-run (the 1 failure is expected:
no local binaries in depot dir when running from eastGate).

---

## WHAT YOU NEED TO DO

### Build Fresh Depot — golgiBody Only (P0)

golgiBody is the **sole depot**. No local depots. The depot has Wave 142b binaries.
The 5 enrolling gates need current genomeBins for **both Linux and Windows**.

sporeGate should:

1. **Cascade**: `membrane temporal.cascade --source forgejo`
2. **Harvest Linux**: `membrane plasmid.harvest --local --target x86_64-unknown-linux-musl`
3. **Harvest Windows**: `membrane plasmid.harvest --local --target x86_64-pc-windows-gnu`
   (blueGate + swiftGate are Windows — need `.exe` genomeBins)
4. **Push to golgi**: `rsync -avz infra/plasmidBin/primals/ golgi:/opt/ecoPrimals/depot/primals/`
5. **Sign**: `membrane plasmid.sign` (updates signatures.toml)

### Prepare blueGate Builder (P1)

Once blueGate is enrolled and meshed:

1. SSH in, verify Tower Atomic is running: `systemctl status beardog-membrane songbird-membrane skunkbat-membrane`
2. Verify build toolchain: `rustup show`, `which cargo`
3. Set `MEMBRANE_BUILD_AUTHORITY=1` in `/opt/membrane/tower.env`
4. Enable cascade timer: `membrane gate.quorum --interval 15`
5. Test harvest: `membrane plasmid.harvest --local --dry-run`

### Topology Awareness

sporeGate should know about the new storage/compute topology:

| Gate | Composition | Platform | Hardware Update | Role |
|------|-------------|----------|-----------------|------|
| westGate | `nest` (7 primals) | Linux | 5x 14TB HDD (70TB raw ZFS cold pool) | Cold storage — NestGate CAS backend |
| ironGate | `full` (13 primals) | Linux | 14TB+1TB+1TB+~2TB HDD enclave | Encrypted data compartments, GPU compute |
| blueGate | `tower` (3 primals) | **Windows** | Existing | Distributed builder, media/gaming |
| strandGate | `compute` (7 primals) | Linux | Existing | GPU/HPC compute workhouse |
| swiftGate | `full` (13 primals) | **Windows** | Existing | Hobby/consumer — house2 northGate equivalent |

### Harvest Priority

When building for the fleet, composition-aware harvest means:

- **Tower gates** (blueGate): only need beardog, songbird, skunkbat
- **Compute gates** (strandGate): Tower + toadstool, barracuda, coralreef, biomeos
- **Nest gates** (westGate): Tower + nestgate, rhizocrypt, loamspine, sweetgrass
- **Full gates** (ironGate, swiftGate, southGate): all 13 primals

golgiBody is the sole depot. It must have all 13 primals for **both Linux musl and
Windows gnu** architectures. Gate-side `gate.bootstrap` auto-detects the platform
and fetches the right genomeBins for each composition via `resolve_gate_primals()`.

**genomeBin evolution**: ecoBins → genomeBins. Silicon-deistic deployment — OS is
an abstraction layer. The codebase compiles to 14+ Cargo target triples (see Wave
140a AAR). Unix/Windows/Android/iOS are jelly strings to abstract across. Self-enrollment
means gates declare their own name, composition, and architecture. golgiBody serves
the right binaries.

---

## CONTEXT FILES

| File | What |
|------|------|
| `infra/wateringHole/ecosystem_manifest.toml` | Composition profiles + gate entries |
| `infra/plasmidBin/profiles/tower-builder.toml` | blueGate builder profile |
| `infra/plasmidBin/deploy_gate.sh` | `--build-authority` flag added |
| `gardens/cellMembrane/crates/membrane-shadow/src/gate/verify.rs` | Checksum fix |
| `gardens/cellMembrane/crates/membrane-shadow/src/plasmid/mod.rs` | `checksum` module now `pub(crate)` |
| `infra/plasmidBin/enroll/gate-enroll.sh` | Post-enrollment instructions updated |
