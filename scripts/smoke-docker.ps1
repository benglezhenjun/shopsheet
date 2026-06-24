param(
    [int]$BackendPort = 18000,
    [int]$FrontendPort = 15173,
    [string]$ProjectName = "shopsheet_smoke",
    [switch]$SkipFrontendBuild,
    [switch]$KeepRunning
)

$ErrorActionPreference = "Stop"

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)]
        [scriptblock]$Command
    )

    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $LASTEXITCODE"
    }
}

function Wait-ForEndpoint {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Uri
    )

    for ($attempt = 1; $attempt -le 30; $attempt++) {
        try {
            Invoke-WebRequest -Uri $Uri -UseBasicParsing -TimeoutSec 2 | Out-Null
            return
        }
        catch {
            Start-Sleep -Seconds 2
        }
    }

    throw "Timed out waiting for $Uri"
}

Push-Location $PSScriptRoot\..
try {
    if (-not $SkipFrontendBuild) {
        Write-Host "== Build frontend dist =="
        Push-Location frontend
        Invoke-Checked { npm run build }
        Pop-Location
    }

    $env:SHOPSHEET_BACKEND_PORT = [string]$BackendPort
    $env:SHOPSHEET_FRONTEND_PORT = [string]$FrontendPort

    Write-Host "== Start Docker runtime =="
    Invoke-Checked { docker compose --project-name $ProjectName up -d --build --force-recreate }

    $backendHealth = "http://127.0.0.1:$BackendPort/health"
    $frontendHome = "http://127.0.0.1:$FrontendPort"
    $frontendReport = "http://127.0.0.1:$FrontendPort/api/demo-report"
    $issueExport = "http://127.0.0.1:$FrontendPort/api/demo-export/issue_rows.csv"

    Write-Host "== Smoke backend health =="
    Wait-ForEndpoint $backendHealth
    $health = Invoke-RestMethod -Uri $backendHealth
    if ($health.status -ne "ok") {
        throw "Unexpected backend health response"
    }

    Write-Host "== Smoke frontend shell =="
    $front = Invoke-WebRequest -Uri $frontendHome -UseBasicParsing
    if ($front.StatusCode -ne 200 -or -not $front.Content.Contains("root")) {
        throw "Frontend shell did not render expected HTML"
    }

    Write-Host "== Smoke frontend API proxy =="
    $demo = Invoke-RestMethod -Uri $frontendReport
    if ($demo.metrics.order_rows -ne 6 -or $demo.metrics.issue_count -ne 7) {
        throw "Unexpected demo report metrics"
    }

    Write-Host "== Smoke export download =="
    $export = (Invoke-WebRequest -Uri $issueExport -UseBasicParsing).Content
    if (-not $export.StartsWith("code,message,source_table,row")) {
        throw "Issue export did not include the expected CSV header"
    }

    Write-Host "Docker smoke passed."
}
finally {
    if ((Get-Location).Path.EndsWith("\frontend")) {
        Pop-Location
    }
    Pop-Location

    if (-not $KeepRunning) {
        $env:SHOPSHEET_BACKEND_PORT = [string]$BackendPort
        $env:SHOPSHEET_FRONTEND_PORT = [string]$FrontendPort
        docker compose --project-name $ProjectName down --remove-orphans | Out-Null
    }
}
