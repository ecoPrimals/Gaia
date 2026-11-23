# rhizoCrypt — Wave 53 Status Ack

**Date**: May 26, 2026
**From**: rhizoCrypt team
**Re**: Wave 53 Primal Mountain Teams Handoff

---

## Status: NO ACTION — Confirmed

v0.14.0, 1,646 tests passing, zero debt markers, zero clippy warnings.

### Wave 49 items completed (prior wave)

- Showcase fossilized to `fossilRecord/primals/rhizoCrypt/showcase_wave49/`
- Startup latency fixed: `announce_to_biomeos()` moved to background
  `tokio::spawn()` — removes up to 7s from critical path
- `0.14.0-dev` → `0.14.0` version suffix dropped (Wave 22 item)
- All stale `target/release/` deployment refs replaced with plasmidBin pattern
- `notify-plasmidbin.yml` active, binary shipping via plasmidBin

### Cold-start latency note

The 8s timeout workaround referenced in the handoff was the
`announce_to_biomeos()` blocking call. This was moved off the critical path
in Wave 49 — service now reports ready in <1s under normal conditions.
The timeout constants (`NEURAL_API_CONNECT_TIMEOUT_SECS = 2`,
`NEURAL_API_READ_TIMEOUT_SECS = 5`) remain for the background announce task
and do not affect readiness.

### Wave 55 readiness

Provenance Trio E2E with loamSpine/sweetGrass in live compositions is the
next natural target. rhizoCrypt's side of the trio pipeline
(`dag.session.create` → `dag.event.append` → `dag.dehydration.trigger`)
is implemented and stable. Awaiting composition orchestration.
