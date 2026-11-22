#!/usr/bin/env pwsh
# PUSH ALL FORGEJO REPOS TO GITHUB
# Run from blueGate with gh CLI authenticated + SSH keys to GitHub
# Requires: email privacy setting disabled on GitHub

$ErrorActionPreference = "Continue"
$TempBase = "$env:TEMP\gaia-push"
if (!(Test-Path $TempBase)) { New-Item -ItemType Directory -Path $TempBase | Out-Null }

$ForgejoBase = "http://192.168.4.244:3000"

# ============================================================
# ORG MAPPING: Forgejo org → GitHub org
# ============================================================
$OrgMap = @{
    "ecoPrimals"        = "ecoPrimals"
    "amicusContra"      = "amicusContra"
    "defendDetroit"     = "defendDetroit"
    "protoKarya"        = "protoKarya"
    "sporeGarden"       = "sporeGarden"
    "syntheticChemistry"= "syntheticChemistry"
    "ecoPrimal"         = "ecoPrimal"
}

# ============================================================
# REPOS TO PUSH: [ForgejoOrg, RepoName, GitHubOrg]
# Only repos that EXIST on Forgejo and should be on GitHub
# ============================================================
$ReposToPush = @(
    # === ecoPrimals (69 repos) ===
    @("ecoPrimals", "agentReagents"),
    @("ecoPrimals", "airSpring"),
    @("ecoPrimals", "barraCuda"),
    @("ecoPrimals", "bearDog"),
    @("ecoPrimals", "benchScale"),
    @("ecoPrimals", "bingoCube"),
    @("ecoPrimals", "biomeOS"),
    @("ecoPrimals", "blueFish"),
    @("ecoPrimals", "caddy"),
    @("ecoPrimals", "cellMembrane"),
    @("ecoPrimals", "coralForge"),
    @("ecoPrimals", "coralReef"),
    @("ecoPrimals", "detroit"),
    @("ecoPrimals", "dromedary"),
    @("ecoPrimals", "esotericWebb"),
    @("ecoPrimals", "footPrint"),
    @("ecoPrimals", "fossilRecord"),
    @("ecoPrimals", "gaia-seed"),
    @("ecoPrimals", "groundSpring"),
    @("ecoPrimals", "healthSpring"),
    @("ecoPrimals", "helixVision"),
    @("ecoPrimals", "hotSpring"),
    @("ecoPrimals", "hud"),
    @("ecoPrimals", "hypothesis"),
    @("ecoPrimals", "infra-campfire-site"),
    @("ecoPrimals", "infra-cns"),
    @("ecoPrimals", "infra-galaxy"),
    @("ecoPrimals", "infra-hooks"),
    @("ecoPrimals", "infra-membrane"),
    @("ecoPrimals", "infra-mesh"),
    @("ecoPrimals", "infra-scripts"),
    @("ecoPrimals", "infra-signal"),
    @("ecoPrimals", "initioChem"),
    @("ecoPrimals", "lithoSpore"),
    @("ecoPrimals", "loamSpine"),
    @("ecoPrimals", "ludoSpring"),
    @("ecoPrimals", "membrane-recipe"),
    @("ecoPrimals", "metalForge"),
    @("ecoPrimals", "models"),
    @("ecoPrimals", "nestGate"),
    @("ecoPrimals", "neuralSpring"),
    @("ecoPrimals", "opsonize-rs"),
    @("ecoPrimals", "petalTongue"),
    @("ecoPrimals", "plasmidBin"),
    @("ecoPrimals", "primalSpring"),
    @("ecoPrimals", "projectFOUNDATION"),
    @("ecoPrimals", "projectNUCLEUS"),
    @("ecoPrimals", "publicRecord"),
    @("ecoPrimals", "reed-it"),
    @("ecoPrimals", "rhizoCrypt"),
    @("ecoPrimals", "rustChip"),
    @("ecoPrimals", "rustdesk"),
    @("ecoPrimals", "signal"),
    @("ecoPrimals", "skunkBat"),
    @("ecoPrimals", "songBird"),
    @("ecoPrimals", "sourDough"),
    @("ecoPrimals", "sporePrint"),
    @("ecoPrimals", "squirrel"),
    @("ecoPrimals", "swarmVine"),
    @("ecoPrimals", "sweetGrass"),
    @("ecoPrimals", "tideGlass"),
    @("ecoPrimals", "toadStool"),
    @("ecoPrimals", "tuebor-repo"),
    @("ecoPrimals", "wateringHole"),
    @("ecoPrimals", "wetSpring"),
    @("ecoPrimals", "whitePaper"),
    @("ecoPrimals", "zola"),

    # === amicusContra (4 repos) ===
    @("amicusContra", "briefs"),
    @("amicusContra", "poison-pill"),
    @("amicusContra", "scyBorg"),
    @("amicusContra", "talos"),

    # === defendDetroit (4 repos) ===
    @("defendDetroit", "blackbook"),
    @("defendDetroit", "cash4kids"),
    @("defendDetroit", "publicRecord"),
    @("defendDetroit", "tuebor"),

    # === protoKarya (7 repos) ===
    @("protoKarya", "amoeba"),
    @("protoKarya", "atlasHugged"),
    @("protoKarya", "footPrint"),
    @("protoKarya", "inkFish"),
    @("protoKarya", "octoPus"),
    @("protoKarya", "pns-amoeba"),
    @("protoKarya", "tideGlass"),

    # === syntheticChemistry (2 repos) ===
    @("syntheticChemistry", "ionChannel"),
    @("syntheticChemistry", "ludoSpring"),

    # === ecoPrimal personal (2 repos) ===
    @("ecoPrimal", "Gaia"),
    @("ecoPrimal", "deploy-fabric")
)

$success = 0
$failed = 0
$skipped = 0
$created = 0

foreach ($entry in $ReposToPush) {
    $forgeOrg = $entry[0]
    $repoName = $entry[1]
    $ghOrg = $OrgMap[$forgeOrg]
    
    if (-not $ghOrg) {
        Write-Host "  SKIP $forgeOrg/$repoName (no GitHub org mapped)" -ForegroundColor Yellow
        $skipped++
        continue
    }

    $cloneUrl = "$ForgejoBase/$forgeOrg/$repoName.git"
    $ghUrl = "git@github.com:$ghOrg/$repoName.git"
    $localDir = "$TempBase\$forgeOrg--$repoName"

    Write-Host "`n--- $forgeOrg/$repoName → $ghOrg/$repoName ---" -ForegroundColor Cyan

    # Clone from Forgejo (bare)
    if (Test-Path $localDir) {
        Write-Host "  Fetching existing clone..." -ForegroundColor Gray
        git -C $localDir fetch origin 2>&1 | Out-Null
    } else {
        Write-Host "  Cloning from Forgejo..." -ForegroundColor Gray
        $cloneOut = git clone --bare $cloneUrl $localDir 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  FAIL: clone failed" -ForegroundColor Red
            Write-Host "  $cloneOut" -ForegroundColor DarkRed
            $failed++
            continue
        }
    }

    # Check if GitHub repo exists, create if not
    $exists = gh repo view "$ghOrg/$repoName" --json name 2>$null
    if (-not $exists) {
        Write-Host "  Creating $ghOrg/$repoName on GitHub..." -ForegroundColor Yellow
        if ($ghOrg -eq "ecoPrimal") {
            gh repo create "$repoName" --public 2>&1 | Out-Null
        } else {
            gh repo create "$ghOrg/$repoName" --public 2>&1 | Out-Null
        }
        $created++
    }

    # Add/update GitHub remote and push
    git -C $localDir remote remove github 2>$null
    git -C $localDir remote add github $ghUrl 2>$null
    
    Write-Host "  Pushing to GitHub..." -ForegroundColor Gray
    $pushOut = git -C $localDir push github --all --force 2>&1
    $pushTags = git -C $localDir push github --tags --force 2>&1
    
    if ($LASTEXITCODE -eq 0 -or $pushOut -match "Everything up-to-date") {
        Write-Host "  OK" -ForegroundColor Green
        $success++
    } else {
        Write-Host "  PUSH RESULT: $pushOut" -ForegroundColor Yellow
        if ($pushOut -match "email privacy") {
            Write-Host "  BLOCKED: email privacy restriction" -ForegroundColor Red
            $failed++
        } else {
            $success++
        }
    }
}

Write-Host "`n========================================" -ForegroundColor White
Write-Host "PUSH COMPLETE" -ForegroundColor Green
Write-Host "  Success: $success" -ForegroundColor Green
Write-Host "  Failed:  $failed" -ForegroundColor Red
Write-Host "  Skipped: $skipped" -ForegroundColor Yellow
Write-Host "  Created: $created new repos" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor White
