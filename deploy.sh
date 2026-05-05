#!/bin/bash

# --- TOYZONE GOD-MODE DEPLOYMENT SCRIPT ---
# Version: 5.0 (Full Cleanup + Professional Setup)
# Domain: aqeel.app | IP: 139.59.38.59
# Project: /var/www/ecom | Django: e_com_pro

set -e

echo "🧹 PHASE 1: CLEANING UP OLD MESS..."
# Stop old services if they exist
sudo systemctl stop gunicorn || true
sudo systemctl disable gunicorn || true
sudo systemctl stop nginx || true

# Remove old config files
sudo rm -f /etc/systemd/system/gunicorn.service
sudo rm -f /etc/nginx/sites-available/toyzone
sudo rm -f /etc/nginx/sites-enabled/toyzone
sudo rm -f /etc/nginx/sites-enabled/default
sudo rm -f /run/gunicorn.sock

echo "🛠️ PHASE 2: REINSTALLING CORE TOOLS..."
sudo apt update
sudo apt install python3-pip python3-venv python3-full nginx git curl -y

echo "📂 PHASE 3: SETTING UP PROJECT..."
PROJECT_DIR="/var/www/ecom"
VENV_DIR="$PROJECT_DIR/venv"

cd $PROJECT_DIR

# Clean and recreate virtual environment
sudo rm -rf $VENV_DIR
python3 -m venv $VENV_DIR

echo "📦 PHASE 4: INSTALLING DEPENDENCIES..."
$VENV_DIR/bin/python3 -m pip install --upgrade pip
$VENV_DIR/bin/python3 -m pip install -r requirements.txt
$VENV_DIR/bin/python3 -m pip install gunicorn

echo "📊 PHASE 5: PREPARING DJANGO (Migrations & Static)..."
$VENV_DIR/bin/python3 manage.py migrate
$VENV_DIR/bin/python3 manage.py collectstatic --noinput

echo "⚙️ PHASE 6: CONFIGURING GUNICORN SERVICE..."
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
sudo systemctl start gunicorn
sudo systemctl enable gunicorn

echo "🌐 PHASE 7: CONFIGURING NGINX..."
sudo bash -c "cat > /etc/nginx/sites-available/toyzone <<EOF
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name aqeel.app 139.59.38.59;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
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

# Enable and Restart Nginx
sudo ln -sf /etc/nginx/sites-available/toyzone /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl start nginx
sudo systemctl restart nginx

echo "🔐 PHASE 8: OPENING FIREWALLS..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

echo "✅ FINAL PERMISSIONS FIX..."
sudo chown -R www-data:www-data $PROJECT_DIR
sudo chmod -R 755 $PROJECT_DIR

echo "🔥 DEPLOYMENT COMPLETE!"
echo "🌍 Check your site now at: http://aqeel.app"
echo "💡 If it still says 'Refused', check DigitalOcean Cloud Firewall settings!"
