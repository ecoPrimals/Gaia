#!/usr/bin/env python3
"""Parse IFR from the CORRECT offset — HII Package List at 0x49BC0 in Setup PE32."""
import struct, json

data = open(r'c:\Users\mokke\Desktop\Gaia\data\gut\setup-pe32-body.bin', 'rb').read()

def parse_guid(b):
    return '-'.join([
        b[3::-1].hex().upper(), b[5:3:-1].hex().upper(), b[7:5:-1].hex().upper(),
        b[8:10].hex().upper(), b[10:16].hex().upper()
    ])

# HII Package List starts at 0x49BC0
HII_START = 0x49BC0
pkg_guid = parse_guid(data[HII_START:HII_START+16])
pkg_total_len = struct.unpack('<I', data[HII_START+16:HII_START+20])[0]
print(f"HII Package List: GUID={pkg_guid}, TotalLen={pkg_total_len}")

# Parse packages
offset = HII_START + 20
pkg_count = 0
forms_ranges = []
strings_ranges = []

while offset < HII_START + pkg_total_len and offset < len(data) - 4:
    raw = struct.unpack('<I', data[offset:offset+4])[0]
    pkg_len = raw & 0xFFFFFF
    pkg_type = (raw >> 24) & 0xFF
    
    if pkg_len < 4 or pkg_type == 0xDF:
        print(f"  End of packages at +0x{offset-HII_START:X}")
        break
    
    pkg_types = {0x01: "GUID", 0x02: "FORMS", 0x04: "STRINGS", 0x05: "FONTS",
                 0x06: "IMAGES", 0x07: "SIMPLE_FONTS", 0xDF: "END"}
    type_name = pkg_types.get(pkg_type, f"UNK_0x{pkg_type:02X}")
    
    pkg_count += 1
    print(f"  Pkg#{pkg_count} at 0x{offset:X}: {type_name}(0x{pkg_type:02X}), len={pkg_len}")
    
    if pkg_type == 0x02:
        forms_ranges.append((offset + 4, offset + pkg_len))
    elif pkg_type == 0x04:
        strings_ranges.append((offset + 4, offset + pkg_len))
    
    offset += pkg_len

# Parse STRINGS first (so we can resolve names)
print(f"\n=== PARSING {len(strings_ranges)} STRING PACKAGES ===")
str_table = {}

for str_start, str_end in strings_ranges:
    str_data = data[str_start:str_end]
    
    # HII String Package Header
    # Offset 0: HdrSize (4), StringInfoOffset (4), LanguageWindow[16] (32),
    # LanguageName (2), Language (null-term ASCII)
    if len(str_data) < 46:
        continue
    
    hdr_size = struct.unpack('<I', str_data[0:4])[0]
    str_info_off = struct.unpack('<I', str_data[4:8])[0]
    
    # Language name at offset 40+
    lang_start = 40
    lang_end = str_data.find(b'\x00', lang_start, lang_start + 20)
    if lang_end < 0:
        lang_end = lang_start + 5
    lang = str_data[lang_start:lang_end].decode('ascii', errors='replace')
    
    if 'en' not in lang.lower() and lang not in ['', 'x-AMI', 'x-UEFI']:
        continue  # Skip non-English
    
    print(f"  Language: '{lang}', HdrSize={hdr_size}, StringInfoOffset={str_info_off}")
    
    # Parse string blocks starting at str_info_off
    si = str_info_off
    sid = 0
    while si < len(str_data) - 1:
        block_type = str_data[si]
        
        if block_type == 0x00:  # END
            break
        elif block_type == 0x21:  # EFI_HII_SIBT_STRING_UCS2
            si += 1
            sid += 1
            end = si
            while end < len(str_data) - 1:
                if str_data[end] == 0x00 and str_data[end+1] == 0x00:
                    break
                end += 2
            s = str_data[si:end].decode('utf-16-le', errors='replace')
            str_table[sid] = s
            si = end + 2
        elif block_type == 0x20:  # EFI_HII_SIBT_STRING_SCSU
            si += 1
            sid += 1
            end = str_data.find(b'\x00', si)
            if end < 0:
                break
            s = str_data[si:end].decode('ascii', errors='replace')
            str_table[sid] = s
            si = end + 1
        elif block_type == 0x22:  # EFI_HII_SIBT_STRING_UCS2_FONT
            si += 1
            font_id = str_data[si]
            si += 1
            sid += 1
            end = si
            while end < len(str_data) - 1:
                if str_data[end] == 0x00 and str_data[end+1] == 0x00:
                    break
                end += 2
            s = str_data[si:end].decode('utf-16-le', errors='replace')
            str_table[sid] = s
            si = end + 2
        elif block_type == 0x30:  # EFI_HII_SIBT_SKIP1
            si += 1
            count = str_data[si]
            sid += count
            si += 1
        elif block_type == 0x31:  # EFI_HII_SIBT_SKIP2
            si += 1
            count = struct.unpack('<H', str_data[si:si+2])[0]
            sid += count
            si += 2
        elif block_type == 0x10:  # EFI_HII_SIBT_STRINGS_SCSU
            si += 1
            count = struct.unpack('<H', str_data[si:si+2])[0]
            si += 2
            for _ in range(count):
                sid += 1
                end = str_data.find(b'\x00', si)
                if end < 0:
                    break
                s = str_data[si:end].decode('ascii', errors='replace')
                str_table[sid] = s
                si = end + 1
        elif block_type == 0x11:  # EFI_HII_SIBT_STRINGS_UCS2
            si += 1
            count = struct.unpack('<H', str_data[si:si+2])[0]
            si += 2
            for _ in range(count):
                sid += 1
                end = si
                while end < len(str_data) - 1:
                    if str_data[end] == 0x00 and str_data[end+1] == 0x00:
                        break
                    end += 2
                s = str_data[si:end].decode('utf-16-le', errors='replace')
                str_table[sid] = s
                si = end + 2
        else:
            break
    
    print(f"  Parsed {len(str_table)} strings (max SID={sid})")
    if str_table:
        break  # First language is enough

# Show key strings
print(f"\n  Key strings found:")
for sid, s in sorted(str_table.items()):
    if any(kw in s for kw in ['Above 4G', 'SMT', 'CCD', 'iGPU', 'UMA', 'Resizable',
                               'Fast Boot', 'IOMMU', 'SVM', 'AMD CBS', 'NVMe', 'PCIe',
                               'Core Perf', 'Re-Size', 'Hyper', 'Thread', 'ReBAR',
                               'M.2', 'Boot']):
        print(f"    #{sid}: \"{s}\"")

# Parse FORMS (IFR opcodes)
print(f"\n=== PARSING {len(forms_ranges)} FORM PACKAGES ===")
varstores = {}
settings = []
formsets = []

for forms_start, forms_end in forms_ranges:
    forms_data = data[forms_start:forms_end]
    print(f"  Forms package: {len(forms_data)} bytes")
    
    i = 0
    opcode_counts = {}
    while i < len(forms_data) - 2:
        opcode = forms_data[i]
        byte1 = forms_data[i+1]
        scope = (byte1 >> 7) & 1
        op_len = byte1 & 0x7F  # 7-bit length field, includes header
        
        if op_len < 2 or op_len > 127:
            i += 1
            continue
        
        opcode_counts[opcode] = opcode_counts.get(opcode, 0) + 1
        
        if opcode == 0x0E and op_len >= 20:  # FormSet
            guid = parse_guid(forms_data[i+2:i+18])
            title = struct.unpack('<H', forms_data[i+18:i+20])[0] if i+20 <= len(forms_data) else 0
            help_id = struct.unpack('<H', forms_data[i+20:i+22])[0] if i+22 <= len(forms_data) else 0
            title_str = str_table.get(title, f"str#{title}")
            formsets.append({"guid": guid, "title_str": title, "title": title_str, "offset": hex(forms_start + i)})
        
        elif opcode == 0x24 and op_len >= 22:  # VarStore
            guid = parse_guid(forms_data[i+2:i+18])
            vsid = struct.unpack('<H', forms_data[i+18:i+20])[0]
            size = struct.unpack('<H', forms_data[i+20:i+22])[0]
            name_end = forms_data.find(b'\x00', i+22, i+op_len)
            name = forms_data[i+22:name_end].decode('ascii', errors='replace') if name_end > 0 else '?'
            if name.isprintable() and len(name) > 0:
                varstores[vsid] = {"name": name, "guid": guid, "size": size}
        
        elif opcode == 0x26 and op_len >= 26:  # EfiVarStore
            guid = parse_guid(forms_data[i+2:i+18])
            vsid = struct.unpack('<H', forms_data[i+18:i+20])[0]
            attrs = struct.unpack('<I', forms_data[i+20:i+24])[0]
            size = struct.unpack('<H', forms_data[i+24:i+26])[0]
            name_end = forms_data.find(b'\x00', i+26, i+op_len)
            name = forms_data[i+26:name_end].decode('ascii', errors='replace') if name_end > 0 else '?'
            if name.isprintable() and len(name) > 0:
                varstores[vsid] = {"name": name, "guid": guid, "size": size, "efi": True}
        
        elif opcode == 0x05 and op_len >= 14:  # OneOf
            prompt = struct.unpack('<H', forms_data[i+2:i+4])[0]
            help_id = struct.unpack('<H', forms_data[i+4:i+6])[0]
            qflags = forms_data[i+6]
            qid = struct.unpack('<H', forms_data[i+7:i+9])[0]
            vsid = struct.unpack('<H', forms_data[i+9:i+11])[0]
            voff = struct.unpack('<H', forms_data[i+11:i+13])[0]
            name = str_table.get(prompt, f"str#{prompt}")
            settings.append({
                "type": "OneOf", "name": name, "prompt_str": prompt,
                "qid": qid, "vsid": vsid, "voff": hex(voff),
                "vs_name": varstores.get(vsid, {}).get("name", f"vs_{vsid}")
            })
        
        elif opcode == 0x07 and op_len >= 14:  # Numeric
            prompt = struct.unpack('<H', forms_data[i+2:i+4])[0]
            qid = struct.unpack('<H', forms_data[i+7:i+9])[0]
            vsid = struct.unpack('<H', forms_data[i+9:i+11])[0]
            voff = struct.unpack('<H', forms_data[i+11:i+13])[0]
            name = str_table.get(prompt, f"str#{prompt}")
            settings.append({
                "type": "Numeric", "name": name, "prompt_str": prompt,
                "qid": qid, "vsid": vsid, "voff": hex(voff),
                "vs_name": varstores.get(vsid, {}).get("name", f"vs_{vsid}")
            })
        
        elif opcode == 0x06 and op_len >= 14:  # Checkbox
            prompt = struct.unpack('<H', forms_data[i+2:i+4])[0]
            qid = struct.unpack('<H', forms_data[i+7:i+9])[0]
            vsid = struct.unpack('<H', forms_data[i+9:i+11])[0]
            voff = struct.unpack('<H', forms_data[i+11:i+13])[0]
            name = str_table.get(prompt, f"str#{prompt}")
            settings.append({
                "type": "Checkbox", "name": name, "prompt_str": prompt,
                "qid": qid, "vsid": vsid, "voff": hex(voff),
                "vs_name": varstores.get(vsid, {}).get("name", f"vs_{vsid}")
            })
        
        i += op_len
    
    print(f"  Opcodes: {sum(opcode_counts.values())} total, {len(opcode_counts)} types")
    op_names = {0x01:'Form', 0x02:'Subtitle', 0x03:'Text', 0x05:'OneOf', 0x06:'Checkbox',
               0x07:'Numeric', 0x09:'OneOfOption', 0x0E:'FormSet', 0x24:'VarStore',
               0x26:'EfiVarStore', 0x29:'End', 0x0A:'SuppressIf', 0x19:'GrayOutIf',
               0x0D:'Action', 0x14:'Ref', 0x20:'ResetButton', 0x12:'DefaultStore',
               0x5B:'Default', 0x0B:'DisableIf'}
    for op, count in sorted(opcode_counts.items(), key=lambda x: -x[1])[:20]:
        name = op_names.get(op, f'0x{op:02X}')
        print(f"    {name}(0x{op:02X}): {count}")

# Report
print(f"\n{'='*60}")
print(f"FORMSETS: {len(formsets)}")
for fs in formsets:
    print(f"  {fs['guid']}: \"{fs['title']}\"")

print(f"\nVARSTORES: {len(varstores)}")
for vsid, vs in sorted(varstores.items()):
    print(f"  VarStore 0x{vsid:04X}: {vs['name']} (GUID={vs['guid']}, size={vs['size']})")

print(f"\nSETTINGS: {len(settings)} total")
from collections import Counter
vs_counts = Counter(s['vs_name'] for s in settings)
for name, count in vs_counts.most_common(20):
    print(f"  {name}: {count} settings")

# Show CRITICAL settings
print(f"\n{'='*60}")
print("CRITICAL SETTINGS (the ones we need to change):")
for s in settings:
    if any(kw in s['name'].lower() for kw in ['above 4g', 'smt', 'ccd', 'igpu', 'uma',
            'resizable', 'fast boot', 'iommu', 'svm', 'rebar', 're-size', 'bar support',
            'core perf', 'nvme', 'pcie gen', 'm.2 slot', 'integrated graph']):
        print(f"  *** {s['name']}: {s['vs_name']}:{s['voff']} ({s['type']}) ***")

# Save
results = {
    "bios": "ROG STRIX X870E-E GAMING WIFI BIOS 1401",
    "formsets": formsets,
    "varstores": {str(k): v for k, v in varstores.items()},
    "settings": settings,
    "strings_count": len(str_table),
    "critical_strings": {str(k): v for k, v in str_table.items()
                        if any(kw in v for kw in ['Above', 'SMT', 'CCD', 'iGPU', 'UMA',
                                                   'Resizable', 'Fast Boot', 'IOMMU', 'SVM',
                                                   'AMD CBS', 'NVMe', 'Core Perf', 'M.2'])}
}
with open(r'c:\Users\mokke\Desktop\Gaia\data\gut\ifr-full-map.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved: {len(settings)} settings, {len(varstores)} varstores, {len(str_table)} strings")
