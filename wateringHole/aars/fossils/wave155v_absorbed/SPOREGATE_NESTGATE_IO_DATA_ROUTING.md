# sporeGate — nestgate.io Data Routing Handoff

**Date**: Aug 3, 2026 | **Wave**: 155q/156b
**From**: sporePrint team | **To**: sporeGate team (DNS/Caddy)
**Context**: Data Braids section now has 16 domain pages with inline
provenance braids + transplant page. nestgate.io should serve as the
data identity surface.

---

## What sporePrint Built

- `/data/` section: 16 domain pages covering 38+ datasets across 17 domains
- Every dataset has an inline W3C PROV-O JSON-LD braid example
- `/data/transplant/` page explaining pseudoSpore/lithoSpore for PIs
- "Data" is now in the top nav bar (between pseudoSpore and Lab)
- Data catalog updated to 519 GB / 130+ datasets

## What sporeGate Needs to Do

### Option A: Redirect (simplest)

Configure nestgate.io to redirect to sporeprint.primals.eco/data/:

```
# Caddy on golgi
nestgate.io {
    redir https://sporeprint.primals.eco/data/{uri} permanent
}
```

### Option B: Reverse proxy (same content, different domain)

Serve the same sporePrint build under nestgate.io, filtered to
the `/data/` paths:

```
nestgate.io {
    reverse_proxy localhost:8080 {
        header_up Host {upstream_hostport}
    }
    handle /data/* {
        reverse_proxy localhost:8080
    }
    handle / {
        redir /data/ permanent
    }
}
```

### Option C: Subdomain of nestgate.io (future)

Eventually data.nestgate.io or just nestgate.io could serve a
dedicated data catalog site (separate Zola build or the same one).

### DNS

nestgate.io needs an A record pointing to golgi ([RELAY_PUBLIC])
and a TLS certificate (Caddy auto-TLS via Let's Encrypt).

DNSSEC is already configured for nestgate.io.

---

## Why nestgate.io

nestgate.io is the CAS/data identity domain for the ecoPrimals ecosystem.
While primals.eco serves the full sporePrint site, nestgate.io should be
the PI-facing front door for "what data is available and how do I get it."

The Data Braids pages are already built and live at
sporeprint.primals.eco/data/. The routing just needs to connect
nestgate.io to that content.

---

*sporePrint Wave 155q/156b — Data Braids section ready. nestgate.io
routing is the sporeGate team's deliverable.*
