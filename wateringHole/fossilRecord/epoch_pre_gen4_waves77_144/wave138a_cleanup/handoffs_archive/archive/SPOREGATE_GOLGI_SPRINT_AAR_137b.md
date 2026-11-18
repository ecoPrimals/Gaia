# sporeGate/golgi Sprint AAR — Wave 137b

**Date**: Jul 13, 2026 | **Wave**: 137b | **Author**: sporeGate overwatch

---

## Items Resolved (5)

### STALE-PEER — 15min

Ghost peer `10.13.37.0:8080` (pre-port-fix songBird) was present because mesh was in `awaiting_init` state after songBird binary upgrade earlier today. Re-initialized mesh with `mesh.init` specifying correct golgi peer `10.13.37.1:7700`. Verified 1 direct peer, no ghost entries.

### FORGEJO-PERMS — 30min

Files inside `sporeprint.git` and `wateringhole.git` on golgi were owned by `root:root` instead of `git:git` — leftover from the SHALLOW-PINGPONG unshallow operation (bare clones run as root via SSH). Fixed with `chown -R git:git /opt/forgejo/data/repositories/ecoprimals/`. Verified 0 non-git-owned files remain. Push tests pass for wateringHole, cellMembrane, and songBird.

**Root cause**: Ad-hoc `git clone --bare` operations running as root during the Forgejo unshallow migration.

**Prevention**: Future unshallow/clone operations should include a `chown -R git:git` step immediately after clone, as the original unshallow script did for individual repos but not for subsequent pushes.

### DEPOT-POLICY — 15min

Promoted depot trust default from `VerifyIfPresent` to `RequireSigned`:

- Set `DEPOT_TRUST_POLICY=require-signed` in `/etc/environment` on both sporeGate and golgi.
- Updated `provision-golgi.sh` to set this env var during provisioning.
- Verified `membrane plasmid.fetch --source wan --dry-run` reads the policy correctly.

Any `plasmid.fetch` invocation will now **reject unsigned depot artifacts**. This closes the SIGN-VERIFY-ON-FETCH trust model gap.

### LIVE-DNS (completed earlier this session)

Cloudflare DNS A record `live → [RELAY_PUBLIC]` created (grey cloud). Caddy on golgi auto-obtained Let's Encrypt cert via TLS-ALPN-01 challenge. `https://live.primals.eco` now serves petalTongue TOPO-VIS dashboard:

- TLSv1.3 / HTTP2
- 7 mesh peers visible (sporeGate, eastGate, ironGate, flockGate, grapheneGate, strandGate, golgi)
- Full security header suite (HSTS, CSP, X-Frame-Options, Permissions-Policy)
- API endpoints: `/api/topology/live`, `/api/topology-layers`, `/api/gate-mesh`, `/api/events` (SSE)

### DEPOT-REFRESH (completed earlier this session)

songBird `74cf7101` rebuilt with FP-API + mesh port + UDS-HTTP fixes. Depot re-signed and synced to golgi. SONGBIRD-EASTGATE unblocked.

---

## Remaining Items (not sporeGate-owned)

| Team | ID | Status |
|------|----|--------|
| biomeOS | NAPI-LIFECYCLE | Open — lifecycle.status count=0 |
| biomeOS | SOCKET-DIR-UNIFY | Open — 3 socket dirs → 1 |
| biomeOS | SOCKET-UMASK | Open — fchmod after bind |
| songBird | DRAWBRIDGE-CAP | Open — routes not registering as capabilities |
| songBird | SONGBIRD-LOCAL | Open — cleanup commit pending |
| flockGate | FP-API-CADDY | Open — Caddy GIS proxy config |
| eastGate | SONGBIRD-EASTGATE | Unblocked — depot refresh done |

---

*sporeGate/golgi team: all 5 items delivered. Depot trust chain fully enforced (RequireSigned). live.primals.eco operational.*
