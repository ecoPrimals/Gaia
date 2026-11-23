# Licensing and Copyleft — scyBorg Framework

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | April 4, 2026 |
| **Status** | Active |

This document consolidates the lysogeny copyleft strategy, the scyBorg triple-license standard (including the provenance trio), and the symbiotic exception protocol. Source materials: `LYSOGENY_PROTOCOL.md`, `SCYBORG_PROVENANCE_TRIO_GUIDANCE.md`, `SCYBORG_EXCEPTION_PROTOCOL.md`.

---

## Philosophy

**Lysogeny** is the ecoPrimals strategy for permanently opening proprietary technology gates by combining documented prior art, cross-domain validation, independent implementation, and **AGPL-3.0-or-later** copyleft. The name analogizes to lysogenic phage biology: copyleft integrates into derivatives and, when adoption occurs, forces openness. Lysogeny is **area denial**, not siege: it does not attack existing proprietary deployments; it reduces the addressable market for proprietary expansion by publishing a free, AGPL-protected alternative backed by prior art and generality proofs.

### Copyleft strategy in brief

1. Identify a proprietary gate (algorithm, platform, or system restricting access).
2. Trace underlying mathematics to **published open research** (prior art).
3. Implement from first principles under **AGPL-3.0-or-later**.
4. Cross-validate across domains (proves generality, not domain-specific IP).
5. Document the **provenance chain** (seven links; see below).
6. Publish and wait; adoption propagates copyleft and weakens proprietary claims on the math.

### Three layers of protection (all required)

Every lysogeny target must satisfy all three; omission weakens legal defensibility.

| Layer | Role | Standard |
|-------|------|----------|
| **Prior art** | Math exists in published, peer-reviewed literature predating the proprietary implementation. | Citations with author, journal, year, page; publication must **predate** the proprietary patent filing (if patented) or first public release (if trade-secreted). |
| **Cross-domain generality** | Same mathematics validated in at least two distinct domains. | At least one cross-domain validation with passing checks in a domain unrelated to the proprietary system’s market. |
| **Independent derivation** | Implementation derives only from published research. | Every source file traceable to published citations only; no proprietary code, assets, documentation, APIs, or reverse-engineering in implementation, comments, or docs. |

**Prior art research (minimums):** at least three independent citations per core algorithm; all pre-patent/pre-release; cross-reference fields; catalog the chain.

**Cross-domain validation:** same barraCuda primitive in both domains; vocabulary mapping (domain A ↔ domain B); independent checks (not a shared test harness). May be one spring, a partner spring, or both.

### Provenance chain (seven links)

1. Published paper (pre-patent) describing the mathematical model.  
2. barraCuda primitive implementing the model (or spring-local with absorption path).  
3. Spring experiment applying the math in the target domain.  
4. Cross-domain experiment validating the same math in another domain.  
5. Vocabulary mapping table proving generality.  
6. **AGPL-3.0-or-later** on all code.  
7. wateringHole documentation (catalog entry + handoff).

Links 1–5 support the three protection layers; link 6 is the copyleft mechanism; link 7 is ecosystem coordination.

### Relationship to scyBorg

Lysogeny operates **inside** the scyBorg framework. Lysogeny’s AGPL requirement is one layer of scyBorg; mechanics and creative outputs from the process also fall under **ORC** and **CC-BY-SA 4.0** as applicable. See **The scyBorg Framework** below.

### Area denial model (summary)

The proprietary vendor’s installed base is largely untouched; lysogeny targets **prospective** customers and new markets where an AGPL alternative with prior art and cross-domain proof reduces proprietary growth. The AGPL propagates through derivatives; documented prior art and generality weaken domain-specific IP arguments.

### Implementation norms (lysogeny targets)

Targets are implemented **only** from published math: **AGPL-3.0-or-later** license header on every file; **Pure Rust** with `#![forbid(unsafe_code)]` where applicable; use barraCuda primitives when available; **hotSpring-style** validation (hardcoded expected values, exit code 0/1); source files under **1000 lines**; **no TODO/FIXME/HACK** in shipping source. Catalog entries live under the spring’s `specs/` directory; handoffs go to **wateringHole** for ecosystem visibility.

---

## The scyBorg Framework

**scyBorg** is the ecoPrimals **triple-copyleft** licensing standard. It applies to every primal, spring, experiment, tool, and derivative work unless a **symbiotic exception** (see below) explicitly covers author-owned contributions for a named grantee.

### Formula and layers

```
scyBorg = AGPL-3.0 (code) + ORC (game mechanics) + CC-BY-SA 4.0 (creative content)
```

| Layer | License | Covers | Governing body |
|-------|---------|--------|----------------|
| Software | **AGPL-3.0-or-later** | Engine, tools, shaders, math, infrastructure | FSF (nonprofit) |
| Mechanics | **ORC** | Rules, stat blocks, progression, encounter math | Open RPG Creative Foundation (nonprofit) |
| Creative | **CC-BY-SA 4.0** | Art, worlds, narrative, characters, music, sound, maps, papers, docs | Creative Commons (nonprofit) |
| Reserved | **ORC Reserved Material** | Studio-specific branding, trademarks, trade dress | Creator retains |

No single entity can unilaterally revoke these license regimes; governance is structural (independent nonprofits), not contractual opt-in.

### AGPL-3.0-or-later (all code)

Applies to Rust sources, WGSL, build scripts, configs, tests, experiments, and tools across listed primals and springs (e.g. BearDog, barraCuda, coralReef, rhizoCrypt, sweetGrass, loamSpine, skunkBat, ludoSpring, wetSpring, hotSpring, and future components). Implications include: derivatives must be **AGPL-3.0-or-later**; **network use** triggers distribution obligations; SaaS wrappers around ecoPrimals code must release source.

### ORC (game mechanics)

ORC Licensed Material covers game rules, stat blocks, progression systems, encounter math, and mechanical designs. **ORC is irrevocable and perpetual** for licensed material.

### CC-BY-SA 4.0 (creative content)

Non-code creative output requires **attribution**; **share-alike** propagates to derivatives.

### Reserved material

Branding, primal names, logos, and related trade dress remain under **ORC Reserved Material** and do not restrict code or mechanics under the other layers.

### Why three layers

A single license cannot cover code, game rules, and creative works simultaneously; scyBorg closes gaps so no major artifact class lacks copyleft-aligned terms.

### Defense in depth (ecosystem)

| Layer | Mechanism | Protects |
|-------|-----------|----------|
| Lysogeny | Prior art + independent derivation + cross-domain proof | Algorithms/math from proprietary patent/secret claims |
| scyBorg | AGPL + ORC + CC-BY-SA | Code, mechanics, creative work from proprietary closure |
| Provenance trio | Machine-verifiable attribution and derivation | Evidentiary chain for violations |
| skunkBat | Network/runtime threat response | Runtime extraction patterns |

### Provenance trio (enforcement of scyBorg as evidence)

- **sweetGrass** — who created what (BY in CC-BY-SA).  
- **rhizoCrypt** — derivation chains (SA in CC-BY-SA).  
- **loamSpine** — immutable license certificates (proof that terms apply).

Together, they make scyBorg **machine-verifiable** and attributable; without them, scyBorg is primarily declarative in repository metadata.

### Content categories and machine-readable licenses

Artifacts should declare category: **Code** (AGPL-3.0-or-later), **GameMechanics** (ORC), **CreativeContent** (CC-BY-SA 4.0), **Reserved** (ORC Reserved Material). Use **SPDX** expressions where applicable (e.g. `AGPL-3.0-or-later`, `CC-BY-SA-4.0`). Derivation tracking supports share-alike evidence (rhizoCrypt DAG, license metadata on vertices, certificates in loamSpine).

### Non-goals (for trio implementation)

- Do **not** build automated license **enforcement** in place of law—the trio provides **evidence**; copyright and license terms remain the enforcement layer.  
- Do **not** build complex license compatibility checkers beyond the chosen non-conflicting stack.  
- Do **not** gate product functionality on license metadata fields.

### Cross-spring applicability

scyBorg applies universally: e.g. ludoSpring (game code + design specs), wetSpring (pipelines + models), hotSpring (simulations + reports), healthSpring (clinical tools + outcome documentation), etc.

### External references

- [AGPL-3.0](https://www.gnu.org/licenses/agpl-3.0.html)  
- [ORC License](https://azoralaw.com/orclicense/)  
- [CC-BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)  
- [SPDX License List](https://spdx.org/licenses/)

---

## Symbiotic Exceptions

A **symbiotic exception** grants **additional permissions** beyond default scyBorg (**AGPL-3.0 + ORC + CC-BY-SA 4.0**) to a **named** organization or project when **reciprocal benefit** exists. **Exceptions are not for sale**; they are license-as-diplomacy, not dual licensing for revenue.

### Legal basis

**AGPL-3.0 Section 7** allows **additional permissions** that supplement the license by excepting named conditions. The copyright holder may:

- Grant named organizations permission to use contributions under terms other than AGPL-3.0 for specified scope.  
- Limit scope to specific code, projects, or use cases.  
- Tie duration and revocability to the reciprocal relationship.

**Critical constraint:** Exceptions apply only to **code the author owns**. For forks of upstream AGPL projects, the exception covers **only the author’s original contributions**, never upstream code.

### Exception tiers

| Tier | Who | Default license | Exception | Reciprocal basis |
|------|-----|-----------------|-----------|------------------|
| **Public** | Everyone | Full scyBorg | None | Prior art, community, lysogeny |
| **Symbiotic** | Named orgs/projects | Full scyBorg | May incorporate **author’s** contributions under their **existing** license | Tools, hardware, knowledge |
| **Reciprocal Open** | Orgs opening their work | Full scyBorg | May incorporate under their license | They publish specs/docs/code under **AGPL or equivalent copyleft** |

**Public tier** is the constitutional baseline (full scyBorg for all); it cannot be weakened.

**Symbiotic tier** allows incorporation of author-original work under the partner’s license for covered scope; the **public scyBorg tree remains unchanged**; both forks may evolve in parallel.

**Reciprocal Open tier** rewards vendors who publish proprietary knowledge under AGPL or equivalent copyleft with strongest mutual benefit and precedent for future partners.

### Exception grant record (fields)

| Field | Purpose |
|-------|---------|
| **Grantee** | Named organization or project |
| **Scope** | Which ecoPrimals code/contributions are covered |
| **Terms** | What the grantee may do (e.g. incorporate into proprietary products) |
| **Reciprocal basis** | What ecoPrimals receives |
| **Duration** | Ongoing while reciprocity holds, or fixed term |
| **Sublicense** | Whether third-party sublicense (default: **no**) |
| **Revocability** | When the exception may end |

### What an exception does **not** grant

- Rights to **upstream** code (author-original only).  
- Rights to **relicense** the public scyBorg version.  
- Rights to **block** others from using the public AGPL version.  
- **Trademark**, branding, or **ecoPrimals name** rights.  
- **Exclusivity**—the same contribution remains available to everyone under AGPL.

### Candidate examples (not formalized as active grants)

| Candidate | Notes |
|-----------|--------|
| **RustDesk** | Partner AGPL-3.0; scope: ecoPrimals contributions to a fork; terms: incorporate under existing AGPL; reciprocal: remote access infrastructure. |
| **BrainChip (Akida)** | Scope: rustChip / Akida integration; terms: incorporate into proprietary products without AGPL on those contributions; reciprocal: hardware, docs, support; requires **100% author-owned** code. |
| **GPU vendor (Reciprocal Open)** | Scope: e.g. coralReef compiler; terms: vendor may incorporate improvements; reciprocal: architecture documentation under **AGPL-3.0 or equivalent copyleft**. |

### Process for granting an exception

1. Identify reciprocal value.  
2. Scope the exception (specific code/contributions).  
3. Verify **100% copyright ownership** of excepted code (no inappropriate upstream mixing).  
4. Draft grant: grantee, scope, terms, reciprocal basis, duration, sublicense, revocation.  
5. Publish in the **Exception Registry** (below).  
6. Notify the partner.  
7. Review annually whether reciprocity persists.

### Exception Registry

Active symbiotic exceptions are listed here when formalized. *As of consolidation, the registry was empty; first grants pending formalization.*

| # | Grantee | Scope | Tier | Status | Date |
|---|---------|-------|------|--------|------|
| — | — | — | — | — | — |

### Additional references

- [AGPL-3.0 Section 7](https://www.gnu.org/licenses/agpl-3.0.html#section7) (additional permissions)

---

## Version History

| Version | Date | Notes |
|---------|------|--------|
| **1.0.0** | April 4, 2026 | Initial consolidated document. Merges **Philosophy** and lysogeny lifecycle/provenance content from `LYSOGENY_PROTOCOL.md`; **The scyBorg Framework** and provenance trio from `SCYBORG_PROVENANCE_TRIO_GUIDANCE.md`; **Symbiotic Exceptions** (legal basis, tiers, scope, registry, process) from `SCYBORG_EXCEPTION_PROTOCOL.md`. Domain-specific lysogeny catalogs, implementation backlogs for sweetGrass/rhizoCrypt/loamSpine, and extended narrative sections are abbreviated here; refer to the original files for full tables and phased engineering detail. |
