#!/usr/bin/env python3
"""Clean remaining iptables rules and verify the lake is balanced"""

import paramiko
import sys

EASTGATE_IP = "192.168.1.131"
EASTGATE_USER = "eastgate"
EASTGATE_PASS = "eastgate"
ROUTER_IP = "192.168.4.1"
ROUTER_USER = "root"
ROUTER_PASS = "***"

def ssh_exec(client, cmd, timeout=10):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    return out, err

def main():
    east = paramiko.SSHClient()
    east.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    east.connect(EASTGATE_IP, username=EASTGATE_USER, password=EASTGATE_PASS, timeout=10)
    print("Connected to eastGate")

    transport = east.get_transport()
    channel = transport.open_channel("direct-tcpip", (ROUTER_IP, 22), ("127.0.0.1", 0))
    router = paramiko.SSHClient()
    router.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    router.connect(ROUTER_IP, username=ROUTER_USER, password=ROUTER_PASS,
                  sock=channel, timeout=10)
    print("Connected to Router\n")

    # Check remaining NAT PREROUTING rules
    print("=== CURRENT NAT PREROUTING ===")
    out, _ = ssh_exec(router, "iptables -t nat -L PREROUTING -n --line-numbers 2>/dev/null")
    print(out)

    # The DNS redirects (53 -> 192.168.9.1) are from the router's DNS policy
    # Port 80 -> .244 might be from miniupnpd or a DMZ setting
    
    print("\n=== CHECKING MINIUPNPD RULES ===")
    out, _ = ssh_exec(router, "iptables -t nat -L MINIUPNPD -n --line-numbers 2>/dev/null")
    print(out or "(no MINIUPNPD chain)")

    print("\n=== CHECKING DMZ SETTINGS ===")
    out, _ = ssh_exec(router, "uci show firewall | grep -i dmz 2>/dev/null")
    print(out or "(no DMZ settings)")
    
    out, _ = ssh_exec(router, "uci show glconfig 2>/dev/null | grep -i dmz")
    print(out or "(no GL DMZ)")

    print("\n=== DNS INTERCEPT RULES ===")
    # These DNS rules redirect all port 53 traffic to the router's dnsmasq
    # This is the DNS filtering feature — may be intentional
    out, _ = ssh_exec(router, "uci show dhcp | grep -E 'dns|server|rebind' | head -10")
    print(out or "(none)")
    
    print("\n=== ADGUARD / DNS FILTERING ===")
    out, _ = ssh_exec(router, "uci show adguardhome 2>/dev/null | head -5")
    print(out or "(no adguardhome)")
    out, _ = ssh_exec(router, "ps | grep -E 'adguard|dnsmasq|pihole' | grep -v grep")
    print(out or "(no dns filter processes)")

    # Remove the port 80 DNAT to eastGate (from miniupnpd or other source)
    print("\n=== REMOVING PORT 80 DNAT RULES ===")
    # Find and delete port 80 rules pointing to eastGate
    out, _ = ssh_exec(router, "iptables -t nat -L PREROUTING -n --line-numbers 2>/dev/null | grep '192.168.4.244'")
    if out:
        print(f"Found eastGate DNAT rules:\n{out}")
        # Delete in reverse order
        lines = out.strip().split("\n")
        rule_nums = []
        for line in lines:
            num = line.split()[0]
            if num.isdigit():
                rule_nums.append(int(num))
        for num in sorted(rule_nums, reverse=True):
            print(f"  Deleting rule {num}...")
            ssh_exec(router, f"iptables -t nat -D PREROUTING {num}")
    else:
        print("No eastGate DNAT rules found in PREROUTING")

    # Don't touch the DNS rules — they're the router's DNS policy
    print("\n=== DNS RULES (keeping — router DNS policy) ===")
    out, _ = ssh_exec(router, "iptables -t nat -L PREROUTING -n 2>/dev/null | grep ':53'")
    print(f"DNS rules: {out}")
    print("(These redirect DNS to router's own DNS server — keeping for clean DNS)")

    # Final verification
    print("\n=== FINAL NAT PREROUTING ===")
    out, _ = ssh_exec(router, "iptables -t nat -L PREROUTING -n --line-numbers 2>/dev/null")
    print(out)

    # Check if port forwards are still active from WAN
    print("\n=== ROUTER LISTENING PORTS ===")
    out, _ = ssh_exec(router, "netstat -tlnp 2>/dev/null | grep -E ':80|:443|:8080|:22' | head -10")
    print(out or "(none)")

    # Enable SSH access from WAN (so we can manage remotely)
    print("\n=== ENABLING SSH ON WAN SIDE ===")
    out, _ = ssh_exec(router, "uci show dropbear 2>/dev/null")
    print(f"Dropbear config: {out}")
    
    # Check if SSH is restricted to LAN
    out, _ = ssh_exec(router, "uci get dropbear.@dropbear[0].Interface 2>/dev/null")
    if out and out != "":
        print(f"SSH restricted to interface: {out}")
        print("Opening SSH to all interfaces...")
        ssh_exec(router, "uci delete dropbear.@dropbear[0].Interface 2>/dev/null")
        ssh_exec(router, "uci commit dropbear")
        ssh_exec(router, "/etc/init.d/dropbear restart")
        print("SSH should now be accessible on all interfaces")
    else:
        print("SSH already accessible on all interfaces")

    router.close()
    east.close()
    print("\n=== LAKE BALANCED ===")

if __name__ == "__main__":
    main()
