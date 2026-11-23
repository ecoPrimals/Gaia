# Three-Domain Topology Spec

**Date**: Aug 4, 2026 | **Wave**: 155v/156d | **From**: sporeGate (eastGate overwatch)
**Owner**: sporeGate topology team
**Status**: OPERATIONAL — ALL 3 LAYERS SEPARATED. primals.eco LIVE (Zola, Cloudflare), nestgate.io LIVE (petalTongue mesh, sovereign DNS), primal.eco SEALED (0 public A records, dnsmasq-only)

---

## Domain Architecture

The ecoPrimals ecosystem operates across three distinct DNS domains,
each mapped to a K-Derm envelope layer:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          INTERNET (public)                               │
│                                                                          │
│  primals.eco ──────────── OUTER MEMBRANE (Cloudflare DNS)                │
│  ├── sporeprint.primals.eco   Public research site (Zola, 302 pages)     │
│  ├── footprint.primals.eco    GIS composition (→ sporeGate :8090)        │
│  ├── webb.primals.eco         CRPG game garden (→ ironGate :8090)        │
│  ├── live.primals.eco         petalTongue TOPO-VIS (→ sporeGate :8190)   │
│  ├── lab.primals.eco          JupyterHub gateway (→ sporeGate :7780)     │
│  ├── membrane.primals.eco     Depot, hooks, status                       │
│  ├── depot.primals.eco        Binary depot browser                       │
│  ├── ca.primals.eco           SSH CA (step-ca)                           │
│  ├── relay.primals.eco        RustDesk MitoBeacon                        │
│  ├── git.primals.eco          Forgejo (localhost:3000)                    │
│  └── *.primals.eco            Wildcard → golgi ([RELAY_PUBLIC])           │
│                                                                          │
│  nestgate.io ──────────── PEPTIDOGLYCAN (Sovereign Knot DNS + DNSSEC)    │
│  ├── nestgate.io              petalTongue mesh (→ sporeGate :8190)       │
│  ├── www.nestgate.io          → redirect to nestgate.io                  │
│  ├── (future) /cas/           Federated CAS browser                      │
│  ├── (future) /depot/         Binary depot (migration from membrane)     │
│  ├── (future) /provenance/    Provenance chain viewer                    │
│  └── (future) /validate/      Replication validation endpoint            │
│                                                                          │
│  primal.eco ───────────── INNER MEMBRANE (Sovereign Knot DNS, NO A recs) │
│  ├── *.primal.eco             dnsmasq only (10.13.37.0/24 WG mesh)       │
│  ├── UDS/JSON-RPC             Primal-to-primal IPC                       │
│  └── songBird mesh            Federation + drawbridge                    │
└──────────────────────────────────────────────────────────────────────────┘
```

### Domain Responsibilities

| Domain | Envelope | Serves | Served By | DNS | Public A Records |
|--------|----------|--------|-----------|-----|-----------------|
| **primals.eco** | Outer membrane | Public site, publications, lab access | sporePrint (Zola) + Caddy | Cloudflare | golgi `[RELAY_PUBLIC]` + wildcard |
| **nestgate.io** | Peptidoglycan | CAS braids, depot, provenance, validation, git | petalTongue + Forgejo + Caddy | **Sovereign Knot DNS** | golgi `[RELAY_PUBLIC]` |
| **primal.eco** | Inner membrane | Mesh-only gate comms, NUCLEUS IPC | WireGuard + UDS + songBird | **Sovereign Knot DNS** | **NONE** (all removed) |

### Why Three Domains

1. **primals.eco** is the public face — researchers, PIs, anyone can see publications
   and the research catalog. Zola static site, maximum security posture.

2. **nestgate.io** is the validation surface — where CAS data braids are exposed so
   others can validate provenance, replicate datasets, and verify computational results.
   This is NOT the public site; it's the PI/researcher-facing "trust surface" where
   data integrity is proven. Served by **petalTongue** (not Zola), making it a
   validated system that dogfoods the primals.

3. **primal.eco** is the inner mesh — gate-to-gate communication, NUCLEUS IPC,
   songBird federation. Never exposed publicly. WireGuard mesh only.

---

## nestgate.io Evolution Plan

### Current State (LIVE — Aug 4, 2026)

nestgate.io is served by petalTongue v1.7.0 on sporeGate NUCLEUS via WG mesh:
```
nestgate.io → golgi Caddy (TLS termination)
           → WG mesh 10.13.37.1 → 10.13.37.2:8190
           → petalTongue (web + IPC mode) on sporeGate
```

DNS: A record → [RELAY_PUBLIC] (golgi), TLS: Let's Encrypt via Caddy, DNSSEC: ON
Service: `petaltongue-web.service` (systemd user, lingering enabled)

**Live now**: Physical topology, K-Derm layers, hardening controls, depot status,
ecosystem coordination — all rendered from manifest data.

**DIVs resolved**:
- DIV-1 FIXED: nestGate `--socket /run/membrane/nestgate-e8b62b6e.sock` added via systemd drop-in.
  Neural API `capability.resolve("content.get")` now routes to nestGate.
- DIV-2 FIXED: Symlink `/run/user/1000/biomeos/content-provider-e8b62b6e.sock → nestgate-e8b62b6e.sock`.
  Persisted via `ExecStartPost` in `membrane-nestgate.service.d/uds-socket.conf`.
- DIV-3 ACCEPTED: Port 8190 (8090 occupied). No action needed.
- DIV-4 FIXED: Title branded "nestgate.io — ecoPrimals Data Surface", h1 "nestgate.io".
  petalTongue v1.7.0 rebuilt with branding and deployed.

**Remaining**: CAS content data not yet populated on sporeGate (WG overlay shows
"Not Found" — this is a CAS miss, not a socket error). Needs CAS population from
westGate or mesh-replicated data braids.

### Phase 1 COMPLETE: petalTongue Mesh Surface

petalTongue serves nestgate.io natively from sporeGate. No more redirect.
Data pages will be served by a primal, not a static site.

### Phase 2: Depot + Provenance Browser — **ACTIVE (Wave 157j)**

Depot browsing and provenance inspection routes added to petalTongue web mode:
- `/depot/` — architecture overview (binary counts, sizes)
- `/depot/{arch}` — list binaries for architecture with BLAKE3 checksums
- `/depot/{arch}/{name}` — single binary provenance (hash, size, depot URL)
- `/provenance/` — provenance chain overview (architectures, tracked binary counts)
- `/provenance/{hash}` — single-object provenance tree (BLAKE3 lookup across depot)

Data source: local depot filesystem + `checksums.toml`. Phase 3 will federate
across gates via songBird `content.locate` mesh queries.

### Phase 3: Federated CAS + Compute Memoization

nestgate.io becomes the **data federation surface** — not just one gate's CAS,
but a federated view across all gates:

- `/cas/{hash}` — retrieve any CAS object by BLAKE3 hash, federated across gates
- `/cas/{hash}/provenance` — full provenance chain (DAG → spine → Merkle → braid)
- `/cas/{hash}/replicate` — replication instructions (which gates hold copies)
- `/compute/configs/` — memoized compute configurations (thermalized lattices, etc.)
- `/compute/configs/{hash}` — retrieve a cached compute config with its provenance

**Data Federation Pattern**: nestgate.io resolves CAS queries by consulting
nestGate instances on multiple gates via songBird mesh. A request for a hash
checks westGate (data NAS), strandGate (compute configs), ironGate (consumer
data), and any gate with a local CAS. The first gate holding the object serves
it. This is the same content-addressed pattern as git — the hash is the address,
the gate is an implementation detail.

**Compute Memoization for QCD**: strandGate's thermalized lattice configs
(38 MB at 16⁴, deterministic on `dims,β,seed,n_therm,integrator`) are CAS
objects with provenance braids. hotSpring can request a config via nestgate.io
and get it from whichever gate holds it — strandGate (origin), biomeGate
(cross-vendor validation), or any future compute gate. The 37-minute CPU
thermalization becomes a one-time cost stored forever.

**Replication**: Any researcher can hit `/cas/{hash}/replicate` to get:
1. The object itself (or a download link to the gate holding it)
2. The full provenance chain proving its lineage
3. Instructions to reproduce it independently (parameters, code commit, gate)

### Phase 4: Validation Endpoint

Public validation API:
- `/validate/cas/{hash}` — verify a CAS object exists and return its provenance
- `/validate/dataset/{name}` — verify all objects in a dataset, report completeness
- `/validate/replicate/{name}` — generate replication package (hashes + instructions)

This is what makes nestgate.io the "trust surface" — external researchers can
independently verify that the data they received matches the provenance chain.

### Phase 5: git Migration

Move `git.primals.eco` under nestgate.io:
- `nestgate.io/git/` or `git.nestgate.io` — Forgejo
- CAS + git + depot all under the peptidoglycan layer

---

## Caddy Configuration (golgi — LIVE)

Source of truth: `/etc/membrane/Caddyfile` on golgi.
Version-controlled copy: `infra/plasmidBin/membrane/Caddyfile` (synced Aug 4, 2026).

golgi does TLS termination (Let's Encrypt auto-cert, CAA-locked).
Security headers, CSP, access logging, gzip on all blocks.

### Routing Table (LIVE)

| Subdomain | Backend | Port | Gate | Notes |
|-----------|---------|------|------|-------|
| `primals.eco` | redirect → `sporeprint.primals.eco` | — | golgi | + `/enroll` → 127.0.0.1:7780 |
| `www.primals.eco` | redirect → `sporeprint.primals.eco` | — | golgi | |
| `sporeprint.primals.eco` | Zola static | filesystem | golgi | 302 pages, pseudoSpore gallery |
| `footprint.primals.eco` | reverse_proxy | :8090 | sporeGate `10.13.37.2` | GIS composition |
| `webb.primals.eco` | reverse_proxy | :8090 | ironGate `10.13.37.7` | CRPG game garden |
| `live.primals.eco` | reverse_proxy | :8190 | sporeGate `10.13.37.2` | petalTongue TOPO-VIS (shares port with nestgate.io) |
| `lab.primals.eco` | reverse_proxy | :7780 | sporeGate `10.13.37.2` | JupyterHub (basicauth) |
| `membrane.primals.eco` | mixed | — | golgi | depot, hooks, status |
| `depot.primals.eco` | filesystem | — | golgi | binary depot browser |
| `ca.primals.eco` | reverse_proxy | :9443 | golgi (localhost) | step-ca SSH CA |
| `relay.primals.eco` | static | — | golgi | RustDesk page (basicauth) |
| `git.primals.eco` | reverse_proxy | :3000 | golgi (localhost) | Forgejo + webhook handler |
| **`nestgate.io`** | reverse_proxy | :8190 | **sporeGate `10.13.37.2`** | **petalTongue mesh** |
| `www.nestgate.io` | redirect → `nestgate.io` | — | golgi | |

---

## Data Federation Architecture

nestgate.io is not a single-gate service — it's a **federated CAS front door**
backed by nestGate instances running on every NUCLEUS gate:

```
                    nestgate.io (golgi / petalTongue)
                         │
              ┌──────────┼──────────────┐
              │          │              │
         westGate    strandGate     ironGate
         (data NAS)  (compute)     (consumer)
         519 GB       lattice       footPrint
         130 datasets configs       projects
         AlphaFold    QCD memos     GIS cache
```

### Federation Flow

1. **Request**: `GET nestgate.io/cas/{hash}`
2. **Resolve**: petalTongue queries local nestGate → not found →
   songBird `content.locate` mesh broadcast → westGate responds "I have it"
3. **Serve**: petalTongue proxies the response from westGate's nestGate
4. **Cache**: golgi optionally caches hot objects locally (L1 cache for public)

### What Lives Where

| Gate | CAS Contents | Federation Role |
|------|-------------|-----------------|
| **westGate** | 519 GB science data, AlphaFold, LINCS, PDB, SRA | Primary data origin |
| **strandGate** | Thermalized lattice configs, QCD production results | Compute memoization origin |
| **ironGate** | footPrint GIS projects, esotericWebb game state | Consumer data origin |
| **golgi** | Hot object cache, depot binaries | Public edge / L1 cache |
| **biomeGate** | Cross-vendor validation configs | Compute validation |

### Why This Matters

- **For hotSpring QCD**: thermalized configs computed on strandGate are available
  to any gate via nestgate.io. biomeGate can pull a config for cross-vendor
  parity checks. A future compute gate joins the mesh and immediately has access
  to all cached configs — no manual transfer.

- **For tideGlass NF**: GPS platform data on westGate is retrievable from any
  gate via nestgate.io. When tideGlass runs on ironGate (or any future gate),
  it fetches data by hash, not by knowing which gate has it.

- **For replication**: A reviewer hits `nestgate.io/cas/{hash}` with a hash
  from a paper. nestgate.io resolves it across the mesh and returns the object
  with its full provenance chain. The reviewer can independently verify that
  the data is what the paper claims.

---

## CAS Data Braids Divergences (Upstream → Overwatch)

These divergences from the tideGlass CAS wiring AAR affect all primals
consuming CAS data. **Owned by upstream overwatch, not sporeGate topology.**

| DIV | Issue | Owner |
|-----|-------|-------|
| DIV-1 | DATA_ACCESS.md wrong hash format (`blake3:abc123` vs plain hex) | overwatch |
| DIV-2 | No `content.query` — only exact hash retrieval | nestGate team |
| DIV-3 | DATA_ACCESS.md references nonexistent methods | overwatch |
| DIV-4 | GPS data is NumPy/pickle — needs converter | westGate data |
| DIV-5 | groundSpring, airSpring stale CAS clients | overwatch |
| DIV-6 | `content.get` 64 MiB limit — needs streaming | nestGate team |

**Recommendation from tideGlass**: Publish canonical `nestgate-client` crate.

---

## DNS Ownership

| Domain | Registrar | DNS Provider | Nameservers | Managed By |
|--------|-----------|--------------|-------------|------------|
| primals.eco | Porkbun | **Cloudflare** | albertus/serena.cloudflare.com | User via CF dashboard |
| nestgate.io | Porkbun | **Sovereign Knot DNS** | ns1/ns2.primals.eco (golgi/golgi-ext) | sporeGate via `knotc` |
| primal.eco | Porkbun | **Sovereign Knot DNS** | ns1/ns2.primals.eco (golgi/golgi-ext) | sporeGate via `knotc` |

Sovereign DNS: Knot DNS with automatic DNSSEC (ECDSA P-256). Master on golgi
(`[RELAY_PUBLIC]`), slave on golgi-ext (`137.184.197.151`). Zone transfers via AXFR/IXFR.

Cloudflare only used for primals.eco (outer membrane). Inner two layers are fully
sovereign — no external DNS dependency.

---

## K-Derm Separation — Operational Plan

### Current DNS Records (Cloudflare)

**primals.eco** (LIVE — outer membrane):
```
A       primals.eco           → [RELAY_PUBLIC] (golgi)        ✓ LIVE
CNAME   sporeprint            → primals.eco                   ✓ LIVE
CNAME   lab                   → primals.eco                   ✓ LIVE
CNAME   relay                 → primals.eco                   ✓ LIVE
CNAME   ca                    → primals.eco                   ✓ LIVE
CNAME   depot                 → primals.eco                   ✓ LIVE
A       git.primals.eco       → [RELAY_PUBLIC] (golgi)        ✓ LIVE (Forgejo)
```

**nestgate.io** (LIVE — peptidoglycan):
```
A       nestgate.io           → [RELAY_PUBLIC] (golgi)        ✓ LIVE (→ petalTongue via mesh)
```

**primal.eco** (NOT YET SEPARATED — inner membrane):
```
(no public DNS records — internal resolution only)
```

### What sporeGate Owns (no user action needed)

| Task | What | Status |
|------|------|--------|
| **golgi Caddy routing** | All Caddyfile changes for primals.eco + nestgate.io | sporeGate SSHs into golgi |
| **sporeGate petalTongue** | `petaltongue-web.service` serving nestgate.io on :8190 | LIVE |
| **dnsmasq LAN resolution** | Internal `*.primal.eco` resolution for mesh gates | sporeGate dnsmasq config |
| **Forgejo config** | git.primals.eco backend on golgi | sporeGate manages |
| **Let's Encrypt certs** | Auto-renewed by Caddy for all public domains | Automatic |
| **nestgate.io content evolution** | Wire biomeOS content provider, branding, CAS federation | sporeGate + petalTongue team |

### What Needs User Action (Porkbun / Cloudflare)

| Task | Where | What | Priority |
|------|-------|------|----------|
| **KD-01: Verify nestgate.io DNSSEC** | Cloudflare | Confirm DNSSEC is ON for nestgate.io zone (should be, but verify) | P2 |
| **KD-02: Add nestgate.io subdomains** | Cloudflare | When ready: `git.nestgate.io` CNAME → nestgate.io (Phase 5 — git migration) | FUTURE |
| **KD-03: primal.eco — remove any public A records** | Porkbun/Cloudflare | If primal.eco has any public A/CNAME records, remove them. Inner membrane must NOT be publicly resolvable. | **P1** |
| **KD-04: primal.eco — verify nameservers** | Porkbun | If primal.eco is on Cloudflare, consider removing it from CF entirely (no public DNS needed). OR keep it on CF with zero records (domain parked). | **P1** |
| **KD-05: footprint.primals.eco** | Cloudflare | Add CNAME `footprint` → `primals.eco` (for ironGate routing via golgi) | **P1** |
| **KD-06: Verify primals.eco DNSSEC** | Cloudflare | Confirm DNSSEC chain is intact (Porkbun DS records → Cloudflare) | P2 |

### primal.eco Internal Resolution (sporeGate dnsmasq)

sporeGate's dnsmasq provides internal resolution for the inner membrane:

```
# /etc/dnsmasq.d/primal-eco.conf (sporeGate)

# Inner membrane — gate names resolve to WireGuard IPs
address=/golgi.primal.eco/10.13.37.1
address=/sporegate.primal.eco/10.13.37.2
address=/biomegate.primal.eco/10.13.37.3
address=/eastgate.primal.eco/10.13.37.5
address=/flockgate.primal.eco/10.13.37.6
address=/irongate.primal.eco/10.13.37.7
address=/northgate.primal.eco/10.13.37.8
address=/strandgate.primal.eco/10.13.37.10
address=/westgate.primal.eco/10.13.37.11
address=/bluegate.primal.eco/10.13.37.12
```

Gates that use sporeGate as DNS (via DHCP or manual) get `*.primal.eco`
resolution for free. Gates off the LAN resolve via WireGuard mesh +
songBird discovery (no DNS needed — UDS sockets).

### Separation Checklist

- [x] **primals.eco (outer)** — LIVE. Zola + Caddy on golgi. DNS on Cloudflare.
- [x] **nestgate.io (peti)** — LIVE. petalTongue on sporeGate via mesh. Sovereign Knot DNS.
- [x] **primal.eco (inner)** — SEALED. All 6 public A records REMOVED from Knot DNS zone.
- [x] **www.nestgate.io** — Fixed to golgi ([RELAY_PUBLIC]). Caddy redirect added.
- [x] **Caddyfile** — nestgate.io + www.nestgate.io + sporeprint.primals.eco blocks added.
- [x] **primal.eco dnsmasq config** — Created. Ready to deploy to sporeGate.
- [x] **golgi SSH host key** — Fixed. Master DNS accessible.
- [ ] **KD-04**: Decide primal.eco nameserver posture (keep sovereign or park) — P3
- [x] ~~**KD-05**~~: `footprint.primals.eco` — NOT NEEDED, wildcard `*.primals.eco` covers all subdomains. sporeGate owns routing via Caddy.
- [x] **KD-06**: primals.eco DNSSEC chain VERIFIED — DS 2371/13/2 matches at .eco TLD and Porkbun
- [ ] **Deploy Caddyfile** to golgi — sporeGate team
- [ ] **Deploy dnsmasq config** to sporeGate — sporeGate team
- [ ] **Wire biomeOS content provider** for nestgate.io (DIV-1)
- [ ] **Brand nestgate.io** — title, header, favicon (DIV-4)
- [ ] **git.nestgate.io** migration (Phase 5, FUTURE)
