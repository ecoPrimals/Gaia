# Tower Atomic Validation — Gate Team Handoff — Wave 155i

**Date**: Jul 29, 2026 | **Wave**: 155i | **From**: eastGate overwatch
**Purpose**: Validate Tower Atomic stability on all LIVE gates before Nest
Atomic proceeds. Tower is the foundation — Nest depends on bearDog + songBird +
nestGate being healthy and responsive on every gate.

---

## WHY THIS FIRST

The Orthogonal Review (D4 Inner Membrane) states:

> Tower Atomic needs live validation on all LIVE gates — `tower.health`
> signal graph dispatch on westGate + strandGate before Nest Atomic proceeds.

Nest Atomic stacks on Tower. If Tower isn't proven stable, Nest pipelines
will fail at the foundation layer. This handoff validates Tower before we
wire Provenance Trio IPC and start AlphaFold ingestion.

---

## VALIDATION MATRIX

| Gate | Tower Status | Action | Owner |
|------|-------------|--------|-------|
| **eastGate** | LIVE (code hub) | Validate `tower.health` — confirm bearDog + songBird responsive | eastGate overwatch |
| **westGate** | TOWER LIVE | Validate `tower.health` + `tower.mesh_status`. This gate hosts Nest Atomic — must be solid. | westGate team |
| **strandGate** | TOWER+COMPUTE LIVE | Validate `tower.health` + `tower.mesh_status`. Compute Trio (barraCuda + coralReef + toadStool) must be healthy. | strandGate team |
| **sporeGate** | ONLINE | Validate Tower components (bearDog + songBird). Build authority — depot must be healthy. | sporeGate team |
| **northGate** | ONLINE (Windows) | **Assess Tower status.** 10.13.37.8 on WG mesh but Tower may not be deployed. G1 validation target. Required for AlphaFold cross-gate federation. | overwatch / northGate |
| **ironGate** | ONLINE | Validate Tower. HDD enclave work secondary. | ironGate team |
| **flockGate** | ONLINE | Validate Tower. Nest Atomic validation target (after westGate). | flockGate team |
| **grapheneGate** | TOWER LIVE (Android) | Health check via eastGate tether. Beacon seed + mobile Tower. | eastGate overwatch |

---

## HOW TO VALIDATE

### Signal Graph Dispatch (preferred)

biomeOS shipped `tower_health.toml` (Wave 155d). On each gate:

```bash
biomeos dispatch tower.health
```

Expected response: bearDog health OK, songBird health OK, nestGate health OK,
all capabilities discoverable.

### Manual Probe (if biomeOS not deployed on a gate)

```bash
# Check bearDog
echo '{"jsonrpc":"2.0","method":"health.check","params":{},"id":1}' | \
  socat - UNIX-CONNECT:${BIOMEOS_SOCKET_DIR}/beardog.sock

# Check songBird
echo '{"jsonrpc":"2.0","method":"health.check","params":{},"id":1}' | \
  socat - UNIX-CONNECT:${BIOMEOS_SOCKET_DIR}/songbird.sock

# Check nestGate
nestgate health
```

### What to Report

For each gate, report:
1. **bearDog**: responding? version? BTSP status?
2. **songBird**: responding? discovery working? mesh peers visible?
3. **nestGate**: responding? CAS healthy? storage paths resolved?
4. **WireGuard**: `wg show wg0` — handshake recent? peers connected?
5. **biomeOS**: socket dir exists? signal graphs discoverable?

---

## OPEN TOWER ITEMS (from Orthogonal Review)

| Item | Dimension | Priority | Status |
|------|-----------|----------|--------|
| P0: glibc depot target for GPU primals | D2, D8 | P0 | OPEN — sporeGate build team |
| Tower on Windows (G1) | D8 | Glacial | OPEN — northGate + blueGate + swiftGate |
| WireGuard DNS catch-all in wg0 template | D4 | P1 | OPEN — cellMembrane |
| bearDog ACME Phase 2 client | D2 | P1 | songBird needs it for G6 |
| J8 step-ca deployment on golgiBody | D10 | P1 | Code shipped, deployment pending |
| grapheneGate HSM not on eastGate | D2 | P2 | Only remaining Tower debt item |
| Only 2 WG peers active (enrollment pending) | D4 | P1 | House2 gates need enrollment |

---

## NORTHGATE TOWER ASSESSMENT

northGate is the critical path for AlphaFold cross-gate federation:

- **Platform**: Windows 11, RTX 5090, 2.5G ethernet
- **Mesh**: 10.13.37.8 on WireGuard mesh
- **Tower status**: UNCLEAR — may have bearDog + songBird from prior wave, may not
- **Needed for**: `content.replicate.pull` from westGate for AlphaFold data

**Assessment steps**:
1. Remote in via RustDesk (or WireGuard SSH if available)
2. Check if bearDog / songBird / nestGate processes running
3. If not: deploy Tower Atomic via startup blurb pattern
4. If yes: validate health, confirm nestGate CAS operational
5. Test WireGuard connectivity: `ping 10.13.37.11` (westGate)

**Fallback** if northGate Tower isn't ready quickly: stage AlphaFold
data to westGate via USB/rsync and ingest locally. Provenance still
traces via `.meta.json` sidecar with `"origin": "northGate"`.

---

## SEQUENCING

```
[NOW]  Tower health validation — all LIVE gates
[NOW]  northGate Tower assessment
[NOW]  P0 glibc depot target (sporeGate build)
  ↓
[THEN] sweetGrass G3 wiring (handoff issued)
[THEN] westGate ZFS pool creation
  ↓
[THEN] E2E Nest Atomic validation (small PDB test)
[THEN] AlphaFold bulk ingestion (~1TB)
```

Tower stable → Nest wiring → Nest validation → data ingestion.

---

## REPORT BACK

Gate teams: after validation, file a brief report in your gate's handoff
channel or respond to this handoff with:

```
Gate: <name>
Tower: HEALTHY / DEGRADED / NOT DEPLOYED
bearDog: OK / FAIL / N/A
songBird: OK / FAIL / N/A
nestGate: OK / FAIL / N/A
WireGuard: X peers, last handshake <time>
Issues: <any blockers>
```

Overwatch will aggregate into the next wave cascade.

---

*Tower Atomic is the foundation. Validate it across the fleet before
building Nest Atomic on top. This is not optional — Nest pipelines
(CAS → DAG → certificate → braid) fail if Tower components are unhealthy.*
