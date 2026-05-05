# 🚀 ToyZone DigitalOcean Deployment Guide

This guide explains how to host the ToyZone E-commerce platform on your DigitalOcean Droplet with the domain **aqeel.app**.

## 📋 Prerequisites
1. A DigitalOcean Droplet (Ubuntu 22.04+).
2. Domain `aqeel.app` pointing to IP `139.59.38.59`.

## ⚡ Quick Deployment (Automated)

1. **SSH into your Droplet:**
   ```bash
   ssh root@139.59.38.59
   ```

2. **Clone the repository:**
   ```bash
   cd /var/www
   git clone https://github.com/saroai/ecom.git
   cd ecom
   ```

3. **Run the Deployment Script:**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

---

## 🛠️ What the script does:
- Installs **Nginx**, **Python**, and **Pip**.
- Creates a **Virtual Environment**.
- Installs all project requirements + **Gunicorn**.
- Sets up a **Systemd Service** (keeps the site running 24/7).
- Configures **Nginx** to handle your domain and static/media files.

## 📁 File Structure on Server
- Project Root: `/var/www/ecom`
- Virtual Env: `/var/www/ecom/venv`
- Nginx Config: `/etc/nginx/sites-available/toyzone`
- Gunicorn Service: `/etc/systemd/system/gunicorn.service`

## 🔄 How to update the site in the future?
When you make changes to your code locally and push to GitHub, just run this on your Droplet:
```bash
cd /var/www/ecom
git pull origin main
sudo systemctl restart gunicorn
```

## 🔐 SSL (Optional - HTTPS)
To make your site secure (HTTPS), run these commands after the main deployment:
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d aqeel.app
```
