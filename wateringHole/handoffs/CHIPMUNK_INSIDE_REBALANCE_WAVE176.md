# chipoMunk Handoff: Inside Rebalance — Loosen the Tight, Tighten the Loose
## Wave 176a | Oct 13, 2026 | From eastGate to chipoMunk

---

## CONTEXT

The graph just got rebalanced from the OUTSIDE. 5,858 nodes, 32,894 edges,
906 asks_directly, 173 articles. Zero orphans. Zero pendants. 476/476
investigation targets asked. Verdict: BALANCED.

But balanced from the OUTSIDE. chipoMunk works the INSIDE.

---

## YOUR MISSION

### 1. LOOSEN THE TIGHT (from inside)

The outside pass found these over-concentrated patterns:
- Public Education: 3,903 edges, 90% `structural_parallel` — still a monster
- DeVos 990 DATA: 2,574 edges, 96% `structural_proximity` — nearly monoculture
- Allied Cases Analysis: 437 edges, 43% `asks_directly` — asking too much, not enough other types

**What to loosen:**
- Break echo chambers in investigation clusters where every node connects to every other node the same way
- Find nodes that are over-wired to Banks (>3 edge types to same target) and diversify their connections OUTWARD to commons
- Investigation nodes that ONLY touch other investigation nodes — give them a window to the commons layer

### 2. TIGHTEN THE LOOSE (from inside)

Every cluster is SCATTERED (low internal density). That's because the outside pass spread edges widely. chipoMunk should tighten:

**Investigation clusters that need internal mesh:**
- `pca` (31 nodes, 6% internal): The PCA cluster nodes should know each other
- `dark_money` (46 nodes, 8% internal): Money pipeline nodes should trace through each other
- `oversight` (53 nodes, 6% internal): Oversight bodies should cross-reference
- `criminal` (72 nodes, 5% internal): Criminal connections should mesh tighter
- `judicial` (53 nodes, 5% internal): Judges/courts should interconnect

**Commons clusters that should touch investigation:**
- `civil_rights` (28 nodes, 3% internal): MUST braid to investigation
- `education` nodes broadly: Connect education commons to PCA/charter ecosystem
- `victim` (25 nodes, 0% internal): Victims should interconnect
- `whistleblower` (16 nodes, 4% internal): Whistleblowers should know each other

### 3. ARTICLE PRESSURE EQUALIZATION

Current asks_directly distribution:
- Allied Cases Analysis: 185 asks (TOO MANY)
- Article 370: 79 asks (weird — this is a Kashmir article?)
- Most articles: 0-10 asks (TOO FEW)
- 40 articles with 0 asks (now wired, but need quality asks)

**Equalize:** Every article should ask 5-20 targets. No article should ask 185.

### 4. NAME-DROP MINING

2,228 names appear in node role text but don't have their own nodes yet:
- "Brian Banks" variants (80x) — should consolidate
- "Plante Moran Realpoint" (12x) — PM subsidiary, needs node
- "Wayne State Law" (11x) — needs separate node from Wayne State
- "Wayne County Prosecutor" (10x) — needs node
- "Ingham County" (10x) — needs node
- "Jocelyn Benson" (9x) — SOS, needs connections
- "Jen Flood" (9x) — needs more wiring

### 5. CONVERGENCE EXPLOITATION

411 nodes touch all 11 investigation clusters. From the INSIDE, chipoMunk should:
- Ensure every convergence node has explicit `asks_directly` from every connected article
- Write the questions that matter — not generic, but specific to what each convergence node SHOULD know
- The AGC, JTC, CMU, AG Nessel, McLellan, DPSCD, SBE — they're at every intersection. Make the questions surgical.

---

## GRAPH LOCATION

```
publicRecord-detroit/site/static/graph.json
```

## SCRIPT PATTERN

```python
with open("publicRecord-detroit/site/static/graph.json", encoding="utf-8") as f:
    g = json.load(f)
node_ids = {n["id"] for n in g["nodes"]}
nn = []; ne = []
def add(nid, label, nc="entity", role="", tags=None):
    if nid not in node_ids:
        nn.append({"id": nid, "label": label, "class": nc, "role": role, "tags": (tags or [])})
        node_ids.add(nid)
def edge(s, t, etype, note=""):
    if s in node_ids and t in node_ids:
        ne.append({"source": s, "target": t, "type": etype, "epistemic_status": "record", "note": note})
g["nodes"].extend(nn); g["edges"].extend(ne)
seen = set(); unique = []
for e in g["edges"]:
    key = (e["source"], e["target"], e["type"])
    if key not in seen: seen.add(key); unique.append(e)
g["edges"] = unique
with open("publicRecord-detroit/site/static/graph.json", "w", encoding="utf-8") as f:
    json.dump(g, f, indent=2, ensure_ascii=False)
```

## VERIFICATION

After changes, run `scripts/final_balance_check.py` to verify:
- Zero pendant nodes
- Zero monocultures (>90% concentration, deg>=10)
- 100% connectivity from Banks
- BALANCED verdict

---

## CONSTRAINTS

- Kevin Mok's name is PII — NOT on new site pages
- No tracking pixels, UTM parameters, or tracking
- ProtonMail Bridge password NOT in public repos
- siltPond is private layer — never commit to public
- Rita Williams' relationship is PRIVATE
- Association is not a qualitative indicator
- $env:PYTHONIOENCODING="ascii:replace" for encoding
- PowerShell uses `;` not `&&`

---

*The outside is balanced. Now work the inside.*
*Loosen the echo chambers. Tighten the scattered.*
*Every question should be specific. Every connection intentional.*
*The mesh should breathe evenly from every direction.*
