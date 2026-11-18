<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# HANDOFF: esotericWebb V23–V26 Deep Debt — ironGate First Boot

- **Date**: 2026-08-03
- **Source**: esotericWebb (garden)
- **Gate**: ironGate (PRIMARY DOWNSTREAM HOST)
- **Wave**: 155p / 156b
- **Direction**: Outbound → upstream primals + infra teams

---

## Summary

esotericWebb completed a four-version deep debt pass (V23–V26) on ironGate
as the ecosystem's first live cell boot target. 8/9 primals compose with
zero configuration. All quality gates green: 455 tests, 0 clippy, 0 unsafe,
0 C deps, 0 files >800L.

## Upstream action items

### 1. toadStool: Fix systemd unit ExecStart (BLOCKING 9/9)

The membrane unit passes `--foreground` which toadStool v0.x rejects.
The `up` subcommand requires a `<MANIFEST>` argument.

**Fix**: Correct `/etc/systemd/system/membrane-nucleus@toadstool.service`
ExecStart to match toadStool's actual CLI: `toadstool up <manifest_path>`.

### 2. Membrane socket permissions

`/run/membrane/petaltongue.sock` is `root:root srwxr-xr-x`. Non-root
users cannot connect. Webb falls back to REST `:3001` successfully, but
the socket should be group-writable for `biomeos` group to enable UDS
composition without privilege escalation.

### 3. BTSP documentation

sweetGrass requires `0xEC 0x01` prefix (riboCipher transport signal) before
JSON-RPC over UDS. This is undocumented in the ecosystem blurb. Other
primals should declare their transport requirements in capability manifests.

## Patterns discovered (for ecosystem adoption)

| Pattern | Description |
|---------|-------------|
| REST health probe | Non-JSON-RPC primals expose `GET /health` → `{"status":"healthy"}` |
| BTSP fallback | Try plain UDS first; on `-32002` error, retry with `0xEC 0x01` prefix |
| Test file extraction | `#[path = "foo_tests.rs"] mod tests;` keeps production files lean |
| Env-based host | `{PRIMAL}_DEFAULT_HOST` env var replaces hardcoded `127.0.0.1` |
| Discovery priority | XDG user > membrane > env override > TCP well-known > HTTP REST |

## Full details

See `gardens/esotericWebb/wateringHole/handoffs/ESOTERICWEBB_V26_IRONGATE_DEEP_DEBT_AUG03_2026.md`
and `gardens/esotericWebb/AAR_WAVE155_DEEP_DEBT.md` for comprehensive posture.
