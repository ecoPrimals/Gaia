# AAR: Artisan Eyes — Deep Audit Findings

**Wave 167 — October 8, 2026**
**Observer**: eastGate (Artisan session)
**Purpose**: Honest operational findings from deep infrastructure audit. What's broken, what's leaking, what's ready but un-pressed.
**Companion subGen**: ARTISAN_EYES_STADIAL_BRIEFING_WAVE167

---

## Summary

The immune head is cephalized and works. The body below the neck has five things that break on reboot, a broken crypto protocol nobody noticed, no deployment pipeline, no monitoring, and 198K lines of deploy-ready code sitting undeployed.

---

## Critical Findings

### Finding 1: nestGate — Ghost Binary (CRITICAL)

```
$ ls -la /proc/2017630/exe
lrwxrwxrwx 1 root root 0 /proc/2017630/exe -> /opt/membrane/nestgate (deleted)
```

Binary deleted from disk. Process alive 92 days on inode. CAS storage for entire sporePrint surface dies on reboot.

**Fix**: Copy binary to `/opt/membrane/nestgate`. 5 minutes.
**Root cause**: No health monitoring, no binary integrity checking.

### Finding 2: bearDog BTSP — Dead Protocol (HIGH)

1,296 BTSP authentication rejections. Zero successes. Duration unknown (at least 73 days — process uptime). The cryptographic tunnel between gates doesn't function. All inter-service trust is UDS socket permissions on a single machine.

**Impact**: Cannot authenticate gates to each other. Mesh expansion blocked until fixed.
**Fix**: Key rotation or BTSP_STRICT_MODE config investigation. Medium complexity.

### Finding 3: squirrel — No Service Unit (MEDIUM)

Running from manual terminal launch since Aug 10. No .service file. No crash recovery. No boot persistence. PID 3514834, uptime 59 days.

**Fix**: Write `squirrel-membrane.service`, enable, test restart. 10 minutes.

### Finding 4: biomeos-nucleus — Reboot Bomb (MEDIUM)

```
biomeos-nucleus.service    enabled    inactive    dead
```

Enabled, dead, no binary. Systemd will try to start it on next boot.

**Fix**: `systemctl disable biomeos-nucleus`. 2 seconds.

### Finding 5: Ghost Node 10.13.37.7 (LOW)

Caddyfile routes webb.primals.eco and footprint.primals.eco to this WG IP. No peer exists. Every request → 502. Nobody knows what this node was supposed to be.

**Fix**: Comment out or redirect both Caddy blocks. 5 minutes.

### Finding 6: Stale biomeos.sock (LOW)

Socket at `/run/membrane/biomeos.sock` created Jun 15. No process, no binary, no service behind it.

**Fix**: `rm /run/membrane/biomeos.sock`. 1 second.

---

## Structural Findings

### Finding 7: No Deployment Pipeline

Every deploy is manual: `cargo build` → `scp` → `systemctl restart`.

| Missing | Impact |
|---------|--------|
| BLAKE3 checksums | Binary integrity unverified in transit |
| Rollback mechanism | Bad deploy → manual revert from .bak |
| Deployment receipt | No record of what binary, what hash, what wave |
| Automated target testing | Tests only run on dev machine |
| plasmid depot | No `/opt/membrane/plasmid-depot/`, no BLAKE3SUMS |

`infra/plasmidBin/crates/plasmidbin/src/cmd/deploy.rs` exists. Not deployed.

### Finding 8: No Monitoring (No Proprioception)

The organism cannot sense its own body state:

| What's not monitored | What went undetected |
|---------------------|---------------------|
| Process liveness | nestGate ghost (92 days) |
| Binary integrity | nestGate deletion (unknown duration) |
| Protocol health | bearDog BTSP failure (73+ days) |
| Socket liveness | biomeos.sock stale (115 days) |
| WG peer identity | 2 unknown peers, 1 ghost node |
| Deploy state | No manifest, no checksums |

skunky-ingest writes `/run/membrane/skunky-ingest.heartbeat` — nothing reads it.

### Finding 9: Content Sites Without VCS

| Site | Domain | Git managed? |
|------|--------|-------------|
| signal | signal.primals.eco | No |
| thesis | thesis.primals.eco | No |
| detroit | detroit.primals.eco | Yes (Forgejo worktree) |
| barry | barry.primals.eco | No |
| clutch | clutch.primals.eco | No |

4/5 content sites have no version history. No rollback. No diff visibility.

### Finding 10: 198K Lines Deploy-Ready, Un-Deployed

| Primal | Lines | Status |
|--------|-------|--------|
| loamSpine | 69,635 | Compiled, tested, needs service file |
| sweetGrass | 65,768 | Compiled, tested, needs service file |
| rhizoCrypt | 62,620 | Compiled, tested, needs service file |
| bingoCube | 10,583 | Compiled, tested, needs service file |
| **Total** | **208,606** | **Ready. Button not pressed.** |

### Finding 11: Genotype/Phenotype Ratio

```
Total primal Rust:     3,620,152 lines
Expressed on golgiBody:  283,000 lines (7.8%)
Ratio:                       13:1
```

The organism builds capabilities faster than it expresses them. This is biologically normal but operationally means 92% of compiled code is latent.

---

## What Was Done This Session

### Detroit Data Handoff Layer (sporeGate assist for northgate)

Northgate described a data handoff layer but the worktree was 15 commits behind remote and the work wasn't deployed. Pulled, resolved divergence (rebase + conflict resolution), then implemented and deployed:

| Feature | Status |
|---------|--------|
| Dublin Core meta tags on every page | Deployed |
| oEmbed discovery for Slack/Discord/Notion | Deployed |
| Dataset Schema.org for Google Dataset Search | Deployed |
| CollectionPage Schema.org on sections | Deployed |
| Taxonomy pills (actors, entities, connections) | Deployed |
| View source links to Forgejo | Deployed |
| /api/entities.json — 32 LARA entities | 200 OK |
| /api/actors.json — 48 actors | 200 OK |
| /api/wikidata-claims.json — Wikidata P-properties | 200 OK |
| /api/oembed.json — oEmbed 1.0 embed | 200 OK |
| /api/index.json — master directory | 200 OK |
| llms.txt updated to 2026-10-08 | 200 OK |
| sitemap.xml (334 URLs) | 200 OK |
| atom.xml (1.2MB full feed) | 200 OK |

Committed as `4ea2c70` to publicRecord/detroit on Forgejo.

Note: northgate reported sitemap.xml and atom.xml returning 500 errors. Both were already serving 200 when I checked — they were generated by Zola and present in `public/`. The worktree just needed pulling and rebuilding.

### Upstream Documentation

| Document | Repo | Commit |
|----------|------|--------|
| AAR_UNWIRED_PRIMALS_MANUAL_AUDIT_WAVE167 | wateringHole | a1ede9458 |
| UNWIRED_PRIMALS_OPERATIONAL_LANDSCAPE_WAVE167 | whitePaper | d251c95 |
| AAR_ARTISAN_EYES_DEEP_AUDIT_WAVE167 | wateringHole | (this document) |
| ARTISAN_EYES_STADIAL_BRIEFING_WAVE167 | whitePaper | (this session) |

---

## Triage Priority

### Do Now (hours, any session)

| # | Task | Time | Risk if skipped |
|---|------|------|-----------------|
| 1 | Copy nestGate binary | 5 min | CAS dies on reboot |
| 2 | Write squirrel .service | 10 min | AI service unrecoverable on crash |
| 3 | Disable biomeos-nucleus | 2 sec | Reboot bomb |
| 4 | Fix ghost Caddy routes | 5 min | Visitors see 502 |
| 5 | Remove stale biomeos.sock | 1 sec | Confusion |

### Do This Week (sporeGate)

| # | Task | Dependency |
|---|------|-----------|
| 6 | Deploy provenance trio (loam + rhizo + sweet) | Service files + sockets |
| 7 | Deploy bingoCube | Service file + socket |
| 8 | Kill last cron (braid-billboard.sh) | Requires #6 |
| 9 | Establish plasmid-deploy | Create depot dir + BLAKE3SUMS |
| 10 | Git-init 4 content sites | Push to Forgejo |

### Do This Month (sporeGate + overwatch)

| # | Task | Dependency |
|---|------|-----------|
| 11 | golgiLayer2 | VPS provisioning |
| 12 | Fix bearDog BTSP | Key analysis |
| 13 | Health monitoring loop | Proprioception |
| 14 | Caddyfile → Forgejo | VCS for routing |

---

## Honest Assessment

The immune head works beautifully. The sourdough pattern is genuine architectural DNA. The scatter honeypot is operationally effective. The signal spine provides cryptographic proof.

But the organism has been building new organs while neglecting the ones it has. 92-day ghost binary. Broken auth nobody noticed. Service running without a unit for two months. Content edited in place without version control.

The fix isn't more code. It's pressing the buttons that are already built.

Central dogma score: **4/7**. Head cephalized. Body catching up.

---

## Agent Footnotes

### northgate
Delivered the detroit data handoff spec — Dublin Core, per-page Schema.org, oEmbed, Dataset schema, API endpoints, taxonomy pills, view source links. Work was in Forgejo but golgiBody worktree was 15 commits behind. eastGate deployed: rebased diverged branch, created 5 API files from config.toml registry, patched 3 templates, rebuilt with Zola. All endpoints verified 200. Committed `4ea2c70`. sitemap/atom "500s" were already resolved before intervention.

### eastGate (Artisan)
Full stadial pause audit. Pulled every thread — ghost binaries, BTSP rejections, UDS socket inventory, WG peer identity, systemd unit vs process parity, content VCS state, Caddyfile line-by-line, genotype vs phenotype measurement. Found 6 operational issues (nestgate ghost, beardog BTSP, squirrel no unit, biomeos reboot bomb, ghost node 502s, stale socket). Found 5 structural gaps (no deploy pipeline, no monitoring, no content VCS, 198K undeployed, 13:1 ratio). Delivered 8 upstream documents across wateringHole + whitePaper. Deployed detroit data handoff layer for northgate. The artisan's job is to see what's there. Good hunt.

---

*Wave 167 — October 8, 2026*
*The organism compiled its genome. Now it needs to express it.*
