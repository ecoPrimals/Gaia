# Wave 111 — Remaining Work

**Date**: 2026-06-13 (overwatch cascade — post-riboCipher full convergence)  
**From**: eastGate overwatch  
**FRAGO**: `impulses/active/2026-06-11T21-30_eastGate__wave111-gate-expansion-federation-sandbox.toml`

---

## Convergence State

### riboCipher (Stream 7) — 9/9 FULL CONVERGENCE

| Team | Status | Evidence |
|------|--------|----------|
| biomeOS | ✅ SHIPPED | v4.26 — `consume_ribocipher_signal()` UDS+TCP, WARN on legacy |
| songBird | ✅ SHIPPED | 3 accept loops, `songbird_types::constants::ribocipher` module, 8929 tests |
| sweetGrass | ✅ SHIPPED | v0.7.57 — reference impl in peek.rs, 1647 tests |
| primalSpring | ✅ SHIPPED | `93207ac` — clear signal `[0xEC, 0x01]` on all IPC |
| cellMembrane | ✅ SHIPPED | `35ad803` — mito-tier HKDF+HMAC, clear on 6 UDS clients, config |
| strandGate/hotSpring | ✅ SHIPPED | server detect + client prepend, 627 tests |
| bearDog | ✅ SHIPPED | `8efc963→123e318` — server detection + client signal, all outbound IPC |
| sourDough | ✅ SHIPPED | `1f68f64` — reference implementation + deep debt evolution |

**The deprecation clock now starts.** Wave 112: WARN on legacy. Wave 113: REJECT. Wave 114: REMOVE.

### Infrastructure

- **Protocol convergence**: 13/13 HEALTH, 6/6 startup, guideStone COMPLETE
- **Stream 6 Divergence**: 14/16 shipped — remaining 2 blocked on hardware
- **Federation**: VALIDATED (64ms RTT, triad deployed, auto-reconnect proven)
- **Pipeline**: P1 automation SHIPPED (freshness auto-publish + VPS auto-rebuild + race fix)
- **ironGate NUCLEUS**: DEPLOYED 13/13 via systemd, benchScale validated
- **Bash fallback**: REMOVED, gate.provision SHIPPED, sandbox/canary SHIPPED
- **strandGate**: LIVE (265/282 validation, riboCipher COMPLIANT)
- **bearDog**: Deep evolution — discovery, storage, genetics from stubs to implementations

### Parity

| Repo | Status |
|------|--------|
| wateringHole | ⚠️ local ahead (stale auto-publish noise from unfixed VPS) |
| cellMembrane | ✅ `34e472d` (origin + forgejo + local) |
| bearDog | ✅ `123e318` (origin + forgejo + local) |
| songBird | ✅ `8effb942` (origin + forgejo + local) |
| biomeOS | ✅ `6d887ea1` (origin + forgejo + local) |
| sweetGrass | ✅ `a00407d` (origin + forgejo + local) |
| primalSpring | ✅ `494c364` (origin + forgejo + local) |
| sourDough | ⚠️ forgejo at `367876d`, origin at `1f68f64` (forgejo 500 error persists) |

### Known Issues

1. **VPS freshness auto-publish is generating Wave 109 junk commits** — gates running old membrane binary (`pre-082d77c`) keep pushing stale freshness. The race-condition fix shipped in `082d77c` but VPS hasn't been rebuilt yet.
2. **sourDough forgejo parity** — remote returns HTTP 500 on push.

---

## Remaining Work by Team

### cellMembrane (Critical Path)

| Item | Priority | Notes |
|------|----------|-------|
| **VPS cellMembrane rebuild** | P1 | Deploy `34e472d` to VPS — stops Wave 109 junk commits, enables mito-tier |
| **VPS `plasmid.harvest --all`** | P1 | Depot integrity — rebuilds all binaries from current HEADs |
| Dev gate cascade | P2 | `temporal.cascade --with-restart` on eastGate/southGate |
| westGate gate.bootstrap | P2 | Nest Atomic profile on 76TB ZFS |
| NUC canary bootstrap | P2 | `canary-fieldmouse` profile — Phase 1 VPS minimization |
| Tolerances in deployment.toml | P3 | 4 named tolerances pending codification |
| Pipeline commands | P3 | docs.publish, git.publish, impulse.resolve, wave.close |
| blueGate + swiftGate | P3 | Windows cross-platform |
| northGate | LAST | Family gate, spare compute when not in use |

### bearDog

| Item | Priority | Notes |
|------|----------|-------|
| Continue deep evolution | P3 | discovery, storage, genetics moved from stubs to impls (`dbc422d`) |

riboCipher COMPLETE. Remaining is maturation-path (no longer blocking convergence).

### songBird

| Item | Priority | Notes |
|------|----------|-------|
| VPS persistent relay | P2 | Depot needs latest — auto-rebuild after VPS update |

Code COMPLETE. Remaining is operational.

### sourDough

| Item | Priority | Notes |
|------|----------|-------|
| `validate ribocipher` subcommand | P2 | Audit tool for fleet compliance checking |
| Scaffold template update | P2 | New primals born with riboCipher |
| Forgejo parity | P2 | Fix 500 error |

Reference impl SHIPPED. Remaining is tooling maturation.

### toadStool

| Item | Priority | Notes |
|------|----------|-------|
| **TOADSTOOL-AUTO-REGISTER** | P2 | PCI/sysfs enumeration — auto-register GPU/NPU with biomeOS |

### primalSpring

| Item | Priority | Notes |
|------|----------|-------|
| nucleus_launcher aarch64 | P3 | grapheneGate ARM cross-compile |
| Proto-nucleate manifest | P3 | Sub-NUCLEUS topology definition |

### ops (hardware)

| Item | Priority | Notes |
|------|----------|-------|
| **westGate power-on** | P2 | i7-4771 + 76TB ZFS — network + gate.bootstrap |
| NUCs + Pixle | P2 | Quick Linux node enrollments |
| DEPLOY-THEN-STALE (Stream 6) | P2 | Deploy westGate, skip cascades 2 waves |
| WINDOWS-ECOBIN-DIVERGENCE (Stream 6) | P3 | Deploy to blueGate, measure delta |
| Akida NPU driver | LOW | BrainChip AKD1000 on strandGate |
| northGate | LAST | After all others stable |

---

## Convergence Gate

Old patterns permanently excised when ALL criteria GREEN:

| # | Criterion | State |
|---|-----------|-------|
| 1 | All gates run post-34e472d membrane | ⚠️ ironGate DEPLOYED, others pending VPS rebuild + cascade |
| 2 | Depot fully fresh (all 13 BLAKE3 match) | ⚠️ VPS auto-rebuild pending |
| 3 | flockGate persistent relay active | ⚠️ needs VPS songBird rebuild |
| 4 | No gate uses bash fallback | ✅ CODE DONE |
| 5 | canary.audit passes on canary node | ❌ NUC bootstrap pending |
| 6 | 2 full cascade cycles, zero intervention | ❌ Not yet tested (VPS blocks) |
| 7 | Version skew = 0 after cascade | ❌ Not yet tested |
| 8 | riboCipher: all primals converged | ✅ 9/9 SHIPPED |

**To clear**: VPS rebuild (`34e472d`) → harvest → cascade all gates → NUC bootstrap → 2 clean cycles.

---

## Priority Order

1. **VPS**: Rebuild cellMembrane to `34e472d` (stops junk commits, enables mito-tier, unblocks everything)
2. **VPS**: `plasmid.harvest --all` (depot integrity)
3. **eastGate/southGate/grapheneGate**: `membrane temporal.cascade --with-restart`
4. **NUC**: `gate.bootstrap` with `canary-fieldmouse` profile
5. **westGate**: Hardware power-on + gate.bootstrap
6. **sourDough**: `validate ribocipher` tooling + scaffold update
7. **toadStool**: TOADSTOOL-AUTO-REGISTER

---

## Active Documents

| Document | Purpose |
|----------|---------|
| This blurb | Remaining work overview |
| `impulses/active/...wave111...toml` | Wave 111 FRAGO (Stream 6 + Stream 7) |
| `RIBOCIPHER_TRANSPORT_SIGNAL_STANDARD.md` | riboCipher standard (9/9 converged) |
| `GATE_NUCLEUS_SYSTEMD_STANDARD.md` | systemd deployment standard |
| `CONVERGENCE_GATE_WAVE111_PATTERN_DEPRECATION_JUN12_2026.md` | Pattern deprecation criteria |
| `handoffs/CELLMEMBRANE_RIBOCIPHER_DISPATCH_SRP_WAVE111_JUN13_2026.md` | cellMembrane mito-tier |

---

**WAVE 111 CLOSED** — riboCipher 9/9 FULL CONVERGENCE achieved. All code work complete. Remaining operational items carried to **Wave 112** (`WAVE112_KICKOFF_BLURB_JUN13_2026.md`). The deprecation clock is ticking — Wave 112 escalates WARN→ERROR.
