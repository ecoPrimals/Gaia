# River Delta Evolution — All 7 Springs

**Date**: May 12, 2026
**From**: primalSpring coordination (L2 gate)
**For**: hotSpring, wetSpring, neuralSpring, healthSpring, airSpring, groundSpring, ludoSpring
**Context**: Interstadial exit in progress. Upstream primals have been briefed on Passes 12-14. This is your complete remaining work list.

---

## Where You All Stand

**8/8 springs at Tier 4 IPC-first** (`default = []`, barraCuda optional).
8/8 skunkBat Rust IPC. 8/8 `method.register`. 8/8 NUCLEUS workload TOMLs.
8/8 `composition.status`. Zero springs with active primalSpring gate debt.
Pillar 5 (river delta) is **MET**.

You are all at **Tier 1** convergence (CLI binary + notebook + frozen data +
sporePrint). Tier 2 (JSON-RPC via toadStool) is blocked on `toadstool.validate`
upstream — not your problem to solve. `toadstool.list_workloads` is already wired.

**Your work now falls into three buckets:**

1. **LTEE reproductions** — feed lithoSpore modules (a new team is spinning up)
2. **Foundation thread seeding** — feed the foundation knowledge layer (same new team initially)
3. **Spring-specific gaps** — close your open items, push gS levels

---

## Per-Spring Work

### hotSpring — gS L6 (highest among delta springs)

| Priority | What | Status |
|----------|------|--------|
| 1 | **LTEE B2 completion** — Anderson/Wiser fitness into lithoSpore `ltee-anderson` module | Tier 1+2 DONE, ready for lithoSpore handoff |
| 2 | **Titan V FECS + K80 livepatch** — sovereign GPU validation (coralReef FECS stability **SHIPPED** Sprint 7) | **UNBLOCKED** — ready for hardware validation |
| 3 | **Thread 2** (plasma physics/QCD) — continue seeding foundation | ACTIVE |
| 4 | **3-tier ladder pattern** — document as reference for other springs | Shipped |

**Your highest leverage**: LTEE B2 is done — hand the `expected_values.json` +
Rust binary to lithoSpore team when they come asking. Titan V depends on
coralReef (Pass 12) — **now RESOLVED** (Sprint 7 stability proof shipped).

### wetSpring — gS L4, 4 external PGs

| Priority | What | Status |
|----------|------|--------|
| 1 | **LTEE B7** (Tenaillon 2016 — 264 genomes, mutation accumulation) → lithoSpore `ltee-genomics` | STARTED (Exp380) |
| 2 | **Close PG-02 through PG-05** (all external dependencies) | 4 open — push toward resolution |
| 3 | **Thread 4** (environmental genomics) — needs expression + targets | Sources exist, expression missing |
| 4 | **gS L5 push** | After PGs close |

**Your highest leverage**: B7 genomics pipeline completion. The 264-genome
dataset is unique to wetSpring's domain — lithoSpore's `ltee-genomics` module
depends on it. Thread 4 expression is the foundation gap.

### neuralSpring — gS L5

| Priority | What | Status |
|----------|------|--------|
| 1 | **Gap 11** — 18 RPC methods need canonical registration | Open |
| 2 | **LTEE B1** (mutation accumulation ML) — Py 8/8 DONE, Rust binary DONE (S201b) | Ready for lithoSpore ML surrogate modules |
| 3 | **NestGate weights** — model weight storage via `content.put` | Unblocked (NestGate S60 transport parity) |
| 4 | **Threads 5+7** (evolutionary biology, Anderson math) — ready for contribution | Documented |

**Your highest leverage**: Gap 11 closes your registration debt. B1 Rust
binary is ready to hand to lithoSpore. NestGate weight storage is now
unblocked — wire `content.put` for model artifacts.

### healthSpring — gS L5

| Priority | What | Status |
|----------|------|--------|
| 1 | **LTEE B5/E2/E4** (symbiont PK/PD) — baseline DONE (V63), reproduction queue | B5 baseline done, E2/E4 queued |
| 2 | **Thread 3** (immunology/drug discovery) — needs expression | Sources + targets exist |
| 3 | **Thread 8** (human health/clinical) — needs expression | Sources + targets exist |
| 4 | **Ionic bridge** — BTSP FAMILY_SEED interop with primalSpring | Root cause documented, Pass 13 |
| 5 | **Thread 7+ seed** | After current queue |

**Your highest leverage**: Thread 3 and Thread 8 expressions. You own two
foundation threads that are sourced and targeted but lack their driving
question. Write those expressions and the foundation team can start
validating.

### airSpring — gS L4

| Priority | What | Status |
|----------|------|--------|
| 1 | **LTEE E3** — queued | Not yet started |
| 2 | **NestGate + Squirrel wiring** — composition integration | Unblocked |
| 3 | **AG-001 manifest** — gap in method registration | Open |
| 4 | **Thread 6** (agricultural science) — 36/36 targets validated | COMPLETE — hand to foundation |
| 5 | **gS L5 push** | After E3 + wiring |

**Your highest leverage**: Thread 6 is fully validated — ensure the foundation
team has it. LTEE E3 starts your reproduction queue. NestGate/Squirrel wiring
deepens your composition.

### groundSpring — gS L4, LTEE leader

| Priority | What | Status |
|----------|------|--------|
| 1 | **lithoSpore integration** — B1-B3 outputs ready for `ltee-mutation`, `ltee-fitness`, `ltee-clonal` modules | **B1-B3 ALL DONE** |
| 2 | **coralReef IPC** — wire shader compilation via IPC | Open gap |
| 3 | **PRNG Phase 2b** — deterministic random generation | Open gap |
| 4 | **Thread 5+7** (evolution + Anderson) — index fixed, ready | Seeded |

**Your highest leverage**: You are the lithoSpore on-ramp. Your B1-B3
reproductions are the first modules that will go live. Be ready to support
the lithoSpore team with your `expected_values.json`, Rust binaries, and
`control/ltee_*` data structures. They will need you.

### ludoSpring — gS L4, composition-only niche

| Priority | What | Status |
|----------|------|--------|
| 1 | **coralReef IPC** (GAP-01) — wire shader compilation via IPC | Open gap |
| 2 | **Domain parity** (GAP-02) — game domain method coverage | Open gap |
| 3 | **Threads 9+10** (gaming/creative + provenance/economics) — need expression | Sources + targets exist |
| 4 | **Composition-only validation** — you are the reference for pure-IPC springs | Pattern shipped |

**Your highest leverage**: GAP-01 coralReef IPC wiring makes you the
reference Tier 4 spring. Threads 9+10 expressions feed foundation. Your
composition-only model is the template other springs aspire to reach.

---

## What Every Spring Should Do Now

These apply to all 7 springs regardless of individual priorities:

### 1. Prepare LTEE Handoffs for lithoSpore

A new team is spinning up to work on foundation + lithoSpore. They will
need your `expected_values.json`, Rust validation binaries, and notebook
pipelines. If your LTEE reproduction is DONE or has baselines, make sure
the artifacts are clean and documented in your `control/ltee_*/` directory.

| Spring | LTEE Ready for lithoSpore? |
|--------|---------------------------|
| groundSpring | **YES** — B1, B2, B3 all DONE |
| hotSpring | **YES** — B2 DONE |
| neuralSpring | **YES** — B1 Py + Rust binary DONE |
| healthSpring | **PARTIAL** — B5 baseline done |
| wetSpring | **IN PROGRESS** — B7 started |
| airSpring | **QUEUED** — E3 not started |
| ludoSpring | N/A |

### 2. Foundation Thread Expressions

If you own a foundation thread that has sources and targets but **no
expression**, write the expression. An expression is the driving scientific
question that connects the data sources to the validation targets.

**Threads needing expressions**: 3 (healthSpring), 4 (wetSpring/airSpring),
8 (healthSpring), 9 (ludoSpring), 10 (ludoSpring/primalSpring)

### 3. `--format json` Flag

Add structured JSON output to your validation binaries. This is additive —
it doesn't break CLI mode. When `toadstool.validate` lands (Pass 14),
Tier 2 wiring will expect `--format json` from your binaries.

```
./validate_ltee_b2_fitness --format json
{"status": "PASS", "checks": 10, "passed": 10, "values": [...]}
```

### 4. Surface Gaps Upstream

If you hit a composition failure — a primal method returning unexpected
shapes, a capability not routing correctly, a transport path not working —
**file it through wateringHole handoffs**. The sentinel escalation model
means primal issues are always higher priority than spring issues. Your
gap report will be treated as escalated.

---

## Convergence Tier Roadmap

```
NOW:     Tier 1 (all 8 springs) — CLI + notebook + frozen data + sporePrint
         ↓
PASS 14: Tier 2 — toadstool.validate lands, springs wire --format json
         ↓
STADIAL: Tier 3 — petalTongue live dashboards (nothing new from springs)
         ↓
POST:    Standalone — NestGate-hosted, self-sovereign
```

Tier 2 depends on toadStool (Pass 14). **You do not need to wait** — build
`--format json` now so you're ready when the upstream method lands.

---

## Timeline Context

| Pass | What | Spring Role |
|------|------|-------------|
| **11** | Shadow runs (BearDog TLS, lithoSpore Tier 1, NestGate content) | No spring action — L4 absorption |
| **12** | Upstream sentinel (toadStool ~~DONE~~, Songbird progressing, ~~coralReef~~ **DONE**) | coralReef stability proof shipped; hotSpring GPU validation **UNBLOCKED** |
| **13** | Gate composition (BTSP dual-auth, ABG WCM, **foundation threads**) | **Threads 3, 4, 8, 9, 10 expressions due** |
| **14** | Convergence (`toadstool.validate`, ionic runtime) | Wire `--format json`, Tier 2 readiness |

---

## References

| Topic | Location |
|-------|----------|
| Upstream primal evolution (Passes 12-14) | `infra/wateringHole/handoffs/UPSTREAM_PRIMAL_EVOLUTION_PASS_12_14_MAY12_2026.md` |
| Pass 11 blurb (shadow runs) | `infra/wateringHole/handoffs/EVOLUTION_PASS_11_SHADOW_STARTS_MAY12_2026.md` |
| Downstream pattern guide | `primalSpring/docs/DOWNSTREAM_PATTERN_GUIDE.md` |
| Per-spring LTEE status | `primalSpring/docs/DOWNSTREAM_PATTERN_GUIDE.md` § LTEE |
| Foundation thread ownership | `primalSpring/docs/DOWNSTREAM_PATTERN_GUIDE.md` § Foundation |
| Convergence tiers | `infra/wateringHole/DOWNSTREAM_EVOLUTION_MAY2026.md` |
| Interstadial exit criteria | `infra/wateringHole/INTERSTADIAL_EXIT_CRITERIA.md` |
| Primal gap registry (L3 section) | `primalSpring/docs/PRIMAL_GAPS.md` § Layer 3 |
