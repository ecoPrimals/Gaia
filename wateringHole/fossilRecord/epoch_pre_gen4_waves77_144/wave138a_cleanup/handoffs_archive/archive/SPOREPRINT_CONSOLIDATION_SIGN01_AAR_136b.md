# AAR — sporePrint Consolidation + SIGN-01 Activation Discovery (Wave 136b)

**Date**: Jul 11, 2026
**Gate**: sporeGate (primalSpring overwatch on eastGate)
**Operator**: agentic session
**Severity**: CRITICAL (DUAL-CHECKOUT) + HIGH (SIGN-01)

---

## Executive Summary

Resolved the CRITICAL P1 dual-checkout divergence on golgi and deployed
the updated membrane binary with `content.rebuild` path fix. Discovered
and documented three distinct blockers preventing SIGN-01 activation.
SIGN-01 fixes are **handed off to cellMembrane team** — all root causes
identified, tested, and documented below.

Also fixed two ecosystem manifest parse errors that were blocking
`cascade-sense` on golgi.

---

## 1. DUAL-CHECKOUT — RESOLVED (CRITICAL)

### Problem

golgi had two sporePrint checkouts:
- `/opt/ecoPrimals/sporePrint/` — Caddy serves from here
- `/opt/ecoPrimals/infra/sporePrint/` — rebuild hook was building here

Site was 30+ commits stale. See `SPOREPRINT_DUAL_CHECKOUT_AAR_136b.md`
for the original discovery.

### Actions Taken

1. **Removed orphan checkout**: `rm -rf /opt/ecoPrimals/infra/sporePrint`
2. **Fixed petaltongue-sporeprint.service**: Updated `ExecStart` and
   `WorkingDirectory` from `infra/sporePrint` to `sporePrint`
3. **Fixed SPOREPRINT_CONTENT_DIR constant** (cellMembrane `4ce165a`):
   - `cellmembrane-types/src/service/constants.rs`: `"infra/sporePrint"` → `"sporePrint"`
   - `content_dispatch.rs`: Added positional arg resolution (CLI `membrane content.rebuild /path` now works)
4. **Rebuilt and deployed membrane** to golgi
5. **Verified cascade-sense** runs `content.rebuild` successfully from both
   explicit path and default fallback

### Validation

```
membrane content.rebuild /opt/ecoPrimals/sporePrint  →  OK (6 output lines)
membrane content.rebuild                              →  OK (6 output lines)
cascade-sense.service                                 →  Finished successfully
```

Single checkout confirmed: `find /opt/ecoPrimals -path "*/sporePrint/public" -type d` returns one result.

---

## 2. ECOSYSTEM MANIFEST FIXES

### Problem

`cascade-sense` on golgi was failing to start after the wateringHole
checkout was refreshed. Two invalid enum values in `ecosystem_manifest.toml`:

```
line 833,854,869: bind_mode = "tcp"        # valid: auto, tcp_only, fallback, uds
line 868:         mobility = "portable"     # valid: fixed, mobile
```

### Actions Taken

- `bind_mode = "tcp"` → `"tcp_only"` (3 instances) — commit `3ecf873`
- `mobility = "portable"` → `"mobile"` (1 instance) — commit `2239504`

Also re-shallowed the wateringHole checkout on golgi (the old shallow
clone couldn't fetch properly — same known pattern from THIN-FORGEJO-RELAY).

### Validation

`cascade-sense` starts clean, syncs 17 repos, and triggers `content.rebuild`.

---

## 3. SITE-REBUILD-DEPLOY — RESOLVED (HIGH)

Rolled into the DUAL-CHECKOUT fix. The membrane binary (`4ce165a`)
deployed to `/usr/local/bin/membrane` on golgi. `content.rebuild` now
resolves the correct path in all invocation modes.

---

## 4. SIGN-01-ACTIVATE — DISCOVERY COMPLETE, HANDOFF TO cellMembrane

### Current State

bearDog ed25519 signing key generated on sporeGate:
- **Key ID**: `depot-signer`
- **Algorithm**: Ed25519
- **HSM**: BearDog Native Software HSM (Argon2id KDF)

bearDog server running on sporeGate at `/run/membrane/beardog.sock`.
Raw JSON-RPC signing **verified working**:

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"crypto.sign_ed25519","params":{"message":"dGVzdA==","key_id":"depot-signer","purpose":"depot"}}' \
  | sudo socat - UNIX-CONNECT:/run/membrane/beardog.sock
# → returns valid signature + public_key
```

### Three Blockers (cellMembrane team to fix)

#### BLOCKER 1: Wrong socket name

`signer_socket_name()` in both `signing.rs` and `sign_dispatch.rs` returns
`beardog-default.sock`. This is the **plaintext health socket** — it only
responds with alive heartbeats.

The actual IPC server listens on `beardog.sock` (no `-default` suffix).

**Fix**: Change `format!("{binary}-default.sock")` → `format!("{binary}.sock")`

Files:
- `membrane-shadow/src/plasmid/signing.rs` line 293
- `membrane-shadow/src/dispatch/sign_dispatch.rs` line 209

#### BLOCKER 2: riboCipher signal not expected by bearDog

`uds_sign_request()` in `signing.rs` prepends `CLEAR_JSONRPC_SIGNAL`
(`[0xEC, 0x01]`) before the JSON-RPC payload. bearDog's IPC server does
**not** expect this prefix — it causes `Parse error: expected value at
line 1 column 1`.

The riboCipher signal is a cellMembrane-to-cellMembrane convention.
bearDog accepts raw NDJSON on its IPC socket.

**Fix**: Remove the `stream.write_all(&crate::ribocipher::CLEAR_JSONRPC_SIGNAL)` line from `uds_sign_request()`.

File: `membrane-shadow/src/plasmid/signing.rs` line 311

#### BLOCKER 3: Socket permissions

bearDog server creates its socket as `root:root` with `srwxr-xr-x`.
When `membrane` runs as user `sporegate`, `connect()` returns
`Permission denied`.

Options:
- A) Run `membrane sign.activate` as root (quick fix)
- B) bearDog server sets socket permissions to `0o777` or `0o770` with
  group membership (proper fix)
- C) Configure bearDog's `--socket-mode` if available

#### BONUS: key_id mismatch

The code in `request_beardog_sign()` hardcodes `"key_id": "depot_signing_key"`.
The generated key is `"depot-signer"`. Either rename the key or update the code.

**Fix**: Change `"depot_signing_key"` → `"depot-signer"` in `signing.rs` line 272,
or generate the key with `--key-id depot_signing_key`.

### Verification Command (once fixes applied)

```bash
membrane sign.activate --depot /opt/ecoPrimals/depot
membrane sign.status --depot /opt/ecoPrimals/depot
membrane sign.verify --depot /opt/ecoPrimals/depot --policy require-signed
```

---

## 5. primalSpring Forgejo Shallow Issue

`git pull --rebase origin main` from Forgejo fails for primalSpring:

```
fatal: revision walk setup failed
error: ssh://git.primals.eco:2222/syntheticChemistry/primalSpring.git
  did not send all necessary objects
```

Same shallow-repo pattern as sporePrint. primalSpring is under
`syntheticChemistry/` org. Needs the same unshallow treatment:
`rm -f /opt/forgejo/data/repositories/syntheticchemistry/primalspring.git/shallow`

This is a known THIN-FORGEJO-RELAY pattern. Not urgent — primalSpring
can be pulled from GitHub mirror as a workaround.

---

## Commits This Session

| Repo | SHA | Description |
|------|-----|-------------|
| wateringHole | `3ecf873` | fix: bind_mode "tcp" → "tcp_only" (3 instances) |
| wateringHole | `2239504` | fix: mobility "portable" → "mobile" for swiftGate |
| cellMembrane | `4ce165a` | fix(content): DUAL-CHECKOUT — SPOREPRINT_CONTENT_DIR + positional args |

---

## Remaining Work

| ID | Status | Owner | Notes |
|----|--------|-------|-------|
| DUAL-CHECKOUT | **DONE** | sporeGate | Single checkout, cascade verified |
| SITE-REBUILD | **DONE** | sporeGate | membrane deployed, content.rebuild working |
| SIGN-01 | **HANDOFF** | cellMembrane | 3 blockers documented above. Key generated on sporeGate. |
| primalSpring | **KNOWN** | operator | Forgejo shallow repo needs unshallow |
| bearDog socket perms | **HANDOFF** | bearDog | IPC socket should be accessible to non-root |

---

*Wave 136b sporeGate session: 2 CRITICAL/HIGH items resolved (DUAL-CHECKOUT,
SITE-REBUILD). 2 manifest parse errors fixed. SIGN-01 root-caused to 3 specific
code locations — handed off to cellMembrane team. ecosystem cascade-sense fully
operational on golgi.*
