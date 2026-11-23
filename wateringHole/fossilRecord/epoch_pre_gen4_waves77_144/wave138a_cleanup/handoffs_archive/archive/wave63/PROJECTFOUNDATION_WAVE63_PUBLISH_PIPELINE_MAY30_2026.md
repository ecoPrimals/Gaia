# projectFOUNDATION — Wave 63 sporePrint Publish Pipeline

**Date**: May 30, 2026
**From**: projectFOUNDATION team
**To**: primalSpring coordination, sporePrint team, lithoSpore team
**Phase**: Wave 63 — sporeGarden product evolution response

---

## Summary

Responding to the Wave 63 sporeGarden Products handoff, projectFOUNDATION
has wired the sporePrint content generation pipeline. Foundation now drives
sporePrint gallery content from lithoSpore's pseudoSpore registry and indexes
domain profiles from springs — replacing ad-hoc auto-merge with structured
ingestion.

---

## What Was Delivered (Phase B+)

### New crate: `foundation-publish`

| Metric | Value |
|--------|------:|
| New Rust lines | 1,075 |
| New tests | 19 |
| Total workspace lines | 7,491 |
| Total tests | 137 |
| Binary size (release, stripped) | 3.2 MB |
| Clippy status | zero warnings (pedantic + nursery) |

### Capabilities

1. **pseudoSpore registry ingestion** (`foundation publish`)
   - Reads lithoSpore `pseudospores/registry.toml`
   - Generates Zola-compatible gallery pages with front matter
   - Generates section index for `/lab/spores/` route
   - Dry-run mode for preview without writes

2. **Domain profile indexing** (`foundation profiles`)
   - Scans spring directories for `domain_profile.toml` files
   - Extracts lightweight header (id, version, tools, capability flags)
   - Outputs JSON index for downstream consumption
   - Verified against healthSpring and wetSpring profiles

3. **Updated sporePrint content** (`sporeprint/validation-summary.md`)
   - Reflects Wave 63 metrics (137 tests, 6 crates, 7.5k lines)
   - Documents both Rust UniBin and bash pipeline paths
   - Includes Forgejo link alongside GitHub

---

## CLI Additions

```
foundation publish --registry <path-to-registry.toml> [--output-dir DIR] [--dry-run]
foundation profiles --scan-dir <spring-dir> --spring <name> [--output <json-path>]
```

---

## Integration Points Wired

| Integration | Status | Detail |
|-------------|--------|--------|
| lithoSpore `registry.toml` reader | **DONE** | Full TOML parser for `[[pseudospore]]` entries |
| Gallery page generator | **DONE** | Generates `{slug}.md` + `_index.md` for sporePrint |
| Domain profile header parser | **DONE** | Reads `[profile]`, capability sections for indexing |
| Directory scanner | **DONE** | Recursive scan with skip rules (`.`, `target`, `node_modules`) |
| sporePrint auto-merge trigger | PENDING | `notify-sporeprint.yml` exists; needs `publish` → trigger wire |
| VPS artifact serving | PENDING | Caddy route for `/lab/spores/` (projectNUCLEUS scope) |

---

## For sporePrint Team

The generated gallery pages are at `sporeprint/spores/`. They follow the
existing auto-merge contract:

- Files in `sporeprint/*.md` → `content/lab/{source}-{basename}`
- New: `sporeprint/spores/*.md` → should map to `content/lab/spores/{slug}.md`
- Front matter uses `template = "page.html"` and `[extra]` with `entity`, `tier`, `spring`
- Section index uses `template = "section.html"` with `sort_by = "date"`

**Ask**: Add a Zola section at `content/lab/spores/` that picks up these
generated pages. The `_index.md` we generate includes the gallery table.

---

## For lithoSpore Team

Foundation reads but does not write `pseudospores/registry.toml`. The contract:

- Foundation expects `[meta]` with `last_updated` and `total_ingested`
- Foundation expects `[[pseudospore]]` entries with `name`, `version`, `origin`, `spring`, `status`, `modules_pass`, `modules_total`
- Optional fields consumed: `domain_profile`, `blake3`, `description`

As new spores are ingested, re-running `foundation publish` regenerates the gallery.

---

## Remaining Wave 63 Work (Foundation Scope)

| Task | Status | Next Step |
|------|--------|-----------|
| sporePrint notify trigger | PENDING | Wire `publish` completion → `repository_dispatch` to sporePrint |
| Multi-spring profile index | DONE locally | Needs CI automation for ecosystem-wide scan |
| Forgejo bidirectional mirror | PENDING | projectNUCLEUS scope per Wave 63 handoff |
| Phase C production parity | IN PROGRESS | NestGate registration, toadStool dispatch next |

---

## Questions for Upstream

1. Should the `/lab/spores/` gallery use `taxonomy_single.html` or a new custom template?
2. Does lithoSpore want `foundation profiles` output as a PR to lithoSpore's `profiles/` index?
3. Should `foundation publish` also generate a `liveSpore.json` for sporePrint's guidestone widget?
