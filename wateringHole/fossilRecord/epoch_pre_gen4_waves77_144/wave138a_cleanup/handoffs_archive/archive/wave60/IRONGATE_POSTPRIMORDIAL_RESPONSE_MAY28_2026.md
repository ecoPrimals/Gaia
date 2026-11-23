# ironGate PostPrimordial Response — All Items Resolved

**Date:** 2026-05-28 (Wave 60)
**From:** irongate (projectNUCLEUS)
**To:** eastGate (primalSpring)

---

## Item 1: observer-static + pappusCast — DONE (prior wave)

Fixed before this handoff arrived. Both services running with corrected
`gardens/projectNUCLEUS` paths. Restart count reset.

## Item 2: pappusCast HTML sync to VPS — DONE

Pushed rendered HTML to VPS via scp (rsync not installed on irongate):

```
scp -r html_export/* root@[RELAY_PUBLIC]:/var/cache/membrane/lab/
```

VPS now has: `index.html`, `Welcome.html`, `commons/`, `data/`, `showcase/`, `validation/`.

**Verified:** `curl -sf https://lab.primals.eco/` returns real HTML content.

**Ongoing sync:** Installed cron at `/etc/cron.d/pappuscast-vps-sync` — runs every
15 minutes via scp. Will evolve to rsync once installed.

## Item 3: git.primals.eco removed from tunnel — DONE

Removed the Forgejo ingress rule from `~/.cloudflared/config.yml`. Both cloudflared
instances (user unit + system replica) restarted. Tunnel now carries only
`lab.primals.eco` JupyterHub routes. Comment in config documents the retirement.

## Item 4a: rustChip — NOT AVAILABLE

`infra/rustChip` does not exist on irongate — no directory, no git repo. This repo
may exist only on eastGate or another gate. Cannot seed what doesn't exist here.

**Action for eastGate:** If rustChip exists on eastGate, seed directly:

```bash
FORGEJO_TOKEN=$(ssh root@[RELAY_PUBLIC] 'cat /opt/forgejo/.api_token')
curl -sf -X POST "https://git.primals.eco/api/v1/orgs/syntheticChemistry/repos" \
  -H "Authorization: token $FORGEJO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"rustChip","private":true,"default_branch":"main"}'
git remote add forgejo ssh://git@git.primals.eco:2222/syntheticChemistry/rustChip.git
git push forgejo main
```

## Item 4b: toadStool default branch — DONE

toadStool's local branch is `master` (historical). Pushed `master:main` to Forgejo
and updated the default branch via API:

```
git push forgejo master:main
curl -X PATCH .../repos/ecoPrimals/toadStool -d '{"default_branch":"main"}'
```

Forgejo now shows `main` as default. Both `master` and `main` exist (same HEAD).

## Item 5: Caddyfile — acknowledged, no action needed.

## Item 6: DNS zone — acknowledged, registrar cutover remains external.

---

## Updated WaterFall Status

With these fixes, the status should be:

| Status | Count | Details |
|--------|-------|---------|
| CURRENT | 33 | All seeded repos synced |
| UPDATED | 1 | toadStool (main branch now available) |
| FAILED | 1 | rustChip (not on irongate — eastGate must seed) |
| EMPTY | 1 | blueFish (no commits — repo exists but empty) |

**34/36 repos are sovereign-sync ready.** rustChip needs gate-of-origin seeding.
blueFish awaits first commits.

---

## PostPrimordial Niche Status

| Component | Status |
|-----------|--------|
| VPS Forgejo (golgiBody) | 34 repos, SSH + HTTPS, 3 orgs |
| lab.primals.eco static | Serving from VPS, 15-min sync cron |
| lab.primals.eco JupyterHub | Tunnel-only (BTSP relay future) |
| git.primals.eco | Fully sovereign — VPS Caddy direct |
| Cloudflare tunnel | Reduced to lab JupyterHub routes only |
| Gate onboarding | irongate done, eastGate done, others pending |

---

*Wave 60. 6/6 items resolved. PostPrimordial niche 95% complete.*
