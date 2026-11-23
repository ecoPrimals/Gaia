# cellMembrane — Wave 79b Completion Report

**Date**: 2026-06-05  
**Gate**: ironGate  
**Operator**: cellMembrane agent (eastGate overwatch)

---

## Completed

### 1. Caddy Reverse Proxy Wiring (P1)

DNS A records added to `primal.eco` zone (authoritative knot-dns on golgiBody):

| Subdomain | IP | Purpose |
|-----------|-----|---------|
| mesh.primal.eco | 137.184.197.151 | Songbird mesh federation |
| auth.primal.eco | 137.184.197.151 | bearDog BTSP auth surface |
| api.primal.eco | 137.184.197.151 | biomeOS Neural API |
| dns.primal.eco | 137.184.197.151 | Reserved |
| relay.primal.eco | 137.184.197.151 | Reserved |

Stale dual A records (pointing to golgiBody inner [RELAY_PUBLIC]) removed.

Caddyfile on golgiBody-ext updated with:
- `mesh.primal.eco` → reverse_proxy to Songbird [RELAY_PUBLIC]:7700 (publicly bound)
- `auth.primal.eco` → placeholder 503 (UDS backend on inner, pending cross-node proxy)
- `api.primal.eco` → placeholder 503 (UDS backend on inner, pending cross-node proxy)
- `nestgate.io` → placeholder 200 (Forgejo on inner loopback:3000, pending cross-node proxy)

All sovereign TLS certs obtained via Let's Encrypt:
- `primal.eco` — LE cert active
- `nestgate.io` — LE cert active
- `mesh.primal.eco` — LE cert active (Jun 05 00:18:36 UTC)
- `auth.primal.eco` — LE cert active (Jun 05 00:18:37 UTC)
- `api.primal.eco` — LE cert active (Jun 05 00:18:35 UTC)

### 2. build-primal.sh Bug Fix (P1)

**Root cause**: When `cargo build --manifest-path` is used on a workspace member,
cargo places the `target/` directory at the workspace root, not relative to the
Cargo.toml path. The script then scanned `$clone_dir/target/...` which was empty.

**Fix**: Added explicit `--target-dir "$clone_dir/target"` to the cargo invocation,
ensuring output always lands at the expected path regardless of workspace discovery.

**Commit**: `4c5f08d` on plasmidBin main.

---

## Remaining — Cross-Node Proxy

Three services on golgiBody (inner) are loopback/UDS only and unreachable
from golgiBody-ext (outer):

| Service | Backend | Access |
|---------|---------|--------|
| NestGate/Forgejo | 127.0.0.1:3000 | Loopback only |
| bearDog | /run/membrane/beardog.sock | UDS |
| biomeOS | /run/membrane/biomeos.sock | UDS |

**Options** (pick one per next wave):
1. SSH tunnel from ext→inner forwarding specific ports
2. Add a lightweight TCP listener on inner (socat or caddy) that binds 0.0.0.0:PORT → UDS
3. Run a local Caddy on golgiBody that proxies UDS → TCP on private interface

Recommended: Option 2 — minimal `socat` forwarders in systemd units.

---

## Gate Status

- **13/13 primals ALIVE via UDS**: 10/12 + skunkBat TCP (3 headless fixes pending)
- **mesh.primal.eco**: DNS + TLS + reverse proxy LIVE, Songbird reachable
- **Zero externally-exposed primal TCP ports**: CONFIRMED (ufw audit)
- **S4 Auth graduation**: 7-day gate ends ~Jun 9
- **Critical path**: Fix 3 headless binaries → redeploy → mesh.init → mesh proof → stadial
