<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# lithoSpore USB Deployment — Hypogeal Cotyledon

**Date**: May 14, 2026
**Status**: Active
**Authority**: WateringHole Consensus
**Deployment Class**: LiveSpore (hypogeal cotyledon subclass)
**Hardware**: ~16GB USB on ironGate (scalable)

---

## Spore Taxonomy

The ecoPrimals ecosystem defines three spore deployment classes for
portable media. Each builds on the previous:

### ColdSpore

A static, read-mostly artifact on USB. biomeOS detects the
`.biomeos-spore` marker and can orchestrate the contents, but the
spore itself does not self-update. Like a seed in cold storage.

| Property | Value |
|----------|-------|
| Marker | `.biomeos-spore` |
| Entry point | `spore` (symlink → `bin/litho`) |
| Data | Frozen (BLAKE3-anchored at build time) |
| Self-update | No |
| Provenance | None (no validation trail) |
| Example | guideStone USB without runtime |

### LiveSpore

ColdSpore plus provenance tracking and data refresh capability. The
artifact accumulates an append-only trail of where it has been
validated. Like a seed that has germinated.

| Property | Value |
|----------|-------|
| Marker | `.biomeos-spore` |
| Entry point | `spore` (symlink → `bin/litho`) |
| Data | Refreshable via `./refresh` (re-fetches sources, re-computes BLAKE3) |
| Self-update | Data only (binaries frozen) |
| Provenance | `liveSpore.json` — append-only validation journal |
| Example | guideStone USB with `liveSpore.json` tracking |

### lithoSpore (Hypogeal Cotyledon)

A LiveSpore that carries its own **food supply** — embedded Python
runtime, all LTEE module data bundles, litho-core Rust ecoBins, and
Foundation targets. The spore can validate independently of any
network or host system beyond a Linux kernel.

The botanical metaphor: a **hypogeal cotyledon** is a seed leaf that
stays underground, nourishing the seedling until it can
photosynthesize. The USB's bundled data and runtime are the cotyledon
— persistent, not consumed, providing sustenance until the spore
connects to NUCLEUS for full compute capability.

| Property | Value |
|----------|-------|
| Marker | `.biomeos-spore` |
| Entry point | `spore` → `validate` (all symlinks to `bin/litho`, argv[0] dispatch) |
| Data | Refreshable + bundled (7 LTEE data bundles, Foundation targets) |
| Runtime | Embedded Python (`python-build-standalone` or equivalent) |
| Binaries | Single `litho` binary (musl-static, 5.1 MB) — unified CLI, in-process module execution |
| Self-update | Data (`./refresh`) + binaries via `litho fetch` |
| Provenance | `liveSpore.json` — append-only, BLAKE3-hashed hostnames |
| Example | Full CATHEDRAL USB on ironGate |

---

## USB Layout (~16GB)

```
/media/lithoSpore/
├── .biomeos-spore                    # biomeOS detection marker
├── .family.seed                      # Genetics lineage for this spore
├── validate                          # symlink → bin/litho (argv[0] dispatch)
├── verify                            # symlink → bin/litho
├── refresh                           # symlink → bin/litho
├── spore                             # symlink → bin/litho (biomeOS entry)
├── liveSpore.json                    # Append-only provenance journal
├── data_manifest.toml                # BLAKE3 hashes for all bundled data
│
├── biomeOS/
│   ├── tower.toml                    # Tower config for spore composition
│   └── graphs/
│       └── lithoSpore_validation.toml  # Validation flow graph
│
├── bin/
│   └── litho                         # Unified musl-static binary (all 7 modules + CLI)
│
├── python/                           # Embedded Python runtime
│   ├── bin/python3                   # python-build-standalone or similar
│   └── lib/                          # Standard library + numpy, scipy, etc.
│
├── artifact/
│   └── data/                         # LTEE data bundles (BLAKE3-anchored)
│       ├── barrick_2009/             # Module 1 source data
│       ├── wiser_2013/               # Module 2 source data
│       ├── good_2017/                # Module 3 source data
│       ├── blount_2012/              # Module 4 source data
│       ├── tenaillon_2016/           # Module 6 source data
│       ├── anderson_wiser/           # Module 7 source data
│       └── neuralspring_ml/          # ML surrogate data
│
├── projectFOUNDATION/
│   └── targets/                      # projectFOUNDATION validation targets
│       ├── thread05_ltee_targets.toml
│       └── ...
│
└── notebooks/                        # Pre-rendered HTML (Tier 1 fallback)
    ├── ltee_mutations.html
    ├── ltee_fitness.html
    └── ...
```

---

## Operating Modes

### Mode 1: Standalone (no network)

The USB is plugged into any Linux machine with no network. The
`validate` entry point detects the absence of primal IPC and falls
back to Tier 1: Python-only validation using the embedded runtime
and bundled data.

```bash
./validate                  # Tier 1: Python, bundled data
./validate --tier 1         # Force Tier 1 even if primals available
```

Results append to `liveSpore.json`. Pre-rendered notebooks in
`notebooks/` provide visual results without Jupyter.

### Mode 2: LAN-connected (ironGate)

The USB is plugged into a gate on the NUCLEUS LAN. litho-core's
`discovery.rs` finds primals via environment variables or UDS
filesystem convention. Validation escalates to Tier 2: Rust ecoBins
calling toadStool, barraCuda, and the provenance trio via Unix
sockets.

```bash
./validate                  # Auto-detects Tier 2 via discovery
./validate --tier 2         # Force Tier 2 (fails if primals absent)
```

### Mode 3: Geo-delocalized (remote gate via cellMembrane)

The USB is plugged into a remote gate (friend's house, family member's
machine). Primal IPC routes through Songbird TURN via the cellMembrane
relay at [RELAY_PUBLIC]:3478. The discovery chain extends:

```
env var ($TOADSTOOL_PORT) → UDS socket → Songbird TURN relay → None
```

```bash
export SONGBIRD_TURN_SERVER=[RELAY_PUBLIC]:3478
./validate                  # Tier 2 via TURN relay
```

All relay traffic is BTSP-encrypted. The cellMembrane sees only opaque
bytes. The remote gate's `liveSpore.json` entry records the geographic
context (BLAKE3-hashed hostname) without leaking PII.

---

## Provenance Trail (liveSpore.json)

Each `./validate` run appends a JSON entry:

```json
{
  "timestamp": "2026-05-14T14:30:00Z",
  "hostname_hash": "blake3(hostname)",
  "arch": "x86_64",
  "os": "linux",
  "tier_reached": 2,
  "modules_passed": 7,
  "modules_total": 7,
  "runtime_ms": 342000,
  "discovery_path": "uds",
  "turn_relay": null
}
```

Geo-delocalized runs include `"turn_relay": "[RELAY_PUBLIC]:3478"` and
`"discovery_path": "turn"` to record the relay path.

No PII is stored. The hostname is BLAKE3-hashed. The artifact
accumulates a provenance trail of where it has been and what it proved
-- publishable on sporePrint as auditable journal entries.

---

## sporePrint Return Path

The liveSpore provenance trail feeds back into the sporePrint
publishing pipeline:

```
USB ./validate at gate (local or remote)
  ├── liveSpore.json appended (provenance entry)
  ├── Foundation targets marked validated
  │
  └── Spring absorbs results
      ├── expected_values.json updated
      ├── notify-sporeprint.yml fires repository_dispatch
      ├── sporePrint auto-refresh.yml runs nbconvert
      └── Zola renders to primals.eco
```

Each validation at a different gate and architecture strengthens the
stadial evidence for interstadial exit. Cross-hardware validation of
Foundation threads (AMD at strandGate, NVIDIA at biomeGate, CPU-only
at remote gates) becomes publishable, auditable proof.

---

## Relationship to Other Deployment Classes

```
NUCLEUS     (full primal composition — gate, all atomics + Squirrel)
  ↓
Niche       (biomeOS deploy graph — selected primals, BYOB composition)
  ↓
fieldMouse  (minimal atomic/chimera — embedded, sensor, edge, no biomeOS)
  ↓
lithoSpore  (hypogeal cotyledon — self-contained USB with food + root)
  ↓
ColdSpore   (static artifact — frozen data, no runtime, no provenance)
```

The lithoSpore USB sits between fieldMouse (which requires a running
host system) and ColdSpore (which requires external orchestration).
It is the most portable deployment: a USB that validates science
anywhere there is a Linux kernel.

---

## SoloKey Witness (Future)

Both ironGate and eastGate have SoloKey 2 devices plugged in. When
BearDog FIDO2/CTAP2 integration ships, the `liveSpore.json` provenance
entry can include a hardware witness signature:

```json
{
  "timestamp": "...",
  "hostname_hash": "...",
  "solokey_witness": {
    "attestation": "fido2-assertion-base64",
    "key_id": "solokey-credential-id"
  }
}
```

This proves physical human presence at the gate during validation --
a stronger provenance claim than software-only timestamping.

---

## Two-Tier Data Model

The USB ships **summary statistics** (~3.4 MB total across all datasets) —
the same numbers published in peer-reviewed papers. Full upstream data
(raw sequencing reads, breseq outputs) ranges from 10–200 GB per dataset
and lives at SRA/NCBI, fetchable via `litho fetch --full` when online.

Upstream springs that computed the summaries from raw data record
provenance via the trio (rhizoCrypt + loamSpine + sweetGrass) and hand
the **braid** to lithoSpore. The braid IDs are stored in `data.toml` and
verified when NUCLEUS is reachable. Airgapped, the braid is documentation;
online, it's a verifiable chain.

See `handoffs/LITHOSPORE_FERMENT_TRANSCRIPT_BRAID_HANDOFF_MAY17_2026.md`
for the upstream contract.

---

## Cross-References

- `TARGETED_GUIDESTONE_STANDARD.md` — guideStone artifact standard, `liveSpore.json` schema
- `CELLMEMBRANE_FIELDMOUSE_DEPLOYMENT.md` — cellMembrane relay for geo-delocalized validation
- `MEMBRANE_CHANNEL_ARCHITECTURE.md` — Channel 2 (TURN relay) used by Mode 3
- `DOWNSTREAM_PATTERN_GUIDE.md` — spring → lithoSpore → sporePrint pipeline
- `FOUNDATION_INTEGRATION_GUIDE.md` — Foundation thread targets consumed by lithoSpore
- `sporePrint/CONTENT_GUIDE.md` — sporePrint publishing pipeline
- `handoffs/archive/CATHEDRAL_DEEP_DEBT_AUDIT_MAY13_2026.md` — lithoSpore debt resolution (archived)
- `plasmidBin/deploy_membrane.sh` — cellMembrane deployment with geo-delocalized gate support
- `handoffs/LITHOSPORE_FERMENT_TRANSCRIPT_BRAID_HANDOFF_MAY17_2026.md` — ferment transcript / braid handoff contract
