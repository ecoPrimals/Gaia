# Showcase Fossilization Standard

**Status**: Active  
**Scope**: All primals and springs in the ecoPrimals ecosystem  
**Effective**: May 2026 (Wave 34 climate shift)

---

## Purpose

Showcases were the primordial scaffolding — the evolutionary stepping stones that
proved out atomics and interactions before they crystallized into springs and
production primal code. As the ecosystem matures, many showcases have been
**mined** into spring experiments, superseded by production APIs, or simply
drifted from current interfaces.

This standard defines how to **fossilize** stale or mined showcases: preserve
them as historical artifacts while cleaning the live tree, so that each primal's
`showcase/` directory reflects only genuinely current, runnable demonstrations.

## Definitions

| Term | Meaning |
|------|---------|
| **Fossilize** | Move to `fossilRecord/` with provenance metadata; not deleted, always recoverable |
| **Mined** | Pattern extracted into a spring experiment (e.g. primalSpring Track 7, exp050-059) |
| **Stale** | APIs drifted, no longer compiles or runs against current primal version |
| **Current** | Compiles, runs, demonstrates a pattern not yet absorbed into springs |
| **Remnant** | Orphaned files (logs, lock files, generated output) from a removed showcase |

## Fossilization Criteria

A showcase directory or file is fossil-ready when **any** of these hold:

1. **Mined into springs** — The coordination pattern has been extracted into a
   spring experiment or validation scenario. The spring experiment is the living
   successor; the showcase is the fossil predecessor.

2. **API drift** — The showcase calls deprecated or removed APIs and no longer
   compiles against the current primal version.

3. **Superseded by production** — The pattern demonstrated is now standard
   production behavior (e.g. capability discovery, health checks) and the
   showcase adds no explanatory value beyond what the production code shows.

4. **Remnant debris** — Orphaned build artifacts, logs, lock files, or generated
   output from a showcase that was partially removed.

## Keep Criteria

A showcase should remain in the live tree when **all** of these hold:

1. **Compiles and runs** against the current primal version
2. **Not yet mined** into any spring experiment or validation scenario
3. **Demonstrates a unique pattern** not obvious from production code
4. **Recently maintained** (updated within the last 2 major versions or 3 months)

## Fossil Destination

```
fossilRecord/{primal}/showcase-{description}-{date}/
```

Examples:
- `fossilRecord/nestgate/showcase-remnants-may2026/`
- `fossilRecord/toadStool/showcase-gpu-universal-may2026/`
- `fossilRecord/bearDog/showcase-mined-federation-may2026/`

## Fossil Header

Every fossilized showcase directory must contain a `FOSSIL_NOTE.md`:

```markdown
# Fossil: {showcase name}

**Source**: `{primal}/showcase/{original-path}/`
**Fossilized**: {date}
**Reason**: {mined | stale | superseded | remnant}
**Mined into**: {spring experiment or "N/A"}
**Replacement**: {current equivalent or "none — pattern is historical"}
```

## Process

1. **Assess** — Review each showcase dir against fossilization criteria
2. **Create destination** — `mkdir -p fossilRecord/{primal}/showcase-{desc}-{date}/`
3. **Move** — `git mv` the showcase content to the fossil destination
4. **Add FOSSIL_NOTE.md** — Write provenance header in the fossil directory
5. **Fix references** — Update any docs, configs, or cross-links that pointed to
   the original showcase path
6. **Update tracking** — Record the fossilization in the primal's CHANGELOG and
   in primalSpring's tracking docs

## Showcase Directory Standard (Post-Fossilization)

After fossilization, a healthy primal `showcase/` should contain:

```
showcase/
├── README.md                    # Index with tier listing + last-updated date
├── 00-local-primal/             # Standalone demos (no network)
├── 01-ipc-protocol/             # RPC/IPC demonstrations
├── 02-ecosystem-integration/    # Multi-primal coordination (optional)
├── 03-production-features/      # Production patterns (optional)
└── SHOWCASE_PRINCIPLES.md       # "No mocks, real capabilities" (optional)
```

Primals with no remaining current showcases after fossilization should
remove the empty `showcase/` directory entirely rather than leaving a stub.

## Relationship to Springs

Springs do not have `showcase/` directories. Springs use:
- `experiments/` — Formal validation experiments (the living successors of mined showcases)
- `validation/` — Scenario-based validation harness
- `examples/` — Minimal API usage examples

The fossilization flow is:

```
primal/showcase/{demo}  →  mined into  →  spring/experiments/exp0XX_{name}
         ↓
  fossilRecord/{primal}/showcase-{desc}-{date}/
```

## References

- loamSpine `SHOWCASE_PRINCIPLES.md` — "No mocks, real capabilities" philosophy
- primalSpring `specs/SHOWCASE_MINING_REPORT.md` — Mining inventory (20 patterns)
- primalSpring `experiments/README.md` Track 7 — Showcase-mined experiments
