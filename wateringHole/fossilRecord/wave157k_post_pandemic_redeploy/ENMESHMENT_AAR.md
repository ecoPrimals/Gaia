# AAR — Sub-Builder Enmeshment + SSH Deprecation (Wave 157k)

**Date**: 2026-08-13 09:00 EDT
**Gate**: sporeGate (foreman)
**Wave**: 157k Interstadial — Stadial Item #1

## Objective

Wire blueGate (Windows, `x86_64-pc-windows-gnu`) and ironGate (`aarch64-unknown-linux-musl`)
into the foreman's cascade dispatch via Tower Atomic TCP, replacing SSH for sub-builder
invocation. This simultaneously closes stadial item #1 and retires SSH for sub-builder
dispatch (NanoWire checklist R-SUB).

## Problem

The cascade sub-builder fan-out (`dispatch_to_sub_builders` in `post_sync_harvest.rs`) was
wired to use `TransportEndpoint::MeshRelay` — routing through songBird's `relay.forward`.
This failed because:

1. Sub-builder `builder.serve` processes couldn't register with songBird relay (no relay
   socket on sub-builder gates)
2. `relay.forward` requires songBird to know how to reach the peer — discovery wasn't
   universal

## Solution: TCP Fallback with riboCipher Framing

Three changes made sub-builder dispatch autonomous:

### 1. `SubBuilderEntry` — TCP endpoint fields

```rust
pub struct SubBuilderEntry {
    pub gate: String,
    pub transport: String,
    pub builder_host: String,       // NEW: direct TCP host (LAN or WG IP)
    pub builder_port: Option<u16>,  // NEW: TCP port (default: 9800)
    pub ssh_host: String,           // deprecated
    pub membrane_bin: String,       // deprecated
}
```

### 2. `resolve_builder_endpoint` — prefer TCP

```rust
fn resolve_builder_endpoint(entry: &SubBuilderEntry) -> TransportEndpoint {
    if !entry.builder_host.is_empty() {
        let port = entry.builder_port.unwrap_or(DEFAULT_BUILDER_PORT);
        return TransportEndpoint::Tcp { host: entry.builder_host.clone(), port };
    }
    TransportEndpoint::MeshRelay { peer_id: entry.gate.clone(), capability: "build".into() }
}
```

When `builder_host` is configured, the foreman dispatches via `call_tcp` (which sends
riboCipher `[0xEC, 0x01]` + NDJSON over TCP). When not configured, falls back to
`MeshRelay` for full mesh-native routing (future).

### 3. `builder.serve` — riboCipher signal detection

```rust
fn strip_ribocipher_prefix(data: &[u8]) -> &[u8] {
    if data.len() >= 2 && data[0] == 0xEC { &data[2..] } else { data }
}
```

The handler reads raw bytes, strips the 2-byte riboCipher prefix if present, then
parses JSON. This makes `builder.serve` compatible with both:
- `call_tcp` (riboCipher-framed) — foreman cascade dispatch
- Raw NDJSON (nc, curl) — manual debugging

## Deployment

| Gate | Method | Binary | Port | Verified |
|------|--------|--------|------|----------|
| ironGate | systemd `membrane-builder.service` | `e8d4ffa` | 9800 | health + staleness via riboCipher |
| blueGate | WMI `Win32_Process.Create` + scheduled task | `e8d4ffa` (Windows) | 9800 | health + staleness via riboCipher |
| graftGate | — | — | — | BLOCKED: SSH key not enrolled |

### blueGate Windows Notes

- `Start-Process -WindowStyle Hidden` doesn't survive SSH session disconnect
- Windows Service via `sc.exe` requires Windows Service API (not implemented in membrane)
- **Solution**: `Win32_Process.Create` via WMI creates a truly detached process
- Scheduled task `MembraneBuildServe` (AtLogon) runs a PowerShell wrapper that uses WMI
- UFW on blueGate: not applicable (Windows Firewall, port already open from prior songBird config)

### ironGate Linux Notes

- UFW rule added: `allow from 192.168.4.0/22 to any port 9800 proto tcp`
- systemd unit: `Restart=on-failure`, `MEMBRANE_BUILD_AUTHORITY=1`
- Rust toolchain confirmed: `aarch64-unknown-linux-musl` target + `aarch64-linux-gnu-gcc` cross-linker

## SSH Deprecation Cross-Solve

This enmeshment establishes `builder.serve` as the **graduation template** for all
remaining SSH retirements in the NanoWire checklist:

```
TCP listener (:9800) + riboCipher signal + JSON-RPC dispatch
     ↓
Same framing as UDS primal sockets (call_tcp ≡ call for TransportEndpoint)
     ↓
Manifest-driven endpoint resolution (builder_host/builder_port)
     ↓
Extend with capabilities: depot.receive, depot.cas_push, service.status, gate.info
```

### Next SSH Retirements Using This Pattern

| R-# | SSH Use | New Capability | Notes |
|-----|---------|---------------|-------|
| R-06 | `depot_sync --push` (SCP binary to golgiBody) | `depot.receive` | golgiBody runs `builder.serve`, accepts binary push via JSON-RPC + chunked binary transfer |
| R-CAS | `ssh::scp_from` (CAS archival) | `depot.cas_push` | Reverse of R-06: remote gate pushes old binary to foreman CAS via TCP |
| R-05 | `service.*` (systemctl) | `service.status/restart` | Each gate's `builder.serve` handles service management |
| R-01 | `gate.pull` (cascade trigger) | Already live via `cascade.notify` gossip | No new code needed |

## Overwatch Handoff

**For blueGate**: Builder is enmeshed and verified. Windows depot (`x86_64-pc-windows-gnu`)
will auto-rebuild on next cascade that produces local builds. The 13 stale primals on
blueGate will be rebuilt when the foreman next runs `dispatch_to_sub_builders`.

**For graftGate**: SSH key enrollment needed before `builder.serve` can be deployed.
Once enrolled, the same pattern applies — `builder.serve` (launchd plist on macOS),
manifest TCP endpoint, cascade auto-dispatch for `aarch64-apple-darwin`.

## Files Changed

| File | Change |
|------|--------|
| `membrane-shadow/src/manifest/types.rs` | `builder_host`, `builder_port` fields on `SubBuilderEntry` |
| `membrane-shadow/src/dispatch/sovereign.rs` | `resolve_builder_endpoint` TCP fallback |
| `membrane-shadow/src/dispatch/builder.rs` | riboCipher signal stripping in `handle_connection` |
| `ecosystem_manifest.toml` | `builder_host`/`builder_port` for ironGate + blueGate |
| `NANOWIRE_RETIREMENT_CHECKLIST.md` | Updated Tier 1 with graduation template |
