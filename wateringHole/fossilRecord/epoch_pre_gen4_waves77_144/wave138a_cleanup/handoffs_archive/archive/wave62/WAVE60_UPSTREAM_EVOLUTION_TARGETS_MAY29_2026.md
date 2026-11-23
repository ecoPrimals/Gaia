# Wave 60 — Upstream Primal Evolution Targets

**Date**: May 29, 2026
**Phase**: PostPrimordial → Glacial Shift
**Context**: Neural API Coordination Triad (quorumSignal/rootPulse/waterFall) formalized.
23 signal graphs spec'd. Cross-gate graph executor designed. Springs stabilizing.
Now primals need to evolve the capabilities that make the triad real.

**Model**: primalSpring has registered 14 new capability methods that don't exist
yet in the primals. These are the API contracts the signal graphs will call.
Each primal team should implement the methods in their domain, following
existing wire standard patterns. primalSpring validation will detect when
methods go live and promote them from structural to semantic testing.

---

## Per-Primal Upstream Targets

### rhizoCrypt — DAG Evolution (4 new methods)

| Method | Signal Graph | What It Does |
|--------|-------------|--------------|
| `dag.branch` | rootpulse.branch | Create a named branch point in the DAG |
| `dag.diff` | rootpulse.diff, rootpulse.federate | Compute diff between two DAG frontiers |
| `dag.merge` | rootpulse.merge | Merge two DAG branches (3-way merge semantics) |
| `dag.federate` | rootpulse.federate | Replicate DAG state to/from a remote peer |

**Priority**: HIGH — rootPulse depends on these. Without them, version control
remains bash + git. With them, version control emerges from graph composition.

**Pattern**: Follow `dag.event.append` / `dag.session.create` wire patterns.
All methods should work over UDS (existing) and be discoverable via
`capability.call("dag", "dag.branch", params)`.

**Cross-gate note**: `dag.federate` is the first method that will be called
across gates via the cross-gate graph executor. It needs to handle partial
state transfer (not full DAG replication — diff-based federation).

---

### loamSpine — Session Dehydration (1 new method)

| Method | Signal Graph | What It Does |
|--------|-------------|--------------|
| `session.dehydrate` | rootpulse.commit | Serialize session state for content-addressed storage |

**Priority**: MEDIUM — rootpulse.commit needs this to dehydrate before signing.
Currently `dag.partial_dehydrate` exists in rhizoCrypt but the session-level
dehydration (loamSpine's responsibility) is missing.

**Pattern**: Follow `session.commit` / `session.create` existing patterns.

---

### sweetGrass — Braid Anchoring (1 new method)

| Method | Signal Graph | What It Does |
|--------|-------------|--------------|
| `braid.anchor` | rootpulse.branch | Anchor a braid to a branch point (attribution at branch time) |

**Priority**: MEDIUM — ensures provenance is established when branches are created,
not just at commit time.

**Pattern**: Follow `braid.commit` / `braid.create` existing patterns.

---

### nestGate — Content Federation (4 new methods)

| Method | Signal Graph | What It Does |
|--------|-------------|--------------|
| `content.fetch_heads` | ecosystem.check | Fetch HEAD refs from remote repos (freshness check) |
| `content.push` | ecosystem.push | Push content to Forgejo remote |
| `content.replicate` | rootpulse.federate | Replicate content blobs to a remote gate |
| `content.sync` | ecosystem.pull | Cascade-pull content from remote sources |

**Priority**: HIGH — waterFall depends on these to graduate from bash to Neural API.
`content.sync` is the Neural API equivalent of `cascade-pull.sh`.

**Cross-gate note**: `content.replicate` will be called cross-gate. It should
accept a list of content CIDs and transfer them to the remote nestGate.

---

### songbird — Mesh Federation (3 new methods)

| Method | Signal Graph | What It Does |
|--------|-------------|--------------|
| `mesh.discover_remotes` | ecosystem.pull | Discover remote gates and their content sources |
| `mesh.mirror` | ecosystem.push | Mirror content/repos to a GitHub remote |
| `mesh.publish` | ecosystem.pull/push/check | Publish freshness/drift status to the mesh |

**Priority**: MEDIUM — ecosystem signals use songbird as the mesh transport.
`mesh.publish` is how gates advertise their sync state to the Plasmodium.

**Pattern**: Follow `mesh.connect` / `mesh.peers` existing patterns.
`mesh.publish` is fire-and-forget broadcast to connected peers.

---

### biomeOS — Manifest + Cross-Gate Executor (2 targets)

| Target | What It Does |
|--------|--------------|
| `manifest.gate_profile` | Resolve gate profile from `ecosystem_manifest.toml` at runtime |
| Cross-gate `graph.execute` | Support `gate` and `relay` hints on graph nodes (Phase B of spec) |

**Priority**: HIGH — `manifest.gate_profile` is needed by all 3 ecosystem signals.
Cross-gate `graph.execute` is the glacial gate's key deliverable — it's what makes
the Plasmodium possible.

**Spec**: `specs/CROSS_GATE_GRAPH_EXECUTOR.md` in primalSpring defines the full
design. Phase B targets Wave 65.

---

## DH-1: /tmp Hardcoding (All Primals)

**8 of 13 primals** write to hardcoded `/tmp` paths, blocking `ProtectSystem=strict`
on the VPS membrane. Full audit in `docs/PRIMAL_GAPS.md` (DH-1 section).

| Primal | Offending Pattern |
|--------|------------------|
| songbird | `/tmp/songbird-data/`, `/tmp/songbird.sock` |
| toadStool | `/tmp/biomeos/compute-tarpc.sock` |
| coralReef | `/tmp/biomeos/coralreef-core-default-tarpc.sock`, `.json`, `.pid` |
| barraCuda | `/tmp/biomeos/barracuda-core.json`, `/tmp/biomeos/barracuda.sock` |
| sweetGrass | `/tmp/sweetgrass.sock`, `/tmp/provenance.sock` |
| squirrel | `/tmp/ecoPrimals-manifests/squirrel.json` |

**Fix**: All sockets to `$SOCKET_DIR` (env-first). All data/state to
`$XDG_DATA_HOME` (desktop) or `/var/lib/<primal>/` (VPS). Zero `/tmp` writes.

**Priority**: P2 — doesn't block eukaryotic, but blocks hardened VPS deployment.

---

## Glacial Gate Summary

The glacial gate requires:

1. **rootPulse real** — rhizoCrypt implements `dag.branch/diff/merge/federate`,
   enabling `rootpulse.*` signal graphs to execute against live primals
2. **waterFall real** — nestGate implements `content.sync/push/replicate/fetch_heads`,
   enabling `ecosystem.*` signal graphs to replace `cascade-pull.sh`
3. **Cross-gate executor** — biomeOS supports `gate`/`relay` hints in `graph.execute`,
   enabling `rootpulse.federate` and `ecosystem.check` to work across gates
4. **DH-1 clean** — all primals run under `ProtectSystem=strict` on VPS
5. **3+ gates meshed** — at least 3 gates with live Songbird mesh and MitoBeacon trust

Items 1-3 are the Neural API evolution. Item 4 is deployment hygiene.
Item 5 is topology — already close (eastGate + ironGate + VPS operational).

---

## Timeline

| Wave | Target |
|------|--------|
| 60 (current) | Spec complete. Springs stabilizing. Upstream begins. |
| 61-63 | rhizoCrypt dag.branch/diff/merge, nestGate content.sync/push |
| 64 | songbird mesh.publish/discover_remotes, sweetGrass braid.anchor |
| 65 | biomeOS cross-gate graph.execute Phase B |
| 66 | DH-1 /tmp cleanup sweep, routing integration |
| 67+ | Fleet orchestration, Plasmodium-level graphs |
