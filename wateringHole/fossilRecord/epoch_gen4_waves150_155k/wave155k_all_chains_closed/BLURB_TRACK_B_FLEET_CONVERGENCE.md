# Track B: Fleet Convergence — 5-Gate Enrollment + NUCLEUS Validation

> **CONVERGED**: Tracks A and B merged into unified ECOSYSTEM_BLURB.md (Wave 155b).
> This file retained as reference for enrollment phases and validation procedures.
> See ECOSYSTEM_BLURB.md for current team assignments and glacial goals (G1, G4, G7).

**Wave**: 155b | **Owner**: eastGate overwatch
**Converged with**: Track A (Evolution) — see ECOSYSTEM_BLURB.md
**Phase 0 COMPLETE** — enrollment endpoint LIVE on golgiBody, tested via WAN Caddy TLS.

---

## GOAL

Get the 5 returning gates fully enrolled and converged via the autonomous
enrollment system. Solve remaining divergences. Validate the entire
postPrimordial deployment pipeline end-to-end using benchScale and agentReagents
to provision a NUCLEUS fleet. **All binaries from golgiBody** — zero USB,
zero manual transfer.

This track tests the membrane and the postPrimordial deployment system we built.
Once validated, this is the template for enrolling any gate anywhere in the world.

---

## PHASE 0: GOLGI DEPLOYMENT — **COMPLETE** (Wave 155b)

The enrollment endpoint is LIVE on golgiBody.

### What Was Done

1. **Binary deployed**: songBird 0.2.1 with `mesh.gate_enroll` handler + `load_family_seed_bytes()` file path support. Built from eastGate, deployed via SCP.
2. **Drawbridge configured**: systemd drop-in at `/etc/systemd/system/songbird-membrane.service.d/enrollment.conf` with:
   - `SONGBIRD_DRAWBRIDGE_ROUTES=/enroll=mesh!public`
   - `SONGBIRD_PROXY_ROUTES=mesh=jsonrpc:///run/membrane/songbird.sock`
   - `GATE_ENROLLMENT_TOKEN` (SHA-256 token)
   - `FORGEJO_API_TOKEN` (Forgejo service account)
3. **Caddy TLS**: `/enroll/*` reverse proxy to `:7780` in `/etc/membrane/Caddyfile`
4. **Scripts staged**: `gate-enroll.sh` and `enroll-fleet.sh` at `membrane.primals.eco/depot/enroll/`

### Verification

```bash
# Drawbridge routing (correct token → phases execute):
curl -s -X POST http://127.0.0.1:7780/enroll/mesh.gate_enroll \
  -H "Content-Type: application/json" \
  -d '{"gate_name":"test","wg_public_key":"test","physical_proof":{"type":"token","token":"<token>"}}'

# WAN path (Caddy TLS):
curl -s -X POST https://primals.eco/enroll/mesh.gate_enroll \
  -H "Content-Type: application/json" \
  -d '{"gate_name":"test","wg_public_key":"test","physical_proof":{"type":"token","token":"wrong"}}'
# → {"enrolled":false,"reason":"Physical proof verification failed"}

# From eastGate over WG — should reach golgiBody:
curl -s http://10.13.37.1:7780/enroll \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"mesh.gate_enroll","params":{},"id":1}'

# From WAN (after Caddy proxy):
curl -s https://primals.eco/enroll \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"mesh.gate_enroll","params":{},"id":1}'
```

### Phase 0 Checklist

- [ ] songBird binary on golgiBody includes `mesh.gate_enroll` (Wave 155a+)
- [ ] bearDog binary on golgiBody includes FIDO2/beacon attestation (Wave 155a+)
- [ ] `SONGBIRD_DRAWBRIDGE_ROUTES=/enroll=mesh!public` configured
- [ ] `GATE_ENROLLMENT_TOKEN` set
- [ ] `FORGEJO_API_TOKEN` set (existing GSC service account)
- [ ] `FAMILY_SEED` or `BEARDOG_FAMILY_SEED` set
- [ ] WAN exposure via Caddy `/enroll` or direct `:7780`
- [ ] Local `curl` to `/enroll` returns JSON-RPC error (not connection refused)
- [ ] Remote `curl` from eastGate over WG succeeds

---

## PHASE 1: COMPLETE ENROLLMENT (5 gates → meshed)

Once Phase 0 is live, enrollment is one command per gate.

### Enrollment Execution

```bash
# On each gate (via RustDesk or SSH):
./infra/plasmidBin/enroll/gate-enroll.sh \
  --hub primals.eco \
  --gate <gate_name> \
  --token <GATE_ENROLLMENT_TOKEN> \
  --compose full
```

### Gate-by-Gate Status

| # | Gate | Current State | Enrollment Action | Post-Enrollment |
|---|------|---------------|-------------------|-----------------|
| 1 | southGate | WG keyed, repos at Wave ~114 | `--token` retroactive | Fast-forward repos from Forgejo |
| 2 | strandGate | WG keyed, repos at Wave ~114 | `--token` retroactive | Fast-forward repos from Forgejo |
| 3 | westGate | WG keyed, mixed-wave repos | `--token` retroactive | **Divergence resolution** (see Phase 2) |
| 4 | blueGate | Fresh, no WG keys, **Windows** | `gate-enroll.ps1` full enrollment | Clone repos, genomeBins (.exe) from golgiBody |
| 5 | swiftGate | Fresh, no WG keys, **Windows** | `gate-enroll.ps1` full enrollment | Clone repos, genomeBins (.exe) from golgiBody |

### Enrollment Success Criteria (per gate)

- [ ] Gate has mesh IP in .20-.254 range
- [ ] `ping 10.13.37.1` succeeds from gate (hub reachable over WG)
- [ ] `ssh -T git@forgejo` succeeds (Forgejo SSH key registered)
- [ ] Family seed stored at `~/.config/ecoPrimals/family_seed.enc`
- [ ] Gate appears in `wg show wg0` peers on golgiBody

---

## PHASE 2: CONVERGENCE — REPOS + BINARIES FROM GOLGI

After enrollment, each gate fetches everything from golgiBody. Zero USB.

### Standard Convergence (south, strand, blue, swift)

```bash
ECO_ROOT=/home/$USER/Development/ecoPrimals
mkdir -p "$ECO_ROOT"/{primals,springs,infra,gardens}

# Clone all repos from Forgejo over mesh
for org in ecoPrimals sporeGarden; do
  repos=$(curl -s "http://10.13.37.1:3000/api/v1/orgs/$org/repos?limit=50" | jq -r '.[].name')
  for repo in $repos; do
    git clone "ssh://git@10.13.37.1:2222/$org/$repo.git" "$ECO_ROOT/$repo" 2>/dev/null \
      || (cd "$ECO_ROOT/$repo" && git fetch origin && git merge --ff-only origin/main)
  done
done
```

### westGate Divergence Resolution

```bash
for repo in "$ECO_ROOT"/*/; do
  cd "$repo"
  git fetch origin
  LOCAL=$(git rev-parse HEAD)
  REMOTE=$(git rev-parse origin/main)
  BASE=$(git merge-base HEAD origin/main 2>/dev/null)
  if [ "$LOCAL" = "$REMOTE" ]; then
    echo "OK: $(basename $repo)"
  elif [ "$LOCAL" = "$BASE" ]; then
    git merge --ff-only origin/main && echo "FF: $(basename $repo)"
  else
    echo "DIVERGED: $(basename $repo) — reset to Forgejo HEAD"
    git reset --hard origin/main
  fi
done
```

### genomeBin Deployment from golgiBody Depot

golgiBody is the **sole depot**. No local depots. Gates fetch genomeBins
for their architecture via WAN TLS or mesh.

```bash
# gate.bootstrap auto-detects architecture and fetches from golgiBody:
membrane gate.bootstrap <gate_name>

# Manual fetch (Linux):
cd "$ECO_ROOT/infra/plasmidBin"
PLASMIDBIN_RELEASE_URL="https://depot.primals.eco" ./fetch.sh pull

# Windows: genomeBins are .exe, fetched via same depot path
# primals/x86_64-pc-windows-gnu/beardog.exe, songbird.exe, etc.
```

### Source Build (validation only, not deployment)

```bash
for primal in "$ECO_ROOT"/primals/*/; do
  (cd "$primal" && cargo build --release 2>&1 | tail -1)
done

# Validate
cd "$ECO_ROOT/springs/primalSpring" && cargo test --release
```

---

## PHASE 3: NUCLEUS VALIDATION — benchScale + agentReagents

Validate the postPrimordial deployment pipeline at increasing fidelity.

### Level 1: Docker Composition (minutes)

```bash
cd infra/benchScale
cargo run -- create nucleus-test topologies/ecoprimals-nucleus-3node.yaml
./scripts/deploy-ecoprimals.sh --lab nucleus-test --plasmidbin ../plasmidBin
./scripts/run-tests.sh
```
**Proves**: 13-primal composition health, cross-gate signaling.

### Level 2: WaterFall Cascade (enrollment-adjacent)

```bash
cargo run -- create wf-test topologies/ecoprimals-waterfall-gate-sync.yaml
./scripts/deploy-waterfall.sh --lab wf-test
```
**Proves**: Forgejo cascade-pull parity, temporal cascade health.

### Level 3: VPS Depot Fleet (6-gate sim)

```bash
cargo run -- create fleet-test topologies/ecoprimals-vps-depot-deploy.yaml
./scripts/deploy-vps-depot.sh --lab fleet-test
```
**Proves**: Multi-gate depot deployment, federation peering, version parity.

### Level 4: Libvirt OS-Fidelity (production mirror)

```bash
# Build gate images
cd infra/agentReagents
cargo run --bin agent-reagents -- build templates/gates/gate-nucleus-full.yaml
cargo run --bin agent-reagents -- build templates/gates/gate-nuc-canary.yaml

# Create mesh
cd ../benchScale
cargo run --features libvirt -- create mesh-test \
  topologies/irongate-nucleus-mesh.yaml --backend libvirt

# Validate
./scripts/validate-mesh.sh --topology irongate-nucleus-mesh
```
**Proves**: Real systemd, UDS sockets, SongBird federation, BearDog crypto spine,
`temporal.cascade --dry-run` zero skew, canary constraints.

---

## PHASE 4: PHYSICAL GATE ENROLLMENT

After simulation passes, enroll the actual 5 gates:

```bash
# On each gate (via RustDesk):
./gate-enroll.sh --hub primals.eco --gate strandGate --token <token> --compose full
# Wait... enrolled. Clone repos, validate.
```

---

## PHASE 5: ENMESHMENT — GATES AS COMPUTE

| Gate | Mesh IP | Role | Composition | K-Derm | Deployments |
|------|---------|------|-------------|--------|-------------|
| strandGate | .20-.254 | Linux. Bioinformatics compute (128 threads, RTX 3090) | `compute` | intra-inner | Tower Atomic workhouse. NF pipeline, wetSpring, neuralSpring |
| westGate | .20-.254 | Linux. 5x14TB HDD (70TB ZFS cold pool) | `nest` | periplasm | NestGate CAS backend, ecosystem archive, WAN mesh |
| blueGate | .20-.254 | **Windows**. Distributed builder + media/gaming | `tower` | intra-inner | Tower Atomic (TCP). Build node under sporeGate foreman |
| swiftGate | .20-.254 | **Windows**. Hobby/consumer (like northGate) | `full` | cytoplasm | Full NUCLEUS (TCP). Gaming, desktop, family use |
| southGate | .20-.254 | Linux. Full NUCLEUS — house2 sovereign site | `full` | cytoplasm | 13-primal deployment, second hub candidate |

### Ongoing Updates from golgiBody

Once meshed, gates stay current automatically:
1. `wave.toml` announces new waves
2. `membrane temporal.cascade --check` detects staleness
3. `git fetch origin && git merge --ff-only origin/main` pulls updates
4. Depot binaries refresh via `plasmidBin/fetch.sh pull`
5. New systems on golgiBody (new primals, new endpoints) propagate to all gates

---

## SCALING: NEW GATES ANYWHERE IN THE WORLD

This pipeline is the template for any future gate enrollment:

1. **Physical access**: Operator has a machine + internet
2. **Trust token**: Operator receives enrollment token (or has SoloKey/grapheneGate)
3. **One command**: `gate-enroll.sh --hub primals.eco --token <token>`
4. **Automatic**: WG mesh IP, Forgejo SSH, family seed — all from golgiBody
5. **Converge**: Clone repos, pull depot binaries, validate
6. **Online**: Gate publishes head, receives cascade updates

No SSH tunneling, no USB drives, no manual WG config, no operator on golgiBody.
The only human action is giving the enrollee a trust token (or stronger: a SoloKey).

### Future Trust Escalation

| Scenario | Proof | Trust |
|----------|-------|-------|
| Remote datacenter | Pre-shared token via secure channel | Extended |
| In-person meeting | grapheneGate beacon tap | Sibling |
| Trusted operator with SoloKey | FIDO2 attestation | Kin |
| Zero-trust onboarding | Token + post-enrollment primalSpring validation | Extended → Sibling (earned) |

---

## SUCCESS CRITERIA — TRACK B COMPLETE WHEN:

### Phase 0 (golgiBody live) — **COMPLETE**
- [x] songBird 0.2.1 with mesh.gate_enroll deployed (SCP from eastGate)
- [x] Drawbridge `/enroll/*` route exposed via Caddy TLS (`primals.eco/enroll/mesh.gate_enroll`)
- [x] Enrollment endpoint verified via curl — WAN + local, correct token → phases execute

### Phase 1 (enrollment)
- [ ] All 5 gates enrolled (mesh IP, WG peer, Forgejo SSH, family seed)

### Phase 2 (convergence)
- [ ] All 5 gates at Forgejo HEAD (43+ repos)
- [ ] westGate divergence resolved
- [ ] All bins sourced from golgiBody depot (zero USB)

### Phase 3 (validation)
- [ ] benchScale Level 1 (Docker NUCLEUS) PASS
- [ ] benchScale Level 2 (WaterFall cascade) PASS
- [ ] benchScale Level 3 (VPS depot fleet) PASS
- [ ] benchScale Level 4 (libvirt OS-fidelity mesh) PASS

### Phase 4 (physical)
- [ ] At least 1 physical gate validates end-to-end enrollment

### Phase 5 (enmeshment)
- [ ] Published heads for all 5 gates in `wateringHole/heads/`
- [ ] At least 1 gate serving its designated compute role

---

*Track B is independent of Track A. Phase 0 is COMPLETE — the enrollment
endpoint is live on golgiBody. Gates anywhere in the world can self-enroll by
fetching `gate-enroll.sh` from `membrane.primals.eco/depot/enroll/` and running
with a valid enrollment token.*
