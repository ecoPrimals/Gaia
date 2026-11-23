# sporeGate AAR — G65 Deployment Wave (Wave 156r)

**Date**: Aug 6, 2026 | **Gate**: sporeGate (eastGate overwatch)

---

## SUMMARY

Full depot rebuild and deployment of all 15 G65 primals. G65 protocol
negotiation now ships on every UDS socket across the mesh. sporeGate local
NUCLEUS deployed and verified. golgi depot updated with all 15 fresh binaries.
Gate teams can now deploy.

---

## COMPLETED

| # | Task | Result |
|---|------|--------|
| 1 | Pull all 15 primals to G65 HEADs | **15/15 verified** — all match blurb commits |
| 2 | Pull all 15 on blueGate | **15/15 verified** |
| 3 | Dispatch blueGate Windows builds | **RUNNING** (sequential, ~30 min for all 15) |
| 4 | sporeGate musl harvest (15) | **15/15 built** — 6 OK exit, 9 DIV-7 false failure |
| 5 | Manual build sourdough + bingoCube | **2/2** — harvest didn't catch these initially |
| 6 | Deploy to sporeGate NUCLEUS | **15/15 deployed**, 14 active + petalTongue user svc |
| 7 | petalTongue G65 health evolution | **12/13 alive** — see divergences below |
| 8 | Push depot to golgi | **15/15 musl binaries** pushed, all Aug 6 timestamps |
| 9 | petalTongue health fix committed | `6c47ae0` pushed to Forgejo |

---

## DIVERGENCES ENCOUNTERED

### DIV-1: G65 riboCipher Transport Signal Enforcement
Several G65 primals now REQUIRE riboCipher signal prefix (`0xEC 0x01`) or
explicit G65 `PROTOCOLS:` negotiation on their UDS sockets. Plain JSON-RPC
(`first_byte=0x7B` / `{`) is rejected with:
```
REJECTED: unsignalled connection (no riboCipher prefix)
```
**Affected**: sweetgrass, biomeos, beardog (main socket), skunkbat
**Resolution**: Updated petalTongue health module to try BTSP-framed query
first, fallback to plain JSON-RPC for primals that accept it (coralReef,
barracuda, etc.)

### DIV-2: beardog BTSP Handshake Requirement
beardog's main socket (`beardog.sock`) requires a full BTSP handshake
(`ClientHello`) beyond the simple `0xEC 0x01` signal prefix. Returns:
```
BEARDOG_UDS_REQUIRE_BTSP=1 — all connections must complete a BTSP handshake
```
**Resolution**: Use `beardog-default.sock` for plaintext health checks.

### DIV-3: skunkBat G65 Socket Relocation
G65 skunkBat creates its socket at `/run/user/0/biomeos/skunkbat-e8b62b6e.sock`
(root user runtime dir) with family-qualified naming. The old `security.sock`
symlink now points there. The systemd config's `--socket /run/membrane/skunkbat.sock`
path is NOT created by the G65 binary.
**Resolution**: Updated health module to use the family-qualified path.

### DIV-4: coralReef G65 Protocol Negotiation SUCCESS
coralReef now accepts plain JSON-RPC via G65 protocol negotiation. Previously
used tarpc-only protocol. `{"status":"alive"}` returned on plain JSON-RPC.
**Status**: RESOLVED — no BTSP prefix needed.

### DIV-5: toadStool Socket Permissions
Socket at `/run/membrane/toadstool.sock` has `srw-------` (root only).
The B1/B2 fix from biomeGate (group-connectable sockets) has not yet been
deployed to sporeGate.
**Status**: BLOCKED on toadStool binary with B1/B2 fix. Next deploy should fix.

### DIV-6: petalTongue "Text File Busy" During Binary Swap
Two petalTongue instances run: a root NUCLEUS service (`membrane-petaltongue`
on port 9900) and a user service (`petaltongue-web` on 10.13.37.2:8190). Both
must be stopped to release the binary for replacement.
**Resolution**: Stop both services before cp, then restart both.

### DIV-7: Harvest Exit Code Unreliability (RECURRING)
9/15 harvests returned non-zero exit codes but all 15 binaries were
successfully built. This is a known issue from the previous depot rebuild.
**Recommendation**: `plasmid.harvest --verify` feature remains needed.

---

## HEALTH STATUS POST-DEPLOY

| Primal | Status | Version | Socket Strategy |
|--------|--------|---------|-----------------|
| barracuda | ALIVE | - | Plain JSON-RPC |
| beardog | ALIVE | 0.9.0 | beardog-default.sock |
| biomeos | ALIVE | 4.56.0 | BTSP 0xEC 0x01 |
| coralreef | ALIVE | - | Plain JSON-RPC (G65!) |
| loamspine | ALIVE | - | BTSP fallback→plain |
| nestgate | ALIVE | - | BTSP fallback→plain |
| petaltongue | ALIVE | - | BTSP 0xEC 0x01 |
| rhizocrypt | ALIVE | 0.14.17 | BTSP fallback→plain |
| skunkbat | ALIVE | - | Family socket + BTSP |
| songbird | ALIVE | - | BTSP fallback→plain |
| squirrel | ALIVE | 0.1.0 | BTSP fallback→plain |
| sweetgrass | ALIVE | - | BTSP 0xEC 0x01 |
| toadstool | ERROR | - | Permission denied (B1/B2) |

---

## DEPOT STATUS

| Target | Binaries | Location |
|--------|----------|----------|
| x86_64-unknown-linux-musl | 15/15 | golgi `/opt/ecoPrimals/depot/primals/` |
| x86_64-pc-windows-gnu | building | blueGate (sequential) |

---

## GATE DEPLOYMENT READY

golgi depot has all 15 G65 musl binaries. Gate teams should:
1. Pull fresh binaries from golgi depot
2. Deploy to local NUCLEUS
3. Restart all membrane services
4. Verify health on nestgate.io dashboard

---

## NEXT

- blueGate: Finalize Windows build push to golgi
- toadStool: Deploy B1/B2 socket permission fix
- All gates: Deploy G65 binaries
- Springs + Science: Unblocked after deployment
