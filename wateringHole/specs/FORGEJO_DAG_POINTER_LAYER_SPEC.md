# Forgejo DAG Pointer Layer Spec

**Date**: Oct 5, 2026 | **Wave**: 161+ | **From**: sporeGate (golgiBody inner membrane)
**Owner**: sporeGate topology team
**Status**: PHASE 1 COMPLETE — PHASE 2 SPECCED

---

## Abstract

golgiBody's Forgejo instance (`git.primals.eco`) evolves from a full git
forge (storing 1.8GB of repository blobs) into a **DAG pointer layer** that
tracks references to where data lives in the mesh. Golgi's role is a Golgi
apparatus — it processes and routes, it doesn't store.

This spec defines the **git reverse-proxy pattern**: how golgi routes git
operations to LAN gates via songBird drawbridge, using Forgejo as a
reference-tracking surface rather than a blob-storage backend.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      PUBLIC INTERNET                                     │
│                                                                          │
│  git clone https://git.primals.eco/ecoPrimals/bearDog.git               │
│        │                                                                 │
│        ▼                                                                 │
│  ┌──────────────────────────────────────────────────┐                    │
│  │  golgiBody ([RELAY_PUBLIC]) — POINTER LAYER       │                    │
│  │                                                   │                    │
│  │  Caddy (TLS termination)                          │                    │
│  │    ├── git.primals.eco → Forgejo (:3000)          │                    │
│  │    │     ├── Web UI: shallow refs (depth=1)       │                    │
│  │    │     ├── Smart HTTP: /info/refs (from local)  │                    │
│  │    │     └── git-upload-pack: redirect to gate    │                    │
│  │    └── /api/v1/repos/* (metadata, refs, DAG)      │                    │
│  │                                                   │                    │
│  │  Pointer State:                                   │                    │
│  │    refs/heads/main → {commit_hash}                │                    │
│  │    canonical_gate  → eastGate (10.13.37.5)        │                    │
│  │    mirror_gates    → [sporeGate, GitHub]           │                    │
│  └──────────────────────────────────────────────────┘                    │
│        │ songBird drawbridge (WireGuard mesh)                            │
│        ▼                                                                 │
│  ┌──────────────────────────────────────────────────┐                    │
│  │  LAN MESH — DATA LAYER                           │                    │
│  │                                                   │                    │
│  │  eastGate (10.13.37.5) — overwatch/dev            │                    │
│  │    └── ~/Development/ecoPrimals/* (full repos)    │                    │
│  │                                                   │                    │
│  │  sporeGate (10.13.37.2) — inner membrane          │                    │
│  │    └── ~/Development/ecoPrimals/* (full repos)    │                    │
│  │                                                   │                    │
│  │  westGate (10.13.37.11) — data NAS (50.7TB ZFS)  │                    │
│  │    └── CAS root + archival copies                 │                    │
│  └──────────────────────────────────────────────────┘                    │
│        │ push mirror                                                     │
│        ▼                                                                 │
│  ┌──────────────────────────────────────────────────┐                    │
│  │  GitHub (outer mirror) — public redundancy        │                    │
│  └──────────────────────────────────────────────────┘                    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1 Results (COMPLETE — Oct 5, 2026)

### Shallow Conversion

All 47 Forgejo repositories converted to depth-1 shallow clones:

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Total repo storage | 1.8 GB | 562 MB | −69% |
| Disk usage (golgi) | 50% (4.7 GB) | 38% (3.6 GB) | −1.1 GB freed |
| bearDog | 647 MB | 152 MB | −77% |
| songBird | 372 MB | 5 MB | −99% |
| hotSpring | 116 MB | 115 MB | −1% (large current-tree blobs) |
| biomeOS | 43 MB | 4 MB | −91% |
| sporePrint | 62 MB | 3 MB | −95% |
| toadStool | 60 MB | 7 MB | −88% |

### Backup Verification

Before shallowing, verified full copies exist on LAN:

| Repository | sporeGate | eastGate | GitHub | Commits Match |
|-----------|-----------|----------|--------|---------------|
| bearDog | ✓ (1387) | ✓ (1387) | ✓ | ✓ |
| songBird | ✓ (1873) | ✓ (1873) | ✓ | ✓ |
| hotSpring | — | ✓ (70) | — | ✓ |
| All others | 26 repos | 45 repos | varies | ✓ |

### Configuration Changes

Forgejo `app.ini` additions:
- `[repository.upload] MAX_FILE_SIZE = 10` — prevent blob accumulation
- `[repository.upload] MAX_FILES = 5` — limit upload count
- `[git] MAX_GIT_DIFF_LINES = 200` — reduce memory for diff rendering
- `[mirror] DEFAULT_INTERVAL = 8h` — reduce sync frequency
- `MemoryMax=400M` / `MemoryHigh=300M` — systemd memory bounds

---

## Phase 2: Git Reverse-Proxy Pattern

### Design Principle

Forgejo on golgi serves two distinct roles:

1. **Web UI Surface** — Browse repos, view recent files, read READMEs.
   Served from local shallow clones. No change needed.

2. **Git Smart HTTP** — `git clone`, `git fetch`, `git push`.
   Currently served from local shallow clones (broken for full history).
   **Evolve to**: route to LAN gate holding the canonical full repo.

### Git Smart HTTP Protocol Flow

Standard git smart HTTP has two phases:

```
Phase 1: Reference Discovery
  GET /repo.git/info/refs?service=git-upload-pack
  → Returns: list of refs (branch names + commit hashes)
  → golgi CAN serve this from shallow clone (refs are complete)

Phase 2: Pack Negotiation + Transfer  
  POST /repo.git/git-upload-pack
  → Client sends: "I want commits X,Y,Z; I have commits A,B,C"
  → Server sends: packfile with requested objects
  → golgi CANNOT serve this fully (shallow clone lacks history objects)
```

### Reverse-Proxy Strategy

golgi handles Phase 1 locally (fast, small) and proxies Phase 2 to a
LAN gate via songBird drawbridge:

```
git clone https://git.primals.eco/ecoPrimals/bearDog.git

1. Client → golgi Caddy → Forgejo
   GET /ecoPrimals/bearDog.git/info/refs?service=git-upload-pack
   ← Forgejo serves from local shallow refs (fast, <1KB response)

2. Client → golgi Caddy → git-proxy-shim → songBird → eastGate
   POST /ecoPrimals/bearDog.git/git-upload-pack
   → git-proxy-shim intercepts upload-pack requests
   → Queries canonical_gate map: bearDog → eastGate (10.13.37.5)
   → Forwards request via songBird drawbridge to eastGate
   → eastGate's git-http-backend serves full packfile
   ← Response streams back through the chain
```

### Canonical Gate Map

A TOML file on golgi tracks which gate holds the canonical (full) copy
of each repository:

```toml
# /opt/forgejo/canonical_gates.toml
# Maps repo → canonical gate for git reverse-proxy routing
# Updated by songBird mesh discovery or manual config

[repos]

[repos.bearDog]
canonical = "eastGate"
wg_ip = "10.13.37.5"
mirrors = ["sporeGate", "github"]
path = "/home/eastgate/Development/ecoPrimals/primals/bearDog"

[repos.songBird]
canonical = "sporeGate"
wg_ip = "10.13.37.2"
mirrors = ["eastGate", "github"]
path = "/home/sporegate/Development/ecoPrimals/primals/songBird"

[repos.hotSpring]
canonical = "eastGate"
wg_ip = "10.13.37.5"
mirrors = []
path = "/home/eastgate/Development/ecoPrimals/springs/hotSpring"

[repos.wateringHole]
canonical = "sporeGate"
wg_ip = "10.13.37.2"
mirrors = ["eastGate", "github"]
path = "/home/sporegate/Development/ecoPrimals/infra/wateringHole"

[repos.detroit]
canonical = "sporeGate"
wg_ip = "10.13.37.2"
mirrors = ["github"]
path = "/home/sporegate/Development/ecoPrimals/infra/detroit"

# ... (all 47 repos)
```

### git-proxy-shim

A lightweight HTTP handler on golgi that intercepts git smart HTTP
upload-pack requests and proxies them to the canonical gate:

```
┌─────────────────────────────────────────────┐
│  git-proxy-shim (golgi, :3001)              │
│                                              │
│  Routes:                                     │
│    POST /:org/:repo.git/git-upload-pack      │
│    POST /:org/:repo.git/git-receive-pack     │
│                                              │
│  Logic:                                      │
│    1. Parse org/repo from URL                │
│    2. Lookup canonical gate in TOML          │
│    3. Open TCP to gate_wg_ip:9418 (git://)  │
│       OR HTTP to gate_wg_ip:8080/git/...    │
│    4. Forward request body, stream response  │
│                                              │
│  Fallback:                                   │
│    If canonical gate unreachable:            │
│    → Try mirror gates in order               │
│    → If all fail: serve from local shallow   │
│      (partial data is better than error)     │
└─────────────────────────────────────────────┘
```

### Caddy Configuration

```caddyfile
# git.primals.eco — DAG pointer layer
git.primals.eco {
    # Web UI — Forgejo serves from shallow clones
    @web_ui {
        not path *.git/git-upload-pack
        not path *.git/git-receive-pack
    }
    handle @web_ui {
        reverse_proxy localhost:3000
    }

    # Git smart HTTP — proxy to canonical LAN gate
    @git_pack {
        path *.git/git-upload-pack
        path *.git/git-receive-pack
    }
    handle @git_pack {
        reverse_proxy localhost:3001  # git-proxy-shim
    }
}
```

### Gate-Side git HTTP Backend

Each LAN gate that holds canonical repos runs a minimal git HTTP server:

```bash
# On eastGate: systemd service
# git-http-backend via nginx/caddy or direct fcgi
# Listens on :8080, serves repos from ~/Development/ecoPrimals/

[Unit]
Description=Git HTTP Backend for DAG Pointer Proxy
After=network.target

[Service]
User=eastgate
ExecStart=/usr/bin/git daemon \
    --reuseaddr \
    --base-path=/home/eastgate/Development/ecoPrimals \
    --export-all \
    --enable=upload-pack \
    --enable=receive-pack \
    --port=9418 \
    --listen=10.13.37.5
Restart=always

[Install]
WantedBy=multi-user.target
```

### Push Path (Receive-Pack)

Pushes are more complex because golgi needs to:
1. Accept the push (update its shallow ref)
2. Forward the objects to the canonical gate
3. Trigger any post-receive hooks (CI, mirror sync)

```
git push https://git.primals.eco/ecoPrimals/bearDog.git

1. Client → golgi Caddy → git-proxy-shim
   POST /ecoPrimals/bearDog.git/git-receive-pack
   → Forward to eastGate (canonical) via WG mesh
   → eastGate accepts push, updates full repo
   ← Success

2. golgi post-push hook:
   → Update local shallow ref (git fetch --depth=1 from eastGate)
   → Trigger GitHub mirror push (existing Forgejo mirror config)
   → Emit songBird event: "repo.push" with commit hash + gate
```

### songBird Integration

songBird provides the mesh routing layer:

```
capability: "git.locate"
  → Query: which gate has repo X?
  → Response: {gate: "eastGate", wg_ip: "10.13.37.5", path: "..."}

capability: "git.push_event"  
  → Emitted after each push
  → Payload: {repo, commit, branch, gate, timestamp}
  → Consumed by: rhizoCrypt (DAG anchor), loamSpine (ledger)

capability: "git.replicate"
  → Request: replicate repo X from gate A to gate B
  → Used for: mesh redundancy, new gate bootstrap
```

### Failure Modes

| Scenario | Behavior |
|----------|----------|
| Canonical gate offline | Try mirror gates in order, serve partial from shallow |
| All gates offline | Serve info/refs from local (browse-only), error on clone |
| songBird down | Use static canonical_gates.toml (no dynamic discovery) |
| Push to offline gate | Queue push, retry when gate comes online |
| Shallow ref diverged | Force-update shallow from canonical gate on next sync |

### Migration Path

Phase 2 is implemented incrementally:

1. **Deploy git-proxy-shim** on golgi (:3001)
2. **Create canonical_gates.toml** from ecosystem manifest
3. **Deploy git daemon** on eastGate + sporeGate (WG-only bind)
4. **Update Caddy** to split web UI vs git pack routes
5. **Test**: `git clone` from external → verify objects come from LAN gate
6. **Monitor**: Log proxy decisions for 1 week before removing Forgejo fallback

---

## Phase 3: Provenance Trio Integration (DESIGN)

### Git Events → Provenance Pipeline

Every git push generates three provenance records:

```
git push → golgi receives push event
  │
  ├── 1. rhizoCrypt: dag.anchor
  │     hash: commit SHA (already a Merkle DAG node)
  │     metadata: {repo, branch, author, timestamp, parent_commits}
  │     → Creates DAG anchor linking git commit to provenance graph
  │
  ├── 2. loamSpine: ledger.append
  │     entry: {repo, canonical_gate, commit, ref, timestamp}
  │     → Records WHERE the authoritative copy lives NOW
  │     → This IS the "pointer" — the ledger tracks data location
  │
  └── 3. sweetGrass: braid.weave
        entries: [dag_anchor_id, ledger_entry_id]
        → Braids the push event into the Merkle chain
        → Proves: this push happened, at this time, with this data
```

### Mapping Git Concepts to Provenance Trio

| Git Concept | Provenance Trio | Role |
|-------------|----------------|------|
| Commit hash | rhizoCrypt DAG node | Content address (what happened) |
| Branch ref | loamSpine ledger entry | Location pointer (where is latest) |
| Push event | sweetGrass braid | Integrity proof (chain is unbroken) |
| Merge commit | rhizoCrypt DAG merge | DAG convergence (two histories join) |
| Tag | loamSpine + rhizoCrypt | Named anchor (release point) |
| Fork/clone | loamSpine replication entry | Data movement record |

### Post-Receive Hook

```bash
#!/bin/bash
# /opt/forgejo/data/repositories/*/hooks/post-receive.d/provenance
# Triggered after every push to any Forgejo repo

while read oldrev newrev refname; do
    REPO=$(basename $(git rev-parse --git-dir) .git)
    ORG=$(basename $(dirname $(git rev-parse --git-dir)))
    BRANCH=$(echo "$refname" | sed 's|refs/heads/||')
    AUTHOR=$(git log -1 --format='%an' "$newrev")
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # 1. rhizoCrypt DAG anchor
    echo "{\"jsonrpc\":\"2.0\",\"method\":\"dag.anchor\",\"params\":{\"hash\":\"$newrev\",\"metadata\":{\"repo\":\"$ORG/$REPO\",\"branch\":\"$BRANCH\",\"author\":\"$AUTHOR\",\"timestamp\":\"$TIMESTAMP\",\"parent\":\"$oldrev\"}},\"id\":1}" | \
        nc -w 2 10.13.37.2 9601 || true
    
    # 2. loamSpine ledger append  
    CANONICAL_GATE=$(grep -A2 "\\[$REPO\\]" /opt/forgejo/canonical_gates.toml | grep canonical | cut -d'"' -f2)
    curl -s --max-time 2 -X POST http://10.13.37.2:9700 \
        -d "{\"jsonrpc\":\"2.0\",\"method\":\"ledger.append\",\"params\":{\"entry\":{\"repo\":\"$ORG/$REPO\",\"canonical_gate\":\"$CANONICAL_GATE\",\"commit\":\"$newrev\",\"ref\":\"$BRANCH\",\"timestamp\":\"$TIMESTAMP\"}},\"id\":2}" || true
    
    # 3. sweetGrass braid (deferred — requires BTSP)
    # sweetGrass weaving is triggered by loamSpine's append event
    # via the standard provenance pipeline, not directly from this hook
done
```

### nestgate.io Integration

Phase 3 connects git provenance to the federated CAS browser:

```
nestgate.io/git/{org}/{repo}/commits     → provenance-aware commit log
nestgate.io/git/{org}/{repo}/refs        → loamSpine ledger entries
nestgate.io/cas/{commit_hash}            → git commit as CAS object
nestgate.io/cas/{commit_hash}/provenance → full DAG → ledger → braid chain
```

---

## Pointer-Layer Pattern (Generalized)

### The Pattern

A **pointer layer** is a thin relay that tracks references to data
without storing the data itself. It answers two questions:

1. **What exists?** — The DAG of all known data identifiers
2. **Where does it live?** — The ledger of which node holds each datum

### Instances of This Pattern

| System | Pointer Layer | Data Layer | DAG | Ledger | Proof |
|--------|--------------|------------|-----|--------|-------|
| **Forgejo (git)** | golgi refs | LAN gate repos | git commit graph | canonical_gates.toml | sweetGrass braid |
| **nestgate.io CAS** | golgi CAS index | LAN gate CAS stores | rhizoCrypt DAG | content.locate results | sweetGrass braid |
| **Binary depot** | depot.primals.eco | LAN plasmidBin dirs | BLAKE3 hashes | depot manifest | checksums.toml |
| **P2P crypto data** | golgi DAG index | Mesh peers | transaction DAG | peer location map | chain proof |
| **DNS (analogy)** | Root/TLD servers | Authoritative NS | Domain hierarchy | NS records | DNSSEC chain |

### Why This Works

1. **Separation of concerns** — The pointer layer is tiny and fast (golgi's
   10GB VPS can hold millions of refs). The data layer is large and slow
   (LAN gates have terabytes).

2. **Failure isolation** — If a data node goes offline, the pointer layer
   still knows what exists and where else to find it (mirrors). The mesh
   degrades gracefully.

3. **Verification** — The pointer layer includes proof of integrity (braid,
   DNSSEC, chain proof). Anyone can verify the data they received matches
   the pointer without trusting the data node.

4. **Content addressing** — Data is identified by hash, not location.
   The pointer layer maps hash → location. If data moves, only the
   pointer updates — the hash stays the same.

### Anti-Patterns

- **Pointer layer stores data** — violates thin relay principle. golgi had
  this problem (1.8GB of git blobs on a 10GB VPS).
- **Data layer stores pointers** — creates circular dependency. Each gate
  should serve data, not maintain the global index.
- **No pointer layer** — each consumer must know all data node locations.
  Breaks when nodes join/leave mesh.

---

## Implementation Status

| Phase | Status | Key Result |
|-------|--------|------------|
| Phase 1: Thin Forgejo | ✅ COMPLETE | 1.8GB → 562MB, all repos depth-1 |
| Phase 2: Reverse Proxy | 📋 SPECCED | git-proxy-shim design, canonical gate map |
| Phase 3: Provenance | 📋 DESIGNED | post-receive → trio pipeline, nestgate.io CAS |

### Phase 2 Implementation Prerequisites

- [ ] eastGate git daemon deployed (WG-only, :9418)
- [ ] sporeGate git daemon deployed (WG-only, :9418)
- [ ] git-proxy-shim written (Go or Rust, ~200 LOC)
- [ ] canonical_gates.toml populated from ecosystem manifest
- [ ] Caddy route split (web UI vs git pack)
- [ ] Integration test: external clone → verify data from LAN gate

### Phase 3 Implementation Prerequisites

- [ ] rhizoCrypt operational on sporeGate (port 9601)
- [ ] loamSpine operational on sporeGate (port 9700)
- [ ] sweetGrass operational on sporeGate (port 9850)
- [ ] post-receive hook deployed to all Forgejo repos
- [ ] nestgate.io /git/ routes added to petalTongue

---

## References

- [THREE_DOMAIN_TOPOLOGY_SPEC.md](THREE_DOMAIN_TOPOLOGY_SPEC.md) — Domain architecture, nestgate.io evolution
- [PROVENANCE_CONTRACT.md](PROVENANCE_CONTRACT.md) — Trio roles, pipeline, transport
- [OUTER_MEMBRANE_TOPOLOGY.md](OUTER_MEMBRANE_TOPOLOGY.md) — golgi routing table
- ecosystem_manifest.toml — Repo catalog, gate profiles, compositions
- K_DERM_TOPOLOGY_STANDARD.md — Three-layer cell envelope model
