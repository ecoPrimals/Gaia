# eye-gap.ps1 — tune the gap between the eyes: shift one monitor's position on the virtual desktop.
# Only the position changes (resolution, orientation and which GPU drives it are untouched).
#   eye-gap.ps1                 show the eyes and the current gap
#   eye-gap.ps1 -Dy -40         move the left eye 40 px up   (+ = down)
#   eye-gap.ps1 -Dx 20          move the left eye 20 px right
#   eye-gap.ps1 -Eye right ...  move the right eye instead (it is primary; Windows re-anchors at 0,0)
param([int]$Dx = 0, [int]$Dy = 0, [ValidateSet('left', 'right')][string]$Eye = 'left')

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public static class EyeGap {
    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    public struct DEVMODE {
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)] public string dmDeviceName;
        public short dmSpecVersion, dmDriverVersion, dmSize, dmDriverExtra;
        public int dmFields, dmPositionX, dmPositionY, dmDisplayOrientation, dmDisplayFixedOutput;
        public short dmColor, dmDuplex, dmYResolution, dmTTOption, dmCollate;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)] public string dmFormName;
        public short dmLogPixels;
        public int dmBitsPerPel, dmPelsWidth, dmPelsHeight, dmDisplayFlags, dmDisplayFrequency;
        public int dmICMMethod, dmICMIntent, dmMediaType, dmDitherType, dmReserved1, dmReserved2, dmPanningWidth, dmPanningHeight;
    }
    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    public static extern bool EnumDisplaySettings(string dev, int mode, ref DEVMODE dm);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    public static extern int ChangeDisplaySettingsEx(string dev, ref DEVMODE dm, IntPtr hwnd, int flags, IntPtr param);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    public static extern int ChangeDisplaySettingsEx(string dev, IntPtr dm, IntPtr hwnd, int flags, IntPtr param);
}
"@

Add-Type -AssemblyName System.Windows.Forms
$right = [System.Windows.Forms.Screen]::PrimaryScreen
$left = [System.Windows.Forms.Screen]::AllScreens | Where-Object { -not $_.Primary } | Select-Object -First 1
if (-not $left) { Write-Host "Only one eye is open ($($right.DeviceName)). Nothing to tune."; exit 1 }
"right eye  $($right.DeviceName)  at ($($right.Bounds.X),$($right.Bounds.Y))  $($right.Bounds.Width)x$($right.Bounds.Height)"
"left eye   $($left.DeviceName)  at ($($left.Bounds.X),$($left.Bounds.Y))  $($left.Bounds.Width)x$($left.Bounds.Height)"
"gap        ($($left.Bounds.X - $right.Bounds.X), $($left.Bounds.Y - $right.Bounds.Y))"
if ($Dx -eq 0 -and $Dy -eq 0) { exit 0 }

$target = if ($Eye -eq 'left') { $left } else { $right }
$dm = New-Object EyeGap+DEVMODE; $dm.dmSize = [Runtime.InteropServices.Marshal]::SizeOf($dm)
if (-not [EyeGap]::EnumDisplaySettings($target.DeviceName, -1, [ref]$dm)) { Write-Host "cannot read $($target.DeviceName)"; exit 1 }
$dm.dmPositionX += $Dx; $dm.dmPositionY += $Dy
$dm.dmFields = 0x20   # DM_POSITION only
$CDS_UPDATEREGISTRY = 0x01; $CDS_NORESET = 0x10000000
$r = [EyeGap]::ChangeDisplaySettingsEx($target.DeviceName, [ref]$dm, [IntPtr]::Zero, ($CDS_UPDATEREGISTRY -bor $CDS_NORESET), [IntPtr]::Zero)
if ($r -ne 0) { Write-Host "Windows refused the move (code $r)"; exit 1 }
[void][EyeGap]::ChangeDisplaySettingsEx($null, [IntPtr]::Zero, [IntPtr]::Zero, 0, [IntPtr]::Zero)
Start-Sleep -Milliseconds 800
$l2 = [System.Windows.Forms.Screen]::AllScreens | Where-Object { $_.DeviceName -eq $left.DeviceName }
$r2 = [System.Windows.Forms.Screen]::PrimaryScreen
"moved $Eye by ($Dx,$Dy); gap now ($($l2.Bounds.X - $r2.Bounds.X), $($l2.Bounds.Y - $r2.Bounds.Y))"
