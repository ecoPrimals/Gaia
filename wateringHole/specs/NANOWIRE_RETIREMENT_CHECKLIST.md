# NanoWire / SSH Retirement Checklist — Inner Membrane Evolution

**Date**: Aug 12, 2026 | **Wave**: 157j | **From**: sporeGate topology team
**Owner**: sporeGate ops
**Status**: AUDIT COMPLETE — 18 files with live SSH shell-out, 0 rsync

---

## Architecture Goal

Gate enrollment and cascade flows move from SSH/SCP dispatch to pure primal
compositions on the inner membrane (primal.eco) via Tower Atomic mesh:

```
CURRENT:  sporeGate --SSH--> remote gate --run commands-->
TARGET:   sporeGate --songBird mesh--> capability.call --> remote gate handles locally
```

primals.eco (outer membrane) remains pull-only: depot, docs, Forgejo.
primal.eco (inner membrane) becomes the live mesh: enrollment, cascade, config push.
nestgate.io (peptidoglycan) bridges them: CAS, provenance, fossilized history.

---

## Central Choke Point

All SSH/SCP in membrane-shadow funnels through `ssh.rs`:

| Function | Purpose | Replacement |
|----------|---------|-------------|
| `exec` | SSH to `config.ssh_host` (golgi) | songBird `capability.call` to gate |
| `exec_raw_on` | SSH to arbitrary host | songBird `mesh.dispatch` |
| `scp_to` / `scp_to_host` | File transfer via SCP | mesh file relay or HTTPS depot pull |
| `cat_remote` | Binary download via SSH cat | HTTPS depot (`FetchSource::Wan`) |
| `exec_on_host` | SSH as user@host (provisioning) | gate self-bootstrap from depot |

---

## Retirement Priority — Ordered by Dependency

### Tier 1: Already Mesh-Native (no SSH)

These paths have been replaced and SSH code is dead or deprecated:

| Path | Status | Replacement | Wave |
|------|--------|-------------|------|
| Sub-builder CI dispatch | **RETIRED** | Tower Atomic TCP JSON-RPC (`builder.serve` :9800) — riboCipher framed, `call_tcp` transport. ironGate (systemd) + blueGate (WMI/scheduled task). `builder_host`/`builder_port` in ecosystem_manifest.toml. | 157k |
| Forgejo repo/mirror API | **HTTP** | REST API via Forgejo token | 157e |
| `plasmid.fetch --source wan` | **HTTP** | HTTPS depot.primals.eco | 156d |
| Neural Bridge delegation | **LIVE** | `gate.info/pull/check/service.*` bridge to biomeOS | 157g |

**Graduation Template**: `builder.serve` established the pattern for all remaining SSH retirements:
1. TCP listener on well-known port with riboCipher signal detection
2. JSON-RPC method dispatch (same framing as UDS primal sockets)
3. `call_tcp` from foreman (same as `call_endpoint` for any `TransportEndpoint::Tcp`)
4. Manifest-driven endpoint resolution (`builder_host`/`builder_port` in ecosystem_manifest.toml)
5. Extend with new capabilities (`depot.receive`, `depot.cas_push`, `service.status`) on same port

### Tier 2: High-Value Retirements (blocks cascade autonomy)

| # | Path | File | SSH Action | Mesh Replacement |
|---|------|------|------------|------------------|
| R-01 | `gate.pull` | `gate/mod.rs:203` | SSH into gate, run cascade | cascade.notify gossip → gate pulls autonomously |
| R-02 | `gate.check` | `gate/mod.rs:213` | SSH into gate, run parity check | mesh `cascade.status` RPC |
| R-03 | `gate.info` | `gate/mod.rs:139` | SSH multi-line system probe | mesh `gate.info` capability |
| R-04 | `plasmid.trigger` | `plasmid/commands.rs:128` | SSH systemctl start pipeline | mesh `plasmid.pipeline` RPC |
| R-05 | `service.*` | `service.rs:44-121` | SSH systemctl list/status/restart/logs | mesh `service.*` capability |

### Tier 3: Depot Push (blocks fleet parity)

| # | Path | File | SSH Action | Mesh Replacement |
|---|------|------|------------|------------------|
| R-06 | `depot_sync --push` | `plasmid/depot_sync.rs:313-393` | SCP binary + atomic mv | mesh file relay or HTTPS PUT |
| R-07 | `depot metadata push` | `plasmid/depot_sync.rs:437` | SCP checksums/signatures | HTTPS depot API |
| R-08 | `plasmid.refresh` | `plasmid/refresh.rs:236-276` | SCP binary, chmod, restart | mesh `plasmid.deploy` capability |

### Tier 4: Caddy / TLS (blocks gateway migration)

| # | Path | File | SSH Action | Mesh Replacement |
|---|------|------|------------|------------------|
| R-09 | `caddy.status/reload/validate` | `caddy/mod.rs` | SSH admin API | gateway module (Wave 132 deprecation) |
| R-10 | `caddy.tls.*` | `caddy/tls.rs` | SSH openssl/curl | gateway TLS probe |
| R-11 | `caddy.depot.*` | `caddy/depot.rs` | SSH sed/inject Caddyfile | gateway config API |

### Tier 5: Enrollment / Provisioning (blocks autonomous enrollment)

| # | Path | File | SSH Action | Mesh Replacement |
|---|------|------|------------|------------------|
| R-12 | `gate.enroll` hub peer | `gate/enroll.rs:290` | SSH `wg set` on hub | mesh peer registration API |
| R-13 | `gate.provision bootstrap` | `provision/bootstrap.rs` | Full droplet lifecycle SSH/SCP | cloud-init + depot pull + mesh join |
| R-14 | `gate.validate` | `dispatch_validate.rs:71-141` | SSH multi-check probe | mesh composition probe API |
| R-15 | `forgejo token.*` | `forgejo/mod.rs:301-365` | SSH sqlite3/CLI on golgi | Forgejo REST API (token endpoints exist) |

### Tier 6: Relay / Mirror (blocks full sovereignty)

| # | Path | File | SSH Action | Mesh Replacement |
|---|------|------|------------|------------------|
| R-16 | `relay.ship` | `relay.rs:451` | SSH git ops on golgi-ext | local git push or mesh git proxy |
| R-17 | `relay.status` | `relay_dispatch.rs:189` | SSH connectivity check | mesh reachability probe |

### Tier 7: Git Transport (gradual, lowest priority)

| # | Path | File | SSH Action | Mesh Replacement |
|---|------|------|------------|------------------|
| R-18 | `GIT_SSH_COMMAND` | `git_ops.rs:250-257` | All git push/pull via SSH | Forgejo HTTPS tokens |
| R-19 | `git ls-remote ssh://` | `plasmid/drift.rs:46,80` | Drift detection | Forgejo API `/repos/.../git/refs` |

---

## Shadow Validation Strategy

The `tower.shadow` module already compares WG vs Tower transport for each gate pair.
Retirement follows the same pattern:

1. Add `--mesh` flag to each command (R-01 through R-19)
2. Both SSH and mesh paths run during shadow period
3. Compare results — mesh must match SSH output
4. Once shadow passes, SSH path becomes `--legacy` fallback
5. After one full wave with no `--legacy` usage, remove SSH code

---

## Files to Modify (Summary)

| File | SSH call sites | Priority |
|------|---------------|----------|
| `ssh.rs` | All primitives (9 functions) | Transport layer — last to remove |
| `gate/mod.rs` | info, pull, check | Tier 2 |
| `service.rs` | list, status, restart, logs | Tier 2 |
| `plasmid/commands.rs` | trigger | Tier 2 |
| `plasmid/depot_sync.rs` | push, sync, metadata | Tier 3 |
| `plasmid/refresh.rs` | refresh_one, sync_depot | Tier 3 |
| `caddy/mod.rs` | status, vhosts, reload, validate | Tier 4 |
| `caddy/tls.rs` | tls_check, tls_external | Tier 4 |
| `caddy/depot.rs` | depot_provision | Tier 4 |
| `gate/enroll.rs` | hub_peer_phase | Tier 5 |
| `provision/bootstrap.rs` | full bootstrap chain | Tier 5 |
| `dispatch/dispatch_validate.rs` | gate_validate | Tier 5 |
| `forgejo/mod.rs` | token_list/create/revoke | Tier 5 |
| `relay.rs` | ship_one_repo | Tier 6 |
| `dispatch/relay_dispatch.rs` | relay.status | Tier 6 |
| `git_ops.rs` | GIT_SSH_COMMAND | Tier 7 |
| `plasmid/drift.rs` | ls-remote | Tier 7 |
| `manifest/types.rs` | SubBuilderEntry.ssh_host (deprecated field) | Schema cleanup |

---

## NanoWire Status

- Zero live NanoWire code paths — only 2 comment references remain
- Sub-builder dispatch fully migrated to mesh JSON-RPC (`builder.serve`)
- `SubBuilderEntry.ssh_host` field marked deprecated in schema
- No `rsync` invocations exist (comments only)

---

## Immediate Actions (Wave 157j)

1. [x] Audit complete — this checklist
2. [ ] Wire `cascade.notify` gossip event (enables R-01, R-02)
3. [ ] Add LAN IPs to dnsmasq (enables LAN inner membrane without WG)
4. [ ] Begin nestgate.io Phase 2 depot/provenance routes
