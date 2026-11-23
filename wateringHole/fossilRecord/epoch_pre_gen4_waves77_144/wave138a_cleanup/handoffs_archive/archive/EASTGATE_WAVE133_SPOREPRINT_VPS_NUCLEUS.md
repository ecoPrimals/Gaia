# eastGate Handoff — Wave 133: sporePrint VPS NUCLEUS Deployment

**Date**: Jul 6, 2026
**Gate**: eastGate
**Primal**: sporePrint + petalTongue + NestGate + songBird + bearDog
**From**: eastGate overwatch
**Type**: Cross-gate deployment — sovereign site hosting
**AAR**: `SPOREPRINT_SOVEREIGN_DEPLOY_AAR_133a.md`

---

## Objective

Deploy a minimal NUCLEUS composition on the VPS (golgi) to serve `primals.eco`
as a sovereign, CAS-backed, live-visualization-enabled website. This replaces
Caddy file_server + GitHub Pages with petalTongue content rendering, NestGate
CAS storage, and bearDog TLS termination.

---

## Current State

| Component | State | Location |
|-----------|-------|----------|
| `primals.eco` DNS | Points to GitHub Pages | GitHub |
| Caddy file_server | Serving stale `public/` from last manual build | golgi VPS |
| petalTongue | Running on eastGate (363 tests, mesh.peers wired) | eastGate |
| NestGate | Running on eastGate + sporeGate | Not on golgi |
| songBird | Running on eastGate + sporeGate + ironGate | Not on golgi |
| bearDog | Running on flockGate (ACME panics — CryptoProvider P1) | Not on golgi |
| sporePrint content | 226 pages, 2 static SVG diagrams, viz_embed with static fallback | Git repo |
| `spore-validate cas-push` | Implemented, tested | sporePrint crate |
| `cas-register` | NOT implemented | Blocks CAS serving |

---

## Architecture

```
Browser → primals.eco
    → DNS → golgi VPS IP (after NS cutover)
    → bearDog :443 (ACME TLS for primals.eco)
        → petalTongue :8080 (content rendering + viz)
            ├── static pages → NestGate CAS (content.get by hash)
            ├── /api/mesh-live → songBird mesh.peers (live topology)
            ├── /viz/gate-mesh → SVG render from LiveMeshState
            ├── /viz/entity-graph → SVG render from entity-graph.json
            └── /viz/* → SceneGraph → SvgCompiler
```

**Fallback**: if petalTongue or NestGate are unavailable, bearDog can serve
static files from `public/` as a degraded mode (Caddy replacement).

---

## Work Items

### 1. Deploy binaries to golgi (sporeGate CI team)

Binaries already exist in depot (Wave 133a — 30/30 ecobins):

```bash
# On golgi — pull from depot
for bin in petaltongue nestgate songbird beardog; do
  curl -o /usr/local/bin/$bin \
    https://membrane.primals.eco/depot/x86_64-unknown-linux-musl/$bin
  chmod +x /usr/local/bin/$bin
done
```

Total: ~70 MB (petalTongue 28M + songBird 23M + bearDog 11M + NestGate 8M).

### 2. Configure petalTongue for sporePrint (eastGate)

petalTongue needs to know where sporePrint content lives:

```toml
# /etc/petaltongue/config.toml
[content]
root = "/opt/ecoPrimals/sporePrint"
content_dir = "content"
entity_graph = "static/graph/entity-graph.json"

[web]
bind = "127.0.0.1:8080"
enable_api = true
enable_viz = true
```

Key endpoints:
- `GET /` → rendered landing page
- `GET /architecture/mesh-topology/` → rendered page with live SVG
- `GET /api/mesh-live` → JSON mesh peer state from songBird
- `GET /viz/gate-mesh` → SVG render (live if songBird available, static fallback)

### 3. Populate NestGate CAS (sporePrint CI)

After each `zola build`:

```bash
spore-validate cas-manifest --emit
spore-validate cas-push --generate
```

This stores all built pages in NestGate's CAS. petalTongue can then
serve content by BLAKE3 hash with integrity verification on every request.

### 4. Deploy songBird (golgi team)

songBird on golgi needs to mesh with existing peers:

```toml
# /etc/songbird/config.toml
[mesh]
node_id = "golgi"
bootstrap_peers = ["10.13.37.2:7700"]  # sporeGate WG
bind = "0.0.0.0:7700"
```

This enables live `mesh.peers` data for the topology visualization and
routes `capability.call` through the VPS.

### 5. Deploy bearDog with ACME (after flockGate P1 fix)

**Blocked on:** bearDog CryptoProvider fix (Wave 132f P1).

Once fixed:

```bash
beardog server --gateway \
  --domain primals.eco \
  --upstream 127.0.0.1:8080 \
  --acme-email acme@primals.eco
```

bearDog handles:
- ACME cert issuance for `primals.eco`
- TLS termination on :443
- Upstream proxy to petalTongue :8080

### 6. DNS NS cutover (eastGate overwatch — manual)

After bearDog ACME validates on golgi:

1. Change `primals.eco` NS records at registrar → golgi VPS IP
2. Wait for DNS propagation (TTL)
3. Verify: `curl -I https://primals.eco` returns bearDog headers
4. Begin 7-day shadow period (monitor for issues)

### 7. Post-cutover cleanup

After 7-day shadow:

1. Archive `.github/workflows/deploy.yml` to fossilRecord
2. Remove dual-push requirement (Forgejo-only)
3. Update `specs/CONTEXT.md` — mark DNS cutover as complete
4. GitHub Pages becomes read-only archive

---

## Acceptance Criteria

1. `curl https://primals.eco` returns 200 from bearDog on golgi (not GitHub)
2. `/architecture/mesh-topology/` renders live SVG with real peer latencies
3. `/viz/entity-graph` renders 66-node entity graph as SVG
4. `spore-validate depot-verify` passes for all deployed binaries
5. Forgejo-only push flow works (no GitHub push needed)
6. Certification manifest verifiable at serve time

---

## Disk Budget (golgi — 10GB VPS)

| Item | Size | Notes |
|------|------|-------|
| OS + packages | ~3 GB | Ubuntu minimal |
| Shallow repo clones (17) | ~1.5 GB | `--depth 1` per Sovereign CI AAR |
| NUCLEUS binaries (4) | ~70 MB | petalTongue, NestGate, songBird, bearDog |
| sporePrint `public/` | ~5 MB | Zola build output |
| NestGate CAS store | ~50 MB | Content-addressed, dedup across builds |
| Logs + journals | ~200 MB | Managed with vacuum |
| **Total** | ~5 GB | Leaves ~5 GB headroom |

Feasible on the current 10GB VPS. Shallow clones (per Sovereign CI AAR
recommendation) are critical — full clones would fill the disk.

---

## Dependencies

| Dependency | Owner | Status |
|------------|-------|--------|
| bearDog CryptoProvider fix | flockGate | **P1 BLOCKED** |
| `cas-register` implementation | NestGate team | Not started |
| DNS registrar access | eastGate overwatch | Manual action |
| golgi disk management | golgi/cellMembrane | Sovereign CI AAR applied |

---

## Gate Assignments

| Work | Gate | Team |
|------|------|------|
| Binary deployment to golgi | sporeGate | Sovereign CI / cellMembrane |
| petalTongue config + content wiring | eastGate | petalTongue team |
| NestGate CAS population | eastGate | sporePrint team |
| songBird mesh enrollment on golgi | sporeGate | cellMembrane |
| bearDog ACME on golgi | flockGate → sporeGate | bearDog team |
| DNS NS cutover | eastGate | overwatch (manual) |
| Post-cutover cleanup | eastGate | sporePrint team |

---

*The site is built. The content is live (on GitHub). The path to sovereignty
is 4 binaries on a VPS and a DNS change. The mesh is ready to serve.*
