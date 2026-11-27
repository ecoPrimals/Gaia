#!/bin/bash
# Gaia node profile, version 1 - the first thing a new server of the house runs.
#
# How to use it
#   A new server:  choose Debian 12 (or newer) or Ubuntu 22.04 (or newer), any size, and paste this whole file into
#                  the box the provider calls "User data", "Cloud-init", "Cloud config" or "Startup script".
#   A server that already exists:  run it once as root. Running it again changes nothing.
#
# What it does
#   - makes the user "gaia", who logs in only with the house's node key and may use sudo
#   - turns password logins over SSH off (root by key only, as the provider set it up)
#   - closes every port but 22, 80 and 443
#   - keeps security updates on
#   - writes what it did to /etc/gaia/node.json, which is what Gaia reads when she adopts the node
# What it does not do
#   It holds no secret and installs nothing of the house. Everything after this is done by Gaia over SSH.
#
# This file is the template: the line NODE_KEY= is filled in with the house's public node key when a copy is made
# for use. A copy without the key refuses to run.
set -u
PROFILE=1
NODE_KEY='__GAIA_NODE_PUBLIC_KEY__'

[ "$(id -u)" = 0 ] || { echo "the node profile has to run as root"; exit 1; }
case "$NODE_KEY" in
  "ssh-ed25519 AAAA"*) ;;
  *) echo "this copy of the node profile has no node key in it"; exit 1 ;;
esac
exec > >(tee -a /var/log/gaia-node-profile.log) 2>&1
echo "== gaia node profile $PROFILE, $(date -u +%Y-%m-%dT%H:%M:%SZ)"
export DEBIAN_FRONTEND=noninteractive
APT="apt-get -q -y -o DPkg::Lock::Timeout=300"

# 1. the user and the key
id gaia >/dev/null 2>&1 || useradd --create-home --shell /bin/bash gaia
install -d -m 700 -o gaia -g gaia /home/gaia/.ssh
KEYS=/home/gaia/.ssh/authorized_keys
touch "$KEYS"
grep -qxF "$NODE_KEY" "$KEYS" || echo "$NODE_KEY" >> "$KEYS"
chown gaia:gaia "$KEYS"; chmod 600 "$KEYS"
KEY_FP=$(ssh-keygen -l -f "$KEYS" 2>/dev/null | awk 'NR==1{print $2}')

# 2. what is needed from the package shelf (a failure here is written down, not fatal)
$APT update >/dev/null 2>&1
$APT install sudo ufw unattended-upgrades >/dev/null 2>&1 || echo "some packages could not be installed"

# 3. sudo for gaia
if command -v visudo >/dev/null 2>&1; then
  echo 'gaia ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/gaia-new
  chmod 440 /etc/sudoers.d/gaia-new
  if visudo -cf /etc/sudoers.d/gaia-new >/dev/null 2>&1; then mv /etc/sudoers.d/gaia-new /etc/sudoers.d/90-gaia; else rm -f /etc/sudoers.d/gaia-new; fi
fi

# 4. SSH: keys only. Done only once the key is in place, and undone if sshd does not accept the settings.
SSH_PASSWORDS=unchanged; ROOT_LOGIN=unchanged
if [ -n "$KEY_FP" ]; then
  mkdir -p /etc/ssh/sshd_config.d /run/sshd
  grep -qE '^[[:space:]]*Include[[:space:]]+/etc/ssh/sshd_config\.d/' /etc/ssh/sshd_config || sed -i '1i Include /etc/ssh/sshd_config.d/*.conf' /etc/ssh/sshd_config
  printf '%s\n' '# gaia node profile: keys only' 'PubkeyAuthentication yes' 'PasswordAuthentication no' 'KbdInteractiveAuthentication no' 'PermitRootLogin prohibit-password' > /etc/ssh/sshd_config.d/00-gaia.conf
  if /usr/sbin/sshd -t; then
    if command -v systemctl >/dev/null 2>&1; then systemctl try-reload-or-restart ssh 2>/dev/null || systemctl try-reload-or-restart sshd 2>/dev/null || true; fi
  else
    rm -f /etc/ssh/sshd_config.d/00-gaia.conf; echo "sshd did not accept the new settings; SSH is left as it was"
  fi
  SSH_PASSWORDS=$(/usr/sbin/sshd -T 2>/dev/null | awk '$1=="passwordauthentication"{print $2}')
  ROOT_LOGIN=$(/usr/sbin/sshd -T 2>/dev/null | awk '$1=="permitrootlogin"{print $2}')
fi

# 5. the firewall: 22 is allowed before anything is closed
FIREWALL=none
if command -v ufw >/dev/null 2>&1; then
  ufw allow 22/tcp >/dev/null && ufw allow 80/tcp >/dev/null && ufw allow 443/tcp >/dev/null \
    && ufw default deny incoming >/dev/null && ufw default allow outgoing >/dev/null && ufw --force enable >/dev/null
  ufw status 2>/dev/null | grep -q '^Status: active' && FIREWALL=active || FIREWALL=inactive
fi

# 6. security updates
UPDATES=off
if [ -d /etc/apt/apt.conf.d ] && dpkg -s unattended-upgrades >/dev/null 2>&1; then
  printf '%s\n' 'APT::Periodic::Update-Package-Lists "1";' 'APT::Periodic::Unattended-Upgrade "1";' > /etc/apt/apt.conf.d/20auto-upgrades
  UPDATES=on
fi

# 7. what was done, for Gaia to read
mkdir -p /etc/gaia
OS=$(. /etc/os-release 2>/dev/null; echo "${PRETTY_NAME:-unknown}")
SUDO=no; [ -f /etc/sudoers.d/90-gaia ] && SUDO=yes
cat > /etc/gaia/node.json <<EOF
{"profile": $PROFILE, "made": "$(date -u +%Y-%m-%dT%H:%M:%SZ)", "os": "$OS", "user": "gaia", "sudo": "$SUDO", "key_fp": "$KEY_FP",
 "ssh_passwords": "$SSH_PASSWORDS", "root_login": "$ROOT_LOGIN", "firewall": "$FIREWALL", "updates": "$UPDATES"}
EOF
chmod 644 /etc/gaia/node.json
cat /etc/gaia/node.json
echo "== done"
exit 0
