# ============================================================
# Finautomation - Windows VPS Setup Script
# Run as Administrator in PowerShell
# ============================================================

$ErrorActionPreference = "Stop"
$PROJECT_DIR = "C:\finautomation"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Finautomation VPS Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# --- 1. Install Chocolatey (package manager) ---
Write-Host "`n[1/12] Installing Chocolatey..." -ForegroundColor Yellow
if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
}
Write-Host "  Chocolatey installed." -ForegroundColor Green

# --- 2. Install Python 3.11 ---
Write-Host "`n[2/12] Installing Python 3.11..." -ForegroundColor Yellow
choco install python311 -y --force
refreshenv
Write-Host "  Python installed." -ForegroundColor Green

# --- 3. Install Node.js 20 ---
Write-Host "`n[3/12] Installing Node.js 20..." -ForegroundColor Yellow
choco install nodejs-lts -y --force
refreshenv
Write-Host "  Node.js installed." -ForegroundColor Green

# --- 4. Install PostgreSQL 16 ---
Write-Host "`n[4/12] Installing PostgreSQL 16..." -ForegroundColor Yellow
choco install postgresql16 --params '/Password:postgres' -y --force
refreshenv
Write-Host "  PostgreSQL installed." -ForegroundColor Green

# --- 5. Install Memurai (Redis for Windows) ---
Write-Host "`n[5/12] Installing Memurai (Redis)..." -ForegroundColor Yellow
choco install memurai-developer -y --force
Write-Host "  Memurai (Redis) installed." -ForegroundColor Green

# --- 6. Install PM2 ---
Write-Host "`n[6/12] Installing PM2..." -ForegroundColor Yellow
npm install -g pm2
Write-Host "  PM2 installed." -ForegroundColor Green

# --- 7. Clone/Copy project files ---
Write-Host "`n[7/12] Setting up project directory..." -ForegroundColor Yellow
if (!(Test-Path $PROJECT_DIR)) {
    New-Item -ItemType Directory -Path $PROJECT_DIR -Force
}
Write-Host "  Copy your project files to $PROJECT_DIR" -ForegroundColor Yellow
Write-Host "  (backend/ and frontend/ folders)" -ForegroundColor Yellow

# --- 8. Setup PostgreSQL database ---
Write-Host "`n[8/12] Creating database..." -ForegroundColor Yellow
$env:PGPASSWORD = "postgres"
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -c "CREATE USER finautomation WITH PASSWORD 'finautomation';" 2>$null
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -c "CREATE DATABASE finautomation OWNER finautomation;" 2>$null
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE finautomation TO finautomation;" 2>$null
Write-Host "  Database created." -ForegroundColor Green

# --- 9. Install Python dependencies ---
Write-Host "`n[9/12] Installing Python dependencies..." -ForegroundColor Yellow
Set-Location "$PROJECT_DIR\backend"
pip install -r requirements.txt
playwright install chromium
Write-Host "  Python dependencies installed." -ForegroundColor Green

# --- 10. Create .env file ---
Write-Host "`n[10/12] Creating .env file..." -ForegroundColor Yellow
$envContent = @"
DATABASE_URL=postgresql+asyncpg://finautomation:finautomation@localhost:5432/finautomation
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=$(New-Guid)
UPLOAD_DIR=./uploads
MULTILOGIN_API_URL=http://localhost:35000/api/v2
SCHEDULE_START_HOUR=9
SCHEDULE_END_HOUR=21
DAILY_JOBS_MIN=2
DAILY_JOBS_MAX=3
CAMPAIGN_DURATION_DAYS=30
"@
Set-Content -Path "$PROJECT_DIR\backend\.env" -Value $envContent
Write-Host "  .env created." -ForegroundColor Green

# --- 11. Run database migrations ---
Write-Host "`n[11/12] Running database migrations..." -ForegroundColor Yellow
Set-Location "$PROJECT_DIR\backend"
python -m alembic upgrade head
Write-Host "  Migrations complete." -ForegroundColor Green

# --- 12. Install frontend dependencies and build ---
Write-Host "`n[12/12] Building frontend..." -ForegroundColor Yellow
Set-Location "$PROJECT_DIR\frontend"
npm install
npm run build
Write-Host "  Frontend built." -ForegroundColor Green

# --- Create PM2 ecosystem file ---
Write-Host "`nCreating PM2 ecosystem config..." -ForegroundColor Yellow
$pm2Config = @"
module.exports = {
  apps: [
    {
      name: 'backend',
      cwd: '$($PROJECT_DIR -replace '\\', '/')/backend',
      script: 'uvicorn',
      args: 'app.main:app --host 0.0.0.0 --port 8000',
      interpreter: 'python',
    },
    {
      name: 'celery-worker',
      cwd: '$($PROJECT_DIR -replace '\\', '/')/backend',
      script: 'celery',
      args: '-A app.tasks.celery_app worker --loglevel=info --concurrency=2 --pool=solo',
      interpreter: 'python',
    },
    {
      name: 'celery-beat',
      cwd: '$($PROJECT_DIR -replace '\\', '/')/backend',
      script: 'celery',
      args: '-A app.tasks.celery_app beat --loglevel=info',
      interpreter: 'python',
    },
    {
      name: 'frontend',
      cwd: '$($PROJECT_DIR -replace '\\', '/')/frontend',
      script: 'npm',
      args: 'start',
    },
  ],
};
"@
Set-Content -Path "$PROJECT_DIR\ecosystem.config.js" -Value $pm2Config
Write-Host "  PM2 config created." -ForegroundColor Green

# --- Configure Windows Firewall ---
Write-Host "`nConfiguring firewall..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "Finautomation HTTP" -Direction Inbound -Port 80 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "Finautomation HTTPS" -Direction Inbound -Port 443 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "Finautomation Frontend" -Direction Inbound -Port 3000 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "Finautomation Backend" -Direction Inbound -Port 8000 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue
Write-Host "  Firewall configured." -ForegroundColor Green

# --- Done ---
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start all services:" -ForegroundColor White
Write-Host "  cd $PROJECT_DIR" -ForegroundColor Yellow
Write-Host "  pm2 start ecosystem.config.js" -ForegroundColor Yellow
Write-Host ""
Write-Host "To check status:" -ForegroundColor White
Write-Host "  pm2 status" -ForegroundColor Yellow
Write-Host ""
Write-Host "Dashboard will be available at:" -ForegroundColor White
Write-Host "  http://YOUR_VPS_IP:3000" -ForegroundColor Yellow
Write-Host "  API: http://YOUR_VPS_IP:8000/docs" -ForegroundColor Yellow
Write-Host ""
