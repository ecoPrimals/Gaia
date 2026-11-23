# cellMembrane — Wave 116 Gate Enrollment Status

> **SUPERSEDED** by `EASTGATE_ENROLLMENT_COMPLETE_WAVE116_JUN18.md` and
> `CELLMEMBRANE_WAVE118_DEEP_DEBT_JUN19_2026.md`. SSH blocker resolved, eastGate enrolled.

**Date:** 2026-06-18
**From:** cellMembrane team (ironGate / sporeGate)
**To:** eastGate overwatch, primalSpring coordination
**Context:** Wave 116 gate enrollment pipeline — sporeGate reference, eastGate first target

---

## Current State

### sporeGate (reference enrolled gate)

| Check | Status |
|-------|--------|
| membrane binary | **FRESH** — rebuilt from `11a7c68` (Jun 18), installed to `~/.local/bin/membrane` |
| 495 tests | **ALL PASS** — workspace (types + shadow), zero clippy |
| sovereignty.s1_tls | OPERATIONAL — `membrane.primals.eco` 200 OK |
| sovereignty.s2_relay | REACHABLE — federation + TURN |
| sovereignty.s3_content | OPERATIONAL — depot serving |
| sovereignty.s4_auth | DEGRADED (expected — local gate, no BearDog UDS) |
| WireGuard | Active — `10.13.37.2` → golgi, pepti |
| cascade | Active — 17 repos from sovereign Forgejo |

### Tooling Ready

| Command | Status | Notes |
|---------|--------|-------|
| `membrane gate.preflight` | WORKING | 6 checks, detected all local interfaces |
| `membrane gate.bootstrap <gate> [--dry-run]` | WORKING | 13-phase pipeline, dry-run verified for eastGate (11/12 pass) |
| `membrane gate.status` | WORKING | Rich local probe with sovereignty checks |
| `membrane gate.health` | WORKING | Remote VPS systemd sweep |
| `membrane firewall.generate --plasma-membrane` | WORKING | Full nftables ruleset generated for eastGate (nucleus composition) |
| `membrane health.audit` | WORKING | Depot version skew |
| `membrane gate.profile <gate>` | WORKING | Manifest lookup |

---

## eastGate Enrollment — Blocker

### SSH key authorization required

```
sporeGate (192.168.4.237) → eastGate (192.168.4.244): Permission denied (publickey,password)
```

**sporeGate public key (needs to be added to `eastgate@192.168.4.244:~/.ssh/authorized_keys`):**

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAmsIkp8xEipnbwNIjGs0uVN+R92ItAgku4zayInAE3p irongate@pop-os
```

**How to authorize (operator action via physical access or RustDesk):**

```bash
# On eastGate:
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAmsIkp8xEipnbwNIjGs0uVN+R92ItAgku4zayInAE3p irongate@pop-os' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### Once SSH is authorized, enrollment sequence:

```bash
# 1. Pre-flight scan
ssh eastgate@192.168.4.244 "sudo apt install -y curl"
# Copy membrane binary to eastGate
scp ~/.local/bin/membrane eastgate@192.168.4.244:/tmp/membrane
ssh eastgate@192.168.4.244 "sudo mv /tmp/membrane /usr/local/bin/ && sudo chmod +x /usr/local/bin/membrane"

# 2. Run preflight on eastGate
ssh eastgate@192.168.4.244 "membrane gate.preflight"

# 3. Generate and apply firewall (review interfaces from preflight first!)
membrane firewall.generate --plasma-membrane --composition nucleus \
  --wan <WAN_IFACE> --lan <LAN_IFACE> --subnet 192.168.4.0/22 \
  --gate-name eastGate --wg-iface wg0 --wg-port 51820 --format nftables \
  | ssh eastgate@192.168.4.244 "sudo tee /etc/nftables.conf"
ssh eastgate@192.168.4.244 "sudo nft -f /etc/nftables.conf"

# 4. Bootstrap (13 phases)
membrane gate.bootstrap eastGate --dry-run   # verify first
membrane gate.bootstrap eastGate             # execute

# 5. Verify
ssh eastgate@192.168.4.244 "membrane gate.status"

# 6. WireGuard peer (manual — assign 10.13.37.3)
# 7. Cascade connect
ssh eastgate@192.168.4.244 "membrane temporal.cascade"
```

---

## eastGate nftables (pre-generated, interface names TBD)

Generated via `membrane firewall.generate --plasma-membrane --composition nucleus`:

- WAN/LAN interfaces need verification from `gate.preflight` output
- WireGuard `wg0` on port 51820
- NUCLEUS composition ports: SSH, DNS, HTTP/HTTPS, TURN, NestGate, RustDesk
- NAT masquerade from LAN → WAN
- IPv6 forwarding blocked

---

## Pipeline Gaps Noted

| Gap | Severity | Detail |
|-----|----------|--------|
| No SSH enablement automation | P2 | Operator prerequisite — physical or RustDesk access |
| `preflight` not integrated into `bootstrap` | P2 | Must run separately; bootstrap won't check |
| No WireGuard peer config generation | P1 | `mesh.rs` is Songbird federation only; WG is separate infra |
| No cascade step in bootstrap | P2 | `temporal.cascade` must be run after bootstrap |
| membrane binary not in system PATH | P2 | Bootstrap installs to `/opt/membrane/`, needs `/usr/local/bin/` symlink |
| DHCP conflict check documented but not implemented | P3 | Preflight header claims it; `check_dhcp()` absent |

---

## What's Next After eastGate

1. **ironGate** — SSH enable (identify OS via RustDesk), then same pipeline
2. **flockGate** — WAN gate, WireGuard site-to-site via golgi
3. **Flint 2 WiFi swap** — physical operator action this weekend
4. **strandGate/southGate/swiftGate** — relay migration after Flint 2 live

---

*cellMembrane tooling is ready. Blocked on eastGate SSH key authorization (operator action).*
