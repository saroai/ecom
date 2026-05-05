#!/bin/bash

# --- TOYZONE NUCLEAR DEPLOYMENT SCRIPT ---
# Version: 3.0 (Absolute Clean Start)
# Domain: aqeel.app | IP: 139.59.38.59

set -e

echo "🚀 Starting Nuclear Deployment for ToyZone..."

# 1. System Cleanup & Updates
sudo apt update
sudo apt install python3-pip python3-venv python3-full nginx git curl -y

# 2. Setup Project Directory
PROJECT_DIR="/var/www/ecom"
VENV_DIR="$PROJECT_DIR/venv"

cd $PROJECT_DIR
echo "📂 Working in: $PROJECT_DIR"

# 3. FRESH START: Delete old venv if it exists to avoid errors
echo "🧹 Cleaning up old environment..."
sudo rm -rf $VENV_DIR

# 4. Create Fresh Virtual Environment
echo "🏗️ Creating fresh virtual environment..."
python3 -m venv $VENV_DIR

# 5. Install Python Packages using Venv's Python binary
echo "📦 Installing requirements (This avoids PEP 668 error)..."
$VENV_DIR/bin/python3 -m pip install --upgrade pip
$VENV_DIR/bin/python3 -m pip install -r requirements.txt
$VENV_DIR/bin/python3 -m pip install gunicorn

# 6. Database Migrations & Static Files
echo "📊 Running migrations and static collection..."
$VENV_DIR/bin/python3 manage.py migrate
$VENV_DIR/bin/python3 manage.py collectstatic --noinput

# 7. Create Gunicorn Systemd Service
echo "⚙️ Configuring Gunicorn Service..."
sudo bash -c "cat > /etc/systemd/system/gunicorn.service <<EOF
[Unit]
Description=gunicorn daemon for ToyZone
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=$PROJECT_DIR
ExecStart=$VENV_DIR/bin/gunicorn --access-logfile - --workers 3 --bind unix:/run/gunicorn.sock e_com_pro.wsgi:application

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
sudo systemctl restart gunicorn
sudo systemctl enable gunicorn

# 8. Configure Nginx
echo "🌐 Configuring Nginx for aqeel.app..."
sudo bash -c "cat > /etc/nginx/sites-available/toyzone <<EOF
server {
    listen 80;
    server_name aqeel.app 139.59.38.59;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias $PROJECT_DIR/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
EOF"

# Enable Nginx Config & Remove Default
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/toyzone /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx

# 9. Final Permissions Fix (CRITICAL)
echo "🔐 Fixing permissions for Nginx..."
sudo chown -R www-data:www-data $PROJECT_DIR
sudo chmod -R 755 $PROJECT_DIR

echo "✅ DEPLOYMENT COMPLETE!"
echo "🌍 Visit: http://aqeel.app"
