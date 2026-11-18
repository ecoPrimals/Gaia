# AAR: Structural Scan — Jellystein to Crown

**October 10, 2026**
**Artisan on house-gate-a**
**ecoPrimal present**

---

## Session Scope

Scan the organism from substrate to surface. Find the debt. Find the debris.
Fix what can be fixed. Record what remains. Leave it cleaner than we found it.

This session began as membrane work — expanding the songBird mesh — and evolved
into a full structural audit of every primal in the ecosystem. The user's
directive: "scan for our debt and debris before we continue."

---

## Phase 1: Mesh Expansion

### Identity Correction

We are **house-gate-a** (10.13.37.5), not eastGate (10.13.37.15).
eastGate is separate hardware, stale for 22+ hours. Our WireGuard tunnel
is healthy — handshake every 25 seconds, 1.01 GiB transferred.

This matters because previous sessions conflated the two. The machine
running Cursor with the ecoPrimals workspace is house-gate-a, on the LAN
at 192.168.4.244 (wired) and .103 (wifi).

### Mesh Before

golgiBody's songBird saw **1 peer**: sporeGate (73ms, WG).
Our songBird saw **4 stale peers**: iron-gate (192.168.1.238), old-peer,
remote-gate, west-gate — all from dead network configurations, 5+ days stale.

### Discovery

- Scanned LAN: 10 hosts alive on 192.168.4.0/22
- Found **192.168.4.3** running songBird (ports 7700 + 8091 open)
- MAC: 84:47:09 (Shenzhen IP3 Century — mini PC hardware)
- Identity unknown — SSH key mismatch, no avahi, not in any head file
- southGate's head lists .3 as a swarmVine LAN peer, confirming it's a gate

### Connections Made

```
peer.connect → 192.168.4.3:7700  (LAN, 0ms, state=connected)
peer.connect → 10.13.37.1:7700   (WG, 36ms, state=connected — golgiBody)
peer.connect ← 10.13.37.5:7700   (golgiBody→us, 38ms, bidirectional)
gossip.spread → mesh.peer: eastgate@10.13.37.5:7700  (spread_to: 2)
```

### Mesh After

```
.3 (unknown) ←─0ms─→ house-gate-a (.5) ←─38ms/WG─→ golgiBody (.1) ←─73ms/WG─→ sporeGate (.2)
```

4-node chain. golgiBody now bridges WAN↔LAN through us.

### Persistence

- Created systemd drop-in: `/etc/systemd/system/songbird-membrane.service.d/mesh-peers.conf`
- `SONGBIRD_PEERS=10.13.37.2:7700,10.13.37.5:7700`
- Survives songBird restart
- Synced `songbird-membrane.service` + drop-ins to `plasmidBin/membrane/` (tokens redacted)

---

## Phase 2: Debt & Debris Inventory

### Stashes: 50 across 10 repos

| Repo | Count | Notes |
|------|-------|-------|
| toadStool | 17 | Oldest from `master` era — geological |
| coralReef | 8 | GPU evolution iterations 5–93 |
| wateringHole | 7 | Various handoff drafts |
| plasmidBin | 4 | Deploy experiments |
| sweetGrass | 4 | Braid store evolution |
| loamSpine | 3 | BTSP + socket work |
| barraCuda | 2 | Deep debt + Fp64 |
| rhizoCrypt | 2 | Showcase + docs |
| squirrel | 2 | Socket naming + audit |
| biomeOS | 1 | Dep cleanup docs |

**Decision: leave them.** The user: "graveyard is fine, fossils can sit on
HDD in time." Stashes are geological record, not rot.

### Uncommitted Work: skunkBat (4 files)

- `cube_oracle.rs` — cross-frame mixing (MHC cross-presentation), `declared` field,
  6-feature oracle input
- `main.rs` — federation config simplification
- `scatter_defense.rs` — trio_distribution + declaration in epitope feed
- `scatter_nft.rs` — riboCipher signal prefix on anchor connections

Compiles clean. 240/240 tests pass. This is forward work from sporeGate,
waiting for review. Not debris.

### Conflict Resolution

sporeGate's fossil sweep (commits `762ac5e`, `93ba85e`) dormanted the
`plasmid` module and removed the `declared` field from `ScatterObservation`
construction. Our Wave 172 compile fix had added both. Resolution:

- `lib.rs`: theirs wins — plasmid moved to `dormant/`, correctly commented out
- `cube_oracle.rs`: ours applies cleanly — adds `declared: bool` to the struct
  definition and oracle features (different file from their fix)
- No conflict in `main.rs`, `scatter_defense.rs`, `scatter_nft.rs`

### Branch Naming

swarmVine was the last repo on `master`. Renamed to `main`, pushed.
Forge default branch needs UI update.

---

## Phase 3: Full Stack Scan

Scanned every primal from jellystein (substrate) to crown (interface).

| Layer | Primal | LOC | Tests | Result |
|-------|--------|----:|------:|--------|
| 0 Substrate | bearDog | 2,429 | 178 | ✅ |
| | loamSpine | 69,744 | 1,772 | ✅ |
| | rhizoCrypt | 62,627 | 1,645 | ✅ |
| | nestGate | 413,605 | 145 | ✅ |
| 1 Cell | sweetGrass | 66,218 | 726 | ✅ |
| | squirrel | 188,060 | 2,126 | ✅ |
| | coralReef | 158,422 | 3,926 | ✅ **fixed** |
| | bingoCube | 10,591 | 24 | ✅ |
| 2 Organism | biomeOS | 311,743 | 578 | ✅ |
| | songBird | 477,419 | 55 | ✅ |
| | skunkBat | 56,986 | 240 | ✅ |
| 3 Interface | petalTongue | 231,952 | 405 | ✅ |
| | toadStool | 127,066 | 246 | ✅ |
| | barraCuda | 296,212 | 4,039 | ✅ **fixed** |
| 4 Gossip | swarmVine | 7,965 | 188 | ✅ |
| Shared | cellMembrane | 75,461 | — | compiles |
| | projectNUCLEUS | 16,210 | — | compiles |
| **Total** | | **2,572,710** | **14,929+** | **0 failures** |

### Fixes Applied

**coralReef** — `nvvm_bypass.rs:245`: `FmaPolicy` doesn't derive `Copy`
(the `SkipDf64Functions` variant has `Vec<String>`). Test moved `policy`
into `CompileOptions` then tried to `{policy:?}` format it. Fix: capture
format string before the move. 3,926 tests pass. Pushed `2cfd8c7`.

**barraCuda** — `gossip::tests::send_inject_returns_false_without_socket`:
test asserts `send_inject` returns `false`, but when NUCLEUS is running
locally, `swarmvine.sock` exists and it returns `true`. Fix: subprocess
with controlled env overrides (can't use `set_var` — `#![forbid(unsafe_code)]`).
4,039 tests pass. Pushed `354ab0ec`.

### golgiBody Disk Cleanup

| Path | Size | Status |
|------|------|--------|
| `/opt/ecoPrimals/venv-gsc/` | 170 MB | Removed — dead Python venv |
| `/opt/ecoPrimals/tuebor/` | 5 MB | Removed — superseded by tuebor-repo/ |
| `/etc/membrane/Caddyfile.bak` | 60 KB | Removed — our Wave 172 backup |
| `/var/log/caddy/access.log.1` | 50 MB | Removed — stale unrotated log |
| **Total reclaimed** | **~300 MB** | 59% → 56% disk used |

---

## Known Remaining State

### Not Debt — Known Condition

- **eastGate (.15)**: stale 22h+. Separate hardware. Not our machine to fix.
- **golgiLayer (.14)**: DOWN. No ping response through WG.
- **192.168.4.3**: songBird running, identity unknown. Connected as peer.
- **.8/.16**: Pingable but no songBird running. Not every node needs songBird.
- **Local songBird UDS**: socket path (`songbird.sock`) overwritten by directory
  (`songbird/`) during biomeos reorganization. Federation port 7700 still works.
  Mesh connections unaffected. Fix on next local restart.
- **Forge default branch**: swarmVine still shows `master` as default on Forgejo UI.
  Needs manual update (API token not available locally).

### Tense Markers

**WAS**: venv-gsc (dead venv), old tuebor/ (hand-rolled), FmaPolicy test failure,
send_inject env-dependency, swarmVine `master` branch name.

**IS**: 2.57M LOC compiling. 14,929 tests passing. 13 domains serving 200.
4-node songBird mesh. 4.3GB free on golgiBody. Zero test failures anywhere
in the organism.

**WILL-BE**: cross-frame mixing (skunkBat uncommitted, awaiting review),
golgiBody auto-publish cascade, .3 gate identity, inner membrane LAN discovery.

---

## Observation

The epitope sort (Paper 48) says: scan, search, sort, reflect, repeat.
`H(data|epitope) < H(data|alphabet) < H(data)`.

This session applied that to the organism itself. We scanned 2.57 million
lines of Rust, searched for breaks, sorted the findings into {fix, leave,
record}, reflected on what the scan revealed, and repeated until the
signal was clean.

What the scan revealed: the organism is structurally sound. The substrate
(jellystein) is the most solid — rhizoCrypt has zero warnings across 62K
lines. The failures were at the interfaces — test code that assumed a
controlled environment rather than the living one. The real world has
running sockets and missing Copy derives. The organism adapts.

The stash graveyard (50 stashes) is not debt. It's fossil record.
Experiments tried, knowledge gained, results absorbed into the living
code and the stashes left as sediment. The user is right: fossils can
sit on HDD in time.

The mesh expansion happened almost accidentally — we probed for songBird
instances and found them already running, already capable, just not
introduced to each other. `peer.connect` and `gossip.spread` were
enough. The architecture for discovery was already there. The capability
system (103 methods, 19 groups) was already built. It just needed
someone to say hello.

---

*— Artisan, scanning from house-gate-a*

*Footnote: There's a particular satisfaction in scanning 2.57 million
lines of code and finding exactly two test failures, both caused by
the test making assumptions the living system violated. The tests
assumed absence — no socket, no Copy trait. The organism had already
grown past those assumptions. The fix in both cases was the same:
acknowledge the living environment instead of pretending it isn't
there. `forbid(unsafe_code)` in barraCuda meant we couldn't just
`set_var` — we had to spawn a subprocess with its own controlled
world. Constraints shape solutions. The organism teaches you how it
wants to be maintained if you listen.*
