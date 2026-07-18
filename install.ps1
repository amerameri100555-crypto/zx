Clear-Host

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "      SibShop Bot Installer v1.0" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

if (!(Test-Path ".\app")) {
    Write-Host "❌ لطفا داخل پوشه پروژه اجرا کنید." -ForegroundColor Red
    exit
}

Write-Host "📦 Installing Python Packages..." -ForegroundColor Yellow

pip install -r requirements.txt

Write-Host ""
Write-Host "✅ Packages Installed." -ForegroundColor Green
Write-Host ""

Write-Host "🚀 Ready To Build Project" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Command:"
Write-Host ".\step1.ps1" -ForegroundColor Yellow
