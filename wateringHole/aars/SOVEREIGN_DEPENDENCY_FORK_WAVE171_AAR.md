# AAR: Sovereign Dependency Fork & GitHub Fleet Shift — Wave 171

**Date**: Oct 11, 2026 | **Wave**: 171 | **Scope**: GitHub (ecoPrimals org), Forgejo (golgiBody), sporePrint, all primals
**From**: overwatch/agentic session (sporeGate inner membrane)
**Type**: Sovereignty hardening — dependency forking, fleet traffic shift, selective permeability enforcement

---

## Summary

Two architectural changes in one session:

1. **Selective permeability enforced**: All public-facing links to source code
   now point to `github.com/ecoPrimals` instead of `git.primals.eco`.
   The membrane's scatter layer absorbs fleet traffic; external visitors
   get routed to GitHub where code is actually accessible.

2. **Upstream dependencies forked**: All critical infrastructure we run
   (RustDesk, Caddy, Zola, Forgejo, WireGuard, Giscus) now has a fork
   under `ecoPrimals/` on GitHub. This is the first step toward full
   sovereign dependency management.

**Key insight**: `git.primals.eco` is the scatter membrane — selective
permeability means the fleet sees decoy content, not real code. Public
links pointing there were sending legitimate visitors into the scatter
layer. Fix: all clickable source links → GitHub. Descriptive/architectural
references to `git.primals.eco` as a membrane component stay.

**Secondary insight**: Making the fleet Microsoft's problem. GitHub
serves the bandwidth for AI crawlers (ClaudeBot, GPTBot, Bingbot).
They own the infrastructure. They can handle it.

---

## What Changed

### 1. Public Content — Selective Permeability Fix

18 files across sporePrint, 28 link substitutions:

| File Category | Count | Change |
|---|---|---|
| llms.txt | 1 | Tagline, LaTeX source link, contact |
| Contact/Resume | 2 | Identity links |
| arXiv paper + audit | 2 | LaTeX source, repo references |
| Science papers | 2 | Code references (Papers 31, 32) |
| Architecture docs | 4 | Ecosystem inventory, forge lockdown, scraping notice, membrane visibility |
| Methodology | 2 | Antidote titration, scyborg bulwark |
| Outreach | 2 | Public record, guerillaGorilla |
| Lab | 2 | Gate status, projectFOUNDATION |
| Data | 1 | Data federation schedule |

**Rule**: If a link expects the reader to click through and access code → GitHub.
If a reference describes what `git.primals.eco` IS (scatter layer, membrane component) → keep as-is.

34 descriptive references remain. Zero clickable `https://git.primals.eco` links remain.

**Commits**: `599c6b0c` (initial fix), `93bf4768` (detroit → defendDetroit/publicRecord)

### 2. GitHub Repos — Full Sync

29 public repos on `github.com/ecoPrimals`, all pushed current:

| Category | Repos | Status |
|---|---|---|
| Primals (16) | skunkBat, bearDog, songBird, squirrel, biomeOS, nestGate, toadStool, coralReef, barraCuda, bingoCube, sourDough, rhizoCrypt, sweetGrass, loamSpine, petalTongue, plasmidBin | ✓ All pushed |
| Infra (6) | sporePrint, wateringHole, whitePaper, fossilRecord, signal, hypothesis | ✓ All pushed |
| Springs (1) | primalSpring | ✓ Pushed |
| Gardens (1) | cellMembrane | ✓ Created + pushed |
| Other (2) | projectFOUNDATION, swarmVine | ✓/⚠ (swarmVine blocked on workflow scope) |
| Org meta (3) | .github, benchScale, agentReagents | Existing |

**Repos created this session**: cellMembrane, projectFOUNDATION, primalSpring, signal, hypothesis
**Repos made public**: whitePaper, fossilRecord (were private)

**Separate orgs** (correct separation):
- `defendDetroit/publicRecord` — detroit evidence site
- `amicusContra/tuebor` — tuebor public accountability
- `amicusContra/lansing` — lansing site

### 3. Upstream Dependency Forks

All critical infrastructure we run now has a sovereign fork:

| Upstream | Fork | Purpose | Version We Run |
|---|---|---|---|
| `rustdesk/rustdesk` | `ecoPrimals/rustdesk` | Relay (hbbs/hbbr), outer membrane | hbbs/hbbr binaries |
| `caddyserver/caddy` | `ecoPrimals/caddy` | TLS reverse proxy, Channel 3 surface | Caddy (apt) |
| `getzola/zola` | `ecoPrimals/zola` | Static site generator for sporePrint | zola (binary) |
| `codeberg.org/forgejo` | `ecoPrimals/forgejo` | Sovereign git forge | Forgejo 16.0.5+gitea-1.22.0 |
| `WireGuard/wireguard-tools` | `ecoPrimals/wireguard-tools` | VPN mesh (inner membrane) | wireguard-tools 1.0.20210914 |
| `giscus/giscus` | `ecoPrimals/giscus` | GitHub Discussions commenting (NOT YET WIRED) | Not deployed yet |

**Forgejo note**: Forgejo lives on Codeberg, not GitHub. Mirror created manually
(`git clone --mirror` from Codeberg → push to GitHub). Some tags rejected by
GitHub pre-receive hooks (version-specific protections). Main branch content pushed.

---

## Pending — Not Yet Done

### Giscus Integration

Giscus (GitHub Discussions-based commenting) is forked but NOT wired into sporePrint.
Integration requires:

1. Enable GitHub Discussions on `ecoPrimals/sporePrint` repo
2. Install Giscus GitHub App on the ecoPrimals org
3. Add Giscus `<script>` tag to Zola templates (base.html or per-section)
4. Configure: repo, category, mapping (pathname → discussion title)
5. Style to match sporePrint dark theme

**Architecture decision**: Giscus comments live on GitHub Discussions.
This is intentional — discussion data lives on Microsoft's infrastructure,
not on the membrane. Commensals can participate without accessing the membrane.

### Crates.io Local Mirror

The ecosystem depends on ~220+ unique crates from crates.io. For full sovereignty:

1. Set up a local crate mirror on golgiBody (or a dedicated gate)
2. Configure `.cargo/config.toml` across all gates to use the local mirror
3. Options: `cargo-local-registry`, `panamax` (full mirror), or `cratesio-index` + vendored crates
4. First step: `cargo vendor` in each repo to snapshot current dependencies

**Key crates** (by usage frequency across primals):
tokio, serde/serde_json, tracing, thiserror, anyhow, uuid, chrono, bytes,
rand, toml, sha2, tempfile, base64, reqwest, hyper, axum

### Forgejo Mirrors of Upstream Forks

The GitHub forks should also be mirrored on Forgejo so the membrane has
sovereign copies of everything:

1. Create mirror repos on Forgejo for each fork
2. Set up periodic sync (cron or Forgejo's built-in mirror feature)
3. This gives: Upstream → GitHub fork → Forgejo mirror → local builds

### Future Forks to Consider

| Upstream | Why |
|---|---|
| `prometheus/prometheus` | If we deploy metrics |
| `grafana/grafana` | If we deploy dashboards |
| `meilisearch/meilisearch` | If we add search (already using elasticlunr) |
| `fish-shell/fish-shell` | Shell on gates |
| `neovim/neovim` | Editor on gates |
| `systemd/systemd` | Init system (all gates) |

---

## Topology After This Change

```
EXTERNAL VISITOR
    │
    ├── Reads sporePrint/detroit/tuebor
    │   └── Clicks source link → github.com/ecoPrimals/...
    │       └── GitHub serves the code (Microsoft's bandwidth)
    │           └── AI fleet crawls here (Microsoft's problem)
    │
    ├── Reads llms.txt
    │   └── Sees "github.com/ecoPrimals (source)"
    │       └── Follows to GitHub, not scatter
    │
    └── Hits git.primals.eco directly
        └── Gets scatter layer (selective permeability)
            └── Fleet sees decoy content
                └── Observations feed nautilus

SOVEREIGN BUILD PATH
    │
    ├── ecoPrimals code → Forgejo (origin) → push to GitHub (mirror)
    ├── Upstream deps → GitHub fork → Forgejo mirror → local builds
    └── Crates.io → (future: local mirror) → cargo build
```

---

## Discussion Items (from northgate standup, still open)

| ID | What | Status |
|---|---|---|
| VERSION-SKEW | 3 version ranges (0.1-0.2, 0.4-0.9, 0.14). Harmonization strategy needed. | Open |
| CERT-OWNER | Certificate shows `loamspine`, expected `beardog`. Cosmetic but confusing. | Open |
| PEPTI-TARGETS | Missing depot: `aarch64-linux-android`, `x86_64-unknown-linux-gnu`. | Open |
| SHADER-SUPPORT | `shader.list` / `trust.list` in capability_registry, no impl. Keep or remove? | Open |
| GISCUS | GitHub Discussions commenting not wired into sporePrint. | **New** |
| CRATES-MIRROR | No local crates.io mirror — builds depend on external registry. | **New** |
| FORGEJO-MIRROR | Upstream forks not mirrored to Forgejo yet. | **New** |

---

## Commits This Session

| Repo | Hash | Message |
|---|---|---|
| skunkBat | `6554671` | Vitality reflection: entropy-gated life signal at the mobility edge |
| skunkBat | `75b2a02` | Negentropy: vuln scanners defend others by mapping the attack surface |
| sporePrint | `806ef883` | baseCamp 59 published + renumbered |
| sporePrint | `599c6b0c` | Selective permeability: git links → GitHub in public content |
| sporePrint | `93bf4768` | Fix detroit GitHub links: defendDetroit/publicRecord |
