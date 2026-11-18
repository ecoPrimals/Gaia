<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# benchScale NUCLEUS Validation + ironGate Production Deployment

**Date**: June 12, 2026
**Wave**: 111
**Gate**: ironGate (cellMembrane)
**Status**: COMPLETE — all 5 phases validated

---

## Summary

Validated full 13-primal NUCLEUS deployment through a graduated
pipeline: Docker lab → libvirt VM mesh → production systemd deployment.
ironGate is now running a permanent NUCLEUS with systemd units, joining
the VPS mesh as a full peer.

## Phases Completed

### Phase 1: Docker Lab Pre-flight

- Built `nucleus-lab-node` Docker image (Ubuntu 24.04 + socat/iproute2/jq)
- Created 2-node lab (ironGate + golgiBody) with `ecoprimals-vps-depot-deploy` topology
- Deployed all 13 primals from `plasmidBin/primals/x86_64-unknown-linux-musl/`
- Health sweep: **13/13 sockets alive**, bearDog JSON-RPC responding
- Songbird federation enabled, inter-container TCP port 7700 reachable

### Phase 2a: agentReagents Templates

New templates for libvirt VM provisioning:

| Template | Resources | Composition | Purpose |
|----------|-----------|-------------|---------|
| `gate-nucleus-full.yaml` | 4 vCPU, 8GB | Full 13/13 | ironGate, eastGate, swiftGate |
| `gate-nuc-canary.yaml` | 1 vCPU, 2GB | Full (constrained) | NUC canary warm standby |

Key features:
- Cloud-init with SSH key injection and `tower.env`
- systemd template units: `beardog-membrane`, `songbird-membrane`, `membrane-nucleus@`
- Resource limits for canary (MemoryMax, CPUQuota, Nice)
- `gate.bootstrap` as post-boot step

### Phase 2b: benchScale Topology

Created `topologies/irongate-nucleus-mesh.yaml` — 3-node libvirt mesh:

| Node | Image | Resources | Composition | Network |
|------|-------|-----------|-------------|---------|
| irongate | gate-nucleus-full | 4 CPU, 8GB | full (13/13) | basement_lan (0ms) |
| nuc-canary | gate-nuc-canary | 1 CPU, 2GB | full (canary) | basement_lan (0ms) |
| golgi-relay | gate-nucleus-full | 1 CPU, 1GB | tower (3/13) | wan_bridge (15ms) |

Created `scripts/validate-mesh.sh` for automated post-deploy federation validation.

### Phase 2c: libvirt VM Mesh Validation

- Created `nucleus-mesh` libvirt network (10.92.0.0/24, static DHCP)
- Booted 3 KVM VMs from Ubuntu 24.04 cloud image (copy-on-write qcow2)
- SSH key auth working on all nodes
- Deployed primals: 13 on ironGate, 13 on nuc-canary, 3 on golgi-relay
- **Results**:
  - BearDog crypto spine: ALIVE on all 3 nodes
  - Songbird federation: enabled on all 3 nodes
  - TCP port 7700: full 3-way mesh connectivity (6/6 directional links)
  - ironGate: 25 UDS sockets (13 primals + 12 capability aliases)

### Phase 3: Production ironGate NUCLEUS

- Created `irongate-full.toml` gate profile (extends full, VPS mesh peers)
- Installed systemd units:
  - `beardog-membrane.service` (crypto foundation, RuntimeDirectory=membrane)
  - `songbird-membrane.service` (federation, --bind 0.0.0.0 --port 7700)
  - `skunkbat-membrane.service` (defense)
  - `membrane-nucleus@{10 primals}.service` (template unit)
  - `membrane-biomeos.service` (api subcommand)
- Configured `/etc/membrane/tower.env` with production identity
- **Result**: 13/13 primals alive, `gate.bootstrap ironGate --dry-run` passes 8/9 phases
- VPS sovereignty confirmed: TLS, federation relay, content serving, BearDog auth

## Operational Notes

### Systemd Management

```bash
# Start full NUCLEUS
sudo systemctl start beardog-membrane
sleep 2
sudo systemctl start songbird-membrane skunkbat-membrane
sudo systemctl start membrane-nucleus@{toadstool,barracuda,coralreef,nestgate,rhizocrypt,loamspine,sweetgrass,squirrel,petaltongue}
sudo systemctl start membrane-biomeos

# Check status
ls /run/membrane/*.sock | wc -l  # expect ≥13
sudo journalctl -u beardog-membrane -f
membrane gate.status
```

### VM Mesh Management

```bash
# VMs are running under libvirt
sudo virsh list --all
sudo virsh net-dhcp-leases nucleus-mesh

# SSH into VMs
ssh irongate@10.92.0.10  # ironGate VM
ssh irongate@10.92.0.20  # nuc-canary VM
ssh irongate@10.92.0.30  # golgi-relay VM

# Validation
bash infra/benchScale/scripts/validate-mesh.sh --topology irongate-nucleus-mesh
```

### Known Issues

1. **biomeos uses `api` subcommand** — not `server`. The generic `membrane-nucleus@` template
   won't work for biomeos; use the dedicated `membrane-biomeos.service` unit.
2. **Songbird --bind 0.0.0.0** — required for cross-node federation. Default is 127.0.0.1.
3. **depot.integrity hash mismatch** — local dev builds differ from depot checksums.
   Resolves after next `plasmid.harvest` cycle.
4. **Freshness race condition** — VPS gates auto-publishing stale Wave 109 freshness,
   racing with active development. See: freshness auto-publish fix (P1 pipeline item).

## Files Created/Modified

| Path | Type | Description |
|------|------|-------------|
| `infra/agentReagents/templates/gates/gate-nucleus-full.yaml` | NEW | Full NUCLEUS VM template |
| `infra/agentReagents/templates/gates/gate-nuc-canary.yaml` | NEW | NUC canary VM template |
| `infra/benchScale/topologies/irongate-nucleus-mesh.yaml` | NEW | 3-node libvirt topology |
| `infra/benchScale/scripts/validate-mesh.sh` | NEW | Mesh validation orchestrator |
| `infra/plasmidBin/profiles/irongate-full.toml` | NEW | ironGate production profile |
| `/etc/systemd/system/beardog-membrane.service` | PROD | Production systemd unit |
| `/etc/systemd/system/songbird-membrane.service` | PROD | Production systemd unit |
| `/etc/systemd/system/skunkbat-membrane.service` | PROD | Production systemd unit |
| `/etc/systemd/system/membrane-nucleus@.service` | PROD | Template unit for 10 primals |
| `/etc/systemd/system/membrane-biomeos.service` | PROD | biomeOS dedicated unit |
| `/etc/membrane/tower.env` | PROD | Production identity + mesh config |

## Upstream Dependencies

- **songBird team**: VPS rebuild to `fe47c012` for persistent relay (ops-owned)
- **cellMembrane**: Freshness auto-publish race fix (P1 pipeline item)
- **NUC hardware**: Physical deployment pending NUC bootstrap for canary-fieldmouse

## Next Steps

1. Fix freshness auto-publish race condition (stale Wave 109 commits from VPS gates)
2. Run `plasmid.harvest` to align depot checksums with latest builds
3. Configure NUC hardware as `nuc-alpha` canary (Phase 1 of VPS minimization)
4. Slim golgiBody VPS to relay-only once NUC is proven stable
