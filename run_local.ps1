# Nepal Entity Service - Local Development Server
Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "🇳🇵 Nepal Entity Service - Local" -ForegroundColor Green  
Write-Host "================================" -ForegroundColor Green
Write-Host ""

Write-Host "Starting local development server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "This will serve the frontend with real parliament data" -ForegroundColor Cyan
Write-Host "No database or Docker required!" -ForegroundColor Cyan
Write-Host ""

try {
    python run_local_simple.py
} catch {
    Write-Host "Error starting server. Make sure Python is installed." -ForegroundColor Red
    Write-Host "Press any key to continue..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}