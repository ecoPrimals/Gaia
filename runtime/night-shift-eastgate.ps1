# GAIA NIGHT SHIFT — eastGate RTX 4070
# Fires through /v1/chat/completions on :8443
# ~20% utilization, 80°C ceiling (monitored via response time)
# Stops at 10 AM

$eastgate = "http://192.168.4.244:8443"
$logFile = "c:\Users\mokke\Desktop\Gaia\data\neutron\night-shift-eastgate.log"
$outputFile = "c:\Users\mokke\Desktop\Gaia\data\reedit\night-shift-eastgate.jsonl"

$models = @("gaia","gaia-code","gaia-fast","gaia-think","gaia-immune","gaia-navigator","gaia-gen1","exoPrimal","metaPrimal","mythoPrimal")

$prompts = @(
    "You are part of a sovereign digital organism running on eastGate (RTX 4070, 64GB RAM). Write a 200-word technical insight about self-hosted AI for Hacker News."
    "Write a 200-word post about biological defense systems in software: how skunkBat uses adaptive immunity to detect and poison scrapers. For r/netsec."
    "Explain how a Rust reverse proxy (dromedary) serves 20 site blocks across 70 subdomains with blackwall defense. 200 words for r/rust."
    "Write about sovereign SMTP: how songBird delivers email without Gmail or ProtonMail. Self-hosted TLS, DKIM, no middlemen. 200 words for r/selfhosted."
    "Analyze the mathematics of trust: sigmoid opacity curves, Anderson localization, and how zero-knowledge identity works without passwords or API keys. 200 words for r/math."
    "Write about the waterlock architecture: OSINT pours IN, processing stays local, nothing seeps OUT. How to build a one-way data membrane. 200 words for r/privacy."
    "Describe RSS as the old web's nervous system: 1819 items broadcasting, feed.xml as the organism's mouth to the internet. 200 words for r/rss."
    "Write about the Tor hidden service as a sovereign endpoint: .onion addresses, no DNS, no certificates needed, end-to-end encryption by default. 200 words for r/tor."
    "Explain the 7-layer organism fabric: perception, membrane, nervous, immune, metabolic, reproductive, cognitive. How biology maps to computing. 200 words for r/compsci."
    "Write about running 63 AI models on 2 GPUs at home: mixture-of-experts without the cloud. How ollama + custom modelfiles create a sovereign AI lab. 200 words for r/localllama."
)

$iteration = 0
$totalTokens = 0

Add-Content $logFile "[$(Get-Date)] EASTGATE NIGHT SHIFT STARTED — $($models.Count) models, $($prompts.Count) prompts"

while ($true) {
    if ((Get-Date).Hour -ge 10 -and (Get-Date).Hour -lt 20) {
        Add-Content $logFile "[$(Get-Date)] MORNING — stopping. iterations=$iteration tokens=$totalTokens"
        break
    }
    
    $model = $models[$iteration % $models.Count]
    $prompt = $prompts[$iteration % $prompts.Count]
    $iteration++
    
    try {
        $body = @{
            model = $model
            messages = @(@{ role = "user"; content = $prompt })
            max_tokens = 800
        } | ConvertTo-Json -Depth 3
        
        $r = Invoke-RestMethod -Uri "$eastgate/v1/chat/completions" -Method POST -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) -ContentType "application/json" -TimeoutSec 300
        $tokens = $r.usage.total_tokens
        $totalTokens += $tokens
        $response = $r.choices[0].message.content
        
        $output = @{
            id = [guid]::NewGuid().ToString("N").Substring(0,16)
            ts = (Get-Date).ToUniversalTime().ToString("o")
            gate = "eastGate"
            model = $model
            prompt_short = $prompt.Substring(0, [math]::Min(80, $prompt.Length))
            response = $response
            tokens = $tokens
            iteration = $iteration
        } | ConvertTo-Json -Compress
        Add-Content $outputFile $output
        
        Add-Content $logFile "[$(Get-Date)] [$iteration] $model ${tokens}tok (eastGate 4070)"
    } catch {
        Add-Content $logFile "[$(Get-Date)] ERROR: $($_.Exception.Message)"
        Start-Sleep 30
    }
    
    # ~20% target: 15s pause between inferences
    Start-Sleep 15
}

Add-Content $logFile "[$(Get-Date)] EASTGATE NIGHT SHIFT COMPLETE — $iteration iterations, $totalTokens tokens"
