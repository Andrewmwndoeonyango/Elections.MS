# Kenya Electoral System - Reliable Local Launcher
# Purpose: prevent Chrome HTTPS upgrades on localhost and guarantee HTTP access.

param(
    [int]$Port = 8000
)

function Test-PortOpen {
    param([int]$TestPort)

    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $async = $client.BeginConnect('127.0.0.1', $TestPort, $null, $null)
        $connected = $async.AsyncWaitHandle.WaitOne(500)

        if ($connected) {
            $client.EndConnect($async)
            $client.Close()
            return $true
        }

        $client.Close()
        return $false
    }
    catch {
        return $false
    }
}

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$baseUrl = "http://127.0.0.1:$Port"
$urls = @(
    "$baseUrl/",
    "$baseUrl/dashboard/",
    "$baseUrl/voter/",
    "$baseUrl/admin-portal/",
    "$baseUrl/admin/"
)

Write-Host "Kenya Electoral System - Local Launcher" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

if (-not (Test-PortOpen -TestPort $Port)) {
    Write-Host "Server not detected on port $Port. Starting Django..." -ForegroundColor Yellow
    Start-Process -FilePath "python" -ArgumentList @("manage.py", "runserver", "127.0.0.1:$Port") -WorkingDirectory $projectRoot -WindowStyle Minimized

    $started = $false
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Seconds 1
        if (Test-PortOpen -TestPort $Port) {
            $started = $true
            break
        }
    }

    if (-not $started) {
        Write-Host "Could not start server on port $Port." -ForegroundColor Red
        Write-Host "Run manually: python manage.py runserver 127.0.0.1:$Port" -ForegroundColor White
        exit 1
    }
}

Write-Host "Server is running on $baseUrl" -ForegroundColor Green

$chromeCandidates = @(
    "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
    "$env:ProgramFiles(x86)\Google\Chrome\Application\chrome.exe",
    "$env:LocalAppData\Google\Chrome\Application\chrome.exe"
)

$chromePath = $null
foreach ($candidate in $chromeCandidates) {
    if (Test-Path $candidate) {
        $chromePath = $candidate
        break
    }
}

if ($null -eq $chromePath) {
    Write-Host "Chrome not found. Opening default browser." -ForegroundColor Yellow
    Start-Process $urls[0]
}
else {
    $profileDir = Join-Path $env:TEMP ("electionsfr-http-profile-" + [DateTime]::Now.ToString("yyyyMMddHHmmss"))

    $chromeArgs = @(
        "--new-window",
        "--no-first-run",
        "--no-default-browser-check",
        "--user-data-dir=$profileDir",
        "--disable-features=HttpsUpgrades,HTTPS-FirstModeSetting,HttpsFirstBalancedModeAutoEnable,HttpsOnlyMode",
        "--allow-insecure-localhost"
    ) + $urls

    Start-Process -FilePath $chromePath -ArgumentList $chromeArgs
    Write-Host "Chrome launched with localhost HTTPS-upgrade disabled." -ForegroundColor Green
}

Write-Host "" 
Write-Host "Verified local links:" -ForegroundColor Cyan
foreach ($u in $urls) {
    Write-Host "  $u" -ForegroundColor White
}
