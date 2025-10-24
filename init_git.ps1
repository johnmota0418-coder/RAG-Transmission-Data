# Initialize Git Repository for Deployment
# Run this in PowerShell from the reduced_model_deploy folder

Write-Host "🚀 Initializing Git repository for reduced transmission RAG model..." -ForegroundColor Green

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Reduced transmission lines RAG model (41,843 lines, 50% dataset)"

# Show status
Write-Host "✅ Git repository initialized successfully!" -ForegroundColor Green
Write-Host "📁 Files ready for deployment:" -ForegroundColor Yellow
git ls-files

Write-Host ""
Write-Host "🔗 Next steps:" -ForegroundColor Cyan
Write-Host "1. Add remote: git remote add origin <your-repo-url>" -ForegroundColor White
Write-Host "2. Push to remote: git push -u origin main" -ForegroundColor White
Write-Host "3. Deploy using your preferred platform" -ForegroundColor White