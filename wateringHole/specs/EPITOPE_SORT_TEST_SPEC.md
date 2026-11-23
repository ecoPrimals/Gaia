# Epitope Sort Test Specification
## The Test IS the Answer. pi != pi yet.
## Wave 175 | Oct 11, 2026

---

## THE PRINCIPLE

The test doesn't verify the answer. **The test IS the answer.**

`the_examination_is_the_proof` (#169) — Wheatley's examiners
intended to disprove her. The examination proved her. The test
IS the proof. Not test → answer. test = answer.

Pi is computed by successive approximation. Each iteration:
closer. Never exact. pi != pi yet. But each pass can measure
HOW FAR from convergence we are. When the delta between passes
drops below threshold: pi ≈ pi. Good enough. Ship it.

**Our system is the same.** 42 → 100 → 136 → 192 epitopes.
Each pass closer. But to what? To the TRUE classification of
each entity: self / non-self / null. That's our pi. We're
still approximating. pi != pi yet. The testing system measures
the convergence.

---

## THE TEST STRUCTURE

### Level 0: The Binding Test (atomic)

The smallest test. One epitope applied to one entity.

```
INPUT:  epitope #N, entity #M
OUTPUT: binds (true/false) + strength (0.0 - 1.0)
```

Total tests at current count: 192 epitopes × 114 entities = **21,888 binding tests**.

Each binding test is binary at its core (binds/doesn't), but
strength is a float (how strongly it binds). Strong binding =
high confidence. Weak binding = edge case. No binding = null
for that epitope-entity pair.

### Level 1: The Classification Test (entity)

All epitopes applied to one entity. The binding PATTERN classifies.

```
INPUT:  entity #M
PROCESS: apply all 192 epitopes, record binding pattern
OUTPUT: classification (self / non-self / null)
        + confidence score (0.0 - 1.0)
        + binding vector [b1, b2, ..., b192]
```

The binding vector IS the entity's fingerprint. Two entities
with similar binding vectors are structurally similar. That's
`graph_isomorphism` (#2) measured, not eyeballed.

**The classification threshold:**
```
capture_epitopes = [#1-#10, #4, #5, #6, #7, #9, #10]
If sum(capture_epitope_bindings) > threshold: NON-SELF
If sum(all_bindings) < minimum: NULL
Else: SELF
```

### Level 2: The Convergence Test (system)

Does adding one more epitope change any classification?

```
INPUT:  entity classifications at N epitopes
        entity classifications at N+1 epitopes
OUTPUT: delta (number of classifications that changed)
        convergence_rate = 1 - (delta / total_entities)
```

**pi ≈ pi when convergence_rate > 0.99.**

If adding epitope #193 changes zero classifications: converged.
If it changes 5: still converging. Each flip is a measurement
of remaining uncertainty.

Track convergence over time:
```
Pass  Epitopes  Changed  Rate
  1       42       —       —
  2      100      ?/?     ?.??
  3      136      ?/?     ?.??
  4      192      ?/?     ?.??
  5      193      ?/114   ?.??   ← are we converged?
```

### Level 3: The Order Independence Test (bug check)

`order_dependence_is_a_bug` (#188). If applying epitopes in
different order gives different classifications, the sort is
BROKEN.

```
INPUT:  entity #M
PROCESS:
  Run 1: apply epitopes in order [1, 2, 3, ..., 192]
  Run 2: apply epitopes in order [192, 191, ..., 1]
  Run 3: apply epitopes in random order (seed=42)
  Run 4: apply epitopes in random order (seed=99)
OUTPUT: 
  all_same = (classification_1 == classification_2 == ... == classification_4)
  IF !all_same: ORDER DEPENDENCE BUG → investigate
```

In WFC, order matters (feature). In structural analysis, order
must NOT matter (correctness). This test catches the bug.

### Level 4: The Vantage Test (robustness)

`vantage_determines_binding` (#148) says classification can
vary by vantage. But `invariance_is_the_proof` (#149) says
non-self from EVERY vantage = structural.

```
INPUT:  entity #M
PROCESS:
  Vantage A: apply from civic perspective (formation, governance edges)
  Vantage B: apply from financial perspective (payment, money_flow edges)
  Vantage C: apply from legal perspective (bench, jurisdiction edges)
  Vantage D: apply from social perspective (family, co-resident edges)
OUTPUT:
  consensus = agree across all vantages?
  IF self from A but non-self from B: EDGE CASE → needs more data
  IF non-self from ALL: STRUCTURAL INVARIANT → proven
```

### Level 5: The Negative Test (falsification)

`the_table_has_blind_spots` (#183). Test what the table MISSES.

```
INPUT:  entity known to be non-self (confirmed by external evidence)
PROCESS: apply all 192 epitopes
EXPECTED: classification = non-self
IF classification = self or null: FALSE NEGATIVE
  → the table has a blind spot
  → which epitopes SHOULD have bound but didn't?
  → new epitope needed

INPUT:  entity known to be self (functioning institution)
PROCESS: apply all 192 epitopes
EXPECTED: classification = self
IF classification = non-self: FALSE POSITIVE
  → the table is overfitting
  → which epitopes bound incorrectly?
  → epitope definition too broad
```

---

## THE TEST FILE STRUCTURE

```
wateringHole/
  tests/
    epitope-sort/
      binding/
        test_epitope_001_regulatory_arbitrage.md
        test_epitope_002_revolving_door.md
        ...
        test_epitope_192_other_is_recruiting_pool.md
      classification/
        test_entity_pca.md
        test_entity_purpose_group.md
        test_entity_dpscd.md
        ...
      convergence/
        convergence_log.md    ← track delta per pass
      order/
        order_independence.md ← run order tests
      vantage/
        vantage_consensus.md  ← multi-vantage results
      negative/
        false_negatives.md    ← blind spots found
        false_positives.md    ← overfitting found
```

---

## THE CONVERGENCE METRIC

pi = true classification vector for all 114 entities.
pi_hat = our current approximation (192 epitopes).
pi != pi yet.

```
||pi - pi_hat|| = number of entities whose classification
                  would change if we had MORE epitopes

We don't know pi. That's the point.
But we can ESTIMATE the error:

  error ≈ (classifications changed by last N epitopes) / N

If the last 10 epitopes changed 0 classifications: error ≈ 0.
If the last 10 changed 5: error ≈ 0.5 per epitope.

The convergence criterion:
  IF error < 0.01 for 10 consecutive epitopes:
    pi ≈ pi. Converged. Ship it.
```

---

## IMPLEMENTATION — WHAT WE CAN DO NOW

### Phase 1: Manual sort (can do from northGate)

Pick 10 entities. Apply the 192 epitopes manually (in a document).
Record bindings. Classify. This is slow but proves the method.

**Top 10 target entities for first sort:**
1. `purpose_group` — formation cascade root (expect: non-self)
2. `pca` — Purpose Charter Academy (expect: non-self)
3. `dpscd` — school district (expect: sort needed — self or captured?)
4. `dykema` — law firm (expect: null — routing)
5. `dykema_federal_pac` — PAC (expect: null — routing)
6. `cmu` — Carnegie Mellon (expect: self)
7. `macdowell` — charter school (expect: non-self)
8. `great_lakes_legal` — legal services (expect: sort needed)
9. `put_progress_first` — ballot committee (expect: null — routing)
10. `banks_strategy` — consulting LLC (expect: non-self)

### Phase 2: Structured test docs

For each entity, create a test doc with:
- Entity name and type
- All edges (from graph.json)
- Epitope binding results (which of 192 bind, with strength)
- Classification output
- Confidence score
- Notes on edge cases

### Phase 3: Convergence tracking

After Phase 2, add epitopes #193+ and track whether any
of the 10 classifications change. If none change after 10
new epitopes: pi ≈ pi for those 10.

### Phase 4: Automation

Build a tool that reads graph.json + epitope table and
runs the binding tests programmatically. Output: classified
graph.json with self/non-self/null per node. Feed back
into the visualization (color-code by classification).

---

## THE META-TEST

The test specification itself is testable:

- Does the binding test produce consistent results?
  → Order independence test
- Does the classification converge?
  → Convergence test
- Does the test catch known non-self?
  → Negative test (false negative rate)
- Does the test spare known self?
  → Negative test (false positive rate)
- Does the test work from every vantage?
  → Vantage test

**The test tests the test.** This is `the_sort_moves_the_sorter`
(#150) applied to quality assurance. The test structure sorts
itself. pi != pi yet — but the test structure can tell us
when pi ≈ pi.

---

*The test IS the answer.*
*pi != pi yet.*
*But we can measure the gap.*
*And the gap shrinks with every pass.*

---
