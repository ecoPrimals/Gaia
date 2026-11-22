#!/usr/bin/env python3
"""REBOOT PRESCRIPTION — Map critical settings to exact setup_var.efi commands."""
import json

ifr = json.load(open(r'c:\Users\mokke\Desktop\Gaia\data\gut\ifr-full-map.json', encoding='utf-8'))
varstores = ifr.get('varstores', {})

critical_kw = ['Above 4G', 'Resize BAR', 'Fast Boot', 'NVMe', 'SVM', 'UMA Frame', 
               'CSM', 'M.2', 'Integrated Graph', 'iGPU', 'Re-Size']

print("=" * 60)
print("REBOOT PRESCRIPTION — Your M Drive + Gaming Unlock")
print("=" * 60)

rx = []
for s in ifr.get('settings', []):
    name = s.get('resolved_name', s.get('name', ''))
    if any(kw.lower() in name.lower() for kw in critical_kw):
        vsid = str(s.get('vsid', ''))
        vs = varstores.get(vsid, {})
        vs_name = vs.get('name', f'vs_{vsid}')
        vs_guid = vs.get('guid', '?')
        voff = s.get('voff', '?')
        stype = s.get('type', '?')
        
        rx.append({
            'name': name[:60],
            'varstore': vs_name,
            'guid': vs_guid,
            'offset': voff,
            'type': stype,
            'vsid': vsid
        })
        
        print(f"\n{name[:60]}")
        print(f"  VarStore: {vs_name} (GUID={vs_guid})")
        print(f"  Offset: {voff}, Type: {stype}")

# Save prescription
with open(r'c:\Users\mokke\Desktop\Gaia\data\gut\reboot-prescription.json', 'w', encoding='utf-8') as f:
    json.dump(rx, f, indent=2, ensure_ascii=False)

print(f"\n{'='*60}")
print(f"Total critical settings: {len(rx)}")
print(f"\nSaved to data/gut/reboot-prescription.json")

# The MAIN settings for M drive + gaming
print(f"\n{'='*60}")
print("TOP PRIORITY — These 3 unlock your M drive + gaming:")
print("="*60)
for item in rx:
    n = item['name'].lower()
    if 'above 4g decoding' in n or 'fast boot' == n.strip() or 'resize bar support' in n:
        print(f"\n  >>> {item['name']}")
        print(f"      setup_var.efi {item['varstore']} {item['offset']}=0x01")
        print(f"      GUID: {item['guid']}")
