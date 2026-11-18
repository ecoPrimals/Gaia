# AAR: RustDesk Relay + Hairpin NAT Fix

**Date**: 2026-06-16 21:00-21:53 EDT
**Gate**: eastGate overwatch + sporeGate
**Outcome**: RESOLVED — all LAN gates can now connect via sovereign RustDesk relay

---

## Problem

After switching all gates from public RustDesk relay (`rs-ny.rustdesk.com`) to
sovereign relay on golgi (`[RELAY_PUBLIC]`), northGate could reach sporeGate but
NOT eastGate via RustDesk ID code.

## Root Cause Chain

### Issue 1: RustDesk config revert

RustDesk GUI overwrites `~/.config/rustdesk/RustDesk2.toml` on startup from its
in-memory state. Writing the config file while the GUI is running has no effect —
the GUI saves its cached (old) config over the file on next write cycle.

**Fix**: Stop ALL RustDesk processes, write config, then start service. OR set
relay in the GUI settings directly (Network → ID/Relay Server).

### Issue 2: Duplicate RustDesk processes

Manually running `nohup rustdesk --service` while the systemd unit was active
created duplicate instances — both registering on different relays, causing icon
flashing and inconsistent connectivity.

**Fix**: `pkexec pkill -9 rustdesk && systemctl start rustdesk` — single instance.

### Issue 3: Hairpin NAT (the real blocker)

When two devices (eastGate + northGate) are behind the same NAT (sporeGate), the
RustDesk relay sees both coming from sporeGate's WAN IP. UDP hole-punching fails
because both endpoints have the same external address. The relay attempts to route
traffic back, but sporeGate's firewall:

1. Had no `eno1 → eno1` forwarding rule (LAN hairpin traffic dropped)
2. Had no LAN-facing masquerade (hairpin NAT)
3. Had the WAN→LAN return rule placed AFTER the `drop` rule (unreachable)

**Fix**: Rebuilt sporeGate's nftables forward chain with correct ordering:

```
ct state established,related accept     # return traffic always
eno1 → enp1s0 accept                    # LAN → internet
enp1s0 → eno1 established accept        # relay returns from WAN
eno1 → eno1 accept                      # LAN hairpin (same-NAT relay)
wg0 accept                              # WireGuard
counter drop                            # everything else
```

Added `oifname "eno1" masquerade` to NAT postrouting for hairpin source rewrite.

### Issue 4: golgi hbbs WorkingDirectory missing

RustDesk server (`hbbs`) on golgi had `WorkingDirectory=/opt/membrane/rustdesk/`
in its systemd unit, but that directory didn't exist. The key (`id_ed25519.pub`)
is generated in the working directory on first start. Since the dir was missing,
hbbs ran from `/` (deleted), never generated a key, and clients couldn't verify.

**Fix**: `mkdir -p /opt/membrane/rustdesk && systemctl restart hbbs-membrane`
Key auto-generated: `[RUSTDESK_KEY_PURGED]`

---

## Relay Key

```
[RUSTDESK_KEY_PURGED]
```

Server: `[RELAY_PUBLIC]` (golgi)
Ports: 21115 (NAT test), 21116 (rendezvous), 21117 (relay)

---

## Deployment Status

| Gate | Relay Config | Status |
|------|-------------|--------|
| sporeGate | ✅ Sovereign | Working |
| eastGate | ✅ Sovereign | Working (after hairpin fix) |
| northGate | ✅ Sovereign | Working |
| fieldGate | ❌ Not configured | Offline (no route to host) |
| golgi (server) | N/A (IS the relay) | hbbs+hbbr ACTIVE |

---

## Lessons for cellMembrane/sporeGate Team

1. **RustDesk config is GUI-authoritative** — never write file while GUI runs.
   Future: `membrane remote.configure` command should stop service first.

2. **Hairpin NAT is required** for any relay-based system where peers share NAT.
   This affects RustDesk, WireGuard relay mode, and any future mesh relay.
   The `eno1 → eno1 accept` + LAN masquerade pattern must be in default nftables.

3. **Working directory matters for hbbs** — key generation is location-dependent.
   If dir doesn't exist, hbbs silently fails to generate keys.

4. **Update deployment kit**: The USB nftables.conf must include hairpin rules
   from day one. Add to SPOREGATE_ACTIVATION_BLURB.md.

---

## Recommendations

- [ ] Add hairpin NAT to default nftables template in USB kit
- [ ] `membrane remote.configure --relay golgiBody` command (auto-fetch key, stop/write/start)
- [ ] Document: "all gates on same relay" requirement in NETWORK_SOVEREIGNTY.md
- [ ] fieldGate: deploy relay config when reachable
- [ ] Consider: run hbbs on sporeGate as well (LAN-local relay for zero-WAN-latency LAN connections)
