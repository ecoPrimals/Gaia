# REBOOT PROFILER — Hidden window, profiles ALL on shutdown + startup
# sourDough: scan -> ferment -> braid -> bone -> REBOOT -> compare -> evolve
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("pre","post")]
    [string]$Phase
)

$gutDir = "c:\Users\mokke\Desktop\Gaia\data\gut"
$ts = Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"
$wave = 233

if ($Phase -eq "pre") {
    # ═══ PRE-REBOOT — Snapshot everything before we go dark ═══
    $outFile = "$gutDir\pre-reboot-wave${wave}.json"
    Write-Host "=== PRE-REBOOT PROFILER — Wave $wave ===" -ForegroundColor Cyan
    Write-Host "  Timestamp: $ts"

    $snap = @{
        phase = "pre-reboot"
        wave = $wave
        ts = $ts
        hostname = $env:COMPUTERNAME
    }

    # CPU state
    $cpu = Get-CimInstance Win32_Processor
    $snap["cpu"] = @{
        name = $cpu.Name
        cores = $cpu.NumberOfCores
        threads = $cpu.NumberOfLogicalProcessors
        speed_mhz = $cpu.CurrentClockSpeed
        max_mhz = $cpu.MaxClockSpeed
        load = $cpu.LoadPercentage
    }
    Write-Host "  CPU: $($cpu.NumberOfCores)C/$($cpu.NumberOfLogicalProcessors)T @ $($cpu.CurrentClockSpeed)MHz"

    # Memory
    $mem = Get-CimInstance Win32_OperatingSystem
    $snap["memory"] = @{
        total_gb = [math]::Round($mem.TotalVisibleMemorySize/1MB, 1)
        free_gb = [math]::Round($mem.FreePhysicalMemory/1MB, 1)
        used_pct = [math]::Round(($mem.TotalVisibleMemorySize - $mem.FreePhysicalMemory)/$mem.TotalVisibleMemorySize*100, 1)
    }

    # ALL NVMe / disk
    $disks = Get-PhysicalDisk | Select-Object FriendlyName, MediaType, HealthStatus, OperationalStatus, Size, BusType
    $snap["disks"] = @($disks | ForEach-Object {
        @{
            name = $_.FriendlyName
            type = "$($_.MediaType)"
            health = "$($_.HealthStatus)"
            status = "$($_.OperationalStatus)"
            size_gb = [math]::Round($_.Size/1GB, 1)
            bus = "$($_.BusType)"
        }
    })
    Write-Host "  Disks: $($disks.Count) found"

    # ALL PnP NVMe controllers
    $nvme = Get-PnpDevice -Class SCSIAdapter -ErrorAction SilentlyContinue | Where-Object { $_.FriendlyName -match "NVM" }
    $snap["nvme_controllers"] = @($nvme | ForEach-Object {
        @{
            name = $_.FriendlyName
            status = "$($_.Status)"
            instance = $_.InstanceId
        }
    })

    # GPU state
    $gpus = Get-PnpDevice -Class Display -ErrorAction SilentlyContinue
    $snap["gpus"] = @($gpus | ForEach-Object {
        @{
            name = $_.FriendlyName
            status = "$($_.Status)"
            instance = $_.InstanceId
        }
    })
    Write-Host "  GPUs: $($gpus.Count)"

    # PCIe root ports
    $rps = Get-PnpDevice | Where-Object { $_.FriendlyName -match "Root Port" }
    $snap["root_ports"] = @($rps | ForEach-Object {
        @{
            name = $_.FriendlyName
            status = "$($_.Status)"
            instance = $_.InstanceId
            location = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName DEVPKEY_Device_LocationInfo -ErrorAction SilentlyContinue).Data
        }
    })
    Write-Host "  Root Ports: $($rps.Count) (OK: $(($rps | Where-Object Status -eq 'OK').Count), Unknown: $(($rps | Where-Object Status -eq 'Unknown').Count))"

    # Running services
    $services = Get-Service | Where-Object Status -eq "Running" | Select-Object Name, DisplayName
    $snap["running_services"] = $services.Count

    # Network
    $nets = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue | Where-Object { $_.IPAddress -notlike "127.*" }
    $snap["network"] = @($nets | ForEach-Object { @{ ip = $_.IPAddress; prefix = $_.PrefixLength; iface = $_.InterfaceAlias } })

    # Uptime
    $boot = (Get-CimInstance Win32_OperatingSystem).LastBootUpTime
    $snap["uptime_hours"] = [math]::Round(((Get-Date) - $boot).TotalHours, 2)
    $snap["last_boot"] = $boot.ToString("o")

    # EFI boot order
    try {
        $bcd = bcdedit /enum firmware 2>&1
        $snap["boot_entries"] = @($bcd | Select-String "description" | ForEach-Object { $_.Line.Trim() })
    } catch {}

    # Write
    $snap | ConvertTo-Json -Depth 4 | Out-File $outFile -Encoding utf8
    Write-Host "`n  PRE-REBOOT SNAPSHOT: $outFile" -ForegroundColor Green
    Write-Host "  $($snap.nvme_controllers.Count) NVMe, $($snap.gpus.Count) GPU, $($snap.root_ports.Count) RP"

} elseif ($Phase -eq "post") {
    # ═══ POST-REBOOT — Catch the sudden seams, compare to pre ═══
    $outFile = "$gutDir\post-reboot-wave${wave}.json"
    $preFile = "$gutDir\pre-reboot-wave${wave}.json"
    Write-Host "=== POST-REBOOT CATCHER — Wave $wave ===" -ForegroundColor Green
    Write-Host "  Timestamp: $ts"

    $snap = @{
        phase = "post-reboot"
        wave = $wave
        ts = $ts
        hostname = $env:COMPUTERNAME
    }

    # Same collection as pre
    $cpu = Get-CimInstance Win32_Processor
    $snap["cpu"] = @{
        name = $cpu.Name
        cores = $cpu.NumberOfCores
        threads = $cpu.NumberOfLogicalProcessors
        speed_mhz = $cpu.CurrentClockSpeed
        max_mhz = $cpu.MaxClockSpeed
    }

    $disks = Get-PhysicalDisk | Select-Object FriendlyName, MediaType, HealthStatus, OperationalStatus, Size
    $snap["disks"] = @($disks | ForEach-Object {
        @{ name=$_.FriendlyName; health="$($_.HealthStatus)"; status="$($_.OperationalStatus)"; size_gb=[math]::Round($_.Size/1GB,1) }
    })

    $nvme = Get-PnpDevice -Class SCSIAdapter -ErrorAction SilentlyContinue | Where-Object { $_.FriendlyName -match "NVM" }
    $snap["nvme_controllers"] = @($nvme | ForEach-Object {
        @{ name=$_.FriendlyName; status="$($_.Status)"; instance=$_.InstanceId }
    })

    $gpus = Get-PnpDevice -Class Display -ErrorAction SilentlyContinue
    $snap["gpus"] = @($gpus | ForEach-Object {
        @{ name=$_.FriendlyName; status="$($_.Status)"; instance=$_.InstanceId }
    })

    $rps = Get-PnpDevice | Where-Object { $_.FriendlyName -match "Root Port" }
    $snap["root_ports"] = @($rps | ForEach-Object {
        @{ name=$_.FriendlyName; status="$($_.Status)"; instance=$_.InstanceId }
    })

    $nets = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue | Where-Object { $_.IPAddress -notlike "127.*" }
    $snap["network"] = @($nets | ForEach-Object { @{ ip=$_.IPAddress; iface=$_.InterfaceAlias } })

    $boot = (Get-CimInstance Win32_OperatingSystem).LastBootUpTime
    $snap["last_boot"] = $boot.ToString("o")
    $snap["uptime_seconds"] = [math]::Round(((Get-Date) - $boot).TotalSeconds, 0)

    # ═══ COMPARE — The sourDough diff ═══
    $diff = @{ changes = @(); new_devices = @(); lost_devices = @() }

    if (Test-Path $preFile) {
        $pre = Get-Content $preFile | ConvertFrom-Json

        # CPU core count change?
        if ($pre.cpu.cores -ne $snap.cpu.cores) {
            $diff.changes += "CPU cores: $($pre.cpu.cores) -> $($snap.cpu.cores)"
        }
        if ($pre.cpu.threads -ne $snap.cpu.threads) {
            $diff.changes += "CPU threads: $($pre.cpu.threads) -> $($snap.cpu.threads)"
        }

        # NVMe count change?
        $preNvme = @($pre.nvme_controllers).Count
        $postNvme = @($snap.nvme_controllers).Count
        if ($preNvme -ne $postNvme) {
            $diff.changes += "NVMe controllers: $preNvme -> $postNvme"
        }

        # NVMe status changes
        foreach ($post in $snap.nvme_controllers) {
            $match = $pre.nvme_controllers | Where-Object { $_.instance -eq $post.instance }
            if (-not $match) {
                $diff.new_devices += "NEW NVMe: $($post.name) [$($post.status)]"
            } elseif ($match.status -ne $post.status) {
                $diff.changes += "NVMe $($post.name): $($match.status) -> $($post.status)"
            }
        }

        # GPU changes
        $preGpu = @($pre.gpus).Count
        $postGpu = @($snap.gpus).Count
        if ($preGpu -ne $postGpu) {
            $diff.changes += "GPUs: $preGpu -> $postGpu"
        }
        foreach ($post in $snap.gpus) {
            $match = $pre.gpus | Where-Object { $_.instance -eq $post.instance }
            if (-not $match) {
                $diff.new_devices += "NEW GPU: $($post.name) [$($post.status)]"
            }
        }

        # Root port status changes
        foreach ($post in $snap.root_ports) {
            $match = $pre.root_ports | Where-Object { $_.instance -eq $post.instance }
            if ($match -and $match.status -ne $post.status) {
                $diff.changes += "Root Port: $($match.status) -> $($post.status) [$($post.instance)]"
            }
        }

        # Disk changes
        $preDisk = @($pre.disks).Count
        $postDisk = @($snap.disks).Count
        if ($preDisk -ne $postDisk) {
            $diff.changes += "Physical disks: $preDisk -> $postDisk"
        }

        Write-Host "`n  === SOURDOUGH DIFF ===" -ForegroundColor Yellow
        if ($diff.changes.Count -gt 0) {
            Write-Host "  CHANGES:" -ForegroundColor Cyan
            foreach ($c in $diff.changes) { Write-Host "    + $c" -ForegroundColor Green }
        } else {
            Write-Host "    (no changes detected)" -ForegroundColor DarkGray
        }
        if ($diff.new_devices.Count -gt 0) {
            Write-Host "  NEW DEVICES:" -ForegroundColor Cyan
            foreach ($d in $diff.new_devices) { Write-Host "    * $d" -ForegroundColor Magenta }
        }
        if ($diff.lost_devices.Count -gt 0) {
            Write-Host "  LOST DEVICES:" -ForegroundColor Red
            foreach ($d in $diff.lost_devices) { Write-Host "    ! $d" }
        }
    } else {
        Write-Host "  (no pre-reboot snapshot to compare)" -ForegroundColor DarkGray
    }

    $snap["diff"] = $diff
    $snap | ConvertTo-Json -Depth 4 | Out-File $outFile -Encoding utf8
    Write-Host "`n  POST-REBOOT SNAPSHOT: $outFile" -ForegroundColor Green
    Write-Host "  $($snap.nvme_controllers.Count) NVMe, $($snap.gpus.Count) GPU, $($snap.root_ports.Count) RP"
    Write-Host "  Boot time: $($snap.last_boot), Up: $($snap.uptime_seconds)s"
}
