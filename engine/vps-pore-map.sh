#!/bin/bash
echo "═══ PORE MAP — ALL PORTS = APERTURES ═══"
ss -tlnp | tail -n +2
echo ""
echo "═══ SERVICES ═══"
systemctl list-units --type=service --state=active --no-pager | grep -E "caddy|tor|stalwart|forgejo|cloudflared|code-server|ntfy|knot|ssh"
echo ""
echo "═══ DISK MASS ═══"
du -sh /opt/* 2>/dev/null | sort -rh
echo ""
echo "═══ REMAINING MASS ═══"
du -sh /opt/ /var/ /root/ /etc/ /usr/lib/code-server 2>/dev/null | sort -rh
echo ""
echo "═══ TOTAL ═══"
df -h / | tail -1
