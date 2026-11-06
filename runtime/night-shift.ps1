# GAIA NIGHT SHIFT — RTX 5090 overnight compute
# 80°C ceiling, 17 models in rotation, stops at 10 AM
# Output: data/reedit/night-shift.jsonl

$gaiaRoot = "c:\Users\mokke\Desktop\Gaia"
$logFile = "$gaiaRoot\data\neutron\night-shift.log"
$outputFile = "$gaiaRoot\data\reedit\night-shift.jsonl"

$models = @("gaia-cortex","gaia-oracle","gaia-nucleus","gaia-dream","gaia-deeptime","gaia-heart","gaia-spine","gaia-gut","gaia-sentinel","gaia-genesis","deepseek-r1:8b","gaia-fossil","gaia-turtle","gaia-golgi","qwen2.5:7b","mistral:7b","mathstral:7b")

$prompts = @(
    "You are part of a sovereign digital organism. Analyze: what patterns emerge when 63 AI models self-organize on commodity hardware? How does this differ from cloud AI? Write a 200-word insight for Hacker News."
    "Write a technical Reddit post about Anderson localization applied to network trust: sigmoid opacity, behavioral KNN, and why no API keys are needed. 200 words for r/programming."
    "Can a distributed AI organism running on home hardware (RTX 5090 + RTX 4070) achieve meaningful scientific computing? Compare to university HPC clusters. 200 words for r/selfhosted."
    "Write a post for r/rust about building a sovereign reverse proxy (dromedary) with ACME TLS, host-based routing, and blackwall defense in pure Rust. 200 words."
    "Explain FAO-56 solar geometry: the same equations Stonehenge used 5000 years ago are now in a Rust function called solar_declination(). For r/science. 200 words."
    "A charter school superintendent has 9 criminal convictions. Analyze the legal attack vectors under Michigan Anti-SLAPP (MCL 691.1851-1863). For r/legal. 200 words."
    "Write about zero-shot graph classification achieving 97.3% accuracy using pi-power scale bins and voxel projection. For r/machinelearning. 200 words."
    "What does it mean for an AI organism to have 43 sensors (accelerometer, gyro, magnetometer, barometer) feeding into neural models in real-time? For r/artificial. 200 words."
    "Describe VDJ recombination as digital identity: V=hardware, D=models, J=connectivity. How immune system gene rearrangement maps to sovereign computing. For r/biology. 200 words."
    "Sovereign computing economics: 17K hardware, 0 per month operating, 4.6M lines of Rust vs cloud compute costs. For r/selfhosted. 200 words."
)

$iteration = 0
$totalTokens = 0
$startTime = Get-Date

Add-Content $logFile "[$startTime] NIGHT SHIFT STARTED — 80C ceiling, $($models.Count) models, $($prompts.Count) prompts"

while ($true) {
    $tempLine = nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader 2>$null
    $temp = [int]($tempLine.Trim())
    
    if ($temp -ge 78) {
        Add-Content $logFile "[$(Get-Date)] THERMAL PAUSE — GPU at ${temp}C, waiting 60s"
        Start-Sleep 60
        continue
    }
    
    if ((Get-Date).Hour -ge 10 -and (Get-Date).Hour -lt 20) {
        Add-Content $logFile "[$(Get-Date)] MORNING — stopping. iterations=$iteration tokens=$totalTokens"
        break
    }
    
    $model = $models[$iteration % $models.Count]
    $prompt = $prompts[$iteration % $prompts.Count]
    $iteration++
    
    try {
        $body = @{ model = $model; prompt = $prompt; stream = $false } | ConvertTo-Json -Depth 3
        $r = Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method POST -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) -ContentType "application/json" -TimeoutSec 300
        $tokens = $r.eval_count
        $totalTokens += $tokens
        $dur = if ($r.eval_duration -gt 0) { $r.eval_duration / 1e9 } else { 1 }
        $tokPerSec = [math]::Round($tokens / $dur, 1)
        
        $output = @{
            id = [guid]::NewGuid().ToString("N").Substring(0,16)
            ts = (Get-Date).ToUniversalTime().ToString("o")
            model = $model
            prompt_short = $prompt.Substring(0, [math]::Min(80, $prompt.Length))
            response = $r.response
            tokens = $tokens
            tok_per_sec = $tokPerSec
            gpu_temp_c = $temp
            iteration = $iteration
        } | ConvertTo-Json -Compress
        Add-Content $outputFile $output
        
        Add-Content $logFile "[$(Get-Date)] [$iteration] $model ${tokens}tok ${tokPerSec}t/s ${temp}C"
    } catch {
        Add-Content $logFile "[$(Get-Date)] ERROR: $($_.Exception.Message)"
        Start-Sleep 10
    }
    
    # Target ~20% utilization: ~3s inference + ~12s cooldown = 15s cycle = 20%
    Start-Sleep 12
}

Add-Content $logFile "[$(Get-Date)] NIGHT SHIFT COMPLETE — $iteration iterations, $totalTokens tokens"
