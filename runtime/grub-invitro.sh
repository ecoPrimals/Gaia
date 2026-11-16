#!/usr/bin/env bash
# In-vitro GRUB test: QEMU + OVMF, no real hardware touched.
# Usage (WSL, root): bash grub-invitro.sh <esp_tools_dir> <out_dir>
#   esp_tools_dir: copy of Z:\EFI\tools (modGRUBShell.efi, grub.cfg)
set -euo pipefail
SRC=$1; OUT=$2
W=$(mktemp -d); mkdir -p "$OUT"
OVMF_CODE=/usr/share/OVMF/OVMF_CODE_4M.fd
OVMF_VARS=/usr/share/OVMF/OVMF_VARS_4M.fd

# Embedded loader: prefer the ESP menu (editable from Windows), never strand at grub>.
cat > "$W/embed.cfg" <<'EOF'
insmod part_gpt
insmod fat
insmod chain
if search --set=esp --file /EFI/tools/grub.cfg; then
    set root=$esp
    configfile /EFI/tools/grub.cfg
fi
set timeout=8
set default=0
menuentry "Windows (built-in fallback)" {
    search --set=root --file /EFI/Microsoft/Boot/bootmgfw.efi
    chainloader /EFI/Microsoft/Boot/bootmgfw.efi
}
menuentry "HUMAN: enter UEFI setup" {
    fwsetup
}
EOF
MODS="part_gpt part_msdos fat chain search search_fs_file configfile normal echo test efi_gop efi_uga all_video font gfxterm"
grub-mkstandalone -O x86_64-efi --modules="$MODS" -o "$OUT/gaia-grub.efi" \
    "boot/grub/grub.cfg=$W/embed.cfg"

# Fake Windows boot manager: a GRUB that only paints a banner.
cat > "$W/stub.cfg" <<'EOF'
echo "=================================="
echo "  HANDOFF-OK: bootmgfw.efi reached"
echo "=================================="
sleep 600
EOF
grub-mkstandalone -O x86_64-efi --modules="echo sleep" -o "$W/bootmgfw.efi" \
    "boot/grub/grub.cfg=$W/stub.cfg"

mkesp() { # $1=image $2=BOOTX64 source $3=include ESP menu (1/0)
    rm -f "$1"; mkfs.fat -C -F 32 "$1" 65536 >/dev/null
    mmd -i "$1" ::/EFI ::/EFI/BOOT ::/EFI/tools ::/EFI/Microsoft ::/EFI/Microsoft/Boot
    mcopy -i "$1" "$2" ::/EFI/BOOT/BOOTX64.EFI
    mcopy -i "$1" "$W/bootmgfw.efi" ::/EFI/Microsoft/Boot/bootmgfw.efi
    [ "$3" = 1 ] && mcopy -i "$1" "$SRC/grub.cfg" ::/EFI/tools/grub.cfg
    return 0
}

shot() { # $1=monitor socket $2=name
    echo "screendump $W/$2.ppm" | socat - UNIX-CONNECT:"$1" >/dev/null
    sleep 1
    python3 - "$W/$2.ppm" "$OUT/$2.png" <<'PY'
import sys, zlib, struct
d = open(sys.argv[1], 'rb').read()
parts = d.split(maxsplit=4); w, h = int(parts[1]), int(parts[2]); px = parts[4]
raw = b''.join(b'\0' + px[y*w*3:(y+1)*w*3] for y in range(h))
c = lambda t, b: struct.pack('>I', len(b)) + t + b + struct.pack('>I', zlib.crc32(t + b))
open(sys.argv[2], 'wb').write(b'\x89PNG\r\n\x1a\n' + c(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + c(b'IDAT', zlib.compress(raw)) + c(b'IEND', b''))
PY
}

run() { # $1=name $2=image $3..=schedule of "sec:action" (shot / key:<qemu key>)
    local name=$1 img=$2; shift 2
    local mon=$W/$name.sock
    cp "$OVMF_VARS" "$W/$name.vars"
    qemu-system-x86_64 -machine q35 -m 512 -display none -vga std \
        -drive if=pflash,format=raw,readonly=on,file="$OVMF_CODE" \
        -drive if=pflash,format=raw,file="$W/$name.vars" \
        -drive format=raw,file="$img" -net none \
        -monitor unix:"$mon",server,nowait &
    local pid=$! t=0
    for step in "$@"; do
        local at=${step%%:*} act=${step#*:}
        sleep $((at - t)); t=$at
        if [ "$act" = shot ]; then shot "$mon" "$name-${at}s"
        else echo "sendkey ${act#key:}" | socat - UNIX-CONNECT:"$mon" >/dev/null; fi
    done
    kill $pid 2>/dev/null; wait $pid 2>/dev/null || true
}

command -v socat >/dev/null || apt-get install -y -qq socat >/dev/null

# A: the shell that is on the ESP today.
mkesp "$W/a.img" "$SRC/modGRUBShell.efi" 1
run A-modshell "$W/a.img" 12:shot 25:shot

# B: Gaia GRUB + ESP menu, untouched -> timeout should hand off to Windows.
mkesp "$W/b.img" "$OUT/gaia-grub.efi" 1
run B-gaia-default "$W/b.img" 8:shot 22:shot

# C: Gaia GRUB with the ESP menu missing -> built-in fallback, not grub>.
mkesp "$W/c.img" "$OUT/gaia-grub.efi" 0
run C-gaia-nocfg "$W/c.img" 8:shot 22:shot

# D: human picks "UEFI setup" -> firmware setup screen.
run D-gaia-fwsetup "$W/b.img" 7:key:down 8:key:ret 14:shot

sha256sum "$OUT/gaia-grub.efi"
ls "$OUT"
