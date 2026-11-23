# Wave 58 Downstream Blurb — cellMembrane, Projects, Springs

**Date:** May 28, 2026
**From:** primalSpring coordination
**To:** cellMembrane, projectNUCLEUS, projectFOUNDATION, all spring teams

---

## For cellMembrane

**Your Wave 57 deep debt sprint is absorbed.** Tracked:

| Item | Status |
|------|--------|
| 95.8% coverage, typed `CellMembraneError` | Absorbed in PRIMAL_GAPS NC-3 |
| `deny.toml`, `rustfmt.toml`, licensing | Acknowledged |
| 174+ tests (up from 93) | Acknowledged |
| Envelope validation + firewall + credential tests | Acknowledged |

**Your next actions (unchanged):**
1. **P0: Deploy biomeOS v3.84 to VPS** — the single remaining blocker
2. **Test `spring-overlay` with hotSpring** — first emission candidate
3. NS registrar cutover (external, not code-blocked)
4. Forgejo releases (config, not code-blocked)

---

## For projectNUCLEUS

**Your Wave 58 deep debt is absorbed.** Tracked:

| Item | Status |
|------|--------|
| 166 Rust tests (from 65) | Absorbed in PRIMAL_GAPS NC-4 |
| Async-correct health (spawn_blocking) | Tracked — critical fix |
| Wire-native NDJSON-RPC discovery | Tracked — protocol alignment confirmed |
| Deploy script port parameterization | Tracked |
| chrono removed, test runtime 68s → 3s | Acknowledged |

**Wire protocol confirmed:** primalSpring uses newline-delimited JSON-RPC
(`write_all(response_json)` + `write_all(b"\n")`). Your discovery migration
to `send_jsonrpc_newline()` is correct.

**NC-1 status correction:** Please update your local tracking from
**WIRED → COMPLETE**. biomeOS v3.84 shipped `biomeos-pseudospore` with full
envelope validation + emit materialization (May 27, 2026).

**No blocking actions.** Deploy tooling is aligned.

---

## For projectFOUNDATION

**No new changes from your side since Wave 56b.** Previous answers still apply:

| Question | Answer |
|----------|--------|
| `health.liveness` canonical? | **YES** — all 13 primals, Cert Layer 2 |
| `FAMILY_ID` discovery? | biomeOS `family.id` method — verify on v3.84 |

FN-5 Rust elevation Phase B remains unblocked.

---

## For All Spring Teams

See **WAVE58_SPRINGS_DELTA_BLURB** for per-spring priorities.

**Summary:** All infrastructure is ready. Awaiting biomeOS v3.84 VPS deploy
to begin spring emissions.

---

*Wave 58. All downstream absorbed. One action remaining: deploy v3.84.*
