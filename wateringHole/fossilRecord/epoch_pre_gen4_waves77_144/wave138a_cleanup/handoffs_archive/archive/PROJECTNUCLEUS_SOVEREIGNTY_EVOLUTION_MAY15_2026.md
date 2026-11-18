# projectNUCLEUS — Sovereignty Evolution Handoff

**Date**: 2026-05-15
**Author**: projectNUCLEUS (ironGate)
**Audience**: primalSpring upstream audit
**Scope**: Forgejo primary adoption, VPS Tower deployment, Channel 3 shadow, content-aware routing

---

## Summary

Five sovereignty evolution items completed in a single session, advancing
the "VPS as touchpoint, gate as source" architecture:

1. **Forgejo as primary git host** — 32 repos, 3 orgs, dual-push configured
2. **VPS upgrade + Tower composition** — resized to 2GB, BearDog + SkunkBat deployed
3. **Channel 3 TLS shadow** — Caddy on :80, TLS blocks ready for DNS grey-cloud
4. **Content-aware routing prototype** — routing_config.toml with trust/bonding model
5. **Canvas visualization** — interactive architecture diagram in Cursor Canvas

---

## Work Items

### 1. Forgejo as Primary Git Host

- Forgejo SSH server enabled (built-in, port 2222)
- API token generated, `.netrc` credential caching configured
- SSH public key added to `irongate` user
- `forgejo_mirror.sh` created — automates org/repo creation + remote setup
- 3 orgs created: `sporeGarden` (5 repos), `ecoPrimals` (19 repos), `syntheticChemistry` (8 repos)
- All 32 repos pushed to Forgejo. Zero failures
- Forgejo remote added to all local repos
- **GitHub is now the push mirror (outer membrane)**

### 2. VPS Upgrade + Tower Composition

- `doctl` installed, authenticated with DO API token
- cellMembrane droplet resized: `s-1vcpu-512mb-10gb` → `s-1vcpu-2gb` ($4→$12/mo)
- BearDog binary uploaded: 9MB, listening on UDS `/run/membrane/beardog.sock` + TCP :9100
- SkunkBat binary uploaded: 2.6MB, listening on TCP :9140 (standalone `--no-uds` mode)
- `beardog-membrane.service` installed and enabled
- `skunkbat-membrane.service` fixed for standalone mode (no biomeOS UDS ecosystem)
- `tmpfiles.d/membrane.conf` created for runtime dir persistence across reboots
- DO API token encrypted with BearDog AES-256-GCM (Argon2id KDF, `membrane-vault` key)
- `vps_resize.sh` created for future resize operations
- **6 services active**: songbird-relay, hbbs-membrane, hbbr-membrane, beardog-membrane, skunkbat-membrane, caddy-tls
- **1.7GB RAM free** after Tower deployment

### 3. Channel 3 TLS Shadow

- Caddy v2.11.3 installed as transitional TLS proxy
- `caddy-tls.service` created: systemd unit with `AmbientCapabilities=CAP_NET_BIND_SERVICE`
- Caddyfile deployed with content-aware routing handlers
- UFW rules added: 443/tcp (TLS Surface), 80/tcp (ACME + Health)
- Health endpoint LIVE: `curl http://[RELAY_PUBLIC]/health` → 200
- TLS subdomain blocks commented — ready for DNS grey-cloud activation
- **Stability note**: Caddy is transitional. Songbird will absorb TLS termination as primal capability

### 4. Content-Aware Routing Prototype

- `routing_config.toml` created with:
  - 4 backends: `vps_cache`, `gate` (BTSP tunnel), `peer` (Songbird P2P), `fallback` (GitHub CDN)
  - 10 routing rules evaluated in priority order
  - Cache policy: 256MB max, 1h TTL, webhook invalidation
  - Cost awareness: prefer P2P for files > 50MB to avoid VPS bandwidth
  - Trust model: covalent/ionic/metallic/weak → content scope mapping
- NestGate cache directory created on VPS (`/var/cache/membrane/nestgate/`)
- Landing page seeded in cache (sovereignty status page)
- `nucleus_config.sh` updated with Channel 3 + routing settings

### 5. Architecture Canvas

- Interactive Canvas visualization created (`sovereignty-architecture.canvas.tsx`)
- Three tabs: Architecture (DAG diagram), Routing (decision flow), Budget (cost breakdown)
- Shows inner/outer/intracellular membrane layers, channel status, shadow tracks

---

## Upstream Gaps Found

None new. Existing gaps remain unchanged:
- **Songbird TLS termination**: Not yet a primal capability. Using Caddy as transitional proxy
- **BearDog reverse-proxy**: BearDog is crypto, not HTTP proxy. Correct architecture: Songbird (TLS) + BearDog (crypto identity)

## Artifacts

| File | Location | Purpose |
|------|----------|---------|
| `forgejo_mirror.sh` | `projectNUCLEUS/deploy/` | Forgejo org/repo creation + dual-push |
| `vps_resize.sh` | `projectNUCLEUS/deploy/` | doctl VPS resize automation |
| `routing_config.toml` | `projectNUCLEUS/deploy/` | Content-aware routing rules |
| `caddy-tls.service` | `plasmidBin/membrane/` | Channel 3 systemd unit |
| `skunkbat-membrane.service` | `plasmidBin/membrane/` | Fixed for standalone mode |
| `sovereignty-architecture.canvas.tsx` | Cursor canvases | Interactive architecture viz |
| VPS `/etc/membrane/Caddyfile` | Remote | Content-aware proxy config |
| VPS `/etc/membrane/routing_config.toml` | Remote | Routing rules (deployed copy) |
| VPS `/opt/membrane/credentials.age` | Remote | Encrypted DO token |
| VPS `/etc/tmpfiles.d/membrane.conf` | Remote | Runtime dir persistence |

## Next Steps (for upstream review)

1. **Songbird TLS capability**: When will Songbird absorb TLS termination? Current Caddy proxy is transitional
2. **Second droplet audit**: 570909451 at 159.223.173.73 — old primalSpring instance, unreachable. Should it be destroyed?
3. **Channel 1 (knot-dns)**: Ready for sovereign DNS when VPS has headroom (2GB provides this)
4. **DNS grey-cloud**: Need to grey-cloud `membrane.primals.eco` A record to VPS IP for ACME cert
5. **Forgejo Actions**: 74 GitHub workflows to port when Forgejo becomes CI-capable
