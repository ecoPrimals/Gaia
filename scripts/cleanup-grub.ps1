# Clean up grub.cfg files + restore safe wrapper
mountvol Z: /S 2>$null
$files = @(
    "Z:\grub.cfg", "Z:\boot\grub\grub.cfg", "Z:\boot\grub\x86_64-efi\grub.cfg",
    "Z:\EFI\tools\grub.cfg", "Z:\EFI\boot\grub.cfg", "Z:\EFI\gaia\grub.cfg",
    "Z:\grub\grub.cfg", "Z:\EFI\BOOT\grub\grub.cfg"
)
foreach ($f in $files) {
    if (Test-Path $f) { Remove-Item $f -Force; Write-Host "  Cleaned: $f" }
}

# Restore safe wrapper (defaults to Windows, 2s timeout)
Copy-Item "c:\Users\mokke\Desktop\Gaia\data\gut\gaia-boot-wrapper.efi" "Z:\EFI\gaia\gaia-boot-wrapper.efi" -Force
Write-Host "  Restored safe wrapper (default=Windows, 2s timeout)"

# Ferment the lesson
$lesson = @{
    timestamp = (Get-Date -Format o)
    cycle = 3
    experiment = "auto-fire: wrapper(timeout=0) -> chainload modGRUBShell + grub.cfg in 8 locations"
    result = "HUNG — modGRUBShell does NOT auto-load grub.cfg from ANY path"
    zk_fact = "modGRUBShell ALWAYS drops to interactive shell. normal module exists but is not auto-invoked. grub.cfg at prefix, root, boot/grub, EFI/tools — NONE work."
    lesson = "modGRUBShell = manual-only tool. Auto-execute needs either: (1) custom GRUB with setup_var compiled from source, (2) ASUS WMI SetOptionData with correct names, (3) UEFI Shell with setvar command"
}
$lesson | ConvertTo-Json -Depth 3 | Out-File "c:\Users\mokke\Desktop\Gaia\data\gut\sourdough-lesson-cycle3.json" -Encoding utf8
Write-Host "  Lesson fermented: sourdough-lesson-cycle3.json"
Write-Host "`nBoot is SAFE. Windows first. GAIA wrapper in F4 menu."
