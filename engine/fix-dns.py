"""Fix hud.primals.eco DNS — delete CF Pages record, add tunnel CNAME."""
import subprocess, json, sys

TUNNEL_ID = "2c12060a-8582-47c2-b8ff-c7c157f036d9"
HOSTNAME = "hud.primals.eco"

# Step 1: Try to delete existing DNS record via cloudflared
# cloudflared uses cert.pem which has API access
print(f"Attempting to route {HOSTNAME} through tunnel {TUNNEL_ID}...")

# The issue: cloudflared route dns fails because a record already exists
# We need to use the CF API to delete it first

# Read the cert.pem to find the API token
# cloudflared cert.pem contains an API token in a specific format
import os
cert_path = os.path.expanduser("~/.cloudflared/cert.pem")
if os.path.exists(cert_path):
    print(f"Found cert at {cert_path}")
else:
    print("No cert found!")
    sys.exit(1)

# Use cloudflared tunnel route to force-create the DNS record
# First try deleting via the CF API using the service token from cloudflared
result = subprocess.run(
    ["cloudflared", "tunnel", "route", "dns", "--overwrite-dns", TUNNEL_ID, HOSTNAME],
    capture_output=True, text=True
)
print(f"stdout: {result.stdout}")
print(f"stderr: {result.stderr}")
print(f"returncode: {result.returncode}")

if result.returncode == 0:
    print(f"SUCCESS: {HOSTNAME} now routes through tunnel!")
else:
    print(f"Failed. May need manual DNS change in Cloudflare dashboard.")
    print(f"Go to: https://dash.cloudflare.com → primals.eco → DNS")
    print(f"Delete the existing hud record")
    print(f"Then run: cloudflared tunnel route dns {TUNNEL_ID} {HOSTNAME}")
