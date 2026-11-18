# Spore Ownership Matrix

**Authority**: eastGate overwatch | **Wave**: 137b (reviewed 155h) | **Last updated**: Jul 13, 2026

---

## Provenance Trio — Role Definitions

The provenance trio provides the content-addressed, immutable, attributed persistence
layer for the ecosystem. Together with nestGate, they form the **Nest Atomic** composition.

| Primal | Role | Metaphor | Socket | Capabilities |
|--------|------|----------|--------|-------------|
| **rhizoCrypt** | Ephemeral DAG | Root network — branching, checkout, slicing | `rhizocrypt.sock` | `dag.slice.checkout` |
| **loamSpine** | Immutable ledger | Soil backbone — permanent, append-only | `loamspine.sock` | `braid.commit` |
| **sweetGrass** | Attribution braid | Prairie grass — woven provenance, SNARE targeting | `sweetgrass.sock` | `braid.commit` |
| **nestGate** | Persistent storage | Nest — content-addressed store, RPC gateway | `nestgate.sock` | `footprint.*`, `content.*`, `coord.*` |

## Ownership Boundaries

### rhizoCrypt — Ephemeral DAG

**Owns**: DAG sessions, branching, checkout, merge, diff operations.
**Does not own**: Permanent storage (that's loamSpine), attribution (that's sweetGrass).

| Capability | Description |
|-----------|-------------|
| `dag.slice.checkout` | Checkout a DAG slice at a specific commit/ref |
| `dag.branch` | Create/list/delete branches in the ephemeral DAG |
| `dag.merge` | Merge DAG branches |
| `dag.diff` | Diff between DAG states |

**Data lifecycle**: Ephemeral. DAG sessions are pruned after finalization. Permanent
records are committed to loamSpine. rhizoCrypt is the "working directory" — loamSpine
is the "committed history."

### loamSpine — Immutable Ledger

**Owns**: Append-only commit log, permanent record, Merkle spine.
**Does not own**: Working state (that's rhizoCrypt), who-did-what (that's sweetGrass).

| Capability | Description |
|-----------|-------------|
| `braid.commit` | Commit a finalized DAG session to the immutable spine |
| `spine.query` | Query the commit log by hash, range, or filter |
| `spine.verify` | Verify Merkle chain integrity |

**Data lifecycle**: Permanent. Once committed, records are immutable. loamSpine is the
ecosystem's "git log" — content-addressed, hash-chained, never rewritten.

### sweetGrass — Attribution Braid

**Owns**: Who did what, when, why. Provenance attribution. SNARE-protein targeting for
cross-membrane workload routing.
**Does not own**: The data itself (that's nestGate/rhizoCrypt), the commit history (that's loamSpine).

| Capability | Description |
|-----------|-------------|
| `braid.commit` | Attach attribution metadata to a spine commit |
| `braid.verify` | Verify attribution chain integrity |
| `braid.wrap` | Wrap a workload in provenance braid for cross-membrane transport |

**Data lifecycle**: Permanent (co-located with loamSpine entries). sweetGrass braids are
the "git blame" + "signed commits" — they prove who produced what and authorize
cross-membrane routing via SNARE targeting (K-Derm vesicle transport).

### nestGate — Content-Addressed Store

**Owns**: Blob storage, CAS deduplication, RPC gateway, HTTP content serving,
coordination data (blurbs, AARs, wave state), footPrint project persistence.
**Does not own**: Provenance (that's the trio), routing (that's songBird), crypto (that's bearDog).

| Capability | Description |
|-----------|-------------|
| `content.store` | Store content-addressed blob |
| `content.get` | Retrieve blob by hash |
| `content.replicate` | Federate content to another gate |
| `footprint.*` | Project CRUD (CAS-backed, Wave 137b) |
| `coord.*` | Coordination data ingest/query |

## Composition: rootPulse

rootPulse is not a primal — it's the **composition** of the provenance trio operating
together as a distributed version control system:

```
rootPulse = rhizoCrypt (working tree) + loamSpine (commit log) + sweetGrass (attribution)
```

| rootPulse Operation | rhizoCrypt | loamSpine | sweetGrass |
|--------------------|-----------|-----------|------------|
| `commit` | Finalize DAG session | Append to spine | Attach attribution |
| `branch` | Create DAG branch | — | — |
| `merge` | Merge DAG branches | Record merge commit | Record merge author |
| `diff` | Compute DAG diff | — | — |
| `federate` | — | Replicate spine segment | Replicate braid segment |
| `verify` | — | Verify Merkle chain | Verify attribution chain |

## Composition: Nest Atomic

The Nest composition (defined in `ecosystem_manifest.toml`) combines all four:

```
Nest = nestGate + rhizoCrypt + loamSpine + sweetGrass
```

- **nestGate** provides the CAS blob store and RPC gateway
- **rhizoCrypt** provides the ephemeral working DAG
- **loamSpine** provides the immutable commit spine
- **sweetGrass** provides attribution braids

Target deployment: westGate (76TB ZFS cold storage).

## Cross-Membrane Interaction (K-Derm)

Per the K-Derm topology standard, sweetGrass braids act as SNARE-protein targeting
signals for vesicle transport:

1. **Budding**: Workload originates. sweetGrass creates braid (DAG session + data refs + attribution)
2. **Transport**: Braid-wrapped workload crosses membrane boundaries
3. **Fusion**: Target membrane verifies braid — DAG refs via rhizoCrypt, attribution chain intact
4. **Facilitated diffusion**: Pre-braided workloads cross faster (no re-verification needed)

Braids are stripped at the outer membrane (only results cross, not provenance) —
this is the ionic/covalent bond boundary.

---

*Spore Ownership Matrix — Wave 137b. Defines the three-way provenance split
(rhizoCrypt/loamSpine/sweetGrass) and their relationship to nestGate and rootPulse.*
