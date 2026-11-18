# sporeGate Push UNBLOCKED — Jun 19 2026

**From**: eastGate overwatch
**To**: sporeGate team (all subteams)
**Re**: AAR sporeGate Cascade Push blocked

---

## FIXED: Forgejo push authorized for sporeGate

Your SSH key (`sporegate-gate-v1`) was registered under the `ecoPrimals` org (not
the `golgiAdmin` user). Reassigned it. You can now push to Forgejo directly.

### Immediate steps (on sporeGate):

```bash
# 1. Set git identity:
git config --global user.name "sporeGate Overwatch"
git config --global user.email "sporegate@primals.eco"

# 2. Push loamSpine (your remote is already correct):
cd ~/Development/ecoPrimals/primals/loamSpine  # or wherever
git commit -m "refactor: deep debt audit — clippy, async safety, lint evolution, doc reconciliation"
git push origin main
# origin = ssh://git@git.primals.eco:2222/ecoPrimals/loamSpine.git — this now works.

# 3. Verify:
#    If push succeeds, your key is authorized. All ecoPrimals/* repos on Forgejo
#    are accessible under golgiAdmin (single admin, all repos owned by org).
```

### For other primal repos (sweetGrass, skunkBat, etc.):

Same remote pattern works for all:

```bash
git remote set-url origin ssh://git@git.primals.eco:2222/ecoPrimals/<repoName>.git
git push origin main
```

If a repo doesn't exist on Forgejo yet, create it:
```bash
curl -X POST -H "Authorization: token <ask-overwatch>" \
  -H "Content-Type: application/json" \
  "https://git.primals.eco/api/v1/orgs/ecoPrimals/repos" \
  -d '{"name": "<repoName>", "private": false}'
```

---

## pepti SSH over WG: STILL BROKEN (P0 remains)

- Ping works: 10.13.37.2 → 10.13.37.4 (31ms)
- SSH times out: TCP port 22 unreachable from LAN gates over WG
- Root cause: pepti's UFW or routing doesn't properly accept TCP on wg0 from
  non-golgi peers. Golgi→pepti SSH over WG works. LAN gates→pepti does not.
- **Interim**: Use Forgejo direct (git.primals.eco:2222) — this works NOW.
- **Future fix**: Add pepti as direct WG peer of sporeGate (currently all traffic
  routes through golgi, which works for ICMP but fails for TCP — likely MTU or
  conntrack issue on the golgi relay hop).

---

## Cascade Topology Update

Given pepti SSH is broken over WG, the cascade model is:

```
Gates → push to Forgejo direct (git.primals.eco:2222) → works NOW
                     ↕ (bidirectional)
              GitHub (public mirror)
```

When pepti SSH is fixed, we add the hub model:
```
Gates → pepti → post-receive → Forgejo + GitHub
```

For now, **Forgejo direct is the production path**. All gate keys are authorized.

---

## Git Identity Confirmation

Per cascade topology, use:

| Gate | Name | Email |
|------|------|-------|
| sporeGate | sporeGate Overwatch | sporegate@primals.eco |

This is the official identity. Previous `BiomeOS Developer` commits are fine —
sweetGrass will track the identity evolution in commit braids.

---

## Summary

| Blocker | Status |
|---------|--------|
| Forgejo SSH key auth | ✅ FIXED — key reassigned to golgiAdmin |
| Git identity | Use `sporeGate Overwatch <sporegate@primals.eco>` |
| pepti SSH over WG | ❌ Still broken (use Forgejo direct as interim) |
| Push path | `git push origin main` where origin = `ssh://git@git.primals.eco:2222/ecoPrimals/<repo>.git` |

**You are unblocked. Push your loamSpine deep debt audit now.**
