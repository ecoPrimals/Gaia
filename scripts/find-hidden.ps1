# FIND HIDDEN — Look for stuck windows, orphan processes, blocked device handles
Write-Host "=" * 60
Write-Host "  FIND HIDDEN — What's stuck/plugged?"
Write-Host "=" * 60

# 1. Hidden windows
Write-Host "`n--- Hidden/Invisible Windows ---"
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
using System.Collections.Generic;
public class WinEnum {
    [DllImport("user32.dll")] static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
    [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
    public static List<string> hidden = new List<string>();
    public static void Find() {
        EnumWindows(delegate(IntPtr hWnd, IntPtr lp) {
            if (!IsWindowVisible(hWnd)) {
                StringBuilder sb = new StringBuilder(256);
                GetWindowText(hWnd, sb, 256);
                string title = sb.ToString();
                if (title.Length > 0) {
                    uint pid = 0;
                    GetWindowThreadProcessId(hWnd, out pid);
                    hidden.Add(pid + " | " + title);
                }
            }
            return true;
        }, IntPtr.Zero);
    }
}
"@
[WinEnum]::Find()
$interesting = [WinEnum]::hidden | Where-Object { $_ -match 'frame|spore|gaia|steam|nvme|pci|disk|drive|storage|umaf|grub|usb' }
if ($interesting) {
    Write-Host "  Interesting hidden windows:"
    $interesting | ForEach-Object { Write-Host "    $_" }
} else {
    Write-Host "  No suspicious hidden windows with key names"
}
Write-Host ("  Total hidden windows with titles: " + [WinEnum]::hidden.Count)

# 2. Processes with device handles on NVMe
Write-Host "`n--- Processes touching storage devices ---"
$storageProcs = Get-Process | Where-Object { $_.HandleCount -gt 500 } | Sort-Object HandleCount -Descending | Select-Object -First 20
$storageProcs | Format-Table ProcessName, Id, HandleCount, WorkingSet64 -AutoSize

# 3. Stuck/zombie processes
Write-Host "`n--- Processes NOT responding ---"
Get-Process | Where-Object { $_.Responding -eq $false } | Format-Table ProcessName, Id, StartTime -AutoSize

# 4. Orphan device stacks
Write-Host "`n--- Devices with problem codes ---"
Get-PnpDevice | Where-Object { $_.Status -ne 'OK' -and $_.Status -ne 'Unknown' } | Format-Table FriendlyName, Status, Class, InstanceId -AutoSize

# 5. Device install state for NVMe
Write-Host "`n--- NVMe Device Install State ---"
$nvmeDevs = Get-PnpDevice | Where-Object { $_.InstanceId -match 'NVME|NVM|VEN_144D|VEN_15B7' }
foreach ($dev in $nvmeDevs) {
    Write-Host ("  " + $dev.FriendlyName + " [" + $dev.Status + "]")
    $props = Get-PnpDeviceProperty -InstanceId $dev.InstanceId -ErrorAction SilentlyContinue
    $installState = $props | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_InstallState' }
    $problem = $props | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_ProblemCode' }
    $problemStatus = $props | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_ProblemStatus' }
    $isPresent = $props | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_IsPresent' }
    $parent = $props | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_Parent' }
    $loc = $props | Where-Object { $_.KeyName -eq 'DEVPKEY_Device_LocationInfo' }
    Write-Host ("    InstallState: " + $installState.Data)
    Write-Host ("    ProblemCode: " + $problem.Data)
    Write-Host ("    ProblemStatus: " + $problemStatus.Data)
    Write-Host ("    IsPresent: " + $isPresent.Data)
    Write-Host ("    Parent: " + $parent.Data)
    Write-Host ("    Location: " + $loc.Data)
}

# 6. Check for frame/spore remnants
Write-Host "`n--- Frame/Spore/Steam remnants ---"
Get-Process | Where-Object { $_.ProcessName -match 'frame|spore|rustdesk|steam' } | Format-Table ProcessName, Id, Path -AutoSize

# 7. USB devices that might be blocking
Write-Host "`n--- USB devices in error state ---"
Get-PnpDevice -Class USB -ErrorAction SilentlyContinue | Where-Object { $_.Status -ne 'OK' } | Format-Table FriendlyName, Status, InstanceId -AutoSize

# 8. Check PCIe Root Port specifically 
Write-Host "`n--- PCIe Root Ports ---"
Get-PnpDevice | Where-Object { $_.FriendlyName -match 'Root Port|PCI Express' -and $_.Class -eq 'System' } | Format-Table FriendlyName, Status, InstanceId -AutoSize

Write-Host "`n" + "=" * 60
Write-Host "  HIDDEN SCAN COMPLETE"
Write-Host "=" * 60
