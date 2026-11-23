# southGate PostPrimordial Enrollment AAR

**Date**: Jul 31, 2026 12:40 EDT | **Wave**: 155n | **Gate**: southGate
**From**: southGate agent (agentic enrollment from golgiBody)
**Posture**: ENROLLED — repos converged, binaries deployed, NUCLEUS launch pending.

---

## SUMMARY

southGate completed postPrimordial enrollment at Wave 155n via agentic cascade.
Gate was offline since Wave 114 (Jun 16, 2026) — approximately 41 waves behind.
All steps self-serve except WireGuard peer add (requires golgiBody root).

**Result**: 32/33 repos at 155n HEAD. 16 sovereign depot binaries (biomeOS v4.55)
installed. Gate profile written. Ready for NUCLEUS launch.

---

## HARDWARE

| Component | Spec |
|-----------|------|
| CPU | AMD Ryzen 7 5800X3D (8c/16t, 3D V-Cache, 96MB L3) |
| GPU | NVIDIA GeForce RTX 4060 (8GB GDDR6, Ada Lovelace AD107) |
| RAM | 128 GB DDR4 |
| Boot Drive | 1TB Samsung 990 EVO Plus NVMe (479G free) |
| Work Drive | 4TB Samsung 990 EVO Plus NVMe (`/mnt/4tb-work`) |
| OS | Pop!_OS 22.04 LTS (kernel 6.17.9) |
| GPU Driver | NVIDIA 580.126.18 |
| Rust | 1.95.0 (2026-04-14) |
| Mesh IP | 10.13.37.9 (allocated) |

---

## ENROLLMENT SEQUENCE

### Step 1: WireGuard Mesh — PARTIAL

- WireGuard tools installed (`wireguard-tools 1.0.20210914`)
- Keypair generated: pubkey `vd3Y4Ts84It+/Goh5mQ++yuuSR1fOi271iQYKU5TkEg=`
- `/etc/wireguard/wg0.conf` not yet written (sudo required)
- Peer not yet added on golgiBody (requires root@[RELAY_PUBLIC])
- **Workaround**: Forgejo reachable via public DNS (`git.primals.eco`) — enrollment proceeded without mesh

**Human action needed**:
```bash
# On golgiBody:
wg set wg0 peer vd3Y4Ts84It+/Goh5mQ++yuuSR1fOi271iQYKU5TkEg= allowed-ips 10.13.37.9/32

# On southGate (sudo):
cat > /etc/wireguard/wg0.conf << EOF
[Interface]
PrivateKey = $(cat /etc/wireguard/privatekey)
Address = 10.13.37.9/24
DNS = 10.13.37.1

[Peer]
PublicKey = A2fvz3czkqRUuu2mzkSS6IVr/TCQcpsJX9HbDBa1FBc=
Endpoint = [RELAY_PUBLIC]:51820
AllowedIPs = 10.13.37.0/24
PersistentKeepalive = 25
EOF
wg-quick up wg0
```

### Step 2: SSH/Forgejo — DONE

- Existing SSH config already had Forgejo entry (`git.primals.eco:2222`)
- Authenticated as `golgiAdmin` with key named `southGate`
- All repos reachable via public internet route

### Step 3: Set Remotes — DONE (33 repos)

All repos repointed:
- `origin` → `ssh://git@git.primals.eco:2222/{org}/{repo}.git`
- `github` → `git@github.com-ecoPrimal:{org}/{repo}.git` (push mirror)

Org mapping verified:
- `primals/*` → `ecoPrimals/`
- `springs/*` → `syntheticChemistry/`
- `infra/*` → `ecoPrimals/`
- `gardens/*` → `sporeGarden/`

### Step 4: Pull and Converge — DONE (32/33)

All repos fast-forwarded from Wave 109-114 to Wave 155n HEAD.

Resolved during convergence:
- `infra/wateringHole`: force-pushed upstream → `git reset --hard origin/main`
- `gardens/blueFish`: empty local init → `git reset --hard origin/main`
- `gardens/foundation`: not on Forgejo (deprecated/unmirrored) — non-blocking

### Step 5: Deploy Binaries — DONE (16 from sovereign depot)

**Source**: `https://depot.primals.eco/primals/x86_64-unknown-linux-musl/`
**Method**: Direct HTTPS fetch from sovereign depot (served by sporeGate via golgiBody Caddy)

| Binary | Size | Status |
|--------|------|--------|
| barracuda | 12M | OK |
| beardog | 8.3M | OK |
| biomeos | 21M | OK |
| coralreef | 7.5M | OK |
| loamspine | 4.7M | OK |
| membrane | 16M | OK |
| nestgate | 8.5M | OK |
| nucleus_launcher | 4.2M | OK |
| petaltongue | 29M | OK |
| rhizocrypt | 7.5M | OK |
| skunkbat | 3.0M | OK |
| songbird | 19M | OK |
| sourdough | 3.0M | OK |
| squirrel | 4.4M | OK |
| sweetgrass | 8.2M | OK |
| toadstool | 13M | OK |

All verified as valid x86_64 ELF (statically linked musl).
Installed to `~/.local/bin/` (in PATH).
Confirmed: `biomeos --version` → `biomeos 4.55.0`

Depot provenance (from `depot.primals.eco/provenance.toml`):
- Builder: sporeGate
- Generated: 2026-07-31T15:07:31Z
- Toolchain: rustc 1.96.1 (31fca3adb 2026-06-26)

### Step 6: Gate Validation — PENDING

NUCLEUS not yet launched. Binaries in place. Boot order ready:
Tower (bearDog → songBird → skunkBat) → Nest (nestGate → rhizoCrypt → loamSpine → sweetGrass) → Node (toadStool → barraCuda → coralReef) → biomeOS + squirrel + petalTongue.

### Step 7: Announce — THIS FILE

Gate head published to `heads/southGate.toml`.
Gate profile written to `gardens/projectNUCLEUS/gates/southgate.toml`.

---

## TIMELINE

| Timestamp | Action |
|-----------|--------|
| Jul 26, 2026 20:50 EDT | Session 1: initial assessment, WG tools installed, keypair generated |
| Jul 26, 2026 20:52 EDT | Remotes repointed (33 repos → Forgejo-first) |
| Jul 26, 2026 20:53 EDT | First convergence: 33/33 repos at Wave 152a HEAD |
| Jul 31, 2026 12:36 EDT | Session 2: cascade to Wave 155n |
| Jul 31, 2026 12:37 EDT | Second convergence: 32/33 repos at Wave 155n HEAD |
| Jul 31, 2026 12:38 EDT | Binary fetch: 16 bins from depot.primals.eco → ~/.local/bin/ |
| Jul 31, 2026 12:40 EDT | Gate profile + head written, AAR authored |

---

## OBSERVATIONS

1. **Sovereign depot worked perfectly** — `depot.primals.eco` served all 16 binaries over HTTPS without issue. No GitHub fallback needed. This is the postPrimordial model working as designed.

2. **Forgejo via public DNS** bypassed the WireGuard chicken-and-egg problem. Gate could converge repos without mesh connectivity. WG can be established later.

3. **Agentic catch-up is viable** — 41-wave delta resolved in two short sessions. The combination of Forgejo-first remotes + sovereign depot + clear boot order makes self-serve enrollment tractable.

4. **Hardware is strong** — 5800X3D + RTX 4060 + 128GB + 4.5TB NVMe. This gate can run full NUCLEUS comfortably and serve as secondary compute for hotSpring/neuralSpring workloads.

---

## REMAINING WORK

| Priority | Item | Blocker |
|----------|------|---------|
| **P0** | Write wg0.conf + bring up mesh | sudo on southGate |
| **P0** | Add WG peer on golgiBody | root@[RELAY_PUBLIC] |
| **P1** | Launch NUCLEUS (13 primals, boot order) | After mesh OR standalone |
| **P1** | Gate validation (primalSpring probes) | After NUCLEUS stable |
| **P2** | NestGate CAS on 4TB work drive | After NUCLEUS validated |

---

*southGate postPrimordial enrollment COMPLETE at Wave 155n. 32/33 repos converged.
16 sovereign depot binaries (biomeOS v4.55) deployed. WireGuard pending sudo + golgi
peer add. NUCLEUS launch ready. Gate role: full NUCLEUS deployment (house2).*
