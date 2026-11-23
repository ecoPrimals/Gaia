# AAR: Unwired Primals & Manual Process Audit

**Wave 167 — October 8, 2026**
**Observer**: eastGate
**Purpose**: Inventory every primal not fully wired, every manual process that needs automation, and the organizational model for closing the gaps.
**Companion subGen**: UNWIRED_PRIMALS_OPERATIONAL_LANDSCAPE_WAVE167

---

## Context

After cephalization (skunky-ingest absorbing 2,096 lines of Python, creating the immune head), we did a full stadial pause survey. This AAR documents the specific operational gaps — not the vision (that's in the subGen) but the concrete state of each primal, each manual process, and the exact handoff boundaries between teams, overwatch, and sporeGate.

---

## Finding 1: Primal Deployment Census

### 5 Active (of 16)

| Primal | Lines | golgiBody Service | Health |
|--------|-------|-------------------|--------|
| skunky-ingest (skunkBat) | 48K | skunky-ingest.service | Healthy — fully cephalized immune head |
| songBird | 477K | songbird-membrane.service | Active — 42 error/hr from sporeGate protocol mismatch |
| swarmVine | 7.5K | swarmvine-membrane.service | Active — gossip working but only 1 peer |
| petalTongue | 227K | membrane-petaltongue.service | Stable — running 57 days |
| squirrel | 188K | **NONE** | Running 59 days from manual launch |

Also running but not a primal: Caddy (TLS), Forgejo (git), step-ca (certificates), membrane-webhook (CI-EVO-01).

### 3 Degraded

| Primal | Issue | Fix |
|--------|-------|-----|
| nestGate (414K lines) | Binary deleted from disk. Process running from ghost inode since Jul 8 (92 days). Dies on reboot. | Copy binary → /opt/membrane/nestgate. 5 minutes. |
| bearDog (540K lines) | BTSP network tunnel broken — 1,296 rejections, 0 successes. UDS sockets work for local crypto. | Key rotation or BTSP_STRICT_MODE config fix. |
| squirrel (188K lines) | No .service file. Running from manual launch Aug 10. No crash recovery, no boot persistence. | Write squirrel-membrane.service. 10 minutes. |

### 4 Deployable Now (not deployed)

| Primal | Lines | Role | What's Needed |
|--------|-------|------|---------------|
| loamSpine | 70K | Provenance chain ledger | Service file + socket |
| sweetGrass | 66K | Braid archival (replaces last cron) | Service file + socket |
| rhizoCrypt | 63K | Cryptographic provenance | Service file + socket |
| bingoCube | 11K | Entropy/randomness | Service file + socket |

### 4 Needs Mesh or Hardware

| Primal | Lines | Blocker |
|--------|-------|---------|
| coralReef | 158K | Needs multi-gate coordination (golgiLayer2+) |
| biomeOS | 312K | Needs multiple gates to orchestrate |
| barraCuda | 296K | Needs GPU/dedicated hardware |
| toadStool | 719K | Needs GPU/CUDA/Akida hardware |

### 1 Library (not standalone)

| Primal | Lines | Role |
|--------|-------|------|
| sourDough | 24K | State persistence dependency, not a service |

### Expression Ratio

- **7.8%** of 3.6M primal lines expressed on golgiBody
- **13.6%** immediately achievable (deploy Tier C)
- **95.3%** dormant genotype waiting for mesh/hardware

---

## Finding 2: Manual Process Inventory

### Process 1: Binary Deployment

**Frequency**: Every deploy (roughly daily during active development)
**Current**: `cargo build` → `scp` → `systemctl restart`
**Missing**: BLAKE3 checksums, rollback, deployment receipt, automated target-side testing, plasmid depot
**Risk**: Binary could be corrupted in transit, wrong binary deployed, no record of what runs
**Evolution**: plasmid-deploy pipeline (code exists in infra/plasmidBin, not deployed)

### Process 2: Content Site Updates

**Frequency**: Several times per week
**Current**: SSH to golgiBody, hand-edit Hugo template/content, hope for the best
**Sites affected**: signal, thesis, detroit, barry, clutch (5 Hugo sites, 0 under VCS)
**Missing**: Git history, diff visibility, rollback, review, CI/CD build
**Risk**: No undo, no history, no peer review
**Evolution**: Git-init sites → Forgejo repos → membrane-webhook auto-build

### Process 3: Caddyfile Routing

**Frequency**: Every domain/route change
**Current**: Hand-edit /etc/membrane/Caddyfile (1,223 lines), 30 backup copies on disk
**Automated portion**: FLEET_PRESSURE block only (skunky-ingest)
**Missing**: Version control, diff visibility, backup rotation
**Risk**: Bad edit = 30 domains and 22 route blocks down simultaneously
**Evolution**: Caddyfile in Forgejo, auto-deploy on push

### Process 4: Monitoring and Health

**Frequency**: Never automated — we SSH in and look
**Current**: Discovered nestgate ghost binary after 92 days
**Missing**: Process liveness checks, binary integrity (BLAKE3), socket health, WG peer monitoring, alerting
**What exists but isn't read**: skunky-ingest heartbeat file at /run/membrane/skunky-ingest.heartbeat
**Evolution**: Health watcher → swarmVine gossip alert → songBird federation broadcast

### Process 5: WireGuard Peer Management

**Frequency**: Every node addition
**Current**: Hand-edit wg0.conf, manually distribute keys
**Known issues**: 2 peers with unknown identity, ghost node 10.13.37.7 in Caddyfile (502 errors)
**Evolution**: biomeOS gate.provision or songBird peer bootstrap

### Process 6: Billboard Content

**Frequency**: Whenever the operator writes
**Status**: INTENTIONALLY MANUAL — this is the human voice
**Automation target**: Replace braid-billboard.sh cron with sweetGrass native braiding (file watch → socket). Content stays human-written.

---

## Finding 3: Stale Artifacts

### Ghost processes
- **nestGate**: PID 2017630, binary deleted from disk, `/proc/2017630/exe → /opt/membrane/nestgate (deleted)`

### Stale sockets
- **biomeos.sock**: Created Jun 15, no process, no binary, no service

### Stale service files (19 total)
- 11 disabled + inactive (safe to rm)
- 1 enabled + inactive with no binary (biomeos-nucleus — reboot bomb)
- 7 disabled (low risk clutter)

### Ghost Caddy routes
- webb.primals.eco → 10.13.37.7:3002 (no WG peer exists, returns 502)
- footprint.primals.eco → 10.13.37.7:8090 (same ghost node, returns 502)

### Python fossils
- `/opt/membrane/__pycache__/epitope_bridge.cpython-311.pyc` (last Python artifact)

---

## Finding 4: Organizational Model

### The Three-Layer Pattern

```
TEAMS ──────────── build primals, submit PRs to Forgejo
                   work at crate level
                   don't need to know about infrastructure

OVERWATCH ──────── detect readiness, coordinate evolution
(eastGate)         stadial assessments, AARs, subGens
                   deployment decisions, integration testing
                   wave management

SPOREGATE ──────── handle mesh and membrane
                   WireGuard peers, Caddy routing, VPS provisioning
                   binary depot, certificate management
                   deployment execution (plasmid-deploy)
```

### Handoff Artifacts

| From → To | Artifact | Medium |
|-----------|----------|--------|
| Team → Overwatch | PR merged | Forgejo |
| Overwatch → sporeGate | Deploy directive | wateringHole impulse |
| sporeGate → Overwatch | Deployment receipt | loamSpine entry (when deployed) |
| Overwatch → Teams | Triage/priorities | wateringHole AAR |
| sporeGate → Teams | Infrastructure state | wateringHole topology |

### What This Means Concretely

- **Teams** can update loamSpine, rhizoCrypt, sweetGrass code independently right now
- **Overwatch** decides deployment order and timing (this document IS that decision)
- **sporeGate** executes: provisions plasmid-deploy, writes service files, manages sockets
- Nobody needs to do all three — the handoff protocol prevents context collapse

---

## Triage: Execution Sequence

### Phase 0 — Immediate Triage (Overwatch, hours)

| # | Task | Time | Risk if skipped |
|---|------|------|-----------------|
| 1 | Copy nestGate binary → /opt/membrane/nestgate | 5 min | CAS storage dies on reboot |
| 2 | Write squirrel-membrane.service, enable | 10 min | No crash recovery for 59 days |
| 3 | `systemctl disable biomeos-nucleus` | 2 min | Reboot bomb |
| 4 | Comment out 10.13.37.7 routes in Caddyfile | 5 min | 502 errors for visitors |
| 5 | Remove stale biomeos.sock | 1 min | Confusion |

### Phase 1 — Provenance Trio (sporeGate, days)

| # | Task | Dependency |
|---|------|-----------|
| 6 | Deploy loamSpine on golgiBody | Service file + /run/membrane/loamspine.sock |
| 7 | Deploy rhizoCrypt on golgiBody | Service file + /run/membrane/rhizocrypt.sock |
| 8 | Deploy sweetGrass on golgiBody | Service file + /run/membrane/sweetgrass.sock |
| 9 | Deploy bingoCube on golgiBody | Service file + /run/membrane/bingocube.sock |
| 10 | Wire skunky-ingest → loamSpine + rhizoCrypt + sweetGrass sockets | Phases 6-8 |
| 11 | Kill braid-billboard.sh cron (replaced by sweetGrass) | Phase 8 |

### Phase 2 — Deployment Pipeline (sporeGate, days)

| # | Task | Dependency |
|---|------|-----------|
| 12 | Create /opt/membrane/plasmid-depot/ | None |
| 13 | Deploy plasmid-deploy tool | Phase 12 |
| 14 | BLAKE3SUMS manifest for all binaries | Phase 13 |
| 15 | Git-init 5 Hugo content sites | None |
| 16 | Push content sites to Forgejo | Phase 15 |
| 17 | Wire membrane-webhook auto-build | Phase 16 |
| 18 | Caddyfile → Forgejo repo | None |

### Phase 3 — Mesh Expansion (sporeGate, weeks)

| # | Task | Dependency |
|---|------|-----------|
| 19 | Provision golgiLayer2 (Hetzner CX22) | VPS account |
| 20 | WireGuard peer + golgiBody hub config | Phase 19 |
| 21 | plasmid-deploy golgiLayer2 binaries | Phase 13 + 19 |
| 22 | Fix bearDog BTSP authentication | Key rotation analysis |
| 23 | Health monitoring loop | Phase 6 (loamSpine for alert anchoring) |

### Phase 4 — Body Plan (teams + overwatch, months)

| # | Task | Dependency |
|---|------|-----------|
| 24 | Deploy coralReef | Phase 19 (needs mesh) |
| 25 | Deploy biomeOS | Phase 24 (needs coordination layer) |
| 26 | Procure GPU hardware | Budget decision |
| 27 | Deploy barraCuda | Phase 26 |
| 28 | Deploy toadStool | Phase 26 |
| 29 | golgiLayer3-5 | Geographic distribution plan |

---

## Wire Gap Summary

| What | Current | Target | Owner |
|------|---------|--------|-------|
| Primal expression | 7.8% | 13.6% (then mesh-dependent) | sporeGate deploys |
| Manual deploys | Every time | Zero (plasmid-deploy) | sporeGate builds pipeline |
| Content VCS | 0/5 sites | 5/5 sites under Forgejo | sporeGate + teams |
| Caddyfile VCS | No | Yes (Forgejo) | sporeGate |
| Health monitoring | None | Automated + gossip alert | sporeGate + overwatch design |
| Cron jobs | 1 | 0 (sweetGrass replaces) | Phase 1 |
| Ghost processes | 1 | 0 | Phase 0 |
| Reboot bombs | 1 | 0 | Phase 0 |
| Stale sockets | 1 | 0 | Phase 0 |
| Ghost Caddy routes | 2 | 0 | Phase 0 |

---

## Conclusion

The head is cephalized. The immune pipeline works. What remains is:

1. **Triage** — fix the three things that will break on reboot (hours)
2. **Provenance** — deploy the trio that gives the organism cryptographic memory (days)
3. **Pipeline** — automate the deployment process so sporeGate can move independently (days)
4. **Mesh** — add one node so the gossip/federation protocols have a real peer (weeks)
5. **Body plan** — express the dormant 95% as hardware and mesh grow (months)

Teams build. Overwatch detects. sporeGate wires. The organism evolves.

---

*Wave 167 — October 8, 2026*
*16 primals. 5 active. 3 degraded. 4 deployable. 4 waiting. 6 manual processes. 1 cron job. 0 Python.*
*The inventory is complete. The work is sequential.*
