# Sovereign Compute Sharing — The "Lend a GPU to a Friend" Pattern

**Version**: 0.2.0
**Date**: May 2026
**Audience**: Any primal team, any operator with hardware to share
**Status**: Guidance — Phase 0 active, Phase 1 validated (Nest Atomic + provenance pipeline)

---

## The Pattern

Anyone with a GPU should be able to lend compute to a friend. That's it.

The friend sends data and a workload. The operator runs it on local hardware.
The friend gets results. The operator gets real-world pressure on their tools.
Over time, the manual process evolves into an automated, encrypted, composable
platform — but it starts with a human running a job for another human.

This document describes the pattern, not a specific deployment. Any machine,
any friend, any domain. ABG (Accelerated Bioinformatics Group) is the first
instance. The architecture is machine-agnostic.

---

## Physical Topology

The ecoPrimals cluster is physically co-located — ~11 machines in a basement
connected by Cat6e ethernet with a 10G backbone switch. This is a covalent
LAN, not a distributed mesh. Every gate can reach every other gate at wire
speed.

This matters for compute sharing because the **intake node** and the
**workload node** don't have to be the same machine.

### The NUC Intake Pattern

```
Internet → [NAT/Tunnel] → NUC (intake) → Cat6e LAN → workload gate
```

An Intel NUC (or similar expendable node) sits at the network edge as the
external-facing intake. It runs the tunnel endpoint and JupyterHub proxy.
The NUC has no valuable data — it's a sacrificial relay. If compromised,
wipe and rebuild.

Actual compute happens on internal gates (strandGate for bioinformatics,
biomeGate for HBM2 work, etc.). The NUC routes requests over the LAN to
whichever gate owns the workload.

This is a **covalent bonding challenge** for the NUCLEUS model. The NUC
and the workload gate must trust each other (genetic trust via bearDog)
and coordinate (biomeOS routing). Early phases use manual coordination;
later phases use the full covalent mesh.

| Component | Role | Example |
|-----------|------|---------|
| **Intake node** | Tunnel endpoint, reverse proxy, expendable | Intel NUC, NucBox M6 |
| **Workload gate** | Runs JupyterHub kernels, GPU compute | strandGate, biomeGate, southGate |
| **Cold storage** | Results archival, ZFS snapshots | westGate (76 TB) |

Long-term, biomeOS deploy graphs handle the intake → workload → storage
routing automatically. Short-term, the operator manually starts JupyterHub
on the right gate and the NUC is just a tunnel relay.

The NUC intake pattern converges with the **membrane channel architecture**
(see `MEMBRANE_CHANNEL_ARCHITECTURE.md`). The NUC serves the same role as
a VPS running Channel 3 (Surface) — it terminates TLS and reverse-proxies
to internal gates. Channel 2 (Relay) handles NAT traversal so external
peers can reach the NUC. The intake node is the physical instantiation of
the membrane surface on the LAN edge.

### sporePrint Deployment Evolution

The public site (primals.eco) and the compute platform share a convergent
path:

```
Now:     GitHub Pages + Cloudflare  →  static Zola site
Next:    + secure tunnel            →  JupyterHub for compute users
Then:    + petalTongue web          →  dynamic site + compute dashboard
Later:   + songBird NAT traversal   →  self-hosted, Cloudflare optional
Finally: + full BTSP                →  BTSP-only tunnel, zero externals
```

Each step eliminates an external dependency. The end state is a sovereign
site served over BTSP with no reliance on GitHub, Cloudflare, or any
third-party tunnel provider. We get there in cycles — each cycle is
validated by real users generating real pressure.

---

## Security Model: Assume Insecure, Evolve to BTSP

```
Phase 0: Manual         — "I know you from Discord"
Phase 1: Tunnel + Auth  — "I can see you're who you say you are"
Phase 2: BTSP Auth      — "bearDog cryptographically verifies your identity"
Phase 3: BTSP Transport — "ChaCha20-Poly1305 encrypts the session"
Phase 4: Full BTSP      — "Policy automation, agentic workloads"
```

### The Principle

**Start by assuming we are insecure.** No automation. Human approves every
action. This is honest and safe.

BTSP (BearDog Trust Security Protocol) progressively replaces human trust
with cryptographic trust. Each phase produces real security validation data
for bearDog and songBird. The security evolution IS the product — not a
prerequisite for shipping.

### Phase-by-Phase Security

| Phase | Trust Model | Automation | Recovery |
|-------|------------|------------|----------|
| 0 | Social ("I know you") | None — human runs everything | N/A |
| 1 | Tunnel + simple auth | None — human monitors | Pull the plug |
| 2 | BTSP Phase 2 (cryptographic identity) | Manual approval, crypto identity | Revoke key |
| 3 | BTSP Phase 3 (encrypted transport) | Partial — channel is AEAD-protected | Session invalidation |
| 4 | Full BTSP (policy + agentic) | Full — policy-based | Automated isolation |

**BTSP Phase 3 is already shipped.** As of May 2, 2026, all 13 primals
support `btsp.negotiate` → ChaCha20-Poly1305 AEAD with HKDF-SHA256
directional session keys. The cryptographic infrastructure exists. The
question is when external-facing use cases catch up to it.

---

## Evolution Phases

### Phase 0: Manual (Current)

The operator runs jobs on behalf of friends. Communication via Discord or
whatever channel exists. Data transferred via file sharing. Results returned
the same way.

**What this tests**: Nothing architectural. But it generates the first real
external workloads and builds human trust.

**Operator gets**: Real-world data for their validation pipelines. Every
standard-tool result (QIIME2, DESeq2, AlphaFold, Scanpy) becomes a
validation target for Rust reimplementations. The pattern:
published results → standard tools → Rust → primal compositions.

**Friend gets**: Free compute on hardware that outperforms cloud notebooks.

### Phase 1: JupyterHub on Any Machine

Stand up JupyterHub on a machine. Which machine doesn't matter. The pattern
is "make a Linux box with a GPU usable by a remote human."

**What to stand up**:

- JupyterHub (multi-user) with per-user notebook environments
- Pre-installed kernels for the friend's domain
  - For bioinformatics: Python (scanpy, pydeseq2, QIIME2), R (Seurat, DESeq2)
  - For other domains: whatever the friend needs
- Secure tunnel for external access (WireGuard, Tailscale, or SSH)
- Per-user storage on local disk
- Resource limits (cgroups/containers) for isolation

**Topology option**: If the cluster is a LAN (as with ecoPrimals), the
tunnel terminates on a NUC or lightweight intake node, and JupyterHub
runs on a heavier internal gate. The intake node is expendable. See
"The NUC Intake Pattern" above.

**Security posture**: Assume insecure. Human monitors all activity. The
tunnel is the only external surface. If compromised, pull the plug and
rebuild. No data on the intake node that can't be recreated.

**What this tests**:

- **Egress**: First time a machine serves an external user. Firewall rules,
  traffic patterns, unexpected behavior.
- **LAN routing**: Intake → workload gate forwarding over Cat6e. Does the
  NUC relay introduce latency or bottlenecks?
- **Multi-user isolation**: Do per-user notebook environments actually
  prevent cross-user interference?
- **Storage lifecycle**: User data creation, archival, deletion on someone
  else's machine.
- **Covalent bonding (early)**: Two machines (intake + workload) must
  coordinate. Manual now, bearDog-authenticated later.
- **The general question**: Is JupyterHub + tunnel sufficient for "lend
  compute to a friend"? What breaks?

**What this is NOT**: A production platform. A secure system. A permanent
deployment. It's a prototype for learning what the real problems are.

### Phase 2: petalTongue Web Alongside JupyterHub

Extend `petalTongue web` mode to serve interactive content alongside
JupyterHub. This is the convergence point — petalTongue progressively
replaces Zola as the sporePrint renderer (per
`[KEY_SCRUBBED]_EVOLUTION_ROADMAP.md`) and
simultaneously grows compute-facing features.

**New petalTongue capabilities**:

- Job status dashboard (SSE-powered, existing `/api/events` endpoint)
- Result visualization (grammar-of-graphics engine)
- Notebook launch links (redirect to JupyterHub with environment config)

**Security evolution**: BTSP Phase 2 authentication starts here. bearDog
verifies who the user is cryptographically before they reach JupyterHub.
Identity is no longer "I know your Discord handle" — it's key-based.

**Primal involvement**: petalTongue (UI), bearDog (auth), songBird
(networking/egress patterns learned from Phase 1).

### Phase 3: Workload Submission

sporePrint becomes a platform. Users (human or agentic) submit workloads
through petalTongue's web interface. The full primal composition handles
the lifecycle:

1. User submits workload via petalTongue web
2. petalTongue creates a biomeOS deploy graph (TOML DAG)
3. biomeOS routes to appropriate hardware via toadStool
4. toadStool dispatches to the target machine
5. Results stored in nestGate (content-addressed)
6. Results served back through petalTongue
7. Provenance chain recorded by loamSpine

**Security**: BTSP Phase 3 encrypted transport protects the full channel.
ChaCha20-Poly1305 AEAD, HKDF-SHA256 session keys, directional encryption.
Workload submission can begin to automate because the channel is encrypted
and the identity is authenticated.

**Human/agentic hybrid**: Initially, the operator (or their AI tooling)
reviews and approves submissions. The approval loop is manual but execution
is automated. Over time, approval evolves from human-in-the-loop to
policy-based to fully agentic.

**Primal involvement**: All of the above plus biomeOS (orchestration),
toadStool (dispatch), nestGate (storage), loamSpine (provenance).

### Phase 4: Full Compositional Platform

The general pattern is now a sovereign compute sharing platform. Any
primal operator can offer compute to any trusted peer.

| Primal | Role |
|--------|------|
| petalTongue | Interface (web, TUI, API) |
| biomeOS | Orchestration (deploy graphs, capability routing) |
| toadStool | Dispatch (CPU/GPU/NPU allocation) |
| songBird | Networking (secure external access, federation) |
| bearDog | Auth / BTSP (identity, keys, policy) |
| nestGate | Storage (content-addressed results, archival) |
| loamSpine | Provenance (audit trail, reproducibility) |
| squirrel | AI orchestration (agentic workload management) |

The platform doesn't need to be designed upfront. It evolves from real
use. Each friend who uses it generates selective pressure on the primals.

---

## How External Workloads Become Spring Validation Data

This is the key insight for why compute sharing is mutually beneficial.

The operator's Rust pipelines are validated against published results. The
friend runs standard tools (Python, R, established bioinformatics packages)
on the operator's hardware. Those standard-tool outputs become new validation
targets:

```
Friend's QIIME2 run         → wetSpring 16S validation target
Friend's DESeq2 analysis     → healthSpring DE validation target
Friend's AlphaFold prediction → helixVision structure target
Friend's Scanpy clustering    → neuralSpring ML validation target
```

The friend doesn't need to know about springs. They just use their tools.
The operator captures the outputs as ground truth for their Rust
reimplementations. The more friends use the hardware, the more validation
data accumulates, and the more the Rust tools evolve.

This is not extraction — it's the same pattern used internally. Published
results → standard tools → Rust → primal compositions. The friend's
science drives the direction of what the operator builds next.

---

## First Instance: ABG (Accelerated Bioinformatics Group)

ABG is a bioinformatics research Discord (~30 members, grad students through
professors). They need compute for scRNA-seq, bulk RNA-seq, metagenomics,
and structure prediction. They were told to use Google Colab.

**Phase 0 (active)**: Tamison runs jobs manually for ABG members.

**Phase 1 (validated 2026-05-04)**: JupyterHub + Full NUCLEUS (13 primals) on ironGate. Pre-installed: scanpy, pydeseq2, QIIME2, Seurat, DESeq2. 235+ wetSpring checks passing through toadStool dispatch, real NCBI data (PRJNA488170, 11.9M reads) processed, full provenance pipeline operational (BLAKE3 → rhizoCrypt DAG → loamSpine ledger → sweetGrass braid). See `[KEY_SCRUBBED]-sharing-logs-may2026/COMPOSITION_VALIDATION_LOG.md` (archived) and `projectNUCLEUS/validation/` for details.

**Phase 2a (validated 2026-05-06)**: Cloudflare Tunnel baseline captured (270ms p50 latency, 15/15 external checks). Three-layer pen testing completed. ABG tiered access operational:

| Tier | Group | Resources | Workspace Access |
|------|-------|-----------|-----------------|
| admin | `abg-admin` | 48G / 16c | Full — create projects, manage showcase/ |
| compute | `abg-compute` | 32G / 8c | commons/, projects/ — read + write + execute |
| observer | `abg-observer` | 8G / 4c | All — read only |
| reviewer | `abg-reviewer` | 4G / 2c | showcase/ only — for PIs and HPC admins |

**Shared workspace** (`/home/irongate/shared/abg/`): Google Doc model — all work visible to all members. No hidden files. commons/ for scratch, projects/ for organized work, showcase/ for polished results ready for external review. Templates and starter notebooks provided. See `projectNUCLEUS/specs/SHARED_WORKSPACE.md`.

**sporePrint integration**: Lab section at primals.eco/lab — public read-only view of validated results. `render_notebooks.sh` converts showcase notebooks to static HTML for Zola. Members can point a PI at primals.eco/lab to demonstrate what they want to run on larger systems.

**Domain-specific validation targets**:
- scRNA-seq outputs → wetSpring / neuralSpring
- Bulk RNA-seq DESeq2 → healthSpring
- Metagenomics → wetSpring (16S, QS gene analysis)
- Structure prediction → helixVision
- Immune pathway analysis → healthSpring (Anderson immunological framework)

**Relevant prior work** (published at primals.eco/science/):
- Papers 01, 05: 16S pipeline, cold seep metagenomics (6,600+ checks)
- Paper 12: Anderson in immunological signaling (329 checks)
- Paper 09: Field genomics architecture
- Paper 13: Sovereign human health (PK/PD, drug discovery)

---

## Future Instances

The pattern generalizes. Potential future friends:

- A physics lab that needs GPU time for simulation
- A game developer who needs compute for procedural generation testing
- A student who needs to run ML training but can't afford cloud
- Another primal operator offering reciprocal compute

Each instance follows the same phases. The domain-specific kernels and
validation targets change; the pattern doesn't.

---

---

## sporePrint Auto-Refresh

Springs and primals can push their own metric updates to sporePrint
(primals.eco) via the same `repository_dispatch` pattern used by plasmidBin.

**Pattern**: Source repo pushes to main → `notify-sporeprint.yml` fires
`repository_dispatch` → sporePrint `auto-refresh.yml` clones the source,
runs `spore-validate refresh --write`, commits updated `config.toml` →
`deploy.yml` rebuilds the site.

**Two tiers**:
- **Metrics** (LOC, tests, files, crates, version): auto-committed directly
  to main. Safe — mechanical numbers validated by `spore-validate`.
- **Content** (lab pages, validation summaries): opened as PR for review.
  Source repos can include a `sporeprint/` directory with markdown fragments.

**Secrets**: `SPOREPRINT_DISPATCH_TOKEN` on source repos (fires dispatch),
`SPOREPRINT_REFRESH_PAT` on sporePrint (clones sources including private,
pushes metrics commits, creates content PRs).

**Template**: `plasmidBin/templates/notify-sporeprint.yml` — copy to
`.github/workflows/` in any spring or primal repo.

**Source map**: `sporePrint/sources.toml` — maps entity IDs to GitHub repos.
Same structure as `plasmidBin/sources.toml` but includes springs.

This ensures primals.eco always reflects the current state of the ecosystem
without manual metric maintenance.

---

## Tiered Access Convergence (Wave 114+)

The four access tiers (observer, reviewer, compute, operator) are converging
with sovereignty-layer tools and primal-native replacements:

| Tier | Current Tool | Sovereignty Layer | Primal Endgame |
|------|-------------|-------------------|----------------|
| Observer (static) | pappusCast → HTML | pappusCast (self-hosted) | petalTongue static render |
| Reviewer (live read) | RustDesk view-only | RustDesk relay on golgiBody | songBird frame stream |
| User (compute) | JupyterHub + IDE | JupyterHub + Cursor/IDE | toadStool + squirrel |
| Operator (hardware) | SSH / console | Direct access | bearDog sovereign key |

**Key architectural principle**: Because remote protocols are parseable
(RustDesk separates video from input, JupyterHub separates render from
execute, IDE protocols separate read from write), view/action separation
can be enforced at the transport layer — not just application permissions.

**bearDog blindness**: In full BTSP Phase 4 deployment, hardware operators
and software admins are cryptographically blind to each other. User compute
state is encrypted per-user; operators cannot read it. This is structural
(key derivation prevents cross-branch decryption), not policy-based.

**RustDesk as reviewer tier**: The golgiBody-ext relay (:21115-21117)
enables view-only sessions — the reviewer sees live screen state but cannot
send input. This validates the separation before primal-native songBird
frame streaming replaces it.

**IDE convergence (Cursor-like)**: Scientists access a Cursor-like IDE that
pushes work to the mesh. The IDE is a thin client over the primal composition:
squirrel decomposes intent into atomic signals, biomeOS dispatches to
available hardware via toadStool. The user never directly touches the OS.

**fieldGate intake pattern**: The NUC intake node (fieldGate) routes external
users to workload gates by tier. Observer/reviewer traffic is lightweight
(static HTML / frame stream). Compute traffic routes to GPU gates (northGate,
strandGate). The intake node is expendable — no user state resides there.

Full architecture: `projectNUCLEUS/specs/TIERED_ACCESS_ARCHITECTURE.md`

---

*This document is a living pattern. Update after each phase transition
with observed friction points, security learnings, and primal evolution
triggered by external use.*
