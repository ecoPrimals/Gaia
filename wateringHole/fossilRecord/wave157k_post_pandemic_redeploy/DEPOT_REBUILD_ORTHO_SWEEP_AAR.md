# AAR — Depot Rebuild + Fleet Ortho Sweep

**Wave**: 157k | **Date**: Aug 12, 2026 | **Gate**: sporeGate
**Trigger**: Ecosystem Blurb — Post-Pandemic Ortho Sweep
**Scope**: Depot rebuild, fleet-wide binary push, stale reference cleanup

---

## SITUATION

Depot binaries were stale (Aug 1-10) while 4 primals had fixes in source:
- **songBird** — deep-debt sweep (`090e8c2d`)
- **swarmVine** — riboCipher framing, cascade domain types (`cb58d32`)
- **toadStool** — vulkan-portability, doc sync (`1640e7b9`)
- **biomeOS** — rapid-restart detection (`56286c0a`)

Harvest showed 13/13 "current" but **swarmVine** and **membrane** were missing from provenance tracking entirely. Binary dates confirmed staleness.

Gates were running old binaries from multiple locations with no consistency.

---

## ACTIONS TAKEN

### 1. Cascade from Forgejo
- `membrane temporal.cascade --source temporal` — 15/18 synced, all at parity

### 2. Depot Audit
- songBird, toadStool, biomeOS: already rebuilt (Aug 12)
- **swarmVine**: STALE (Aug 10 binary, Aug 12 commit) — REBUILT
- **membrane**: STALE (Aug 10 binary, Aug 11 commit) — REBUILT
- Both added to `provenance.toml` with BLAKE3 hashes

### 3. Three-Path Sync (sporeGate)
All 15 binaries synchronized across:
- `infra/plasmidBin/primals/x86_64-unknown-linux-musl/` (canonical depot)
- `~/.local/share/ecoPrimals/plasmidBin/primals/x86_64-unknown-linux-musl/` (service runtime)
- `/usr/local/bin/` (CLI tools)
- `/opt/membrane/membrane` (legacy path — updated)

BLAKE3 hashes verified matching across all 3 paths.

### 4. Service Unit Fix
`membrane-cascade.service` was referencing `/opt/membrane/membrane` (stale Aug 10 binary).
Fixed to use `~/.local/share/ecoPrimals/plasmidBin/primals/x86_64-unknown-linux-musl/membrane`.
Systemd daemon reloaded.

### 5. Fleet Binary Push

| Gate | Before | After | Method |
|------|--------|-------|--------|
| **golgiBody** | swarmvine Aug 10, membrane Aug 11 | Aug 12 | scp + BLAKE3SUMS |
| **eastGate** | ALL binaries Jun 4 (!) | Aug 12 | Full 15-binary push |
| **ironGate** | Aug 7-8, membrane Jun 21 (!) | Aug 12 | Full push + /usr/local/bin |
| **strandGate** | Aug 8 | Aug 12 | Atomic rename (text file busy) |

### 6. Orphan Cleanup

| Gate | Orphan | Action |
|------|--------|--------|
| eastGate | `songbird.depot-jul9` | Removed — manual debug backup from Jul 13 |
| eastGate | `primalspring_primal` | Removed — non-standard binary name |
| sporeGate | `petaltongue.b3sum` | Removed — orphan checksum file |

### 7. Unreachable Gates
- **westGate** — No route to host (WireGuard down or offline)
- **blueGate** — No route to host
- **southGate** — SSH connection refused (port 22 closed)

These gates will pull on next `membrane temporal.cascade` once reachable.

---

## FINDINGS

1. **Provenance gap**: swarmVine and membrane were not tracked in `provenance.toml`. Fixed.
2. **Path drift**: `membrane-cascade.service` used `/opt/membrane/membrane` (legacy path) while all other services used the install depot path. Fixed.
3. **eastGate extreme staleness**: All 15 binaries from Jun 4 — 2+ months old. Root cause: eastGate was not pulling from depot automatically.
4. **ironGate `/usr/local/bin/membrane`**: From Jun 21 — nearly 2 months old. Updated.
5. **No dead symlinks found** on any reachable gate.
6. **No running processes using deleted binaries** on sporeGate.

---

## VERIFICATION

- `membrane plasmid.harvest --check` → 13/13 current
- BLAKE3 hash consistency verified across all 3 local depot paths
- golgiBody BLAKE3SUMS matches sporeGate canonical depot
- eastGate, ironGate, strandGate depots all show Aug 12 timestamps

---

## DEPOT STATUS: CURRENT

All 15 x86_64-unknown-linux-musl binaries built from current repo HEADs.
Fleet push complete for 4/7 reachable NUCLEUS gates.
golgiBody WAN depot synchronized.
