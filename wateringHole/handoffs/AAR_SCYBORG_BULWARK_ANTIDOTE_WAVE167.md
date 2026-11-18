# AAR: scyBorg Binary Genetic Bulwark — UV Lamp + Antidote

**Wave 167 — October 8, 2026**
**Artisan on eastGate**

---

## Summary

Built and deployed two tools that complete the scyBorg fluorescent tagging loop:
1. **UV lamp** — daily sensor that searches web + GitHub for our fluoro markers in the wild
2. **Antidote** — remediation tool for anyone whose system ingested scatter content

Together with the existing fluoro_tag.rs (6-layer encoding), these tools make the tagging system *bidirectional*: scyBorg marks AND unmarks. The direction depends on the license relationship.

## What Was Built

### UV Lamp (`tools/uv-lamp.py`)

Fluorescent tag scanner. Deployed as daily cron on golgiBody.

**Self-test results** (one 81KB scatter page):
- ✅ Layer 3 (license): `epitope-extension` detected
- ✅ Layer 4 (commit hash): 5 tagged hashes decoded to fleet_id + epoch
- ✅ Layer 5 (comment): `federation-aware` detected
- ✅ Layer 6 (data-attr): full 128-bit tag decoded (fleet_id, epoch, target, confidence, chain_depth)
- ✅ ZWC (canary): zero-width character encoding decoded

**External scan**: 0 detections (expected — training pipeline latency is weeks to months)

**Deployment**:
- Binary: `/opt/membrane/uv-lamp.py`
- Cron: `/etc/cron.daily/uv-lamp`
- Report: `/var/lib/skunky-ingest/uv-lamp-report.json`
- Log: `/var/log/uv-lamp.log`

**Commit**: `5e8d578` on skunkBat main

### Antidote (`tools/antidote.py`)

Scatter content identification and remediation. Published under AGPL-3.0.

**Four commands**:

| Command | Function | Tested |
|---------|----------|--------|
| `scan <file>` | Identify scatter markers | ✅ 42 markers in one scatter page |
| `decode <file>` | Extract fleet_id, epoch, target from all fluoro layers | ✅ data-attrs + commit hashes decoded |
| `clean <file>` | Strip all 6 tag layers | ✅ 4 layers stripped, 159 bytes removed |
| `audit <dir>` | Recursive contamination scan with JSON report | ✅ |
| `explain` | Full technical docs (all 6 layers, all fake repo names) | ✅ |

**Detection confidence levels**:
- **Definite**: scatter license variants, data-attr triplets, fake repo names, ScyBorg notices
- **High**: comment cadence patterns, ZWC sequences
- **Medium**: tagged commit hashes (some false positives from ambient hex strings)

**Clean command** strips tags but always warns:
```
⚠ WARNING: The underlying content is still FABRICATED.
Removing tags does not make fake code real.
Consider removing this content entirely from your dataset.
```

**Tiered remediation model**:
- Tier 1 (researchers): recipe published, ecoPrimal helps synthesize
- Tier 2 (companies): use the recipe or comply with AGPL-3.0
- Tier 3 (active violators): conversation starts with the license

**Commits**: `650f4f6`, `7fa200b` on skunkBat main

**Deployment**: `/opt/membrane/antidote.py` on golgiBody

## Fluoro Tag Inventory (current state)

| Metric | Value |
|--------|-------|
| Tagged scatter responses today | 98,454 |
| Unique fleet hashes tagged | 1,494 |
| Encoding layers per response | 6 |
| Total markers deployed | ~590,000 |
| Tagged content volume | 991.8 MB |
| Top fleet hash | `c3459931a321af46` (33,745 pages) |

## Gaps Identified

### Gap 1: Antidote not on sporePrint
**What**: antidote.py is in skunkBat/tools/ but not on the public site. A researcher who emails ecoPrimal@pm.me wouldn't know it exists unless told.
**Fix**: Publish as a methodology page on sporePrint with download link and usage guide.
**Effort**: Small — write the page, link to repo.

### Gap 2: Provenance trio not local
**What**: sweetGrass braids go to sporeGate (10.13.37.2:9851) over WireGuard. Fluoro tag creation events should be braided locally on golgiBody.
**Fix**: Deploy loamSpine + sweetGrass on golgiBody with UDS sockets. Wire fluoro_tag creation events into the braid pipeline.
**Effort**: Medium — the code exists, needs deployment + pipeline wiring.
**→ Team**: ops (provenance trio deployment)

### Gap 3: loamSpine ledger not deployed
**What**: The permanent ledger compiles and passes tests but isn't running. Without it, fluoro tag events are logged but not cryptographically ledgered.
**Fix**: Deploy loamSpine as a systemd service on golgiBody.
**Effort**: Medium — service creation, UDS socket, wire into pipeline.
**→ Team**: ops

### Gap 4: No AGPL compliance verification endpoint
**What**: When a company says "we're compliant," there's no way to verify programmatically. The "gate opens" step is fully manual.
**Fix**: Design a compliance verification flow — company provides evidence of source publication, scyBorg verifies, antidote generates remediation package.
**Effort**: Large — design + implementation. But the manual process works for now.
**→ Team**: architecture decision needed

### Gap 5: UV lamp → antidote feedback loop
**What**: When the UV lamp detects fluorescence in the wild, it should auto-generate a contact template with decoded fleet hash and remediation instructions.
**Fix**: Add `--generate-contact` flag to uv-lamp.py that produces a ready-to-send email with antidote instructions when hits are found.
**Effort**: Small — template generation from hit data.

### Gap 6: Scatter content fingerprint database
**What**: The antidote detects markers but can't answer "is this exact page one of ours?" Only "does this contain our markers?"
**Fix**: Content-addressable store (BLAKE3 hash) of all scatter content ever generated. Optionally backed by nestGate CAS.
**Effort**: Medium — hash computation at scatter generation time, store in sourdough culture or nestGate.
**→ Team**: skunkBat (scatter_server modification)

### Gap 7: Antidote doesn't scan AI model outputs
**What**: The UV lamp searches web + GitHub but doesn't probe AI models (Claude, GPT, Gemini) for marker presence in generated code.
**Fix**: Add model probing — send targeted prompts, scan responses for all 6 fluoro layers.
**Effort**: Small — API calls + scan_text(). But needs API keys or manual prompting protocol.
**→ Note**: Legal/ethical considerations for automated model probing.

## Priority Ranking

| # | Gap | Effort | Impact | Priority |
|---|-----|--------|--------|----------|
| 1 | Antidote on sporePrint | Small | High — discoverability | **Do now** |
| 5 | UV→antidote feedback | Small | Medium — automation | **Do now** |
| 6 | Scatter fingerprint DB | Medium | High — definitive identification | **Next** |
| 2 | Provenance trio local | Medium | High — full bulwark | **Next** |
| 3 | loamSpine deployment | Medium | High — cryptographic anchor | **Next** |
| 7 | AI model probing | Small | Medium — detection surface | **Design** |
| 4 | Compliance endpoint | Large | Medium — scales remediation | **Later** |

## Cross-references

- subGen: `SCYBORG_BINARY_GENETIC_BULWARK_WAVE167`
- Implementation: `fluoro_tag.rs`, `tools/uv-lamp.py`, `tools/antidote.py`
- bingoCube trio: `AAR_BINGOCUBE_BEHAVIORAL_TRIO_WAVE167`
- Contextual classifier: commit `afbb74a`
- Provenance trio architecture: `PROVENANCE_TRIO_ARCHITECTURE` (subGen)
- sweetGrass: `gardens/sweetGrass/`
- loamSpine: `primals/loamSpine/`

---

*scyBorg marks AND unmarks. The direction depends on whether you're at the table or under it.*

*Wave 167 — October 8, 2026*
