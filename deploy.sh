#!/bin/bash

# --- TOYZONE AUTO-DEPLOYMENT SCRIPT FOR DIGITAL OCEAN ---
# Domain: aqeel.app | IP: 139.59.38.59

set -e

echo "🚀 Starting Deployment for ToyZone..."

# 1. Update System
sudo apt update && sudo apt upgrade -y

# 2. Install Dependencies
sudo apt install python3-pip python3-venv nginx git curl -y

# 3. Setup Project Directory (Assuming we are in the project folder)
PROJECT_DIR=$(pwd)
VENV_DIR="$PROJECT_DIR/venv"

echo "📂 Project Directory: $PROJECT_DIR"

# 4. Create Virtual Environment
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# 5. Install Python Packages
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# 6. Database Migrations & Static Files
python manage.py migrate
python manage.py collectstatic --noinput

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

sudo systemctl start gunicorn
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

# 9. Firewall setup
sudo ufw allow 'Nginx Full'

echo "✅ DEPLOYMENT COMPLETE!"
echo "🌍 Visit: http://aqeel.app"
