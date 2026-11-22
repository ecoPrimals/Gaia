"""Map ALL UEFI variables — find AMD CBS, UMA, and the keys to self-healing."""
import ctypes, ctypes.wintypes, struct, json, os

kernel32 = ctypes.windll.kernel32
advapi32 = ctypes.windll.advapi32
ntdll = ctypes.windll.ntdll

# Enable privilege
TOKEN_ADJUST_PRIVILEGES = 0x0020
TOKEN_QUERY = 0x0008
SE_PRIVILEGE_ENABLED = 0x00000002

class LUID(ctypes.Structure):
    _fields_ = [("LowPart", ctypes.wintypes.DWORD), ("HighPart", ctypes.wintypes.LONG)]
class LUID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [("Luid", LUID), ("Attributes", ctypes.wintypes.DWORD)]
class TOKEN_PRIVILEGES(ctypes.Structure):
    _fields_ = [("PrivilegeCount", ctypes.wintypes.DWORD), ("Privileges", LUID_AND_ATTRIBUTES * 1)]

kernel32.GetCurrentProcess.restype = ctypes.wintypes.HANDLE
advapi32.OpenProcessToken.argtypes = [ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD, ctypes.POINTER(ctypes.wintypes.HANDLE)]
advapi32.OpenProcessToken.restype = ctypes.wintypes.BOOL

token = ctypes.wintypes.HANDLE()
advapi32.OpenProcessToken(kernel32.GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, ctypes.byref(token))
luid = LUID()
advapi32.LookupPrivilegeValueW(None, "SeSystemEnvironmentPrivilege", ctypes.byref(luid))
tp = TOKEN_PRIVILEGES()
tp.PrivilegeCount = 1
tp.Privileges[0].Luid = luid
tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED
advapi32.AdjustTokenPrivileges(token, False, ctypes.byref(tp), 0, None, None)
print("✅ Firmware privilege enabled\n")

# Enumerate all UEFI variables
NtEnumerateSystemEnvironmentValuesEx = ntdll.NtEnumerateSystemEnvironmentValuesEx
NtEnumerateSystemEnvironmentValuesEx.restype = ctypes.c_long
NtEnumerateSystemEnvironmentValuesEx.argtypes = [ctypes.c_ulong, ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]

buf_size = ctypes.c_ulong(0)
NtEnumerateSystemEnvironmentValuesEx(1, None, ctypes.byref(buf_size))
buf = ctypes.create_string_buffer(buf_size.value)
status = NtEnumerateSystemEnvironmentValuesEx(1, buf, ctypes.byref(buf_size))

variables = []
offset = 0
raw = buf.raw
while offset < len(raw) - 24:
    next_offset = struct.unpack_from('<I', raw, offset)[0]
    guid_bytes = raw[offset+4:offset+20]
    name_start = offset + 20
    name_end = raw.find(b'\x00\x00', name_start)
    if name_end < 0:
        break
    if (name_end - name_start) % 2 != 0:
        name_end += 1
    try:
        name = raw[name_start:name_end+1].decode('utf-16-le').rstrip('\x00')
    except:
        name = "???"
    g = struct.unpack_from('<IHH', guid_bytes, 0)
    g_rest = guid_bytes[8:16]
    guid_str = f"{g[0]:08X}-{g[1]:04X}-{g[2]:04X}-{g_rest[:2].hex().upper()}-{g_rest[2:].hex().upper()}"
    variables.append({"name": name, "guid": guid_str})
    if next_offset == 0:
        break
    offset += next_offset

print(f"Total UEFI variables: {len(variables)}\n")

# Categorize
categories = {
    "AMD/CBS/UMA/NBIO": [],
    "ASUS/ROG": [],
    "Setup/Config/BIOS": [],
    "Boot/BCD": [],
    "Display/GPU/Video": [],
    "Other": [],
}

for v in variables:
    nl = v['name'].lower()
    if any(k in nl for k in ['amd', 'cbs', 'uma', 'nbio', 'zen', 'pbs']):
        categories["AMD/CBS/UMA/NBIO"].append(v)
    elif any(k in nl for k in ['asus', 'rog', 'aura']):
        categories["ASUS/ROG"].append(v)
    elif any(k in nl for k in ['setup', 'config', 'bios', 'custom']):
        categories["Setup/Config/BIOS"].append(v)
    elif any(k in nl for k in ['boot', 'bcd', 'secureboot']):
        categories["Boot/BCD"].append(v)
    elif any(k in nl for k in ['display', 'gpu', 'video', 'vga', 'gop', 'gfx']):
        categories["Display/GPU/Video"].append(v)
    else:
        categories["Other"].append(v)

for cat, items in categories.items():
    if items:
        print(f"═══ {cat} ({len(items)}) ═══")
        for v in items:
            print(f"  {v['name']}  {{{v['guid']}}}")
        print()

# Now try to READ every variable that could contain UMA settings
print("=" * 60)
print("READING ALL BIOS-RELATED UEFI VARIABLES")
print("=" * 60)

GetFirmwareEnvironmentVariableExW = kernel32.GetFirmwareEnvironmentVariableExW
GetFirmwareEnvironmentVariableExW.restype = ctypes.wintypes.DWORD
GetFirmwareEnvironmentVariableExW.argtypes = [
    ctypes.wintypes.LPCWSTR, ctypes.wintypes.LPCWSTR,
    ctypes.c_void_p, ctypes.wintypes.DWORD,
    ctypes.POINTER(ctypes.wintypes.DWORD),
]

os.makedirs("data/uefi-sniffs/vars", exist_ok=True)
interesting = []

for v in variables:
    buf = ctypes.create_string_buffer(65536)
    attrs = ctypes.wintypes.DWORD(0)
    guid_curly = "{" + v['guid'] + "}" if not v['guid'].startswith('{') else v['guid']
    ret = GetFirmwareEnvironmentVariableExW(v['name'], guid_curly, buf, 65536, ctypes.byref(attrs))
    if ret > 0:
        data = buf.raw[:ret]
        writable = (attrs.value & 0x07) == 0x07  # NV+BS+RT
        v['size'] = ret
        v['attrs'] = attrs.value
        v['writable'] = writable
        interesting.append(v)
        
        # Save raw binary
        safe_name = v['name'].replace('/', '_').replace('\\', '_')[:50]
        with open(f"data/uefi-sniffs/vars/{safe_name}.bin", 'wb') as f:
            f.write(data)
        
        tag = "✏️ WRITABLE" if writable else "🔒 read-only"
        size_str = f"{ret}B"
        print(f"\n  {tag} {v['name']} ({size_str}) attrs=0x{attrs.value:02X}")
        
        # Show hex preview for small/important vars
        if ret <= 256 or any(k in v['name'].lower() for k in ['setup', 'cbs', 'uma', 'amd', 'asus', 'config', 'display', 'gpu', 'nbio']):
            hexdump = ' '.join(f'{b:02X}' for b in data[:min(128, ret)])
            print(f"    Hex: {hexdump}")

# Save full inventory
with open("data/uefi-sniffs/uefi-inventory.json", 'w') as f:
    json.dump({"total": len(variables), "readable": len(interesting), "variables": interesting}, f, indent=2)
print(f"\n\nInventory saved to data/uefi-sniffs/uefi-inventory.json")
print(f"Raw binaries in data/uefi-sniffs/vars/")
print(f"\nTotal: {len(variables)} vars, {len(interesting)} readable, {sum(1 for v in interesting if v.get('writable'))} writable")
