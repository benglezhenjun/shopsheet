param(
    [int]$BackendPort = 8001,
    [int]$FrontendPort = 5173
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path "$PSScriptRoot\.."
$RuntimeDir = Join-Path $Root ".runtime"
$PidFile = Join-Path $RuntimeDir "dev-processes.json"

function Assert-PortAvailable {
    param(
        [Parameter(Mandatory = $true)]
        [int]$Port,
        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($connection) {
        throw "$Name port $Port is already in use."
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
            Start-Sleep -Seconds 1
        }
    }

    throw "Timed out waiting for $Uri"
}

New-Item -ItemType Directory -Force -Path $RuntimeDir | Out-Null
Assert-PortAvailable -Port $BackendPort -Name "Backend"
Assert-PortAvailable -Port $FrontendPort -Name "Frontend"

$backendUrl = "http://127.0.0.1:$BackendPort"
$frontendUrl = "http://127.0.0.1:$FrontendPort"
$backendOut = Join-Path $RuntimeDir "backend.out.log"
$backendErr = Join-Path $RuntimeDir "backend.err.log"
$frontendOut = Join-Path $RuntimeDir "frontend.out.log"
$frontendErr = Join-Path $RuntimeDir "frontend.err.log"

Write-Host "Starting ShopSheet backend on $backendUrl"
$backend = Start-Process -FilePath powershell -ArgumentList @(
    "-NoProfile",
    "-Command",
    "`$env:PYTHONPATH='src'; python -m uvicorn shopsheet.api:app --host 127.0.0.1 --port $BackendPort"
) -WorkingDirectory $Root -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput $backendOut -RedirectStandardError $backendErr

Write-Host "Starting ShopSheet frontend on $frontendUrl"
$frontend = Start-Process -FilePath powershell -ArgumentList @(
    "-NoProfile",
    "-Command",
    "`$env:VITE_API_PROXY='$backendUrl'; npm run dev -- --port $FrontendPort"
) -WorkingDirectory "$Root\frontend" -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput $frontendOut -RedirectStandardError $frontendErr

@{
    backendPid = $backend.Id
    frontendPid = $frontend.Id
    backendPort = $BackendPort
    frontendPort = $FrontendPort
    backendUrl = $backendUrl
    frontendUrl = $frontendUrl
    runtimeDir = $RuntimeDir
} | ConvertTo-Json | Set-Content -Path $PidFile -Encoding utf8

Wait-ForEndpoint "$backendUrl/health"
Wait-ForEndpoint $frontendUrl

Write-Host "Open $frontendUrl"
Write-Host "Logs: $RuntimeDir"
Write-Host "Stop with: .\scripts\stop-dev.ps1"
