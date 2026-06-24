param(
    [switch]$SkipE2E,
    [switch]$SkipAudits,
    [switch]$SkipDockerSmoke
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

Push-Location $PSScriptRoot\..
try {
    Write-Host "== Backend tests =="
    Invoke-Checked { python -m pytest -q --cov=shopsheet --cov-report=term-missing --cov-fail-under=90 }

    Write-Host "== Backend lint =="
    Invoke-Checked { python -m ruff check src tests }

    if (-not $SkipAudits) {
        Write-Host "== Python dependency audit =="
        Invoke-Checked { python -m pip_audit -r requirements.txt }
    }

    Push-Location frontend
    Write-Host "== Frontend install =="
    Invoke-Checked { npm ci }

    if (-not $SkipAudits) {
        Write-Host "== Frontend audit =="
        Invoke-Checked { npm audit --audit-level=high }
    }

    Write-Host "== Frontend build =="
    Invoke-Checked { npm run build }

    if (-not $SkipE2E) {
        Write-Host "== Browser E2E =="
        Invoke-Checked { npx playwright install chromium }
        Invoke-Checked { npm run e2e }
    }
    Pop-Location

    Write-Host "== Docker Compose config =="
    Invoke-Checked { docker compose config | Out-Null }

    Write-Host "== Docker image build =="
    Invoke-Checked { docker compose build }

    if (-not $SkipDockerSmoke) {
        Write-Host "== Docker runtime smoke =="
        Invoke-Checked { powershell -ExecutionPolicy Bypass -File .\scripts\smoke-docker.ps1 -SkipFrontendBuild }
    }

    Write-Host "Verification passed."
}
finally {
    if ((Get-Location).Path.EndsWith("\frontend")) {
        Pop-Location
    }
    Pop-Location
}
