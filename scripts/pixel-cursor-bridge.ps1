# pixel-cursor-bridge.ps1 — Pixel touch → Windows mouse cursor
# Sovereign ADB bridge. No installs. Pure pipe.
# 
# Reads multitouch events from Pixel's goodix_ts0 touchscreen
# Translates X/Y coordinates → Windows mouse position + clicks
#
# Pixel: 1080 x 2400 (portrait)
# We use the bottom ~1080x1080 square as the trackpad zone
#
# Usage: .\pixel-cursor-bridge.ps1
# Requires: ADB connected to Pixel (USB or WiFi)

param(
    [string]$Serial = "44251JEKB04957",
    [int]$PixelW = 1080,
    [int]$PixelH = 2400,
    [int]$TrackpadTop = 600,    # Top of trackpad zone (below status bar area)
    [int]$TrackpadBottom = 2400,
    [switch]$Relative           # Use relative mode (like a trackpad) vs absolute
)

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class MouseBridge {
    [DllImport("user32.dll")]
    public static extern bool SetCursorPos(int X, int Y);
    
    [DllImport("user32.dll")]
    public static extern void mouse_event(uint dwFlags, int dx, int dy, uint dwData, IntPtr dwExtraInfo);
    
    [DllImport("user32.dll")]
    public static extern bool GetCursorPos(out POINT lpPoint);
    
    [StructLayout(LayoutKind.Sequential)]
    public struct POINT { public int X; public int Y; }
    
    public const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
    public const uint MOUSEEVENTF_LEFTUP = 0x0004;
    public const uint MOUSEEVENTF_RIGHTDOWN = 0x0008;
    public const uint MOUSEEVENTF_RIGHTUP = 0x0010;
}
"@

$screenW = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width
$screenH = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height

Write-Host "=== PIXEL CURSOR BRIDGE ==="
Write-Host "  Pixel: ${PixelW}x${PixelH}"
Write-Host "  Screen: ${screenW}x${screenH}"
Write-Host "  Trackpad zone: Y=${TrackpadTop}-${TrackpadBottom}"
Write-Host "  Mode: $(if ($Relative) {'relative (trackpad)'} else {'absolute (touch screen)'})"
Write-Host "  Serial: $Serial"
Write-Host ""
Write-Host "  Touch the Pixel screen to move the cursor!"
Write-Host "  Tap = click. Two-finger tap = right-click."
Write-Host "  Press Ctrl+C to stop."
Write-Host ""

$trackpadH = $TrackpadBottom - $TrackpadTop

$process = Start-Process -FilePath "adb" -ArgumentList "-s $Serial shell getevent -lt /dev/input/event2" `
    -RedirectStandardOutput "$env:TEMP\pixel_touch.txt" `
    -NoNewWindow -PassThru

$lastX = 0; $lastY = 0; $touching = $false; $slots = 0

try {
    $stream = [System.IO.File]::Open("$env:TEMP\pixel_touch.txt", 'Open', 'Read', 'ReadWrite')
    $reader = New-Object System.IO.StreamReader($stream)
    
    while ($true) {
        $line = $reader.ReadLine()
        if ($null -eq $line) { Start-Sleep -Milliseconds 5; continue }
        
        if ($line -match "ABS_MT_POSITION_X\s+(\w+)") {
            $lastX = [Convert]::ToInt32($matches[1], 16)
        }
        elseif ($line -match "ABS_MT_POSITION_Y\s+(\w+)") {
            $lastY = [Convert]::ToInt32($matches[1], 16)
            
            if ($lastY -ge $TrackpadTop -and $lastY -le $TrackpadBottom) {
                $normX = $lastX / $PixelW
                $normY = ($lastY - $TrackpadTop) / $trackpadH
                $winX = [int]($normX * $screenW)
                $winY = [int]($normY * $screenH)
                [MouseBridge]::SetCursorPos($winX, $winY)
            }
        }
        elseif ($line -match "BTN_TOUCH\s+DOWN") {
            $touching = $true
            [MouseBridge]::mouse_event([MouseBridge]::MOUSEEVENTF_LEFTDOWN, 0, 0, 0, [IntPtr]::Zero)
        }
        elseif ($line -match "BTN_TOUCH\s+UP") {
            $touching = $false
            [MouseBridge]::mouse_event([MouseBridge]::MOUSEEVENTF_LEFTUP, 0, 0, 0, [IntPtr]::Zero)
        }
    }
} finally {
    if ($reader) { $reader.Close() }
    if ($stream) { $stream.Close() }
    if ($process -and !$process.HasExited) { $process.Kill() }
    Write-Host "`n  Bridge stopped."
}
