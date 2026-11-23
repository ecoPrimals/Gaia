# Wave 57 Downstream Blurb — cellMembrane, Projects, Springs

**Date:** May 28, 2026
**From:** primalSpring coordination
**To:** cellMembrane, projectNUCLEUS, projectFOUNDATION, all spring teams

---

## What primalSpring Shipped (Wave 57)

- **main.rs split** — 804L monolith → `main.rs` + `serve.rs` + `registry_lint.rs`
- **Last hardcoded env var eliminated** — `biomeos.rs` graphs discovery → `env_keys`
- **NeuralBridge unreachable eliminated** — `ProtocolError` instead
- **Doctest fixes** — `CompositionContext::signal`/`dispatch` type mismatches fixed
- **NC-1 COMPLETE absorbed** — biomeOS v3.81 `biomeos-pseudospore` + emit materialization
- **Downstream absorption** — your Wave 56 work is tracked in `PRIMAL_GAPS.md`
- **Port SSOT confirmed** — `tolerances/mod.rs` matches `ports.env` exactly
- **`health.liveness` confirmed** as canonical method (FOUNDATION ask answered)
- **797 lib tests**, 56 scenarios, zero clippy, zero unsafe

---

## For cellMembrane

**Your Wave 56 VPS standard is fully absorbed and tracked.** We confirmed:

| Item | Status |
|------|--------|
| `TransportMode` enum consumed | Tracked in PRIMAL_GAPS NC-3 |
| `--uds-only` + `deploy_membrane.sh` | Acknowledged |
| Port SSOT reconciliation | Verified — all 14 ports match |
| Spring overlay mode | Documented in VPS contract |
| 93 tests, 13 transport tests | Acknowledged |

**Your next actions:**
1. **Deploy biomeOS v3.81 to VPS** — critical path for NC-1 live + spring emissions
2. **Test `spring-overlay` with hotSpring** — first spring to pass column U
3. NC-3.3 NS cutover — registrar coordination (not code-blocked)
4. NC-3.4 Forgejo releases — Forgejo instance configuration

**Remaining debt we noted:** `deploy_membrane.sh` (1378L) split candidate. Not blocking.

---

## For projectNUCLEUS

**Your Wave 56 `--uds-only` deploy is fully absorbed.** Status update:

| Item | Status |
|------|--------|
| 13 primal `--uds-only` deploy cases | Tracked in NC-4 |
| `socket_health_check()` | Acknowledged |
| Cell graphs consumed (6 VPS, 3 desktop) | Acknowledged |
| 65 Rust tests | Acknowledged |

**Please update your local NC-1 status from WIRED → COMPLETE.** biomeOS v3.81
shipped `biomeos-pseudospore` + full emit materialization. Your handoff
`PROJECTNUCLEUS_WAVE56_ABSORPTION_MAY27_2026.md` still shows NC-1 as WIRED.

**No blocking actions.** Your deploy tooling is aligned.

---

## For projectFOUNDATION

**Your Wave 56b deep debt is absorbed.** Answers to your asks:

| Question | Answer |
|----------|--------|
| Is `health.liveness` canonical? | **YES** — all primals implement it. Certification Layer 2 uses it. `health.check` is an alias. |
| `FAMILY_ID` discovery via JSON-RPC? | biomeOS confirms `family.id` method — verify on v3.81 |

**Your next actions:**
1. FN-5 Rust elevation Phase B — unblocked by Wave 56
2. Thread 10 live test once biomeOS v3.81 is deployed
3. BLAKE3 backfill threads 4, 5, 1 — blocked on `.data/` fetch (not primalSpring-related)

**Gap 8 (toadStool env expansion in workload TOMLs):** Noted, will coordinate with toadStool.

---

## For All Spring Teams

See the dedicated **Springs Delta Blurb** for per-spring status and actions.

**Summary:** cellMembrane is ready to deploy spring overlays. The 3-step VPS
deployment path is operational. Springs should prepare for column U passes
once biomeOS v3.81 is live on VPS.

---

*Wave 57. All downstream work absorbed. Deploy path clear.*
