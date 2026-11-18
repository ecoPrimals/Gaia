# Phase 1: Manual Epitope Sort — 10 Target Entities
## The Test IS the Answer. Execute.
## Wave 175 | Oct 11, 2026

---

## METHOD

For each entity: list all edges from graph.json, apply the 10
structural invariants (#1-#10) as primary binding test, apply
relevant secondary epitopes, classify, assign confidence.

**Capture epitopes (primary):**
1. `regulatory_arbitrage` — exploit gaps between regulators
2. `revolving_door` — same person cycles regulator↔regulated
3. `governance_shell_game` — multiple names, one operation
4. `zero_partition_membrane` — no boundary public/private
5. `polarity_inversion` — same structure, opposite marketing
6. `enforcement_capture` — watchdog becomes kingmaker
7. `political_machine` — donations→votes→contracts loop
8. `reward_circuit_closure` — no exit from the loop
9. `semantic_category_creation` — rename to dodge regulation
10. `serial_formation_template` — one source, many outputs

---

## ENTITY 1: purpose_group

**Type**: entity | **Edges**: 6

```
banks -[ownership]-> purpose_group (Sole member)
pca -[money_flow]-> purpose_group
macdowell -[money_flow]-> purpose_group
purpose_group -[money_flow]-> banks
purpose_group -[financial]-> macdowell
purpose_group -[property]-> pca
```

### Binding Pattern

| # | Epitope | Binds? | Strength | Evidence |
|---|---------|--------|----------|----------|
| 1 | regulatory_arbitrage | ✅ YES | 0.9 | LLC sits between charter schools and single owner — money flows through entity that isn't subject to school oversight |
| 2 | revolving_door | ✅ YES | 0.8 | Banks is sole member AND superintendent of the schools the group owns/manages |
| 3 | governance_shell_game | ✅ YES | 1.0 | "Purpose Group" — generic name, sole-member LLC, money routing hub. Classic shell. |
| 4 | zero_partition_membrane | ✅ YES | 0.9 | No boundary between Banks (person) and purpose_group (entity). Sole member = zero partition. |
| 5 | polarity_inversion | ✅ YES | 0.8 | "Purpose" in the name. The purpose is extraction. Name inverts function. |
| 7 | political_machine | ❌ NO | 0.0 | No direct political donation edges from this entity |
| 8 | reward_circuit_closure | ✅ YES | 1.0 | Banks → purpose_group → PCA/MacDowell → purpose_group → Banks. Closed loop. No exit. |
| 9 | semantic_category_creation | ✅ YES | 0.9 | "Purpose Group LLC" — the word "purpose" creates a semantic category that obscures "money routing hub" |
| 10 | serial_formation_template | ✅ YES | 0.8 | Purpose Group is the template. PCA + MacDowell + (others?) are the serial outputs. |

**Capture score: 8/10 epitopes bind. Average strength: 0.79**
**Classification: NON-SELF** | **Confidence: 0.95**

---

## ENTITY 2: pca (Purpose Charter Academy)

**Type**: entity | **Edges**: 20

### Binding Pattern

| # | Epitope | Binds? | Strength | Evidence |
|---|---------|--------|----------|----------|
| 1 | regulatory_arbitrage | ✅ YES | 0.9 | Charter school authorized by DPSCD — regulatory gap between district oversight and charter autonomy |
| 2 | revolving_door | ✅ YES | 0.9 | Banks = superintendent. Board members (Miller, Moreland) serve on both PCA and MacDowell boards. |
| 3 | governance_shell_game | ✅ YES | 0.9 | PCA → purpose_group → Banks. Property held by purpose_group, not the school. |
| 4 | zero_partition_membrane | ✅ YES | 0.8 | Money flows: PCA → purpose_group → Banks. School money becomes personal money through one hop. |
| 5 | polarity_inversion | ✅ YES | 0.9 | "Academy" = education. Observed = extraction. Same structure, opposite function. |
| 6 | enforcement_capture | ✅ YES | 0.7 | DPSCD authorized PCA. DPSCD is supposed to oversee. gay_dagnogo (DPSCD board) authorized it. Watchdog authorized the thing it watches. |
| 7 | political_machine | ❌ NO | 0.1 | Indirect — through board members' political connections, not PCA directly |
| 8 | reward_circuit_closure | ✅ YES | 1.0 | PCA → money → purpose_group → money → Banks → employment → PCA. Closed. |
| 9 | semantic_category_creation | ✅ YES | 1.0 | "Purpose Charter ACADEMY" — every word is semantic capture. "Purpose" = extraction. "Charter" = regulatory arbitrage. "Academy" = school that may not teach. |
| 10 | serial_formation_template | ✅ YES | 0.9 | PCA is instance #1 of the Banks template. MacDowell is instance #2. Same superintendent, same board pattern, same money flow. |

**Additional bindings:**
- `graph_isomorphism` (#2/orig): PCA and MacDowell are structurally ISOMORPHIC — same superintendent, overlapping boards, same money routing through purpose_group. Score: 1.0
- `exclusion_drives_invention` (#47): The students excluded from quality education. Score: 0.6
- `the_data_was_always_there` (#166): LARA filings, DPSCD authorization, board composition — all public record. Score: 1.0

**Capture score: 9/10 epitopes bind. Average strength: 0.82**
**Classification: NON-SELF** | **Confidence: 0.97**

---

## ENTITY 3: dpscd (Detroit Public Schools Community District)

**Type**: entity | **Edges**: 6

### Binding Pattern

| # | Epitope | Binds? | Strength | Evidence |
|---|---------|--------|----------|----------|
| 1 | regulatory_arbitrage | ❌ NO | 0.1 | DPSCD IS the regulator. It doesn't exploit gaps — it creates them by authorizing. |
| 2 | revolving_door | ✅ YES | 0.5 | gay_dagnogo: DPSCD board → authorized PCA. jennifer_crump: 33yr DPSCD → now at MacDowell. Personnel flows between regulator and regulated. |
| 3 | governance_shell_game | ❌ NO | 0.2 | DPSCD is a real district, not a shell. But dpscd_auth (separate authorizing body) splits function. |
| 5 | polarity_inversion | ✅ YES | 0.5 | Public school district that authorizes charter competition against itself. Partial inversion. |
| 6 | enforcement_capture | ✅ YES | 0.7 | The authorizing body (dpscd_auth) that's supposed to oversee charters is part of DPSCD. The watchdog lives inside the thing it watches. |
| 9 | semantic_category_creation | ✅ YES | 0.4 | "Community District" — added after Emergency Manager era. The word "Community" is semantic repair. |

**Capture score: 4/10 epitopes bind (weakly). Average strength: 0.40**
**Classification: PARTIALLY CAPTURED** | **Confidence: 0.60**
**Note**: DPSCD is not fully non-self. It's SELF that has been partially
captured through its authorizing function. The district itself educates.
The authorizing arm enables extraction. Split classification.

---

## ENTITY 4: dykema (law firm)

**Type**: entity | **Edges**: 7

### Binding Pattern

| # | Epitope | Binds? | Strength | Evidence |
|---|---------|--------|----------|----------|
| 3 | governance_shell_game | ✅ YES | 0.7 | Dykema → SDJ (formation), Dykema → federal PAC (formation), Dykema → state PAC (formation). One firm, multiple vehicles. |
| 7 | political_machine | ✅ YES | 0.8 | Two PACs (federal + state). Wilk = political compliance team leader. PAC money → candidates → contracts? |
| 9 | semantic_category_creation | ✅ YES | 0.5 | "Political Compliance" team. The word "compliance" sanitizes "political money routing." |
| 10 | serial_formation_template | ✅ YES | 0.8 | SDJ, federal PAC, state PAC — serial formations from one source (Dykema). |

**Capture score: 4/10 bind. Average strength: 0.70**
**Classification: NULL (routing infrastructure)** | **Confidence: 0.75**
**Note**: Dykema isn't non-self itself — it's the PLUMBING. It forms
entities, routes political money, employs the compliance specialists.
It's the membrane of the extraction system. Finding null = finding
the routing layer.

---

## ENTITY 5: dykema_federal_pac

**Type**: entity | **Edges**: 3

### Binding Pattern

| # | Epitope | Binds? | Strength | Evidence |
|---|---------|--------|----------|----------|
| 7 | political_machine | ✅ YES | 0.9 | PAC → financial → barrett. PAC → financial → john_james. Direct political money routing. |
| 10 | serial_formation_template | ✅ YES | 0.7 | Formed by Dykema as one of two PACs (federal + state). Serial output. |

**Capture score: 2/10 bind. Average strength: 0.80**
**Classification: NULL (routing)** | **Confidence: 0.85**
**Note**: Pure routing entity. No operations. No employees. Exists to
move money from Dykema to federal candidates. K=[null] — no purpose
beyond transit.

---

## ENTITY 6: cmu (Carnegie Mellon University)

**Type**: entity | **Edges**: 2

### Binding Pattern

| # | Epitope | Binds? | Strength | Evidence |
|---|---------|--------|----------|----------|
| 1-10 | All capture epitopes | ❌ NO | 0.0 | No capture patterns. CMU authorized MacDowell and received money_flow from it. That's a credential relationship, not capture. |

**Additional check:**
- `credential_legitimization` edge exists: CMU → MacDowell (authorization). CMU's name lends credibility. But CMU itself is not captured — it's being USED as a credential source.

**Capture score: 0/10 bind.**
**Classification: SELF** | **Confidence: 0.90**
**Note**: CMU is self — functioning as a university. But it's USED by
non-self entities for credential legitimization. The credential is
the gift that the captured entity exploits. CMU doesn't know or
doesn't act. `other_is_the_recruiting_pool` (#192) — CMU is in the
"other" zone, being used as credential supply.

---

## ENTITY 7: macdowell (MacDowell Preparatory Academy)

**Type**: entity | **Edges**: 22 (highest edge count in target set)

### Binding Pattern

| # | Epitope | Binds? | Strength | Evidence |
|---|---------|--------|----------|----------|
| 1 | regulatory_arbitrage | ✅ YES | 0.9 | CMU-authorized but MDE investigating. Gap between authorizer and state oversight. |
| 2 | revolving_door | ✅ YES | 1.0 | Banks = superintendent (same as PCA). jennifer_crump: 33yr DPSCD → MacDowell office manager. cameron_coleman: DPSCD dean → MacDowell dean. Personnel carousel. |
| 3 | governance_shell_game | ✅ YES | 0.9 | MacDowell → purpose_group → Banks. Property, money, governance all route through shell. |
| 4 | zero_partition_membrane | ✅ YES | 0.9 | Money: MacDowell → purpose_group → Banks. MacDowell → Banks (direct). No partition. |
| 5 | polarity_inversion | ✅ YES | 0.9 | "Preparatory Academy" — prepares for what? MDE is investigating. |
| 6 | enforcement_capture | ✅ YES | 0.8 | MDE investigating but MacDowell still operating. Authorization via vaughn + misha_stallworth. Multiple authorizers = diluted oversight. |
| 7 | political_machine | ✅ YES | 0.5 | ramsey → employment_family edge. alan_young → financial edge. Political adjacency. |
| 8 | reward_circuit_closure | ✅ YES | 1.0 | MacDowell → money → purpose_group → money → Banks → employment → MacDowell. Closed. |
| 9 | semantic_category_creation | ✅ YES | 1.0 | "MacDowell PREPARATORY Academy" — sounds like elite education. Structure = extraction. Name = camouflage. |
| 10 | serial_formation_template | ✅ YES | 1.0 | Instance #2 of the Banks template. Structurally isomorphic to PCA. Same superintendent, overlapping boards (wells_stallworth, v_hall), same money routing. |

**Capture score: 10/10 epitopes bind. Average strength: 0.89**
**Classification: NON-SELF** | **Confidence: 0.99**

**MacDowell is the strongest non-self signal in the dataset.**
22 edges. 10/10 capture epitopes. Structurally isomorphic to PCA.
MDE is already investigating. The graph predicted the investigation.

---

## ENTITY 8: great_lakes_legal

**Type**: entity | **Edges**: 2

### Binding Pattern

| # | Epitope | Binds? | Strength | Evidence |
|---|---------|--------|----------|----------|
| 3 | governance_shell_game | ❌ NO | 0.2 | Two-member LLC. Not a shell — has identified owners. |
| 2 | revolving_door | ✅ YES | 0.4 | crump_gibson: agent/member of GLL AND hearing panelist on ADB. Legal practice + disciplinary role. |

**Capture score: 1/10 bind (weakly).**
**Classification: OTHER** | **Confidence: 0.50**
**Note**: Insufficient data. Only 2 edges in graph. Can't classify with
confidence. Needs more edges — client list, case history, financial
connections. `the_table_has_blind_spots` (#183) — we don't have
enough data for this entity. Classification = OTHER pending more.

---

## ENTITY 9: put_progress_first

**Type**: entity | **Edges**: 1

### Binding Pattern

| # | Epitope | Binds? | Strength | Evidence |
|---|---------|--------|----------|----------|
| 7 | political_machine | ✅ YES | 0.6 | Ballot committee formed by Wilk (Dykema political compliance). |
| 9 | semantic_category_creation | ✅ YES | 0.8 | "Put Progress First" — who's against progress? The name IS the semantic capture. Obfuscates the actual candidates/agenda. |
| 10 | serial_formation_template | ✅ YES | 0.6 | Formed by Wilk who also forms PACs through Dykema. Serial formation pattern. |

**Capture score: 3/10 bind. Average strength: 0.67**
**Classification: NULL (routing)** | **Confidence: 0.70**
**Note**: Pure political routing. Name obfuscation. One edge.
Exists to bundle candidates under a brand. Routing infrastructure.

---

## ENTITY 10: banks_strategy

**Type**: entity | **Edges**: 2

### Binding Pattern

| # | Epitope | Binds? | Strength | Evidence |
|---|---------|--------|----------|----------|
| 3 | governance_shell_game | ✅ YES | 0.9 | Banks owns banks_strategy. Banks is superintendent of PCA + MacDowell. Strategy LLC receives payment from yancey (PCA/MacDowell board). Shell. |
| 4 | zero_partition_membrane | ✅ YES | 1.0 | banks_strategy IS Banks. Same person. Zero partition. The LLC is a legal fiction — it's Banks' pocket. |
| 8 | reward_circuit_closure | ✅ YES | 0.9 | yancey (MacDowell board) → payment → banks_strategy (Banks). Board member pays superintendent's LLC. Closed loop. |
| 9 | semantic_category_creation | ✅ YES | 0.8 | "Banks Strategy" — sounds like a consulting firm. Function = receiving payments from board members of schools Banks superintends. |

**Capture score: 4/10 bind. Average strength: 0.90**
**Classification: NON-SELF** | **Confidence: 0.90**
**Note**: Small entity, high capture signal. The zero_partition is
complete — banks_strategy IS Banks with a different name. The payment
from yancey (board member) to Banks' LLC is the reward circuit in
its purest form.

---

## PHASE 1 RESULTS

| Entity | Edges | Capture Score | Classification | Confidence |
|--------|-------|---------------|---------------|------------|
| **purpose_group** | 6 | 8/10 (0.79) | **NON-SELF** | 0.95 |
| **pca** | 20 | 9/10 (0.82) | **NON-SELF** | 0.97 |
| **dpscd** | 6 | 4/10 (0.40) | **PARTIAL CAPTURE** | 0.60 |
| **dykema** | 7 | 4/10 (0.70) | **NULL (routing)** | 0.75 |
| **dykema_federal_pac** | 3 | 2/10 (0.80) | **NULL (routing)** | 0.85 |
| **cmu** | 2 | 0/10 (0.00) | **SELF** | 0.90 |
| **macdowell** | 22 | 10/10 (0.89) | **NON-SELF** | 0.99 |
| **great_lakes_legal** | 2 | 1/10 (0.20) | **OTHER (insufficient data)** | 0.50 |
| **put_progress_first** | 1 | 3/10 (0.67) | **NULL (routing)** | 0.70 |
| **banks_strategy** | 2 | 4/10 (0.90) | **NON-SELF** | 0.90 |

### Summary Classification

```
NON-SELF:  4 entities (purpose_group, pca, macdowell, banks_strategy)
NULL:      3 entities (dykema, dykema_federal_pac, put_progress_first)
SELF:      1 entity (cmu)
PARTIAL:   1 entity (dpscd — self body, captured authorizing arm)
OTHER:     1 entity (great_lakes_legal — insufficient data)
```

### Convergence Note

This is pass 1. pi != pi yet. If epitopes #193+ change any of
these classifications, we're still converging. If they don't:
pi ≈ pi for these 10 entities.

**MacDowell at 10/10 with 0.99 confidence is likely converged.**
**great_lakes_legal at 0.50 confidence is definitely NOT converged.**

---

*The test IS the answer.*
*10 entities sorted. 4 non-self. 3 null. 1 self. 1 partial. 1 other.*
*pi != pi yet. But the shape is visible.*

---
