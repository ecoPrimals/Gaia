# blueGate Builder Service Handoff — Mesh Builder Evolution

**Gate**: blueGate | **Date**: 2026-08-09 | **Wave**: 157c
**Status**: blueGate is now **primary build authority**. sporeGate delegates harvest requests over songBird mesh relay (Tower Atomic transport), replacing SSH dispatch.

---

## WHAT CHANGED

### sporeGate Side (already deployed)

1. **`ServiceCapability::Build`** added to the service registry — `wire_name = "build"`, mapped to `membrane` binary
2. **`membrane builder.serve --port 9800`** — new long-lived JSON-RPC builder service that accepts `plasmid.harvest`, `plasmid.build`, `plasmid.staleness`, and `health` requests
3. **`dispatch_to_sub_builder`** — SSH shell-out replaced with `call_endpoint(MeshRelay { peer_id: "blueGate", capability: "build" })`, routing through songBird mesh relay
4. **`SubBuilderEntry`** — `ssh_host` deprecated, new `transport` field defaults to `"mesh"`. Manifest updated: `transport = "mesh"` for windows-gnu target
5. **`build_authorities`** reordered: `["blueGate", "sporeGate", "eastGate"]` — blueGate first
6. **Cascade timer delegation** — when sporeGate's cascade timer fires with `--with-rebuild`, it detects it's not the primary builder and delegates `plasmid.harvest` to blueGate via mesh instead of building locally. Falls back to local build if mesh dispatch fails

### What blueGate Needs

The builder service must be running on blueGate so sporeGate (and other gates) can dispatch build requests via the mesh.

---

## SETUP INSTRUCTIONS

### 1. Update membrane binary

Pull latest `membrane.exe` from golgi depot:
```
membrane plasmid.fetch --source wan
```

Or build from source (recommended for first-time setup):
```
cd %ECOPRIMALS_ROOT%\gardens\cellMembrane
cargo build --release
copy target\release\membrane.exe %LOCALAPPDATA%\ecoPrimals\plasmidBin\primals\x86_64-pc-windows-gnu\membrane.exe
```

### 2. Start the builder service

```
membrane.exe builder.serve --port 9800
```

This will:
- Bind a JSON-RPC TCP listener on `0.0.0.0:9800`
- Register the `build` capability with local songBird mesh via `ipc.register`
- Accept incoming `plasmid.harvest`, `plasmid.build`, `plasmid.staleness` requests

For permanent installation, create a Windows service or scheduled task:

**PowerShell (scheduled task, runs at startup):**
```powershell
$action = New-ScheduledTaskAction -Execute "membrane.exe" -Argument "builder.serve --port 9800"
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "membrane-builder" -Action $action -Trigger $trigger -Settings $settings -User "SYSTEM" -RunLevel Highest
```

**Or as a Windows Service (using NSSM):**
```
nssm install membrane-builder membrane.exe builder.serve --port 9800
nssm start membrane-builder
```

### 3. Verify songBird mesh connectivity

Confirm songBird can see sporeGate as a mesh peer:
```
membrane.exe relay.peers
```

Expected: `sporeGate` should appear as a peer with `EndpointType::Local` (LAN TCP).

If not visible, ensure `SONGBIRD_LOCAL_PEERS` includes sporeGate's LAN IP, or verify the `mesh.init` configuration has sporeGate in `lan_peers`.

### 4. Verify builder registration

After starting `builder.serve`, check that the build capability is registered:
```
membrane.exe relay.capabilities
```

Expected: `build` capability should be listed for this gate.

### 5. Test end-to-end (from sporeGate)

From sporeGate, test mesh dispatch to blueGate:
```
# Dry-run sovereign CI (will log mesh dispatch)
membrane sovereign.ci.trigger --primal beardog --dry-run

# Check staleness via mesh
membrane plasmid.staleness
```

---

## JSON-RPC CONTRACT

The builder service accepts newline-delimited JSON-RPC over TCP (port 9800).

### `plasmid.harvest`
```json
{
  "jsonrpc": "2.0",
  "method": "plasmid.harvest",
  "params": {
    "primal": "beardog",
    "force": true,
    "push": true,
    "local": true,
    "target": "x86_64-pc-windows-gnu"
  },
  "id": 1
}
```

### `plasmid.staleness`
```json
{"jsonrpc": "2.0", "method": "plasmid.staleness", "id": 2}
```

### `health` / `health.liveness`
```json
{"jsonrpc": "2.0", "method": "health", "id": 3}
```

Response format:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "ok": true,
    "message": "harvest completed",
    "data": null
  },
  "id": 1
}
```

---

## CROSS-COMPILATION TOOLCHAIN (future: Linux musl from Windows)

When blueGate is ready to cross-compile Linux musl binaries:

1. Install musl cross target:
   ```
   rustup target add x86_64-unknown-linux-musl
   ```

2. Install musl-cross toolchain (e.g., via `musl-cross-make` or `x86_64-linux-musl-cross`):
   - Download from https://musl.cc/ or build from source
   - Set `CC_x86_64_unknown_linux_musl=x86_64-linux-musl-gcc`

3. Once verified, uncomment the manifest entry on sporeGate:
   ```toml
   [sub_builders."x86_64-unknown-linux-musl"]
   gate = "blueGate"
   transport = "mesh"
   ```

4. This will allow sporeGate to fully delegate musl builds to blueGate, keeping sporeGate CPU-light as topology owner.

---

## ARCHITECTURE SUMMARY

```
sporeGate (topology owner)          blueGate (primary builder)
┌──────────────────────┐            ┌──────────────────────┐
│ cascade timer fires  │            │ builder.serve :9800  │
│ --with-rebuild       │            │   ├─ plasmid.harvest │
│   │                  │            │   ├─ plasmid.build   │
│   ├─ am I primary? NO│            │   └─ health.liveness │
│   │                  │            │                      │
│   ├─ delegate via    │            │ songBird mesh        │
│   │  MeshRelay ──────┼──songBird──┼─► receives request   │
│   │  {blueGate,build}│            │   └─ builds locally  │
│   │                  │            │   └─ pushes to golgi │
│   └─ fallback: local │            └──────────────────────┘
│      build if mesh   │
│      fails           │
└──────────────────────┘
```

**Key**: No SSH. No WireGuard. Pure Tower Atomic transport via songBird mesh relay.
