# Wave 63 — sporeGarden Products: projectNUCLEUS, projectFOUNDATION, pseudoSpore Hosting

**Date**: May 30, 2026
**From**: primalSpring coordination (eastGate)
**To**: projectNUCLEUS, projectFOUNDATION, lithoSpore, sporePrint teams
**Phase**: River delta → product evolution

---

## Summary

Mountain primals are at zero debt. Springs are pushing from their gates. The
sporeGarden products are the next evolution tier — they consume the ecosystem
and deliver value to external audiences. This handoff defines the long-term
trajectory for each product and the immediate Wave 63 work.

---

## Product Roles (Clarified)

```
primalSpring (defines patterns) ─────────────────────────────┐
       ↓                                                      │
projectNUCLEUS (deploys patterns on gates + VPS)             │
       ↓                     ↑                                │
  ABG workloads ────→ gap handbacks ──→ projectFOUNDATION ───┘
                                        (the soil: validated lineage,
                                         living evidence, hosted spores)
       ↓
  sporePrint (the face: primals.eco, hosted pseudoSpore library)
       ↓
  lithoSpore (self-contained reproduction chassis for end users)
```

### projectNUCLEUS — Late-Stage Deployment Patterns

**Role**: Deploy the ecosystem for real use. Host compute and data support for
the ABG group (academic/biotech/government collaborators). Every ABG workload
validates that primalSpring's deploy graphs, BTSP, discovery hierarchy, and
provenance pipeline work in production.

**Current state**: 6 hotSpring workload definitions, VPS depot config, gate
provisioning scripts, Forgejo mirror tooling, sporePrint DNS management.
46 deploy scripts (mostly bash).

**Evolution trajectory**:
- Absorb ABG compute hosting: JupyterHub with BTSP auth, tier-based GPU access
- Sovereign DNS cutover (knot-dns replaces Cloudflare)
- Deploy pseudoSpore hosting on VPS (serve via petalTongue or static Caddy)
- Evolve deploy scripts from bash to Rust (cellMembrane membrane-shadow pattern)

### projectFOUNDATION — Living Evidence Layer

**Role**: Ingest and evolve the springs' scientific output. The soil that
NUCLEUS grows on — 10 domain threads, 26 baseCamp companion papers, 70+
reproduced papers, 8 springs with 13,100+ quantitative checks. Should work
more closely with sporePrint to evolve it from ad-hoc content merges into a
living document of the project.

**Current state**: UniBin Rust binary (`foundation` CLI), Phase B sealed,
deep debt resolved (Wave 59b). Has `sporeprint/` dir but only contains a
validation summary stub.

**Evolution trajectory**:
- **sporePrint ingestion pipeline**: foundation should drive sporePrint content
  generation — when a spring validates, foundation captures the evidence and
  publishes it to sporePrint automatically
- **pseudoSpore hosting**: foundation should manage the pseudoSpore library on
  VPS — ingested spores become browsable, interactive artifacts that anyone
  can access via `https://primals.eco/lab/spores/<name>`
- **lithoSpore emission**: foundation should coordinate with lithoSpore so that
  hosted pseudoSpores can be "taken home" — a visitor creates a lithoSpore on
  their side from the hosted spore

### sporePrint — The Public Face

**Role**: `primals.eco` — the static site (currently GitHub Pages + Cloudflare).
Contains lab notebooks, validation summaries, architecture docs, science sections.

**Current state**: Zola static site generator. Auto-merge content from springs.
`base_url = "https://primals.eco"`. Currently extracellular (GitHub Pages).

**Evolution trajectory**:
- **VPS hosting**: Move from GitHub Pages to sovereign hosting on golgiBody VPS
  via Caddy (sovereignty shadow S3 cutover)
- **pseudoSpore gallery**: Add interactive pseudoSpore pages — instead of sending
  tarballs, send a link to `primals.eco/lab/spores/hotspring-compchem-guidestone`
  where visitors can browse computation receipts, braid provenance, data outputs
- **lithoSpore download**: Each gallery entry includes "Take this home" —
  generates a lithoSpore package the visitor can download and run locally

### lithoSpore — Self-Contained Reproduction

**Role**: USB-deployable verification chassis. The hypogeal cotyledon — carries
its own food supply. Currently LTEE-focused with `pseudospore-core` crate.

**Current state**: `pseudospore-core` (tarball, envelope, braid, validation,
receipts, domain_profile). Registry has 1 ingested spore (hotSpring CompChem
v1.6.1, 7/8 modules pass). 10 LTEE-specific crates. Containerfile for deployment.

**Evolution trajectory**:
- **Domain-agnostic emission**: `litho emit-pseudospore` should work for any
  spring's `domain_profile.toml` (hotSpring proven, 6 more springs pending)
- **Remote spore fetch**: `litho fetch --from primals.eco/lab/spores/<name>` —
  pull a pseudoSpore from the hosted gallery and set up local reproduction
- **Validation round-trip**: Local lithoSpore validates → results push back to
  foundation → foundation updates sporePrint evidence

---

## Wave 63 Immediate Work

### projectNUCLEUS

| Task | Priority | Detail |
|------|----------|--------|
| pseudoSpore hosting Caddy config | **HIGH** | Add a Caddy route for `primals.eco/lab/spores/` on golgiBody VPS. Serve pseudoSpore artifacts as static browsable pages. |
| ABG workload definitions | MEDIUM | Expand beyond hotSpring — add workload TOMLs for wetSpring (LTEE/breseq), neuralSpring (inference), healthSpring (PK-PD) |
| Deploy script audit | LOW | 46 bash scripts in `deploy/`. Identify which are active, which are stale. Begin Rust evolution for critical-path scripts. |

### projectFOUNDATION

| Task | Priority | Detail |
|------|----------|--------|
| sporePrint content pipeline | **HIGH** | Wire foundation to generate sporePrint content when springs emit pseudoSpores. Replace ad-hoc auto-merge with structured ingestion. |
| pseudoSpore library management | **HIGH** | Foundation manages the spore catalog — reads `registry.toml` from lithoSpore, generates browsable gallery pages for sporePrint |
| `domain_profile.toml` integration | MEDIUM | As springs write `domain_profile.toml`, foundation should ingest and index them |

### sporePrint

| Task | Priority | Detail |
|------|----------|--------|
| pseudoSpore gallery template | **HIGH** | Zola template for `/lab/spores/{name}/` — shows computation receipts, braid provenance, data outputs, "take home" download link |
| VPS build pipeline | MEDIUM | `zola build` on golgiBody → serve from Caddy (supplements or replaces GitHub Pages) |
| healthSpring `domain_profile.toml` content | DONE | healthSpring shipped BTSP probe + domain_profile.toml (Wave 63) |

### lithoSpore

| Task | Priority | Detail |
|------|----------|--------|
| Multi-spring emission test | **HIGH** | healthSpring has `domain_profile.toml` now — run `litho emit-pseudospore --spring healthSpring` and validate |
| Remote fetch subcommand | MEDIUM | `litho fetch --from <url>` — pull pseudoSpore from hosted gallery |
| Registry automation | LOW | Auto-update `registry.toml` when new spores are ingested |

---

## pseudoSpore Hosting Architecture

The end goal: a visitor at `primals.eco/lab/spores/hotspring-compchem-guidestone`
sees an interactive page with:

```
┌─────────────────────────────────────────────────────┐
│  hotSpring CompChem GuideStone v1.6.1               │
│  ─────────────────────────────────────────────────  │
│  7/8 modules validated | 3,400+ tests              │
│                                                     │
│  Computation Receipts:                              │
│  ├── Yukawa MD: ε=0.2% vs Stanton-Murillo 2016     │
│  ├── Lattice QCD: plaquette 0.5933 vs literature    │
│  ├── Gradient flow: t₀ = 0.1117 vs BMW 2012        │
│  └── ... 4 more modules                            │
│                                                     │
│  Braid Provenance: sweetGrass W3C PROV-O            │
│  Data: 14 notebooks, 6 workloads                    │
│                                                     │
│  [ Download lithoSpore ]  [ View Source on Forgejo ] │
└─────────────────────────────────────────────────────┘
```

**Data flow**:
1. Spring team runs `litho emit-pseudospore` → generates artifact
2. Foundation ingests artifact → updates registry → generates gallery page
3. sporePrint builds with gallery template → deploys to VPS
4. Visitor browses → clicks "Download lithoSpore" → gets self-contained package
5. Visitor runs lithoSpore locally → validates → optionally pushes results back

**VPS stack**:
- Caddy serves `primals.eco` (sovereign, replaces GitHub Pages)
- pseudoSpore artifacts in `/opt/ecoPrimals/sporePrint/spores/`
- petalTongue renders interactive pages (or static Zola fallback)
- NestGate stores artifact provenance (content-addressed)
- BearDog signs download bundles (BLAKE3 + Ed25519)

---

## Forgejo Mirror Status

| Repo | Org | Mirror | Convert Priority |
|------|-----|--------|-----------------|
| projectNUCLEUS | sporeGarden | pull mirror | HIGH — needs bidirectional for VPS deploy |
| projectFOUNDATION | sporeGarden | pull mirror | HIGH — needs bidirectional for content pipeline |
| lithoSpore | sporeGarden | pull mirror | MEDIUM |
| sporePrint | ecoPrimals | pushed successfully | Already bidirectional or not a mirror |

---

## Success Criteria (Wave 63-64)

- [ ] pseudoSpore gallery template exists in sporePrint
- [ ] At least 2 pseudoSpores in lithoSpore registry (hotSpring + healthSpring)
- [ ] sporePrint builds and serves on golgiBody VPS via Caddy
- [ ] Foundation drives sporePrint content (not ad-hoc auto-merge)
- [ ] projectNUCLEUS + projectFOUNDATION Forgejo repos converted to bidirectional
- [ ] `primals.eco/lab/spores/` serves at least 1 interactive pseudoSpore page
