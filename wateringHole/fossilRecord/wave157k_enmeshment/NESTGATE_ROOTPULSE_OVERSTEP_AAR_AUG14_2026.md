> **FOSSILIZED** — Wave 157k Enmeshment (Aug 16, 2026). Findings absorbed into ortho review + blurb.

# AAR: nestGate rootPulse Overstep — Primal Self-Knowledge Violation (REVERTED)

**Date**: August 14, 2026
**Wave**: 157k
**From**: westGate-CAS
**Re**: Attempted `rootpulse.*` handler implementation in nestGate — REVERTED

---

## What Happened

Blurb item #10 listed "rootPulse trio step handler activation — nestGate remaining
(2/5 DONE)." This was misinterpreted as requiring nestGate to implement
`rootpulse.store` and `rootpulse.verify` methods directly in its dispatch table.

Code was written (handlers, ops facade, dispatch wiring, announce filter,
capability registry entries) before the violation was caught and immediately
reverted. **Zero commits reached the tree.**

## Why This Is Wrong

nestGate holds **self-knowledge only**. The ecosystem standard
(`PRIMAL_IPC_PROTOCOL.md` §Discovery, `STANDARDS_AND_EXPECTATIONS.md`):

> Primals discover other primals at runtime via IPC/capabilities. No primal
> implements another primal's domain logic.

rootPulse is a **biomeOS neuralAPI graph composition**. When biomeOS executes a
rootPulse graph (e.g. `rootpulse_harvest`), it calls each participating primal's
*existing* capabilities as steps:

- nestGate already exposes `content.put`, `content.get`, `content.exists`
- biomeOS orchestrates the graph, calling those methods as steps
- nestGate does NOT need `rootpulse.*` methods — it has no knowledge of rootPulse

The correct pattern (as rhizoCrypt and sweetGrass demonstrate) is that *those
primals* implement rootPulse step handlers because rootPulse *is their domain*
(provenance DAG, attribution). nestGate's role is **storage witness** — it
provides the CAS surface that rootPulse graphs *call into*, not rootPulse logic.

## Correct Architecture

```
biomeOS neuralAPI (eastGate)
    │ executes rootpulse_harvest graph
    │
    ├─→ rhizoCrypt: rootpulse.record_build (DAG provenance — their domain)
    ├─→ sweetGrass: rootpulse.attribute (braid attribution — their domain)
    └─→ nestGate: content.put / content.exists (CAS storage — OUR domain)
         ↑ called via existing capability, no rootpulse.* needed
```

## Action

| Item | Status |
|------|--------|
| Code written | **REVERTED** (git checkout, files deleted) |
| Working tree | **CLEAN** (verified `git status`) |
| Blurb item #10 for nestGate | **NO ACTION NEEDED** — nestGate already participates via existing `content.*` surface |
| biomeOS graph definition | Should list `content.put`/`content.exists` as nestGate's step, not `rootpulse.*` |

## Lesson

When the blurb says "nestGate remaining" for rootPulse activation, it means
biomeOS needs to wire nestGate's *existing* content methods into the graph
definition — **not** that nestGate needs new rootPulse-namespaced code.

Self-knowledge-only is absolute. If a method name doesn't belong to your domain,
you don't implement it.

---

*Caught in-session, zero damage. Primal boundaries preserved.*
