#!/usr/bin/env python3
"""Inject walk-route and lake-balance into eastGate's persistent data"""

import paramiko
import json
import os

EASTGATE_IP = "192.168.4.244"
EASTGATE_USER = "eastgate"
EASTGATE_PASS = "eastgate"

def ssh_exec(client, cmd, timeout=10):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.read().decode("utf-8", errors="replace").strip()

def main():
    east = paramiko.SSHClient()
    east.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    east.connect(EASTGATE_IP, username=EASTGATE_USER, password=EASTGATE_PASS, timeout=10)
    print("Connected to eastGate at .244")

    # Find the data directory
    data_dir = ssh_exec(east, "ls -d /opt/Gaia/infra/hud/site/public/data/ 2>/dev/null || ls -d /opt/Gaia/hud/site/public/data/ 2>/dev/null || echo NOTFOUND")
    print(f"Data dir: {data_dir}")

    if data_dir == "NOTFOUND":
        data_dir = ssh_exec(east, "find /opt/Gaia -name 'now.json' -type f 2>/dev/null | head -1 | xargs dirname")
        print(f"Found data dir via now.json: {data_dir}")

    if not data_dir or data_dir == "NOTFOUND":
        print("Could not find data directory!")
        east.close()
        return

    # Read local walk-route.json and lake-balance.json
    walk_path = os.path.join(os.path.dirname(__file__), "walk-route.json")
    lake_path = os.path.join(os.path.dirname(__file__), "lake-balance.json")

    for local_file, remote_name in [(walk_path, "walk-route.json"), (lake_path, "lake-balance.json")]:
        if os.path.exists(local_file):
            with open(local_file, "r") as f:
                content = f.read()

            # Write to eastGate data directory via sftp
            sftp = east.open_sftp()
            remote_path = f"{data_dir}/{remote_name}"
            with sftp.open(remote_path, "w") as rf:
                rf.write(content)
            sftp.close()
            print(f"Injected {remote_name} -> {remote_path}")

            # Verify
            verify = ssh_exec(east, f"ls -la {remote_path}")
            print(f"  Verified: {verify}")
        else:
            print(f"Local file not found: {local_file}")

    # Also inject into the git-tracked data directory
    git_data = ssh_exec(east, "ls -d /opt/Gaia/data/ 2>/dev/null || echo NONE")
    if git_data != "NONE":
        print(f"\nGit data dir: {git_data}")
        sftp = east.open_sftp()
        for local_file, remote_name in [(walk_path, "walk-route.json"), (lake_path, "lake-balance.json")]:
            if os.path.exists(local_file):
                with open(local_file, "r") as f:
                    content = f.read()
                remote_path = f"{git_data}/{remote_name}"
                with sftp.open(remote_path, "w") as rf:
                    rf.write(content)
                print(f"Injected {remote_name} -> {remote_path}")
        sftp.close()

    # Check what's being served on the data endpoint
    print("\n=== VERIFY SERVED DATA ===")
    walk_served = ssh_exec(east, f"curl -s http://127.0.0.1:8080/data/walk-route.json 2>/dev/null | head -3")
    print(f"walk-route.json served: {walk_served[:100]}")
    lake_served = ssh_exec(east, f"curl -s http://127.0.0.1:8080/data/lake-balance.json 2>/dev/null | head -3")
    print(f"lake-balance.json served: {lake_served[:100]}")

    # Get current eastGate state
    print("\n=== EASTGATE CURRENT STATE ===")
    print(f"Uptime: {ssh_exec(east, 'uptime')}")
    print(f"IPs: {ssh_exec(east, 'ip addr show | grep inet\\ | grep -v 127.0.0.1')}")
    print(f"Tor: {ssh_exec(east, 'systemctl is-active tor')}")
    print(f"Crons running: {ssh_exec(east, 'crontab -l 2>/dev/null | grep -v ^# | wc -l')}")

    east.close()
    print("\n=== INJECTION COMPLETE ===")

if __name__ == "__main__":
    main()
