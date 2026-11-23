<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# SporePrint Webhook Pattern — Sovereign Notification

**Date**: May 28, 2026 (Wave 59)
**Status**: Shadow — running alongside GitHub Actions `notify-sporeprint.yml`
**Owner**: primalSpring coordination
**Replaces**: `.github/workflows/notify-sporeprint.yml` (GitHub Actions repository_dispatch)

---

## Problem

Every repo that publishes content to sporePrint uses a GitHub Actions
workflow (`notify-sporeprint.yml`) that fires `repository_dispatch` to
`ecoPrimals/sporePrint`. This is a wire to the outer membrane — it
requires a GitHub PAT (`SPOREPRINT_DISPATCH_TOKEN`) and GitHub Actions
runner availability.

## Sovereign Alternative

Forgejo supports webhooks natively. When a repo is pushed to Forgejo
(either directly or via pull mirror sync), Forgejo fires a webhook
that triggers sporePrint refresh on the VPS.

### Architecture

```
Push to repo (any gate)
  → GitHub receives push (current primary)
  → Forgejo pull mirror syncs (8h or on-demand)
  → Forgejo post-receive webhook fires
  → POST to VPS NestGate endpoint
  → NestGate triggers sporePrint rebuild (zola build + deploy)
```

### Forgejo Webhook Configuration

For each repo that publishes to sporePrint, add a Forgejo webhook:

```
URL:          https://membrane.primals.eco/hooks/sporeprint-refresh
HTTP Method:  POST
Content Type: application/json
Secret:       <shared HMAC secret in /etc/membrane/webhook_secrets.env>
Trigger On:   Push events (branch: main)
Active:       Yes
```

Payload sent by Forgejo (standard push event):

```json
{
  "ref": "refs/heads/main",
  "repository": {
    "name": "primalSpring",
    "full_name": "syntheticChemistry/primalSpring"
  },
  "after": "<commit-sha>"
}
```

### VPS Receiver (NestGate endpoint)

The VPS runs a lightweight webhook receiver (Caddy route → script):

```
# /etc/caddy/Caddyfile snippet
handle /hooks/sporeprint-refresh {
    reverse_proxy unix//run/membrane/nestgate.sock
}
```

NestGate processes the webhook and triggers:

```bash
#!/usr/bin/env bash
# /opt/ecoPrimals/hooks/sporeprint-refresh.sh
cd /opt/ecoPrimals/sporePrint
git pull --ff-only origin main
zola build --output-dir /var/www/primals.eco/public
echo "sporePrint refreshed at $(date -Iseconds)"
```

### Shadow Period Protocol

1. **Both active**: GitHub Actions workflow AND Forgejo webhook run simultaneously
2. **Validate**: Confirm sporePrint refreshes correctly via webhook alone
3. **Cutover**: Remove `notify-sporeprint.yml` from repos (archive to fossilRecord)
4. **Cleanup**: Revoke `SPOREPRINT_DISPATCH_TOKEN` GitHub PAT

### Repos Using This Pattern

| Repo | Has `notify-sporeprint.yml` | Has Forgejo webhook |
|------|----------------------------|---------------------|
| primalSpring | Yes | **Pending** |
| hotSpring | Yes | Pending |
| wetSpring | Yes | Pending |
| (other springs) | Yes | Pending |

### Migration Checklist (per repo)

- [ ] Verify repo is synced to Forgejo (check `forgejo_pull_mirror.sh --status`)
- [ ] Add Forgejo webhook for `sporeprint-refresh`
- [ ] Validate sporePrint refresh triggers from Forgejo push event
- [ ] Add `POSTPRIMORDIAL STATUS: Shadow` comment to GitHub Actions workflow
- [ ] After 7-day shadow validation: archive GitHub Actions workflow

---

## Cross-References

- `SOVEREIGNTY_STANDARDS.md` — CI sovereignty section
- `REPO_MEMBRANE_BOUNDARY.md` — Forgejo sync model
- `cellMembrane/Caddyfile` — VPS reverse proxy configuration
- `primalSpring/.github/workflows/notify-sporeprint.yml` — Current workflow
