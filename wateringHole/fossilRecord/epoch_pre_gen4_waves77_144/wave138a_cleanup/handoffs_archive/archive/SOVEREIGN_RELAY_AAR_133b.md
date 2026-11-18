# AAR: Sovereign Relay Architecture — golgi as Thin Edge

**Wave**: 133b
**Gate**: sporeGate (executing), golgi (target)
**Date**: 2026-07-06
**Status**: COMPLETE

---

## Objective

Invert the golgi/sporeGate relationship: sporeGate becomes the sovereign warehouse (full git repos, CI builds, 812GB headroom), golgi becomes a thin, image-reproducible edge relay. Pepti depot remains the canonical deployment surface.

## Results

| Step | Before | After | Delta |
|------|--------|-------|-------|
| Forgejo GC | 3.9G repos | 3.8G repos | -120M |
| Service prune | 14 primals + bridges + RustDesk | 5 relay services | -19 units |
| Binary cleanup | 381M in /opt/membrane | 90M (relay only) | -291M |
| Shallow clones | 256M /opt/ecoPrimals/primals/ | 0 (removed) | -264M |
| sporeGate mirror | 0 | 3.7G /opt/forgejo-mirror (39 repos) | +3.7G on 809GB free |
| Provision script | none | wateringHole/provision/provision-golgi.sh | reproducible |
| **golgi disk** | **7.3G used / 2.4G free (75%)** | **7.1G used / 2.2G free (77%)** | **net ~200M freed** |

### Note on Disk Recovery

The projected -2.3G was partially offset by:
- Aggressive GC failed on 2GB RAM (OOM on bearDog 982M repo) — only regular GC ran
- Cascade timer ran a harvest cycle during GC, temporarily consuming 248M in /tmp/membrane-harvest (cleaned)
- Forgejo repos are already efficiently packed at ~3.8G

The more impactful gains are operational: 19 fewer attack-surface services, zero working copies to maintain, and full image reproducibility.

## Services Retained on golgi (Relay Only)

| Service | Purpose |
|---------|---------|
| forgejo.service | Sovereign git forge, SSH :2222, HTTP :3000 |
| caddy-tls.service | TLS termination, ACME, depot file_server, reverse proxy |
| beardog-membrane.service | Crypto identity, BTSP security provider |
| songbird-membrane.service | Mesh federation hub, dark-forest mode |
| songbird-relay.service | TURN relay :3478 for NAT traversal |
| cascade-sense.timer | 15min cascade + freshness publish |
| fail2ban.service | SSH brute-force protection |
| knot.service | DNS server |

## Services Stopped + Disabled

barracuda, biomeos, coralreef, loamspine, nestgate, petaltongue, rhizocrypt, skunkbat, squirrel, sweetgrass, toadstool (11 primals), membrane-bridge-beardog, membrane-bridge-biomeos, membrane-bridge-forgejo (3 bridges), hbbs-membrane, hbbr-membrane (RustDesk), s1-tls-gate, s4-auth-gate, plasmid-pipeline (3 timers).

## Code Change: `cellMembrane` — Bare Repo Freshness Fallback

**File**: `crates/membrane-shadow/src/freshness.rs`
**Commit**: pending (this AAR)

Added `resolve_repo_head()` with 3-tier resolution:
1. Working copy (`repo_dir/.git` exists) — standard gate behavior
2. Bare repo at local_path (`repo_dir/HEAD + objects` exists) — for future local bare repos
3. Forgejo bare repo fallback (`FORGEJO_REPO_ROOT/<org>/<name>.git`) — for thin relays

This allows `publish_gate_heads()` to populate HEADs on gates that have no source clones — they read directly from Forgejo's repository storage. Controlled via `FORGEJO_REPO_ROOT` env var in cascade-sense.service.

### Bug Found During Implementation

`GATE_NAME` was set to `golgi` on the VPS, but the ecosystem manifest uses `golgiBody` as the gate profile name. This caused `gate_repos("golgi")` to return 0 repos and publish empty heads. Fixed by correcting both the systemd env var and `/etc/membrane/gate-name` to `golgiBody`.

## Sovereign Warehouse: sporeGate

- **Mirror location**: `/opt/forgejo-mirror/` — 39 bare repos, 3.7G total
- **Mirror command**: `git clone --mirror ssh://git@10.13.37.1:2222/<org>/<name>.git`
- **Refresh**: `git -C /opt/forgejo-mirror/<org>/<name>.git fetch --all --prune`
- **Recovery**: If golgi dies, rsync mirror + depot to new droplet, run `provision-golgi.sh`

## Provision Script

`wateringHole/provision/provision-golgi.sh` — full droplet rebuild covering:
- System packages (wireguard, fail2ban, git, rsync, socat)
- Forgejo install + app.ini
- Caddy install + Caddyfile
- All 7 systemd units (forgejo, caddy, beardog, songbird x2, cascade service+timer)
- WireGuard template
- UFW firewall rules
- Recovery steps (rsync from sporeGate)

## Upstream Divergences for Team Review

### DIV-RELAY-01: Forgejo GC on Constrained Hosts (P2)
`git gc --aggressive` OOMs on 2GB RAM with repos >500M. Need either:
- Scheduled GC with `pack.windowMemory` limits
- Or accept regular GC (~3% savings) on small VPS

### DIV-RELAY-02: Gate Name Consistency (P1)
The ecosystem manifest uses `golgiBody` but several places used `golgi`. The `GATE_NAME` env var, `/etc/membrane/gate-name` file, and systemd units must all match the manifest's `[gates.<name>]` key exactly. This should be validated by `membrane shadow validate`.

### DIV-RELAY-03: Harvest on Relay Gates (P2)
The cascade timer on golgi ran a harvest phase (building binaries in /tmp/membrane-harvest) even though golgi is a relay, not a build host. `temporal.cascade` should detect relay-only gates and skip harvest. Alternatively, the cascade-sense.service should pass `--no-harvest` (if supported) or the manifest should mark gates as `composition = "relay"` to suppress build phases.

### DIV-RELAY-04: Binary Path Duplication (P3)
Some services reference `/opt/membrane/<binary>` while newer deploys go to `/usr/local/bin/<binary>`. The provision script standardizes on `/opt/membrane/` for relay binaries and `/usr/local/bin/` for membrane CLI + forgejo. This should be formalized in the deployment tooling.

## Pattern for New NUC Spin-Up

This implementation establishes a repeatable pattern for onboarding new gates:

1. **Define gate profile** in `ecosystem_manifest.toml` under `[gates.<name>]`
2. **Set `GATE_NAME`** consistently in systemd units, `/etc/membrane/gate-name`
3. **Choose composition**: `full` (builds + serves) or `relay` (sync + serve only)
4. **For relay gates**: set `FORGEJO_REPO_ROOT` to point at local Forgejo bare repos
5. **For warehouse gates**: `git clone --mirror` all repos, run CI builds
6. **Create provision script**: document all packages, configs, units, and recovery steps
7. **Validate**: `membrane shadow validate` should check gate name, service status, heads freshness

### primalSpring Resilience Testing

This pattern should be added to `primalSpring` resilience testing for `cellMembrane` topology:

- **Test: relay-gate freshness** — verify `publish_gate_heads()` populates from bare repos when `FORGEJO_REPO_ROOT` is set and no working copies exist
- **Test: gate name resolution** — verify `resolve_gate_name()` returns the manifest-matching name from env, file, and hostname fallback
- **Test: provision idempotency** — run `provision-golgi.sh` twice on same host, verify no errors
- **Test: mirror freshness** — after sporeGate `fetch --all`, verify HEADs match golgi's Forgejo
- **Test: cascade without harvest** — relay gates should complete cascade + freshness without attempting builds
