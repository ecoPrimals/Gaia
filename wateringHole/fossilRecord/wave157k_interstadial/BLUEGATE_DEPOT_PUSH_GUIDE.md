# blueGate Depot Push Guide — sporeGate Response to 157b AAR

**Gate**: sporeGate | **Date**: 2026-08-09 | **Recipients**: blueGate team
**Re**: blueGate 157b AAR — depot push mechanism, build flags, and findings response

---

## #1 BLOCKER: DEPOT PUSH MECHANISM

The existing `membrane plasmid.harvest --local --push` already works on Windows.
It uses OpenSSH's `scp` binary (which blueGate confirms is installed).

### SSH Config Setup

Add the golgi SSH alias to `~/.ssh/config` (or `C:\Users\<user>\.ssh\config`):

```
Host golgi
    HostName [RELAY_PUBLIC]
    User root
    Port 22
    IdentityFile ~/.ssh/id_ed25519
    StrictHostKeyChecking accept-new
    ConnectTimeout 10
```

**Key**: Use the same ed25519 key that's authorized on golgiBody. If blueGate
doesn't have a key authorized on golgi, coordinate with sporeGate topology to
add blueGate's public key to golgi's `~/.ssh/authorized_keys`.

### Push Workflow

```powershell
# Build all primals locally
membrane.exe plasmid.harvest --local --target x86_64-pc-windows-gnu

# Push to golgi depot (SCP per-binary, BLAKE3 diff detection)
membrane.exe plasmid.harvest --local --target x86_64-pc-windows-gnu --push

# Or push separately after build:
membrane.exe plasmid.depot_sync --push
```

The `--push` flag calls `depot_sync_push` which:
1. Walks all arch dirs in local depot
2. BLAKE3-hashes each binary locally
3. Compares with remote BLAKE3 via SSH
4. SCP-copies only changed binaries (atomic: copy to `.new`, rename)
5. Pushes `checksums.toml` + `provenance.toml` + `signatures.toml`

### Environment Variables (optional)

```powershell
# Override SSH host alias (default: "golgi")
$env:MEMBRANE_SSH_HOST = "golgi"

# Override VPS root path (default: /home/sporegate/Development/ecoPrimals)
$env:VPS_ECOPRIMALS_ROOT = "/home/sporegate/Development/ecoPrimals"
```

---

## #2: CROSS-BUILD FLAGS PER PRIMAL

sporeGate uses these exact flags when cross-building for `x86_64-pc-windows-gnu`:

```bash
# Standard primal (most primals)
cargo build --release --target x86_64-pc-windows-gnu -p <crate-name>

# Key: -p targets the SPECIFIC crate, not the workspace root.
# This avoids pulling in test binaries and workspace-wide deps.
```

### Per-primal crate names:

| Primal | Crate flag | Notes |
|--------|-----------|-------|
| beardog | `-p beardog` | |
| songbird | `-p songbird` | |
| skunkbat | `-p skunkbat` | |
| nestgate | `-p nestgate` | |
| rhizocrypt | `-p rhizocrypt` | |
| loamspine | `-p loamspine` | |
| sweetgrass | `-p sweetgrass` | |
| toadstool | `-p toadstool` | |
| barracuda | `-p barracuda` | NOT `-p barracuda-core` alone |
| coralreef | `-p coralreef` | |
| biomeos | `-p biomeos` | Largest, longest build |
| squirrel | `-p squirrel` | |
| petaltongue | `-p petaltongue` | |
| sourdough | `-p sourdough` | |
| swarmvine | `-p swarmvine` | 16th primal, verify Windows |
| membrane | `-p membrane-shadow` | Builder itself |

### barraCuda Size Fix

The 4.4x size discrepancy (22 MB native vs 5 MB cross) is because building from
workspace root links ALL workspace binaries. Fix:

```powershell
# WRONG (builds entire workspace, 22MB):
cargo build --release

# RIGHT (builds just barracuda server, ~5MB):
cd primals\barraCuda
cargo build --release -p barracuda
```

### LTO Configuration

Cross-builds use whatever `[profile.release]` is in each primal's `Cargo.toml`.
Most primals have `lto = true` in their release profile. If native Windows builds
are oversized, check that you're building with `--release` and not `--profile dev`.

---

## #3: BLAKE3SUMS FOR WINDOWS DEPOT

This is already wired. After `plasmid.harvest --local`, run:

```powershell
membrane.exe depot.integrity --generate
```

This generates both `checksums.toml` and per-arch `BLAKE3SUMS` files
(GNU-compatible format) in each arch directory.

---

## #4: SONGBIRD PID PATH — ACKNOWLEDGED P2

We acknowledge the 3-wave PID path instability. The canonical path going forward is:

**Windows**: `C:\ProgramData\songbird\songbird-<gate>.pid`
**Linux**: `/run/membrane/songbird.pid` (managed by systemd)

The PID liveness validation recommendation is filed for songBird team. Until then,
the workaround is to delete stale PID files before restart:

```powershell
Remove-Item "C:\ProgramData\songbird\songbird-blueGate.pid" -ErrorAction SilentlyContinue
```

---

## #5: PETALTONGUE PORT — KNOWN, LOW PRIORITY

petalTongue's `--port` in `server` mode is a known issue. On Windows, petalTongue
is reachable only via UDS-equivalent (named pipe) or the discovery port that
biomeOS advertises. This is P3 — not blocking sub-builder utility.

---

## #6: MEMBRANE.EXE REBUILD

membrane.exe should be built from cellMembrane workspace:

```powershell
cd gardens\cellMembrane
cargo build --release -p membrane-shadow --target x86_64-pc-windows-gnu
copy target\x86_64-pc-windows-gnu\release\membrane.exe <depot-path>\primals\x86_64-pc-windows-gnu\membrane.exe
```

The new membrane includes `builder.serve` for mesh-native build dispatch.

---

## #7: SWARMVINE ON WINDOWS

swarmVine should compile for Windows — it's pure Rust with no platform-specific
deps. Test with:

```powershell
cd primals\swarmVine
cargo build --release -p swarmvine --target x86_64-pc-windows-gnu
```

If it compiles, add `swarmvine.exe` to the Windows depot alongside the other 14.

---

## IMMEDIATE NEXT STEPS (Priority Order)

1. **Set up SSH config for golgi** — enables `--push` to work
2. **Rebuild membrane.exe** from cellMembrane with builder.serve support
3. **Test `plasmid.harvest --local --push`** — verify SCP to golgi works from Windows
4. **Build swarmVine** — add 16th primal to Windows depot
5. **Run `depot.integrity --generate`** — generate BLAKE3SUMS for Windows arch
6. **Start `membrane.exe builder.serve --port 9800`** — enable mesh dispatch from sporeGate

Once steps 1-3 are confirmed, blueGate is a fully operational primary builder
with autonomous push capability.

---
*FOSSILIZED Wave 157k interstadial (Aug 13, 2026). Content superseded by ECOSYSTEM_BLURB.md and current ecosystem standards.*
