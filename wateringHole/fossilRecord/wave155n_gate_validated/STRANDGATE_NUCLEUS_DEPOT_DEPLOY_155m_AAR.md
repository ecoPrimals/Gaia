# AAR — strandGate NUCLEUS Depot Deploy — Wave 155m

**Gate**: strandGate  
**Wave**: 155m  
**Date**: 2026-07-31  
**Operator**: strandGate overwatch (Cursor agent)

---

## Summary

Pure depot deploy of all 13 primals + biomeOS from `depot.primals.eco`.
biomeOS depot binary now includes commit `999044e7` (user-space binary discovery fix).
NUCLEUS lifecycle-managed via `biomeos nucleus start`.

**Result: 11/12 healthy — best NUCLEUS composition achieved on strandGate.**

---

## Deploy Method

```
Source: depot.primals.eco/primals/
  musl:  biomeos beardog songbird skunkbat nestgate loamspine sweetgrass rhizocrypt squirrel petaltongue
  gnu:   barracuda coralreef toadstool
Target: ~/.local/bin/
Launch: biomeos nucleus start --node-id strandGate --mode full --log-level info
```

---

## Results

### Health — 11/12

| Primal      | Version | Status      | Protocol | Latency |
|-------------|---------|-------------|----------|---------|
| bearDog     | 0.9.0   | healthy     | json     | 0.4ms   |
| songBird    | —       | RESPAWN LOOP| —        | —       |
| skunkBat    | 0.2.18  | Healthy     | json     | 0.5ms   |
| nestGate    | 0.5.0   | healthy     | json     | 0.3ms   |
| loamSpine   | ?       | Healthy     | json     | 0.3ms   |
| sweetGrass  | 0.8.0   | healthy     | ribo     | 0.2ms   |
| rhizoCrypt  | ?       | True        | json     | 0.5ms   |
| barraCuda   | 0.4.0   | healthy     | json     | 0.4ms   |
| coralReef   | 0.2.0   | operational | json     | 0.2ms   |
| toadStool   | 0.2.0   | alive       | ribo     | 0.2ms   |
| petalTongue | 1.6.6   | healthy     | json     | 0.3ms   |
| squirrel    | 0.1.0   | alive       | json     | 0.4ms   |

### Capabilities — 912 methods

bearDog(216) skunkBat(30) nestGate(78) loamSpine(50) sweetGrass(40) rhizoCrypt(38) barraCuda(98) coralReef(18) toadStool(249) petalTongue(56) squirrel(39)

### GPU Compute

- Device: NVIDIA GeForce RTX 3090 (Vulkan)
- matmul 256×256 (20 rounds): p50=0.26ms, p99=88.60ms

### Crypto

- bearDog `crypto.sign_ed25519`: OK (Ed25519, key_id=default_signing_key)

### IPC Latency (50-round health.check)

| Primal    | p50     | p99     |
|-----------|---------|---------|
| bearDog   | 0.065ms | 0.127ms |
| barraCuda | 0.088ms | 0.146ms |
| nestGate  | 0.118ms | 0.231ms |
| loamSpine | 0.118ms | 0.213ms |
| coralReef | 0.088ms | 0.200ms |

### Sockets

- Filesystem: 27 sockets in `/run/user/1000/membrane/`
- Kernel: 18 listening
- Family ID: `e8b62b6e`

---

## Key Fix Validated: Binary Path Retention (999044e7)

Previous depot deploys (Wave 155k) failed because biomeOS searched `./plasmidBin/primals/`
for binaries during respawn, ignoring `~/.local/bin/` user-space deployments.

With `999044e7` in the depot binary, biomeOS now correctly discovers:
```
beardog    -> /home/strandgate/.local/bin/beardog
skunkbat   -> /home/strandgate/.local/bin/skunkbat
toadstool  -> /home/strandgate/.local/bin/toadstool
coralreef  -> /home/strandgate/.local/bin/coralreef
squirrel   -> /home/strandgate/.local/bin/squirrel
petaltongue -> /home/strandgate/.local/bin/petaltongue
loamspine  -> /home/strandgate/.local/bin/loamspine
songbird   -> /home/strandgate/.local/bin/songbird
nestgate   -> /home/strandgate/.local/bin/nestgate
rhizocrypt -> /home/strandgate/.local/bin/rhizocrypt
```

Respawn from binary works correctly — the `999044e7` user-space discovery fix is validated.

---

## Remaining P2: songBird Respawn Loop

songBird transitions to ACTIVE after launch, but biomeOS's RPC health ping fails
(riboCipher framing mismatch — songBird responds on a different protocol than biomeOS expects).
After 3 failed pings → DEGRADED → resurrect → respawn → socket not found → loop.

This is a known P2 from Wave 155i. songBird's depot binary needs its health endpoint
to respond to biomeOS's RPC ping format, or biomeOS needs a per-primal ping protocol config.

**Severity**: P2 — non-blocking, songBird functionality available between respawn cycles  
**Owner**: eastGate

---

## Delta from Previous Deploy (155k AAR)

| Metric                   | 155k       | 155m       |
|--------------------------|------------|------------|
| Healthy                  | 7/12       | 11/12      |
| Methods                  | ~780       | 912        |
| Binary path discovery    | BROKEN     | FIXED      |
| Socket evaporation       | Widespread | songBird only |
| Respawn from binary      | Failed     | Working    |
| GPU compute              | Working    | Working    |

---

## Recommendations for eastGate

1. **P2 songBird ping**: Add riboCipher health ping support to songBird, or add per-primal protocol config to biomeOS supervisor
2. **Provenance 7/7**: With crypto.sign working and NUCLEUS stable, full provenance chain validation is unblocked
3. **biomeOS v4.51**: blurb mentions v4.51 on sporeGate — when depot catches up, songBird may be fixed

---

*Filed by strandGate overwatch — Wave 155m — 2026-07-31*
