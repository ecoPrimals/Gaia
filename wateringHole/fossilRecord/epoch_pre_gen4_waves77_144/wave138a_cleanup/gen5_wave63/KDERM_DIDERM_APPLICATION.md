# Gen5 — K-Derm Diderm Application: Physical Envelope Deployment

**Authority**: wateringHole consensus (Wave 63)
**Prerequisites**: K_DERM_TOPOLOGY_STANDARD.md, BONDING_MODEL_STANDARD.md
**Status**: LIVE — deployed May 30, 2026

---

## Overview

Gen5 marks the physical realization of the K-Derm diderm topology. Where Gen4
described the conceptual cell envelope and Golden Cage, Gen5 deploys it as
real infrastructure: three VPS nodes forming inner membrane, peptidoglycan,
and outer membrane. Every service has a defined K-Derm layer, bond type
permission, and channel protein mediator.

Gen4 → Gen5 transition: concepts become infrastructure.

---

## Diderm Envelope — Physical Mapping

### Layer → Node → Services

| K-Derm Layer | Physical Node | IP | Services | Bond Types |
|-------------|---------------|-----|----------|------------|
| Cytoplasm | LAN gates (eastGate, ironGate, southGate, biomeGate) | LAN | 13 NUCLEUS primals, UDS IPC | Covalent |
| Plasma membrane | Gate firewall (UFW/nftables) | — | Tower mediates all exits | Covalent, Metallic |
| Inner membrane | golgiBody VPS | [RELAY_PUBLIC] | Forgejo, NUCLEUS primals, knot-dns, BTSP auth | Covalent, Metallic |
| Peptidoglycan | peptidoglycan VPS | [RELAY_PUBLIC] | Workspace, builds, temporal sync | Metallic |
| Outer membrane | golgiBody-ext VPS | 137.184.197.151 | Caddy, sporePrint, TURN, RustDesk | Ionic, Weak |
| Extracellular | GitHub, public internet | — | Trailing mirrors, CDN, CI | Weak |

### Bond Type Interactions at Each Boundary

```
Cytoplasm ←─[covalent: UDS IPC, family seed]──→ Plasma membrane
Plasma    ←─[covalent/metallic: SSH, Tower]──→ Inner membrane (golgiBody)
Inner     ←─[metallic: SSH, fleet ops]──→ Peptidoglycan
Peptido   ←─[ionic: BTSP-scoped]──→ Outer membrane (golgiBody-ext)
Outer     ←─[weak: public read-only]──→ Extracellular
```

### Channel Proteins per Boundary

| Boundary | Channel Protein | Mechanism |
|----------|----------------|-----------|
| Cytoplasm → Plasma | Aquaporin | Always open (UDS, shared seed) |
| Plasma → Inner | Aquaporin | SSH covalent (registered keys) |
| Inner → Peptidoglycan | Aquaporin | SSH metallic (fleet keys) |
| Peptidoglycan → Outer | Gated ion | BTSP-scoped tokens, method filtering |
| Outer → Extracellular | Passive diffusion | Public read-only, no active transport |

---

## Golgi cis/trans Model

The biological Golgi apparatus has cis (receiving) and trans (shipping) faces.

**golgiBody (cis)**: receives from gate cytoplasm, processes, stores in Forgejo.
Gates push evolution upward through covalent bonds. Forgejo is the sovereign
git store — the receiving face.

**golgiBody-ext (trans)**: ships to the public, handles external interactions.
sporePrint content, pseudoSpore galleries, WAN relay for remote gates.
The shipping face.

**peptidoglycan**: the rigid structural layer between cis and trans.
Provides mechanical strength (build infrastructure), holds the envelope shape
(temporal sync convergence), and enables selective transport between faces.

---

## Bonding Interactions — Service Examples

### Covalent (cytoplasm ↔ inner membrane)

- Gate pushes `git push forgejo main` to golgiBody Forgejo
- cascade-pull fetches from Forgejo via SSH
- NUCLEUS primals communicate via UDS IPC within golgiBody
- Family seed shared across covalent boundary

### Metallic (inner ↔ peptidoglycan)

- peptidoglycan clones from golgiBody Forgejo (fleet SSH key)
- membrane binary built on peptidoglycan from cellMembrane source
- Temporal sync validates convergence across both nodes
- Build artifacts flow both directions (delocalized)

### Ionic (peptidoglycan ↔ outer)

- sporePrint built on peptidoglycan, deployed to golgiBody-ext
- BTSP-scoped tokens authorize specific operations
- Method-level filtering: `content.serve` allowed, `storage.*` denied
- Capability masks enforce least-privilege

### Weak (outer ↔ extracellular)

- Public visitors browse sporePrint at primals.eco
- GitHub trailing mirrors sync via weak/ionic hybrid
- No active transport: read-only content, no braid provenance crosses
- Passive diffusion only

### Ceremony (time-bound decay)

- Workshop access granted to ABG collaborators
- Starts as ionic (BTSP token), decays to weak over time
- Used for visiting researcher access to lab.primals.eco

---

## Endosymbiosis Path

External VPS services can be absorbed through bond escalation:

| Phase | Bond | State | Example |
|-------|------|-------|---------|
| 1 External | Weak | Separate organism | GitHub Actions, Let's Encrypt |
| 2 Contract | Ionic | Symbiotic, own membrane | DigitalOcean VPS |
| 3 Fleet | Metallic | Delocalized, specialized | peptidoglycan build hub |
| 4 Internalized | Covalent | External membrane → host layer | westGate NAS, future sovereign HSM |

---

## Multi-Vendor Evolution Path

The diderm model is vendor-agnostic. Current deployment is DigitalOcean nyc1,
but the architecture supports:

- **Multi-diderm**: Shared periplasm, multiple outer membranes (e.g. DO + Hetzner)
- **Nested diderm**: One system's outer membrane = another's periplasm (e.g. university lab)
- **Geo-distributed**: Inner in nyc1, outer in eu-west, peptidoglycan in both

The structural invariant: inner membrane is always sovereign (covalent access only),
outer membrane is always expendable (can be replaced without data loss).

---

## Configuration Reference

### ecosystem_manifest.toml

```toml
[topology]
model = "diderm"
inner_membrane = "golgiBody"
peptidoglycan = "peptidoglycan"
outer_membrane = "golgiBody-ext"

[topology.hosts]
golgiBody = "[RELAY_PUBLIC]"
peptidoglycan = "[RELAY_PUBLIC]"
golgiBody-ext = "137.184.197.151"
```

### membrane.toml

```toml
[membrane.layers.inner]
host = "golgiBody"
services = ["forgejo", "nucleus-primals", "knot-dns", "btsp-auth"]

[membrane.layers.peptidoglycan]
host = "peptidoglycan"
services = ["workspace", "builds", "temporal-sync", "membrane-binary"]

[membrane.layers.outer]
host = "golgiBody-ext"
services = ["caddy-tls", "sporeprint", "turn-relay", "rustdesk"]
```
