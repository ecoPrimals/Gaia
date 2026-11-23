# petalTongue v1.6.7 — Wave 67 flockGate W67/W68 Review

**Date:** June 1, 2026
**Author:** ironGate agent
**Wave:** 67 (glacial cutover)
**Trigger:** flockGate W67/W68 review requests (content_render.rs, VizRegistry pattern, document.rs)

---

## Summary

Reviewed and resolved all flockGate upstream review requests from Wave 67 and Wave 68
handoffs. Three orphaned modules (`content_render`, `viz_data/`, `content_direct`) were
wired into the binary, TRUE PRIMAL violations fixed, document types hardened, and missing
markdown extensions implemented.

---

## Review Responses

### 1. document.rs — Scene Graph Types (W67 Request)

**Q: Are the types complete for the scene graph?**

The types are complete for the Wave 67 content rendering pipeline. The document IR
runs parallel to `SceneGraph`/`SceneNode` (intentional — different compilation paths).
Scene-graph bridging (`DocumentNode::SceneEmbed`) is a future Phase item.

**Actions taken:**
- Added `Inline::Strikethrough(Vec<Inline>)` and `Inline::Image { alt, src, title }`
  (pulldown-cmark enables these but they were silently dropped)
- Added `PartialEq` + `Eq` to all document types (where `toml::Value` allows `Eq`)
- Added `#[serde(default)]` to `PageMeta`, `EntityRegistryEntry`, `SiteContent`
  for safe partial deserialization
- Changed `EntityRegistryEntry` doc from "mirrors sporePrint config" to agnostic wording

**Open items for Phase 2:**
- `DocumentNode::SceneEmbed` bridge to visual scene graph
- `NavTree` canonical model (currently three nav representations exist)
- `SiteContent.pages` should be page-typed, not arbitrary `DocumentNode`

### 2. content_render.rs — pulldown-cmark Patterns (W67 Request)

**Q: Any pulldown-cmark patterns you'd change?**

The stack-based walker is the correct approach for custom AST output. Improvements made:

**Actions taken:**
- Added `Tag::Strikethrough` start/end handlers
- Added `Tag::Image` handler (alt text extracted from events)
- Extended `resolve_shortcodes` to walk `DocumentNode::Table` cells
- **Removed TRUE PRIMAL violation**: Hardcoded `/primals/{key}/` and `/springs/{key}/`
  URL fallbacks in `expand_entity_shortcodes` removed. Entity href now comes from
  registry `page` field only — no ecosystem layout assumptions.
- Fixed module docs: removed sporePrint/NestGate name coupling

**Wiring fix (BLOCKER):**
- `content_render` module was not declared in `main.rs` — dead code. Now wired as
  `mod content_render`.
- `toml` workspace dependency added to root binary crate (was missing).

### 3. VizRegistry Pattern (W68 Request)

**Q: VizRegistry pattern acceptable for other viz-enabled backends?**

**Yes.** The capability-based discovery pattern is well-designed:
- Probes filesystem at startup, exposes only visualizations whose data sources exist
- New visualizations can be added by implementing a builder and registering in `discover()`
- `build_scene()` and `build_animation()` dispatch by slug
- No hardcoded primal names in the registry itself

**Q: viz_data/ module structure — stays in binary or moves to scene crate?**

**Stays in binary for now.** The builders reference ecosystem-specific topology data
(K-Derm layers, NUCLEUS composition levels). The `SceneGraph` output type lives in
the scene crate, but the *builders* that produce domain-specific scenes belong in
the binary (or a future `petal-tongue-viz` crate).

**Wiring fix (BLOCKER):**
- `viz_data/` module was not declared in `main.rs` — dead code. Now wired as `mod viz_data`.
- `content_direct` was not declared in `web_mode/mod.rs` — dead code. Now wired as
  `pub mod content_direct`.

---

## Metrics

| Metric | Value |
|--------|-------|
| Tests passing | 6,208 (was 6,191) |
| Modules wired | 3 (content_render, viz_data, content_direct) |
| TRUE PRIMAL violations fixed | 1 (expand_entity_shortcodes href fallback) |
| Inline variants added | 2 (Strikethrough, Image) |
| Serde attributes added | 3 (#[serde(default)] on PageMeta, EntityRegistryEntry, SiteContent) |
| PartialEq derives added | 10 types |
| Doc coupling references removed | 4 (sporePrint/NestGate in module docs and HTML) |

---

## Remaining Dead-Code Warnings (Expected)

4 warnings from newly-wired modules awaiting router integration:
- `EntityGraph` import unused (viz routes not routed yet)
- `VizEntry` fields unused (viz API not exposed yet)
- `VizRegistry::get` unused (same)
- `ContentDirectState::nav` unused (nav rendering not wired to HTML output)

These resolve when `content-direct` backend mode is added to the web router (Phase 2).

---

## Next Steps

1. **Router integration**: Add `content-direct` backend variant to `web_mode/mod.rs`
2. **Phase 2 DNS cutover**: Caddy → petalTongue:8080 for primals.eco
3. **Scene-graph bridging**: `DocumentNode::SceneEmbed` for inline viz
4. **Nav canonicalization**: Single canonical nav model
5. **wasm-opt investigation**: Disabled due to validation error (W68 open item)
