#!/usr/bin/env python3
"""Find HII Package Lists inside the Setup PE32 by searching for known GUIDs."""
import struct, json

data = open(r'c:\Users\mokke\Desktop\Gaia\data\gut\setup-pe32-body.bin', 'rb').read()
print(f"PE32 body: {len(data)} bytes")

def parse_guid(b):
    return '-'.join([
        b[3::-1].hex().upper(), b[5:3:-1].hex().upper(), b[7:5:-1].hex().upper(),
        b[8:10].hex().upper(), b[10:16].hex().upper()
    ])

def make_guid_bytes(guid_str):
    parts = guid_str.split('-')
    return (bytes.fromhex(parts[0])[::-1] + bytes.fromhex(parts[1])[::-1] + 
            bytes.fromhex(parts[2])[::-1] + bytes.fromhex(parts[3]) + bytes.fromhex(parts[4]))

# Known GUIDs to search for
known = {
    "Setup": "899407D7-99FE-43D8-9A21-79EC328CAC21",
    "AMI_SETUP": "EC87D643-EBA4-4BB5-A1E5-3F3E36B20DA9",
    "CBS_SETUP": "B04535E3-3004-4946-9EB7-149428983053",
    "AMD_PBS": "A339D746-F678-49B3-9FC7-54CE0F9DF226",
}

print("\n=== Searching for known GUIDs ===")
for name, guid in known.items():
    gb = make_guid_bytes(guid)
    idx = 0
    while True:
        idx = data.find(gb, idx)
        if idx == -1:
            break
        print(f"  {name} ({guid}) found at 0x{idx:X}")
        idx += 1

# Search for HII Package List Header
# Structure: GUID(16) + Length(4) -> then packages
# Package header: Length(3) + Type(1)
# Types: 0x04=FORMS, 0x06=STRINGS
print("\n=== Searching for HII Package Headers ===")
for i in range(len(data) - 24):
    # Check for package type FORMS (0x04) at offset +3
    pkg_len_raw = data[i:i+3]
    pkg_type = data[i+3]
    
    if pkg_type == 0x04:  # Forms package
        pkg_len = struct.unpack('<I', pkg_len_raw + b'\x00')[0]
        if 200 < pkg_len < 500000:
            print(f"  FORMS package at 0x{i:X}, length={pkg_len}")
            # Try parsing IFR from here
            forms_data = data[i+4:i+pkg_len]
            # Count opcodes
            j = 0
            opcodes = {}
            while j < len(forms_data) - 3:
                op = forms_data[j]
                scope = (forms_data[j+1] >> 7) & 1
                op_len = struct.unpack('<H', bytes([forms_data[j+1] & 0x7F, forms_data[j+2]]))[0]
                if op_len < 2 or op_len > 10000:
                    break
                opcodes[op] = opcodes.get(op, 0) + 1
                j += op_len
            if opcodes:
                print(f"    Opcodes: {len(opcodes)} types, total {sum(opcodes.values())} ops")
                op_names = {0x01:'Form', 0x02:'Subtitle', 0x03:'Text', 0x05:'OneOf', 0x06:'Checkbox',
                           0x07:'Numeric', 0x09:'OneOfOption', 0x0E:'FormSet', 0x24:'VarStore',
                           0x26:'VarStoreEfi', 0x29:'End', 0x0A:'SuppressIf', 0x19:'GrayOutIf',
                           0x0D:'Action', 0x14:'Ref', 0x20:'ResetButton'}
                for op, count in sorted(opcodes.items(), key=lambda x: -x[1])[:15]:
                    name = op_names.get(op, f'0x{op:02X}')
                    print(f"      {name}: {count}")

# Parse PE32 headers to find sections
print("\n=== PE32 Structure ===")
if data[:2] == b'MZ':
    pe_off = struct.unpack('<I', data[0x3C:0x40])[0]
    print(f"  MZ header, PE at 0x{pe_off:X}")
    if data[pe_off:pe_off+4] == b'PE\x00\x00':
        machine = struct.unpack('<H', data[pe_off+4:pe_off+6])[0]
        nsections = struct.unpack('<H', data[pe_off+6:pe_off+8])[0]
        opt_size = struct.unpack('<H', data[pe_off+20:pe_off+22])[0]
        print(f"  Machine: 0x{machine:X}, Sections: {nsections}, OptHdr: {opt_size}")
        
        # Section headers start after optional header
        sec_start = pe_off + 24 + opt_size
        for s in range(nsections):
            off = sec_start + s * 40
            name = data[off:off+8].rstrip(b'\x00').decode('ascii', errors='replace')
            vsize = struct.unpack('<I', data[off+8:off+12])[0]
            vaddr = struct.unpack('<I', data[off+12:off+16])[0]
            rsize = struct.unpack('<I', data[off+16:off+20])[0]
            raddr = struct.unpack('<I', data[off+20:off+24])[0]
            print(f"  Section '{name}': VA=0x{vaddr:X}, VSize={vsize}, Raw=0x{raddr:X}, RawSize={rsize}")

# Search for string table by looking for UTF-16LE "Above 4G"
target_strings = [
    ("Above 4G", "Above 4G".encode('utf-16-le')),
    ("SMT Control", "SMT Control".encode('utf-16-le')),
    ("Fast Boot", "Fast Boot".encode('utf-16-le')),
    ("AMD CBS", "AMD CBS".encode('utf-16-le')),
    ("Resizable BAR", "Resizable BAR".encode('utf-16-le')),
    ("IOMMU", "IOMMU".encode('utf-16-le')),
    ("SVM Mode", "SVM Mode".encode('utf-16-le')),
    ("CCD Control", "CCD Control".encode('utf-16-le')),
    ("iGPU", "iGPU".encode('utf-16-le')),
    ("UMA Frame", "UMA Frame".encode('utf-16-le')),
    ("Core Performance Boost", "Core Performance Boost".encode('utf-16-le')),
]

print("\n=== Critical String Locations ===")
for name, needle in target_strings:
    idx = data.find(needle)
    if idx >= 0:
        # Read the full string
        end = data.find(b'\x00\x00', idx)
        if end > idx:
            full = data[idx:end+1].decode('utf-16-le', errors='replace')
            print(f"  '{name}' at 0x{idx:X}: \"{full}\"")
    else:
        print(f"  '{name}': NOT FOUND")
