# Fix songBird — start it properly
$songbird = "C:\Users\mokke\Desktop\Gaia\plasmidBin\primals\songbird.exe"

Write-Host "--- Starting songBird ---"
Write-Host "  Binary: $songbird"
Write-Host "  Size: $((Get-Item $songbird).Length / 1KB) KB"

# Try running it to see what args it wants
$proc = Start-Process -FilePath $songbird -ArgumentList "server","--socket","C:\Users\mokke\Desktop\Gaia\runtime\membrane\songbird-gaia-pi.sock" -PassThru -WindowStyle Hidden -RedirectStandardError "C:\Users\mokke\Desktop\Gaia\runtime\membrane\songbird-err.txt"
Start-Sleep 3

if ($proc -and -not $proc.HasExited) {
    Write-Host "  songBird ALIVE! PID=$($proc.Id)"
    $proc.Id | Out-File "C:\Users\mokke\Desktop\Gaia\runtime\membrane\songbird-gaia-pi.pid" -NoNewline
    Write-Host "  PID written to membrane"
} else {
    Write-Host "  songBird exited. Checking error..."
    if (Test-Path "C:\Users\mokke\Desktop\Gaia\runtime\membrane\songbird-err.txt") {
        Get-Content "C:\Users\mokke\Desktop\Gaia\runtime\membrane\songbird-err.txt" | Select-Object -First 10
    }
    
    Write-Host "`n  Trying without args..."
    $proc2 = Start-Process -FilePath $songbird -PassThru -WindowStyle Hidden
    Start-Sleep 3
    if ($proc2 -and -not $proc2.HasExited) {
        Write-Host "  songBird ALIVE (no args)! PID=$($proc2.Id)"
        $proc2.Id | Out-File "C:\Users\mokke\Desktop\Gaia\runtime\membrane\songbird-gaia-pi.pid" -NoNewline
    } else {
        Write-Host "  songBird won't stay up"
        Write-Host "  Checking what help says:"
        & $songbird --help 2>&1 | Select-Object -First 15
    }
}

# Final count
Write-Host "`n--- ALL primals now ---"
Get-Process | Where-Object { $_.ProcessName -match 'biome|beardog|songbird|barracuda|skunkbat|squirrel|nestgate|coralreef|loamspine|rhizocrypt|swarmvine|sweetgrass|toadstool|petaltongue|gaia-hands' } | Group-Object ProcessName | Select-Object Count, Name | Sort-Object Name | Format-Table -AutoSize
