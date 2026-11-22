# PRIMAL TRIAD FEED — Use rhizoCrypt + sweetGrass + loamSpine to handle UEFI model
# The primals are ALREADY RUNNING on northGate. We feed them, they solve.

Write-Host "=== PRIMAL TRIAD — LOCAL BODY ==="

# === 1. Find all running primals and their ports ===
Write-Host "`n--- Active Primals ---"
$primals = @{}
$primalProcs = Get-Process | Where-Object { $_.Path -and $_.Path -match 'primals|biomeos|Gaia' }
foreach ($p in $primalProcs) {
    $name = $p.ProcessName.ToLower()
    if (-not $primals.ContainsKey($name)) {
        $primals[$name] = @{ pid = $p.Id; path = $p.Path; mem = [math]::Round($p.WorkingSet64/1MB, 1) }
    }
}
foreach ($k in $primals.Keys | Sort-Object) {
    $v = $primals[$k]
    Write-Host ("  {0,-20} PID={1,-6} MEM={2,6}MB" -f $k, $v.pid, $v.mem)
}

# === 2. Find listening ports for primals ===
Write-Host "`n--- Primal Ports ---"
$ports = @{}
Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -gt 1024 -and $_.LocalPort -lt 65000 } | ForEach-Object {
    $port = $_.LocalPort
    $pid = $_.OwningProcess
    $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
    if ($proc -and $proc.Path -match 'primals|biomeos|Gaia') {
        $ports[$port] = @{ pid = $pid; name = $proc.ProcessName; port = $port }
        Write-Host ("  :{0,-6} -> {1} (PID {2})" -f $port, $proc.ProcessName, $pid)
    }
}

# === 3. Probe each known primal endpoint ===
Write-Host "`n--- Probing Primal APIs ---"
$endpoints = @(
    @{ name="biomeOS"; port=31415; paths=@("/", "/api", "/health", "/status", "/topology", "/spine", "/graph") },
    @{ name="nestGate"; port=8080; paths=@("/", "/api", "/health") },
    @{ name="bearDog"; port=9200; paths=@("/", "/api", "/identity", "/zk") },
    @{ name="skunkBat"; port=9750; paths=@("/", "/api", "/scan", "/detect") },
    @{ name="petalTongue"; port=9900; paths=@("/", "/api", "/render") },
    @{ name="sweetGrass"; port=12000; paths=@("/", "/api", "/graph", "/braid", "/query") },
    @{ name="loamSpine"; port=5000; paths=@("/", "/api", "/spine", "/bone", "/data") },
    @{ name="rhizoCrypt"; port=7800; paths=@("/", "/api", "/store", "/encrypt", "/vault") },
    @{ name="toadStool"; port=13000; paths=@("/", "/api", "/discover", "/services") },
    @{ name="squirrel"; port=1700; paths=@("/", "/api", "/dispatch") },
    @{ name="sourDough"; port=3400; paths=@("/", "/api", "/ferment") },
    @{ name="barraCuda"; port=5300; paths=@("/", "/api", "/stream") },
    @{ name="coralReef"; port=7700; paths=@("/", "/api", "/compute") },
    @{ name="swarmVine"; port=2600; paths=@("/", "/api", "/gossip") },
    @{ name="bingoCube"; port=9300; paths=@("/", "/api", "/coordinate") },
    @{ name="songBird"; port=24000; paths=@("/", "/api", "/mesh") },
    @{ name="dromedary"; port=3700; paths=@("/", "/api", "/proxy") }
)

$alive = @()
foreach ($ep in $endpoints) {
    foreach ($path in $ep.paths) {
        $url = "http://localhost:$($ep.port)$path"
        try {
            $resp = Invoke-WebRequest -Uri $url -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
            $body = $resp.Content
            if ($body.Length -gt 200) { $body = $body.Substring(0, 200) + "..." }
            Write-Host ("  [ALIVE] {0}:{1}{2} = {3} ({4} bytes)" -f $ep.name, $ep.port, $path, $resp.StatusCode, $resp.Content.Length)
            $alive += @{ name=$ep.name; port=$ep.port; path=$path; status=[int]$resp.StatusCode; body=$body }
            break
        } catch {
            # Try next path
        }
    }
}

# === 4. Scan ALL listening ports for hidden primal APIs ===
Write-Host "`n--- Full Port Scan (primal binaries only) ---"
$allPrimalPorts = @()
Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | ForEach-Object {
    $port = $_.LocalPort
    $pid = $_.OwningProcess
    $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
    if ($proc -and $proc.Path -and $proc.Path -match '(primals|biomeos|Gaia)\\') {
        $species = ""
        if ($proc.Path -match '\\([^\\]+)\\target\\') { $species = $Matches[1] }
        elseif ($proc.Path -match '\\([^\\]+)\.exe') { $species = $Matches[1] }
        $allPrimalPorts += @{ port=$port; pid=$pid; name=$proc.ProcessName; species=$species; path=$proc.Path }
    }
}
$allPrimalPorts | Sort-Object { $_.port } | ForEach-Object {
    Write-Host ("  :{0,-6} {1,-15} ({2}) PID={3}" -f $_.port, $_.species, $_.name, $_.pid)
}

# === 5. Feed UEFI model into biomeOS neuralAPI ===
Write-Host "`n--- Feeding UEFI Model to Primals ---"
$modelPath = "c:\Users\mokke\Desktop\Gaia\data\gut\uefi-reactor-model.json"
if (Test-Path $modelPath) {
    $modelJson = Get-Content $modelPath -Raw
    Write-Host "  Model loaded: $($modelJson.Length) chars"
    
    # Try biomeOS neuralAPI
    foreach ($apiPort in @(31415, 8080, 9200)) {
        foreach ($feedPath in @("/api/feed", "/api/ingest", "/feed", "/ingest", "/spine/write", "/data/write", "/neuralapi/feed", "/api/neuralapi", "/v1/ingest")) {
            $url = "http://localhost:${apiPort}${feedPath}"
            try {
                $resp = Invoke-WebRequest -Uri $url -Method POST -Body $modelJson -ContentType "application/json" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
                Write-Host ("  [FED] {0} -> {1} ({2} bytes)" -f $url, $resp.StatusCode, $resp.Content.Length)
            } catch {
                # silent
            }
        }
    }
}

# === 6. Check biomeOS binary for CLI flags ===
Write-Host "`n--- biomeOS Binary Inspection ---"
$biomeosPath = "c:\Users\mokke\Desktop\Gaia\primals\biomeOS\target\release\biomeos.exe"
if (Test-Path $biomeosPath) {
    $sz = (Get-Item $biomeosPath).Length
    Write-Host "  Size: $([math]::Round($sz/1MB, 1))MB"
    
    # Extract strings mentioning API, port, config, efi, uefi
    $bytes = [System.IO.File]::ReadAllBytes($biomeosPath)
    $current = ""
    $hits = @()
    foreach ($b in $bytes) {
        if ($b -ge 0x20 -and $b -le 0x7E) {
            $current += [char]$b
        } else {
            if ($current.Length -ge 8 -and $current -match '(port|api|config|efi|uefi|spine|neural|feed|ingest|grub|firmware|setup_var|pcie|nvme|igpu)') {
                $hits += $current
            }
            $current = ""
        }
    }
    Write-Host "  Relevant strings: $($hits.Count)"
    $hits | Select-Object -Unique | Select-Object -First 40 | ForEach-Object {
        $trimmed = if ($_.Length -gt 100) { $_.Substring(0, 100) + "..." } else { $_ }
        Write-Host "    $trimmed"
    }
}

Write-Host "`n=== TRIAD STATUS ==="
Write-Host "  Alive endpoints: $($alive.Count)"
Write-Host "  Primal ports: $($allPrimalPorts.Count)"
Write-Host "  Model size: $((Get-Item $modelPath -ErrorAction SilentlyContinue).Length) bytes"
