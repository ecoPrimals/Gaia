# Fossil Record — Wave 132h (July 5-6, 2026)

**Fossilization date**: Jul 6, 2026
**Wave**: 132h — LAN+WAN MESHED
**Posture at fossilization**: E2E LIVE, all mesh peered, zero P1 upstream debt

## What was archived

### FRAGOs (5) — all completed, objectives achieved
- `FRAGO_GOLGI_BIDIRECTIONAL_RELAY_WAVE132E_JUL04_2026.md` — relay LIVE, 39/39 parity
- `FRAGO_IRONGATE_JUPYTERHUB_WAVE132E_JUL04_2026.md` — JupyterHub 5.4.5 returning 200
- `FRAGO_SPOREGATE_GATEHOUSE_CUTOVER_WAVE132G_JUL05_2026.md` — Caddy retired, bearDog gatehouse active
- `IRONGATE_WAVE132_COMPUTE_REGISTRATION_JUL04_2026.md` — compute capabilities registered
- `SPOREGATE_WAVE132_GATEWAY_WIRING_JUL04_2026.md` — gateway wired to drawbridge :7780

### Superseded deployment docs (moved from top-level)
- `CELLMEMBRANE_FIELDMOUSE_DEPLOYMENT.md` — superseded by Gatehouse/Darkforest standard
- `DNS_NS_CUTOVER_INSTRUCTIONS.md` — pre-gatehouse DNS instructions (golgi still owns IP)
- `DNS_NS_CUTOVER_OPERATOR_CHECKLIST.md` — companion to above
- `S1_TLS_GRADUATION_CHECKLIST.md` — pre-gatehouse TLS plan (bearDog now owns TLS)
- `WESTGATE_ENROLLMENT_OPERATOR_CHECKLIST.md` — westGate hardware never materialized
- `SONGBIRD_VIRTUAL_ENDPOINT_RELAY_DESIGN.md` — superseded by drawbridge implementation

### Deprecated freshness file
- `freshness.toml` — deprecated, replaced by wave.toml + heads/*.toml

## What remains active

All evergreen standards (BTSP, CAPABILITY_WIRE, DARK_FOREST, etc.) remain in place.
The ecosystem's active coordination document is `handoffs/ECOSYSTEM_BLURB.md`.
Wave metadata lives in `wave.toml` + `heads/*.toml`.

## Achievements at fossilization

- E2E HTTP path: internet → golgi TLS → sporeGate drawbridge → ironGate JupyterHub → 200
- LAN mesh: sporeGate↔ironGate peered (FAMILY_ID trust)
- WAN mesh: flockGate peered via golgi relay (2 reachable peers)
- Pepti warehouse: all architectures built and published
- Caddy: permanently retired on sporeGate
- All 39 repos at GitHub↔Forgejo parity
- 13/13 primals STANDBY, 0 known debt
- primalSpring: 1095 tests passing, 122 scenarios, 0 failures
