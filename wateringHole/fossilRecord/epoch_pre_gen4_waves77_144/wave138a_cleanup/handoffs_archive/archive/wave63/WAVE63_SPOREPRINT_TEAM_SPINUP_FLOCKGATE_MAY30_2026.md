# Wave 63 — sporePrint: Dedicated Team Spinup on flockGate (WAN Shadow)

**Date**: May 30, 2026
**From**: primalSpring coordination (eastGate)
**To**: sporePrint team (NEW — spinning up on flockGate)
**Gate**: flockGate (i9-13900K, RTX 3070 Ti, 64GB — remote WAN node)
**Phase**: Team genesis + flockGate deployment + WAN shadow validation

---

## Mission

sporePrint is the public-facing science site at `primals.eco` — the living
document of the ecoPrimals project. This team is being spun up as a dedicated
team on flockGate, serving dual roles:

1. **sporePrint product team**: Evolve the site from ad-hoc content merges into
   a living, interactive scientific library with hosted pseudoSpore artifacts
2. **WAN shadow (flockGate)**: First remote covalent node — validates that the
   entire ecosystem works across WAN, not just LAN. Glacial shift criterion #4.

flockGate is on the other side of the state from the LAN gates. It connects
via cellMembrane (Songbird TURN relay on golgiBody VPS). Every sporePrint
build, every temporal sync, every primal composition on flockGate proves the
ecosystem works over real-world WAN latency.

---

## What You Have

sporePrint is a Zola static site with a Rust validation crate:

```
infra/sporePrint/
├── config.toml          # Zola site config, base_url = "https://primals.eco"
├── sources.toml         # GitHub repo map (primals + springs) for auto-refresh
├── content/
│   ├── science/         # 27 baseCamp companion papers
│   ├── architecture/    # 12 ecosystem architecture docs
│   ├── lab/             # 8 spring validation summaries + notebooks
│   │   ├── springs/     # Per-spring lab pages
│   │   └── notebooks/   # Rendered Jupyter notebooks (hotSpring CompChem)
│   ├── products/        # blueFish, esotericWebb, helixVision, lattice QCD
│   ├── guidestone/      # GuideStone verification class
│   ├── audience/        # PI, student, builder, compliance guides
│   ├── methodology/     # Constrained evolution, K-NOME, playbooks
│   └── technical/       # Hardware, grants, pipelines
├── templates/           # Tera HTML templates (base, page, section, taxonomy)
├── static/              # CSS, images, CNAME
├── crates/
│   └── spore-validate/  # Rust crate: typed validation, registry, metric sync
├── scripts/
│   ├── refresh-metrics.sh    # Clone upstream repos, run spore-validate refresh
│   └── render_notebooks.sh   # Jupyter → markdown lab pages
└── specs/               # Content standards (voice, taxonomy, templates, evolution queue)
```

**Current deployment**: GitHub Actions → GitHub Pages + Cloudflare CDN
**Live sovereign deployment**: golgiBody-ext VPS (`137.184.197.151`) serving via Caddy
**Target deployment**: golgiBody-ext serves primals.eco (DNS cutover pending)

---

## Prerequisites (complete BEFORE starting)

- [x] **SSH key registered on GitHub**: `gh ssh-key add ~/.ssh/id_ed25519.pub --title "flockGate"`
- [x] **SSH key registered on Forgejo**: Key ID 7, registered Wave 63
- [x] **Gate profile exists**: `[gates.flockGate]` in ecosystem_manifest.toml
- [ ] **Verify Forgejo connectivity**: `ssh -p 2222 git@git.primals.eco` should print `Hi golgiAdmin!`

See `GATE_SETUP_STANDARD.md` for the full prerequisites checklist.

---

## Pre-Bootstrap Cleanup

If flockGate previously had repos cloned at non-standard paths, remove them:

```bash
rm -rf ~/Development/ecoPrimals/songbird    # superseded by primals/songBird/
rm -rf ~/Development/ecoPrimals/toadstool   # superseded by primals/toadStool/
```

---

## Phase 1: flockGate Bootstrap (Immediate)

Before you can develop sporePrint, flockGate needs to be a working ecosystem gate.

### Gate Setup — K-Derm Diderm Path

The workspace is `~/Development/ecoPrimals/` — a plain directory, same as every
other gate. The VPS infrastructure is now a three-node diderm envelope:

- **golgiBody** (inner, `[RELAY_PUBLIC]`): Forgejo SSH at port 2222, sovereign git
- **peptidoglycan** (`[RELAY_PUBLIC]`): Full workspace, build hub, deployment source
- **golgiBody-ext** (outer, `137.184.197.151`): sporePrint hosting, TURN relay

```bash
# 1. Create workspace
mkdir -p ~/Development/ecoPrimals
cd ~/Development/ecoPrimals

# 2. Create gate identity
echo "flockGate" > .gate
export GATE_NAME=flockGate

# 3. Clone wateringHole (prefer Forgejo, fall back to GitHub)
mkdir -p infra
git clone ssh://git@git.primals.eco:2222/ecoPrimals/wateringHole.git infra/wateringHole
# Fallback: git clone git@github.com:ecoPrimals/wateringHole.git infra/wateringHole

# 4. Pull entire ecosystem via cascade-pull (WAN-safe with --shallow)
cd infra/wateringHole
./scripts/cascade-pull.sh --gate flockGate --clone-missing --shallow --source temporal
# If Forgejo unreachable, use: --source origin

# 5. Verify Songbird WAN connectivity (relayed via golgiBody-ext outer membrane)
export SONGBIRD_FEDERATION_PORT=7700
export SONGBIRD_PEERS=137.184.197.151:7700
```

### Known Large Repos (shallow clone recommended)

These repos will timeout on full WAN clone. `cascade-pull.sh --shallow` handles this,
or auto-shallows known large repos even without `--shallow`:

bearDog, songBird, toadStool, petalTongue, hotSpring, sporePrint, rustChip

To get full history later: `git fetch --unshallow`

### Dev Platform Standards

flockGate should run modern dev platform standards:

- **Rust**: latest stable (`rustup update stable`)
- **Zola**: latest release (for sporePrint builds)
- **plasmidBin**: fetch and deploy primals (`plasmidbin fetch --all && plasmidbin launch`)
- **membrane**: build from cellMembrane for temporal sync + VPS control
- Songbird with `SONGBIRD_PEERS` pointing at golgiBody for WAN relay

### WAN Validation Checklist

- [ ] `cascade-pull.sh --source temporal` works from flockGate (proves WAN fetch)
- [ ] `SONGBIRD_PEERS` connects to golgiBody TURN relay
- [ ] `plasmidbin launch` deploys NUCLEUS on flockGate (proves WAN binary fetch)
- [ ] `zola build` in sporePrint succeeds (proves content pipeline)
- [ ] Cross-gate `discovery.peers` from flockGate → eastGate via WAN
- [ ] `capability.call` from flockGate → any LAN gate via Songbird relay

---

## Phase 2: sporePrint Evolution (Ongoing)

### Current State Audit

Review this repo's codebase, specs/, docs, and the ecosystem standards at
`ecoPrimals/infra/wateringHole/` (especially `README.md`,
`PURE_RUST_SOVEREIGN_STACK_GUIDANCE.md`, `SCYBORG_PROVENANCE_TRIO_GUIDANCE.md`,
`ECOBIN_ARCHITECTURE_STANDARD.md`, `PRIMAL_REGISTRY.md`, and
`NUCLEUS_SPRING_ALIGNMENT.md`). Also review sibling springs for handoff
patterns and cross-spring conventions.

sporePrint is not a spring (it doesn't validate science baselines), but it
should follow spring-grade development standards:

**COMPLETION STATUS**: What have we not completed? What mocks, TODOs, FIXMEs,
debt, hardcoding (paths, URLs, primal names) and gaps remain? Is every
content page traceable to a source repo and commit?

**CODE QUALITY**: `spore-validate` crate — passing all linting, fmt, clippy
(pedantic+nursery), doc checks with zero warnings? Idiomatic Rust? Zero
unsafe in application code (`#![forbid(unsafe_code)]`). Zero `#[allow()]`
in production code. All files under 1000 LOC. Pure Rust deps only (ecoBin
compliant). Is the Zola theme clean and modern?

**CONTENT FIDELITY**: Do ALL validation summaries match current upstream
primal/spring state? Are test counts, version numbers, and capability lists
current? Is `sources.toml` complete and accurate? Are science papers
linked to reproducible evidence (notebooks, sporePrint lab pages)?

**ECOSYSTEM STANDARDS** (wateringHole/):
  - License: AGPL-3.0-or-later (code), CC-BY-SA 4.0 (content)
  - Architecture: ecoBin compliant (pure Rust deps for spore-validate)
  - Sovereignty: no vendor lock-in. GitHub Pages is extracellular shadow,
    not permanent home. Target: Caddy on golgiBody VPS.
  - Handoffs: wateringHole/handoffs/ follow naming convention

**SCRIPTS AUDIT**: `refresh-metrics.sh` and `render_notebooks.sh` are bash.
These should eventually evolve to Rust (spore-validate absorbs). For now,
audit for correctness and hardcoded paths.

### pseudoSpore Gallery (New Feature)

The primary evolution target: hosted interactive pseudoSpore pages.

**What to build**:
1. Zola template for `/lab/spores/{name}/` gallery pages
2. Each gallery page shows: computation receipts, braid provenance, data
   outputs, module pass/fail status, "Download lithoSpore" link
3. Gallery index at `/lab/spores/` listing all available pseudoSpores
4. `spore-validate` learns to read lithoSpore `registry.toml` and generate
   gallery page front matter

**Data flow**:
```
spring emits pseudoSpore (litho emit-pseudospore)
  → lithoSpore registry.toml updated
  → spore-validate reads registry, generates gallery markdown
  → Zola builds gallery pages
  → Deploy to VPS (Caddy serves primals.eco)
  → Visitor browses → clicks "Download lithoSpore"
  → Gets self-contained reproduction package
```

**Available pseudoSpores now**:
- hotSpring CompChem GuideStone v1.6.1 (7/8 modules, reference implementation)
- healthSpring (domain_profile.toml shipped Wave 63, emission pending)

### Content Pipeline Evolution

Currently sporePrint uses GitHub Actions `repository_dispatch` for auto-refresh.
This should evolve to:

1. **projectFOUNDATION-driven ingestion**: Foundation captures spring validation
   results and publishes structured content to sporePrint
2. **Temporal sync-driven updates**: When a spring pushes, temporal sync on
   flockGate detects the change and triggers a local rebuild
3. **VPS deployment**: `zola build` on golgiBody, Caddy serves the result

### VPS Hosting Migration — K-Derm Diderm Architecture (Wave 63)

The VPS infrastructure is now a proper K-Derm diderm envelope with three nodes:

```
Inner membrane (golgiBody, [RELAY_PUBLIC]):
  Forgejo, NUCLEUS primals, knot-dns, BTSP auth
  Bond: covalent/metallic — gates only

Peptidoglycan (peptidoglycan, [RELAY_PUBLIC]):
  Full 39-repo workspace, Rust toolchain, Zola, membrane binary
  Bond: metallic — build/sync hub between inner and outer
  Role: Clone from here, build here, converge here

Outer membrane (golgiBody-ext, 137.184.197.151):
  Caddy TLS, sporePrint hosting (LIVE — HTTP 200), TURN relay
  Bond: ionic/weak — public-facing
```

sporePrint is LIVE on golgiBody-ext. Migration path to full sovereignty:

```
Phase A (DONE): sporePrint built and served on golgiBody-ext via Caddy
Phase B: DNS cutover — primals.eco A record → 137.184.197.151
Phase C: HTTPS via Caddy automatic TLS (Let's Encrypt)
Phase D: GitHub Pages becomes extracellular shadow (backup)
```

Build pipeline: peptidoglycan builds → rsync/scp to golgiBody-ext → Caddy serves

---

## Phase 3: WAN Shadow Role (Continuous)

flockGate is the first remote covalent node. As the sporePrint team, you are
also the WAN validation team. Every daily operation validates:

- **Temporal sync over WAN**: Does `cascade-pull.sh --source temporal` converge
  from a remote site? Latency? Failures?
- **Songbird relay**: Does the TURN relay on golgiBody handle persistent
  WAN connections for mesh federation?
- **Content freshness**: Does sporePrint on flockGate stay current with
  upstream spring pushes via temporal sync?
- **NUCLEUS over WAN**: Can NUCLEUS compositions run with primals fetched
  over WAN? What's the cold-start time?

Report WAN findings back via wateringHole handoffs — these are glacial shift
validation evidence for criterion #4 (remote covalent node validated over WAN).

---

## Proto-Nucleate Composition

sporePrint's NUCLEUS composition for content serving:

```
Tower Atomic:  BearDog (TLS certs, content signing) + Songbird (discovery, WAN relay)
Nest Atomic:   NestGate (content-addressed storage) + sweetGrass (provenance braids)
Meta:          petalTongue (rendering) + biomeOS (orchestration)

NOT needed:    Node Atomic (no GPU compute — sporePrint is content, not science)
```

sporePrint should register capabilities:
- `content.serve` — serve static site content
- `content.gallery` — serve pseudoSpore gallery pages
- `content.refresh` — trigger content rebuild from upstream sources

---

## Success Criteria

### Immediate (Wave 63)
- [ ] flockGate bootstrapped — ecoPrimals workspace cloned, `.gate` file created
- [ ] `cascade-pull.sh --source temporal` succeeds from flockGate over WAN
- [ ] Songbird WAN relay connects flockGate → golgiBody → LAN mesh
- [ ] `zola build` succeeds locally on flockGate
- [ ] sporePrint codebase audited against ecosystem standards

### Near-term (Wave 64-65)
- [ ] pseudoSpore gallery template implemented and serving 2+ spores
- [ ] `spore-validate` reads lithoSpore registry and generates gallery content
- [x] sporePrint builds and serves on golgiBody-ext via Caddy (DONE — Wave 63)
- [ ] DNS cutover: primals.eco A record → golgiBody-ext (137.184.197.151)
- [ ] Cross-gate `capability.call` proven over WAN (flockGate → LAN gate)

### Glacial Gate
- [ ] flockGate validated as remote covalent node (criterion #4)
- [ ] primals.eco DNS cutover to sovereign (criterion #5/6)
- [ ] sporePrint is the living interactive library — link, not tarball
