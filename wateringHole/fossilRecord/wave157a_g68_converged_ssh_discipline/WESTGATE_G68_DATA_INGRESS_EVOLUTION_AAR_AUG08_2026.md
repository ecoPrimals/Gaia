# AAR: westGate G68 Data Ingress — Braiding, Federation, and Neural API Evolution

**Gate**: westGate | **Wave**: 157a (G68) | **Date**: Aug 8, 2026 10:00 AM
**Audience**: primalSpring team, overwatch, all gate operators
**Session**: Full cascade → gate redeploy → NG-05 → monitoring → this AAR

---

## Executive Summary

westGate is **fully operational on G68-converged depot binaries** with
**990,500 files braided inline during data ingress** across 3 datasets, all
committed to a single spine. The full provenance chain (nestGate → rhizoCrypt →
loamSpine → sweetGrass → bearDog) is live. songBird capability resolution
works — all 26 capabilities across 5 provenance primals resolve correctly.
biomeOS Neural API reports 679 registered capabilities but `capability.call`
still times out due to the Tower Atomic relay dispatch order issue. The
**riboCipher transport signal** (0xEC prefix) is enforced by G68 sweetGrass and
rhizoCrypt — `native_braid.py` already handles this. This AAR captures
everything primalSpring needs for Neural API compositional evolution.

---

## 1. Gate Redeploy — Depot, Not Build

**Pattern proven**: 17 musl-static binaries pulled from
`depot.primals.eco/primals/x86_64-unknown-linux-musl/` via HTTPS in ~15 seconds.
No local `cargo build`. SporeGate builds once, pushes to golgi, gates pull and
restart. Total redeploy: stop → pull → restart in dependency order → 13/13 alive.

**Key correction from overwatch**: Initial instinct was to rebuild from source
locally. "We should be deploying from golgi depot, not building." This is the
intended deployment topology. Gates are consumers, not builders.

**Service startup order matters**: provenance chain first (nestgate → loamspine →
rhizocrypt → sweetgrass → beardog), then biomeOS, then remaining primals. This
ensures dependencies are satisfied before consumers start.

---

## 2. Data Ingress — Inline Braiding Working

### Active Pipeline

AlphaFold full sync runs via systemd timer (`alphafold-sync.timer`, daily 03:00).
The sync script (`alphafold_full_sync.sh`) calls `native_braid.py --incremental`
after **every rsync phase** — this is the "atomic ingress" pattern where no data
lands without provenance.

```
rsync v1/ → cold    →  braid_now()
rsync v2/ → cold    →  braid_now()
  ...
rsync v6/ → cold    →  braid_now()
rsync sequences.fasta → cold  →  braid_now()
rsync metadata → cold  →  braid_now()
```

### Current State (Aug 8 10:00 AM)

| Dataset | Files Braided | Chunks | Dedup Hits | Merkle Roots |
|---------|--------------|--------|------------|--------------|
| alphafold (tars + metadata) | 324 | 7 (v1-v6 + _root) | 18 | 7 ✓ |
| alphafold_structures | 989,423 | 228 | 23,967 | 228 ✓ |
| sra_fastq | 753 | 5 | 351 | 5 ✓ |
| **Total** | **990,500** | **240** | **24,336** | **240 ✓** |

All on single spine: `019fd782-67d5-7903-8d2d-8ba369ca0490`

### Download Progress

- `sequences.fasta`: 5.1 GB of 118 GB (4.3%, actively rsyncing)
- AlphaFold v1-v6 proteome tars: COMPLETE
- AlphaFold structures: 228 organism directories on disk
- SRA FASTQ: 5 BioProjects (267 GB metagenomics), braided

### What "Inline Braiding" Means Concretely

Each `braid_now()` call runs `native_braid.py --incremental`, which:
1. Discovers new/changed chunks (subdirectories)
2. Stages files from cold (HDD) to warm (NVMe) tier
3. Streams BLAKE3 hashes (handles files >256 MB that `content.ingest` skips)
4. `content.put` to nestGate CAS (multi-tier: warm NVMe + cold ZFS)
5. `dag.event.append_batch` to rhizoCrypt (200 events per RPC)
6. `dag.dehydration.trigger` for Merkle root
7. `session.commit` to loamSpine spine
8. `braid.batch_create` to sweetGrass

The script is crash-resumable via `.native_braid_state` files per dataset. Workers
claim chunks via lock files. Incremental mode detects both new chunks and grown
chunks (new files in existing directories).

---

## 3. Provenance Chain — G68 Binary Behavior

### What Works

| Primal | Method | Status | Notes |
|--------|--------|--------|-------|
| nestGate | `health.check` | ✓ | v0.5.0, TCP 0.0.0.0:8080, UDS |
| nestGate | `content.get` | ✓ | Returns data or null, BLAKE3 validation |
| nestGate | `content.exists` | ✓ | Boolean existence check |
| nestGate | `content.put` | ✓ | Multi-tier CAS (warm NVMe + cold ZFS) |
| rhizoCrypt | `health.check` | ✓ | Requires riboCipher prefix |
| rhizoCrypt | `dag.event.append_batch` | ✓ | Requires riboCipher prefix |
| rhizoCrypt | `dag.session.create` | ✓ | Requires riboCipher prefix |
| rhizoCrypt | `dag.dehydration.trigger` | ✓ | Requires riboCipher prefix |
| loamSpine | `health.check` | ✓ | v0.5.0, UDS + tarpc |
| loamSpine | `spine.list` | ✓ | In-memory state (resets on restart) |
| loamSpine | `spine.create` | ✓ | Used by native_braid.py |
| loamSpine | `session.commit` | ✓ | Used by native_braid.py |
| sweetGrass | `health.check` | ✓ | v0.8.0, **persistent store** |
| sweetGrass | `braid.list` | ✓ | **2,464 braids in store** |
| sweetGrass | `braid.batch_create` | ✓ | Requires riboCipher prefix |
| bearDog | `health.check` | ✓ | Ed25519 signing ready |
| bearDog | `identity.sign` | ✓ | No riboCipher required |

### riboCipher Transport Signal — G68 Enforcement

G68 sweetGrass and rhizoCrypt now **reject plain JSON-RPC connections**. Clients
must send a 2-byte prefix before the JSON payload:

```
[0xEC, 0x01] + JSON-RPC payload + \n
```

- `0xEC` = JSON-RPC protocol type
- `0x01` = protocol version
- Response also prefixed with `[0xEC, 0x01]`

**Impact**: Any tooling that uses raw `socat` or plain socket connections to
sweetGrass or rhizoCrypt will fail with:

```
REJECTED: unsignalled connection (no riboCipher prefix).
Clients MUST send [0xEC/0xED, protocol_type] prefix.
```

**native_braid.py already handles this** — it sends `RIBOCIPHER_PREFIX` for all
primals except bearDog (which still accepts plain JSON-RPC).

**For primalSpring**: This is correct behavior. The riboCipher signal is the
transport layer security handshake. But it means:
1. biomeOS `capability.call` dispatch needs to send the riboCipher prefix when
   routing to sweetGrass/rhizoCrypt
2. Any Neural API consumer that discovers sweetGrass via `capability.resolve`
   and then connects directly needs to know about the prefix
3. The capability registry should advertise the transport protocol requirement

### Persistence Model

| Primal | Persistence | Behavior on Restart |
|--------|-------------|---------------------|
| nestGate | Disk (ZFS CAS) | CAS objects survive |
| rhizoCrypt | Ephemeral | DAG sessions lost, 0 vertices after restart |
| loamSpine | Ephemeral | Spine state lost, 0 spines after restart |
| sweetGrass | **Persistent** | **2,464 braids survive restart** |
| bearDog | Persistent | Keys survive |

**For primalSpring**: rhizoCrypt and loamSpine ephemeral state is a known
architectural choice (DAG events and spine entries are rebuilt from CAS on
demand). But it means `spine.list` returns 0 after redeploy even though the
braid state files on disk record the spine ID. The spine is a logical construct
that lives in the `.native_braid_state` file, not in loamSpine's memory. This
could confuse consumers who expect `spine.list` to show active provenance chains.

---

## 4. Neural API — What Works, What Doesn't, What primalSpring Needs

### What Works

| Feature | Status | Evidence |
|---------|--------|----------|
| `health.check` | ✓ | Returns alive, 679 registered capabilities |
| songBird `ipc.register` | ✓ | 5 provenance primals registered with capabilities |
| songBird `capability.resolve` | ✓ | All 26 capabilities route correctly |
| songBird `ipc.list` | ✓ | 10 services visible |
| songBird `mesh.peers` | ✓ | ironGate visible at 192.168.4.213:7700 |
| nestGate TCP | ✓ | 0.0.0.0:8080, reachable from LAN |
| Direct primal RPC | ✓ | All methods work via UDS (with riboCipher where needed) |

### What Doesn't Work

| Feature | Issue | Root Cause |
|---------|-------|------------|
| `capability.call` | Times out (returns empty after 5s) | Tower Atomic relay consumes timeout budget for non-Tower capabilities. AAR: `NEURAL_API_ROUTING_INVESTIGATION_AAR_AUG08_2026.md` |
| Plain socket to sweetGrass | REJECTED | G68 riboCipher enforcement. biomeOS dispatch doesn't send riboCipher prefix |
| Plain socket to rhizoCrypt | BTSP handshake enforced | Same — biomeOS dispatch uses raw JSON-RPC |

### The capability.call Timeout — Full Diagnosis

When biomeOS receives `capability.call(capability="content", operation="get")`:
1. It formats `semantic_name = "content.get"`
2. It tries **Tower Atomic relay first** (songBird), even for non-Tower capabilities
3. SongBird doesn't handle `content.get`, so the request **times out after 15s**
4. Only THEN does it fall back to the translation registry
5. The total timeout budget is consumed by step 3

**Fix attempted and reverted**: Reordering dispatch to check translation registry
before Tower relay. Reverted because the capability registry itself is
architecturally problematic (monolithic, not primal-owned).

### What primalSpring Needs to Evolve

#### 1. Dispatch Order Fix
Check translation registry / songBird IPC resolution BEFORE Tower Atomic relay.
The relay should be a fallback for Tower-scoped methods, not the primary path.

#### 2. riboCipher-Aware Dispatch
When `capability.call` dispatches to sweetGrass or rhizoCrypt, it must send the
`[0xEC, 0x01]` riboCipher prefix. Currently it sends raw JSON-RPC, which G68
binaries reject. This is the single biggest gap — the Neural API can discover
and resolve capabilities but can't actually call them on riboCipher-enforcing
primals.

#### 3. Per-Primal Capability Ownership
The monolithic `capability_registry.toml` (1,326 lines) should be replaced by
per-primal capability advertisements. Each primal knows its own methods. The
registry should be populated by `ipc.register` (as we did manually with
songBird), not hand-maintained in a TOML file.

#### 4. Transport Protocol Advertisement
When a capability is resolved, the response should include the transport
protocol requirement:
```json
{
  "primal_id": "sweetgrass",
  "socket": "/run/user/1000/membrane/sweetgrass-westgate-tower-155f.sock",
  "transport_protocol": "ribocipher_jsonrpc",
  "signal_prefix": [236, 1]
}
```
This lets consumers know they need the riboCipher prefix before connecting.

#### 5. Primal Self-Registration
Primals should `ipc.register` with songBird on startup, advertising their
capabilities. Currently, auto-discovery finds primals but doesn't populate
capability lists. The `songbird-register.service` we created is a workaround —
the real fix is primals registering themselves.

#### 6. Spine Reconstruction After Restart
When loamSpine restarts, it should be able to reconstruct spine state from the
CAS objects and braid state files, or from sweetGrass's persistent braid store.
Currently, `spine.list` returns 0 after restart even though 990,500 files are
braided.

---

## 5. Storage Topology

| Tier | Path | Size | Role |
|------|------|------|------|
| T0 RAM (ZFS ARC) | — | ~32 GB | Auto-cached hot reads |
| T1 NVMe | /mnt/cas-hot | 1.3 TB / 1.8 TB (74%) | Hot ingest, braiding staging |
| T2 SSD | — | ZFS L2ARC | Warm read cache |
| T3 HDD (ZFS raidz1) | /mnt/nestgate/cold/zfs | 5.11 TB / 63.7 TB (10%) | Cold archive |
| CAS cold | nestgate/cas | 1.31 TB | Content-addressed objects |
| CAS warm | /mnt/cas-hot/datasets | 1.1 TB | Staged CAS data |

**Principle**: Cold storage is for durability, not for work. All braiding
happens on NVMe. Files are staged from HDD → NVMe before hashing, then
results written to CAS. The `native_braid.py` script enforces this via
explicit NVMe staging with batch staging for oversized chunks.

---

## 6. What the Ecosystem Can Learn

### Deploy from depot, don't build
Gates pull pre-built musl binaries from golgi. 15 seconds vs 20 minutes.
`depot.primals.eco` serves static files via Caddy.

### Inline braiding is atomic ingress
No data lands without provenance. The rsync → braid pattern ensures every byte
is hashed, CAS-indexed, DAG-tracked, spine-committed, and braid-created before
the next download phase begins.

### riboCipher is the new normal
G68 enforces transport signals. All tooling must adapt. Plain `socat`
JSON-RPC is dead for sweetGrass and rhizoCrypt. Python clients need the
2-byte prefix. biomeOS dispatch needs it too.

### songBird IPC is the capability layer
`ipc.register` + `capability.resolve` is the correct path for capability
discovery. The monolithic TOML registry is a maintenance burden. songBird
already has the runtime infrastructure — primals just need to self-register.

### sweetGrass is the provenance anchor
With 2,464 braids in persistent storage, sweetGrass is the most durable
proof that braiding happened. Even when loamSpine and rhizoCrypt lose
in-memory state on restart, sweetGrass retains every braid.

---

## 7. Files Changed This Session

| File | Change |
|------|--------|
| `~/.config/systemd/user/songbird-register.sh` | New — IPC registration script (riboCipher-aware) |
| `~/.config/systemd/user/songbird-register.service` | New — systemd oneshot, enabled at boot |
| `plasmidBin/primals/*` | 17 binaries replaced from golgi depot |

---

## 8. Numbers for primalSpring

```
Braided files:           990,500
Braided chunks:          240
Spine:                   019fd782-67d5-7903-8d2d-8ba369ca0490
sweetGrass braids:       2,464 (persistent)
CAS pool:                2.5 TB (1.1 warm + 1.4 cold)
ZFS pool:                5.11 TB used / 63.7 TB total (10%)
NVMe:                    1.3 TB / 1.8 TB (74%)
Services:                13/13 active (G68 depot)
songBird registrations:  10 services, 26 capabilities
biomeOS capabilities:    679 registered
Mesh peers:              ironGate (192.168.4.213:7700)
Download active:         sequences.fasta 5.1/118 GB
Dedup hits:              24,336 (2.5% of braided files)
```

---

*westGate is braiding inline at ingress, 990,500 files provenanced on a single
spine. sweetGrass holds 2,464 braids in persistent storage. songBird resolves
all 26 provenance capabilities correctly. The one gap: biomeOS capability.call
times out (Tower relay dispatch order) and doesn't speak riboCipher to G68
primals. primalSpring owns these evolution items: dispatch order, riboCipher-aware
dispatch, per-primal capability ownership, transport protocol advertisement,
primal self-registration, spine reconstruction. The architecture works — the
routing substrate needs to catch up to what the primals already enforce.*
