# ironGate PostPrimordial Ops — Remaining Items

**Date:** 2026-05-28 (Wave 60)
**From:** eastGate (primalSpring)
**To:** ironGate (projectNUCLEUS / cellMembrane)

---

## Context

eastGate has completed VPS sync validation. WaterFall Phase 3 result: **33/36 repos pull cleanly from sovereign Forgejo**. The following items need ironGate action to complete the postPrimordial niche.

---

## 1. Fix observer-static + pappusCast Unit Files (P0)

Both services crash-loop because systemd unit paths still reference `sporeGarden/projectNUCLEUS` instead of `gardens/projectNUCLEUS`.

```bash
# Fix both unit files
sudo sed -i 's|sporeGarden/projectNUCLEUS|gardens/projectNUCLEUS|g' \
  /etc/systemd/system/observer-static.service \
  /etc/systemd/system/pappusCast.service

sudo systemctl daemon-reload
sudo systemctl restart observer-static pappusCast

# Verify
systemctl status observer-static pappusCast --no-pager
curl -sf http://localhost:8866/ | head -5
```

---

## 2. Set Up pappusCast rsync to VPS (P1)

VPS Caddy now serves `lab.primals.eco` static content from `/var/cache/membrane/lab/` (currently empty). pappusCast needs to push rendered HTML there.

```bash
# One-shot sync (run from ironGate after pappusCast is healthy)
rsync -avz --delete \
  "$ABG_SHARED/public/.pappusCast/html_export/" \
  root@[RELAY_PUBLIC]:/var/cache/membrane/lab/

# Verify VPS has content
ssh root@[RELAY_PUBLIC] 'ls -la /var/cache/membrane/lab/'
curl -sf https://lab.primals.eco/ | head -5
```

For ongoing sync, add to pappusCast's post-export hook or set up a cron:

```bash
# /etc/cron.d/pappuscast-vps-sync
*/15 * * * * root rsync -avz --delete /path/to/.pappusCast/html_export/ root@[RELAY_PUBLIC]:/var/cache/membrane/lab/ 2>&1 | logger -t pappuscast-sync
```

---

## 3. Remove git.primals.eco from Cloudflare Tunnel (P2)

`git.primals.eco` is now served directly by VPS Caddy (golgiBody Phase A). Remove the stale tunnel route:

```bash
# In deploy/cloudflared/config-full.yml, remove:
#   - hostname: git.primals.eco
#     service: http://127.0.0.1:3000

# Restart cloudflared to apply
sudo systemctl restart cloudflared
```

Keep `lab.primals.eco` tunnel routes alive until BTSP relay replaces them for JupyterHub interactive paths.

---

## 4. Forgejo Repo Fixes (P2)

Two repos need attention on VPS Forgejo:

### 4a. Seed rustChip

rustChip was not included in the original 34-repo seeding. Create and push:

```bash
# Create repo on Forgejo
FORGEJO_TOKEN=$(cat /opt/forgejo/.api_token)
curl -sf -X POST "https://git.primals.eco/api/v1/orgs/syntheticChemistry/repos" \
  -H "Authorization: token $FORGEJO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"rustChip","default_branch":"main"}'

# Push from local
cd $ECOPRIMALS_ROOT/infra/rustChip
git push forgejo main
```

### 4b. Rename toadStool default branch

toadStool was mirrored with `master` as default, but all gates use `main`:

```bash
# Option A: Push main branch and update default
cd $ECOPRIMALS_ROOT/primals/toadStool
git push forgejo main

# Then via API, set default branch to main
FORGEJO_TOKEN=$(cat /opt/forgejo/.api_token)
curl -sf -X PATCH "https://git.primals.eco/api/v1/repos/ecoPrimals/toadStool" \
  -H "Authorization: token $FORGEJO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"default_branch":"main"}'
```

---

## 5. Caddyfile Update — Already Deployed

The VPS Caddyfile has been updated. Interactive lab routes (`/hub/*`, `/user/*`, `/api/*`, `/services/*`) now return a 503 explaining JupyterHub is gate-local until BTSP relay is ready. Static content serves from `/var/cache/membrane/lab/`.

No action needed on ironGate for this — just the rsync in item 2.

---

## 6. DNS Sovereignty — Zone Updated

`lab.primals.eco` and `git.primals.eco` A records have been added to the VPS knot-dns zone, both pointing to [RELAY_PUBLIC]. DNSSEC-signed and verified. These will resolve correctly once the NS registrar cutover happens.

**Registrar NS cutover** remains an external action item.

---

## WaterFall Shadow Status

eastGate validated `cascade-pull.sh --source forgejo` on all 36 repos:

| Status | Count | Details |
|--------|-------|---------|
| CURRENT | 32 | Synced cleanly from sovereign Forgejo |
| UPDATED | 1 | projectNUCLEUS (pulled ironGate's new commits) |
| FAILED | 2 | rustChip (not seeded), toadStool (master/main mismatch) |
| EMPTY | 1 | blueFish (no commits yet) |

Once items 4a and 4b are resolved, WaterFall Phase 3 shadow period can begin formally across all gates.

---

*Wave 60. PostPrimordial niche tightening. 33/36 sovereign sync validated.*
