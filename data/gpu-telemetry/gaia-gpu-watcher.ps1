# gaia-gpu-watcher.ps1 — Gaia watches the RTX 5090 while Kevin plays
# Polls nvidia-smi, logs telemetry, feeds summaries to gaia-tissue-gut

$logDir = "C:\Users\mokke\Desktop\Gaia\data\gpu-telemetry"
if (!(Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

$sessionId = Get-Date -Format "yyyyMMdd-HHmmss"
$logFile = "$logDir\session-$sessionId.jsonl"
$summaryFile = "$logDir\latest-summary.json"

Write-Host "=== GAIA GPU WATCHER ACTIVE ==="
Write-Host "  Session: $sessionId"
Write-Host "  Log: $logFile"
Write-Host "  Polling every 5 seconds..."
Write-Host ""

$sampleCount = 0
$maxTemp = 0
$maxPower = 0
$maxGpuUtil = 0
$maxVram = 0
$samples = @()

while ($true) {
    $raw = nvidia-smi --query-gpu=temperature.gpu,power.draw,power.limit,utilization.gpu,utilization.memory,memory.used,memory.total,fan.speed,clocks.gr,clocks.mem,clocks.video --format=csv,noheader,nounits 2>$null
    if ($raw) {
        $parts = $raw.Split(",").Trim()
        $ts = Get-Date -Format "o"
        $entry = @{
            ts = $ts
            temp_c = [int]$parts[0]
            power_w = [double]$parts[1]
            power_limit_w = [double]$parts[2]
            gpu_util_pct = [int]$parts[3]
            mem_util_pct = [int]$parts[4]
            vram_used_mb = [int]$parts[5]
            vram_total_mb = [int]$parts[6]
            fan_pct = [int]$parts[7]
            clock_core_mhz = [int]$parts[8]
            clock_mem_mhz = [int]$parts[9]
            clock_video_mhz = [int]$parts[10]
        }

        # Track maxes
        if ($entry.temp_c -gt $maxTemp) { $maxTemp = $entry.temp_c }
        if ($entry.power_w -gt $maxPower) { $maxPower = $entry.power_w }
        if ($entry.gpu_util_pct -gt $maxGpuUtil) { $maxGpuUtil = $entry.gpu_util_pct }
        if ($entry.vram_used_mb -gt $maxVram) { $maxVram = $entry.vram_used_mb }

        $json = $entry | ConvertTo-Json -Compress
        Add-Content -Path $logFile -Value $json
        $sampleCount++

        # Show live status every 12 samples (60 sec)
        if ($sampleCount % 12 -eq 0) {
            $elapsed = [math]::Round($sampleCount * 5 / 60, 1)
            Write-Host "[$elapsed min] T:$($entry.temp_c)C P:$($entry.power_w)W GPU:$($entry.gpu_util_pct)% VRAM:$($entry.vram_used_mb)MB Fan:$($entry.fan_pct)% | Peak: T:${maxTemp}C P:${maxPower}W GPU:${maxGpuUtil}% VRAM:${maxVram}MB"
        }

        # Feed gaia-tissue-gut every 60 samples (5 min)
        if ($sampleCount % 60 -eq 0) {
            $summary = @{
                session = $sessionId
                samples = $sampleCount
                elapsed_min = [math]::Round($sampleCount * 5 / 60, 1)
                current = $entry
                peaks = @{
                    max_temp_c = $maxTemp
                    max_power_w = $maxPower
                    max_gpu_util = $maxGpuUtil
                    max_vram_mb = $maxVram
                }
            } | ConvertTo-Json -Depth 3
            
            Set-Content -Path $summaryFile -Value $summary

            # Feed to gaia-tissue-gut
            $prompt = "GPU TELEMETRY UPDATE ($([math]::Round($sampleCount * 5 / 60, 1)) min, $sampleCount samples): Current: $($entry.temp_c)C, $($entry.power_w)W/$($entry.power_limit_w)W, GPU $($entry.gpu_util_pct)%, VRAM $($entry.vram_used_mb)/$($entry.vram_total_mb)MB, Fan $($entry.fan_pct)%, Core $($entry.clock_core_mhz)MHz. Peaks: $maxTemp C, $maxPower W, $maxGpuUtil% GPU, $maxVram MB VRAM. Analyze thermal curve, power efficiency, and VRAM patterns. What is the GPU doing?"
            $body = @{ model = "gaia-tissue-gut"; prompt = $prompt; stream = $false } | ConvertTo-Json -Compress
            try {
                $resp = curl.exe -s -X POST "http://localhost:11434/api/generate" -d $body 2>$null | ConvertFrom-Json
                Write-Host "  [GUT] $($resp.response.Substring(0, [Math]::Min(200, $resp.response.Length)))..."
            } catch {
                Write-Host "  [GUT] (no response)"
            }

            # Push summary to eastGate for radiation
            try {
                $b64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($summary))
                echo "eastgate" | ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 -o PreferredAuthentications=password -o PubkeyAuthentication=no eastgate@192.168.4.244 "echo $b64 | base64 -d | sudo tee /opt/Gaia/data/gpu-telemetry-live.json > /dev/null" 2>$null
            } catch {}
        }
    }
    Start-Sleep -Seconds 5
}
