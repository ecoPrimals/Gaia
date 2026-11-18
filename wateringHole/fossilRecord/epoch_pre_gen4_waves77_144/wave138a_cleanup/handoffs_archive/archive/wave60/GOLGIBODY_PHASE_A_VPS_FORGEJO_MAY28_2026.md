# golgiBody Phase A — VPS Forgejo Deployment

**Date:** 2026-05-28 (Wave 60)
**Status:** Forgejo installed, Caddy configured, awaiting DNS cutover
**VPS:** [RELAY_PUBLIC] (membrane-relay, cellMembrane fieldMouse)

## What happened

Forgejo v15.0.2 has been installed on the cellMembrane VPS as the
**golgiBody** — a periplasmic git surface that makes `git.primals.eco`
gate-agnostic. Previously, Forgejo ran only on ironGate behind a Cloudflare
tunnel, making it a plasma membrane appendage of one gate. Now the
peptidoglycan layer is unified: any gate can push/pull through the VPS
without hairpinning through Cloudflare.

## What's deployed on VPS

- **Forgejo v15.0.2** — `/usr/local/bin/forgejo`, runs as `git` user
- **Data:** `/opt/forgejo/data/` (SQLite, repositories)
- **Config:** `/opt/forgejo/custom/conf/app.ini`
- **Service:** `forgejo.service` (systemd, enabled)
- **HTTP:** `127.0.0.1:3000` (Caddy-fronted at `git.primals.eco`)
- **SSH:** `0.0.0.0:2222` (direct, UFW allowed)
- **Orgs:** `ecoPrimals`, `syntheticChemistry`, `sporeGarden`
- **Admin:** `golgiAdmin` (API token at `/opt/forgejo/.api_token`)
- **Memory:** ~109MB RSS (VPS has 1.4GB available after)

## Caddy config

`git.primals.eco` block added to `/etc/membrane/Caddyfile` (SSOT in
`infra/plasmidBin/membrane/Caddyfile`):

```caddy
git.primals.eco {
    reverse_proxy localhost:3000
}
```

## DNS cutover needed

`git.primals.eco` currently points at a Cloudflare tunnel (CNAME to
ironGate's cloudflared). To complete Phase A:

1. In Cloudflare dashboard for `primals.eco`:
   - **Delete** the existing `git` CNAME record
   - **Create** A record: `git` → `[RELAY_PUBLIC]` (DNS only / grey cloud)
2. Caddy will auto-obtain Let's Encrypt cert via ACME
3. Verify: `curl -I https://git.primals.eco/` should return Forgejo response

## Repo seeding needed

After DNS cutover, seed repos from ironGate:

```bash
# On ironGate:
FORGEJO_URL=https://git.primals.eco FORGEJO_TOKEN=<vps-token> \
  bash gardens/projectNUCLEUS/deploy/forgejo_mirror.sh
```

Or push each repo individually via `git push forgejo main` — the SSH
remotes (`ssh://git@git.primals.eco:2222/org/repo.git`) will resolve to
the VPS once DNS flips.

## K-Derm framing

**golgiBody** is a deployment role on the VPS fieldMouse substrate. Like
the biological Golgi apparatus, it packages (Forgejo repos), routes (Caddy
TLS), and modifies (post-receive hooks) between cytoplasms and the
extracellular surface. This is Phase A; future phases add bearDog vault
for token distribution (Phase B) and full golgiBody NUCLEUS with
inter-membrane negotiation (Phase C).

## Files modified

- `infra/plasmidBin/membrane/Caddyfile` — added `git.primals.eco` block
- `infra/wateringHole/ecosystem_manifest.toml` — `forgejo_host = "vps"`
- `gardens/cellMembrane/membrane.toml` — added `[membrane.channels.surface.git]`
- `gardens/cellMembrane/VPS_STATE.md` — Forgejo in service list + UFW
- `gardens/projectNUCLEUS/deploy/routing_config.toml` — git routes to `vps_local`
