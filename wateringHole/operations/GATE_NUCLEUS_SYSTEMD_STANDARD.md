<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Gate NUCLEUS systemd Deployment Standard

**Status**: Ecosystem Standard
**Version**: 1.0.0
**Date**: June 12, 2026
**Authority**: wateringHole (cellMembrane Wave 111)
**Validated by**: benchScale libvirt mesh (irongate-nucleus-mesh topology)

---

## Purpose

This standard defines how a full NUCLEUS (13/13 primals) is deployed as
persistent systemd services on a production gate. It replaces ad-hoc process
management and ensures primals survive reboots, respect dependency ordering,
and participate in the federation mesh.

This is the canonical pattern for desktop gates (ironGate, eastGate, swiftGate)
and NUC canary nodes. VPS/relay nodes use a subset (tower-only or fieldMouse).

---

## Architecture

```
systemd (PID 1)
  ├── beardog-membrane.service      ← crypto spine (starts FIRST)
  │     └── /run/membrane/beardog.sock
  ├── songbird-membrane.service     ← mesh federation (Requires beardog)
  │     └── /run/membrane/songbird.sock + TCP :7700
  ├── skunkbat-membrane.service     ← threat defense (Requires beardog)
  │     └── /run/membrane/skunkbat.sock
  ├── membrane-nucleus@toadstool    ← compute dispatch
  ├── membrane-nucleus@barracuda    ← GPU math
  ├── membrane-nucleus@coralreef    ← shader compile
  ├── membrane-nucleus@nestgate     ← storage transport
  ├── membrane-nucleus@rhizocrypt   ← ephemeral DAG
  ├── membrane-nucleus@loamspine    ← permanent ledger
  ├── membrane-nucleus@sweetgrass   ← attribution braids
  ├── membrane-nucleus@squirrel     ← AI coordination
  ├── membrane-nucleus@petaltongue  ← multi-modal UI
  └── membrane-biomeos.service      ← orchestrator (api subcommand)
        └── /run/membrane/biomeos.sock
```

---

## Required Files

### `/etc/membrane/tower.env`

Environment file sourced by all units. Contains gate identity and mesh config:

```ini
FAMILY_SEED=<production-family-seed>
FAMILY_ID=e8b62b6e
NODE_ID=<gate-name>
GATE_NAME=<gate-name>
SONGBIRD_PEERS=<peer1>@<host1>:7700,<peer2>@<host2>:7700
SONGBIRD_FEDERATION_ENABLED=true
SECURITY_SOCKET=/run/membrane/beardog.sock
PRIMAL_BIND_MODE=auto
ECOPRIMALS_ROOT=/home/irongate/Development/ecoPrimals
```

**Permissions**: `chmod 600` (contains FAMILY_SEED).

### `/opt/ecoPrimals/primals/`

All 13 musl-static binaries from `plasmidBin/primals/x86_64-unknown-linux-musl/`.

### Gate Profile

`infra/plasmidBin/profiles/<gate>-full.toml` — defines composition, mesh peers,
launch order, and health thresholds.

---

## systemd Unit Patterns

### Tower Units (dedicated)

Tower primals get dedicated unit files because they have unique startup requirements:

- **beardog-membrane.service**: `RuntimeDirectory=membrane` (creates `/run/membrane/`)
- **songbird-membrane.service**: `--port 7700 --bind 0.0.0.0` for federation
- **skunkbat-membrane.service**: Standard socket binding

### Template Unit (`membrane-nucleus@.service`)

All non-tower, non-biomeos primals use the parameterized template:

```ini
[Service]
ExecStart=/opt/ecoPrimals/primals/%i server --socket /run/membrane/%i.sock
```

Instantiated as: `membrane-nucleus@toadstool`, `membrane-nucleus@barracuda`, etc.

### biomeOS Unit (dedicated)

biomeOS uses `api` subcommand (not `server`), requiring a dedicated unit:

```ini
ExecStart=/opt/ecoPrimals/primals/biomeos api --socket /run/membrane/biomeos.sock
```

---

## Startup Order

The dependency chain enforces correct ordering:

1. **beardog-membrane** — starts first (crypto spine, creates RuntimeDirectory)
2. **songbird-membrane** + **skunkbat-membrane** — Requires beardog
3. **membrane-nucleus@*{10}** — After beardog + songbird
4. **membrane-biomeos** — After beardog + songbird (needs crypto for Dark Forest)

---

## Validation

### Socket Count

A healthy full NUCLEUS produces ≥13 sockets in `/run/membrane/`:

```bash
ls /run/membrane/*.sock | wc -l  # expect ≥13 (up to ~25 with capability aliases)
```

### Health Probes

```bash
# BearDog crypto spine
echo '{"jsonrpc":"2.0","method":"health","id":1}' | \
  socat -t2 - UNIX-CONNECT:/run/membrane/beardog.sock

# Songbird federation
echo '{"jsonrpc":"2.0","method":"federation.status","id":1}' | \
  socat -t2 - UNIX-CONNECT:/run/membrane/songbird.sock
```

### membrane gate.status

```bash
membrane gate.status
# Expect: sovereignty.s1_tls OK, s2_relay OK, s3_content OK, s4_auth OK
```

### gate.bootstrap

```bash
membrane gate.bootstrap <gate-name> --dry-run
# Expect: ≥8/9 phases pass (checksum.git may fail with dev builds)
```

---

## Songbird Federation Requirements

For cross-gate mesh to form, songbird MUST:

1. Bind to `0.0.0.0:7700` (not localhost) — use `--bind 0.0.0.0`
2. Have `SECURITY_SOCKET` pointing to beardog's UDS
3. Have `SONGBIRD_PEERS` configured with at least one peer
4. Have `SONGBIRD_FEDERATION_ENABLED=true`

---

## benchScale Pre-Validation

Before deploying to production, validate via the graduated pipeline:

1. **Docker lab** (`nucleus-lab-node` image) — fast smoke test
2. **libvirt VM mesh** (`irongate-nucleus-mesh` topology) — OS-fidelity
3. **Production deploy** — `gate.bootstrap` + systemd enable/start

---

## Cascade Integration

Once deployed, the NUCLEUS participates in the cascade pipeline:

```bash
membrane temporal.cascade --with-restart
```

This pulls latest from forgejo, rebuilds if needed, and restarts affected services.

---

## Composition Variants

| Profile | Primals | Units | Use Case |
|---------|---------|-------|----------|
| `irongate-full` | 13 | 13 (3 dedicated + 10 template + biomeos) | Desktop workstation |
| `canary-fieldmouse` | 13 | 13 (resource-constrained) | NUC warm standby |
| `tower` | 3 | 3 (beardog + songbird + skunkbat) | VPS relay, beacon |
| `fieldMouse` | 7 | 7 (tower + nest) | NAS, archive, edge |
