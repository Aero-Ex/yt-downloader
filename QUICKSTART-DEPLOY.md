# Quick Start Deployment Guide

Choose your deployment method based on your needs and experience level:

## 🚀 Fastest & Easiest: Railway (Free)

1. **Create account** at [railway.app](https://railway.app)

2. **Deploy in 3 clicks:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Select this repository

3. **Done!** Railway will:
   - Install FFmpeg automatically
   - Deploy your app
   - Give you a public URL

**Cost:** Free tier includes 500 hours/month

---

## 🐳 Easiest with VPS: Docker

If you have a VPS (DigitalOcean, Linode, etc.):

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone your code
cd yt-downloader

# Run with Docker
docker-compose up -d

# Access at http://your-server-ip:5000
```

**Cost:** $5-10/month for VPS

---

## 🖥️ Full Control: VPS with Auto Script

For Ubuntu/Debian VPS:

```bash
# 1. Upload files to your server
scp -r yt-downloader/ user@your-server:/home/user/

# 2. SSH into server
ssh user@your-server

# 3. Run deployment script
cd yt-downloader
sudo bash deploy-vps.sh

# Follow the prompts and you're done!
```

The script automatically:
- ✅ Installs all dependencies
- ✅ Sets up nginx
- ✅ Configures systemd service
- ✅ Sets up firewall
- ✅ Configures automatic file cleanup

**Cost:** $5-10/month for VPS

---

## 📊 Comparison

| Method | Difficulty | Cost | Setup Time | Best For |
|--------|-----------|------|------------|----------|
| Railway | ⭐ Easy | Free-$5 | 2 minutes | Quick test, small scale |
| Docker | ⭐⭐ Medium | $5-10 | 10 minutes | Portable, easy updates |
| VPS Script | ⭐⭐⭐ Medium | $5-10 | 15 minutes | Full control, production |
| Manual VPS | ⭐⭐⭐⭐ Hard | $5-10 | 30+ minutes | Learning, customization |

---

## 🔒 After Deployment

### 1. Enable HTTPS (Important!)

**With domain name:**
```bash
sudo certbot --nginx -d your-domain.com
```

**Without domain:**
Use Cloudflare Tunnel or ngrok (free options)

### 2. Set Environment Variables

Create `.env` file:
```bash
SECRET_KEY=your-random-secret-key-here
FLASK_ENV=production
RATE_LIMIT=10
```

Generate secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Test Your Deployment

Visit your URL and:
- ✅ Paste a YouTube URL
- ✅ Download a video
- ✅ Check real-time progress
- ✅ Download the file

---

## 🆘 Troubleshooting

### App won't start
```bash
# Check logs
sudo journalctl -u ytdl -f

# Or with Docker
docker-compose logs -f
```

### Can't access from outside
```bash
# Check firewall
sudo ufw status

# Open ports
sudo ufw allow 80
sudo ufw allow 443
```

### Downloads fail
```bash
# Check FFmpeg
ffmpeg -version

# Check disk space
df -h

# Check permissions
ls -la downloads/
```

---

## 📚 Full Documentation

For detailed guides, see:
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide
- **[README.md](README.md)** - Application usage guide

---

## ⚠️ Important Notes

### Legal
- Only download content you have rights to
- YouTube's TOS may prohibit downloading
- Use for educational/personal purposes only

### Security
- Always use HTTPS in production
- Set a strong SECRET_KEY
- Enable rate limiting if public
- Implement authentication for sensitive use

### Resources
- Minimum: 1 CPU, 1GB RAM, 10GB storage
- Recommended: 2 CPU, 2GB RAM, 50GB storage

---

## 🎯 Recommended Quick Setup

**For beginners:**
1. Use Railway (free, automatic)
2. Or use Docker on DigitalOcean ($6/month)

**For production:**
1. VPS with the automated script
2. Add Cloudflare for DDoS protection
3. Enable HTTPS with Let's Encrypt
4. Set up monitoring (UptimeRobot)

---

## Need Help?

1. Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions
2. Review logs: `sudo journalctl -u ytdl -f`
3. Test locally first: `python app.py`
4. Verify all dependencies are installed

---

## Quick Commands Reference

```bash
# Start application
sudo systemctl start ytdl

# Stop application
sudo systemctl stop ytdl

# Restart application
sudo systemctl restart ytdl

# View logs
sudo journalctl -u ytdl -f

# Check status
sudo systemctl status ytdl

# Test nginx config
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx

# View nginx logs
sudo tail -f /var/log/nginx/error.log

# Check disk space
df -h

# Clean old downloads manually
find downloads/ -type f -mmin +60 -delete
```

---

**Ready to deploy? Choose your method above and start in minutes!** 🚀
