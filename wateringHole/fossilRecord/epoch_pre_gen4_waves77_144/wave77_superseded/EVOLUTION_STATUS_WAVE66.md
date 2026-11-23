# Evolution Status — Wave 66 Checkpoint

**Date**: 2026-06-01
**Phase**: Shadow validation + non-temporal work sprint
**Authority**: eastGate overwatch
**Prior**: Wave 65 checkpoint (fossilized)

---

## Where We Are

Wave 66 marks the transition from construction to operational validation.
The S1 TLS 7-day shadow has **PASSED** (13 days). wateringHole has been
cleaned to **zero code** — it's now purely comms (manifests, impulses,
handoffs, standards, binary distribution). ironGate delivered deep debt
completion for projectNUCLEUS (235 tests, 9 nucleus-deploy subcommands).
flockGate validated K-Derm relay and cursor hook auto-injection.
The VPS stack runs 20/20 primal membrane services with zero crashes
since the May 28 deployment cycle.

---

## System Topology

### K-Derm Diderm Envelope (VPS)

```
GitHub ←──weak──── golgiBody-ext (137.184.197.151)
                        │ ionic           Knot DNS + Caddy 2.11.3 + sporePrint
                   peptidoglycan ([RELAY_PUBLIC])
                        │ metallic        membrane binary + full ecosystem
                   golgiBody-inner ([RELAY_PUBLIC])
                   ┌────┤ covalent        20 primal services + Forgejo 15.0.2
              eastGate   ironGate   southGate   biomeGate   flockGate
              (LAN)      (LAN)      (LAN)       (LAN)       (WAN)
```

### VPS Health (Collected June 1, 2026)

| Node | Uptime | Disk | Services | Key |
|---|---|---|---|---|
| golgiBody | 16d 18h | 6.3G/9.7G (68%) | 20 active | All primals + Forgejo |
| peptidoglycan | 1d 21h | 6.5G/79G (9%) | membrane only | Relay mediator |
| golgiBody-ext | 1d 21h | 2.8G/50G (6%) | Knot + Caddy | Outer membrane |

### Gate Status

| Gate | Status | Role | Temporal Sync |
|---|---|---|---|
| eastGate | OPERATIONAL | Orchestrator, overwatch | Full superset (39 repos) |
| ironGate | OPERATIONAL | ABG compute, dev | 22 repos, Wave 64 debt complete |
| southGate | OPERATIONAL | Gaming + compute | Core + wet/neural |
| biomeGate | OPERATIONAL | HBM2 test bench | Core + hotSpring (19/19) |
| flockGate | OPERATIONAL | WAN covalent, sporePrint | Full superset (~1.3s Forgejo) |
| strandGate | Hardware ready | Bioinformatics | Not deployed |
| northGate | Hardware ready | Heavy compute | Not deployed |
| westGate | Hardware ready | Cold storage (76TB ZFS) | Not deployed |

### Sovereignty Shadows

| Track | Status | Detail |
|---|---|---|
| S1 TLS | **PASSED** (13 days) | beardog-tls-shadow running since May 19, 3.3M RAM, <2s CPU |
| S2 NAT | LIVE (100%) | RustDesk hbbs/hbbr running 17 days on golgiBody |
| S3 Content | LIVE (67ms TTFB) | Sovereign Forgejo + Knot DNS, sporePrint on Caddy |
| S4 Auth | Pending | ironGate team needs to configure beardog auth services |
| DNS | ns1+ns2 LIVE, DNSSEC | Zone replication healthy (hourly refresh), awaiting registrar NS cutover |

### TLS Certificate Status (golgiBody)

| Domain | Issuer | Issued | Expires | Auto-renew |
|---|---|---|---|---|
| git.primals.eco | Let's Encrypt (YE2) | May 28, 2026 | Aug 26, 2026 | Caddy ACME |
| membrane.primals.eco | Let's Encrypt | Active | Active | Caddy ACME |

---

## What's New Since Wave 65

### Wave 66 Deliveries

1. **wateringHole → zero code**: All 11 scripts fossilized or relocated to owners
   - 5 relay scripts → fossilRecord (superseded by `relay.rs`)
   - `cascade-pull.sh` (1029L) → fossilRecord (superseded by `temporal.cascade`)
   - `bootstrap.sh`, `beacon_tunnel.sh`, `s1-tls-gate-probe.sh`, `setup-jupyterhub.sh` → fossilRecord
   - `golgi-post-receive-relay.sh` → cellMembrane/deploy/hooks/forgejo/
   - `context-sense.sh` → cellMembrane/deploy/hooks/cursor/
   - `cloudflared-config.yml.template` → fossilRecord (sovereignty supersedes)
   - `wetspring-science-facade.service` → springs/wetSpring/deploy/
   - systemd units updated to reference `membrane temporal.cascade`

2. **ironGate: projectNUCLEUS deep debt** (via impulse)
   - 235 tests, 9 nucleus-deploy subcommands
   - Security module split, shared util, Songbird transport
   - Context braid active

3. **flockGate: K-Derm relay validation**
   - Diderm envelope validated end-to-end
   - K-NOME cursor hook live (context.sense auto-injection)

4. **S1 TLS shadow: GRADUATED**
   - 13-day continuous operation, zero restarts
   - Ready to move from shadow to OPERATIONAL status

5. **Shadow data collection** (this document companion: `SHADOW_DATA_COLLECTION_WAVE66.md`)

### Primal Service Matrix (golgiBody, June 1)

| Service | Status | Running Since | Days |
|---|---|---|---|
| hbbs-membrane (RustDesk) | active | May 15 | 17d |
| hbbr-membrane (RustDesk) | active | May 15 | 17d |
| beardog-tls-shadow (S1) | active | May 19 | **13d** |
| petaltongue-web | active | May 19 | 13d |
| beardog-membrane | active | May 28 | 4d |
| skunkbat-membrane | active | May 28 | 4d |
| songbird-relay (TURN) | active | May 28 | 4d |
| coralreef-membrane | active | May 28 | 4d |
| toadstool-membrane | active | May 28 | 4d |
| barracuda-membrane | active | May 28 | 4d |
| loamspine-membrane | active | May 28 | 4d |
| nestgate-membrane | active | May 28 | 4d |
| rhizocrypt-membrane | active | May 28 | 4d |
| sweetgrass-membrane | active | May 28 | 4d |
| biomeos-membrane | active | May 28 | 4d |
| petaltongue-membrane | active | May 28 | 4d |
| squirrel-membrane | active | May 28 | 4d |
| caddy-tls | active | May 28 | 4d |
| songbird-membrane | active | May 29 | 3d |
| forgejo | active | May 31 | 1d |

**20/20 active. Zero crashes since May 28 deployment cycle.**

---

## Bash → Rust Evolution Summary

### membrane-shadow Modules

| Module | Lines | Domain | Wave |
|---|---|---|---|
| `dispatch.rs` | 709 | Command routing | 62 |
| `temporal.rs` | 638 | WaterFall sync engine | 63 |
| `impulse.rs` | 712 | Impulse/potential coordination | 63 |
| `relay.rs` | ~400 | K-Derm diderm relay chain | 65 |
| `context.rs` | 464 | Context braid weaving | 64 |
| `plasmid.rs` | 423 | Binary artifact fetching | 63 |
| `cli.rs` | 176 | Argument parsing | 62 |
| `main.rs` | 129 | Thin entry point | 62 |
| `git_ops.rs` | 94 | Shared git operations | 63 |
| Others | ~600 | forgejo, gate, config, manifest, identity | 62-64 |

### nucleus-deploy Subcommands (ironGate delivery)

| Subcommand | Status | Replaces |
|---|---|---|
| `nucleus security` | Complete | security_validation.sh |
| `nucleus provenance` | Complete | provenance checks |
| `nucleus deploy` | Complete | deploy.sh |
| `nucleus spore` | Complete | spore generation |
| `nucleus telemetry` | Complete | telemetry collection |
| `nucleus summary` | Complete | membrane_summary.sh |
| `nucleus verify` | Complete | verification scripts |
| `nucleus provision` | Complete | gate_provision.sh |
| `nucleus dns` | Complete | DNS management |

### Remaining Bash on VPS (peptidoglycan)

These are deployed copies that remain running until Rust relay is deployed:

| Script | Lines | Rust Replacement | Deploy Status |
|---|---|---|---|
| `pepti-sync-relay.sh` | 95 | `membrane relay.mediate` | VPS still uses bash |
| `ext-github-push.sh` | 91 | `membrane relay.ship` | VPS still uses bash |
| `impulse-relay-hook.sh` | 52 | `membrane impulse.post` | VPS still uses bash |
| `setup-push-mirrors.sh` | 111 | manifest-driven | VPS still uses bash |

---

## Known Issues

### Tower Atomic — Songbird Security Provider Socket

Songbird's outbound TLS client (`songbird_http_client::connection::https`) looks for
`/tmp/neural-api-*.sock` instead of using the configured `--security-socket /run/membrane/beardog.sock`.
The beardog socket exists and is healthy. The songbird server code path correctly uses it.
The outbound client code path has a hardcoded neural API socket pattern.

**Fix needed**: `songbird_http_client` must read the security socket from the same
`--security-socket` flag used by the server, or from `BEARDOG_SOCKET` env var.

**Impact**: Cross-gate federation TLS handshakes fail. TURN relay still works.

### biomeOS capability.call Not Implemented

The `capability.call` JSON-RPC method returns `-32601 Method not found`. This blocks
cross-gate capability routing through biomeOS.

**Fix needed**: Implement `capability.call` in biomeOS API server.

### golgiBody Disk Pressure

68% used (6.3G/9.7G). The 20-service primal stack and Forgejo fit but leaves
limited headroom. Consider moving build artifacts to peptidoglycan (9% used, 79G).

---

## Remaining Evolution Work

### HIGH — Blocks Glacial Shift

| Item | Owner | Status |
|---|---|---|
| S1 → OPERATIONAL graduation | cellMembrane | 13d passed, ready to declare |
| DNS NS registrar cutover | Manual (eastGate) | Waiting on registrar login |
| Songbird security socket fix | cellMembrane/ironGate | Code fix in songbird_http_client |
| biomeOS capability.call | cellMembrane/ironGate | New RPC method |
| VPS relay Rust deployment | cellMembrane | Deploy relay.rs to peptidoglycan |

### MEDIUM — Strengthens Sovereignty

| Item | Owner | Notes |
|---|---|---|
| S4 formal 7-day gate | ironGate | Needs beardog auth service config |
| Transport quorum Phase 1 | cellMembrane | Timer-based potential.sense on VPS |
| Forgejo Actions CI | projectNUCLEUS | Self-hosted runner |
| Family seed deployment | cellMembrane | Replace development mode on golgiBody |
| golgiBody-ext HTTPS | cellMembrane | Blocked on DNS cutover |
| Cross-subnet routing | infra/network | southGate needs TURN |
| strandGate/northGate deploy | ops | Hardware ready |

### LOW — Enhancements

| Item | Owner | Notes |
|---|---|---|
| Caddy → BearDog ACME | cellMembrane | Caddy works fine |
| BearDog Vault (encrypted creds) | bearDog | Phase 2 |
| golgiBody disk cleanup | ops | Move artifacts to peptidoglycan |
| pseudoSpore delta coverage | springs | 2/7 have spores |
| Songbird test coverage 73→90% | songBird | Incremental |

---

## Concept Evolution (gen4 → gen5)

| gen4 Document | gen5 Document | What Changed |
|---|---|---|
| `K_DERM_RECONCILIATION.md` | `KDERM_DIDERM_ENVELOPE.md` | Naming → physical deployment |
| `SOVEREIGNTY_EVOLUTION_NARRATIVE.md` | `SOVEREIGNTY_SHADOW_EVOLUTION.md` | Narrative → operational S1-S4 |
| (no precedent) | `TRANSPORT_EVOLUTION.md` | Nanowire → quorum sensing |
| (no precedent) | `IMPULSE_POTENTIAL_COORDINATION.md` | Neural API triad + provenance trio |
| (existed) | `CONTEXT_BRAID_PATTERN.md` | sweetGrass external analog |
| (existed) | `EXTERNAL_SOVEREIGNTY_PATTERN.md` | Collaborator gate routing |

---

## Context Braids (Active)

| Gate | Project | Summary |
|---|---|---|
| ironGate | projectNUCLEUS | Wave 64 deep debt COMPLETE — 235 tests, 9 subcommands |
| flockGate | wateringHole | K-Derm diderm relay validated |
| flockGate | cellMembrane | K-NOME hook live — auto context injection |
| eastGate | cellMembrane | impulsePotential + context braid three-layer model |

---

## Next Wave Priorities

### Wave 66 (Current) — Shadow Validation Sprint
1. Graduate S1 TLS from shadow to OPERATIONAL
2. wateringHole zero-code cleanup — **DONE**
3. Shadow data collection — **DONE**
4. Fire impulse for songbird socket fix
5. DNS registrar NS cutover (manual)

### Wave 67 — Mesh Connectivity
1. Songbird security socket fix (code)
2. biomeOS capability.call implementation
3. Cross-gate discovery.peers smoke test
4. Deploy Rust relay to peptidoglycan VPS

### Wave 68 — Quorum Phase 1
1. Timer-based potential.sense on VPS nodes
2. S4 formal 7-day gate (if ironGate configured)
3. Family seed deployment to golgiBody

### Wave 69+ — Expansion
1. strandGate deployment
2. northGate deployment
3. Multi-vendor peptidoglycan
4. Forgejo Actions CI

---

*The ecosystem is in the validation phase. Infrastructure is built, 20 services
are running, S1 TLS is proven. The remaining work is mesh connectivity
(songbird socket fix + capability.call), DNS cutover, and VPS relay deployment.*
