#!/usr/bin/env python3
"""Fix IFR string extraction — find the EXACT setting names and offsets for setup_var.efi."""
import struct, json

data = open(r'c:\Users\mokke\Desktop\Gaia\data\gut\setup-pe32-body.bin', 'rb').read()

# We know critical strings exist at these offsets (from UTF-16LE search):
# "Above 4GB MMIO Limit" at 0x698A7
# "Fast Boot" at 0x67662  
# "AMD CBS" at 0x6AE45
# "SVM Mode" at 0x6930C
# "UMA Frame Buffer Size" at 0x85164
# "Core Performance Boost" at 0x998A1

# The string packages start at 0x670BC (first one, en-US)
# HdrSize=52, StringInfoOffset=52
# String blocks start at 0x670BC + 52 = 0x670F0

# The problem: block type at 0x670F0 is 0x00 which we treated as END.
# But 0x00 might be an empty string (string ID 1 = empty), not the end marker.
# Let's look at what's actually there

str_pkg_start = 0x670BC
hdr_size = 52
str_info = str_pkg_start + hdr_size

print(f"String blocks start at 0x{str_info:X}")
print(f"First 32 bytes: {data[str_info:str_info+32].hex()}")

# In HII, block type 0x00 = EFI_HII_SIBT_END
# But before that there might be a StringInfoOffset that points differently
# Let's re-read the header more carefully

# Actually, the StringInfoOffset might be relative to the STRING package start,
# not the PE32 start. The string package header starts AFTER the HII package header (4 bytes)
# So string package data starts at 0x670B8 + 4 = 0x670BC

# Let me look at more of the raw data around 0x670F0
print(f"\nData at string block start:")
for off in range(0, 128, 16):
    pos = str_info + off
    hex_str = ' '.join(f'{data[pos+j]:02X}' for j in range(16))
    ascii_str = ''.join(chr(data[pos+j]) if 32 <= data[pos+j] <= 126 else '.'
                       for j in range(16))
    print(f"  0x{pos:06X}: {hex_str}  {ascii_str}")

# The first byte 0x00 at 0x670F0 followed by 0x67... looks like:
# It might be that 0x00 is indeed string 1 (empty), then 0x67 = 'g', 0x00 = null...
# Wait - 0x670F0 contains: 00 67 00 6C 00 69 00 73 00 68 00 00 00 14 00 00
# That's: \x00 g \x00 l \x00 i \x00 s \x00 h \x00 \x00 \x00 \x14 ...
# Which is part of "English" in UTF-16LE! The string table starts INSIDE the header!

# Let me look at the ACTUAL string package header format:
# typedef struct {
#   EFI_HII_PACKAGE_HEADER Header;  // 4 bytes (in our case, already stripped)
#   UINT32 HdrSize;                 // 4 bytes
#   UINT32 StringInfoOffset;        // 4 bytes  
#   UINT16 LanguageWindow[16];      // 32 bytes
#   EFI_STRING LanguageName;        // Variable (UTF-16 "English\0")
#   CHAR8 Language[];               // Variable ("en-US\0")
# };

# HdrSize = 52 bytes, StringInfoOffset = 52 bytes
# But LanguageName is "English" in UTF-16LE = 7 chars * 2 + 2 null = 16 bytes
# Starting at offset 40 in the header
# Then Language = "en-US\0" = 6 bytes starting at offset 56
# But HdrSize says 52... so the LanguageName starts at 40, 
# "English" = 14 bytes + 2 null = 16, ending at 56
# But HdrSize is 52 which means the header ends at 52...

# Let me just scan forward from the known string positions and work backwards
# We KNOW "Fast Boot" is at 0x67662 in UTF-16LE
# Each string has a block type byte before it (0x21 for UCS2)

print(f"\n=== Working backwards from known strings ===")
known_strings = {
    0x67662: "Fast Boot",
    0x698A7: "Above 4GB MMIO Limit", 
    0x6930C: "SVM Mode",
    0x6AE45: "AMD CBS",
    0x85164: "UMA Frame Buffer Size",
    0x998A1: "Core Performance Boost"
}

for addr, name in sorted(known_strings.items()):
    # Look for block type byte before the string
    # Might be 0x21 (UCS2) or the string might start right after another string's null terminator
    prev_bytes = data[addr-8:addr]
    print(f"\n  '{name}' at 0x{addr:X}")
    print(f"    8 bytes before: {prev_bytes.hex()}")
    # The null terminator of previous string + block type
    # \x00\x00 (null term) + 0x21 (UCS2 block) = pattern to look for

# Let's try a different approach: just scan the whole string package for ALL UCS2 strings
# by looking for the pattern: 0x21 + printable UTF-16LE
print(f"\n=== FULL STRING SCAN ===")
str_table = {}
sid = 0

# Start scanning from just after the header
# The first string (ID 1) should be near the header end
scan_start = str_info  # 0x670F0
scan_end = 0x670B8 + 343463  # End of string package

i = scan_start
while i < scan_end - 2:
    b = data[i]
    
    if b == 0x21:  # EFI_HII_SIBT_STRING_UCS2
        sid += 1
        i += 1
        # Read UTF-16LE until \x00\x00
        start = i
        while i < scan_end - 1:
            if data[i] == 0x00 and data[i+1] == 0x00:
                break
            i += 2
        s = data[start:i].decode('utf-16-le', errors='replace')
        str_table[sid] = s
        i += 2  # Skip null terminator
        
    elif b == 0x20:  # EFI_HII_SIBT_STRING_SCSU (ASCII)
        sid += 1
        i += 1
        start = i
        while i < scan_end and data[i] != 0x00:
            i += 1
        s = data[start:i].decode('ascii', errors='replace')
        str_table[sid] = s
        i += 1
        
    elif b == 0x30:  # SKIP1
        count = data[i+1]
        sid += count
        i += 2
        
    elif b == 0x31:  # SKIP2
        count = struct.unpack('<H', data[i+1:i+3])[0]
        sid += count
        i += 3
        
    elif b == 0x14:  # EFI_HII_SIBT_STRING_UCS2_FONT (font byte IS first string char in AMI)
        sid += 1
        i += 1  # Skip only block type, string starts immediately
        start = i
        while i < scan_end - 1:
            if data[i] == 0x00 and data[i+1] == 0x00:
                break
            i += 2
        s = data[start:i].decode('utf-16-le', errors='replace')
        str_table[sid] = s
        i += 2
        
    elif b == 0x00:  # END or just a null byte
        # Check if this is truly END or part of data
        # If next byte is also 0x00, might be END
        if i + 1 < scan_end and data[i+1] == 0x00:
            # Could be null terminator of something, skip
            i += 2
        else:
            i += 1
    else:
        i += 1

print(f"Total strings: {len(str_table)}")
print(f"Max SID: {sid}")

# Show critical strings
print(f"\n=== CRITICAL SETTINGS ===")
critical_keywords = ['Above 4G', 'SMT', 'CCD', 'iGPU', 'UMA', 'Resizable', 'Re-Size',
                     'Fast Boot', 'IOMMU', 'SVM', 'AMD CBS', 'NVMe', 'PCIe', 'Core Perf',
                     'Integrated', 'M.2', 'Boot', 'BAR', 'Above4G', 'Hyper-Thread']
for sid_val, s in sorted(str_table.items()):
    if any(kw.lower() in s.lower() for kw in critical_keywords):
        print(f"  STR#{sid_val}: \"{s}\"")

# Save
with open(r'c:\Users\mokke\Desktop\Gaia\data\gut\ifr-strings.json', 'w', encoding='utf-8') as f:
    json.dump({str(k): v for k, v in str_table.items()}, f, indent=2, ensure_ascii=False)
print(f"\nSaved {len(str_table)} strings")

# Now cross-reference with the IFR settings
print(f"\n=== CROSS-REFERENCE: Settings with Names ===")
ifr = json.load(open(r'c:\Users\mokke\Desktop\Gaia\data\gut\ifr-full-map.json'))
critical_found = []
for s in ifr.get('settings', []):
    prompt_id = s.get('prompt_str', 0)
    name = str_table.get(prompt_id, f"str#{prompt_id}")
    s['resolved_name'] = name
    if any(kw.lower() in name.lower() for kw in critical_keywords):
        vs_name = s.get('vs_name', '?')
        voff = s.get('voff', '?')
        critical_found.append(s)
        print(f"  *** {name}: {vs_name}:{voff} ({s.get('type','?')}) ***")

# Update IFR map with resolved names
for s in ifr.get('settings', []):
    s['resolved_name'] = str_table.get(s.get('prompt_str', 0), f"str#{s.get('prompt_str', 0)}")
with open(r'c:\Users\mokke\Desktop\Gaia\data\gut\ifr-full-map.json', 'w', encoding='utf-8') as f:
    json.dump(ifr, f, indent=2, ensure_ascii=False)
print(f"\nUpdated ifr-full-map.json with {len(critical_found)} critical settings resolved")
