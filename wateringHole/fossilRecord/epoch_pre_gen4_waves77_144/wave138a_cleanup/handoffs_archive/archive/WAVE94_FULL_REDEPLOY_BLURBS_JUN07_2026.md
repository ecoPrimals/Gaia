# Wave 94 Blurbs — Full Redeploy + 3-Gate Mesh

**Strategy**: Full redeploy and validate on eastGate + strandGate. ironGate is the
clean-room LAN deployment proving ground — rollback and redeploy until bulletproof.

**ironGate already validated**: clean-room PASS (all checks except capability.call).

---

## bearDog Team — P1: `capability.call` Handler

**Sole mesh blocker.** Songbird peer TLS handshake calls `capability.call` on beardog
for cert provisioning. beardog v0.9.0 returns `-32601 Method not found`. All 3 gates
show `reachable_peers: 0` despite Songbird healthy on `:7700`.

beardog has 217 methods (full TLS + BTSP suites). Needs `capability.call` as routing
dispatcher connecting them to Songbird's federation handshake.

After shipping: rebuild, `membrane plasmid.harvest`, then all gates get the fix via
`membrane plasmid.refresh`.

**Priority**: P1 — blocks 3-gate mesh.

---

## cellMembrane / ironGate — Validated, Ready for Mesh

ironGate clean-room deployment: **PASS**. All 13 primals from depot, idempotent
rollback/redeploy, health OK, LAN reachable at 192.168.1.238:7700.

Key findings documented:
- `--security-socket` flag NOT recognized — use `SONGBIRD_SECURITY_PROVIDER` env
- Stale sockets require `rm -f /run/user/1000/biomeos/*.sock` on rollback

**Next**: Once beardog ships `capability.call`, refresh depot and mesh.init with
eastGate + strandGate peers. ironGate becomes the 3rd mesh node.

Also: toadStool divergence detected (forgejo +13 vs origin +126). Resolve via
`pull_leader_push_followers` per impulse.

---

## hotSpring / strandGate — Full Redeploy Validation

strandGate Songbird healthy on 192.168.1.132:7700. Needs the same clean-room
validation ironGate completed:

```bash
# 1. Full rollback
pkill -f beardog; pkill -f songbird; sleep 1
rm -f /run/user/1000/biomeos/*.sock

# 2. Fresh deploy from plasmidBin
$ECOPRIMALS_PLASMID_BIN/beardog server --socket /run/user/1000/biomeos/beardog.sock &
sleep 2
SONGBIRD_SECURITY_PROVIDER=/run/user/1000/biomeos/beardog.sock \
  $ECOPRIMALS_PLASMID_BIN/songbird server --federation-port 7700 --bind 0.0.0.0 \
  --socket /run/user/1000/biomeos/songbird.sock &
sleep 2

# 3. Verify
curl http://192.168.1.132:7700/health   # OK
membrane plasmid.status                 # 13/13
```

**Checklist** (must ALL pass — match ironGate standard):
- [ ] `membrane plasmid.status` → 13/13 current
- [ ] All primals from depot (no cargo build)
- [ ] Sockets present in `/run/user/1000/biomeos/`
- [ ] `:7700/health` → OK
- [ ] beardog `health.liveness` → alive
- [ ] Rollback + redeploy = identical result

**Priority**: P1 — must match ironGate deployment standard before mesh.

---

## eastGate (us) — Redeploy + Overwatch

We run the same pattern, then coordinate the 3-gate mesh bring-up.

Current: Songbird LIVE (PID 1235788), beardog LIVE (v0.9.0), depot 13/13,
cascade 37/38 (wateringHole divergence resolved), primalSpring hardened.

**After beardog fix ships** — all 3 gates mesh.init simultaneously:
```bash
# eastGate
curl -s http://192.168.1.144:7700/jsonrpc -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"mesh.init","params":{"node_id":"east-gate","peers":["192.168.1.132:7700","192.168.1.238:7700"]}}'

# Validate all 3
for ip in 192.168.1.144 192.168.1.132 192.168.1.238; do
  echo "=== $ip ===" && curl -s http://$ip:7700/jsonrpc -X POST \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","id":1,"method":"mesh.status","params":{}}' && echo
done
# All must show: reachable_peers: 2
```

---

## Success Gate → Transport Evolution

All true before proceeding to Phase 2 M1 (ipc.resolve):
1. All 3 gates deploy identically from plasmidBin (13/13, zero build)
2. Rollback + redeploy = identical on every gate
3. `discovery.peers` returns 2 on each gate
4. `mesh.health_check` → `all_healthy: true` on each gate
5. Cross-gate `capability.call` routes to remote providers
