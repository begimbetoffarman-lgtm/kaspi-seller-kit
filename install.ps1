# Kaspi seller kit installer (Windows PowerShell 5.1+)
# Usage:  powershell -ExecutionPolicy Bypass -File install.ps1 [-UserHome <dir>] [-Vault <dir>] [-Force]
# Copies skills to <Home>\.claude\skills, creates the product vault, installs 1688-cli.
# Nothing is overwritten unless -Force is given. No secrets are read or written.
param(
    [string]$UserHome = $env:USERPROFILE,
    [string]$Vault = "",
    [switch]$Force,
    [switch]$SkipNpm
)
$ErrorActionPreference = "Stop"
$kit = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $Vault) { $Vault = Join-Path $UserHome "kaspi-agents" }
$skillsDst = Join-Path $UserHome ".claude\skills"
New-Item -ItemType Directory -Force -Path $skillsDst | Out-Null

Write-Host "== Skills -> $skillsDst"
foreach ($s in Get-ChildItem -Directory (Join-Path $kit "skills")) {
    $dst = Join-Path $skillsDst $s.Name
    if ((Test-Path $dst) -and -not $Force) {
        Write-Host "   skip (exists): $($s.Name)  (use -Force to overwrite)"
        continue
    }
    if (Test-Path $dst) { Remove-Item -Recurse -Force $dst }
    Copy-Item -Recurse $s.FullName $dst
    Write-Host "   installed: $($s.Name)"
}

Write-Host "== Vault -> $Vault"
if (-not (Test-Path $Vault)) {
    Copy-Item -Recurse (Join-Path $kit "vault-template") $Vault
    Write-Host "   created from vault-template"
} else {
    Write-Host "   exists, left untouched"
}
$claudeMd = Join-Path $Vault "CLAUDE.md"
if (-not (Test-Path $claudeMd) -or $Force) {
    $text = [IO.File]::ReadAllText((Join-Path $kit "CLAUDE.md"), [Text.Encoding]::UTF8)
    $text = $text.Replace("__VAULT_PATH__", $Vault)
    [IO.File]::WriteAllText($claudeMd, $text, (New-Object Text.UTF8Encoding($false)))
    Write-Host "   CLAUDE.md written (vault path filled in)"
}

Write-Host "== 1688-cli"
if ($SkipNpm) {
    Write-Host "   skipped (-SkipNpm)"
} elseif (Get-Command npm -ErrorAction SilentlyContinue) {
    if (Get-Command 1688 -ErrorAction SilentlyContinue) {
        Write-Host "   already installed"
    } else {
        npm install -g 1688-cli
        if ($LASTEXITCODE -ne 0) { Write-Warning "npm install -g 1688-cli failed, install Node.js LTS and retry" }
    }
} else {
    Write-Warning "npm not found. Install Node.js LTS from https://nodejs.org then run: npm install -g 1688-cli"
}

Write-Host ""
Write-Host "DONE. Next (manual): log in to 1688 by QR code ->  1688 --help  (see INSTALL.md step 5)."
Write-Host "Then open Claude Code in: $Vault"
