# NestGate UB-4 — sporePrint Pipeline: Investigation & Handback

**Date**: May 15, 2026  
**From**: NestGate (Session 62+)  
**To**: projectNUCLEUS team  
**Re**: UB-4 sporePrint pipeline wiring  

---

## Finding

NestGate's content backend is **complete** — all 8 `content.*` methods are routed
on every transport path (UDS, SemanticRouter, isomorphic IPC, HTTP API) since
Session 60. No NestGate code changes are needed.

The disconnect is in `projectNUCLEUS/deploy/publish_sporeprint.sh`, which has
**two RPC mismatches** against NestGate's actual API.

---

## Mismatch 1: `content.put` params

**Script sends** (line 81):
```json
{"method": "content.put", "params": {"path": "index.html", "data": "<base64>", "blake3": "abc123..."}}
```

**NestGate expects**:
```json
{"method": "content.put", "params": {"data": "<base64>"}}
```

NestGate computes the BLAKE3 hash internally and returns it in the response.
The `path` and `blake3` params are silently ignored (unknown fields).

**Fix**: Capture the returned `hash` from each `content.put` response to build
the manifest. Optional provenance fields are also available: `source`,
`pipeline`, `stored_by`, `content_type` (Session 62).

**Response shape**:
```json
{
  "hash": "abc123...",
  "size": 4096,
  "stored": true,
  "deduplicated": false,
  "content_type": "text/html",
  "family_id": "default"
}
```

## Mismatch 2: `collection.create` does not exist

**Script calls** (line 100):
```json
{"method": "collection.create", "params": {"name": "sporeprint", "version": "20260515", "manifest": "/tmp/..."}}
```

**NestGate exposes `content.publish`**:
```json
{"method": "content.publish", "params": {
  "collection": "sporeprint-20260515",
  "manifest": {
    "/index.html": "abc123...",
    "/about/index.html": "def456...",
    "/lab/compute-access/index.html": "789abc..."
  }
}}
```

The manifest is a **JSON object** mapping URL paths to BLAKE3 hashes (not a
local file path). All referenced hashes must already exist via `content.put`.

To alias "latest":
```json
{"method": "content.promote", "params": {
  "collection": "sporeprint-20260515",
  "alias": "sporeprint-latest"
}}
```

petalTongue resolves content via:
```json
{"method": "content.resolve", "params": {
  "collection": "sporeprint-latest",
  "path": "/index.html",
  "inline": true
}}
```

---

## Correct publish workflow

```bash
# 1. For each file: content.put → capture hash
HASH=$(echo '{"jsonrpc":"2.0","method":"content.put","params":{"data":"'$(base64 < file)'","content_type":"text/html","source":"sporePrint","pipeline":"publish_sporeprint"},"id":1}' \
  | nc -w 5 127.0.0.1 $NESTGATE_PORT | jq -r '.result.hash')

# 2. Build manifest JSON: { "/path": "hash", ... }

# 3. content.publish with full manifest
echo '{"jsonrpc":"2.0","method":"content.publish","params":{"collection":"sporeprint-'$VERSION'","manifest":'$MANIFEST'},"id":1}' \
  | nc -w 5 127.0.0.1 $NESTGATE_PORT

# 4. content.promote to set "latest" alias
echo '{"jsonrpc":"2.0","method":"content.promote","params":{"collection":"sporeprint-'$VERSION'","alias":"sporeprint-latest"},"id":1}' \
  | nc -w 5 127.0.0.1 $NESTGATE_PORT
```

---

## Available NestGate content methods

| Method | Purpose |
|--------|---------|
| `content.put` | Store content → returns BLAKE3 hash |
| `content.get` | Retrieve by hash (includes provenance metadata) |
| `content.exists` | Check hash existence (includes provenance) |
| `content.list` | Enumerate all stored hashes |
| `content.publish` | Create named manifest (path → hash mapping) |
| `content.promote` | Alias one collection to another |
| `content.resolve` | Look up hash by path within collection |
| `content.collections` | List all manifests/aliases |

---

## Action items

| Owner | Item |
|-------|------|
| projectNUCLEUS | Fix `publish_sporeprint.sh` to use correct RPC names and params |
| projectNUCLEUS | Capture hash from `content.put` responses, build JSON manifest |
| projectNUCLEUS | Replace `collection.create` with `content.publish` + `content.promote` |
| NestGate | **None** — backend complete on all transport paths |
