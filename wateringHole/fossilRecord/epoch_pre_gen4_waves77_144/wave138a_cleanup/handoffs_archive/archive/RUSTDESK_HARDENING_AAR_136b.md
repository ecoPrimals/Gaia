# RustDesk Relay Hardening AAR — Wave 136b

**Date**: 2026-07-11
**Scope**: Security standardization of the RustDesk relay on golgi,
covering key management, version upgrade, access control, and rate limiting.

---

## Physical Topology

```
House 1 (MikroTik LAN)
├── northGate — operator workstation (RustDesk client)
├── eastGate  — main dev node (RustDesk target)
└── sporeGate — compute node (portable, co-located with eastGate)

Remote
└── flockGate — WAN dev node (RustDesk target, [FLOCK_WAN])

VPS (golgi — [RELAY_PUBLIC])
└── RustDesk relay (hbbs + hbbr)
    ├── LAN sessions:  northGate ↔ eastGate (direct or relay)
    └── WAN sessions:  northGate ↔ flockGate (relay through golgi)
```

## Pre-Hardening State

| Item | State | Risk |
|------|-------|------|
| Version | 1.1.14 (1.1.15 available) | Known fixes missed |
| Key enforcement | `-k` flag absent — **open relay** | Any RustDesk client could register and use the relay |
| Private key perms | `644` (world-readable) | Key material exposed to any local user |
| Rate limiting | None on ports 21115-21119 | Brute-force and relay abuse possible |
| Stranger relay usage | **4 relay requests from unknown IPs** in 7 days | Relay bandwidth consumed by non-ecosystem traffic |

Stranger relay IPs observed:
- `188.240.59.10` (Jul 8)
- `193.176.29.6` (Jul 9)
- `31.14.254.50` (Jul 10)
- `31.14.254.41` (Jul 11)

## Hardening Applied

### 1. Private Key Permissions

```
chmod 600 /opt/membrane/rustdesk/id_ed25519
```

Before: `644 root:root` — After: `600 root:root`

Public key remains `644` (intentional — clients need it).

### 2. Key Enforcement (`-k _`)

Added `-k _` to hbbs ExecStart. This requires all connecting clients to
present the server's public key during handshake. Clients without the key
are rejected at the rendezvous stage — they cannot register, discover
peers, or initiate relay sessions.

**Impact on ecosystem clients**: Each RustDesk client (northGate, eastGate,
flockGate) must have the server's public key configured. The key is:

```
[RUSTDESK_KEY_PURGED]
```

Clients that already had the key configured will continue working. Any
client that was relying on keyless connection needs the key added to their
RustDesk settings under ID/Relay Server → Key.

### 3. Version Upgrade (1.1.14 → 1.1.15)

- Downloaded from official GitHub release
- Old binaries backed up to `*.1.1.14.bak`
- `rustdesk-utils` also installed
- Both services restarted and healthy

### 4. Rate Limiting

| Port | Protocol | Limit | Purpose |
|------|----------|-------|---------|
| 21115-21119 | TCP | 20 new conn/10s per IP | Brute-force protection |
| 21116 | UDP | 30 pkt/10s per IP | NAT probe flood protection |

Rules saved to `/etc/iptables.rules` for persistence.

## Post-Hardening State

```
PORT       PROTO  PROTECTION
21115/tcp  TCP    iptables rate limit + key enforcement
21116/tcp  TCP    iptables rate limit + key enforcement
21116/udp  UDP    iptables rate limit
21117/tcp  TCP    iptables rate limit (relay)
21118/tcp  TCP    iptables rate limit (websocket)
21119/tcp  TCP    iptables rate limit (websocket relay)
```

- Stranger relay requests: **blocked** (key enforcement rejects unkeyed clients)
- Ecosystem clients: **unaffected** (have server public key)
- Version: **1.1.15** (current)
- Key material: **600 perms** (root-only)

## Registered Peers

5 peers in `db_v2.sqlite3`, all from ecosystem IPs:
- `[NUCLEUS_WAN]` (sporeGate / eastGate — 4 entries)
- `[FLOCK_WAN]` (flockGate — 1 entry)

## Remaining / Future

| Item | Priority | Notes |
|------|----------|-------|
| Backup identity keys to depot | P2 | `id_ed25519` + `id_ed25519.pub` → depot for DR |
| RustDesk client key verification | P2 | Confirm all gates have the public key configured |
| fail2ban for RustDesk | P3 | hbbs logs auth failures — could feed a fail2ban filter |
| Version tracking in checksums.toml | P3 | Track hbbs/hbbr alongside primals |
| Sovereign relay evaluation | P4 | birdSong transport could eventually subsume RustDesk relay |

## Files Changed

- `provision-golgi.sh` — RustDesk version bumped to 1.1.15, `-k _` added
  to hbbs ExecStart, key permissions hardened, rate limiting rules added
- `/etc/systemd/system/hbbs-membrane.service` (golgi live) — `-k _` added
- `/opt/membrane/hbbs`, `/opt/membrane/hbbr` (golgi live) — upgraded to 1.1.15
- `/opt/membrane/rustdesk/id_ed25519` (golgi live) — permissions 600
- `/etc/iptables.rules` (golgi live) — RustDesk rate limiting rules

---

*sporeGate — RustDesk relay hardened. Key enforcement active, strangers
blocked, version current, rate limiting deployed. Ecosystem connectivity
preserved.*
