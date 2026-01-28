# Nepal Entity Service Setup Script
Write-Host "🇳🇵 Nepal Entity Service - Setup Script" -ForegroundColor Green
Write-Host "=" * 50

# Check if Docker is available
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker not found. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Start Docker services
Write-Host "`nStarting Docker services..." -ForegroundColor Yellow
docker compose up -d

# Wait for services
Write-Host "`nWaiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Check if Python is available
Write-Host "`nChecking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    
    # Run data seeding
    Write-Host "`nRunning data seeding..." -ForegroundColor Yellow
    python scripts/comprehensive_seed_data.py
} catch {
    Write-Host "⚠️ Python not found. Skipping data seeding." -ForegroundColor Yellow
    Write-Host "You can run it manually later: python scripts/comprehensive_seed_data.py" -ForegroundColor Cyan
}

# Test API
Write-Host "`nTesting API endpoints..." -ForegroundColor Yellow
try {
    python test_api_endpoints.py
} catch {
    Write-Host "⚠️ Could not run API tests. Testing manually..." -ForegroundColor Yellow
    
    # Manual health check
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8195/health" -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ API is responding" -ForegroundColor Green
        }
    } catch {
        Write-Host "❌ API not responding yet. Please wait a moment and try again." -ForegroundColor Red
    }
}

Write-Host "`n" + "=" * 50
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host "`n🌐 Access your application:" -ForegroundColor Cyan
Write-Host "   Main App: http://localhost:8195" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8195/docs" -ForegroundColor White
Write-Host "   Leaders: http://localhost:8195/leaders.html" -ForegroundColor White
Write-Host "   Parties: http://localhost:8195/parties.html" -ForegroundColor White

Write-Host "`n📋 Useful Commands:" -ForegroundColor Cyan
Write-Host "   View logs: docker compose logs -f" -ForegroundColor White
Write-Host "   Stop services: docker compose down" -ForegroundColor White
Write-Host "   Restart: docker compose restart" -ForegroundColor White

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")