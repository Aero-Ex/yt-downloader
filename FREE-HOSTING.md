# Free Hosting Guide - YouTube Downloader

## 🆓 Best Free Hosting Options

This guide shows you how to host your YouTube downloader **completely FREE** with three excellent platforms.

### Comparison

| Platform | Free Tier | Setup Time | FFmpeg | WebSocket | Best For |
|----------|-----------|------------|--------|-----------|----------|
| **Railway** | 500 hrs/month | 2 min | ✅ Auto | ✅ Yes | Easiest |
| **Render** | 750 hrs/month | 5 min | ✅ Auto | ✅ Yes | Reliable |
| **Fly.io** | 3 apps free | 10 min | ✅ Docker | ✅ Yes | Advanced |

**Recommended: Railway** (easiest setup, instant deployment)

---

## 🚂 Option 1: Railway (Easiest - 2 Minutes)

### Why Railway?
- ✅ **Truly free** - No credit card required
- ✅ **500 hours/month** free tier
- ✅ **Automatic FFmpeg** installation
- ✅ **WebSocket support** built-in
- ✅ **Custom domain** support
- ✅ **Auto-deploy** from GitHub

### Step-by-Step Instructions

#### Step 1: Push to GitHub

First, create a GitHub repository:

```bash
cd yt-downloader

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit"

# Create repo on GitHub and push
# Go to github.com and create a new repository
# Then:
git remote add origin https://github.com/YOUR_USERNAME/yt-downloader.git
git branch -M main
git push -u origin main
```

#### Step 2: Deploy on Railway

1. **Go to Railway.app**
   - Visit: https://railway.app
   - Click "Start a New Project"
   - Sign up with GitHub (free, no credit card)

2. **Deploy from GitHub**
   - Click "Deploy from GitHub repo"
   - Authorize Railway to access your repos
   - Select your `yt-downloader` repository
   - Click "Deploy Now"

3. **Wait for Build** (2-3 minutes)
   - Railway automatically:
     - Detects Python
     - Installs dependencies from `requirements.txt`
     - Installs FFmpeg automatically
     - Starts your app with `Procfile`

4. **Get Your URL**
   - Click on your deployment
   - Click "Settings" tab
   - Click "Generate Domain"
   - You get a URL like: `your-app.up.railway.app`

5. **Done!** 🎉
   - Visit your URL
   - Your YouTube downloader is live!

#### Environment Variables (Optional)

Add these in Railway dashboard → Variables:

```
SECRET_KEY=your-random-secret-here
FLASK_ENV=production
```

Generate secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🎨 Option 2: Render.com (5 Minutes)

### Why Render?
- ✅ **750 hours/month** free tier
- ✅ **Automatic HTTPS**
- ✅ **Custom domains**
- ✅ **Auto-deploy** from GitHub
- ⚠️ Sleeps after 15 min inactivity (takes 30s to wake)

### Step-by-Step Instructions

#### Step 1: Push to GitHub (Same as Railway)

Follow Step 1 from Railway section above.

#### Step 2: Create render.yaml

Create a file `render.yaml` in your project:

```yaml
services:
  - type: web
    name: youtube-downloader
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT --timeout 300 app:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
    healthCheckPath: /
```

Commit and push:
```bash
git add render.yaml
git commit -m "Add Render config"
git push
```

#### Step 3: Deploy on Render

1. **Go to Render.com**
   - Visit: https://render.com
   - Click "Get Started for Free"
   - Sign up with GitHub

2. **Create Web Service**
   - Click "New +"
   - Select "Web Service"
   - Connect your GitHub account
   - Select your `yt-downloader` repository

3. **Configure Service**
   - Name: `youtube-downloader`
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT app:app`
   - Plan: **Free**

4. **Add Environment Variables**
   - Click "Environment"
   - Add:
     ```
     SECRET_KEY=<generate-random-string>
     FLASK_ENV=production
     ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait 3-5 minutes for build
   - You get a URL like: `your-app.onrender.com`

6. **Done!** 🎉

#### Important: Render Free Tier Note

Free tier apps sleep after 15 minutes of inactivity. First request takes ~30 seconds to wake up. To prevent this:
- Use a free uptime monitor (UptimeRobot, cron-job.org)
- Ping your URL every 14 minutes

---

## 🐳 Option 3: Fly.io (For Docker Users)

### Why Fly.io?
- ✅ **3 apps free forever**
- ✅ **No sleeping** (always on)
- ✅ **Fast performance**
- ✅ **Multiple regions**
- ⚠️ Requires credit card for verification (no charges)

### Step-by-Step Instructions

#### Step 1: Install Fly CLI

```bash
# macOS
brew install flyctl

# Linux
curl -L https://fly.io/install.sh | sh

# Windows
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

#### Step 2: Login

```bash
flyctl auth login
```

#### Step 3: Create fly.toml

Create `fly.toml` in your project:

```toml
app = "your-app-name"  # Change this to unique name

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "5000"
  FLASK_ENV = "production"

[http_service]
  internal_port = 5000
  force_https = true
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 1

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

#### Step 4: Deploy

```bash
cd yt-downloader

# Launch app
flyctl launch --no-deploy

# Set secret key
flyctl secrets set SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Deploy
flyctl deploy

# Open in browser
flyctl open
```

#### Step 5: Get Your URL

```bash
flyctl info
```

Your app is at: `https://your-app-name.fly.dev`

---

## 📋 Quick Comparison

### Railway
- **✅ Best for beginners**
- **✅ No credit card**
- **✅ Instant setup**
- **✅ 500 hours/month**
- ⚠️ Usage tracking

### Render
- **✅ More free hours (750)**
- **✅ No credit card**
- **✅ Auto HTTPS**
- ⚠️ Sleeps after inactivity
- ⚠️ Slow cold starts (30s)

### Fly.io
- **✅ Always on (no sleeping)**
- **✅ 3 apps free**
- **✅ Fast performance**
- ⚠️ Requires credit card (no charges)
- ⚠️ More complex setup

---

## 🎯 My Recommendation

**For most users:** Start with **Railway**

1. **Easiest setup** (2 minutes)
2. **No credit card** required
3. **No sleeping** issues
4. **Auto-deploys** from GitHub

**If Railway limits are reached:** Use **Render**

---

## 🔧 After Deployment Checklist

✅ Test the app by visiting your URL
✅ Try downloading a video
✅ Check WebSocket works (real-time progress)
✅ Set up custom domain (optional)
✅ Monitor usage/uptime

---

## 🌐 Adding Custom Domain (Optional)

### Railway
1. Go to your project → Settings
2. Click "Custom Domains"
3. Add your domain
4. Add CNAME record: `your-domain.com` → `your-app.up.railway.app`

### Render
1. Go to Settings → Custom Domain
2. Enter your domain
3. Add CNAME: `your-domain.com` → `your-app.onrender.com`

### Fly.io
```bash
flyctl certs add your-domain.com
# Follow DNS instructions
```

---

## 📊 Free Tier Limits

### Railway
- **500 execution hours/month**
- **100 GB bandwidth/month**
- **10 GB storage**
- Auto-sleep when not used

### Render
- **750 execution hours/month**
- **100 GB bandwidth/month**
- Sleeps after 15 min inactivity
- Limited build minutes

### Fly.io
- **3 apps**
- **160 GB bandwidth/month**
- **3 GB storage**
- Always on (no sleep)

---

## 🆘 Troubleshooting

### Build Failed

**Check logs:**
```bash
# Railway
View in dashboard → Logs

# Render
View in dashboard → Logs

# Fly.io
flyctl logs
```

**Common fixes:**
```bash
# Ensure requirements.txt is correct
pip freeze > requirements.txt

# Commit and push
git add requirements.txt
git commit -m "Update requirements"
git push
```

### App Not Starting

**Check environment variables:**
- `SECRET_KEY` is set
- `PORT` is correct (use platform's $PORT)
- `FLASK_ENV=production`

**Check Procfile:**
```
web: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT --timeout 300 app:app
```

### Downloads Not Working

**Check FFmpeg:**
- Railway: Auto-installed
- Render: Auto-installed
- Fly.io: In Dockerfile

**Check file permissions:**
- Downloads folder is writable
- App has enough disk space

### WebSocket Not Working

**Ensure:**
- Using `eventlet` worker: `--worker-class eventlet`
- Nginx config (if self-hosted) has WebSocket headers
- HTTPS is enabled (required for WebSocket)

---

## 💡 Tips for Free Hosting

1. **Use GitHub for Auto-Deploy**
   - Push changes → Auto-deploy
   - No manual updates needed

2. **Monitor Usage**
   - Check dashboard regularly
   - Don't exceed free tier limits

3. **Keep App Awake (Render only)**
   - Use UptimeRobot (free)
   - Ping every 14 minutes
   - Prevents cold starts

4. **Optimize Resources**
   - Clean up old downloads automatically
   - Use file cleanup script (included)
   - Monitor disk usage

5. **Use Multiple Platforms**
   - Deploy on Railway + Render
   - Switch if one reaches limits
   - Different URLs for different users

---

## 🚀 Complete Railway Deployment Script

Copy-paste this to deploy in 1 minute:

```bash
# 1. Create GitHub repo (do this on github.com first)

# 2. Push code
cd yt-downloader
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/yt-downloader.git
git branch -M main
git push -u origin main

# 3. Go to railway.app
# - Sign up with GitHub
# - Click "Deploy from GitHub"
# - Select your repo
# - Wait 2 minutes
# - Click "Generate Domain"
# - Done! 🎉
```

---

## 📱 Mobile Access

All free hosting options provide HTTPS URLs that work perfectly on:
- 📱 Mobile phones
- 💻 Tablets
- 🖥️ Desktop browsers
- 🌍 Anywhere with internet

---

## ⚖️ Legal Reminder

**Important:** Even when hosting for free:
- ⚠️ YouTube's Terms of Service may prohibit downloading
- 📜 Only download content you have rights to
- 🎓 Use for educational/personal purposes only
- 🔒 Consider adding authentication if public

---

## 🎉 You're Ready!

Choose your platform and deploy in minutes:

1. **🚂 Railway** - Easiest (recommended)
2. **🎨 Render** - More free hours
3. **🐳 Fly.io** - Always on

All three are excellent free options. Pick one and get your YouTube downloader online in minutes!

---

## 📚 Additional Resources

- [Railway Docs](https://docs.railway.app)
- [Render Docs](https://render.com/docs)
- [Fly.io Docs](https://fly.io/docs)
- [GitHub Guide](https://docs.github.com/en/get-started)

**Need help?** Check logs in your platform's dashboard.

Happy hosting! 🚀
