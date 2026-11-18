# AAR: DNS/TLS Cutover — primals.eco to golgi (Wave 134h)

> **SUPERSEDED** by `DNS_CUTOVER_EVOLUTION_AAR_134k.md` — the bearDog-on-:443
> architecture described here was rolled back in 134j due to subdomain routing
> collapse. Caddy is now the TLS front door on :443 for all domains.
> See 134k for the full divergence catalog and current production topology.

**Date**: Jul 9, 2026
**Operator**: sporeGate (Cursor agent)
**Duration**: ~45 minutes

## Objective

Migrate `primals.eco` from GitHub Pages to sovereign infrastructure on `golgi`,
with bearDog providing ACME TLS on :443 and Caddy handling remaining subdomains
on :8443.

## Execution Summary

### Phase 1: DNS Cutover (Caddy-first validation)

1. **Cloudflare DNS changes** (user):
   - Deleted 4 GitHub Pages A records (185.199.x.x)
   - Added `primals.eco` A → [RELAY_PUBLIC] (DNS-only)
   - Deleted `www.primals.eco` Tunnel record
   - Added `www.primals.eco` CNAME → `primals.eco` (DNS-only)

2. **DNS propagation**: Verified via Google DNS (8.8.8.8) — clean IPv4, no stale AAAA.

3. **Caddy ACME**: Initial Let's Encrypt attempts failed because the ACME
   validator resolved IPv6 to stale Cloudflare addresses. Caddy restart after
   AAAA TTL expiry resolved it — HTTP-01 challenges passed, cert issued.

4. **Phase 1 result**: `primals.eco` sovereign on Caddy with Let's Encrypt cert.

### Phase 2: bearDog TLS Swap

1. **bearDog binary deployed** to `/opt/membrane/beardog` on golgi.

2. **beardog-sporeprint.service** created with:
   - `BEARDOG_GATEHOUSE_MODE=true`
   - `BEARDOG_ACME_DOMAINS=primals.eco,www.primals.eco`
   - `BEARDOG_ACME_EMAIL=ops@primals.eco`
   - `BEARDOG_GATEWAY_UPSTREAM=127.0.0.1:8090`
   - `BEARDOG_DATA_DIR=/var/lib/beardog`

3. **CSR SAN bug fixed** (beardog-acme): `build_csr()` only set CN, not SAN
   extensions. ACME finalization failed with "CSR does not specify same
   identifiers as Order". Fixed by adding `SubjectAltName` with all configured
   domains. Binary rebuilt and redeployed.

4. **Caddy reconfigured** to `:8443`/`:8880`, removed `primals.eco` and
   `www.primals.eco` blocks, added explicit cert paths from `/caddy/certificates/`.

5. **Swap sequence**: Stop Caddy → Start bearDog (ACME cert issued in ~4s) →
   Start Caddy on new ports.

6. **UFW updated**: Port 8443/tcp opened for Caddy subdomain access.

## Final Architecture

```
Internet → DNS (primals.eco → [RELAY_PUBLIC])
  :443  → bearDog (ACME TLS) → Caddy :8091 (sporePrint static files)
  :80   → bearDog (HTTP-01 + HTTPS redirect)
  :8443 → Caddy (membrane/git/lab subdomains, existing LE certs)
  :3000 → Forgejo (via Caddy reverse proxy on :8443)
```

## Validation Results

| Endpoint | Status | Details |
|----------|--------|---------|
| `https://primals.eco` | 200 | bearDog TLS, LE cert (YE2), SAN: primals.eco + www |
| `http://primals.eco` | 301 → https | bearDog HTTP redirect |
| `https://www.primals.eco` | 200 | Same content (no Host routing in bearDog) |
| `https://membrane.primals.eco:8443/health` | 200 | Caddy, LE cert (E8) |
| `https://git.primals.eco:8443` | 200 | Caddy → Forgejo |

## Bug Fix: beardog-acme CSR SAN

**File**: `crates/beardog-acme/src/client/issuance.rs`
**Issue**: `build_csr()` constructed a PKCS#10 CSR with only `CN=<primary_domain>`
but no SubjectAltName extension. Multi-domain ACME orders require all identifiers
as SANs in the CSR.
**Fix**: Added `SubjectAltName` extension with `GeneralName::DnsName` for each
configured domain.

## Divergences from Plan

1. **Port 8080 conflict**: songBird already uses :8080. Changed Caddy HTTP port
   to :8880.
2. **`BEARDOG_DATA_DIR`** needed: bearDog requires this env var to store ACME
   data when HOME is not set.
3. **Caddy storage path**: Needed explicit `storage file_system /caddy` and
   `tls <cert> <key>` directives because Caddy won't serve existing certs
   without explicit paths when ACME renewal fails.
4. **www.primals.eco**: Serves 200 (same content) instead of 301 redirect.
   bearDog's TCP proxy has no Host-header routing. Acceptable — both URLs serve
   sporePrint.

## Post-cutover Fix: petalTongue vs sporePrint

After initial deployment, `primals.eco` showed the petalTongue dashboard
instead of the sporePrint website. Root cause: the plan assumed petalTongue
(:8090) served sporePrint static content, but petalTongue serves its own
dashboard. Caddy was always the sporePrint file server.

**Fix**: Added Caddy `:8091` server block serving `/opt/ecoPrimals/sporePrint/public`,
changed `BEARDOG_GATEWAY_UPSTREAM` from `:8090` to `:8091`.

## Remaining Items

- bearDog Host-header routing would allow all domains on :443 (eliminate :8443)
- Caddy cert renewal blocked (bearDog owns :80) — existing certs valid until Aug 13
- Cert renewal strategy before Aug 13: either add DNS-01 support to bearDog, or
  temporarily stop bearDog to let Caddy renew via HTTP-01

## Files Modified

- `provision-golgi.sh` — Updated Caddyfile, added beardog-sporeprint.service,
  UFW port 8443
- `crates/beardog-acme/src/client/issuance.rs` — SAN extension in CSR builder

## Services on golgi

| Service | Port | Status |
|---------|------|--------|
| `beardog-sporeprint` | :443, :80 | active |
| `caddy-tls` | :8443, :8880 | active |
| `forgejo` | :3000 (SSH :2222) | active |
| `petaltongue-sporeprint` | :8090 | active |
