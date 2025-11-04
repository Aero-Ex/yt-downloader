# Deployment Guide - YouTube Downloader

## ⚠️ Important Legal & Security Warnings

### Legal Considerations
- **Terms of Service**: Downloading YouTube videos may violate YouTube's Terms of Service
- **Copyright**: Only download content you have the right to download
- **Personal Use**: This tool is intended for personal, educational use only
- **Liability**: You are responsible for how you use this tool and ensuring compliance with all applicable laws

### Security Considerations
- **Public Access**: Hosting this publicly allows anyone to use your server's resources
- **Resource Usage**: Video downloads consume bandwidth and CPU
- **Abuse Prevention**: Implement rate limiting and authentication if hosting publicly
- **HTTPS**: Always use HTTPS in production to protect user data
- **Storage**: Downloaded files consume disk space - implement cleanup policies

## Hosting Options

### Option 1: VPS (Recommended for Full Control)
**Providers**: DigitalOcean, Linode, Vultr, AWS EC2, Google Cloud
**Cost**: $5-20/month
**Best for**: Full control, custom domain, HTTPS

### Option 2: Platform as a Service (Easiest)
**Providers**: Heroku, Railway, Render
**Cost**: $0-10/month (with limitations)
**Best for**: Quick deployment, automatic scaling

### Option 3: Docker Container
**Providers**: Any Docker-compatible host
**Cost**: Varies
**Best for**: Portability, easy deployment

### Option 4: Home Server (Free but Complex)
**Requirements**: Port forwarding, dynamic DNS
**Cost**: Free (electricity only)
**Best for**: Learning, personal use

---

## Quick Deployment Options

## 🐳 Option 1: Docker Deployment (Easiest)

### Prerequisites
- Docker installed
- Domain name (optional but recommended)

### Steps

1. **Build and run with Docker Compose:**
```bash
cd yt-downloader
docker-compose up -d
```

2. **Access the app:**
```
http://your-server-ip:5000
```

3. **With custom domain and HTTPS:**
- Point your domain to server IP
- Use nginx-proxy with Let's Encrypt (see below)

---

## 🌐 Option 2: VPS Deployment (Ubuntu/Debian)

### Prerequisites
- Ubuntu 20.04+ or Debian 11+ server
- SSH access
- Domain name (optional)

### Step-by-Step Guide

#### 1. Initial Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv ffmpeg nginx certbot python3-certbot-nginx

# Create app user
sudo useradd -m -s /bin/bash ytdl
sudo su - ytdl
```

#### 2. Deploy Application

```bash
# Clone/upload your code
cd /home/ytdl
# Upload files via scp, git, or rsync

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Test the application
python app.py
# Press Ctrl+C to stop
```

#### 3. Create Systemd Service

Exit to root user and create service file:

```bash
sudo nano /etc/systemd/system/ytdl.service
```

Paste this configuration:

```ini
[Unit]
Description=YouTube Downloader Web Application
After=network.target

[Service]
Type=simple
User=ytdl
WorkingDirectory=/home/ytdl/yt-downloader
Environment="PATH=/home/ytdl/venv/bin"
ExecStart=/home/ytdl/venv/bin/gunicorn --worker-class eventlet -w 1 --bind 127.0.0.1:5000 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ytdl
sudo systemctl start ytdl
sudo systemctl status ytdl
```

#### 4. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/ytdl
```

Paste this configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_read_timeout 86400;
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:5000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/ytdl /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 5. Enable HTTPS (Recommended)

```bash
sudo certbot --nginx -d your-domain.com
```

Follow the prompts. Certbot will automatically configure HTTPS.

#### 6. Setup Automatic Cleanup (Optional)

Create cleanup script:

```bash
sudo nano /home/ytdl/cleanup.sh
```

```bash
#!/bin/bash
# Delete files older than 1 hour
find /home/ytdl/yt-downloader/downloads -type f -mmin +60 -delete
```

Add to crontab:

```bash
sudo crontab -e

# Add this line (runs every hour)
0 * * * * /home/ytdl/cleanup.sh
```

---

## 🚂 Option 3: Railway Deployment

### Steps

1. **Create account** at [Railway.app](https://railway.app)

2. **Add to `requirements.txt`:**
```txt
gunicorn
eventlet
```

3. **Create `Procfile`:**
```
web: gunicorn --worker-class eventlet -w 1 app:app
```

4. **Create `railway.json`:**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT app:app",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

5. **Deploy:**
- Connect GitHub repository
- Or use Railway CLI: `railway up`

---

## 🎨 Option 4: Heroku Deployment

### Steps

1. **Install Heroku CLI**

2. **Add files:**

Create `Procfile`:
```
web: gunicorn --worker-class eventlet -w 1 app:app
```

Create `runtime.txt`:
```
python-3.11.0
```

Update `requirements.txt`:
```bash
echo "gunicorn" >> requirements.txt
echo "eventlet" >> requirements.txt
```

3. **Deploy:**

```bash
heroku login
heroku create your-app-name
heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
heroku buildpacks:add --index 2 heroku/python
git init
git add .
git commit -m "Initial commit"
git push heroku main
heroku open
```

---

## 🔒 Security Best Practices

### 1. Environment Variables

Create `.env` file:

```bash
SECRET_KEY=your-very-secret-random-key-here
FLASK_ENV=production
MAX_DOWNLOAD_SIZE=500M
RATE_LIMIT=10
```

Update `app.py` to use:

```python
import os
from dotenv import load_dotenv

load_dotenv()

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-this-in-production')
```

### 2. Rate Limiting

Add to requirements:
```bash
pip install Flask-Limiter
```

### 3. Authentication (Optional)

Implement basic auth or OAuth if needed for private hosting.

### 4. Firewall Configuration

```bash
# Ubuntu/Debian
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22
sudo ufw enable
```

### 5. Monitoring

Consider using:
- **Uptime monitoring**: UptimeRobot, Pingdom
- **Error tracking**: Sentry
- **Server monitoring**: Netdata, Prometheus

---

## 🧹 Maintenance

### Log Management

```bash
# View logs
sudo journalctl -u ytdl -f

# Rotate logs
sudo logrotate /etc/logrotate.d/ytdl
```

### Updates

```bash
sudo su - ytdl
cd yt-downloader
source venv/bin/activate
git pull  # or upload new files
pip install -r requirements.txt --upgrade
exit
sudo systemctl restart ytdl
```

### Backup

```bash
# Backup script
rsync -avz /home/ytdl/yt-downloader user@backup-server:/backups/
```

---

## 📊 Resource Requirements

### Minimum Requirements
- **CPU**: 1 core
- **RAM**: 1GB
- **Storage**: 10GB (with cleanup)
- **Bandwidth**: 100GB/month

### Recommended for Production
- **CPU**: 2 cores
- **RAM**: 2GB
- **Storage**: 50GB SSD
- **Bandwidth**: 1TB/month

---

## 🔍 Troubleshooting

### Application won't start
```bash
sudo systemctl status ytdl
sudo journalctl -u ytdl -n 50
```

### Nginx errors
```bash
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

### Permission issues
```bash
sudo chown -R ytdl:ytdl /home/ytdl/yt-downloader
sudo chmod -R 755 /home/ytdl/yt-downloader
```

### WebSocket not working
- Check nginx configuration for WebSocket support
- Verify proxy headers are set correctly
- Check firewall allows WebSocket connections

---

## 📝 Post-Deployment Checklist

- [ ] Application runs successfully
- [ ] HTTPS is configured
- [ ] Firewall is configured
- [ ] Automatic cleanup is enabled
- [ ] Monitoring is set up
- [ ] Backups are configured
- [ ] Domain is pointed correctly
- [ ] Environment variables are set
- [ ] Rate limiting is enabled (if public)
- [ ] Error tracking is configured

---

## 🌟 Recommended Setup

For most users, I recommend:

1. **Small VPS** (DigitalOcean $6/month droplet)
2. **Ubuntu 22.04 LTS**
3. **Nginx + Let's Encrypt**
4. **Systemd service**
5. **Automatic file cleanup**
6. **Rate limiting enabled**

This provides the best balance of:
- Cost efficiency
- Performance
- Security
- Ease of maintenance

---

## Need Help?

- Check logs first: `sudo journalctl -u ytdl -f`
- Test configuration: `python app.py`
- Verify dependencies: `pip list`
- Check disk space: `df -h`
- Monitor resources: `htop`
