#!/usr/bin/env python3
"""
PUSH LIVE - sync with eastGate's Forgejo, then push.

No credential lives in this file or in any remote URL. Git Credential Manager
holds it. The wire (192.168.4.248) is tried first; if it is dark, the Wi-Fi
face (192.168.1.103) is used. Override with GAIA_FORGE_HOST.
"""
import os
import socket
import subprocess
import sys

FACES = [os.environ["GAIA_FORGE_HOST"]] if os.environ.get("GAIA_FORGE_HOST") else ["192.168.4.248", "192.168.1.103"]
TARGET_PATH = "/gaia/Gaia.git"
BRANCH = sys.argv[1] if len(sys.argv) > 1 else "main"
ENV = dict(os.environ, GIT_MERGE_AUTOEDIT="no", GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")


def up(host, port=3000, timeout=2.5):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def run(args, label):
    print(f"--- {label} ---")
    r = subprocess.run(args, capture_output=True, text=True, env=ENV)
    print((r.stdout + r.stderr).strip() or "(no output)")
    return r.returncode


host = next((h for h in FACES if up(h)), None)
if not host:
    print("  eastGate's forge is dark on every face: " + ", ".join(FACES))
    sys.exit(2)

url = f"http://{host}:3000{TARGET_PATH}"
print(f"=== PUSH LIVE -> {url} ({BRANCH}) ===")
if run(["git", "pull", url, BRANCH, "--no-rebase", "--no-edit"], "sync (pull)") != 0:
    print("  pull failed - not pushing. Resolve the above first.")
    sys.exit(1)
rc = run(["git", "push", url, BRANCH], "push")
print("\n  PUSHED. eastGate Forgejo has it." if rc == 0 else "\n  push failed - see output above.")
sys.exit(rc)
