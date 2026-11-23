#!/usr/bin/env python3
"""REPACK v2 — Do the tar surgery LOCALLY on northGate, no upload needed."""
import tarfile, io, os, shutil

modgrub = r"Z:\EFI\tools\modGRUBShell.efi"
print(f"=== REPACK modGRUBShell LOCALLY ===\n")
print(f"  Source: {modgrub} ({os.path.getsize(modgrub)} bytes)")

with open(modgrub, 'rb') as f:
    efi_data = bytearray(f.read())

# Find ALL tar headers
tar_offset = None
idx = 0
found = 0
while True:
    pos = efi_data.find(b'ustar', idx)
    if pos == -1:
        break
    start = pos - 257
    found += 1
    if start >= 0:
        try:
            bio = io.BytesIO(bytes(efi_data[start:]))
            tf = tarfile.open(fileobj=bio)
            members = tf.getnames()
            cfg_members = [m for m in members if 'grub.cfg' in m]
            if cfg_members:
                tar_offset = start
                print(f"  FOUND memdisk at offset {start}")
                print(f"  Members: {len(members)} files")
                for m in cfg_members:
                    content = tf.extractfile(m).read().decode()
                    print(f"  Current grub.cfg ({m}):")
                    print(f"    {content[:200]}...")
                tf.close()
                break
            tf.close()
        except Exception as e:
            pass
    idx = pos + 1

print(f"  Scanned {found} 'ustar' markers")

if not tar_offset:
    print("\n  No memdisk with grub.cfg found!")
    print("  Trying alternative: put grub.cfg next to modGRUBShell.efi")
    
    # Write grub.cfg next to modGRUBShell — it checks $prefix/grub.cfg
    cfg = (
        "insmod setup_var\n"
        "\n"
        'echo ""\n'
        'echo "========================================"\n'
        'echo "  GAIA AUTO-SURGERY - Wave 233"\n'
        'echo "========================================"\n'
        'echo ""\n'
        'echo "Writing AMD_PBS_SETUP variables..."\n'
        'echo ""\n'
        "\n"
        "setup_var_cv AMD_PBS_SETUP 0x48 0x01 0x01\n"
        'echo "  [OK] iGPU (0x48) = 0x01 (Forces)"\n'
        "\n"
        "setup_var_cv AMD_PBS_SETUP 0x49 0x01 0x06\n"
        'echo "  [OK] UMA (0x49) = 0x06 (512M)"\n'
        "\n"
        'echo ""\n'
        'echo "Surgery complete! Booting Windows in 5s..."\n'
        "sleep 5\n"
        "\n"
        "search --set=root --file /EFI/Microsoft/Boot/bootmgfw.efi\n"
        "chainloader /EFI/Microsoft/Boot/bootmgfw.efi\n"
        "boot\n"
    )
    
    # Write to BOTH possible locations
    tools_cfg = r"Z:\EFI\tools\grub.cfg"
    with open(tools_cfg, 'w', newline='\n') as f:
        f.write(cfg)
    print(f"  Written: {tools_cfg}")
    
    # Also try (hd0,gpt1)/boot/grub/grub.cfg
    boot_grub = r"Z:\boot\grub"
    os.makedirs(boot_grub, exist_ok=True)
    with open(os.path.join(boot_grub, "grub.cfg"), 'w', newline='\n') as f:
        f.write(cfg)
    print(f"  Written: Z:\\boot\\grub\\grub.cfg")
    
    # Update GAIA Boot Engine to auto-chain to modGRUBShell
    gaia_cfg = (
        "# GAIA BOOT ENGINE - Auto-surgery chain\n"
        "set timeout=3\n"
        "set default=0\n"
        "\n"
        'menuentry "GAIA AUTO-SURGERY (iGPU + UMA)" {\n'
        "    chainloader /EFI/tools/modGRUBShell.efi\n"
        "}\n"
        "\n"
        'menuentry "Windows Boot Manager" {\n'
        "    chainloader /EFI/Microsoft/Boot/bootmgfw.efi\n"
        "}\n"
    )
    with open(r"Z:\EFI\gaia\grub.cfg", 'w', newline='\n') as f:
        f.write(gaia_cfg)
    print(f"  Updated: Z:\\EFI\\gaia\\grub.cfg (auto-chain, 3s)")
    
    print(f"\n  BOOT FLOW:")
    print(f"  1. GAIA Boot Engine loads (3s timeout)")
    print(f"  2. Auto-chains to modGRUBShell")
    print(f"  3. modGRUBShell drops to grub> prompt")
    print(f"  4. Type: normal")
    print(f"  5. Surgery config auto-executes")
    print(f"  6. Windows boots")
    print(f"\n  ONE WORD: normal")
    
else:
    # Extract and rebuild tar
    extract_dir = r"c:\Users\mokke\Desktop\Gaia\data\gut\memdisk"
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    
    bio = io.BytesIO(bytes(efi_data[tar_offset:]))
    tf = tarfile.open(fileobj=bio)
    tf.extractall(extract_dir)
    old_end = bio.tell()
    tf.close()
    
    # Write surgery config
    cfg = (
        "insmod setup_var\n"
        'echo "GAIA AUTO-SURGERY - Wave 233"\n'
        "setup_var_cv AMD_PBS_SETUP 0x48 0x01 0x01\n"
        'echo "iGPU = Forces"\n'
        "setup_var_cv AMD_PBS_SETUP 0x49 0x01 0x06\n"
        'echo "UMA = 512M"\n'
        'echo "Booting Windows..."\n'
        "sleep 3\n"
        "search --set=root --file /EFI/Microsoft/Boot/bootmgfw.efi\n"
        "chainloader /EFI/Microsoft/Boot/bootmgfw.efi\n"
        "boot\n"
    )
    
    cfg_path = os.path.join(extract_dir, 'boot', 'grub', 'grub.cfg')
    with open(cfg_path, 'w', newline='\n') as f:
        f.write(cfg)
    
    # Rebuild tar
    new_buf = io.BytesIO()
    new_tf = tarfile.open(fileobj=new_buf, mode='w')
    for root, dirs, files in os.walk(extract_dir):
        for d in sorted(dirs):
            full = os.path.join(root, d)
            arcname = os.path.relpath(full, extract_dir)
            new_tf.add(full, arcname=arcname, recursive=False)
        for fname in sorted(files):
            full = os.path.join(root, fname)
            arcname = os.path.relpath(full, extract_dir)
            new_tf.add(full, arcname=arcname)
    new_tf.close()
    new_tar = new_buf.getvalue()
    
    # Splice
    new_efi = bytearray()
    new_efi.extend(efi_data[:tar_offset])
    new_efi.extend(new_tar)
    if len(new_tar) < old_end:
        new_efi.extend(b'\x00' * (old_end - len(new_tar)))
    new_efi.extend(efi_data[tar_offset + old_end:])
    
    output = r"Z:\EFI\gaia\gaia-auto-surgery.efi"
    with open(output, 'wb') as f:
        f.write(bytes(new_efi))
    print(f"\n  REPACKED: {output} ({len(new_efi)} bytes)")
    print(f"  ZERO TYPING — boots and auto-writes vars")

print("\n=== DONE ===")
