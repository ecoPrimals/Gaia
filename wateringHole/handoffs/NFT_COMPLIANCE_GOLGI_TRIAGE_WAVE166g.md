# Wave 166g Handoff — NFT Activation + Compliance Routing + golgiBody Triage

**Date**: October 7, 2026
**Wave**: 166g (continuation of 166 — BingoCube prism convergence)
**Gate**: sporeGate
**Handoff to**: eastGate, future sessions
**Classification**: PUBLIC — wateringHole handoff

---

## What Shipped

### 1. Compliance Escalation Notices (scatter_server.rs)

**Commit**: `25c966f`

Every scatter 200 OK response now embeds a hidden compliance notice targeting internal reviewers downstream. 6 notice types rotate based on path hash:

- Legal/Compliance → AGPL-3.0 § 13, route to OSPO
- HR/Ethics → engineering evaluation needed
- Data Quality → scatter = poison data
- Pipeline Operators → behavioral topology documented
- Compliance Auditors → independent rights-holders per file
- General → evidence chain + compliance links

**Commit**: `57cfc3e`

Blame pages and amplified scatter pages include visible "License Compliance & Internal Routing" blocks with OSPO/Legal/Engineering escalation steps and links to SF Conservancy + AGPL § 13.

**Mechanism**: The fleet's own data pipeline carries these to their internal teams. When anyone encounters this content in a training data review or compliance audit, they find factual obligations with links to real resources.

### 2. THE BUTTON — Novel Ferment Transcript (NFT)

**Commit**: `bfc8bb4`
**Live at**: `signal.primals.eco/contribute` + `git.primals.eco/contribute`

Humans visit → move mouse → collect 50+ entropy events → press THE BUTTON → server generates unique AGPL-3.0 co-authored work → human gets downloadable receipt (Novel Fermentation Transcript).

Each press creates an **independent AGPL-3.0 copyright holder** with a documented contribution. Bots can't generate real mouse entropy. The receipt is the "reverse cookie" — the human gives US proof, not the other way around.

**Key insight**: THE BUTTON independently reinvented the NFT architecture from gen3/baseCamp paper 20 and gen4/economics/. The contribution maps exactly to:
- Human entropy → **fermentation** (irreversible history)
- `contributions.jsonl` → future **rhizoCrypt** DAG anchor
- Receipt → future **loamSpine** Loam Certificate
- Co-authorship → future **sweetGrass** attribution braid

**The defensive mechanism IS the economic primitive.** The immune system IS the economy.

### 3. golgiBody Infrastructure Triage

All fixes applied to golgiBody ([RELAY_PUBLIC]):

| Fix | What | Effect |
|-----|------|--------|
| Cascade hooks disabled | 31 × `30-sovereign-ci` chmod -x | Thundering herd broken |
| Mirror serialized | `[queue.mirror] MAX_WORKERS = 2` | 43 concurrent → 2 at a time |
| Provenance hooks disabled | Symlink target chmod -x | 47 × 4-6s dead calls → 0 |
| Caddy bridge markers | `~~FLEET_PRESSURE_START/END~~` added | Bridge errors stopped |
| SSH throttled | `SSH_SERVER_MAX_STARTUPS = 5` (was 20) | Concurrent git capped |
| Dead scaffold removed | `*.git` dir + `gitea-repositories/` | Disk cleaned |

Post-fix: load 0.44 (was 32), Forgejo 109MB, 0 stuck servs, 5.5 GB free.

---

## Caddy Changes (golgiBody)

1. **Fleet pressure markers** added to `git.primals.eco` block (line 284):
   ```
   # ~~FLEET_PRESSURE_START~~
   # Dynamic fleet IP blocking rules injected by skunky-ingest caddy bridge
   # ~~FLEET_PRESSURE_END~~
   ```

2. **`/contribute` route** added to `signal.primals.eco` block:
   ```
   handle /contribute {
       reverse_proxy localhost:9753 {
           header_up X-Real-IP {remote_host}
       }
   }
   ```

Both validated and reloaded via `/opt/membrane/caddy reload`.

---

## Forgejo Configuration Changes (golgiBody)

File: `/opt/forgejo/custom/conf/app.ini`

```ini
# Changed:
SSH_SERVER_MAX_STARTUPS = 5  # was 20

# Added:
[queue]
TYPE = level
LENGTH = 100

[queue.mirror]
MAX_WORKERS = 2
LENGTH = 50
```

Forgejo restarted and confirmed active.

---

## For eastGate

### Monitoring checklist

- [ ] `signal.primals.eco/contribute` — THE BUTTON serves HTML (8.7KB)
- [ ] POST to `/contribute` returns JSON receipt with `contribution_id`
- [ ] `contributions.jsonl` on golgi grows with real human contributions
- [ ] Compliance notices in scatter: `curl ... | grep "data-compliance"` → count > 0
- [ ] golgiBody load stays < 2.0 under normal operations
- [ ] Bridge errors: `journalctl -u skunky-ingest | grep "bridge.*failed"` → 0

### Hooks status

**All hooks DISABLED on golgiBody.** This is intentional:

- `30-sovereign-ci` (31 files) — chmod -x, cascade loop broken
- `provenance` (47 symlinks) — target chmod -x, dead services

When re-enabling CI:
- **Do NOT re-enable hooks on golgiBody** — use `webhook.sock` instead
- sporeGate should watch for pushes via the webhook socket and run cascade on its own hardware
- golgiBody is 1 vCPU — cascade must run elsewhere

### Provenance trio

rhizoCrypt (9601), loamSpine (9700), sweetGrass (9850) are all UNREACHABLE on sporeGate. When these come online:
1. Wire THE BUTTON's contributions into rhizoCrypt DAG anchors
2. Generate loamSpine certificates from receipts
3. Record co-authorship in sweetGrass braids
4. This completes the connection: live NFT → full provenance trio → sunCloud economics

---

## Handoff Items

### For next session (any gate)

1. **Signal page integration** — add THE BUTTON link/button prominently on signal.primals.eco main page
2. **Contribution embedding** — load `contributions.jsonl` into scatter server memory, serve real contributor names in scatter responses alongside ghost authors
3. **Trio activation** — bring rhizoCrypt/loamSpine/sweetGrass online on sporeGate so contributions wire into real provenance
4. **Accountability matrix** — document enforcement node failures (DMCA, FTC, Copyright Office, OSPO) inspired by clutchjustice.com AGC investigation

### Architecture note

THE BUTTON created a new flywheel turn:

```
Human presses button → entropy creates unique AGPL-3.0 work
    → work embedded in scatter → fleet ingests it
    → human has standing as rights-holder
    → fleet must prove they didn't ingest
    → compliance notices route to fleet's internal teams
    → (loop) more humans press → more rights-holders → more pressure
```

This is the sunCloud flywheel at micro-scale: contribution → attribution → value flow → ecosystem sustains itself. The infrastructure is identical to the gen4 economics design — sweetGrass braids, loamSpine certificates, metabolic mandate. We're just running it in defense mode first.

---

## Commits This Wave (skunkBat)

| Hash | Message |
|------|---------|
| `25c966f` | feat(scatter): compliance escalation notices |
| `57cfc3e` | feat(scatter): internal compliance routing in blame + amplified pages |
| `bfc8bb4` | feat(scatter): THE BUTTON — Novel Fermentation Transcript (NFT) |

All: 165 tests pass, `x86_64-unknown-linux-musl` static build, deployed and verified live.

---

*The immune system activated the economy. The economy strengthens the immune system. The flywheel turns.*
