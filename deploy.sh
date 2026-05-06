#!/bin/bash

# --- TOYZONE GOD-MODE DEPLOYMENT SCRIPT ---
# Version: 6.0 (New Droplet & SSL Support)
# Domain: learnmythos.app | IP: 143.110.182.223
# Project: /var/www/ecom | Django: e_com_pro

set -e

echo "🧹 PHASE 1: CLEANING UP OLD MESS..."
sudo fuser -k 80/tcp || true
sudo systemctl stop gunicorn || true
sudo systemctl stop nginx || true

echo "🛠️ PHASE 2: INSTALLING SYSTEM TOOLS..."
sudo apt update
sudo apt install python3-pip python3-venv python3-full nginx git curl psmisc certbot python3-certbot-nginx -y

echo "📂 PHASE 3: SETTING UP PROJECT..."
PROJECT_DIR="/var/www/ecom"
VENV_DIR="$PROJECT_DIR/venv"

# Ensure directory exists and permissions are correct
sudo mkdir -p $PROJECT_DIR
sudo chown -R $USER:$USER $PROJECT_DIR
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

echo "⚙️ PHASE 6: CONFIGURING GUNICORN..."
sudo bash -c "cat > /etc/systemd/system/gunicorn.service <<EOF
[Unit]
Description=gunicorn daemon for ToyZone
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment=\"ENVIRONMENT=production\"
ExecStart=$VENV_DIR/bin/gunicorn --access-logfile - --workers 3 --bind unix:/run/gunicorn.sock e_com_pro.wsgi:application

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn

echo "🌐 PHASE 7: CONFIGURING NGINX..."
sudo rm -f /etc/nginx/sites-enabled/default
sudo bash -c "cat > /etc/nginx/sites-available/toyzone <<EOF
server {
    listen 80;
    server_name learnmythos.app www.learnmythos.app 143.110.182.223;

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

# Enable Nginx Config
sudo ln -sf /etc/nginx/sites-available/toyzone /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx

echo "🔐 PHASE 8: OPENING FIREWALLS..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

echo "🔐 PHASE 9: FIXING PERMISSIONS..."
sudo chown -R www-data:www-data $PROJECT_DIR
sudo chmod -R 755 $PROJECT_DIR

echo "🔥 DEPLOYMENT COMPLETE!"
echo "🌍 Visit: http://learnmythos.app"
echo "🔐 NEXT STEP: Run 'sudo certbot --nginx -d learnmythos.app -d www.learnmythos.app' to enable HTTPS!"
