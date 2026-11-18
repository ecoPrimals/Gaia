# ironGate Handoff — Wave 132: Compute Capability Registration

**Date**: Jul 4, 2026  
**Gate**: ironGate  
**Team**: compute team  
**From**: eastGate overwatch  
**Type**: Deployment + capability registration — mesh-routed compute

---

## Objective

Make ironGate a first-class **capability provider** in the mesh. Deploy JupyterHub, register the `jupyter` capability with local songBird via `primal.announce`, and ensure songBird can proxy inbound `http.proxy` requests to localhost:8000. This enables sporeGate's Tower gateway to route external student traffic to ironGate compute without any port exposure.

---

## Current State on ironGate

| Component | State |
|-----------|-------|
| songBird | Running v0.2.1, mesh peered (eastGate, sporeGate) |
| Federation port | 7700/TCP open to LAN (192.168.4.0/22) |
| JupyterHub | **Not deployed** |
| GPU | RTX 5070 (16GB), CUDA driver installed |
| UFW | 7700/tcp from LAN allowed, 22/tcp open |

---

## Work Items

### 1. Deploy JupyterHub (localhost:8000)

#### Option A: Docker (recommended for isolation)

```bash
# Pull JupyterHub image
docker pull quay.io/jupyterhub/jupyterhub:latest

# Create config directory
sudo mkdir -p /etc/jupyterhub
cat > /etc/jupyterhub/jupyterhub_config.py << 'EOF'
c.JupyterHub.bind_url = 'http://127.0.0.1:8000'
c.JupyterHub.base_url = '/'
c.Authenticator.admin_users = {'bake3011', 'alistaire'}
c.Authenticator.allowed_users = {'bake3011', 'alistaire'}
c.LocalAuthenticator.create_system_users = False
c.Spawner.default_url = '/lab'
c.Spawner.environment = {
    'CUDA_VISIBLE_DEVICES': '0',
}
EOF

# Run (bind localhost only — songBird handles external routing)
docker run -d \
  --name jupyterhub \
  --restart always \
  --network host \
  -v /etc/jupyterhub:/srv/jupyterhub \
  -v /home:/home \
  --gpus all \
  quay.io/jupyterhub/jupyterhub:latest \
  jupyterhub -f /srv/jupyterhub/jupyterhub_config.py
```

#### Option B: Systemd (native)

```bash
pip install jupyterhub jupyterlab
sudo mkdir -p /etc/jupyterhub

# Create systemd unit
cat > /etc/systemd/system/jupyterhub.service << 'EOF'
[Unit]
Description=JupyterHub for ABG Compute
After=network-online.target

[Service]
Type=simple
ExecStart=/usr/local/bin/jupyterhub -f /etc/jupyterhub/jupyterhub_config.py
WorkingDirectory=/etc/jupyterhub
Restart=always
RestartSec=5
Environment=CUDA_VISIBLE_DEVICES=0

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable jupyterhub
sudo systemctl start jupyterhub
```

#### Validate

```bash
curl http://localhost:8000/hub/login
# Should return HTML login page
```

---

### 2. Register `jupyter` Capability with songBird

songBird supports `primal.announce` for dynamic capability registration. Register `jupyter` so the mesh knows ironGate provides this service.

#### Via JSON-RPC (UDS)

```bash
echo '{"jsonrpc":"2.0","method":"primal.announce","params":{"primal":"jupyterhub","capabilities":["jupyter","compute.jupyter"],"transports":{"http":{"host":"127.0.0.1","port":8000}}},"id":1}' | \
  socat - UNIX:/run/songbird/songbird.sock
```

If songBird socket is at a different path:
```bash
# Check running socket
ss -lx | grep songbird
```

#### Persist on restart

Create `/etc/songbird/capabilities.d/jupyter.json`:

```json
{
  "primal": "jupyterhub",
  "capabilities": ["jupyter", "compute.jupyter"],
  "transports": {
    "http": {
      "host": "127.0.0.1",
      "port": 8000
    }
  }
}
```

songBird loads capability registrations from `capabilities.d/` on startup (if supported in v0.2.1+). Otherwise, add a systemd ExecStartPost:

```ini
ExecStartPost=/bin/sh -c 'sleep 2 && echo ... | socat - UNIX:/run/songbird/songbird.sock'
```

---

### 3. songBird `http.proxy` Local Handler

When songBird on ironGate receives an inbound `capability.call` with `operation: "http.proxy"` for the `jupyter` capability, it must proxy to localhost:8000.

This is handled by the evolved songBird binary from flockGate (see FLOCKGATE handoff). Once deployed:

1. songBird receives: `{"method":"capability.call","params":{"capability":"jupyter","operation":"http.proxy","data":{"path":"/hub/login","method":"GET",...}}}`
2. songBird resolves `jupyter` → local provider at `127.0.0.1:8000`
3. songBird makes HTTP request to `http://127.0.0.1:8000/hub/login`
4. Returns response back through mesh

**Config needed** (in songbird.toml or equivalent):

```toml
[local_capabilities]
jupyter = { host = "127.0.0.1", port = 8000 }
```

---

### 4. Validate End-to-End

#### From ironGate locally

```bash
# Direct
curl http://localhost:8000/hub/login

# Via songBird local proxy
echo '{"jsonrpc":"2.0","method":"http.proxy","params":{"host":"localhost","path":"/hub/login","method":"GET"},"id":1}' | \
  socat - UNIX:/run/songbird/songbird.sock
```

#### From eastGate (cross-gate via mesh)

```bash
echo '{"jsonrpc":"2.0","method":"capability.call","params":{"capability":"jupyter","operation":"http.proxy","data":{"path":"/hub/login","method":"GET"}},"id":1}' | \
  socat - UNIX:/run/user/1000/biomeos/songbird.sock
```

Should return JupyterHub login HTML from ironGate.

#### From sporeGate (full Tower path, after SPOREGATE handoff)

```bash
curl https://lab.primals.eco/hub/login
```

---

## Firewall (no changes needed)

- Port 8000 binds to `127.0.0.1` only — not exposed
- Port 7700/TCP already open to LAN for songBird federation
- All inbound compute traffic arrives via songBird mesh (port 7700), not direct HTTP

---

## Bioinformatics Stack (Phase 2)

After JupyterHub is live and capability-registered, install compute tools:

```bash
# Conda environment for ABG
conda create -n abg python=3.11 -y
conda activate abg
pip install salmon-tools scanpy anndata
conda install -c bioconda star salmon samtools -y

# GPU tools
pip install cupy-cuda12x rapids-singlecell
```

Stage pilot dataset (eastGate overwatch will transfer via mesh):
- GSE166686 RNA-seq (salmon quant)
- ~2GB compressed

---

## Acceptance Criteria

1. JupyterHub accessible at `http://localhost:8000/hub/login` on ironGate
2. `jupyter` capability registered with local songBird (`capabilities.list` shows it)
3. Cross-gate `capability.call` from eastGate/sporeGate for `jupyter` capability reaches JupyterHub
4. JupyterHub binds only to localhost — zero external port exposure
5. GPU available in JupyterHub notebooks (`nvidia-smi` works, CUDA toolkit accessible)

---

## Dependencies

- songBird v0.2.1 already running and mesh-peered (validated Wave 132b)
- Evolved songBird with `http.proxy` local handler (from flockGate — needed for full E2E, but capability registration can happen now)

---

*Compute enters the mesh. Students connect through the membrane, not through ports.*
