# AAR: westGate Tower Atomic Deployment — Wave 155f

**Date**: Jul 28, 2026 13:12 EDT | **Wave**: 155f | **Gate**: westGate
**From**: westGate hardware/overwatch team
**Type**: After-Action Report — Tower Atomic live deployment

---

## Summary

westGate Tower Atomic is **LIVE**. Three primals (bearDog, songBird, skunkBat)
deployed from golgiBody depot genomeBins, running as systemd user units with
auto-restart and linger persistence. Health verified via JSON-RPC over UDS.
Federation port :7700 live — mesh-visible.

Gate went from dead checkout → synced working node → live Tower Atomic in a
single session (~70 minutes).

---

## Deployment Timeline

| Time (EDT) | Action |
|------------|--------|
| 12:05 | Session start — first blurb paste (WireGuard-first, blocked) |
| 12:29 | Updated blurb (Forgejo-is-public correction) |
| 12:37 | HTTPS public pull discovery — unblocked |
| 12:38 | 41 repos synced to Wave 155f (13 cloned, 27 fast-forwarded) |
| 12:42 | SSH key registered in Forgejo — push verified |
| 13:00 | Enrollment AAR pushed (hardware divergences documented) |
| 13:05 | Tower genomeBins fetched from depot (beardog 11MB, songbird 18MB, skunkbat 2.8MB) |
| 13:06 | Tower Atomic launched via `nucleus_launcher.sh --composition tower --uds-only` |
| 13:08 | socat installed, hostname set to `westgate` |
| 13:10 | Systemd user units installed, linger enabled |
| 13:11 | Tower Atomic live under systemd — all 3 healthy |

---

## Tower Atomic Status

| Primal | Version | Health | systemd Unit | Socket |
|--------|---------|--------|--------------|--------|
| bearDog | 0.9.0 | **healthy** | `beardog-tower.service` (active) | `beardog-westgate-tower-155f.sock` |
| songBird | 0.2.1 | **healthy** | `songbird-tower.service` (active) | `songbird-westgate-tower-155f.sock` |
| skunkBat | 0.2.18 | **Healthy** | `skunkbat-tower.service` (active) | `skunkbat-westgate-tower-155f.sock` |

### Transport

| Surface | Binding | Purpose |
|---------|---------|---------|
| UDS (11 sockets) | `/run/user/1000/biomeos/*.sock` | Inter-primal IPC |
| TCP :7700 | `0.0.0.0:7700` | songBird federation |

### Capability Symlinks

```
btsp.sock     → beardog-westgate-tower-155f.sock
crypto.sock   → beardog-westgate-tower-155f.sock
ed25519.sock  → beardog-westgate-tower-155f.sock
x25519.sock   → beardog-westgate-tower-155f.sock
security.sock → skunkbat-westgate-tower-155f.sock
network-*.sock → songbird-westgate-tower-155f.sock
```

### Persistence

- Systemd user units in `~/.config/systemd/user/`
- Linger enabled (`loginctl enable-linger westgate`)
- Auto-restart on failure (`Restart=always`, `RestartSec=5`)
- Environment from `~/.config/systemd/user/tower.env`
- Survives logout; starts on boot

---

## Issues and Divergences

### I1: First Blurb Assumed WireGuard Required for Sync (RESOLVED)

The initial startup blurb (pasted 12:05) implied WireGuard was prerequisite
for all operations. Agent concluded gate was blocked. Updated blurb (12:29)
correctly stated Forgejo is public — no WireGuard for sync.

**Further improvement**: The updated blurb still only documents SSH clone URLs.
We actually unblocked by switching to HTTPS (`https://git.primals.eco/<org>/<repo>.git`)
since the SSH key wasn't yet registered. A note about HTTPS fallback for
unauthenticated pull would make any fresh gate fully autonomous on first paste.

### I2: SSH Key Not Pre-Registered (RESOLVED)

The gate's existing SSH key (`id_ed25519_ecoPrimal`, created Jan 2026) was
registered on GitHub but not Forgejo. Required human intervention to register.
HTTPS public pull was the workaround.

**Suggestion**: The startup blurb's Phase 0 should mention HTTPS as the
zero-auth fallback path for initial sync, with SSH setup for push only.

### I3: Hardware Divergence — CPU is AMD, Not Intel (DOCUMENTED)

| Documented | Actual |
|------------|--------|
| Intel i7-4771 (Haswell, 4c/8t) | **AMD Ryzen 7 5700X** (Zen 3, 8c/16t, 32MB L3) |
| Not documented | **64GB DDR4 RAM** |
| "NVMe if present" | **Samsung 970 EVO Plus 2TB** (1.1TB free) |
| "5x14TB HDD (ZFS)" | 5×14TB HDD **raw/unmounted** (no ZFS pool) |
| "2.5" SSD available" | **No SATA SSD present** |

**Impact on tiering model**:
- TIER 0 (AMD cache): **APPLICABLE** — Zen 3 has 32MB unified L3
- TIER 1 (RAM): **64GB available** — substantial cache capacity
- TIER 2 (NVMe): **2TB Samsung 970 EVO Plus** — confirmed present
- TIER 3 (SSD): **ABSENT** — no SATA SSD
- TIER 4 (HDD): **RAW** — 5×14TB present but not pooled

Gate profiles and blurbs should be updated.

### I4: toadStool Was a Symlink, Not a Real Directory (RESOLVED)

`primals/toadStool` was a symlink to `primals/toadstool` (lowercase).
Removing the lowercase target during naming fixes created a dangling symlink.
Both removed, toadStool cloned fresh from Forgejo.

**Suggestion**: Step 1a in the blurb should handle symlinks:
`[ -L primals/toadStool ] && rm primals/toadStool` before clone.

### I5: songBird Didn't Start via nucleus_launcher.sh (RESOLVED)

On first launch, `nucleus_launcher.sh` started bearDog and skunkBat
successfully, but songBird silently failed (empty log, no process). Manual
launch with environment variables set explicitly succeeded.

**Root cause**: The launcher's `start_primal.sh` invocation for songBird
didn't pass the `BEARDOG_SOCKET` and `BEARDOG_MODE` environment variables.
The songBird `server` case in `start_primal.sh` checks for `$BEARDOG_SOCKET`
in the environment but the launcher doesn't export it before calling
`start_primal.sh` — the `EXTRA_FLAGS` block only fires if the socket file
exists at check time, which races with bearDog's startup.

**Fix suggestion** (for eastGate): In `nucleus_launcher.sh`, around line 300,
always export `BEARDOG_SOCKET` for songBird regardless of socket file existence:
```bash
if [[ "$p" == "songbird" ]]; then
    export BEARDOG_SOCKET="$SOCKET_DIR/beardog-${FAMILY_ID}.sock"
    export BEARDOG_MODE=direct
    export SONGBIRD_SECURITY_PROVIDER=beardog
    ...
fi
```

### I6: Legacy Federation Probes on :7700 (INFO)

Immediately after songBird started, it received federation connections from
two LAN hosts (`192.168.4.169` and `192.168.4.3`) without riboCipher signal
(0x47). These are pre-Wave 112 peers — likely other gates on the LAN segment
that auto-discover via federation port.

Not a problem — songBird correctly logged and rejected them. But it confirms
the peptidoglycan layer is active and westGate is mesh-visible.

### I7: ZFS Pool Not Created (DEFERRED)

The 5×14TB HDD array is raw/unmounted. ZFS pool creation requires human
decisions on topology (raidz1 vs raidz2 vs mirror) and is deferred to Nest
Atomic Phase 0 work.

### I8: Hostname Was `pop-os` (RESOLVED)

Changed to `westgate` via `hostnamectl set-hostname westgate`.

---

## Dev Loop Status

| Capability | Status | Method |
|------------|--------|--------|
| Pull from Forgejo | **WORKING** | HTTPS public (no auth) |
| Push to Forgejo | **WORKING** | SSH (`westGate-wave155f` key, `golgiAdmin`) |
| Tower Atomic running | **LIVE** | systemd user units, auto-restart, linger |
| Health monitoring | **WORKING** | JSON-RPC via socat over UDS |
| Federation | **LIVE** | songBird `:7700` — mesh-visible |
| Code team spin-up | **READY** | All 6 westGate primals synced |

The dev loop is closed. eastGate can:
1. Pull this AAR from Forgejo (`git pull` on wateringHole)
2. Verify westGate Tower health remotely (federation :7700 or SSH probe)
3. Spin up code teams on westGate for the assigned primals

---

## Recommendations for eastGate

1. **Update gate hardware profile**: westGate is AMD Ryzen 7 5700X / 64GB / 2TB NVMe / 5×14TB raw
2. **Fix `nucleus_launcher.sh`**: Export `BEARDOG_SOCKET` for songBird unconditionally (I5)
3. **Add HTTPS fallback to startup blurb**: `https://git.primals.eco/<org>/<repo>.git` for zero-auth initial sync
4. **Add symlink guard to Step 1a**: Handle `toadStool` symlink edge case
5. **Update `wave.toml` gate status**: westGate should move from `enrolling` to `online`

---

## Quick Reference — Managing Tower on westGate

```bash
# Status
systemctl --user status beardog-tower songbird-tower skunkbat-tower

# Health check (all three)
for p in beardog songbird skunkbat; do
  echo -n "$p: "
  echo '{"jsonrpc":"2.0","method":"health.check","params":{},"id":1}' | \
    socat - UNIX-CONNECT:/run/user/1000/biomeos/${p}-westgate-tower-155f.sock 2>/dev/null | \
    python3 -c "import sys,json; print(json.load(sys.stdin)['result']['status'])" 2>/dev/null || echo "UNREACHABLE"
done

# Restart
systemctl --user restart beardog-tower songbird-tower skunkbat-tower

# Logs
journalctl --user -u beardog-tower -f
journalctl --user -u songbird-tower -f
journalctl --user -u skunkbat-tower -f

# Stop
systemctl --user stop beardog-tower songbird-tower skunkbat-tower
```

---

*westGate Wave 155f: Tower Atomic LIVE. bearDog 0.9.0 + songBird 0.2.1 +
skunkBat 0.2.18 running as systemd user units with auto-restart and linger.
UDS IPC + federation :7700 mesh-visible. Dev loop closed: HTTPS pull, SSH push,
Tower health verified. 8 issues documented (5 resolved, 1 deferred, 2 info).
Gate ready for code team spin-up and Nest Atomic Phase 0 when Tower is proven stable.*
