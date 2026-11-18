# Wave 59b Downstream Blurb — cellMembrane, Projects, Springs

**Date:** May 28, 2026
**From:** primalSpring coordination
**To:** cellMembrane, projectNUCLEUS, projectFOUNDATION, wet/neuralSpring

---

## P0 RESOLVED. Strategy shifts to southGate.

NUCLEUS is live on VPS. 13/13 primals, UDS sockets, zero new ports.

**All springs delayed except wet/neuralSpring.** southGate becomes the
concentrated pattern node. We prove the membrane-to-spring connection
path there, then hand off the proven patterns to other springs.

---

## For cellMembrane

**Congratulations on P0.** NUCLEUS deploy experiment absorbed and tracked.

| Next Action | Priority | Blocker |
|-------------|----------|---------|
| Set `FAMILY_ID` in `tower.env` | P0b | Config update only |
| Dark Forest re-audit (13 primals) | P2 | Post-deploy |
| Provenance pipeline re-validation | P2 | Post-deploy |
| NS registrar cutover | P4 | External |
| Forgejo releases | P4 | Config |

**VPS observations tracked in SSOT:**
- toadStool socket path (`/tmp/biomeos/` → `/run/membrane/`) — toadStool owner
- biomeOS `graph.execute` — biomeOS owner
- `nucleus_launcher` not in releases — plasmidBin owner
- coralReef stderr on `--version` — cosmetic

**NC-3.5 unblocked:** bearDog W118 resolved `auth.issue_session` content scope.
sporePrint living content can proceed when ready.

---

## For biomeOS

**New P0b: `graph.execute` over UDS.** The VPS has biomeOS v0.1.0 which
parses cell graphs but can't orchestrate node execution. This is the
single code blocker for spring emissions.

---

## For wet/neuralSpring (southGate focus team)

**You are the pattern node.** southGate is currently 7/13 health.

| Action | Priority |
|--------|----------|
| Fresh plasmidBin redeploy for southGate | P1 |
| Songbird PEERS config for mesh seeding | P1 |
| Stabilize to 13/13 NUCLEUS health | P1 |
| Run `CompositionContext::from_live_discovery()` against live sockets | P1b |
| Column U preparation (cell graph, domain_profile, health.liveness) | P1b |
| Document patterns for other springs | After P1b |

**Pattern success here unblocks all other springs.**

---

## For projectNUCLEUS / projectFOUNDATION

No new actions. Your work is fully absorbed. Continue on open items
(FN-5 Phase C, CI-R) at natural pace.

---

## For All Other Spring Teams (delayed)

**No action needed this wave.** We are concentrating on proving the
membrane connection patterns on southGate via wet/neuralSpring. When
those patterns are proven, we'll hand off a documented playbook.

Prepare column U artifacts at your own pace — the checklist is unchanged:
- Cell graph with `vps_standard = true`
- `domain_profile.toml` for lithoSpore emission
- `health.liveness` responding
- Binary in plasmidBin depot

---

*Wave 59b. NUCLEUS live. Focus southGate. Prove the patterns.*
