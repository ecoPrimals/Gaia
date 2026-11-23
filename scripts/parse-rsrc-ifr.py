#!/usr/bin/env python3
"""Parse IFR from the .rsrc section of Setup DXE PE32.
The HII Package List starts at 0x49B60 in the PE32."""
import struct, json

data = open(r'c:\Users\mokke\Desktop\Gaia\data\gut\setup-pe32-body.bin', 'rb').read()
rsrc_start = 0x49B60
rsrc_data = data[rsrc_start:]
print(f"PE32: {len(data)} bytes, .rsrc section: {len(rsrc_data)} bytes starting at 0x{rsrc_start:X}")

def parse_guid(b):
    return '-'.join([
        b[3::-1].hex().upper(), b[5:3:-1].hex().upper(), b[7:5:-1].hex().upper(),
        b[8:10].hex().upper(), b[10:16].hex().upper()
    ]).lower()

# HII Package List Header: GUID(16) + Length(4)
# Then packages follow: each has Length(3)+Type(1) header
# Look for the HII Package List starting with the Setup FormSet GUID

# The .rsrc section likely IS the HII resource
# Parse HII Package List Header
pkg_list_guid = parse_guid(rsrc_data[0:16])
pkg_list_len = struct.unpack('<I', rsrc_data[16:20])[0]
print(f"HII Package List: GUID={pkg_list_guid}, Length={pkg_list_len}")

# Parse packages within the list
offset = 20  # After the header
packages = []
while offset < len(rsrc_data) - 4:
    raw = struct.unpack('<I', rsrc_data[offset:offset+4])[0]
    pkg_len = raw & 0xFFFFFF
    pkg_type = (raw >> 24) & 0xFF
    
    if pkg_len < 4 or pkg_len > len(rsrc_data) - offset:
        break
    
    pkg_types = {0x01: "GUID", 0x02: "FORM", 0x04: "STRINGS", 0x05: "FONTS",
                 0x06: "IMAGES", 0x07: "SIMPLE_FONTS", 0x08: "DEVICE_PATH",
                 0x09: "KEYBOARD", 0x0E: "ANIMATIONS", 0xDF: "END"}
    
    type_name = pkg_types.get(pkg_type, f"0x{pkg_type:02X}")
    print(f"  Package at +0x{offset:X}: type={type_name}({pkg_type}), len={pkg_len}")
    packages.append({"offset": offset, "type": pkg_type, "type_name": type_name, "length": pkg_len})
    
    if pkg_type == 0xDF:  # End
        break
    
    offset += pkg_len

# Find FORM package (type 0x02) — this has all the IFR opcodes
print("\n=== PARSING IFR FORMS ===")
varstores = {}
settings = []
formsets = []

for pkg in packages:
    if pkg["type"] == 0x02:  # FORM package
        forms_data = rsrc_data[pkg["offset"]+4:pkg["offset"]+pkg["length"]]
        print(f"  Forms package: {len(forms_data)} bytes")
        
        i = 0
        while i < len(forms_data) - 3:
            opcode = forms_data[i]
            byte1 = forms_data[i+1]
            scope = (byte1 >> 7) & 1
            op_len = struct.unpack('<H', bytes([byte1 & 0x7F, forms_data[i+2]]))[0]
            
            if op_len < 2 or op_len > 10000:
                i += 1
                continue
            
            # FormSet (0x0E)
            if opcode == 0x0E and op_len >= 20:
                guid = parse_guid(forms_data[i+3:i+19])
                title = struct.unpack('<H', forms_data[i+19:i+21])[0]
                help_id = struct.unpack('<H', forms_data[i+21:i+23])[0]
                formsets.append({"guid": guid, "title_str": title, "help_str": help_id, "offset": hex(i)})
            
            # VarStore (0x24)
            elif opcode == 0x24 and op_len >= 22:
                guid = parse_guid(forms_data[i+3:i+19])
                vsid = struct.unpack('<H', forms_data[i+19:i+21])[0]
                size = struct.unpack('<H', forms_data[i+21:i+23])[0]
                name_end = forms_data.find(b'\x00', i+23, i+op_len+3)
                name = forms_data[i+23:name_end].decode('ascii', errors='replace') if name_end > 0 else '?'
                if name.isprintable() and len(name) > 0:
                    varstores[vsid] = {"name": name, "guid": guid, "size": size}
            
            # EfiVarStore (0x26)  
            elif opcode == 0x26 and op_len >= 26:
                guid = parse_guid(forms_data[i+3:i+19])
                vsid = struct.unpack('<H', forms_data[i+19:i+21])[0]
                attrs = struct.unpack('<I', forms_data[i+21:i+25])[0]
                size = struct.unpack('<H', forms_data[i+25:i+27])[0]
                name_end = forms_data.find(b'\x00', i+27, i+op_len+3)
                name = forms_data[i+27:name_end].decode('ascii', errors='replace') if name_end > 0 else '?'
                if name.isprintable() and len(name) > 0:
                    varstores[vsid] = {"name": name, "guid": guid, "size": size, "efi": True}
            
            # OneOf (0x05)
            elif opcode == 0x05 and op_len >= 14:
                prompt = struct.unpack('<H', forms_data[i+3:i+5])[0]
                help_id = struct.unpack('<H', forms_data[i+5:i+7])[0]
                qflags = forms_data[i+7]
                qid = struct.unpack('<H', forms_data[i+8:i+10])[0]
                vsid = struct.unpack('<H', forms_data[i+10:i+12])[0]
                voff = struct.unpack('<H', forms_data[i+12:i+14])[0]
                flags = forms_data[i+14] if op_len > 14 else 0
                settings.append({
                    "type": "OneOf", "prompt_str": prompt, "help_str": help_id,
                    "qid": qid, "vsid": vsid, "voff": voff,
                    "vs_name": varstores.get(vsid, {}).get("name", f"vs_{vsid}"),
                    "offset": hex(rsrc_start + pkg["offset"] + 4 + i)
                })
            
            # Numeric (0x07)
            elif opcode == 0x07 and op_len >= 14:
                prompt = struct.unpack('<H', forms_data[i+3:i+5])[0]
                help_id = struct.unpack('<H', forms_data[i+5:i+7])[0]
                qflags = forms_data[i+7]
                qid = struct.unpack('<H', forms_data[i+8:i+10])[0]
                vsid = struct.unpack('<H', forms_data[i+10:i+12])[0]
                voff = struct.unpack('<H', forms_data[i+12:i+14])[0]
                settings.append({
                    "type": "Numeric", "prompt_str": prompt, "help_str": help_id,
                    "qid": qid, "vsid": vsid, "voff": voff,
                    "vs_name": varstores.get(vsid, {}).get("name", f"vs_{vsid}"),
                    "offset": hex(rsrc_start + pkg["offset"] + 4 + i)
                })
            
            # Checkbox (0x06)
            elif opcode == 0x06 and op_len >= 14:
                prompt = struct.unpack('<H', forms_data[i+3:i+5])[0]
                help_id = struct.unpack('<H', forms_data[i+5:i+7])[0]
                qflags = forms_data[i+7]
                qid = struct.unpack('<H', forms_data[i+8:i+10])[0]
                vsid = struct.unpack('<H', forms_data[i+10:i+12])[0]
                voff = struct.unpack('<H', forms_data[i+12:i+14])[0]
                settings.append({
                    "type": "Checkbox", "prompt_str": prompt, "help_str": help_id,
                    "qid": qid, "vsid": vsid, "voff": voff,
                    "vs_name": varstores.get(vsid, {}).get("name", f"vs_{vsid}"),
                    "offset": hex(rsrc_start + pkg["offset"] + 4 + i)
                })
            
            i += max(op_len, 1)

# Parse STRINGS package for string resolution
print("\n=== PARSING STRING TABLE ===")
str_table = {}
for pkg in packages:
    if pkg["type"] == 0x04:  # STRINGS package
        str_data = rsrc_data[pkg["offset"]+4:pkg["offset"]+pkg["length"]]
        print(f"  Strings package: {len(str_data)} bytes")
        
        # HII String Package Header: Header(44) + Language(var) then string blocks
        # Simpler approach: extract UTF-16LE strings from the package
        j = 0
        sid = 0
        # Find strings by scanning for Unicode text
        while j < len(str_data) - 4:
            # String block type 0x21 = UCS2 string
            if str_data[j] == 0x21 and j + 2 < len(str_data):
                # Next bytes are the UTF-16LE string until null terminator
                end = j + 1
                while end < len(str_data) - 1:
                    if str_data[end] == 0x00 and str_data[end+1] == 0x00:
                        end += 2
                        break
                    end += 2
                s = str_data[j+1:end-2].decode('utf-16-le', errors='replace')
                if len(s) > 0:
                    sid += 1
                    str_table[sid] = s
                j = end
            elif str_data[j] == 0x00:
                # Skip string (empty)
                sid += 1
                j += 1
            else:
                j += 1
        
        print(f"  Extracted {len(str_table)} strings")
        # Show some key strings
        for sid, s in sorted(str_table.items()):
            if any(kw in s for kw in ['Above 4G', 'SMT', 'CCD', 'iGPU', 'UMA', 'Resizable',
                                       'Fast Boot', 'IOMMU', 'SVM', 'AMD CBS', 'NVMe',
                                       'Core Perf', 'Re-Size', 'Hyper', 'Thread']):
                print(f"    STR#{sid}: \"{s}\"")
        break  # First language only

# Report
print(f"\n=== RESULTS ===")
print(f"FormSets: {len(formsets)}")
for fs in formsets:
    title = str_table.get(fs['title_str'], f"str#{fs['title_str']}")
    print(f"  {fs['guid']}: \"{title}\"")

print(f"\nVarStores: {len(varstores)}")
for vsid, vs in sorted(varstores.items()):
    print(f"  0x{vsid:04X}: {vs['name']} (GUID={vs['guid']}, size={vs['size']})")

print(f"\nSettings: {len(settings)} total")
from collections import Counter
vs_counts = Counter(s['vs_name'] for s in settings)
for name, count in vs_counts.most_common(20):
    print(f"  {name}: {count} settings")

# Map settings to strings
print(f"\n=== FULL OFFSET MAP (with string names) ===")
for s in settings:
    name = str_table.get(s['prompt_str'], f"str#{s['prompt_str']}")
    s['name'] = name
    vs_name = s['vs_name']
    voff = s['voff']
    if any(kw in name.lower() for kw in ['above 4g', 'smt', 'ccd', 'igpu', 'uma', 'resizable',
                                           'fast boot', 'iommu', 'svm', 'amd cbs', 'nvme',
                                           'core perf', 're-size', 'hyper', 'thread', 'pcie',
                                           'above4g', 'rebar', 'bar support']):
        print(f"  *** {name}: {vs_name}:0x{voff:04X} ({s['type']}) ***")

# Save full map
results = {
    "bios": "ROG STRIX X870E-E GAMING WIFI BIOS 1401",
    "formsets": formsets,
    "varstores": {str(k): v for k, v in varstores.items()},
    "settings": settings,
    "critical_strings": {str(k): v for k, v in str_table.items() 
                        if any(kw in v for kw in ['Above', 'SMT', 'CCD', 'iGPU', 'UMA', 
                                                   'Resizable', 'Fast Boot', 'IOMMU', 'SVM',
                                                   'AMD CBS', 'NVMe', 'Core Perf'])},
    "stats": {
        "total_settings": len(settings),
        "total_varstores": len(varstores),
        "total_strings": len(str_table),
        "by_varstore": dict(vs_counts)
    }
}
with open(r'c:\Users\mokke\Desktop\Gaia\data\gut\ifr-full-map.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved full IFR map: {len(settings)} settings, {len(varstores)} varstores, {len(str_table)} strings")
