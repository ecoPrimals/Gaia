# sporePrint Wave 67 — Local Nest Atomic Validation

**Date:** June 1, 2026
**Author:** flockgate (agent-assisted)
**Status:** Complete
**Upstream review:** petalTongue team, eastGate (VPS deployment)

---

## Summary

Implemented full local validation of the pure-primal rendering pipeline against
the Zola reference build. petalTongue now has a `content-direct` backend that
reads raw sporePrint markdown from disk, resolves entity shortcodes, builds
navigation, and renders through the DocumentNode pipeline with multi-modal output.

A 5-phase parity validation script confirms **22/22 structural checks pass**
against Zola output.

## Deliverables

### petalTongue (`primals/petalTongue/`)

| File | Action | Purpose |
|------|--------|---------|
| `src/web_mode/content_direct.rs` | New | Filesystem-direct content backend |
| `src/web_mode/mod.rs` | Modified | Wire `content-direct` as third backend option |
| `src/content_render.rs` | Modified | Added `load_entity_registry()` + `build_nav_tree()` |

### sporePrint (`infra/sporePrint/`)

| File | Action | Purpose |
|------|--------|---------|
| `scripts/validate_parity.sh` | New | 22-check parity validation script |
| `README.md` | Updated | Wave 67 items marked complete |
| `specs/EVOLUTION_QUEUE.md` | Updated | Local nest validation section added |
| `specs/CONTEXT.md` | Updated | Local validation noted in current state |
| `specs/RUST_TOOLING_VISION.md` | Updated | content-direct backend documented |

## Architecture

```
sporePrint content/ + config.toml
    │
    ├──→ petalTongue web --backend content-direct --docroot ./content
    │        ├── load_entity_registry(config.toml) → 66 entities
    │        ├── build_nav_tree(content/) → 11 sections
    │        └── per-request: parse_document() → compile_to_html/description/json
    │
    └──→ zola build → public/ (validation oracle)

validate_parity.sh compares both outputs (22 structural checks)
```

## Validation Results

```
Phase 1: Content Serving .............. 9/9 pass
Phase 2: Entity Shortcode Resolution .. 4/4 pass
Phase 3: Modality Support ............. 3/3 pass
Phase 4: Static Assets ................ 2/2 pass
Phase 5: Structural Comparison ........ 4/4 pass
─────────────────────────────────────────────────
Total:                                  22/22 pass
```

## Upstream Review Requests

### eastGate Team
- Deploy petalTongue binary to VPS with `--backend content-provider --port 8080`
- Caddy reverse proxy: primals.eco → localhost:8080
- The `content-direct` backend is for local validation only; production uses NestGate

### petalTongue Team
- New `content_direct.rs` module is intentionally simple (filesystem only)
- The rendering pipeline is shared with the NestGate-backed `content_backend.rs`
- Entity registry loading from TOML is duplicated between backends by design
  (each backend is self-contained, no shared mutable state)

## Key Metrics

| Metric | Value |
|--------|-------|
| Entity registry entries loaded | 66 |
| Navigation sections discovered | 11 |
| Parity checks passing | 22/22 |
| Modalities supported | 3 (HTML, description, JSON) |
| Release binary size | ~15 MiB |
| Server startup time | <3ms |
| Per-request render time | <30ms (full page) |

## Next Steps (Wave 68+)

- eastGate deploys to VPS (production: NestGate-backed)
- DNS cutover after eastGate confirms live serving
- GitHub Pages archived to fossilRecord
- Provenance trio data system (BLAKE3 content addressing per page)
