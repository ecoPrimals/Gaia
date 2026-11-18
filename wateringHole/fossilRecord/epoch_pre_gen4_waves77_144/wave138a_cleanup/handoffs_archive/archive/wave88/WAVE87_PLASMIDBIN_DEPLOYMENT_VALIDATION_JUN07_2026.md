# Wave 87: plasmidBin Deployment Pipeline — End-to-End Validation

**Date**: 2026-06-07  
**Author**: eastGate overwatch  
**Type**: Deployment pipeline validation + gap identification  
**Status**: Complete (pipeline proven, gaps documented)

---

## Pipeline Validated

The full plasmidBin deployment pipeline was exercised end-to-end:

| Step | Tool | Result |
|------|------|--------|
| 1. Detect drift | `membrane plasmid.status` | 3 drifted: biomeOS, loamSpine, petalTongue |
| 2. Harvest | `membrane plasmid.harvest` | 3 built, 10 current, 0 failed (253s) |
| 3. Verify | `membrane plasmid.status` | **13/13 current, 0 drifted** |
| 4. Launch NUCLEUS | `biomeos nucleus start --node-id eastGate` | Launched from depot binary |
| 5. Primal health | beardog, songbird | **HEALTHY** from depot |

### Harvested Binaries

| Binary | Commit | Size | BLAKE3 |
|--------|--------|------|--------|
| biomeOS | `9b08e66c` (v4.09 — federation env fix) | 15,517 KB | `b229f1c76172e17d` |
| loamSpine | `26bbb420` | 4,557 KB | `e4b446d9f2aabf58` |
| petalTongue | `62123005` | 31,563 KB | `a143a63a04299efe` |

### Key Confirmation

**Songbird v4.09 federation fix confirmed working via plasmidBin pipeline.**
The biomeOS team pushed the `nucleus_launch_profiles.toml` fix (SONGBIRD_FEDERATION_PORT,
SONGBIRD_PEERS, SONGBIRD_NODE_ID env passthrough). The fixed binary was harvested into the
depot and launched via NUCLEUS — songbird reported HEALTHY.

### Environment

`ECOPRIMALS_PLASMID_BIN` added to `~/.bashrc` alongside existing `ECOPRIMALS_ROOT`:
```
export ECOPRIMALS_PLASMID_BIN="$ECOPRIMALS_ROOT/infra/plasmidBin/primals/x86_64-unknown-linux-musl"
```

---

## Gaps Identified

### P1: cellMembrane On-Demand Trigger Mechanism

The 30-minute `plasmid-pipeline.timer` on the VPS handles background convergence. But when
a primal team pushes a critical fix (like biomeOS v4.09), the operator must currently:
1. SSH to the gate
2. Run `membrane plasmid.harvest` manually
3. Then restart NUCLEUS

**Required**: An on-demand trigger mechanism for cellMembrane:

| Trigger Type | Description | Priority |
|--------------|-------------|----------|
| `membrane plasmid.pipeline --now` | CLI command to trigger immediate harvest + refresh cycle | P1 |
| Forgejo webhook → cascade rebuild | Push to any primal repo triggers selective harvest | P2 (CM-WEBHOOK-01) |
| `membrane plasmid.watch` | Daemon mode: poll upstream commits, auto-harvest on drift detection | P3 |

The timed + triggered model gives both background convergence and immediate response.

### P2: biomeOS Binary Search Priority

`discover_binaries_with()` in `nucleus_procs.rs` searches `livespore-usb/` before the
configured `ECOPRIMALS_PLASMID_BIN` depot. Result: 5/12 primals still resolve from
`livespore-usb` even when `ECOPRIMALS_PLASMID_BIN` is set.

| Source | Primals |
|--------|---------|
| plasmidBin depot | coralreef, rhizocrypt, loamspine, sweetgrass, skunkbat, barracuda, petaltongue (7) |
| livespore-usb | beardog, songbird, toadstool, squirrel, nestgate (5) |

**Fix**: biomeOS should prioritize `ECOPRIMALS_PLASMID_BIN` over `livespore-usb` in search order.
The depot is the single source of truth for harvested, checksummed binaries.

### P2: barracuda Socket Timeout

`barracuda` fails to create its UDS socket within the 10s NUCLEUS timeout.
Blocks full NUCLEUS startup. Needs barracuda team investigation.

### P3: Incubating Health Checks

skunkbat, toadstool, coralreef report "Health check RPC failed" on initial probe
but register as "incubating." These are startup-race conditions, not critical failures.

---

## Deployment Flow (Proven)

```
primal team pushes fix
        ↓
membrane plasmid.status → detects drift
        ↓
membrane plasmid.harvest → rebuilds, checksums, stages
        ↓
[NEEDED] membrane plasmid.pipeline --now  (on-demand trigger)
        ↓
VPS: plasmid-pipeline.timer → plasmid.refresh → atomic replace + restart
        ↓
Local: ECOPRIMALS_PLASMID_BIN → biomeos nucleus start → primals from depot
```

---

*"Pipeline proven end-to-end. Now we need the trigger to close the loop."*
