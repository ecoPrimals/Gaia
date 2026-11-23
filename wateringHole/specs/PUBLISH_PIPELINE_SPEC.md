# Publish Pipeline Specification

**Status**: ACTIVE — proven on [detroit.primals.eco](https://detroit.primals.eco), sporePrint.primals.eco
**Wave**: 157 | **Date**: Sep 25, 2026
**Scope**: Webhook-driven static site publication from Forgejo push to live serving
**Predecessor**: Manual bash hooks (10-deploy-*, 50-zola-publish, 20-crawler-notify, 60-seo-resubmit)

---

## Principle

A git push is the only human action required to publish a static site. Everything after the push — build, artifact generation, evidence sync, SEO notification, and consistency verification — is automated by the membrane webhook pipeline. The pipeline is declarative: each site declares its properties in the `PublishSite` registry, and the pipeline derives all behavior from those fields.

## Architecture

```
    ┌─────────────────────────────────────────────────────────────────────┐
    │  TRIGGER                                                            │
    │                                                                     │
    │  git push (Forgejo) ─→ HMAC webhook ─→ membrane UDS ─→ pipeline.rs │
    └──────────────────────────────┬──────────────────────────────────────┘
                                   │
    ┌──────────────────────────────▼──────────────────────────────────────┐
    │  Step 0: Caddy vhost check (idempotent)                             │
    │    vhost_exists(host) — warn + provisioning hint if missing         │
    └──────────────────────────────┬──────────────────────────────────────┘
                                   │
    ┌──────────────────────────────▼──────────────────────────────────────┐
    │  Step 1: Git fetch + reset (worktree on golgiBody)                  │
    │    fetch origin/main → reset --hard HEAD (GIT_DIR unset)            │
    └──────────────────────────────┬──────────────────────────────────────┘
                                   │
    ┌──────────────────────────────▼──────────────────────────────────────┐
    │  Step 2: Zola build (HTML generation)                               │
    │    zola build --force → {public_dir}                                │
    └──────────────────────────────┬──────────────────────────────────────┘
                                   │
    ┌──────────────────────────────▼──────────────────────────────────────┐
    │  Step 2.5: Artifact generation (site-specific build tool)          │
    │    artifact_command subprocess (e.g. detroit-build --root .)        │
    └──────────────────────────────┬──────────────────────────────────────┘
                                   │
    ┌──────────────────────────────▼──────────────────────────────────────┐
    │  Step 3: Evidence push (SCP to golgiBody) + Evidence braid        │
    │    SCP local evidence → golgiBody depot; provenance trio braids   │
    └──────────────────────────────┬──────────────────────────────────────┘
                                   │
    ┌──────────────────────────────▼──────────────────────────────────────┐
    │  Step 4: SEO notify                                                 │
    │    IndexNow + GSC sitemap resubmit + Google URL Indexing API        │
    └──────────────────────────────┬──────────────────────────────────────┘
                                   │
    ┌──────────────────────────────▼──────────────────────────────────────┐
    │  Step 5: Verify consistency                                         │
    │    sitemap.xml <loc> count vs api/site.json total_pages               │
    └─────────────────────────────────────────────────────────────────────┘
```

## PublishSite Registry

The central registry lives in `membrane-shadow/src/seo/mod.rs`. Each site declares:

| Field | Type | Purpose |
|-------|------|---------|
| `repo_name` | `&str` | Forgejo repo name (case-insensitive match) |
| `host` | `&str` | Hostname served by Caddy |
| `worktree` | `&str` | Git worktree path on golgiBody |
| `public_dir` | `&str` | Output directory (Caddy root) |
| `build_subdir` | `Option<&str>` | Zola project subdir (None if root) |
| `seo` | `SiteConfig` | host, sitemap URL, IndexNow key |
| `evidence_dir` | `Option<&str>` | Local evidence depot path |
| `artifact_command` | `Option<&[&str]>` | Post-build artifact generation command |

## Step Details

### Step 0: Caddy Vhost Check

Check if the site's vhost block exists on golgiBody. If missing, log a warning with the provisioning command. Does not auto-provision — use `membrane caddy.deploy <site>` manually.

### Step 1: Git Fetch + Reset

Fetch origin/main and reset the worktree to HEAD. Unsets GIT_DIR to avoid interference from Forgejo's hook environment. Fails the pipeline if the worktree doesn't exist (initial clone must be done manually).

### Step 2: Zola Build

Runs `zola build` in the build subdirectory (or worktree root). Output goes to `{public_dir}`. Uses `--force` to ensure clean rebuild. Returns page count from Zola output.

### Step 2.5: Artifact Generation

If `artifact_command` is set, invokes it as a subprocess in the worktree. For detroit, this is `detroit-build --root .` which generates: graph.json, graph.csv, api/site.json, llms.txt, llms-full.txt, content-manifest.toml. Non-fatal — pipeline continues if artifacts fail.

### Step 3: Evidence Push + Braid

If `evidence_dir` is set, SCP syncs local evidence files to golgiBody. Then, if the provenance trio (rhizoCrypt, loamSpine, sweetGrass) is available via UDS, generates braids for evidence collections. Non-fatal on both counts.

### Step 4: SEO Notify

Triple notification:

1. IndexNow: POST sitemap URLs to Bing/DuckDuckGo/Yandex
2. GSC: Resubmit sitemap URL to Google Search Console
3. URL Notify: POST each URL to Google Indexing API as URL_UPDATED

### Step 5: Verify Consistency

Cross-check sitemap.xml `<loc>` count vs api/site.json `total_pages`. Flag extreme drift (>10× ratio). Check content-manifest.toml exists if site.json exists.

## Adding a New Site

1. Add entry to `PUBLISH_SITES` array in `seo/mod.rs`
2. Create worktree on golgiBody: `git clone --bare` + `git worktree add`
3. Run `membrane caddy.deploy <site>` to provision the vhost
4. Create Forgejo webhook pointing to membrane UDS endpoint
5. Push — the pipeline handles everything else

## Verification Criteria

A site is considered correctly standardized when:

- [ ] All 6 pipeline steps execute on push (check webhook response JSON)
- [ ] All static endpoints return 200 (sitemap.xml, robots.txt, site root)
- [ ] Security headers present: HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy
- [ ] If artifacts configured: site.json, llms.txt accessible
- [ ] If evidence configured: /evidence/ returns 200
- [ ] SEO: site submitted to IndexNow + GSC

## Source Files

| File | Purpose |
|------|---------|
| `cellMembrane/crates/membrane-shadow/src/webhook/pipeline.rs` | Pipeline orchestration |
| `cellMembrane/crates/membrane-shadow/src/webhook/publish_artifacts.rs` | Artifact generation |
| `cellMembrane/crates/membrane-shadow/src/webhook/verify_consistency.rs` | Consistency check |
| `cellMembrane/crates/membrane-shadow/src/seo/mod.rs` | PublishSite registry + SEO dispatch |
| `cellMembrane/crates/membrane-shadow/src/caddy/mod.rs` | Caddy block generation + deploy |
