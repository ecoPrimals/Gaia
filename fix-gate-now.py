#!/usr/bin/env python3
"""FIX THE GATE NOW — restore from backup, patch runtime copy correctly."""
import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15)

# Check if runtime/gaia_gate.pi is a symlink
print("=== RUNTIME PATH ===")
stdin, stdout, stderr = ssh.exec_command('ls -la /opt/Gaia/runtime/gaia_gate.pi /opt/Gaia/gaia_gate.pi')
print(stdout.read().decode().strip())
stdin, stdout, stderr = ssh.exec_command('readlink -f /opt/Gaia/runtime/gaia_gate.pi')
real_runtime = stdout.read().decode().strip()
print(f"Real runtime path: {real_runtime}")

# Check line 1536 of the runtime file
print("\n=== RUNTIME LINE 1536 ===")
stdin, stdout, stderr = ssh.exec_command('sed -n "1530,1545p" /opt/Gaia/runtime/gaia_gate.pi')
print(stdout.read().decode())

# Check if runtime is a symlink to gaia_gate.pi
stdin, stdout, stderr = ssh.exec_command('md5sum /opt/Gaia/runtime/gaia_gate.pi /opt/Gaia/gaia_gate.pi /opt/Gaia/gaia_gate.pi.bak.259 2>/dev/null')
print(f"MD5 comparison:\n{stdout.read().decode().strip()}")

# STEP 1: Restore the base file from backup
print("\n=== RESTORE FROM BACKUP ===")
stdin, stdout, stderr = ssh.exec_command('cp /opt/Gaia/gaia_gate.pi.bak.259 /opt/Gaia/gaia_gate.pi')
stdout.read()
print("Restored /opt/Gaia/gaia_gate.pi from backup")

# Check if runtime is the same file or separate
stdin, stdout, stderr = ssh.exec_command('stat -c "%i" /opt/Gaia/runtime/gaia_gate.pi /opt/Gaia/gaia_gate.pi 2>/dev/null')
inodes = stdout.read().decode().strip().split('\n')
print(f"Inodes: runtime={inodes[0] if len(inodes)>0 else '?'}, base={inodes[1] if len(inodes)>1 else '?'}")

same_file = len(inodes) >= 2 and inodes[0] == inodes[1]
print(f"Same inode: {same_file}")

if not same_file:
    # They're different files — check if runtime was also corrupted
    stdin, stdout, stderr = ssh.exec_command('python3 -c "compile(open(\'/opt/Gaia/runtime/gaia_gate.pi\').read(), \'runtime\', \'exec\')" 2>&1')
    runtime_check = stdout.read().decode().strip() + stderr.read().decode().strip()
    print(f"Runtime syntax: {runtime_check or 'OK'}")
    
    if 'SyntaxError' in runtime_check:
        # Runtime was also corrupted — but it was working before, so let's check the backup
        stdin, stdout, stderr = ssh.exec_command('python3 -c "compile(open(\'/opt/Gaia/gaia_gate.pi.bak.259\').read(), \'backup\', \'exec\')" 2>&1')
        backup_check = stdout.read().decode().strip() + stderr.read().decode().strip()
        print(f"Backup syntax: {backup_check or 'OK'}")
        
        if not backup_check or 'OK' in backup_check or not 'SyntaxError' in backup_check:
            # Backup is clean — but runtime is separate, maybe it was already broken?
            # Check if there's a git version
            stdin, stdout, stderr = ssh.exec_command('cd /opt/Gaia && git diff runtime/gaia_gate.pi 2>/dev/null | head -30')
            diff = stdout.read().decode().strip()
            if diff:
                print(f"Git diff on runtime:\n{diff[:500]}")
            
            # Try to restore runtime from git
            stdin, stdout, stderr = ssh.exec_command('cd /opt/Gaia && git checkout runtime/gaia_gate.pi 2>&1')
            git_restore = stdout.read().decode().strip() + stderr.read().decode().strip()
            print(f"Git restore runtime: {git_restore}")
            
            # Check syntax again
            stdin, stdout, stderr = ssh.exec_command('python3 -c "compile(open(\'/opt/Gaia/runtime/gaia_gate.pi\').read(), \'runtime\', \'exec\')" 2>&1')
            check2 = stdout.read().decode().strip() + stderr.read().decode().strip()
            print(f"Runtime syntax after git restore: {check2 or 'OK'}")

# STEP 2: Patch the CORRECT file (whichever the service uses)
print("\n=== PATCHING RUNTIME ===")
target = '/opt/Gaia/runtime/gaia_gate.pi'
stdin, stdout, stderr = ssh.exec_command(f'cat {target}')
gate = stdout.read().decode()

# First check syntax of current runtime
stdin, stdout, stderr = ssh.exec_command(f'python3 -c "compile(open(\'{target}\').read(), \'t\', \'exec\')" 2>&1')
check = stdout.read().decode().strip() + stderr.read().decode().strip()
if 'SyntaxError' in check:
    print(f"  Runtime still has syntax error: {check[:200]}")
    # Try just the base file
    target = '/opt/Gaia/gaia_gate.pi'
    stdin, stdout, stderr = ssh.exec_command(f'python3 -c "compile(open(\'{target}\').read(), \'t\', \'exec\')" 2>&1')
    check = stdout.read().decode().strip() + stderr.read().decode().strip()
    print(f"  Base file syntax: {check[:200] or 'OK'}")

if 'in.nestgate.io' not in gate:
    old_line = '            if host in ("nestgate.io","www.nestgate.io"): self._serve_static("nestgate.html"); return'
    new_block = '            if host in ("out.nestgate.io",): self._serve_static("outer-face.html"); return\n            if host in ("in.nestgate.io",): self._serve_static("senses.html"); return\n            if host in ("nestgate.io","www.nestgate.io"): self._serve_static("nestgate.html"); return'
    
    if old_line in gate:
        gate_new = gate.replace(old_line, new_block)
        # Verify syntax before writing
        try:
            compile(gate_new, 'test', 'exec')
            print("  Patch compiles OK locally")
        except SyntaxError as e:
            print(f"  ⚠ Patch has syntax error: {e}")
            print("  NOT patching — will just restore and restart")
            gate_new = None
        
        if gate_new:
            sftp = ssh.open_sftp()
            with sftp.file(target, 'w') as f:
                f.write(gate_new)
            sftp.close()
            
            # Verify on remote
            stdin, stdout, stderr = ssh.exec_command(f'python3 -c "compile(open(\'{target}\').read(), \'t\', \'exec\')" 2>&1')
            verify = stdout.read().decode().strip() + stderr.read().decode().strip()
            print(f"  Remote syntax after patch: {verify or 'OK'}")
    else:
        print(f"  Could not find expected line in {target}")
else:
    print(f"  Already patched in {target}")

# STEP 3: Restart
print("\n=== RESTART ===")
# Stop crash loop first
stdin, stdout, stderr = ssh.exec_command('systemctl --user stop gaia-gate 2>/dev/null; sudo systemctl stop gaia-gate 2>/dev/null')
stdout.read()
time.sleep(2)

# Start the system service (which has priority)
stdin, stdout, stderr = ssh.exec_command('sudo systemctl start gaia-gate 2>/dev/null; echo $?')
rc = stdout.read().decode().strip()
print(f"System start: exit {rc}")

time.sleep(3)

# Check if running
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://localhost:8443/pulse 2>/dev/null')
pulse = stdout.read().decode().strip()
print(f"Gate /pulse: {pulse}")

if pulse == '000' or pulse == '':
    # Try user service
    stdin, stdout, stderr = ssh.exec_command('systemctl --user start gaia-gate 2>/dev/null; echo $?')
    rc2 = stdout.read().decode().strip()
    print(f"User start: exit {rc2}")
    time.sleep(3)
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://localhost:8443/pulse 2>/dev/null')
    print(f"Gate /pulse: {stdout.read().decode().strip()}")

# Final test
print("\n=== FINAL TEST ===")
time.sleep(2)
for sub in ['out.nestgate.io', 'in.nestgate.io', 'nestgate.io', 'hud.primals.eco', 'primals.eco']:
    stdin, stdout, stderr = ssh.exec_command(f'curl -s -o /dev/null -w "%{{http_code}} %{{size_download}}" -H "Host: {sub}" http://localhost:8443/ 2>/dev/null')
    result = stdout.read().decode().strip()
    stdin, stdout, stderr = ssh.exec_command(f'curl -s -H "Host: {sub}" http://localhost:8443/ 2>/dev/null | grep -o "<title>[^<]*</title>" | head -1')
    title = stdout.read().decode().strip()
    print(f"  {sub:25s} → {result:15s} {title}")

ssh.close()
