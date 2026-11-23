#!/usr/bin/env python3
"""Look at hex around the Setup GUID and other key locations."""
import struct

data = open(r'c:\Users\mokke\Desktop\Gaia\data\gut\setup-pe32-body.bin', 'rb').read()

def hexdump(d, offset, length=128):
    for i in range(0, min(length, len(d)-offset), 16):
        hex_part = ' '.join(f'{d[offset+i+j]:02X}' for j in range(min(16, len(d)-offset-i)))
        ascii_part = ''.join(chr(d[offset+i+j]) if 32 <= d[offset+i+j] <= 126 else '.' 
                           for j in range(min(16, len(d)-offset-i)))
        print(f"  0x{offset+i:06X}: {hex_part:<48} {ascii_part}")

# Key locations from earlier scan
print("=== Setup GUID at 0x49BC0 ===")
hexdump(data, 0x49BC0 - 32, 128)

print("\n=== AMD_PBS GUID at 0x31920 ===")
hexdump(data, 0x31920 - 32, 128)

print("\n=== .rsrc start at 0x49B60 ===")
hexdump(data, 0x49B60, 128)

# Look for IFR FormSet opcode (0x0E) near the GUIDs
print("\n=== Searching for FormSet opcode near Setup GUID ===")
setup_guid_off = 0x49BC0
for off in range(setup_guid_off - 64, setup_guid_off + 4):
    if data[off] == 0x0E:
        byte1 = data[off+1]
        scope = (byte1 >> 7) & 1
        op_len = struct.unpack('<H', bytes([byte1 & 0x7F, data[off+2]]))[0]
        if scope and 20 < op_len < 5000:
            print(f"  FormSet at 0x{off:X}: scope={scope}, len={op_len}")
            hexdump(data, off, 64)

# Actually, look at what's BEFORE the GUID — the HII header should be there
print("\n=== 256 bytes before and after .rsrc start ===")
hexdump(data, 0x49B60, 256)

# Search for HII Package List magic pattern differently
# The format might be: Length(4) + GUID(16) for HII Package header
# Where Length includes the header itself
print("\n=== Alternative: search for HII packages at known string locations ===")
# "Above 4GB MMIO Limit" at 0x698A7
# "Fast Boot" at 0x67662
# "AMD CBS" at 0x6AE45
# These strings are in the .data section (0x2EA20-0x47360)
# The IFR forms reference these by string ID

# Let's look at the .data section for HII structure
data_start = 0x2EA20
print(f"\n=== .data section start ===")
hexdump(data, data_start, 128)

# Search for a proper HII Package List by looking for valid GUID + Length patterns
print("\n=== Searching for HII Package Lists ===")
for i in range(len(data) - 24):
    # Check if bytes 16-19 could be a reasonable total length
    total_len = struct.unpack('<I', data[i+16:i+20])[0]
    if total_len > 1000 and total_len < 2000000:
        # Check if first 16 bytes look like a valid GUID (non-zero, not all-same)
        guid = data[i:i+16]
        if guid != b'\x00' * 16 and guid != b'\xFF' * 16:
            # Check first package after header
            pkg_off = i + 20
            if pkg_off < len(data) - 4:
                raw = struct.unpack('<I', data[pkg_off:pkg_off+4])[0]
                pkg_len = raw & 0xFFFFFF
                pkg_type = (raw >> 24) & 0xFF
                if pkg_type in [0x02, 0x04] and 100 < pkg_len < total_len:
                    from scripts_parse import parse_guid as pg
                    pass

# Better approach: the strings we found are UTF-16LE in the binary
# Let's search for the HII string blocks that contain them
# String "Above 4GB MMIO Limit" at 0x698A7
print(f"\n=== Context around 'Above 4GB MMIO Limit' at 0x698A7 ===")
hexdump(data, 0x698A7 - 64, 128)

# The string block type 0x21 (EFI_HII_SIBT_STRING_UCS2) should be just before each string
# Search backwards from the string for the block type
for s_off in [0x698A7, 0x67662, 0x6AE45, 0x6930C]:
    # Look back for block type byte
    for back in range(1, 20):
        if data[s_off - back] == 0x21:
            print(f"  String block type 0x21 at 0x{s_off-back:X} ({back} bytes before string at 0x{s_off:X})")
            break
        elif data[s_off - back] == 0x14:
            print(f"  String block type 0x14 at 0x{s_off-back:X}")
            break

# Let's find where the string package starts by searching for the language string
# English strings start with "en-US" or "eng"
eng = b'e\x00n\x00-\x00U\x00S\x00'
idx = data.find(eng)
while idx >= 0:
    print(f"\n  'en-US' found at 0x{idx:X}")
    hexdump(data, idx - 48, 96)
    idx = data.find(eng, idx + 1)
    if idx > 0x100000:
        break
