# AAR: golgiBody Fossil Layer — Service & Binary Cleanup

**Wave 167 — October 8, 2026**
**Observer**: eastGate
**Purpose**: Inventory of stale systemd services, orphaned binaries, and protocol mismatches discovered during Python convergence. Actionable cleanup for sporeGate or next session.

---

## Context

During Python convergence (Wave 167), we cleaned the runtime jellystein — 2,096 lines of Python → 0, bloom-live.service removed. But the audit exposed a deeper fossil layer: 19 disabled systemd service files, stale binaries, backup files, and a protocol mismatch on the songbird federation link.

This AAR catalogs everything found so it can be cleaned systematically.

---

## 1. Songbird Federation Protocol Mismatch

**Status**: Songbird IS properly deployed and running (25MB binary, 0.1% CPU, 16MB RAM).

**Problem**: sporeGate (`10.13.37.2`) connects to songbird's federation port (7700) every ~100ms without the riboCipher signal (`0x7B`). Every connection fails:

```
Federation connection from [::ffff:10.13.37.2]:58600 without riboCipher signal (0x7B) — legacy path (deprecated Wave 112, reject Wave 113)
Error serving HTTP connection from [::ffff:10.13.37.2]:58600: invalid HTTP method parsed
```

**Rate**: ~84 errors/hour, sustained. Harmless (songbird rejects cleanly), but noisy in the journal.

**Fix**: Update sporeGate's songbird client to include riboCipher signal in federation connections. The protocol was deprecated at Wave 112 and scheduled for rejection at Wave 113 — sporeGate is still using the pre-112 protocol.

**Songbird WireGuard peers** (for reference):
- `10.13.37.2` (sporeGate) — legacy protocol, 84 errors/hr
- `10.13.37.5` — active, 178MB rx / 1.19GB tx
- `10.13.37.8` — active, 176MB rx / 295MB tx  
- `10.13.37.14` — light, 121KB rx / 82KB tx
- `10.13.37.15` — light, 124KB rx / 86KB tx

---

## 2. Disabled Systemd Service Files (19 files)

These unit files exist in `/etc/systemd/system/` but are disabled. They are fossils from earlier architecture iterations — either superseded by newer naming conventions, never deployed on golgiBody, or disabled during refactors.

### Safe to remove (superseded by active services)

| Service File | Description | Superseded By |
|---|---|---|
| `skunkbat-membrane.service` | SkunkBat Defense (old naming) | `skunkbat.service` (active) |
| `squirrel-membrane.service` | Squirrel AI (disabled duplicate) | `squirrel-membrane.service` (active, different unit) |
| `petaltongue-membrane.service` | petalTongue (old naming) | `membrane-petaltongue.service` (active) |
| `nestgate-membrane.service` | NestGate CAS (old naming) | `nestgate-sporeprint.service` (active) |
| `songbird-gateway.service` | songBird mesh hub (old naming) | `songbird-membrane.service` (active) |

### Safe to remove (no binary on golgiBody)

| Service File | Description | Notes |
|---|---|---|
| `barracuda-membrane.service` | barraCuda — pure math | Not deployed on golgiBody |
| `biomeos-membrane.service` | biomeOS — Neural API | Not deployed on golgiBody |
| `coralreef-membrane.service` | coralReef — shader compilation | Not deployed on golgiBody |
| `loamspine-membrane.service` | loamSpine — permanent ledger | Not deployed on golgiBody |
| `rhizocrypt-membrane.service` | rhizoCrypt — ephemeral DAG | Not deployed on golgiBody |
| `sweetgrass-membrane.service` | sweetGrass — attribution braids | Not deployed on golgiBody |
| `toadstool-membrane.service` | ToadStool — compute dispatch | Not deployed on golgiBody |

### Review before removing (may have residual purpose)

| Service File | Description | Notes |
|---|---|---|
| `songbird-relay.service` | Songbird TURN Relay (port 3478) | Disabled. Binary exists (`songbird relay` subcommand). No credentials file at `/etc/songbird/relay-credentials`. Remove if TURN not needed. |
| `hbbr-membrane.service` | RustDesk Relay Server | Disabled. Binary `/opt/membrane/hbbr` exists (3.3MB). |
| `hbbs-membrane.service` | RustDesk Rendezvous Server | Disabled. Binary `/opt/membrane/hbbs` exists (9.5MB). |
| `beardog-sporeprint.service` | BearDog ACME gateway | Disabled. May be needed for sovereign TLS. |
| `membrane-bridge-beardog.service` | UDS→TCP bridge: bearDog | Disabled. Cross-node bridge for multi-VPS. |
| `membrane-bridge-biomeos.service` | UDS→TCP bridge: biomeOS | Disabled. Cross-node bridge for multi-VPS. |
| `membrane-bridge-forgejo.service` | TCP→private net: Forgejo | Disabled. Cross-node bridge for multi-VPS. |

### Decision: bridge services

The `membrane-bridge-*.service` files are infrastructure for the golgiLayer multi-VPS deployment. They'll be needed when golgiLayer2-5 are created (pending VPS creation task). **Keep these** until the federation layer is built, then update or replace.

---

## 3. Enabled But Inactive Services (will start on reboot)

These are **enabled** in systemd but currently **not running**. They will attempt to start on next reboot.

| Service | Status | Risk |
|---|---|---|
| `beardog-tls-shadow.service` | enabled, inactive | Will try to start on reboot. May conflict or fail if config is stale. |
| `membrane-socket-bridge.service` | enabled, inactive | Will try to start on reboot. |
| `petaltongue-sporeprint.service` | enabled, inactive | Will try to start on reboot. Superseded by `membrane-petaltongue`? |
| `petaltongue-web.service` | enabled, inactive | Will try to start on reboot. |

**Action**: Either disable these or verify they're still needed. They're ticking time bombs — harmless now but will cause noise/failures on next reboot.

---

## 4. Stale Binaries and Files in /opt/membrane/

### RustDesk binaries (unused)

| File | Size | Notes |
|---|---|---|
| `/opt/membrane/hbbr` | 3.3 MB | RustDesk relay, disabled |
| `/opt/membrane/hbbs` | 9.5 MB | RustDesk rendezvous, disabled |
| `/opt/membrane/id_ed25519` | 88 B | RustDesk relay key |
| `/opt/membrane/id_ed25519.pub` | 44 B | RustDesk relay pubkey |

**Total**: 12.8 MB. Remove if RustDesk relay is no longer needed.

### Orphaned database

| File | Size | Notes |
|---|---|---|
| `/opt/membrane/db_v2.sqlite3` | 24 KB | SQLite 3.x, not open by any process |
| `/opt/membrane/db_v2.sqlite3-shm` | 32 KB | WAL shared memory (stale) |
| `/opt/membrane/db_v2.sqlite3-wal` | 330 KB | WAL journal (stale) |

**Total**: 386 KB. Not in use. Check if any service needs it before removing (likely old RustDesk state).

### NFT contributions

| File | Size | Notes |
|---|---|---|
| `/opt/membrane/contributions.jsonl` | 1.3 KB | 8 entries, NFT test contributions. Actively written (Oct 8). |

**Keep** — active NFT scatter counter state.

### Backup binaries in /usr/local/bin/

| File | Size | Date | Notes |
|---|---|---|---|
| `/usr/local/bin/membrane.bak` | 18.6 MB | Oct 5 | One version old |
| `/usr/local/bin/membrane.bak-20260925` | 17.3 MB | Sep 25 | Two versions old |
| `/usr/local/bin/songbird` | 26.8 MB | Jul 24 | Old copy (current is `/opt/membrane/songbird`, Oct 5) |

**Total**: 62.7 MB of stale backups.

### Binary location split

Active binaries are split between two locations:

| Location | Binaries |
|---|---|
| `/opt/membrane/` | caddy, skunky-ingest, skunkbat, swarmvine, membrane, songbird, squirrel |
| `/usr/local/bin/` | beardog, forgejo, membrane (duplicate), songbird (old duplicate) |

**Note**: `beardog` and `forgejo` are only in `/usr/local/bin/`, not in `/opt/membrane/`. The service files reference them by name (found via PATH). Consider standardizing all binaries to `/opt/membrane/` for consistency.

---

## 5. Fossil Archive Status

Fossils directory is well-organized:

```
/opt/membrane/fossils/
├── bloom-live-converged/          ← Wave 167 (this session)
│   ├── bloom_live.py (31 KB)
│   └── investigation_export.py (6.4 KB)
├── entity-topology-converged/     ← Wave 167 (this session)
│   └── entity_topology.py (22 KB)
├── bloom_live_v2.py.fossil        ← Wave 165i
├── bloom_live_v3.py.fossil        ← Wave 165i
├── entity_topology.pre-epitope.py ← Wave 165i
├── epitope_bridge.py.fossil       ← Wave 167
├── epitope_bridge.sh.fossil       ← Wave 165i
├── feed-to-repo.fossil.sh
├── forgejo-watchdog.fossil.sh
├── membrane-inflammatory.fossil.*
├── plasmid-federation.fossil.sh
├── skunky-backups/                ← 2 old skunky-ingest binaries
│   ├── skunky-ingest-musl
│   └── skunky-ingest.bak.1791404109
├── tower-shadow-benchmark.fossil.*
└── wg0.conf.pre-wave166

/opt/ecoPrimals/fossils/
└── signal-writer-converged/       ← Wave 167 (this session)
    ├── gen-signal-data.py (27 KB)
    └── refresh-signal-data.sh (830 B)
```

No action needed — fossils directory is clean.

---

## Recommended Cleanup Sequence

### Phase 1: Quick wins (safe, no risk)

```bash
# Remove superseded service files
rm /etc/systemd/system/skunkbat-membrane.service
rm /etc/systemd/system/petaltongue-membrane.service
rm /etc/systemd/system/nestgate-membrane.service
rm /etc/systemd/system/songbird-gateway.service

# Remove services for non-deployed binaries
rm /etc/systemd/system/barracuda-membrane.service
rm /etc/systemd/system/biomeos-membrane.service
rm /etc/systemd/system/coralreef-membrane.service
rm /etc/systemd/system/loamspine-membrane.service
rm /etc/systemd/system/rhizocrypt-membrane.service
rm /etc/systemd/system/sweetgrass-membrane.service
rm /etc/systemd/system/toadstool-membrane.service

# Remove stale backups
rm /usr/local/bin/membrane.bak
rm /usr/local/bin/membrane.bak-20260925
rm /usr/local/bin/songbird  # old copy; current is /opt/membrane/songbird

# Reload systemd
systemctl daemon-reload
```

**Reclaims**: ~63 MB disk, 11 stale unit files removed.

### Phase 2: Disable reboot time bombs

```bash
systemctl disable beardog-tls-shadow
systemctl disable membrane-socket-bridge
systemctl disable petaltongue-sporeprint
systemctl disable petaltongue-web
```

### Phase 3: Decide (needs human judgment)

1. **RustDesk** — remove hbbr/hbbs/id_ed25519 + service files? Or keep for remote access?
2. **songbird-relay** — remove if TURN relay not needed?
3. **membrane-bridge-*** — keep for golgiLayer federation? Or remove and recreate when VPS layer exists?
4. **squirrel-membrane.service (disabled)** — the active one is also called `squirrel-membrane.service` (enabled). Verify they're the same unit or remove the disabled one.
5. **beardog-sporeprint.service** — still needed for sovereign TLS?

### Phase 4: Songbird protocol fix

Update sporeGate's songbird federation client to include riboCipher signal (`0x7B`) in connections. Current protocol deprecated at Wave 112, rejection scheduled at Wave 113.

---

## System State After Full Cleanup (projected)

| Metric | Before | After |
|---|---|---|
| Service files | 37 | ~22 |
| Enabled services | 16 | 12 |
| Stale binaries | 63 MB | 0 |
| Reboot time bombs | 4 | 0 |
| Journal noise (songbird) | 84 errors/hr | 0 (after peer update) |

---

*The jellystein is gone. Now we're finding the geological strata underneath — service files from Wave 112, binary backups from September, RustDesk relays from July. Each layer tells a story of the system's evolution. Clean it up and the geology becomes simple: one Rust binary per function, one service file per binary, no ghosts.*

*Wave 167 — October 8, 2026*
