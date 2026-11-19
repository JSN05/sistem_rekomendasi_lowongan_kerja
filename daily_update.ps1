$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $ProjectDir "backend"
$PythonExe = Join-Path $ProjectDir ".venv\Scripts\python.exe"

$ProcessedFile = Join-Path $BackendDir "data\processed\penjualan_bisnis_clean.csv"
$BackupFile = "$ProcessedFile.backup"

$ReloadUrl = "http://127.0.0.1:8000/api/reload"

$LogDir = Join-Path $ProjectDir "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$LogFile = Join-Path $LogDir ("daily_update_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".log")

Start-Transcript -Path $LogFile

$ReloadSucceeded = $false
$HasBackup = $false

try {
    Write-Host "=== DAILY DATA UPDATE ===" -ForegroundColor Cyan

    if (-not (Test-Path $PythonExe)) {
        throw "Python virtual environment tidak ditemukan: $PythonExe"
    }

    if (-not $env:RELOAD_TOKEN) {
        $env:RELOAD_TOKEN = [Environment]::GetEnvironmentVariable(
            "RELOAD_TOKEN",
            "User"
        )
    }

    if (-not $env:RELOAD_TOKEN) {
        throw "RELOAD_TOKEN belum tersedia pada environment."
    }

    if (-not (Test-Path $ProcessedFile)) {
        throw "Processed dataset sebelumnya tidak ditemukan."
    }

    Copy-Item $ProcessedFile $BackupFile -Force
    $HasBackup = $true

    Set-Location $BackendDir

    Write-Host "`n[1/3] Menjalankan scraping..." -ForegroundColor Yellow

    & $PythonExe scraper.py

    if ($LASTEXITCODE -ne 0) {
        throw "Scraping gagal. Pipeline tidak dijalankan."
    }

    Write-Host "`n[2/3] Menjalankan preprocessing..." -ForegroundColor Yellow

    & $PythonExe pipeline.py

    if ($LASTEXITCODE -ne 0) {
        throw "Preprocessing atau validasi gagal."
    }

    Write-Host "`n[3/3] Reload dataset dan Knowledge Graph..." -ForegroundColor Yellow

    $Headers = @{
        "X-Reload-Token" = $env:RELOAD_TOKEN
    }

    $Response = Invoke-RestMethod `
        -Uri $ReloadUrl `
        -Method POST `
        -Headers $Headers

    if ($Response.status -ne "success") {
        throw "Reload tidak mengembalikan status success."
    }

    $ReloadSucceeded = $true

    Write-Host "`n=== UPDATE BERHASIL ===" -ForegroundColor Green
    Write-Host "Jumlah lowongan: $($Response.jobs)"
    Write-Host "Statistik graph:"
    $Response.graph | Format-List

}
catch {
    Write-Host "`n=== UPDATE GAGAL ===" -ForegroundColor Red
    Write-Host $_.Exception.Message

    if ($HasBackup -and -not $ReloadSucceeded) {
        Copy-Item $BackupFile $ProcessedFile -Force
        Write-Host "Dataset processed sebelumnya berhasil dipulihkan." -ForegroundColor Yellow
    }

    exit 1
}
finally {
    if ($ReloadSucceeded -and $HasBackup -and (Test-Path $BackupFile)) {
        Remove-Item $BackupFile -Force
    }

    Set-Location $ProjectDir
    Stop-Transcript
}

if ($ReloadSucceeded) {
    exit 0
}