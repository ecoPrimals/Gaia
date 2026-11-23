# sweetGrass v0.7.51 — Wave 79b Handoff

**Date**: 2026-06-05
**From**: strandGate (sweetGrass)
**Wave**: 79b

---

## What Landed

### Localhost-Only Default Bind

VPS overwatch flagged `--http-address` defaulting to `0.0.0.0:0`
(all interfaces). Fixed:

| Flag | Before | After |
|------|--------|-------|
| `--http-address` | `0.0.0.0:0` | `127.0.0.1:0` |
| `--tarpc-address` | `0.0.0.0:0` | `127.0.0.1:0` |
| `--http-port N` | `0.0.0.0:N` | `127.0.0.1:N` |

External all-interfaces binding is now opt-in only via explicit
`0.0.0.0:PORT` or `--http-address 0.0.0.0:PORT`.

### VPS Impact

The VPS unit's `--http-address 127.0.0.1:0` workaround is no longer
needed — the default now matches the workaround. The binary can be
refreshed and the explicit flag removed from the systemd unit.

## Metrics

| Metric | Value |
|--------|-------|
| Version | v0.7.51 |
| Tests | 1,615+ |
| Coverage | 91.7% |
| Clippy | Zero warnings (pedantic + nursery) |

## Status

sweetGrass action item from Wave 79b blurbs: **RESOLVED**.
Ready for VPS binary refresh.
