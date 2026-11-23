# sporeGate Deployment Ops — Wave 155d→155h AAR

**Date**: 2026-07-28 through 2026-07-29
**Gate**: sporeGate (build authority, peptidoglycan anchor H1)
**Scope**: Infrastructure deployment, firewall hardening, depot evolution, SSH CA

---

## Summary

Three waves of deployment work on hardware/topology/deployment (our ownership
lane), while code teams shipped in parallel on eastGate, westGate, and
strandGate. All P0 and P1 deployment items from the 155h blurb are resolved.

## What We Did

### 1. depot.primals.eco — New Caddy TLS Surface (Wave 155d)

**Problem**: `gate.status` sovereignty probe couldn't reach the depot. The depot
was only served at `membrane.primals.eco/depot/*` (nested path), but the probe
hit `depot.primals.eco` (wildcard DNS resolves but Caddy had no site block).

**Fix**: Added a dedicated `depot.primals.eco` Caddy site block on golgiBody
serving `/opt/ecoPrimals/depot` at root with `file_server browse` + `/health`
endpoint. TLS cert acquired automatically via ACME.

**Result**: `depot.primals.eco` returns 200 OK. `sovereignty.s1_tls` probe green.

### 2. Socket Permissions — membrane Group (Wave 155d)

**Problem**: `membrane gate.status` returned "Permission denied (os error 13)"
when connecting to primal sockets (`neural-api.sock`, `biomeos.sock`,
`compute-tarpc.sock`). The `membrane` CLI runs as `sporegate` (uid 1000) but
sockets were `root:root` with no world access.

**Fix**:
- Created `membrane` system group
- Added `sporegate` to group
- Set all sockets to `0660 root:membrane`
- Persisted via `/etc/tmpfiles.d/membrane-sockets.conf`

**Result**: `gate.status` connects to all sockets. 13/13 primals alive check works.

### 3. membrane Binary Rebuild (Wave 155d→155f)

**Problem**: Deployed membrane binary (Jul 24, pre-J1/J2) couldn't parse
`checksums.toml` — the CLI expected `ChecksumEntry` struct format but the depot
had plain hash strings.

**Fix**: Rebuilt membrane from latest cellMembrane (fc7c4d9, includes J1/J2
codification + checksum format fix). Fixed a `pub(super)` → `pub(crate)`
visibility issue on `systemctl()` that blocked the build (stale incremental
cache; clean rebuild resolved).

**Result**: `depot.integrity` probe now shows "16 verified, 0 hash mismatch."

### 4. LOG before DROP — RUSTDESK_MEMBRANE Chain (Wave 155f)

**Problem**: Rate-limit DROPs in the firewall were silent. Two previous NAT
topology traps were diagnosed by packet-counting, not by logs. Future incidents
would be invisible.

**Fix**: Inserted LOG rules before each DROP in the `RUSTDESK_MEMBRANE` chain:
- Rule 4: `LOG "RUSTDESK_UDP_RATELIMIT:"` before UDP DROP (120/10s)
- Rule 8: `LOG "RUSTDESK_TCP_RATELIMIT:"` before TCP DROP (60/10s)

Saved via `netfilter-persistent save`. Currently 0 drops — healthy.

**Result**: Any future rate-limit activation will appear in syslog/journalctl.
The Cursor rule `outer-membrane-rustdesk.mdc` updated with full chain layout.

### 5. Fresh Harvest + Depot Push (Wave 155f→155h)

**Problem**: Depot binaries were 13 days old (Jul 14-16). Teams deploying to
westGate and strandGate needed fresh genomeBins.

**Fix**: Ran two harvest cycles:
1. **Wave 155f**: `membrane plasmid.harvest --push` — 12/15 musl binaries built
   and pushed. nestgate (binary path mismatch) and coralreef (compile errors,
   since fixed by code team) failed.
2. **Wave 155h**: Second harvest after coralReef fixes landed — 14/15 built,
   8 new pushed + 6 already current. nestgate still fails (code team item).

**Result**: golgiBody depot has fresh binaries for all primals except nestgate.

### 6. glibc Depot Target — P0 GPU Primals (Wave 155h)

**Problem**: musl-static genomeBins cannot `dlopen` glibc Vulkan ICD loaders.
strandGate's compute trio (barraCuda, coralReef, toadStool) needs dynamically-
linked glibc binaries for GPU workloads on the RTX 3090.

**Fix**:
- Added `gpu = true` to compute trio entries in `sources.toml`
- Created `x86_64-unknown-linux-gnu` depot directory on both sporeGate + golgiBody
- Harvest automatically builds both musl + gnu targets for GPU-flagged primals

**Result**: `barracuda` (12MB) and `coralreef` (8.8MB) glibc binaries live on
golgiBody at `depot/primals/x86_64-unknown-linux-gnu/`. toadStool built musl-only
(it dispatches compute, doesn't `dlopen` GPU drivers directly).

### 7. step-ca SSH Certificate Authority — J8 Deployment (Wave 155h)

**Problem**: SSH keys exchanged via chat (J8 jelly string). No audit trail, no
expiry, TOFU on every new gate connection.

**Fix**: Deployed step-ca (Smallstep) v0.30.2 on golgiBody as a sovereign SSH CA:
- Installed step-cli v0.30.6 + step-ca v0.30.2
- Initialized with SSH support: `--dns ca.primals.eco,golgi.primals.eco,[RELAY_PUBLIC],10.13.37.2`
- Created systemd service (`step-ca.service`), enabled + running
- Added `ca.primals.eco` Caddy reverse proxy (TLS via ACME → localhost:9443)
- Issued host certificate for golgiBody
- Configured golgiBody sshd: `TrustedUserCAKeys` + `HostCertificate`
- Bootstrapped sporeGate as first client

**Result**: `https://ca.primals.eco/health` returns `{"status":"ok"}`.

**Constants for cellMembrane J8 Phase 2**:

| Constant | Value |
|----------|-------|
| CA URL | `https://ca.primals.eco` |
| Root fingerprint | `566b6a6ef9611355c5697973a7c9d699acc06318ef918ce992cd4e7884581cd5` |
| Provisioner | `admin` |
| SSH cert lifetime | `8h` (default) |

---

## Ownership Model Applied

| Item | Owner | Lane |
|------|-------|------|
| Caddy sites, TLS, depot serving | sporeGate/golgiBody deployment | Ours |
| Socket permissions, tmpfiles.d | sporeGate deployment | Ours |
| Firewall rules (RUSTDESK_MEMBRANE) | golgiBody deployment | Ours |
| Harvest + push (build authority) | sporeGate deployment | Ours |
| glibc depot target | sporeGate deployment | Ours |
| step-ca deployment | golgiBody deployment | Ours |
| nestgate binary path mismatch | cellMembrane code team | Flagged |
| checksums.toml format evolution | cellMembrane code team | Resolved by rebuild |
| s3_content probe path | cellMembrane code team | Flagged |
| vcs.parity drift | Code teams | Flagged |
| mesh.reachability socket | cellMembrane code team | Flagged |

## Remaining — Needs Human Hands

| Item | Blocker |
|------|---------|
| northGate RustDesk | SSH denied (key mismatch). LAN-reachable at ~0.3ms. Needs physical access. |
| ironGate RustDesk | SSH denied. LAN-reachable at ~0.25ms. Needs physical access. |
| blueGate LAN IP | Can't identify without RustDesk session. Candidates: 192.168.4.200 (Dell) or 192.168.4.231 (Gigabyte). |
| blueGate WG keygen | Planned IP 10.13.37.12, pending identification + keygen. |

## Peptidoglycan Scan (Wave 155h)

| Host | LAN IP | Status |
|------|--------|--------|
| sporeGate | 192.168.4.3 | ONLINE, anchor H1 |
| Omada SX3008F | 192.168.4.111 | ONLINE (house2 hub) |
| Flint 2 | 192.168.4.250 | ONLINE (house2 WiFi bridge) |
| ironGate | 192.168.4.237 | LAN-reachable, RustDesk degraded |
| ironGate-compute | 192.168.4.169 | LAN-reachable |
| CRS310 mgmt | 192.168.4.210 | ONLINE (backbone hub) |
| 192.168.4.200 | ? | LIVE — Dell MAC, possible blueGate |
| 192.168.4.231 | ? | LIVE — Gigabyte MAC, possible blueGate or northGate |

---

*sporeGate deployment ops, Wave 155d→155h. 7 deployment items completed.
P0 glibc depot target resolved. step-ca sovereign SSH CA live. Depot fresh.
Firewall observable. Code team items flagged upstream. — sporeGate, Wave 155h*
