# Songbird Wave 202 — VPS Relay Ops Deployment Readiness

**Date**: May 12, 2026  
**Primal**: Songbird v0.2.1  
**Wave**: 202  
**From**: Songbird team  
**For**: projectNUCLEUS (NAT shadow run), all primal teams

---

## Summary

Wave 202 delivers everything projectNUCLEUS needs to deploy the sovereign TURN
relay on a VPS and run the NAT shadow (replacing `cloudflared`). This is the
final Songbird deliverable for interstadial exit.

---

## What's Deployable Now

### `songbird relay` CLI

```bash
songbird relay                                    # 0.0.0.0:3478, open mode
songbird relay --credentials-file /etc/songbird/relay-credentials
songbird relay --port 4000 --bind 10.0.0.1        # custom bind
```

### Credential Loading

Production credentials loaded from:
1. `--credentials-file PATH` (or `SONGBIRD_RELAY_CREDENTIALS_FILE` env)
2. `SONGBIRD_RELAY_CREDENTIALS` env var (inline, newline-separated)

Format: `username:hex_key` per line (beacon-tier HMAC material from BearDog).

### systemd Service Unit

`deployment/systemd/songbird-relay.service` — security-hardened, ready to copy:
- `PrivateTmp`, `NoNewPrivileges`, `ProtectSystem=strict`
- `CAP_NET_BIND_SERVICE` for port 3478
- Auto-restart on failure
- Reads credentials from `/etc/songbird/relay-credentials`

### Full Deployment Guide

`deployment/relay/README.md` covers:
- 5-minute quick deploy (scp + systemctl)
- Credential provisioning (BearDog keys + manual)
- Firewall rules (UFW, iptables, nftables)
- Monitoring and log queries
- projectNUCLEUS NAT shadow run environment variables

---

## projectNUCLEUS: How to Run the NAT Shadow

1. Deploy `songbird relay` on VPS (follow `deployment/relay/README.md`)
2. Configure clients:
   ```bash
   export SONGBIRD_TURN_SERVER=<vps-ip>:3478
   export SONGBIRD_TURN_USERNAME=nucleus-relay
   export SONGBIRD_TURN_KEY=<hex_key>
   ```
3. The `ConnectionFallbackChain` Tier 4 automatically allocates through the relay
4. Validate: two clients behind NAT can exchange data through the relay
5. Confirm: the chain Songbird VPS relay → NAT shadow → NestGate extracellular works

---

## Pass 12 — COMPLETE

| Component | Status |
|-----------|--------|
| STUN wire-compliant (RFC 5389) | Shipped (Wave 196) |
| TURN client (RFC 5766) | Shipped (Wave 197) |
| Cloudflare DDNS | Shipped (Wave 197) |
| 5-tier ConnectionFallbackChain | Shipped (Wave 197) |
| TurnRelayServer (836L) | Shipped (Wave 199) |
| Bidirectional data plane | Shipped (Wave 201) |
| `songbird relay` CLI | Shipped (Wave 201) |
| Credential loading (file/env) | Shipped (Wave 202) |
| systemd service unit | Shipped (Wave 202) |
| VPS deployment guide | Shipped (Wave 202) |

**Songbird VPS relay is ops-ready. projectNUCLEUS can deploy immediately.**

---

## Songbird — CLEAR Through Stadial Gate

Per the primalSpring Ecosystem Wave Sync (May 12, 2026):

> "Songbird and coralReef sentinel items are the only upstream blockers to
> interstadial exit."

**Update**: coralReef sentinel is also **RESOLVED** (Sprint 7 — FECS stability proof shipped).

With Wave 202, Songbird's sentinel item is **fully resolved**:
- Code: complete (TURN server + bidirectional relay + CLI)
- Ops: complete (systemd + credentials + firewall + deployment guide)
- Documentation: complete (env vars + deployment README)

The ball is now with **projectNUCLEUS** to deploy and validate the shadow run.
