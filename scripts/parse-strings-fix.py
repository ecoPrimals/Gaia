#!/usr/bin/env python3
"""Fix string parsing — extract all UTF-16LE strings from the string packages."""
import struct, json

data = open(r'c:\Users\mokke\Desktop\Gaia\data\gut\setup-pe32-body.bin', 'rb').read()

# String packages from the parser output
string_ranges = [
    (0x670B8 + 4, 0x670B8 + 343463),
    (0xBAE5F + 4, 0xBAE5F + 214320),
    (0xEF38F + 4, 0xEF38F + 75956),
]

print("=== STRING EXTRACTION ===")

# First, let's just look at the raw bytes at the start of the first string package
str_start = 0x670B8 + 4
print(f"\nFirst string package header at 0x{str_start:X}:")
for off in range(0, 64, 16):
    hex_str = ' '.join(f'{data[str_start+off+j]:02X}' for j in range(16))
    ascii_str = ''.join(chr(data[str_start+off+j]) if 32 <= data[str_start+off+j] <= 126 else '.'
                       for j in range(16))
    print(f"  0x{str_start+off:06X}: {hex_str}  {ascii_str}")

# HII String Package Header:
# UINT32 HdrSize
# UINT32 StringInfoOffset  
# UINT16 LanguageWindow[16] (32 bytes)
# EFI_STRING LanguageName
# CHAR8 Language[]

hdr_size = struct.unpack('<I', data[str_start:str_start+4])[0]
str_info_off = struct.unpack('<I', data[str_start+4:str_start+8])[0]
print(f"\nHdrSize: {hdr_size}")
print(f"StringInfoOffset: {str_info_off}")

# Language is at offset 40 (after 8 bytes + 16*2 bytes window)
lang_off = str_start + 40
print(f"Language bytes at 0x{lang_off:X}:")
lang_bytes = data[lang_off:lang_off+20]
print(f"  {lang_bytes.hex()}")
print(f"  {lang_bytes}")

# Actually the Language is null-terminated ASCII string at the end of the header
# Find it by looking for "en" or "x-" pattern
for off in range(40, hdr_size):
    b = data[str_start + off]
    if b == ord('e') and data[str_start+off+1] == ord('n'):
        lang = data[str_start+off:data.find(b'\x00', str_start+off)].decode()
        print(f"  Language found at +{off}: '{lang}'")
        break
    elif b == ord('x') and data[str_start+off+1] == ord('-'):
        lang = data[str_start+off:data.find(b'\x00', str_start+off)].decode()
        print(f"  Language found at +{off}: '{lang}'")
        break

# Now parse string blocks from StringInfoOffset
str_table = {}
si = str_start + str_info_off
sid = 0
max_offset = str_start + 343463
print(f"\nParsing strings from 0x{si:X}...")
print(f"First bytes: {data[si:si+16].hex()}")

errors = 0
while si < max_offset - 1 and errors < 5:
    block_type = data[si]
    
    if block_type == 0x00:  # END
        print(f"  End block at 0x{si:X}, sid={sid}")
        break
    elif block_type == 0x21:  # EFI_HII_SIBT_STRING_UCS2
        si += 1
        sid += 1
        end = si
        while end < max_offset - 1:
            if data[end] == 0x00 and data[end+1] == 0x00:
                break
            end += 2
        s = data[si:end].decode('utf-16-le', errors='replace')
        str_table[sid] = s
        si = end + 2
    elif block_type == 0x20:  # SIBT_STRING_SCSU (simple ASCII)
        si += 1
        sid += 1
        end = data.find(b'\x00', si, min(si+2000, max_offset))
        if end < 0:
            errors += 1
            si += 1
            continue
        s = data[si:end].decode('ascii', errors='replace')
        str_table[sid] = s
        si = end + 1
    elif block_type == 0x22:  # SIBT_STRING_UCS2_FONT
        font_id = data[si+1]
        si += 2
        sid += 1
        end = si
        while end < max_offset - 1:
            if data[end] == 0x00 and data[end+1] == 0x00:
                break
            end += 2
        s = data[si:end].decode('utf-16-le', errors='replace')
        str_table[sid] = s
        si = end + 2
    elif block_type == 0x30:  # SIBT_SKIP1
        count = data[si+1]
        sid += count
        si += 2
    elif block_type == 0x31:  # SIBT_SKIP2
        count = struct.unpack('<H', data[si+1:si+3])[0]
        sid += count
        si += 3
    elif block_type == 0x10:  # SIBT_STRINGS_SCSU (multiple strings)
        count = struct.unpack('<H', data[si+1:si+3])[0]
        si += 3
        for _ in range(count):
            sid += 1
            end = data.find(b'\x00', si, min(si+2000, max_offset))
            if end < 0:
                break
            s = data[si:end].decode('ascii', errors='replace')
            str_table[sid] = s
            si = end + 1
    elif block_type == 0x11:  # SIBT_STRINGS_UCS2 (multiple UCS2 strings)
        count = struct.unpack('<H', data[si+1:si+3])[0]
        si += 3
        for _ in range(count):
            sid += 1
            end = si
            while end < max_offset - 1:
                if data[end] == 0x00 and data[end+1] == 0x00:
                    break
                end += 2
            s = data[si:end].decode('utf-16-le', errors='replace')
            str_table[sid] = s
            si = end + 2
    elif block_type == 0x12:  # SIBT_STRING_SCSU_FONT
        font_id = data[si+1]
        si += 2
        sid += 1
        end = data.find(b'\x00', si, min(si+2000, max_offset))
        if end < 0:
            break
        s = data[si:end].decode('ascii', errors='replace')
        str_table[sid] = s
        si = end + 1
    else:
        print(f"  Unknown block type 0x{block_type:02X} at 0x{si:X} (sid={sid})")
        print(f"  Context: {data[si:si+16].hex()}")
        errors += 1
        si += 1

print(f"\nTotal strings extracted: {len(str_table)}")

# Show critical strings
print("\n=== CRITICAL STRINGS ===")
for sid, s in sorted(str_table.items()):
    if any(kw in s for kw in ['Above 4G', 'SMT', 'CCD', 'iGPU', 'UMA', 'Resizable',
                               'Fast Boot', 'IOMMU', 'SVM', 'AMD CBS', 'NVMe', 'PCIe',
                               'Core Perf', 'Re-Size', 'Hyper', 'Thread', 'ReBAR',
                               'M.2', 'Integrated', 'Above4G']):
        print(f"  #{sid}: \"{s}\"")

# Save
with open(r'c:\Users\mokke\Desktop\Gaia\data\gut\ifr-strings.json', 'w') as f:
    json.dump(str_table, f, indent=2, ensure_ascii=False)
print(f"\nSaved {len(str_table)} strings to ifr-strings.json")
