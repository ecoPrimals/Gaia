# Caddy Deploy Protocol

**Status**: ACTIVE — proven on golgiBody ([RELAY_PUBLIC])
**Wave**: 157 | **Date**: Sep 25, 2026
**Scope**: Static site vhost provisioning via membrane CLI
**Transport**: SSH to golgiBody (root@[RELAY_PUBLIC])

---

## Principle

Static site Caddy configuration should be derivable from the `PublishSite` registry — not hand-managed. `caddy.deploy` generates a complete vhost block from registry fields and deploys it atomically to golgiBody with validation and rollback.

## CLI Interface

```
membrane caddy.deploy <site>     # Deploy single site
membrane caddy.deploy --all      # Deploy all registered sites
membrane caddy.deploy <site> --dry-run  # Print block without deploying
```

## Block Template

The generated block includes all necessary directives, in this order:

1. Domain declaration + root + encode gzip
2. SEO handles (sitemap.xml, robots.txt)
3. Evidence routes (if evidence_dir configured):
   - `/evidence/` — Zola HTML landing page (try_files)
   - `/evidence/*` — file_server browse from separate evidence dir
4. SPA fallback (try_files with /index.html fallback)
5. 404 error handler
6. Security headers (inline `header {}` block)

## Security Headers (Required)

Every static site block MUST include:

```
header {
    Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
    X-Content-Type-Options "nosniff"
    X-Frame-Options "DENY"
    Referrer-Policy "strict-origin-when-cross-origin"
    Permissions-Policy "camera=(), microphone=(), geolocation=(), interest-cohort=()"
}
```

## Deploy Protocol (SSH)

1. Backup: `cp /etc/membrane/Caddyfile /etc/membrane/Caddyfile.bak`
2. Block replace: Python regex finds `{host} {` ... matching `}` and replaces entire block, or appends if new
3. Validate: `caddy validate --config /etc/membrane/Caddyfile`
4. Reload: `caddy reload --config /etc/membrane/Caddyfile --force`
5. On validation failure: restore from `.bak` and reload (automatic rollback)

## Evidence Route Ordering

CRITICAL: Caddy `handle` blocks are mutually exclusive and matched in order.

- `handle /evidence/` MUST come BEFORE `handle /evidence/*`
- The bare `/evidence/` path serves Zola's HTML landing page
- The `/evidence/*` paths serve raw files from the evidence depot

This ordering was learned from a production incident (Wave 157) where the file browser intercepted the landing page.

## Example: Generated Block (detroit.primals.eco)

Dry-run output from `membrane caddy.deploy detroit --dry-run`:

```
detroit.primals.eco {
    root * /opt/ecoPrimals/detroit/public
    encode gzip

    # Static files first
    handle /sitemap.xml {
        file_server
    }
    handle /robots.txt {
        file_server
    }

    # Evidence landing page — serve the Zola HTML page (not the file browser)
    handle /evidence/ {
        try_files /evidence/index.html
        file_server
    }

    # Evidence depot — separate from Zola build output (survives zola --force)
    handle /evidence/* {
        uri strip_prefix /evidence
        root * /opt/ecoPrimals/detroit/evidence
        file_server browse
    }

    # SPA fallback for Zola pages (must be after handle blocks)
    handle {
        try_files {path} {path}/index.html /index.html
        file_server
    }

    handle_errors {
        @404 expression `{http.error.status_code} == 404`
        rewrite @404 /404.html
        file_server
    }

    header {
        Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "DENY"
        Referrer-Policy "strict-origin-when-cross-origin"
        Permissions-Policy "camera=(), microphone=(), geolocation=(), interest-cohort=()"
    }
}
```

## Source

Function: `generate_static_site_block()` in `cellMembrane/crates/membrane-shadow/src/caddy/mod.rs`
Deploy: `dispatch_caddy_deploy()` in same file
Check: `vhost_exists()` in same file
