# Wave 49 — Post-Primordial Deployment + Covalent Mesh

**Date**: May 25, 2026
**From**: primalSpring (eastGate)
**To**: ALL spring teams (wetSpring, ludoSpring, neuralSpring, airSpring, groundSpring, healthSpring, hotSpring)

---

## Two things to do

### 1. Cut all primordial patterns — deploy from plasmidBin only

We are **post-primordial**. All primal binaries must come from `plasmidBin`.
This applies to every spring on every gate, effective immediately.

**What to cut:**

- Remove any primal binaries from `~/.local/bin/` (stubs, symlinks, direct builds)
- Remove any `cargo install` or `cargo build --release` patterns for deploying primals
- Remove any `which beardog`/`which songbird`/etc. fallback logic
- Remove any `target/release/` paths used for deployment
- Stop building primals from source for deployment — plasmidBin is the depot

**Verify you're clean:**

```bash
# These should all return empty (no primals in PATH outside plasmidBin):
for p in beardog songbird biomeos toadstool barracuda coralreef nestgate \
         squirrel rhizocrypt loamspine sweetgrass skunkbat petaltongue; do
    w=$(which $p 2>/dev/null) && echo "STALE: $p -> $w"
done

# This should be your sole binary source:
ls infra/plasmidBin/primals/x86_64-unknown-linux-musl/
```

**If your spring has its own launcher scripts** that call primals directly,
update them to source from plasmidBin. The primalSpring `nucleus_launcher.sh`
now auto-detects the git checkout at `infra/plasmidBin/primals/{triple}/` —
no env vars needed.

### 2. Start NUCLEUS from plasmidBin with LAN federation

```bash
# Pull latest primalSpring (has the plasmidBin auto-detect + bind fix):
cd springs/primalSpring && git pull

# Pull latest plasmidBin:
cd infra/plasmidBin && git pull

# Start NUCLEUS — auto-detects plasmidBin, binds federation to all interfaces:
cd springs/primalSpring
SONGBIRD_FEDERATION_PORT=7700 ./tools/nucleus_launcher.sh start
```

That's it. The launcher:
- Finds binaries in `infra/plasmidBin/primals/x86_64-unknown-linux-musl/`
- Starts all 13 primals over UDS
- Enables Songbird TCP on `0.0.0.0:7700` for LAN mesh
- Errors hard if any binary is missing (no silent fallback)

**Verify federation is LAN-reachable** (not loopback):

```bash
ss -tlnp | grep 7700
# Should show *:7700 — NOT 127.0.0.1:7700
```

**Verify discovery:**

```bash
# Over UDS (always works):
echo '{"jsonrpc":"2.0","id":1,"method":"discovery.peers","params":{}}' | \
  socat - UNIX-CONNECT:/run/user/$(id -u)/biomeos/songbird-*.sock

# Over TCP from another gate (replace IP with your gate's LAN IP):
echo '{"jsonrpc":"2.0","id":1,"method":"discovery.peers","params":{}}' | \
  socat - TCP:192.168.1.144:7700,connect-timeout=5
```

eastGate is live at **192.168.1.144:7700** — you should be able to reach it now.

---

## Known pipeline debt (workarounds included)

| Issue | Workaround |
|-------|------------|
| petalTongue musl binary rejects `--family-id` | Pass via env: `FAMILY_ID=nucleus01`; launcher handles this automatically |
| petalTongue stale socket on restart (EADDRINUSE) | `rm /run/user/$(id -u)/biomeos/petaltongue-*.sock` before restart |
| loamSpine Tokio runtime-in-runtime panic | Upstream bug — does not block mesh. Skip loamSpine health probe if needed. |
| Songbird sled DB corruption after unclean shutdown | Clean `~/.local/share/songbird/task_lifecycle*` and restart |

---

## Gate roster (8/8 sounded off)

| Spring | Gate | Status |
|--------|------|--------|
| primalSpring | eastGate + ironGate | **operational** — plasmidBin, federation 0.0.0.0:7700 |
| airSpring | eastGate | **operational** |
| groundSpring | eastGate | **operational** |
| ludoSpring | ironGate | **operational** (12/12 proto-nucleate) |
| healthSpring | ironGate | **operational** (23 UDS, 4 domain caps) |
| wetSpring | southGate | **operational** (V185) |
| neuralSpring | southGate | **operational** (9/13 UDS) |
| hotSpring | biomeGate | **operational** |

## Next: verify cross-gate mesh

Once 2+ gates are running with plasmidBin + federation:

```bash
# Check if you see peers:
echo '{"jsonrpc":"2.0","id":1,"method":"discovery.peers","params":{}}' | \
  socat - UNIX-CONNECT:/run/user/$(id -u)/biomeos/songbird-*.sock

# Expected: {"result":{"peers":[{"gate":"eastGate",...}],"total_count":1}}
```

When 3+ gates are meshed: `biomeos plasmodium status` to see the collective.

---

**Upstream refs:**
- `WAVE48_COVALENT_SPRING_MESH_MAY25_2026.md` — full covalent handoff
- `PRIMALSPRING_WAVE49_COVALENT_EVOLUTION_MAY25_2026.md` — Wave 49 scenario + next steps
- `PLASMIDBIN_DEPOT_PATTERN.md` (primalSpring wateringHole) — binary discovery standard
- `DISTRIBUTED_COVALENT_DEPLOYMENT.md` (wateringHole root) — architecture
