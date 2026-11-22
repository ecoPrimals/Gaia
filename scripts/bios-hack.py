"""Try every possible BIOS option name + read PCI config"""
import subprocess

print("=== BIOS OPTION DISCOVERY ===\n")

# Try many possible option name variations
names = [
    # UMA variations
    "UMAFrameBufferSize", "UMA Frame Buffer Size", "UMA FB Size", 
    "UmaFrameBufferSize", "UmaFbSize", "UMA_FRAME_BUFFER_SIZE",
    "UMA Mode", "UMAMode",
    # iGPU variations  
    "IntegratedGraphics", "Integrated Graphics", "IGFX", "iGPU",
    "IGD", "InternalGraphics", "Internal Graphics",
    "Initiate Graphic Adapter", "Primary Display",
    # Primary video
    "PrimaryVideoDevice", "Primary Video Device", "PrimaryDisplay",
    "Primary Video", "PrimaryVideo",
    # PCIe
    "Above4GDecoding", "Above 4G Decoding",
    "ResizableBAR", "Re-Size BAR Support", "ReBar",
    # Try numeric/encoded names
    "Setup_NB_IGD", "Setup_NB_UMA", "GFX_UMA",
]

print("Trying option names against ASUS WMI...\n")
for name in names:
    cmd = f'''
    $inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement
    $result = Invoke-CimMethod -InputObject $inst -MethodName "GetOptionData" -Arguments @{{ OptionName = "{name}" }}
    if ($result.ErrorCode -ne 14) {{
        Write-Output "  HIT: '{name}' = Value=$($result.Value) Error=$($result.ErrorCode)"
    }}
    '''
    r = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, timeout=5)
    out = r.stdout.strip()
    if out and 'HIT' in out:
        print(out)

# Try reading from PCI config space using ASUS WMI  
print("\n=== PCI Config Space Read — Bus 123 Device 0 ===\n")
# asio_hw_fun11: Read PCI config (Bus, Dev, Func, Reg, Width) -> dwData
for func in range(5):
    for reg in [0, 4, 8, 0x0C, 0x10, 0x14, 0x2C]:
        cmd = f'''
        $inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement
        $result = Invoke-CimMethod -InputObject $inst -MethodName "asio_hw_fun11" -Arguments @{{ Bus = [byte]123; Dev = [byte]0; Func = [byte]{func}; Reg = [uint16]{reg}; Width = [byte]4 }}
        $data = $result.dwData
        if ($data -ne 0 -and $data -ne 4294967295) {{
            Write-Output "Bus123 Dev0 Func{func} Reg 0x{reg:02X}: 0x$($data.ToString('X8'))"
        }}
        '''
        r = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, timeout=5)
        out = r.stdout.strip()
        if out:
            print(f"  {out}")

print("\n=== Bus 0 Device 8 (iGPU root port) ===\n")
for func in [0, 1]:
    for reg in [0, 4, 8, 0x0C, 0x18, 0x19, 0x1A]:
        cmd = f'''
        $inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement
        $result = Invoke-CimMethod -InputObject $inst -MethodName "asio_hw_fun11" -Arguments @{{ Bus = [byte]0; Dev = [byte]8; Func = [byte]{func}; Reg = [uint16]{reg}; Width = [byte]4 }}
        $data = $result.dwData
        if ($data -ne 0 -and $data -ne 4294967295) {{
            Write-Output "Bus0 Dev8 Func{func} Reg 0x{reg:02X}: 0x$($data.ToString('X8'))"
        }}
        '''
        r = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, timeout=5)
        out = r.stdout.strip()
        if out:
            print(f"  {out}")

print("\nDone!")
