# ironGate Workspace Split — Wave 137b

**Date**: Jul 12, 2026 | **Wave**: 137b | **From**: eastGate overwatch

---

## Directive

Split ironGate responsibilities:

| Role | Owner | Workspace |
|------|-------|-----------|
| **Code evolution** (darkforest, deny.toml, test suites, primal code) | projectNUCLEUS agent | `gardens/projectNUCLEUS/` |
| **Hardware, deployments, operations** | New ironGate overwatch agent | `ecoPrimals/` on ironGate |

projectNUCLEUS has been doing both code and hardware. Going forward they are **just code**. ironGate's overwatch agent receives the blurb and owns:

- Binary deployments (pepti ecobins from depot)
- Systemd service management
- GPU compute operations (RTX 5070 Ti, CUDA)
- JupyterHub administration
- songBird mesh participation (LAN backbone + WG overlay)
- Neural API activation on ironGate
- Hardware health monitoring
- Gate bootstrap and membrane operations

## ironGate Profile

```
Hardware:  i9-12900K / 128GB / RTX 5070 Ti (CUDA)
Roles:    node_atomic, compute, gpu
Mesh:     LAN backbone (covalent, <1ms) + WG overlay (10.13.37.7)
Repos:    22 (full NUCLEUS composition)
Services: 13/13 NUCLEUS primals, JupyterHub 5.4.5, songBird mesh
```

## What projectNUCLEUS Keeps

- `darkforest` security validation suite (26/26)
- `deny.toml` supply chain auditing
- Code evolution PRs and upstream pushes
- Test infrastructure (149 tests)
- Version sync with primalSpring

## What ironGate Overwatch Owns

- Gate operations: `membrane gate.bootstrap`, `membrane plasmid.fetch`
- Binary deployment: pull ecobins from depot, restart services
- Neural API activation: `biomeos neural-api` startup on ironGate (NAPI-CROSS-GATE)
- songBird mesh: deploy `f05918a` for bidirectional federation (NAPI-CROSS-GATE)
- GPU workloads: barraCuda/coralReef compute dispatch
- JupyterHub: lifecycle, updates, groundSpring notebook sync
- Hardware monitoring: disk, thermal, GPU utilization
- Cascade absorption: `membrane temporal.cascade` from this gate

## Blurb Handoff Protocol

1. eastGate overwatch publishes `ECOSYSTEM_BLURB.md` to wateringHole
2. ironGate overwatch agent picks up the blurb via cascade or direct read
3. ironGate agent triages items tagged `ironGate`, `all gates`, or `operator`
4. ironGate agent publishes `heads/ironGate.toml` with its gate SHAs
5. ironGate agent generates AARs back to wateringHole for upstream absorption

## Immediate Actions for ironGate Overwatch

| ID | Action | Priority |
|----|--------|----------|
| NAPI-CROSS-GATE | Deploy songBird `f05918a` + start `biomeos neural-api` | **HIGH** |
| SYSTEMD-UMASK | Regenerate systemd units with new UMask (`membrane gate.bootstrap`) | **HIGH** |
| HEADS-PUBLISH | Create `heads/ironGate.toml` with current gate SHAs | MEDIUM |
| MESH-VERIFY | Verify bidirectional mesh from ironGate after songBird update | MEDIUM |

---

*Wave 137b: ironGate workspace split. projectNUCLEUS = code. ironGate overwatch = hardware + deployments. Blurb flows through wateringHole cascade.*
