"""Map ALL UEFI variables — fixed UTF-16 parsing."""
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

# Enumerate
NtEnumerateSystemEnvironmentValuesEx = ntdll.NtEnumerateSystemEnvironmentValuesEx
NtEnumerateSystemEnvironmentValuesEx.restype = ctypes.c_long
NtEnumerateSystemEnvironmentValuesEx.argtypes = [ctypes.c_ulong, ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]

buf_size = ctypes.c_ulong(0)
NtEnumerateSystemEnvironmentValuesEx(1, None, ctypes.byref(buf_size))
buf = ctypes.create_string_buffer(buf_size.value)
status = NtEnumerateSystemEnvironmentValuesEx(1, buf, ctypes.byref(buf_size))
raw = buf.raw

variables = []
offset = 0

while offset < len(raw) - 24:
    next_offset = struct.unpack_from('<I', raw, offset)[0]
    guid_bytes = raw[offset+4:offset+20]
    
    # Format GUID
    d1, d2, d3 = struct.unpack_from('<IHH', guid_bytes, 0)
    d4 = guid_bytes[8:16]
    guid_str = f"{d1:08X}-{d2:04X}-{d3:04X}-{d4[:2].hex().upper()}-{d4[2:].hex().upper()}"
    
    # Parse UTF-16LE name starting at offset+20
    # Search for null WCHAR (0x0000) on 2-byte boundaries
    name_start = offset + 20
    pos = name_start
    while pos < len(raw) - 1:
        wchar = struct.unpack_from('<H', raw, pos)[0]
        if wchar == 0:
            break
        pos += 2
    
    try:
        name_bytes = raw[name_start:pos]
        name = name_bytes.decode('utf-16-le')
    except:
        name = f"<binary:{name_bytes[:20].hex()}>"
    
    variables.append({"name": name, "guid": guid_str})
    
    if next_offset == 0:
        break
    offset += next_offset

print(f"Total UEFI variables: {len(variables)}\n")

# Print ALL with categories
amd_cbs = []
asus_vars = []
setup_vars = []
all_names = []

for v in variables:
    nl = v['name'].lower()
    all_names.append(v['name'])
    if any(k in nl for k in ['amd', 'cbs', 'uma', 'nbio', 'zen', 'pbs', 'granite', 'strix']):
        amd_cbs.append(v)
    elif any(k in nl for k in ['asus', 'rog', 'aura', 'asio']):
        asus_vars.append(v)
    elif any(k in nl for k in ['setup', 'config', 'bios', 'custom', 'oem']):
        setup_vars.append(v)

print("─── ALL VARIABLE NAMES ───")
for v in variables:
    print(f"  {v['name']:50s} {{{v['guid']}}}")

if amd_cbs:
    print(f"\n═══ AMD/CBS/UMA ({len(amd_cbs)}) ═══")
    for v in amd_cbs:
        print(f"  {v['name']} {{{v['guid']}}}")

if asus_vars:
    print(f"\n═══ ASUS ({len(asus_vars)}) ═══")
    for v in asus_vars:
        print(f"  {v['name']} {{{v['guid']}}}")

if setup_vars:
    print(f"\n═══ Setup/Config ({len(setup_vars)}) ═══")
    for v in setup_vars:
        print(f"  {v['name']} {{{v['guid']}}}")

# Now READ them all
print(f"\n{'='*60}")
print("READING ALL VARIABLES")
print(f"{'='*60}\n")

GetVar = kernel32.GetFirmwareEnvironmentVariableExW
GetVar.restype = ctypes.wintypes.DWORD
GetVar.argtypes = [ctypes.wintypes.LPCWSTR, ctypes.wintypes.LPCWSTR,
                   ctypes.c_void_p, ctypes.wintypes.DWORD, ctypes.POINTER(ctypes.wintypes.DWORD)]

os.makedirs("data/uefi-sniffs/vars", exist_ok=True)
read_count = 0
write_count = 0
big_vars = []

for v in variables:
    vbuf = ctypes.create_string_buffer(262144)
    attrs = ctypes.wintypes.DWORD(0)
    guid_fmt = "{" + v['guid'] + "}"
    ret = GetVar(v['name'], guid_fmt, vbuf, 262144, ctypes.byref(attrs))
    if ret > 0:
        data = vbuf.raw[:ret]
        writable = (attrs.value & 0x01) != 0  # NV bit set
        read_count += 1
        if writable:
            write_count += 1
        
        safe = v['name'].replace('/', '_').replace('\\', '_').replace(' ', '_')[:60]
        with open(f"data/uefi-sniffs/vars/{safe}.bin", 'wb') as f:
            f.write(data)
        
        tag = "✏️" if writable else "🔒"
        print(f"{tag} {v['name']:45s} {ret:>6}B  attrs=0x{attrs.value:02X}  {{{v['guid'][:13]}...}}")
        
        if ret > 100:
            big_vars.append({"name": v['name'], "guid": v['guid'], "size": ret, "writable": writable})
        
        # Extra detail for potentially interesting vars
        nl = v['name'].lower()
        if any(k in nl for k in ['setup', 'cbs', 'amd', 'uma', 'nbio', 'config', 'asus', 'custom', 'oem']) or ret > 1000:
            hexline = ' '.join(f'{b:02X}' for b in data[:96])
            print(f"     [{hexline}]")

print(f"\n{'='*60}")
print(f"SUMMARY: {len(variables)} total, {read_count} readable, {write_count} NV (persistent)")
print(f"Large vars (>100B): {len(big_vars)}")
for bv in big_vars:
    print(f"  {'✏️' if bv['writable'] else '🔒'} {bv['name']} = {bv['size']}B")
