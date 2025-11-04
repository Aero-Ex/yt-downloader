#!/bin/bash

# VPS Deployment Script for YouTube Downloader
# Usage: sudo bash deploy-vps.sh

set -e

echo "========================================"
echo "  YouTube Downloader - VPS Deployment  "
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root (sudo)${NC}"
    exit 1
fi

# Get domain name
read -p "Enter your domain name (or press enter to skip): " DOMAIN
if [ -z "$DOMAIN" ]; then
    DOMAIN="localhost"
    echo -e "${YELLOW}No domain provided. Using localhost${NC}"
fi

echo ""
echo "Step 1: Updating system..."
apt update && apt upgrade -y

echo ""
echo "Step 2: Installing dependencies..."
apt install -y python3 python3-pip python3-venv ffmpeg nginx certbot python3-certbot-nginx

echo ""
echo "Step 3: Creating application user..."
if id "ytdl" &>/dev/null; then
    echo "User ytdl already exists"
else
    useradd -m -s /bin/bash ytdl
    echo -e "${GREEN}User ytdl created${NC}"
fi

echo ""
echo "Step 4: Setting up application..."
APP_DIR="/home/ytdl/yt-downloader"

# Copy files to app directory
if [ ! -d "$APP_DIR" ]; then
    mkdir -p "$APP_DIR"
fi

# Copy current directory to app directory
cp -r . "$APP_DIR/"
chown -R ytdl:ytdl "$APP_DIR"

echo ""
echo "Step 5: Installing Python dependencies..."
su - ytdl -c "cd $APP_DIR && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"

echo ""
echo "Step 6: Generating secret key..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
su - ytdl -c "cd $APP_DIR && echo 'SECRET_KEY=$SECRET_KEY' > .env"
su - ytdl -c "cd $APP_DIR && echo 'FLASK_ENV=production' >> .env"

echo ""
echo "Step 7: Creating systemd service..."
cat > /etc/systemd/system/ytdl.service <<EOF
[Unit]
Description=YouTube Downloader Web Application
After=network.target

[Service]
Type=simple
User=ytdl
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --worker-class eventlet -w 1 --bind 127.0.0.1:5000 --timeout 300 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ytdl
systemctl start ytdl

echo ""
echo "Step 8: Configuring Nginx..."
cat > /etc/nginx/sites-available/ytdl <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    client_max_body_size 100M;
    client_body_timeout 300s;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:5000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_buffering off;
        proxy_read_timeout 86400;
    }
}
EOF

ln -sf /etc/nginx/sites-available/ytdl /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl restart nginx

echo ""
echo "Step 9: Setting up automatic cleanup..."
cat > /home/ytdl/cleanup.sh <<EOF
#!/bin/bash
# Delete files older than 1 hour
find $APP_DIR/downloads -type f -mmin +60 -delete
EOF

chmod +x /home/ytdl/cleanup.sh
chown ytdl:ytdl /home/ytdl/cleanup.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "0 * * * * /home/ytdl/cleanup.sh") | crontab -

echo ""
echo "Step 10: Configuring firewall..."
ufw --force enable
ufw allow 22
ufw allow 80
ufw allow 443

echo ""
echo "========================================"
echo -e "${GREEN}  Deployment Complete! ${NC}"
echo "========================================"
echo ""
echo "Your application is now running at:"
if [ "$DOMAIN" != "localhost" ]; then
    echo "  http://$DOMAIN"
    echo ""
    echo "To enable HTTPS, run:"
    echo "  sudo certbot --nginx -d $DOMAIN"
else
    echo "  http://$(curl -s ifconfig.me)"
fi
echo ""
echo "Useful commands:"
echo "  sudo systemctl status ytdl    - Check application status"
echo "  sudo systemctl restart ytdl   - Restart application"
echo "  sudo journalctl -u ytdl -f    - View logs"
echo "  sudo nginx -t                 - Test nginx configuration"
echo ""
echo -e "${YELLOW}Important: Change the SECRET_KEY in $APP_DIR/.env${NC}"
echo ""
