# wetSpring — Wave 55 southGate Deployment Issues

**Date**: 2026-05-26
**From**: wetSpring (southGate)
**To**: primalSpring coordination, primal teams
**Version**: V188

---

## Summary

Redeployed NUCLEUS on southGate with Wave 53 hardened binaries (v2026.05.27).
Songbird socket fix confirmed. loamSpine Tokio fix confirmed. NUCLEUS 8/13
health-responding. PG-02/PG-04 provenance trio verified (live IPC roundtrip).
All 22 wetSpring PG gaps resolved.

**5 primals not health-responding — upstream fixes needed for 13/13.**

---

## Deployment Issues for Upstream Absorption

### 1. petalTongue: binary rejects `--socket` flag

**Binary**: `infra/plasmidBin/petaltongue/petaltongue` (pre-v2026.05.27, not in release)
**Error**: `error: unexpected argument '--socket' found. Usage: petaltongue server`
**Impact**: petalTongue cannot participate in NUCLEUS composition on southGate
**Ask**: Ship petalTongue with `--socket <PATH>` CLI support in next plasmidBin release

### 2. barraCuda: process crashes after startup

**Binary**: `primals/x86_64-unknown-linux-musl/barracuda` (v2026.05.27)
**Behavior**: Starts, gets PID, then crashes before socket is ready. No error in stdout.
**Impact**: No GPU tensor compute via IPC on southGate
**Ask**: Investigate barraCuda startup crash on 5800X3D / RTX 4060+3090 hardware. May
need `RUST_BACKTRACE=1` or GPU driver version check.

### 3. Squirrel: socket not at expected name

**Binary**: `primals/x86_64-unknown-linux-musl/squirrel` (pre-v2026.05.27, not in release)
**Behavior**: Process running (`server --socket /run/user/1000/biomeos/squirrel-nucleus01.sock`)
but socket file not created at that path
**Impact**: No AI inference routing on southGate
**Ask**: Check if Squirrel requires Ollama running first (`http://localhost:11434` is down on
southGate) — may be blocking socket creation

### 4. ToadStool: socket exists, no health response

**Binary**: `primals/x86_64-unknown-linux-musl/toadstool` (v2026.05.27)
**Behavior**: Process running, socket at `toadstool-nucleus01.sock`, but `health.liveness`
returns empty response (not an error, just empty)
**Impact**: ToadStool appears alive but health probes fail — `nucleus_launcher.sh status`
shows SOCKET rather than ALIVE
**Ask**: Confirm ToadStool `health.liveness` is wired. May need `NODE_ID` or other env var.

### 5. skunkBat: socket not detected by launcher

**Binary**: `primals/x86_64-unknown-linux-musl/skunkbat` (v2026.05.27 — 3.2MB static)
**Behavior**: Not started by `nucleus_launcher.sh` — not in the launcher's primal list
**Impact**: Minor — skunkBat is auxiliary
**Ask**: Add skunkBat to `nucleus_launcher.sh` primal list if it should be in composition

### 6. fetch.sh bug: `RECENT_TAGS` unbound variable

**Script**: `infra/plasmidBin/fetch.sh` line 350
**Error**: `fetch.sh: line 350: RECENT_TAGS: unbound variable`
**Trigger**: When a primal's asset is not found in the latest release and the script
tries `${#RECENT_TAGS[@]}` — but RECENT_TAGS is a string, not an array
**Impact**: 4 primals (rhizocrypt, sweetgrass, petaltongue, squirrel) cannot be fetched
when not in the latest release. Must be downloaded manually or individually.
**Fix**: Change `${#RECENT_TAGS[@]}` to `$(echo "$RECENT_TAGS" | wc -l)` or declare
RECENT_TAGS as an array

### 7. New env var requirements (Wave 53 binaries)

The following environment variables are now required for successful NUCLEUS launch:
- `NODE_ID` or `BEARDOG_NODE_ID` — BearDog identity (was not needed before Wave 53)
- `NESTGATE_JWT_SECRET` — NestGate JWT (openssl rand -base64 48)
- `nucleus_launcher.sh` should set defaults for these if not provided

---

## What's Working

| Primal | Status | Socket |
|--------|--------|--------|
| biomeOS | ALIVE | neural-api-nucleus01.sock |
| BearDog | ALIVE | beardog-nucleus01.sock |
| Songbird | ALIVE | songbird-nucleus01.sock |
| coralReef | ALIVE | shader.sock |
| NestGate | ALIVE | nestgate-nucleus01.sock |
| loamSpine | ALIVE | loamspine-nucleus01.sock |
| sweetGrass | ALIVE | sweetgrass-nucleus01.sock |
| rhizoCrypt | ALIVE | permanence-nucleus01.sock |

**Provenance trio operational.** spine.create + braid.create IPC roundtrip confirmed.
Songbird TCP federation on *:7700. Mesh seeded with eastGate (192.168.1.144:7700).

---

## Gate Status

```
wetSpring Wave 55: NUCLEUS 8/13 on southGate, mesh seeded, PG-02/PG-04 verified, covalent ready
```
