# AAR: Wave 107 — Mobile Golgi NUC Fleet Infrastructure

**Date**: 2026-06-10
**From**: cellMembrane + ironGate team
**Scope**: Deployment infrastructure for portable NUCLEUS gates (NUCs) that mirror the VPS mesh
**Purpose**: Enable 2-3 mobile NUCs as full NUCLEUS gates — mesh anywhere, LAN auto-peer when colocated

---

## What Was Built

### 1. GateMobility Type (`cellmembrane-types`)

```toml
# membrane.toml
[membrane.identity]
family_id = "eco"
gate_id = "golgiAlpha"
mobility = "mobile"  # or "fixed" (default)
```

- `GateMobility::Fixed` — stable location, persistent mesh anchor
- `GateMobility::Mobile` — portable, needs reconnect hook on network changes
- Methods: `needs_reconnect_hook()`, `is_mesh_anchor()`, `Display`

### 2. gate.bootstrap --mobile

New flag that, in addition to standard 6-phase enrollment:
- Writes `/etc/membrane/gate-name` (identity for reconnect hook)
- Reports `mobility.configure` phase in output

Usage:
```bash
sudo /opt/membrane/membrane gate.bootstrap golgiAlpha --mobile
# or with dry-run:
sudo /opt/membrane/membrane gate.bootstrap golgiAlpha --mobile --dry-run
```

### 3. Systemd Units

**System-level** (`deploy/systemd/`):
- `songbird-federation.service` — mesh relay with `:7700` bind, peer persistence, auto-restart
- `membrane-nucleus@.service` — template unit per primal (instance = binary name)
- `membrane-nucleus.target` — aggregate target, enables all NUCLEUS as a group

**User-level** (`deploy/systemd/user/`):
- Same services but running in user session (Pop/Ubuntu desktop, XDG paths)
- Binary paths from local depot, sockets in `$XDG_RUNTIME_DIR/biomeos/`

### 4. NetworkManager Dispatcher Hook

`deploy/nm-dispatcher/99-mesh-reconnect`:
- Triggers on `up` and `connectivity-change` events
- Finds songbird socket (3-tier: `/run/membrane/` → `$XDG_RUNTIME_DIR/biomeos/` → `/run/user/$UID/biomeos/`)
- Reads gate name from `/etc/membrane/gate-name` or `~/.config/membrane/gate-name`
- Fires `mesh.init` JSON-RPC to VPS relay (default: [RELAY_PUBLIC]:7700)

### 5. Provisioning Script

`deploy/provision-golgi.sh <gate-name>`:
- One-shot: creates dirs → fetches 13 primals from WAN depot → installs systemd → writes identity → installs NM hook → starts mesh + NUCLEUS
- Zero Rust toolchain required (uses pre-built binaries from WAN depot)
- Reports progress per-phase with error recovery

---

## Deployment Procedure (Per-NUC)

### Quick (no Rust):
```bash
scp -r gate:/path/to/cellMembrane/deploy /tmp/deploy
sudo /tmp/deploy/provision-golgi.sh golgiAlpha
```

### Full (with membrane CLI):
```bash
sudo /opt/membrane/membrane gate.bootstrap golgiAlpha --mobile
```

---

## Fleet Naming

| NUC | Gate Name | Concept |
|-----|-----------|---------|
| #1 | `golgiAlpha` | First mobile NUCLEUS |
| #2 | `golgiBeta` | Second mobile NUCLEUS |
| #3 | `golgiGamma` | Third mobile NUCLEUS |

---

## Mesh Behavior

- **WAN (between buildings)**: NUC peers through VPS relay at [RELAY_PUBLIC]:7700 (33ms typical)
- **LAN (colocated)**: NM hook fires mesh.init, songbird discovers direct LAN peers (sub-5ms)
- **Boot**: systemd starts songbird → loads `peers.toml` → auto-reconnects persisted peers → biomeOS starts NUCLEUS
- **Network change**: NM dispatcher fires mesh.init → re-establishes paths if dropped

---

## Upstream Notes

1. **songBird mDNS**: Already wired in discovery layer, not field-tested. Would eliminate explicit `mesh.init` for LAN peers.
2. **biomeOS**: NUCLEUS supervision (v4.17) handles primal restarts. No cellMembrane changes needed for supervision on NUCs.
3. **Primal bind**: NUCs on Pop/Ubuntu use UDS natively (no `PRIMAL_BIND_MODE=tcp_only` needed, unlike grapheneGate/Android).

---

## Status

- Code: SHIPPED (`9e07b01`)
- Physical: READY for first NUC provisioning
- 360 tests, zero clippy, zero development debt
