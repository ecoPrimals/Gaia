# Shadow Data Collection — Wave 66 (June 1, 2026)

Collected while S1 TLS 7-day shadow runs. Non-temporal work window.

## K-Derm VPS Health Matrix

| Node | Role | Uptime | Disk | Services |
|---|---|---|---|---|
| golgiBody | Inner membrane (Forgejo, primals) | 16d 18h | 6.3G/9.7G (68%) | 20 active |
| peptidoglycan | Sync mediator (relay, builds) | 1d 21h | 6.5G/79G (9%) | 5 system |
| golgiBody-ext | Outer membrane (DNS, sporePrint) | 1d 21h | 2.8G/50G (6%) | 7 system + DNS + Caddy |

## S1 TLS Shadow — GATE PASSED (13+ days)

| Metric | Value |
|---|---|
| beardog-tls-shadow uptime | Since May 19 (13 days) — **exceeds 7-day gate** |
| PID | 82825 |
| Memory | 3.3M / 64M max |
| CPU total | 1.804s (negligible) |
| Behavior | Rejecting scanner probes (expected: invalid JSON, non-UTF8) |
| Cert: git.primals.eco | Let's Encrypt, issued May 28, expires Aug 26 |
| Cert: membrane.primals.eco | Let's Encrypt, auto-renewing via Caddy ACME |
| Caddy TLS | Active since May 28 (3d), 41.2M memory, TLS 1.3 (cipher 4865) |

### S1 Observations
- beardog TLS shadow is stable at minimal resource usage (3.3M RAM, <2s CPU over 13 days)
- Internet scanners are hitting port 8443 — beardog correctly rejects all non-BTSP traffic
- Caddy auto-renewal confirmed working for both `git.primals.eco` and `membrane.primals.eco`
- S1 shadow can be declared PASSED and graduated to OPERATIONAL

## Tower Atomic — Songbird Mesh Hub

| Service | Status | Since | Notes |
|---|---|---|---|
| songbird-membrane | active | May 29 (2d) | Federation port 7700, dark-forest |
| songbird-relay | active | May 28 (3d) | TURN relay, port 3478 |

### Tower Issues Requiring Resolution
1. **tarpc bind conflict**: `Address in use (os error 98)` — previous PID socket not cleaned
2. **Security provider socket missing**: `No such file or directory: /tmp/neural-api-e8b62b6e.sock`
   - Songbird can't complete TLS handshakes without beardog security provider
   - Needs: beardog to expose security provider on the expected socket path
3. **capability.call not found**: `Method not found: capability.call (code -32601)`
   - biomeOS doesn't implement capability.call yet — this is the cross-gate mesh gap

### Tower Data Points
- songbird is listening on federation port 7700 with dark-forest enabled
- TURN relay on 3478 is stable (3.4M memory, 1.968s CPU over 3 days)
- External connection attempts observed from 195.184.76.24, [NUCLEUS_WAN]
- All handshake failures trace back to missing security provider socket

## biomeOS Neural API

| Metric | Value |
|---|---|
| Status | Active since May 28 (3d) |
| Protocol | JSON-RPC 2.0 on Unix socket |
| Socket | /run/membrane/biomeos.sock |
| Dark Forest | Active (direct capability routing) |
| Family Seed | Missing (development mode) |
| Neural API | Fallback mode (socket discovery) |

## Full Service Health Matrix (golgiBody)

| Service | Status | Running Since | Days |
|---|---|---|---|
| hbbs-membrane (RustDesk) | active | May 15 | 17d |
| hbbr-membrane (RustDesk) | active | May 15 | 17d |
| beardog-tls-shadow (S1) | active | May 19 | 13d |
| petaltongue-web | active | May 19 | 13d |
| beardog-membrane | active | May 28 | 4d |
| skunkbat-membrane | active | May 28 | 4d |
| songbird-relay | active | May 28 | 4d |
| coralreef-membrane | active | May 28 | 4d |
| toadstool-membrane | active | May 28 | 4d |
| barracuda-membrane | active | May 28 | 4d |
| loamspine-membrane | active | May 28 | 4d |
| nestgate-membrane | active | May 28 | 4d |
| rhizocrypt-membrane | active | May 28 | 4d |
| sweetgrass-membrane | active | May 28 | 4d |
| biomeos-membrane | active | May 28 | 4d |
| petaltongue-membrane | active | May 28 | 4d |
| squirrel-membrane | active | May 28 | 4d |
| caddy-tls | active | May 28 | 4d |
| songbird-membrane | active | May 29 | 3d |
| forgejo | active | May 31 | 1d |

**20/20 services active. Zero crashes since deployment cycle May 28.**

## Sovereign DNS (Knot)

| Metric | Value |
|---|---|
| Zone | primals.eco (slave) |
| Serial | 2026052213 |
| Master | [RELAY_PUBLIC] (golgiBody) |
| Refresh | Hourly |
| Expiration | 14 days |
| Status | Up-to-date, refreshing every hour |

### DNS Remaining Work
- NS registrar cutover still needed (manual action at registrar)
- Zone serial current, replication healthy between golgiBody (master) → golgiBody-ext (slave)

## Caddy (golgiBody-ext)

- Version: 2.11.3
- Serving sporePrint static site on `:80` from `/opt/ecoPrimals/infra/sporePrint/public`
- K-Derm headers: `X-K-Derm-Layer: outer-membrane`, `X-Gate: golgiBody-ext`, `X-Bond-Type: weak`
- No HTTPS yet on ext (awaiting DNS cutover for cert issuance)

## Impulse Potential State

- 1 active impulse: `projectNUCLEUS deploy script evolution` (ACKED by ironGate Jun 1)
- cellMembrane impulse already discharged (relay evolution complete)

## peptidoglycan Notes

- membrane binary deployed at `/usr/local/bin/membrane` + `/opt/ecoPrimals/gardens/cellMembrane/target/release/membrane`
- Full ecosystem checkout present
- Old bash relay scripts still present (superseded but still running — Rust relay not yet deployed to VPS)
- No primal services running — correct for mediator role

## Actionable Non-Temporal Work

1. **S1 → OPERATIONAL**: Graduate beardog-tls-shadow from shadow to operational (13d > 7d gate)
2. **Tower socket fix**: Configure beardog security provider socket for songbird
3. **capability.call**: Implement in biomeOS or wire through beardog
4. **Family seed**: Deploy production family seed to golgiBody
5. **VPS relay deployment**: Deploy Rust relay.rs to peptidoglycan (replace bash scripts)
6. **DNS NS cutover**: Manual registrar action
7. **golgiBody-ext HTTPS**: Enable once DNS cutover provides cert-issuable domain
