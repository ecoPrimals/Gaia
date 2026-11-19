#!/usr/bin/env python3
"""Drain port forward torpedoes via eastGate -> Router SSH chain"""

import paramiko
import sys

EASTGATE_IP = "192.168.1.131"
EASTGATE_USER = "eastgate"
EASTGATE_PASS = "eastgate"
ROUTER_IP = "192.168.4.1"
ROUTER_USER = "root"
ROUTER_PASS = "ExoticPanda714!!"

def ssh_exec(client, cmd, timeout=10):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    return out, err

def main():
    print("=== STEP 1: Connecting to eastGate ===")
    east = paramiko.SSHClient()
    east.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    east.connect(EASTGATE_IP, username=EASTGATE_USER, password=EASTGATE_PASS, timeout=10)
    print("CONNECTED to eastGate!")

    out, _ = ssh_exec(east, "hostname; uptime")
    print(f"  {out}")

    print("\n=== STEP 2: Router SSH check ===")
    out, _ = ssh_exec(east, "ping -c 1 -W 2 192.168.4.1 2>&1 | tail -1")
    print(f"  Router ping: {out}")

    # Check router SSH port
    out, _ = ssh_exec(east, "nc -z -w 3 192.168.4.1 22 && echo OPEN || echo CLOSED")
    print(f"  Router SSH port 22: {out}")

    print("\n=== STEP 3: SSH to Router via tunnel ===")
    transport = east.get_transport()
    try:
        channel = transport.open_channel("direct-tcpip", (ROUTER_IP, 22), ("127.0.0.1", 0))
        router = paramiko.SSHClient()
        router.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        router.connect(ROUTER_IP, username=ROUTER_USER, password=ROUTER_PASS,
                      sock=channel, timeout=10)
        print("CONNECTED to Router!")

        out, _ = ssh_exec(router, "uname -a")
        print(f"  Router: {out}")

        print("\n=== STEP 4: Current port forwards ===")
        out, _ = ssh_exec(router, "uci show firewall | grep redirect")
        if out:
            for line in out.split("\n"):
                print(f"  {line}")
        else:
            print("  No redirect rules via uci")
            out, _ = ssh_exec(router, "iptables -t nat -L PREROUTING -n --line-numbers 2>/dev/null | head -20")
            print(f"  iptables NAT: {out}")

        print("\n=== STEP 5: DRAINING TORPEDOES ===")
        out, _ = ssh_exec(router, "uci show firewall | grep '@redirect'")
        if out:
            lines = out.split("\n")
            names = [l for l in lines if ".name=" in l]
            ports = [l for l in lines if ".dest_port=" in l or ".src_dport=" in l]
            
            print(f"  Found {len(names)} redirect rules:")
            for n in names:
                print(f"    {n}")
            for p in ports:
                print(f"    {p}")

            # Count redirects
            out2, _ = ssh_exec(router, "uci show firewall | grep '@redirect' | grep '.name=' | wc -l")
            count = int(out2.strip()) if out2.strip().isdigit() else 0
            print(f"\n  Total redirects to drain: {count}")

            if count > 0:
                # Delete all redirects (from last to first)
                for i in range(count - 1, -1, -1):
                    name_out, _ = ssh_exec(router, f"uci get firewall.@redirect[{i}].name 2>/dev/null")
                    print(f"  Draining [{i}]: {name_out}")
                    ssh_exec(router, f"uci delete firewall.@redirect[{i}]")

                print("\n  Committing firewall changes...")
                out, err = ssh_exec(router, "uci commit firewall")
                print(f"  Commit: {out or 'OK'} {err}")

                print("  Reloading firewall...")
                out, err = ssh_exec(router, "/etc/init.d/firewall reload", timeout=15)
                print(f"  Reload: {out or 'OK'} {err}")

                print("\n=== VERIFICATION ===")
                out, _ = ssh_exec(router, "uci show firewall | grep redirect")
                if out:
                    print(f"  Remaining: {out}")
                else:
                    print("  ALL TORPEDOES DRAINED!")

                out, _ = ssh_exec(router, "iptables -t nat -L PREROUTING -n 2>/dev/null | head -10")
                print(f"  NAT PREROUTING: {out}")
        else:
            print("  No redirect rules found!")
            out, _ = ssh_exec(router, "iptables -t nat -L -n 2>/dev/null | grep -i dnat | head -10")
            if out:
                print(f"  Active DNAT rules: {out}")
            else:
                print("  No DNAT rules either - already clean?")

        router.close()

    except Exception as e:
        print(f"  Router connection error: {e}")
        print("\n  Trying sshpass from eastGate...")
        out, err = ssh_exec(east, "which sshpass 2>/dev/null && echo FOUND || echo NOTFOUND")
        if "FOUND" in out:
            out, _ = ssh_exec(east, f"sshpass -p '{ROUTER_PASS}' ssh -o StrictHostKeyChecking=no {ROUTER_USER}@{ROUTER_IP} 'uci show firewall | grep redirect' 2>/dev/null")
            print(f"  Via sshpass: {out}")
        else:
            print(f"  sshpass not available: {out}")

    print("\n=== STEP 6: Tor status on eastGate ===")
    out, _ = ssh_exec(east, "systemctl is-active tor 2>/dev/null")
    print(f"  Tor service: {out}")
    out, _ = ssh_exec(east, "ss -tlnp 2>/dev/null | grep -E ':9050|:9051|:80 |:443 |:8080 |:8443 ' | head -10")
    print(f"  Key listeners:\n{out}")

    east.close()
    print("\n=== COMPLETE ===")

if __name__ == "__main__":
    main()
