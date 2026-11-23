# sourDough v0.3.1 — Neural API + Post-Primordial Compliance

**Date**: May 25, 2026
**From**: sourDough team
**To**: primalSpring (downstream audit), all primal teams (scaffold consumers)
**Status**: COMPLETE — pushed to main

---

## What Shipped

### Wave 42/43: Neural API `primal.announce` in Scaffold

Scaffolded primals now auto-announce to biomeOS on startup:

- New `announce.rs` generated in server crate
- Tiered socket discovery: `$NEURAL_API_SOCKET` → `$XDG_RUNTIME_DIR/biomeos/neural-api-{family}.sock` → `/tmp/biomeos/`
- Fire-and-forget: graceful degradation when biomeOS is unavailable
- `primal.announce` classified Public in MethodGate
- Dispatch includes `primal.announce` in METHODS constant
- Inbound handler returns correct v3.68 schema (capabilities as domains, methods as RPC names)

### Wave 44: Announce Handler Fix

- Fixed conflation of capabilities (domain names) with methods (RPC method names)
- `capabilities` field now uses `crate::announce::capabilities()`
- `methods` field uses `METHODS` constant

### Wave 49: Post-Primordial Compliance

- Added `notify-plasmidbin.yml` workflow (was missing)
- Docs updated to plasmidBin-first patterns (no stale `target/release/` in primary paths)
- Scaffolded README template documents plasmidBin as production channel
- Binary paths reference triple-first layout (`primals/<triple>/<name>`)

---

## Verification

| Check | Status |
|-------|--------|
| `notify-plasmidbin.yml` active | YES |
| `notify-sporeprint.yml` active | YES |
| No `showcase/` | Clean (never had) |
| No local `wateringHole/` | Clean (never had) |
| No stale deployment patterns in docs | Fixed |
| Tests | 281 passing |
| Clippy | 0 warnings |
| Cargo.toml version | 0.3.0 (aligned) |

---

## What Teams Using `sourdough scaffold` Get Now

A freshly scaffolded primal includes:

1. `announce.rs` — Neural API startup announce with TODO markers
2. `method_gate.rs` — JH-0/JH-2 pre-dispatch gate
3. `dispatch.rs` — capability wire + `btsp.negotiate` + `primal.announce`
4. `server.rs` — UDS listener + first-byte peek + announce spawn
5. `.github/workflows/` — `ci.yml` + `notify-plasmidbin.yml` + `release.yml`
6. `deny.toml` — ecoBin v3.0 + explicit `ring` ban

Teams should populate `capabilities()`, `signal_tiers()`, `cost_hints()`, and
`latency_estimates()` in `announce.rs` before shipping.

---

## No Open Debt

sourDough has zero open items in primalSpring's tracking. Stadial-current.
