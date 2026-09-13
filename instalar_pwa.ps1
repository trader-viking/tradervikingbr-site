# =====================================================================
#  TraderVikingBR - Live Desk : instalacao do PWA no repositorio
# =====================================================================
#  Copie esta pasta descompactada para qualquer lugar e rode:
#      powershell -ExecutionPolicy Bypass -File instalar_pwa.ps1
#
#  O script copia os arquivos para o repositorio, commita e publica.
# =====================================================================

$ErrorActionPreference = "Stop"
$origem = $PSScriptRoot

Write-Host ""
Write-Host "=== TraderVikingBR - instalacao do PWA ===" -ForegroundColor Yellow
Write-Host ""

# --- 1. Localiza o repositorio -----------------------------------------
$candidatos = @(
  "C:\tradervikingbr-site\tradervikingbr-site",
  "C:\tradervikingbr-site",
  "$env:USERPROFILE\Documents\tradervikingbr-site",
  "$env:USERPROFILE\tradervikingbr-site"
)
$repo = $null
foreach ($c in $candidatos) {
  if (Test-Path (Join-Path $c ".git")) { $repo = $c; break }
}
if (-not $repo) {
  Write-Host "Repositorio nao encontrado nos caminhos padrao." -ForegroundColor Red
  $repo = Read-Host "Informe o caminho da pasta que contem a pasta .git"
  if (-not (Test-Path (Join-Path $repo ".git"))) {
    Write-Host "Esse caminho nao e um repositorio git. Abortando." -ForegroundColor Red
    exit 1
  }
}
Write-Host "Repositorio : $repo" -ForegroundColor Green

# --- 2. Copia os arquivos ----------------------------------------------
Write-Host ""
Write-Host "Copiando arquivos..." -ForegroundColor Yellow
Copy-Item (Join-Path $origem "index.html")            $repo -Force
Copy-Item (Join-Path $origem "manifest.webmanifest")  $repo -Force
Copy-Item (Join-Path $origem "sw.js")                 $repo -Force

$destIcons = Join-Path $repo "icons"
if (-not (Test-Path $destIcons)) { New-Item -ItemType Directory -Path $destIcons | Out-Null }
Copy-Item (Join-Path $origem "icons\*.png") $destIcons -Force

Write-Host "  index.html"
Write-Host "  manifest.webmanifest"
Write-Host "  sw.js"
Get-ChildItem (Join-Path $origem "icons\*.png") | ForEach-Object { Write-Host "  icons/$($_.Name)" }

# --- 3. Confere -------------------------------------------------------
Write-Host ""
$faltando = @()
foreach ($f in @("index.html","manifest.webmanifest","sw.js","icons\icon-192.png","icons\icon-512.png","icons\icon-maskable-512.png")) {
  if (-not (Test-Path (Join-Path $repo $f))) { $faltando += $f }
}
if ($faltando.Count -gt 0) {
  Write-Host "Arquivos ausentes apos a copia:" -ForegroundColor Red
  $faltando | ForEach-Object { Write-Host "  $_" }
  exit 1
}
Write-Host "Todos os arquivos no lugar." -ForegroundColor Green

# --- 4. Publica -------------------------------------------------------
Write-Host ""
Write-Host "Publicando no GitHub..." -ForegroundColor Yellow
Push-Location $repo
try {
  git add index.html manifest.webmanifest sw.js icons
  $status = git status --porcelain
  if (-not $status) {
    Write-Host "Nada novo para commitar - os arquivos ja estavam publicados." -ForegroundColor Yellow
  } else {
    git commit -m "PWA: app instalavel com icone proprio" | Out-Null
    git push origin main
    Write-Host "Publicado com sucesso." -ForegroundColor Green
  }

  $url = git config --get remote.origin.url
  if ($url -match "github\.com[:/]([^/]+)/([^/.]+)") {
    $pages = "https://$($Matches[1]).github.io/$($Matches[2])/"
    Write-Host ""
    Write-Host "Aguarde 1 a 2 minutos e abra:" -ForegroundColor Cyan
    Write-Host "  $pages" -ForegroundColor White
    Write-Host ""
    Write-Host "No navegador use Ctrl+Shift+R para forcar a atualizacao." -ForegroundColor Cyan
  }
}
finally { Pop-Location }

Write-Host ""
Write-Host "Concluido." -ForegroundColor Green
