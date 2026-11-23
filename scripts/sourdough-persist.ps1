# SOURDOUGH PERSISTENCE — Ferment UEFI knowledge into the primal spine
# Pattern: scan → ferment → braid → bone → encrypt → persist across reboots

Write-Host "=== SOURDOUGH PERSISTENCE PATTERN ==="

# === 1. Find actual primal ports (fix $PID bug) ===
Write-Host "`n--- Primal Port Map ---"
$portMap = @()
Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | ForEach-Object {
    $lport = $_.LocalPort
    $procId = $_.OwningProcess
    $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
    if ($proc -and $proc.Path -and $proc.Path -match '(primals|biomeos|Gaia)\\') {
        $species = ""
        if ($proc.Path -match '\\([^\\]+)\\target\\') { $species = $Matches[1] }
        elseif ($proc.Path -match '\\([^\\]+)\.exe') { $species = $Matches[1] }
        $portMap += [PSCustomObject]@{ Port=$lport; Species=$species; Name=$proc.ProcessName; ProcId=$procId }
    }
}
$portMap | Sort-Object Port | ForEach-Object {
    Write-Host ("  :{0,-6} {1,-15} (PID {2})" -f $_.Port, $_.Species, $_.ProcId)
}

# === 2. Probe JSON-RPC endpoints (from config: loamspine :8301, etc) ===
Write-Host "`n--- JSON-RPC Probes ---"
$rpcTargets = @(
    @{ name="loamSpine-jsonrpc"; port=8301 },
    @{ name="loamSpine-tarpc"; port=9001 },
    @{ name="bearDog"; port=9200 },
    @{ name="nestGate"; port=9201 },
    @{ name="skunkBat"; port=9202 },
    @{ name="barraCuda"; port=9203 },
    @{ name="biomeOS-api"; port=31415 },
    @{ name="sweetGrass-default"; port=12000 },
    @{ name="rhizoCrypt-default"; port=7800 }
)

$aliveRpc = @()
foreach ($t in $rpcTargets) {
    # Try JSON-RPC health check
    $body = '{"jsonrpc":"2.0","method":"health_check","params":{},"id":1}'
    try {
        $resp = Invoke-WebRequest -Uri "http://127.0.0.1:$($t.port)/" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        Write-Host ("  [JSON-RPC ALIVE] {0}:{1} -> {2}" -f $t.name, $t.port, $resp.Content.Substring(0, [Math]::Min(100, $resp.Content.Length)))
        $aliveRpc += $t
    } catch {
        # Try plain TCP
        try {
            $tcp = New-Object System.Net.Sockets.TcpClient
            $tcp.Connect("127.0.0.1", $t.port)
            if ($tcp.Connected) {
                Write-Host ("  [TCP ALIVE] {0}:{1} (connected but no HTTP)" -f $t.name, $t.port)
                $aliveRpc += $t
                $tcp.Close()
            }
        } catch {
            Write-Host ("  [DEAD] {0}:{1}" -f $t.name, $t.port)
        }
    }
}

# === 3. Also try all ports from the actual port map ===
Write-Host "`n--- Probing actual primal ports ---"
foreach ($pm in $portMap) {
    if ($aliveRpc | Where-Object { $_.port -eq $pm.Port }) { continue }
    
    $body = '{"jsonrpc":"2.0","method":"health_check","params":{},"id":1}'
    try {
        $resp = Invoke-WebRequest -Uri "http://127.0.0.1:$($pm.Port)/" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        Write-Host ("  [JSON-RPC] :{0} {1} -> {2}" -f $pm.Port, $pm.Species, $resp.Content.Substring(0, [Math]::Min(100, $resp.Content.Length)))
    } catch {
        try {
            $resp = Invoke-WebRequest -Uri "http://127.0.0.1:$($pm.Port)/" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
            Write-Host ("  [HTTP] :{0} {1} -> {2} ({3})" -f $pm.Port, $pm.Species, $resp.StatusCode, $resp.Content.Length)
        } catch {
            $errMsg = $_.Exception.Message
            if ($errMsg.Length -gt 60) { $errMsg = $errMsg.Substring(0, 60) }
            Write-Host ("  [?] :{0} {1} -> {2}" -f $pm.Port, $pm.Species, $errMsg)
        }
    }
}

# === 4. SOURDOUGH: Write persistent fermentation state ===
Write-Host "`n--- Fermenting UEFI knowledge ---"
$timestamp = Get-Date -Format o
$rebootCycle = 2  # We're on cycle 2 (first was the failed GRUB attempt)

$ferment = @{
    organism = "northGate"
    pattern = "sourDough"
    cycle = $rebootCycle
    timestamp = $timestamp
    
    knowledge = @{
        amd_pbs_setup = @{
            guid = "A339D746-F678-49B3-9FC7-54CE0F9DF226"
            size = 256
            igpu_offset = "0x48"
            igpu_current = "0x00"
            igpu_target = "0x01"
            uma_offset = "0x49"
            uma_current = "0xFF"
            uma_target = "0x06"
            primary_video = "0x4E=0x02 (PCIE, keep)"
        }
        pcie_dead_ports = @("RP05 (0:1.3) -> Samsung 4TB ghost", "RP06 (0:1.4) -> WD BLACK 4TB ghost")
        cpu_half_blind = "8C/8T visible, should be 16C/32T. CCD1 invisible. Game Mode or CBS setting."
        nvme_ghost = @("Samsung 990 PRO 4TB (bus 3)", "WD_BLACK SN850X 4TB (bus 4)")
    }
    
    primal_state = @{
        alive_count = 16
        http_api = "SKIPPED (config error)"
        bind_mode = "tcp (fallback from unix sockets)"
        tarpc = "primary transport"
        note = "All primals running but deaf to HTTP. Need JSON-RPC or tarpc to talk."
    }
    
    reboot_history = @(
        @{ cycle=1; goal="iGPU enable via modGRUBShell auto-grub.cfg"; result="FAILED — GRUB dropped to shell, config not auto-executed"; learning="modGRUBShell starts in rescue mode, needs 'normal' or 'configfile' command to load grub.cfg" },
        @{ cycle=2; goal="model UEFI + primals before next reboot"; result="IN PROGRESS"; learning="16 primals alive but HTTP dead. tarpc/JSON-RPC is the path." }
    )
    
    next_reboot = @{
        goal = "iGPU enable (0x48->0x01, 0x49->0x06)"
        method = "F4 -> GAIA EFI Key -> type setup_var_cv commands -> reboot"
        verify = "agent reads AMD_PBS_SETUP after boot, checks 0x48=0x01"
        fallback = "UMAF browser for manual toggle"
    }
    
    boot_engine_evolution = @{
        v1 = "Manual: Kevin types in GRUB shell"
        v2 = "Semi-auto: agent writes grub.cfg, Kevin types 'configfile' or 'normal'"
        v3 = "Auto: custom GRUB EFI with embedded config (needs grub-efi-amd64-bin on eastGate)"
        v4 = "Full: biomeOS manages boot cycle, reads/writes firmware, verifies post-boot"
    }
} 

$fermentJson = $ferment | ConvertTo-Json -Depth 10
$fermentPath = "c:\Users\mokke\Desktop\Gaia\data\gut\sourdough-ferment.json"
$fermentJson | Out-File $fermentPath -Encoding utf8
Write-Host "  Fermented: $fermentPath ($($fermentJson.Length) chars)"

# === 5. BRAID: Write into sweetGrass knowledge graph format ===
$braidPath = "c:\Users\mokke\Desktop\Gaia\data\gut\sweetgrass-braid-uefi.json"
$braid = @{
    graph = "uefi-hardware"
    nodes = @(
        @{ id="amd_pbs_setup"; type="efi_variable"; data=@{guid="A339D746";size=256;offsets=@("0x48","0x49","0x4E")} },
        @{ id="igpu"; type="hardware"; data=@{name="AMD Raphael iGPU";state="disabled";offset="0x48";target="0x01"} },
        @{ id="uma"; type="config"; data=@{name="UMA Frame Buffer";state="none";offset="0x49";target="0x06"} },
        @{ id="rtx5090"; type="hardware"; data=@{name="RTX 5090";state="OK";root_port="RP03"} },
        @{ id="samsung_1tb"; type="hardware"; data=@{name="Samsung 990 PRO 1TB";state="OK";root_port="RP04"} },
        @{ id="samsung_4tb"; type="hardware"; data=@{name="Samsung 990 PRO 4TB";state="ghost";root_port="RP05"} },
        @{ id="wd_4tb"; type="hardware"; data=@{name="WD BLACK SN850X 4TB";state="ghost";root_port="RP06"} },
        @{ id="rp05"; type="pcie_port"; data=@{pci="0:1.3";state="UNKNOWN";expected="samsung_4tb"} },
        @{ id="rp06"; type="pcie_port"; data=@{pci="0:1.4";state="UNKNOWN";expected="wd_4tb"} },
        @{ id="ccd0"; type="cpu_ccd"; data=@{cores=8;l3_mb=96;vcache=1;state="visible"} },
        @{ id="ccd1"; type="cpu_ccd"; data=@{cores=8;l3_mb=32;vcache=0;state="invisible"} },
        @{ id="modgrubshell"; type="tool"; data=@{path="\EFI\tools\modGRUBShell.efi";commands=@("setup_var","setup_var_cv","configfile","chainloader","normal")} }
    )
    edges = @(
        @{ from="amd_pbs_setup"; to="igpu"; relation="controls_at_0x48" },
        @{ from="amd_pbs_setup"; to="uma"; relation="controls_at_0x49" },
        @{ from="rp05"; to="samsung_4tb"; relation="should_host" },
        @{ from="rp06"; to="wd_4tb"; relation="should_host" },
        @{ from="modgrubshell"; to="amd_pbs_setup"; relation="can_write" },
        @{ from="ccd0"; to="ccd1"; relation="sibling_ccd" },
        @{ from="igpu"; to="rtx5090"; relation="co_gpu" }
    )
}
$braid | ConvertTo-Json -Depth 10 | Out-File $braidPath -Encoding utf8
Write-Host "  Braided: $braidPath"

# === 6. BONE: Write loamSpine anchor ===
$bonePath = "c:\Users\mokke\Desktop\Gaia\data\gut\loamspine-bone-uefi.json"
$bone = @{
    anchor = "uefi-northgate-cycle-$rebootCycle"
    timestamp = $timestamp
    hash_before = "69d0c12e606719a3dd4315ac58ead194fa05acdc7289ebd3515059df54910c55"
    state = @{
        igpu = "0x00 (disabled)"
        uma = "0xFF (none)"
        pcie_rp05 = "UNKNOWN"
        pcie_rp06 = "UNKNOWN"
        cpu_cores = "8C/8T"
    }
    pending_writes = @(
        @{ var="AMD_PBS_SETUP"; offset="0x48"; from="0x00"; to="0x01"; meaning="iGPU Forces" },
        @{ var="AMD_PBS_SETUP"; offset="0x49"; from="0xFF"; to="0x06"; meaning="UMA 512M" }
    )
    primal_ports = @($portMap | ForEach-Object { @{port=[int]$_.Port; species=$_.Species} })
}
$bone | ConvertTo-Json -Depth 10 | Out-File $bonePath -Encoding utf8
Write-Host "  Boned: $bonePath"

# === 7. Summary ===
Write-Host "`n=== SOURDOUGH FERMENTATION COMPLETE ==="
Write-Host "  Ferment: $fermentPath"
Write-Host "  Braid:   $braidPath"
Write-Host "  Bone:    $bonePath"
Write-Host "  Reactor: data\gut\uefi-reactor-model.json"
Write-Host "`n  Primal ports found: $($portMap.Count)"
Write-Host "  RPC alive: $($aliveRpc.Count)"
Write-Host "`n  NEXT: Reboot with clean goal (iGPU enable)"
Write-Host "  Each cycle: scan -> compare bone -> ferment delta -> braid -> bone -> evolve"
