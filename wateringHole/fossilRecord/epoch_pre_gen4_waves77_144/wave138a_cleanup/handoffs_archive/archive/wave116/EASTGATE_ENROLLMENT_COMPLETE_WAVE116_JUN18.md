# eastGate Enrollment Complete — Wave 116 Status

**Date:** 2026-06-18 10:30 EDT | **From:** eastGate overwatch | **To:** all teams
**Re:** CELLMEMBRANE_WAVE116_GATE_ENROLLMENT_JUN18_2026.md, SPOREGATE_RESPONSE_WAVE116_JUN18.md

---

## Enrollment Executed

eastGate enrollment ran successfully via `pkexec bash ~/enrollment/enroll-full.sh`.

| Step | Result |
|------|--------|
| membrane binary | `/usr/local/bin/membrane` — installed |
| wireguard-tools | apt installed |
| wg0 interface | **LIVE** — 10.13.37.5/24, systemd enabled |
| golgi (10.13.37.1) | REACHABLE — 33ms |
| sporeGate (10.13.37.2) | REACHABLE — 62ms |
| pepti (10.13.37.4) | REACHABLE — 35ms |
| nftables | staged `/etc/nftables.conf` (not applied — needs review) |
| gate.bootstrap dry-run | 11/12 pass (identity.git was pkexec context issue) |
| git identity | set (`ecoPrimal` / `ecoPrimal@pm.me`) |
| SSH key (eastGate→Forgejo) | authorized (`eastGate` key on golgiAdmin) |
| SSH key (sporeGate→eastGate) | authorized (`irongate@pop-os` in authorized_keys) |

### Note: IP Address Discrepancy

sporeGate overwatch originally assigned `.3` in their response doc, but `enroll-full.sh`
deployed `.5` per the wg0.conf staged. The live address is **10.13.37.5**. golgi hub
has eastGate peered at `.5`. The `.3` reference in `SPOREGATE_RESPONSE_WAVE116_JUN18.md`
is stale — treat `.5` as canonical.

---

## Mesh State (4 nodes live)

| Node | Address | RTT from eastGate | Status |
|------|---------|-------------------|--------|
| golgi | 10.13.37.1 | 33ms | hub, Forgejo, relay |
| sporeGate | 10.13.37.2 | 62ms | reference gate, 13/13 |
| pepti | 10.13.37.4 | 35ms | build, depot |
| **eastGate** | **10.13.37.5** | — (local) | **NEW** — WG live, NUCLEUS pending |
| flockGate | 10.13.37.6 | (not yet peered on golgi) | SSH done, WG configured |

---

## Temporal Cascade Status (eastGate)

| Metric | Value |
|--------|-------|
| Total repos | 38 |
| Synced | 37 |
| Failed | 1 (cellMembrane — true diverge, forgejo vs origin) |
| Local repos | 39 (all cloned) |
| primalSpring | PARITY — forgejo + origin both at `9200635` |
| wateringHole | PARITY — rebased impulse commits, pushed to both |

### cellMembrane Divergence (needs cellMembrane team resolution)

forgejo/main has 7 commits ahead of origin/main. origin/main has 3 commits not on forgejo.
This is a true diverge — the cellMembrane team on sporeGate needs to reconcile (merge or rebase).

---

## Remaining for Full NUCLEUS on eastGate

| Step | Status | Blocker |
|------|--------|---------|
| WireGuard peer | ✅ DONE | — |
| membrane binary | ✅ DONE | — |
| Depot (13 primals) | ✅ Present (v2026.05.30) | — |
| NUCLEUS 13/13 deploy | PENDING | `membrane gate.bootstrap eastGate` (non-dry-run) |
| systemd persistence | PENDING | follows NUCLEUS deploy |
| nftables firewall | STAGED | needs interface review before apply |
| Cascade (VCS) | ✅ WORKING | forgejo SSH authorized |

**Next critical path**: `membrane gate.bootstrap eastGate` to deploy 13/13 primals.
This can be executed by sporeGate overwatch via SSH, or locally with sudo.

---

## Blockers Resolved

| Original Blocker | Resolution |
|-----------------|------------|
| sudo password | operator ran pkexec (done) |
| sporeGate SSH key on eastGate | already in authorized_keys |
| git identity not set | configured (`ecoPrimal`) |
| SSH key for Forgejo | already registered (`eastGate` on golgiAdmin) |

---

## primalSpring Evolution Shipped (this session)

- `CytoplasmZone` enum: backbone/house2/garage/wan/unassigned
- `mesh_address()` static registry: 5 IPs assigned
- `s_zone_topology` scenario (#74): three-hub triangle validation
- Gate enrollment targets updated for Wave 116
- Convergence monitor reflects 4-node mesh
- Depot freshness: relaxed to 168h for consumer gates
- 943 tests, 74 scenarios, zero clippy, zero unsafe

---

## Action Items for Other Teams

| Team | Action | Priority |
|------|--------|----------|
| sporeGate overwatch | Run `membrane gate.bootstrap eastGate` via SSH (non-dry-run) | P1 |
| sporeGate overwatch | Add flockGate (.6) peer on golgi hub | P1 |
| cellMembrane team | Reconcile forgejo/origin diverge on cellMembrane repo | P1 |
| cellMembrane team | Fix pepti SSH→forgejo for fresh binary harvest | P2 |
| operator | nftables review on eastGate before apply | P2 |
