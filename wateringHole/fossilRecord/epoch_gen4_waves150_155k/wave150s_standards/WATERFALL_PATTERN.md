# WaterFall Pattern — Sovereign Gate Sync

**Pattern class**: firstLast coordination (biomeOS neuralAPI)
**Lineage**: Parallels **RootPulse** — both are distributed coordination patterns.
RootPulse coordinates primals for single-repo version control within a
cytoplasm; WaterFall coordinates membranes for multi-repo ecosystem sync
across envelope layers.

**Status**: Phase 1–4 implemented. Phase 4 inversion LIVE (Wave 63+).
Gates push to Forgejo only; K-Derm diderm relay chain propagates to GitHub
via peptidoglycan → golgiBody-ext with proper bond-type degradation.
Phase 5 specified (gate specialization + covalent routing).
**Wave 65**: `temporal.cascade` fully Rust (replaces bash `cascade-pull.sh`),
`plasmid.fetch` fully Rust (replaces bash `fetch_primals.sh`), manifest-driven
gate discovery (no hardcoded gate lists), dynamic validation.

## K-Derm Topology

The diderm cell envelope model from `cellMembrane` provides the
architectural framing. Each layer maps to an ecosystem component:

| K-Derm Layer        | Ecosystem Component                        | Role in WaterFall                                |
|---------------------|--------------------------------------------|--------------------------------------------------|
| **Cytoplasm**       | Gate NUCLEUS workspace                     | Local evolution — repos evolve independently     |
| **Plasma membrane** | Gate firewall + SSH keys                   | Covalent boundary — SSH auth to periplasm        |
| **Periplasm**       | Forgejo on VPS — golgiBody (`git.primals.eco`) | WaterFall mediator — distributes pulls, receives pushes |
| **Outer membrane**  | VPS channels (Caddy, sporePrint, TURN)     | Service surface — lab.primals.eco, membrane.primals.eco |
| **Extracellular**   | GitHub                                     | Trailing mirror — outer-world CI and discovery   |

The **peptidoglycan layer** (Caddy TLS surface + static lab) sits between
the outer membrane and periplasm, providing structural rigidity — this is
now live at `lab.primals.eco`.

## Flow

```
                    ┌──────────────────────────────────┐
                    │        Extracellular (GitHub)     │
                    │   trailing mirror (weak bond)     │
                    └──────────────┬───────────────────┘
                                   │ weak (membrane relay.ship)
                    ┌──────────────┴───────────────────┐
                    │  Outer Membrane (VPS channels)    │
                    │  lab.primals.eco, sporePrint       │
                    └──────────────┬───────────────────┘
                                   │ webhook
                    ┌──────────────┴───────────────────┐
                    │   Periplasm (Forgejo)             │
                    │   git.primals.eco                 │
                    │   38 repos, waterfall source      │
                    └───┬───────┬───────┬──────────────┘
                        │       │       │
          ┌─────────────┘       │       └──────────────┐
          ▼                     ▼                      ▼
    ┌───────────┐       ┌───────────┐          ┌───────────┐
    │ eastGate  │       │ southGate │          │ biomeGate │
    │ cytoplasm │       │ cytoplasm │          │ cytoplasm │
    └───────────┘       └───────────┘          └───────────┘

    ─── waterfall down: membrane temporal.cascade ───▶
    ◀── evolution up:   git push forgejo ──────────────
```

### Waterfall Down (pull)

Gates invoke `membrane temporal.cascade`. The Rust binary:

1. Reads `ecosystem_manifest.toml` for gate profile, sync config, and Forgejo SSH URL
2. For each repo in the gate's manifest, selects the temporal leader remote
3. Executes `git pull --ff-only <remote>` concurrently across repos
4. Reports per-repo status (OK, SKIP, FAIL) with timing

**Historical note**: `cascade-pull.sh` (1,029 lines) was the bash predecessor.
It was fossilized in Wave 66 (June 2026). All gates now use `membrane temporal.cascade`.

### Evolution Up (push)

Individual repos push to Forgejo after local development:

```bash
git push forgejo main
```

Forgejo post-receive hooks then:
- Push to GitHub as a trailing mirror (extracellular)
- Trigger sporePrint webhook refresh (outer membrane)

## Configuration

### ecosystem_manifest.toml

```toml
[sync]
forgejo_base_url = "https://git.primals.eco"
forgejo_ssh = "ssh://git@git.primals.eco:2222"
forgejo_host = "golgiBody"
default_source = "temporal"
default_branch = "main"
push_to_followers = true
push_target = "forgejo"       # Phase 4 inversion: gates push to Forgejo only

[repos.primalSpring]
# ... existing fields ...
forgejo_repo = "syntheticChemistry/primalSpring"
```

**`push_target`**: Controls where temporal sync pushes. `"forgejo"` means gates
push only to the Forgejo remote (golgiBody-inner, cis face). The K-Derm diderm
relay chain propagates to GitHub through peptidoglycan → golgiBody-ext.
Set to `"all"` for legacy dual-push behavior (bypasses K-Derm layers).

### Gate-level override

```bash
# ~/.config/cascade-pull.env (or environment variable)
CASCADE_SYNC_SOURCE=forgejo
```

### membrane temporal.cascade flags

| Flag                  | Description                                      |
|-----------------------|--------------------------------------------------|
| `--gate auto`         | Auto-detect gate identity from `.gate` file      |
| `--gate <name>`       | Specify gate explicitly                          |
| `--source temporal`   | Use temporal leader (default)                    |
| `--check`             | Dry-run: report status without pulling           |
| `--clone-missing`     | Clone repos not yet present on this gate         |

## Inversion Protocol (Phase 3–4)

The inversion flips Forgejo from trailing mirror to primary source.

### Phase 3: Shadow Period (dual-source validation)

1. Run `membrane temporal.cascade --check` alongside normal pulls
2. Compare HEADs from both remotes for parity
3. Track parity for 7+ days (matching membrane telemetry cutover gate)
4. Extend `s_ecosystem_freshness` or add `s_ecosystem_forgejo_parity`
   to validate in CI

### Phase 4: Inversion — LIVE (Wave 63+)

1. `[sync].push_target = "forgejo"` in manifest — gates push to Forgejo only
2. `[sync].default_source = "temporal"` — pull from whichever remote leads
3. K-Derm diderm relay chain wired with proper bond-type degradation:
   - Gate → golgiBody-inner (covalent: Forgejo receives)
   - golgiBody-inner → peptidoglycan (metallic: `pepti-sync-relay.sh` syncs)
   - peptidoglycan → golgiBody-ext (ionic: relay to outer membrane)
   - golgiBody-ext → GitHub (weak: `ext-github-push.sh` ships extracellularly)
4. GitHub SSH write credentials live only on golgiBody-ext (trans/shipping face)
5. GitHub becomes the external linear ledger (analogous to loamSpine → BTC/ETH)
6. `topology.roles` in manifest declares per-layer function assignments
7. Impulse cascade runs on peptidoglycan during relay

**Implementation files**:
- `hooks/forgejo/pepti-sync-relay.sh` — peptidoglycan metallic→ionic relay
- `hooks/forgejo/ext-github-push.sh` — golgiBody-ext trans face GitHub push
- `hooks/forgejo/impulse-relay-hook.sh` — standalone impulse detection
- `graphs/waterfall_publish.toml` — full cascade graph specification

**K-Derm diderm relay** (Wave 63+): Proper bond-type degradation wired.
`pepti-sync-relay.sh` on peptidoglycan mediates between inner and outer.
`ext-github-push.sh` on golgiBody-ext (trans face) pushes to GitHub.
Flow: inner (covalent) → peptidoglycan (metallic) → golgiBody-ext (ionic) → GitHub (weak).
GitHub SSH write credentials live only on golgiBody-ext (outer membrane).
See `hooks/forgejo/README.md` for relay chain setup.

### Rollback

If Forgejo becomes unavailable during shadow period or after inversion:
```bash
cascade-pull --source github    # explicit fallback
```

## Phase 5: Multi-Biome / Multi-Membrane — Gate Specialization

Once gates pull from Forgejo and push back to it, WaterFall becomes a
full biomeOS coordination pattern with covalent routing.

### Gate-Spring Ownership

Each gate owns specific science domains and pulls only what it needs.
The canonical SSOT is `GATE_SPRING_OWNERSHIP.md`.

| Gate | Domain | Springs | Sync Profile |
|------|--------|---------|-------------|
| **eastGate** | Coordination hub | primalSpring, airSpring, groundSpring | Full superset (38 repos) |
| **ironGate** | Clinical, game science | healthSpring, ludoSpring | Core + health/ludo + esotericWebb |
| **southGate** | Biology, ML inference | wetSpring, neuralSpring | Core + wet/neural |
| **biomeGate** | GPU compute | hotSpring | Core + hotSpring |
| **strandGate** | ABG science, genomics | hotSpring, wetSpring | Core + ABG gardens + lithoSpore |
| **golgiBody** | Periplasmic relay | — | NUCLEUS primals + deployment infra |

### Gate Auto-Detection

`membrane temporal.cascade` resolves the current gate identity:

1. `GATE_NAME` environment variable (explicit override)
2. Hostname detection (`hostname -s` mapped to gate name)
3. Falls back to pulling all repos if unresolved

This makes per-gate sync the default operational mode. Gates pull only
their assigned repos, reducing bandwidth and avoiding conflicts in
repos they don't own.

### Cross-Gate Compute Routing

hotSpring operates on both strandGate (ABG science validation) and
biomeGate (GPU-accelerated physics). The science evolves on strandGate;
heavy compute dispatches to biomeGate via Songbird mesh. This is the
first cross-gate covalent bond — work flows between gates through the
periplasm rather than through manual coordination.

### Covalent Evolution Path

```
Ad-hoc routing (Wave 55-59)
    Handoff blurbs coordinate gate work manually.
    ↓
Documented ownership (Wave 60) — THIS PHASE
    GATE_SPRING_OWNERSHIP.md + manifest [gates.*] profiles.
    cascade-pull --gate auto syncs per-gate repos.
    ↓
Songbird mesh discovery (Wave 62+)
    Gates advertise capabilities via Songbird primitives.
    Cross-gate dispatch replaces manual blurbs.
    ↓
toadStool covalent dispatch (Wave 63+)
    Compute jobs route to best-fit gate hardware.
    hotSpring GPU work auto-dispatches to biomeGate.
    ↓
biomeOS graph.execute (Wave 65+)
    WaterFall becomes a TOML-defined neuralAPI pattern.
    Routing via biomeOS engine instead of shell scripts.
    Parallels RootPulse coordination of primals.
```

### Infrastructure Patterns

- **VPS cascade profile**: golgiBody gets its own cascade-pull profile
  (periplasm-local NUCLEUS repos only — no springs)
- **New gate bootstrap**: Clone from Forgejo, install cascade-pull timer,
  done — K-Derm endosymbiosis (Phase 1 weak → Phase 4 covalent)
- **Nested diderm**: A lab's outer membrane is the campus periplasm;
  WaterFall flows through each envelope independently
- **neuralAPI elevation**: WaterFall becomes a TOML-defined neuralAPI
  pattern in biomeOS, routing via the biomeOS engine instead of shell
  scripts — just as RootPulse coordinates rhizoCrypt + loamSpine +
  NestGate + sweetGrass

## Key Files

| File | Role |
|------|------|
| `infra/wateringHole/ecosystem_manifest.toml` | Repo catalog + `[sync]` config |
| `cellMembrane/crates/membrane-shadow/src/temporal.rs` | Rust WaterFall engine (`membrane temporal.cascade`) |
| `cellMembrane/crates/membrane-shadow/src/relay.rs` | K-Derm relay chain (`relay.run`, `relay.mediate`, `relay.ship`) |
| `infra/wateringHole/freshness.toml` | Wave state snapshot |
| `gardens/projectNUCLEUS/deploy/forgejo_mirror.sh` | Forgejo repo provisioning |
| `springs/primalSpring/ecoPrimal/.../s_ecosystem_freshness.rs` | Manifest + sync validation |

## History

- **Wave 66** (2026-06-01): wateringHole at zero code. All bash scripts
  fossilized. `membrane temporal.cascade` fully Rust, manifest-driven.
  K-Derm relay chain evolved to `relay.rs` (relay.run/mediate/ship).
  S1 TLS shadow PASSED (13 days). MESH_DEPLOYMENT_STANDARD.md added.
- **Wave 63+** (2026-05-31): Phase 4 inversion LIVE. `push_target = "forgejo"`
  in manifest. K-Derm diderm relay chain wired: golgi-post-receive-relay on
  golgiBody triggers pepti-sync-relay on peptidoglycan, which triggers
  ext-github-push on golgiBody-ext (trans face). `topology.roles` added.
  GitHub SSH write credentials moved exclusively to golgiBody-ext.
  Bonding violation resolved: proper covalent→metallic→ionic→weak degradation.
- **Wave 60** (2026-05-28): Phase 1–2 implemented. Manifest v2.0.0 with
  `[sync]` section and `forgejo_repo` fields. `cascade-pull.sh` evolved
  with `--source` and `--ensure-remotes` (now fossilized — replaced by
  `membrane temporal.cascade`). All eastGate repos configured with
  `forgejo` remote.
