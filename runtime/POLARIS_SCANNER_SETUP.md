# EPSON ES-400 Scanner — Polaris Bridge Setup

## The Problem
The ES-400 is USB-connected to Polaris (northGate, .147).
SSH port 22 is filtered on Polaris. SANE daemon port 6566 also filtered.
Polaris communicates via git pull from Forgejo/GitHub.

## The Solution
Run `scan_bridge.pi` on Polaris. It exposes the USB scanner over HTTP.

### On Polaris (northGate):
```bash
# 1. Pull latest Gaia repo
cd /path/to/Gaia && git pull

# 2. Check the ES-400 is visible
scanimage -L
# Should show: device 'epson2:libusb:...' or 'airscan:...'

# 3. Start the scan bridge
python3 runtime/scan_bridge.pi 6580 &

# 4. Open firewall for port 6580
# Windows: netsh advfirewall firewall add rule name="Gaia-Scan-Bridge" dir=in action=allow protocol=TCP localport=6580
# Linux: sudo ufw allow 6580/tcp
```

### From eastGate:
```bash
# Scan via Polaris
curl http://192.168.4.147:6580/scan?format=png&resolution=300 -o scan.png

# Get status
curl http://192.168.4.147:6580/status

# Format theory
curl http://192.168.4.147:6580/formats
```

## Alternative: Open SSH
```bash
# On Polaris, open SSH:
# Windows: Start-Service sshd  (or enable in Settings → Apps → Optional Features)
# Linux: sudo ufw allow 22/tcp

# Then from eastGate:
ssh tamison@192.168.4.147 scanimage -d 'epson2:libusb:...' --format=png -o /tmp/scan.png
scp tamison@192.168.4.147:/tmp/scan.png /opt/Gaia/data/gut/images/
```

## Alternative: Open saned
```bash
# On Polaris, start SANE daemon:
# 1. Add eastGate to /etc/sane.d/saned.conf: 192.168.4.244
# 2. Start: saned -a saned
# 3. Open firewall: port 6566

# Then on eastGate, add to /etc/sane.d/net.conf:
# 192.168.4.147
# Scanners on Polaris become visible to scanimage -L on eastGate
```
