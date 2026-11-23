# FRAGO: ironGate JupyterHub — projectNUCLEUS + projectFOUNDATION

**Date**: Jul 4, 2026 18:30 EDT  
**Wave**: 132e  
**Gate**: ironGate  
**Teams**: projectNUCLEUS (deployment validation), projectFOUNDATION (infrastructure)  
**From**: eastGate overwatch  
**Priority**: P1 — this is the E2E Tower HTTP blocker  
**Parent handoff**: `IRONGATE_WAVE132_COMPUTE_REGISTRATION_JUL04_2026.md`

---

## Situation

Tower HTTP Gateway is **code-complete** (songBird `http.proxy` + bearDog ACME :443 + skunkBat scan). sporePrint living topology is **wired**. The full end-to-end path is blocked on one thing: **JupyterHub is not running on ironGate**.

Once JupyterHub is live at `localhost:8000` and the `jupyter` capability is registered with songBird, the entire sovereign compute pipeline activates.

---

## Mission

Get JupyterHub operational on ironGate, register it as a mesh capability, and validate the E2E path.

---

## Execution

### Phase 1: JupyterHub Deploy (projectFOUNDATION)

ironGate has CUDA drivers installed, RTX 5070 available, songBird running.

```bash
# SSH to ironGate
ssh irongate@192.168.4.237

# Docker approach (recommended — clean isolation, GPU passthrough)
docker pull quay.io/jupyterhub/jupyterhub:latest

sudo mkdir -p /etc/jupyterhub
sudo tee /etc/jupyterhub/jupyterhub_config.py << 'PYEOF'
c.JupyterHub.bind_url = 'http://127.0.0.1:8000'
c.Authenticator.admin_users = {'bake3011', 'alistaire'}
c.Authenticator.allowed_users = {'bake3011', 'alistaire'}
c.Spawner.default_url = '/lab'
c.Spawner.environment = {'CUDA_VISIBLE_DEVICES': '0'}
PYEOF

docker run -d \
  --name jupyterhub \
  --restart always \
  --network host \
  -v /etc/jupyterhub:/srv/jupyterhub \
  -v /home:/home \
  --gpus all \
  quay.io/jupyterhub/jupyterhub:latest \
  jupyterhub -f /srv/jupyterhub/jupyterhub_config.py

# Validate
curl -s http://localhost:8000/hub/login | grep -q "JupyterHub" && echo "OK" || echo "FAIL"
```

If Docker is not installed or GPU passthrough has issues, fall back to systemd:

```bash
pip install jupyterhub jupyterlab
sudo systemctl enable --now jupyterhub  # (after unit file creation, see parent handoff)
```

### Phase 2: Capability Registration (projectNUCLEUS)

Once JupyterHub responds at localhost:8000:

```bash
# Find songBird socket
SOCK=$(ss -lx | grep songbird | awk '{print $5}')

# Register jupyter capability
echo '{"jsonrpc":"2.0","method":"primal.announce","params":{"primal":"jupyterhub","capabilities":["jupyter","compute.jupyter"],"transports":{"http":{"host":"127.0.0.1","port":8000}}},"id":1}' | \
  socat - UNIX:${SOCK}

# Verify registration
echo '{"jsonrpc":"2.0","method":"capabilities.list","params":{},"id":2}' | \
  socat - UNIX:${SOCK}
# Should show "jupyter" in provided_capabilities
```

For persistence across restarts, set the env var on songBird:

```bash
# Add to songBird systemd override or env file
echo 'SONGBIRD_PROXY_ROUTES=jupyter=http://localhost:8000' | \
  sudo tee -a /etc/default/songbird

sudo systemctl restart membrane-nucleus@songbird
```

### Phase 3: E2E Validation (projectNUCLEUS)

From eastGate (or any peered gate):

```bash
# Cross-gate capability.call
echo '{"jsonrpc":"2.0","method":"capability.call","params":{"capability":"jupyter","gate":"ironGate","operation":"health"},"id":3}' | \
  socat - UNIX:/run/user/1000/biomeos/songbird.sock
```

From sporeGate (once Tower deployed there):

```bash
curl https://lab.primals.eco/hub/login
```

---

## Coordination

| Action | Team | Notes |
|--------|------|-------|
| SSH to ironGate, deploy JupyterHub | projectFOUNDATION | User `irongate`, `.237` on LAN |
| Register capability, validate mesh routing | projectNUCLEUS | songBird already peered |
| Report back to overwatch when localhost:8000 responds | Either | Update wateringHole heads |
| Trigger sporeGate binary build (once validated) | overwatch | Sovereign CI on sporeGate |

---

## Known State

- songBird v0.2.1 running on ironGate, peered with eastGate + sporeGate (0ms LAN)
- UFW: 7700/tcp + 8000/tcp from LAN allowed, 22/tcp open
- GPU: RTX 5070 (16GB), nvidia-smi confirms CUDA 12.8
- Depot: 22/22 repos synced, all binaries at parity
- Docker: verify `docker --version` — if not installed, use `sudo apt install docker.io nvidia-container-toolkit`

---

## Success Criteria

1. `curl http://localhost:8000/hub/login` on ironGate returns HTML
2. `capabilities.list` on ironGate songBird shows `jupyter`
3. `capability.call` from eastGate reaches ironGate JupyterHub
4. No ports exposed beyond existing (8000 binds localhost only)

---

*This is the last blocker for sovereign compute. Deploy it, register it, validate it.*
