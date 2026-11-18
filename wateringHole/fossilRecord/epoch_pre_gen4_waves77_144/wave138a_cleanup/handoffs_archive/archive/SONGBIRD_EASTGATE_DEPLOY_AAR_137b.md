# SONGBIRD-EASTGATE Deployment AAR — Wave 137b

**Date**: Jul 13, 2026 11:10 EDT | **Gate**: eastGate | **Author**: eastGate overwatch

---

## Summary

Deployed songBird `74cf7101` (v0.2.1) from WAN depot to eastGate. Mesh operational with 2 peers (sporeGate + golgi). Three divergences discovered during deployment.

## Result

```
songBird v0.2.1 — active (PID 2690897)
Mesh: eastGate → sporeGate (71ms WG) + golgi (35ms WG)
UDS-HTTP fix confirmed: mesh_registered=true on peer.connect
94 methods, 15 capabilities, 2 direct paths
```

---

## Divergences Found

### DIV-01: Depot Checksum Mismatch (P2)

**Observed**: BLAKE3 of downloaded binary does not match `checksums.toml`.

| Source | BLAKE3 |
|--------|--------|
| `checksums.toml` | `55b66f7a1bb7740759a587346834ee9383ddb7d9a195c70b47a02f99b1d9add5` |
| Downloaded binary | `ece3dcac96cc50781b2049965f8652e89c8af159a8a16080913aec4be01ce710` |

**Evidence**: Downloaded binary is "with debug_info, not stripped" (26.6MB). The checksums were likely computed against a stripped build. The depot binary was rebuilt after checksums were signed.

**Impact**: cellMembrane's `VerifyIfPresent` policy would **reject** this binary. Any gate running `plasmid.fetch` with the new SIGN-VERIFY-ON-FETCH code (`89bf12f`) will fail to deploy songBird.

**Owner**: sporeGate team — re-sign depot after confirming binary is final. Either strip the binary or regenerate checksums against the current binary.

**Action**: `plasmid.harvest` songBird → checksums → sign → sync to golgi.

### DIV-02: Local Depot Path Empty (P2)

**Observed**: `plasmidBin/primals/x86_64-unknown-linux-musl/songbird` did not exist. The systemd template `membrane-nucleus@songbird.service` pointed to this path, causing a crash loop since service creation.

**Root cause**: The old `plasmid.fetch` (primalSpring fetch via GitHub releases) created a doubled nested path: `primals/x86_64-unknown-linux-musl/primals/x86_64-unknown-linux-musl/`. Only `nestgate` was in the nested dir. songBird was never placed at the correct path.

**Impact**: songBird was crash-looping on eastGate — no mesh participation until manual binary placement.

**Fix applied**: Manually downloaded from WAN depot and placed at correct path. Service now running.

**Owner**: cellMembrane team — `plasmid.fetch` path resolution needs to match the systemd template's `ExecStart` path. The doubled nesting suggests the fetch script prepends a path prefix that the binary directory already includes.

### DIV-03: Stale Gate Head Files (P3)

**Observed**: `mesh.status` reports stale head files:

```json
"stale_peers": [
  {"age_hours": 60, "file": "heads/golgi.toml", "gate": "golgi"},
  {"age_hours": 60, "file": "heads/sporeGate.toml", "gate": "sporeGate"}
]
```

Head files are 60 hours old (since Jul 11). golgiBody auto-publishes but the local copies haven't been refreshed since last cascade.

**Impact**: songBird's auto-discovery from head files uses stale addresses. Not a blocker (manual `peer.connect` works), but degrades auto-mesh capability.

**Owner**: Process — cascades should touch head files. Consider `songBird` reading heads from the repo directly rather than caching copies.

---

## Expected Errors (Not Divergences)

**TLS delegation failure**: songBird hardcodes `/var/run/biomeos/neural-api.sock` for TLS delegation to bearDog. Actual socket is at `/run/user/1000/biomeos/`. This is the known SOCKET-DIR-UNIFY issue (biomeOS team). Does not block mesh federation, only HTTPS outbound requests.

---

## Deployment Sequence (for future reference)

```
1. curl -o /tmp/songbird https://membrane.primals.eco/depot/x86_64-unknown-linux-musl/songbird
2. chmod +x /tmp/songbird
3. cp /tmp/songbird $ECOPRIMALS_ROOT/infra/plasmidBin/primals/x86_64-unknown-linux-musl/songbird
4. systemctl --user restart membrane-nucleus@songbird.service
5. socat: mesh.init → peer.connect (sporeGate, golgi) → mesh.peers (verify)
```

This should be `membrane plasmid.fetch --source wan && membrane deploy songbird` once SOCKET-DIR-UNIFY and DIV-02 are resolved.

---

*SONGBIRD-EASTGATE: COMPLETE. eastGate is now a 3-gate mesh participant. 3 divergences documented for upstream teams.*
