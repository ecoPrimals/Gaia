# AAR: Isomorphic RustDesk Relay — Outage + Hardening

**Wave**: 133b (follow-up)
**Gate**: sporeGate (executing), golgi (target)
**Date**: 2026-07-06
**Status**: COMPLETE — RustDesk restored, isomorphic pattern implemented

---

## Incident Summary

During the Sovereign Relay Architecture service prune, RustDesk (hbbs + hbbr) was incorrectly classified as non-relay and its binaries were deleted from golgi. This broke remote desktop access to all gates via the sovereign RustDesk server.

**Duration**: ~20 minutes (from prune execution to restore)
**Impact**: All RustDesk remote desktop sessions disconnected; gates unreachable via RustDesk
**Data loss**: None — identity keys and DB in `/opt/membrane/rustdesk/` were preserved

## Root Cause Chain

1. **Classification error**: RustDesk is a symbiotic AGPL partner, not a primal. The prune logic treated all non-relay binaries in `/opt/membrane/` as expendable. No manifest role or protected-services list tracked RustDesk.
2. **Binary deletion**: `rm -f /opt/membrane/hbbs /opt/membrane/hbbr` removed the executables (9.3M + 3.3M).
3. **Service crash**: `systemctl enable --now` restarted services pointing at deleted binaries → exit 127 (hbbs, binary not found) and exit 203 (hbbr, exec format error) → restart loop → `StartLimitBurst` hit → service failed.

## Immediate Fix

1. Downloaded RustDesk server v1.1.14 from GitHub releases
2. Installed `hbbs` and `hbbr` to `/opt/membrane/`
3. `systemctl reset-failed && systemctl restart` both services
4. Verified ports 21115-21119 listening, clients reconnected

## Hardening Implemented

### 1. DNS Abstraction: `remote.primals.eco`

Added A record to Knot DNS zone on golgi:
```
remote.primals.eco. 300 A [RELAY_PUBLIC]
```
DNSSEC auto-signed. Clients should be reconfigured to use `remote.primals.eco` instead of raw IP. Moving RustDesk to any host = update one DNS record.

### 2. Portable Identity

RustDesk server identity (`id_ed25519` + `id_ed25519.pub`) copied to:
- `/opt/ecoPrimals/depot/rustdesk/` on both sporeGate and golgi
- Public key: `[RUSTDESK_KEY_PURGED]`

The DB (`db_v2.sqlite3`) is ephemeral — clients re-register on startup. Only the keypair matters for trust. Any gate can become the RustDesk server by restoring the keypair.

### 3. Manifest Role: `remote_access`

Added to `ecosystem_manifest.toml`:
- `[topology.roles]`: `remote_access = "golgiBody"` 
- `[gates.golgiBody]`: `roles` array now includes `"remote_access"`

This makes RustDesk visible to `membrane shadow validate`, prune logic, and provision scripts.

### 4. Provision Script Updated

`provision-golgi.sh` now includes:
- RustDesk binary download + install (step 5)
- `hbbs-membrane.service` and `hbbr-membrane.service` unit definitions (step 8)
- UFW rules for ports 21115-21117 (step 9)
- Identity restore from depot in NEXT STEPS (step 6)

## Divergences for Upstream

### DIV-RUSTDESK-01: Client Reconfiguration (P2 — Action Required)
All RustDesk clients on gates should be updated to point at `remote.primals.eco` instead of `[RELAY_PUBLIC]`. This is a one-time manual change per gate. Until done, clients still use the hardcoded IP and will break if golgi's IP changes.

### DIV-RUSTDESK-02: Prune Safety (P1 — cellMembrane Code)
`membrane shadow prune` (or equivalent) should read the gate's `roles` array from the manifest and protect services associated with each role. A gate with `remote_access` role must not have `hbbs-membrane` or `hbbr-membrane` stopped or their binaries deleted. This should be enforced in the prune logic, not just documented.

### DIV-RUSTDESK-03: Health Monitoring (P2 — cellMembrane Code)
The `rootpulse` or `shadow validate` should check that the `remote_access` gate has:
- `hbbs` listening on TCP 21116
- `hbbr` listening on TCP 21117
- `remote.primals.eco` resolving to the gate's IP

### DIV-RUSTDESK-04: Tower Absorption (P3 — Future)
songBird's TURN relay (`:3478`) and hbbr both relay opaque encrypted bytes. hbbr could eventually be absorbed into songBird. hbbs (rendezvous/NAT detection) could be absorbed into songBird's peer discovery. This is a longer-term convergence target.

## Pattern for New NUC Spin-Up

When deploying RustDesk to a different gate:
1. Assign `remote_access` role to the new gate in `ecosystem_manifest.toml`
2. Remove it from the old gate's roles
3. Install hbbs/hbbr binaries (from GitHub release or depot)
4. Restore `id_ed25519` keypair from depot — same key = clients don't reconfigure
5. Update `remote.primals.eco` DNS to point at new host
6. Open ports 21115-21117 on the new host's firewall

## primalSpring Resilience Tests

- **remote_access_role**: Verify gate with `remote_access` has hbbs+hbbr active on 21115/21116/21117
- **dns_remote_resolve**: Verify `remote.primals.eco` resolves to the `remote_access` gate's IP
- **identity_portability**: Deploy RustDesk to second gate with same `id_ed25519`, verify client connectivity
- **prune_safety**: Run prune against gate with `remote_access` role, verify hbbs/hbbr NOT stopped
