$ErrorActionPreference = "Stop"
$Root = Resolve-Path "$PSScriptRoot\.."
$RuntimeDir = Join-Path $Root ".runtime"
$PidFile = Join-Path $RuntimeDir "dev-processes.json"

if (-not (Test-Path $PidFile)) {
    Write-Host "No ShopSheet dev process file found."
    exit 0
}

$processes = Get-Content -Raw $PidFile | ConvertFrom-Json
foreach ($pidValue in @($processes.frontendPid, $processes.backendPid)) {
    if ($pidValue) {
        $process = Get-Process -Id $pidValue -ErrorAction SilentlyContinue
        if ($process) {
            Stop-Process -Id $pidValue -Force
            Write-Host "Stopped process $pidValue"
        }
    }
}

foreach ($port in @($processes.frontendPort, $processes.backendPort)) {
    if ($port) {
        $connections = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
        foreach ($connection in $connections) {
            $processInfo = Get-CimInstance Win32_Process -Filter "ProcessId=$($connection.OwningProcess)" -ErrorAction SilentlyContinue
            $commandLine = [string]$processInfo.CommandLine
            if ($commandLine.Contains("shopsheet.api:app") -or $commandLine.Contains("$Root\frontend")) {
                Stop-Process -Id $connection.OwningProcess -Force
                Write-Host "Stopped listener $($connection.OwningProcess) on port $port"
            }
        }
    }
}

Remove-Item -Path $PidFile -Force
Write-Host "ShopSheet dev services stopped."
