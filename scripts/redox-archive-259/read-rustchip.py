import paramiko
DA = {'keys': ['rsa-sha2-256', 'rsa-sha2-512']}
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10,
          look_for_keys=False, allow_agent=False, disabled_algorithms=DA, banner_timeout=15)

def run(cmd, t=15):
    _, o, e = c.exec_command(cmd, timeout=t)
    return o.read().decode().strip(), e.read().decode().strip()

RCHIP = "/home/eastgate/Development/ecoPrimals/springs/rustChip"

print("=== rustChip/ — OUR OWN SILICON ===\n")

out, _ = run(f"ls -la {RCHIP}/")
print(f"ROOT:\n{out}\n")

out, _ = run(f"find {RCHIP} -type f | head -40")
print(f"FILES:\n{out}\n")

out, _ = run(f"cat {RCHIP}/README.md 2>/dev/null || cat {RCHIP}/readme.md 2>/dev/null || echo 'no README'")
print(f"README:\n{out}\n")

out, _ = run(f"cat {RCHIP}/Cargo.toml 2>/dev/null || echo 'no Cargo.toml'")
print(f"Cargo.toml:\n{out}\n")

# Check src
out, _ = run(f"find {RCHIP}/src -name '*.rs' 2>/dev/null | head -20")
print(f"Rust source:\n{out}\n")

# Read main lib/main
out, _ = run(f"cat {RCHIP}/src/main.rs 2>/dev/null | head -60")
print(f"main.rs:\n{out}\n")

out, _ = run(f"cat {RCHIP}/src/lib.rs 2>/dev/null | head -60")
print(f"lib.rs:\n{out}\n")

# Also check brainchip
print("\n=== brainchip_devhub ===")
BCHIP = "/home/eastgate/Development/ecoPrimals/springs/brainchip_devhub"
out, _ = run(f"ls {BCHIP}/ 2>/dev/null | head -20")
print(f"Contents: {out}")

out, _ = run(f"cat {BCHIP}/README.md 2>/dev/null | head -30")
print(f"README:\n{out}")

print("\n=== brainchip_models ===")
BMOD = "/home/eastgate/Development/ecoPrimals/springs/brainchip_models"
out, _ = run(f"ls {BMOD}/ 2>/dev/null | head -20")
print(f"Contents: {out}")

c.close()
