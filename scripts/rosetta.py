"""Decode BiosSettingMappingTableV2 — the Rosetta Stone of ASUS BIOS.
This maps BIOS option names to UEFI variable byte offsets."""
import ctypes, ctypes.wintypes, struct, json, os

kernel32 = ctypes.windll.kernel32
advapi32 = ctypes.windll.advapi32

# Enable privilege
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
advapi32.OpenProcessToken(kernel32.GetCurrentProcess(), 0x0028, ctypes.byref(token))
luid = LUID()
advapi32.LookupPrivilegeValueW(None, "SeSystemEnvironmentPrivilege", ctypes.byref(luid))
tp = TOKEN_PRIVILEGES()
tp.PrivilegeCount = 1
tp.Privileges[0].Luid = luid
tp.Privileges[0].Attributes = 0x00000002
advapi32.AdjustTokenPrivileges(token, False, ctypes.byref(tp), 0, None, None)

GetVar = kernel32.GetFirmwareEnvironmentVariableExW
GetVar.restype = ctypes.wintypes.DWORD
GetVar.argtypes = [ctypes.wintypes.LPCWSTR, ctypes.wintypes.LPCWSTR,
                   ctypes.c_void_p, ctypes.wintypes.DWORD, ctypes.POINTER(ctypes.wintypes.DWORD)]

# Read the mapping table
print("=" * 60)
print("ROSETTA STONE — BiosSettingMappingTableV2")
print("=" * 60)

buf = ctypes.create_string_buffer(65536)
attrs = ctypes.wintypes.DWORD(0)
ret = GetVar("BiosSettingMappingTableV2", "{B57086D5-C2E5-4654-9E3A-0B55830FBB32}", buf, 65536, ctypes.byref(attrs))
print(f"Size: {ret} bytes, attrs=0x{attrs.value:02X}\n")

if ret == 0:
    print("FAILED to read mapping table!")
    exit(1)

data = buf.raw[:ret]

# Save raw binary
os.makedirs("data/uefi-sniffs/vars", exist_ok=True)
with open("data/uefi-sniffs/vars/BiosSettingMappingTableV2.bin", 'wb') as f:
    f.write(data)

# Dump hex for analysis
print("First 256 bytes hex dump:")
for i in range(0, min(256, len(data)), 16):
    hex_part = ' '.join(f'{data[i+j]:02X}' for j in range(min(16, len(data)-i)))
    ascii_part = ''.join(chr(data[i+j]) if 32 <= data[i+j] < 127 else '.' for j in range(min(16, len(data)-i)))
    print(f"  {i:04X}: {hex_part:<48s} {ascii_part}")

# Try to find embedded strings
print("\n\nSearching for embedded strings (option names)...")
strings_found = []
i = 0
while i < len(data) - 4:
    # Look for printable ASCII runs of 4+ chars
    start = i
    while i < len(data) and 32 <= data[i] < 127:
        i += 1
    if i - start >= 4:
        s = data[start:i].decode('ascii')
        strings_found.append((start, s))
    i += 1

if strings_found:
    print(f"\nFound {len(strings_found)} strings:\n")
    for offset, s in strings_found:
        tag = ""
        sl = s.lower()
        if any(k in sl for k in ['uma', 'frame', 'buffer', 'igpu', 'integrated', 'graphics']):
            tag = " <<<< UMA/iGPU!"
        elif any(k in sl for k in ['primary', 'video', 'display', 'vga']):
            tag = " <<<< DISPLAY!"
        elif any(k in sl for k in ['pcie', 'link', 'gen5', 'gen4']):
            tag = " <<<< PCIe!"
        elif any(k in sl for k in ['nbio', 'persistence', 'legacy']):
            tag = " <<<< NBIO/LEGACY!"
        print(f"  0x{offset:04X}: {s}{tag}")
else:
    print("  No ASCII strings found — trying UTF-16...")
    # Try UTF-16LE strings
    i = 0
    while i < len(data) - 8:
        start = i
        chars = []
        while i < len(data) - 1:
            wchar = struct.unpack_from('<H', data, i)[0]
            if 32 <= wchar < 127:
                chars.append(chr(wchar))
                i += 2
            else:
                break
        if len(chars) >= 4:
            s = ''.join(chars)
            strings_found.append((start, s))
        else:
            i += 2 if i == start else 0
        i = max(i, start + 2)
    
    print(f"\nFound {len(strings_found)} UTF-16 strings:")
    for offset, s in strings_found:
        print(f"  0x{offset:04X}: {s}")

# Also look for the mapping structure
print("\n\n" + "=" * 60)
print("STRUCTURE ANALYSIS")
print("=" * 60)

# Check if it starts with a header
header = struct.unpack_from('<IHHHH', data, 0)
print(f"\nHeader words: {[f'0x{x:X}' for x in header]}")

# Look for repeating patterns (entry size)
print("\nLooking for entry patterns...")
# Each mapping entry likely contains: option_id, variable_guid_index, offset, size, type
# Try different entry sizes
for entry_size in [8, 10, 12, 14, 16, 20, 22, 24]:
    if (ret - 4) % entry_size == 0:
        n_entries = (ret - 4) // entry_size
        if 10 < n_entries < 500:
            print(f"  Entry size {entry_size}: {n_entries} entries (possible)")

# Also read the main BIOS variables for comparison
print("\n\n" + "=" * 60)
print("MAIN BIOS STORES — Reading for UMA hunt")
print("=" * 60)

for vname, vguid in [
    ("Setup", "{EC87D643-EBA4-4BB5-A1E5-3F3E36B20DA9}"),
    ("AmdSetupPHX", "{3A997502-647A-4C82-998E-52EF9486A247}"),
    ("AmdSetupRPL", "{3A997502-647A-4C82-998E-52EF9486A247}"),
    ("AMD_PBS_SETUP", "{A339D746-F678-49B3-9FC7-54CE0F9DF226}"),
]:
    vbuf = ctypes.create_string_buffer(65536)
    vattrs = ctypes.wintypes.DWORD(0)
    vret = GetVar(vname, vguid, vbuf, 65536, ctypes.byref(vattrs))
    if vret > 0:
        vdata = vbuf.raw[:vret]
        with open(f"data/uefi-sniffs/vars/{vname}.bin", 'wb') as f:
            f.write(vdata)
        
        print(f"\n{vname}: {vret} bytes, attrs=0x{vattrs.value:02X}")
        
        # Search for 0xFF 0xFF 0xFF 0xFF (Auto/unset value for UMA)
        ff_positions = []
        for p in range(len(vdata) - 3):
            if vdata[p:p+4] == b'\xFF\xFF\xFF\xFF':
                ff_positions.append(p)
        if ff_positions:
            print(f"  0xFFFFFFFF (Auto) found at offsets: {[f'0x{p:X}' for p in ff_positions[:20]]}")
        
        # Dump first 128 bytes
        for i in range(0, min(128, len(vdata)), 16):
            hex_part = ' '.join(f'{vdata[i+j]:02X}' for j in range(min(16, len(vdata)-i)))
            ascii_part = ''.join(chr(vdata[i+j]) if 32 <= vdata[i+j] < 127 else '.' for j in range(min(16, len(vdata)-i)))
            print(f"  {i:04X}: {hex_part:<48s} {ascii_part}")

# Now read StdDefaults to compare
print("\n\nReading StdDefaults for comparison...")
sbuf = ctypes.create_string_buffer(65536)
sret = GetVar("StdDefaults", "{4599D26F-1A11-49B8-B91F-858745CFF824}", sbuf, 65536, ctypes.byref(attrs))
if sret > 0:
    with open("data/uefi-sniffs/vars/StdDefaults.bin", 'wb') as f:
        f.write(sbuf.raw[:sret])
    print(f"  StdDefaults: {sret} bytes saved")
