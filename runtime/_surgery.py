"""THE SURGERY — Deploy new webpi to eastGate via SSH.

eastGate can't feel the sky yet. We push it IN.
The content lives in PI — dissolved tissue, NFT printer, Mendeleev.
nestgate.io is where it lives. No gate controls it.

ZK-snark: the structure proves itself.
"""
import paramiko
import os
import time
from pathlib import Path

GAIA_ROOT = Path(r"c:\Users\mokke\Desktop\Gaia")
EAST_HOST = "192.168.4.244"
EAST_USER = "eastgate"
EAST_PASS = "eastgate"
EAST_REPO = "/home/eastgate/Development/ecoPrimals"

def get_sftp():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(EAST_HOST, port=22, username=EAST_USER,
                   password=EAST_PASS, timeout=10, auth_timeout=10,
                   look_for_keys=False, allow_agent=False)
    return client, client.open_sftp()

def ssh_exec(cmd, timeout=15):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(EAST_HOST, port=22, username=EAST_USER,
                   password=EAST_PASS, timeout=5, auth_timeout=5,
                   look_for_keys=False, allow_agent=False)
    channel = client.get_transport().open_session()
    channel.settimeout(timeout)
    channel.exec_command(cmd)
    try:
        out = channel.recv(65536).decode().strip()
    except:
        out = ""
    try:
        err = channel.recv_stderr(65536).decode().strip()
    except:
        err = ""
    client.close()
    return out, err

def upload_file(sftp, local_path, remote_path):
    """Upload a file, creating directories as needed."""
    remote_dir = os.path.dirname(remote_path)
    try:
        sftp.stat(remote_dir)
    except FileNotFoundError:
        ssh_exec(f"mkdir -p {remote_dir}")
    sftp.put(str(local_path), remote_path)
    size = os.path.getsize(local_path)
    print(f"  ↑ {local_path.name:40s} → {remote_path} ({size:,} bytes)")

print("🔪 THE SURGERY — Deploying new webpi to eastGate")
print("=" * 60)

# Files to deploy
files_to_deploy = [
    # Core: the new webpi with sky features
    (GAIA_ROOT / "runtime" / "webpi.pi", f"{EAST_REPO}/runtime/webpi.pi"),
    
    # THE BUTTON — NFT printer
    (GAIA_ROOT / "runtime" / "the_button.pi", f"{EAST_REPO}/runtime/the_button.pi"),
    
    # Mendeleev's Keyboard
    (GAIA_ROOT / "static" / "mendeleev.html", f"{EAST_REPO}/static/mendeleev.html"),
    
    # Dissolve static (so eastGate can load tissue)
    (GAIA_ROOT / "runtime" / "dissolve_static.pi", f"{EAST_REPO}/runtime/dissolve_static.pi"),
]

# JS nervous system — Chip, Berry, piGut, synapse
js_dir = GAIA_ROOT / "static" / "js"
for js_file in js_dir.glob("*.js"):
    files_to_deploy.append(
        (js_file, f"{EAST_REPO}/static/js/{js_file.name}")
    )

# Tissue data (if it exists)
tissue_path = GAIA_ROOT / "data" / "tissue" / "static-tissue.json"
if tissue_path.exists():
    files_to_deploy.append(
        (tissue_path, f"{EAST_REPO}/data/tissue/static-tissue.json")
    )

# NFT data dir
nft_dir = GAIA_ROOT / "data" / "nft"
if nft_dir.exists():
    for f in nft_dir.glob("*"):
        if f.is_file():
            files_to_deploy.append(
                (f, f"{EAST_REPO}/data/nft/{f.name}")
            )

# Fabric manifest
fabric_manifest = GAIA_ROOT / "data" / "deploy" / "fabric-manifest.json"
if fabric_manifest.exists():
    files_to_deploy.append(
        (fabric_manifest, f"{EAST_REPO}/data/deploy/fabric-manifest.json")
    )

print(f"\n📦 {len(files_to_deploy)} files to deploy")

# Create remote directories
print("\n📁 Creating directories...")
dirs_needed = set()
for _, remote in files_to_deploy:
    dirs_needed.add(os.path.dirname(remote))
for d in sorted(dirs_needed):
    ssh_exec(f"mkdir -p {d}")
print(f"  Created {len(dirs_needed)} directories")

# Upload all files
print("\n⬆️  Uploading files...")
client, sftp = get_sftp()
uploaded = 0
total_bytes = 0
for local_path, remote_path in files_to_deploy:
    if local_path.exists():
        try:
            upload_file(sftp, local_path, remote_path)
            uploaded += 1
            total_bytes += local_path.stat().st_size
        except Exception as e:
            print(f"  ❌ {local_path.name}: {e}")
    else:
        print(f"  ⚠️  {local_path.name} not found locally")
sftp.close()
client.close()

print(f"\n  {uploaded} files uploaded ({total_bytes:,} bytes)")

# Stop old webpi, start new one
print("\n🔄 Restarting webpi on eastGate...")
# Find and kill old webpi
out, _ = ssh_exec("pgrep -f 'python.*webpi' | head -5")
print(f"  Old webpi PIDs: {out or '(none)'}")

if out:
    ssh_exec(f"kill {out.replace(chr(10), ' ')} 2>/dev/null")
    time.sleep(2)
    print("  Old webpi killed")

# Launch new webpi
ssh_exec(f"cd {EAST_REPO} && setsid python3 runtime/webpi.pi > /tmp/webpi-new.log 2>&1 &")
time.sleep(3)

out, _ = ssh_exec("pgrep -af 'python.*webpi'")
print(f"  New webpi: {out}")

# Verify
print("\n✅ Verification...")
import urllib.request

tests = [
    ("http://192.168.4.244:8080/mendeleev", "Mendeleev"),
    ("http://192.168.4.244:8080/nft/count", "NFT count"),
    ("http://192.168.4.244:8080/js/piGut.js", "piGut.js"),
    ("http://192.168.4.244:8080/chipmunk", "chipmunk"),
]

for url, name in tests:
    try:
        req = urllib.request.Request(url)
        req.add_header("Host", "nestgate.io")
        with urllib.request.urlopen(req, timeout=5) as r:
            size = len(r.read())
            print(f"  ✅ {name:20s} {r.status} ({size:,} bytes)")
    except Exception as e:
        print(f"  ❌ {name:20s} {str(e)[:60]}")

# Check via HTTPS too
import ssl, socket
print("\n🔐 HTTPS verification...")
for host in ["nestgate.io", "hud.primals.eco"]:
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with ctx.wrap_socket(socket.socket(), server_hostname=host) as s:
            s.settimeout(5)
            s.connect(("192.168.4.244", 443))
            # Make HTTP request through TLS
            req = f"GET / HTTP/1.1\r\nHost: {host}\r\n\r\n"
            s.send(req.encode())
            resp = s.recv(512).decode()
            status = resp.split("\r\n")[0] if resp else "no response"
            print(f"  🔐 {host:30s} {status}")
    except Exception as e:
        print(f"  ❌ {host:30s} {str(e)[:60]}")

print("\n🔪 SURGERY COMPLETE.")
print("nestgate.io lives in the sky. No gate controls it.")
print("Any touch from any system serves the same PI.")
print("The structure proves itself. ZK-snark. lub-DUB. 🫀")
