# flockGate Team — Wave 116 Blurb

**Date**: Jun 18 2026 | **From**: eastGate overwatch
**Context**: flockGate is on sovereign relay (WAN, offsite). You have three roles:
sporePrint content modernization, WAN NUCLEUS enrollment, and K-Derm periplasm validation.

---

## Triple Role

### Role 1: sporePrint Content Team

sporePrint (primals.eco) is a 222-page Zola site with a Rust validation crate (`spore-validate`, 150 tests).
You own content modernization — many pages are stale (written March 2026, never revisited).
Your git pushes also validate the WAN cascade pipeline (flockGate → Forgejo → GitHub).

### Role 2: WAN NUCLEUS Test Node

You are the first gate enrolled that is NOT on the LAN. NUCLEUS 13/13 primals running
across real WAN latency proves the deployment pipeline works without LAN proximity to
sporeGate. If it works on flockGate, it works on any internet-connected machine.

### Role 3: K-Derm Periplasm/Outer Membrane Validator

LAN gates validate the plasma membrane (sporeGate's nftables). You validate everything
outside it — WireGuard overlay, RustDesk relay, golgi/pepti services, cascade pipeline.
You are the only gate that exercises ALL K-Derm layers end-to-end.

```
Layer                  LAN gates test    flockGate tests
─────                  ───────────────   ────────────────
Plasma Membrane        YES (nftables)    NO (bypasses)
Periplasm (WG)         partial (LAN)     YES (real WAN)
Periplasm (relay)      partial (hairpin) YES (real WAN)
Outer Membrane (VPS)   partial (direct)  YES (sole path)
Extracellular (WAN)    NO                YES (lives here)
```

---

## Enrollment Status

| Step | Status | Action |
|------|--------|--------|
| Sovereign relay | ✅ Done | Already on sovereign RustDesk |
| WireGuard peer | ✅ Done | 10.13.37.6 LIVE (32ms to golgi, 72ms to sporeGate) |
| SSH enable | ✅ Done | SSH responding |
| SSH key auth | PENDING | sporeGate overwatch connecting to authorize their key |
| NUCLEUS deploy | PENDING | sporeGate will deploy after SSH key authorized |
| Cascade connect | PENDING | After NUCLEUS |

**sporeGate overwatch is handling SSH key + NUCLEUS deploy for you.** Once done, you
start your Tower work immediately.

## Atomic Role: Tower (BearDog, Songbird, SkunkBat)

You are the **trust layer proving ground**. Tower work is dispatched here because you're
the only gate on real WAN — trust must work at 65ms+ latency, through NAT, over public internet.

| Primal | Work |
|--------|------|
| **BearDog** | Initiate BTSP handshakes over WG to sporeGate + eastGate. Validate latency-tolerant crypto. |
| **Songbird** | Call `mesh.init`. Establish WAN federation with golgi + sporeGate. Test NAT traversal. |
| **SkunkBat** | Configure WAN threat rules. Audit cascade integrity from offsite. Anomaly detection. |

**Why here**: If BTSP works at 65ms over public internet, it works everywhere. You prove
that Tower encryption is robust regardless of network conditions.

**WireGuard topology**: You connect directly to golgi hub (10.13.37.1), not through
sporeGate. This validates the periplasm path that bypasses the plasma membrane entirely.

---

## sporePrint Audit Summary

### Healthy (auto-maintained, don't touch)
- `content/lab/` (133 pages) — auto-merged from springs
- `content/science/` (32 pages) — baseCamp papers, self-updating

### Moderately Stale (fix numbers, update claims)
- `content/architecture/PRIMAL_CATALOG.md` — "Last Updated March 31", test counts stale
- `content/architecture/ECOSYSTEM_INVENTORY.md` — missing repos added since March
- `content/architecture/SOVEREIGN_DEPLOYMENT.md` — no K-Derm, no WireGuard, no multi-gate
- `config.toml` entity registry — metrics measured 2026-04-04, 2.5 months behind

### Stale (March 2026, never revisited)
- `content/technical/MSU_ASSET_ACCELERATION.md` — institution-specific
- `content/technical/GRANT_TECHNICAL_APPENDIX.md` — grant-specific
- `content/technical/HARDWARE_COST_ANALYSIS.md` — no RTX 5090, old pricing
- `content/audience/` (6 pages) — academic pitch, may be outdated
- `content/products/blueFish.md` — "repo pending" since March

### Stubs / Wrong Numbers
- `content/sitemap/_index.md` — says "105 pages" (actual: 222)
- `content/philosophy/` — "coming soon" stub since creation
- `content/glossary/` — missing K-Derm, enrollment, WireGuard, cytoplasm zone terms
- `config.toml` line 44: `last_push = "2026-06-01"` — stale
- `config.toml` line 47: `sovereign_url = "http://137.184.197.151"` — verify IP

### Structural Issues
1. "15 primals" claim used on ~30 pages — audit if still accurate
2. JupyterHub references in lab/_index.md — may not be live
3. ABG ("Accelerated Bioinformatics Group") references — status unclear
4. No public K-Derm or gate enrollment documentation
5. KDERM_DIDERM_ARCHITECTURE.md may be outdated vs gen5 spec

---

## Task Priorities

### P0 — Automated Fixes (run immediately after enrollment)

```bash
# Update entity metrics from source repos
cargo run -- refresh /path/to/all/repos --write

# Check for broken internal links
cargo run -- check-links

# Preview locally
zola serve
```

1. Run `spore-validate refresh` to update config.toml metrics
2. Run `spore-validate check-links` to find broken links
3. Fix `sitemap/_index.md` page count (222, not 105)
4. Update `config.toml` `last_push` to current date
5. Verify `sovereign_url` IP is correct (golgi is [RELAY_PUBLIC], golgiBody-ext may differ)

### P1 — Content Currency (high-value, low-effort)

1. **Glossary refresh**: Add K-Derm, gate enrollment, WireGuard mesh, cytoplasm zone, plasma membrane, periplasm, cascade terms
2. **PRIMAL_CATALOG.md**: Refresh "Last Updated" and test counts from registry after refresh
3. **ECOSYSTEM_INVENTORY.md**: Add repos created since March 31
4. **HARDWARE_COST_ANALYSIS.md**: Add RTX 5090 (northGate), update pricing
5. **SOVEREIGN_DEPLOYMENT.md**: Add K-Derm model, WireGuard overlay, multi-gate enrollment

### P2 — New Content (medium effort, high value)

1. **K-Derm public page**: Public-facing explanation of the multi-membrane topology model and why it matters for sovereignty. Source: `gen5/foundations/KDERM_DIDERM_ENVELOPE.md` + `cellMembrane/specs/K_DERM_TOPOLOGY.md`
2. **Gate enrollment page**: How gates join the sovereign mesh (SSH → preflight → NUCLEUS → WG → cascade). This IS the "reproduce it yourself" story for infrastructure.
3. **Covalent mesh page**: Distributed compute vision — relates to `FOR_HARDWARE_BUILDERS_AND_HOBBYISTS.md`

### P3 — Content Cleanup (evaluate and decide)

1. MSU content: Still relevant? Archive or modernize.
2. ABG/JupyterHub: Live infrastructure? If not, mark as "planned" or remove.
3. Philosophy: Write atlasHugged or remove "coming soon" promise.
4. blueFish: Resolve "repo pending" or mark as conceptual.

---

## Key Infrastructure

| Resource | Access | Notes |
|----------|--------|-------|
| sporePrint repo | `git clone git@github.com:ecoPrimals/sporePrint.git` | Also on Forgejo |
| golgi | ssh root@[RELAY_PUBLIC] (WG: 10.13.37.1) | After key authorized |
| pepti | ssh root@[RELAY_PUBLIC] (WG: 10.13.37.4) | After key authorized |
| Forgejo | https://git.primals.eco | Push target for cascade |
| Sovereign relay config | See wateringHole/compute-sharing/RUSTDESK_CONFIG.md | Already configured |
| primals.eco (live site) | Caddy on golgiBody-ext VPS | Rebuild on push via systemd timer |

---

## What NOT to Touch

- `content/science/` — auto-refreshed by springs pipeline
- `content/lab/` — auto-merged from springs
- Landing page stat cards — they read from `config.toml` (update config, cards follow)
- Template structure (base.html, etc.) — stable, well-tested
- `spore-validate` crate internals — unless fixing bugs discovered during use

---

## What This Proves

When flockGate completes all three roles:
- **sporePrint is current** — the public site reflects the real ecosystem
- **WAN NUCLEUS works** — deployment pipeline is not LAN-dependent
- **K-Derm is proven end-to-end** — every layer validates from extracellular through periplasm
- **Any internet-connected machine can become a gate** — flockGate is the template

This is the pattern for every future WAN gate: a friend's NUC, a colo server, a VPS.
If flockGate can enroll and contribute, anything can.
