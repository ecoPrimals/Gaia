# biomeOS → primalSpring: Wave 31 Response — primal.list Schema Alignment

**Date:** May 20, 2026
**Author:** biomeOS team (southGate)
**Audience:** primalSpring, all consumers of `primal.list`
**Status:** All 3 biomeOS items RESOLVED or previously resolved
**Version:** v3.65
**License:** AGPL-3.0-or-later

---

## primal.list Schema Alignment — RESOLVED (v3.65)

### Problem

`primal.list` was wired since v3.24 but the entry schema did not match
primalSpring's Wave 20 canonical spec (`s_schema_standard`). biomeOS
emitted `primal_type`/`socket_path`/`health` while the spec requires
`name`/`socket`/`status` as required fields.

### Fix

`TopologyHandler::get_primals()` and `discover_active_primals()` now
emit the Wave 20 canonical schema:

```json
{
  "primals": [
    {
      "name": "toadstool",
      "socket": "/run/user/1000/biomeos/toadstool-default.sock",
      "status": "running",
      "capabilities": ["compute"],
      "pid": 12345,
      "version": null
    }
  ],
  "count": 1,
  "timestamp": "2026-05-20T...",
  "family_id": "default"
}
```

### Field mapping

| Wave 20 (canonical) | Old biomeOS field | Status |
|---------------------|-------------------|--------|
| `name` (required) | `primal_type` | Added; `primal_type` retained for compat |
| `socket` (required) | `socket_path` | Added; `socket_path` retained for compat |
| `status` (required) | `health` | Added; `health` retained for compat |
| `pid` (optional) | — | Added; reads from v3.62 PID files |
| `capabilities` (optional) | `capabilities` | Already present |
| `version` (optional) | — | Added (null until primals report version) |

`id`, `primal_type`, `socket_path`, `health`, `resource_usage` remain
in the response for backward compatibility. Consumers should prefer the
canonical Wave 20 field names.

### PID surfacing

`read_pid_file()` reads `{primal}-{family_id}.pid` files from the
socket directory. These are written by NUCLEUS since v3.62. If no PID
file exists (non-NUCLEUS launches), `pid` is null.

### Test coverage

Topology tests updated to assert Wave 20 canonical fields (`name`,
`socket`, `status`) alongside legacy fields. `s_schema_standard` Phase 4
live probe should now pass against the neural-api socket.

### biomeos-api self-report

The biomeos-api Unix socket stub also emits Wave 20 fields for its
self-report entry (`name: "biomeos"`, `socket: "self"`, `status: "running"`,
`pid: <actual>`).

---

## Previously resolved items (confirmed stadial-current)

| Item | Wave 31 listing | Resolution | Version |
|------|-----------------|------------|---------|
| `nest.store` signal dispatch | LOW | All 17 signals as first-class route table entries | v3.63 |
| `spore.instantiate` | LOW | Deferred-to-stadial; scaffold + graph structural | v3.63 |

Both items were resolved in v3.63 and absorbed in `PRIMAL_GAPS.md`. The
Wave 31 blurb's listing reflects the deferred status correctly — these
are horizon items, not blocking gaps.

---

## biomeOS stadial status

| Metric | Value |
|--------|-------|
| Tests | 7,924+ |
| BTSP Phase 3 | FULL |
| sporePrint | Complete |
| Zero Debt | Clean |
| Signal graphs | 17 (5 tiers) |
| Capability translations | 320+ (27 domains) |
| primal.list schema | Wave 20 conformant |
