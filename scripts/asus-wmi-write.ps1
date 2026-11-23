# ASUS WMI WRITE — Set all UEFI options before reboot
# sourDough: bone -> WRITE -> reboot -> compare -> evolve
$gutDir = "c:\Users\mokke\Desktop\Gaia\data\gut"
$ts = Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"

Write-Host "=== ASUS WMI — WRITING UEFI SETTINGS ===" -ForegroundColor Cyan
Write-Host "  Timestamp: $ts`n"

$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement

$changes = @(
    @{name="AboveForGBMemorySupport"; target=1; reason="Unlock 4TB NVMe mapping"},
    @{name="FastBoot";                target=0; reason="Full PCIe init (find ghost NVMe)"},
    @{name="SmtMode";                 target=1; reason="Enable SMT (8T -> 16T)"},
    @{name="SmtControl";              target=1; reason="SMT control enable"},
    @{name="CpuMultiThreading";       target=1; reason="Multi-threading on"},
    @{name="ResizableBarSupport";     target=1; reason="ReBAR for RTX 5090"},
    @{name="AmdReBar";                target=1; reason="AMD ReBAR enable"},
    @{name="IntegratedGraphics";      target=1; reason="iGPU Force enable"},
    @{name="SvmMode";                 target=1; reason="AMD-V virtualization"},
    @{name="IommuSupport";            target=1; reason="IOMMU for passthrough"}
)

$results = @()
$success = 0
$failed = 0

foreach ($c in $changes) {
    $name = $c.name
    $target = $c.target

    # Read BEFORE
    $before = Invoke-CimMethod -InputObject $inst -MethodName GetOptionData -Arguments @{OptionName=$name}
    $beforeVal = $before.Value
    $beforeErr = $before.ErrorCode

    if ($beforeVal -eq $target) {
        Write-Host "  SKIP $name = $target (already set)" -ForegroundColor DarkGray
        $results += @{name=$name; before=$beforeVal; after=$beforeVal; status="already_set"; reason=$c.reason}
        continue
    }

    # WRITE
    Write-Host "  WRITE $name : $beforeVal -> $target  ($($c.reason))" -ForegroundColor Yellow -NoNewline
    $writeResult = Invoke-CimMethod -InputObject $inst -MethodName SetOptionData -Arguments @{OptionName=$name; Value=[uint32]$target}
    $writeErr = $writeResult.ErrorCode

    # Read AFTER
    $after = Invoke-CimMethod -InputObject $inst -MethodName GetOptionData -Arguments @{OptionName=$name}
    $afterVal = $after.Value

    if ($afterVal -eq $target) {
        Write-Host "  OK!" -ForegroundColor Green
        $success++
        $results += @{name=$name; before=$beforeVal; after=$afterVal; status="written"; error_code=$writeErr; reason=$c.reason}
    } else {
        Write-Host "  FAIL (got $afterVal, err=$writeErr)" -ForegroundColor Red
        $failed++
        $results += @{name=$name; before=$beforeVal; after=$afterVal; status="failed"; error_code=$writeErr; reason=$c.reason}
    }
}

# Summary
Write-Host "`n=== RESULTS ===" -ForegroundColor Cyan
Write-Host "  Written: $success" -ForegroundColor Green
Write-Host "  Failed:  $failed" -ForegroundColor $(if($failed -gt 0){"Red"}else{"Green"})
Write-Host "  Skipped: $($results.Count - $success - $failed)" -ForegroundColor DarkGray

Write-Host "`n--- Full read-back ---"
foreach ($c in $changes) {
    $r = Invoke-CimMethod -InputObject $inst -MethodName GetOptionData -Arguments @{OptionName=$c.name}
    $ok = if($r.Value -eq $c.target){"OK"}else{"MISMATCH"}
    $color = if($ok -eq "OK"){"Green"}else{"Red"}
    Write-Host "  $($c.name) = $($r.Value) (target=$($c.target)) [$ok]" -ForegroundColor $color
}

# Save results
$report = @{
    ts = $ts
    phase = "pre-reboot-write"
    wave = 233
    success = $success
    failed = $failed
    results = $results
}
$report | ConvertTo-Json -Depth 3 | Out-File "$gutDir\asus-wmi-write-results.json" -Encoding utf8
Write-Host "`n  Results: $gutDir\asus-wmi-write-results.json"

if ($failed -eq 0) {
    Write-Host "`n  READY TO REBOOT — All settings written. Restart to apply." -ForegroundColor Green
} else {
    Write-Host "`n  WARNING: $failed writes failed. Check before rebooting." -ForegroundColor Red
}
