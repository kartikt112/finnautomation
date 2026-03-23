#!/bin/bash
# ============================================================
# Finautomation - Ubuntu VPS Setup Script
# Run as root: bash setup_ubuntu.sh
# ============================================================

set -e

PROJECT_DIR="/opt/finautomation"
DB_USER="finautomation"
DB_PASS="finautomation"
DB_NAME="finautomation"

echo "========================================"
echo "  Finautomation VPS Setup (Ubuntu)"
echo "========================================"

# --- 1. System update ---
echo -e "\n[1/11] Updating system..."
apt update && apt upgrade -y
apt install -y curl wget git build-essential software-properties-common

# --- 2. Install Python 3.12 (ships with Ubuntu 24.04) ---
echo -e "\n[2/11] Installing Python..."
apt install -y python3 python3-pip python3-venv python3-dev
python3 --version

# --- 3. Install Node.js 20 ---
echo -e "\n[3/11] Installing Node.js 20..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
node --version
npm --version

# --- 4. Install PostgreSQL 16 ---
echo -e "\n[4/11] Installing PostgreSQL..."
apt install -y postgresql postgresql-contrib
systemctl enable postgresql
systemctl start postgresql

# Create database and user
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" 2>/dev/null || true
echo "  Database created."

# --- 5. Install Redis ---
echo -e "\n[5/11] Installing Redis..."
apt install -y redis-server
systemctl enable redis-server
systemctl start redis-server
redis-cli ping

# --- 6. Install PM2 ---
echo -e "\n[6/11] Installing PM2..."
npm install -g pm2
pm2 startup systemd -u root --hp /root

# --- 7. Setup project directory ---
echo -e "\n[7/11] Setting up project..."
mkdir -p $PROJECT_DIR
if [ -d "/tmp/finhostinger" ]; then
    cp -r /tmp/finhostinger/* $PROJECT_DIR/
    echo "  Project files copied."
else
    echo "  WARNING: Copy your project files to $PROJECT_DIR first!"
    echo "  (backend/ and frontend/ folders)"
fi

# --- 8. Setup Python virtual environment & dependencies ---
echo -e "\n[8/11] Installing Python dependencies..."
cd $PROJECT_DIR/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
playwright install-deps
deactivate
echo "  Python dependencies installed."

# --- 9. Create .env file ---
echo -e "\n[9/11] Creating .env file..."
SECRET=$(openssl rand -hex 32)
cat > $PROJECT_DIR/backend/.env << EOF
DATABASE_URL=postgresql+asyncpg://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=$SECRET
UPLOAD_DIR=./uploads
MULTILOGIN_API_URL=http://localhost:35000/api/v2
SCHEDULE_START_HOUR=9
SCHEDULE_END_HOUR=21
DAILY_JOBS_MIN=2
DAILY_JOBS_MAX=3
CAMPAIGN_DURATION_DAYS=30
EOF
mkdir -p $PROJECT_DIR/backend/uploads
echo "  .env created."

# --- 10. Run database migrations ---
echo -e "\n[10/11] Running database migrations..."
cd $PROJECT_DIR/backend
source venv/bin/activate
python -m alembic upgrade head 2>/dev/null || echo "  Run migrations manually after first alembic revision."
deactivate

# --- 11. Build frontend ---
echo -e "\n[11/11] Building frontend..."
cd $PROJECT_DIR/frontend
npm install
npm run build
echo "  Frontend built."

# --- Create PM2 ecosystem file ---
echo -e "\nCreating PM2 config..."
cat > $PROJECT_DIR/ecosystem.config.js << 'PMEOF'
module.exports = {
  apps: [
    {
      name: 'backend',
      cwd: '/opt/finautomation/backend',
      script: 'venv/bin/uvicorn',
      args: 'app.main:app --host 0.0.0.0 --port 8000',
      env: {
        PATH: '/opt/finautomation/backend/venv/bin:' + process.env.PATH,
      },
    },
    {
      name: 'celery-worker',
      cwd: '/opt/finautomation/backend',
      script: 'venv/bin/celery',
      args: '-A app.tasks.celery_app worker --loglevel=info --concurrency=2',
      env: {
        PATH: '/opt/finautomation/backend/venv/bin:' + process.env.PATH,
      },
    },
    {
      name: 'celery-beat',
      cwd: '/opt/finautomation/backend',
      script: 'venv/bin/celery',
      args: '-A app.tasks.celery_app beat --loglevel=info',
      env: {
        PATH: '/opt/finautomation/backend/venv/bin:' + process.env.PATH,
      },
    },
    {
      name: 'frontend',
      cwd: '/opt/finautomation/frontend',
      script: 'node_modules/.bin/next',
      args: 'start -p 3000',
    },
  ],
};
PMEOF
echo "  PM2 config created."

# --- Install & configure Nginx ---
echo -e "\nSetting up Nginx..."
apt install -y nginx

cat > /etc/nginx/sites-available/finautomation << 'NGINXEOF'
server {
    listen 80;
    server_name _;

    # Frontend
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        client_max_body_size 50M;
    }

    # Swagger docs
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:8000/openapi.json;
        proxy_set_header Host $host;
    }
}
NGINXEOF

ln -sf /etc/nginx/sites-available/finautomation /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx
systemctl enable nginx
echo "  Nginx configured."

# --- Configure UFW Firewall ---
echo -e "\nConfiguring firewall..."
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw --force enable
echo "  Firewall configured."

# --- Done ---
echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "To start all services:"
echo "  cd $PROJECT_DIR"
echo "  pm2 start ecosystem.config.js"
echo "  pm2 save"
echo ""
echo "To check status:"
echo "  pm2 status"
echo "  pm2 logs"
echo ""
echo "Dashboard: http://$(curl -s ifconfig.me)"
echo "API Docs:  http://$(curl -s ifconfig.me)/docs"
echo ""
