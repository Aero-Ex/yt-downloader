# Railway Quick Start - Deploy in 2 Minutes ⚡

The **absolute fastest** way to get your YouTube downloader online for **FREE**.

## ✅ What You Get

- 🆓 **Completely free** (no credit card needed)
- ⚡ **2-minute setup**
- 🔗 **Public URL** instantly
- 🔄 **Auto-updates** when you push to GitHub
- 🌐 **Works worldwide**
- ⏱️ **500 hours/month** free

---

## 🚀 Deploy in 3 Steps

### Step 1: Push to GitHub (1 minute)

```bash
cd yt-downloader

# If you haven't already:
git init
git add .
git commit -m "Initial commit"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/yt-downloader.git
git branch -M main
git push -u origin main
```

**Don't have GitHub account?**
- Go to [github.com](https://github.com)
- Click "Sign up"
- Takes 1 minute

---

### Step 2: Deploy on Railway (30 seconds)

1. **Go to** → https://railway.app
2. **Click** → "Start a New Project"
3. **Sign in** → with GitHub
4. **Click** → "Deploy from GitHub repo"
5. **Select** → your `yt-downloader` repository
6. **Click** → "Deploy Now"

---

### Step 3: Get Your URL (30 seconds)

1. **Wait** → 2-3 minutes for build (Railway installs everything)
2. **Click** → "Settings" tab
3. **Click** → "Generate Domain"
4. **Copy** → your URL (like `my-yt-downloader.up.railway.app`)
5. **Done!** 🎉

---

## 🌐 Your App is Live!

Visit your URL and you'll see:
- ✅ Beautiful web interface
- ✅ Visual trimming slider
- ✅ Real-time progress
- ✅ Works on mobile

Share the URL with anyone!

---

## 🔒 Optional: Add Security

Add a secret key (recommended):

1. In Railway dashboard → Variables
2. Click "+ New Variable"
3. Name: `SECRET_KEY`
4. Value: (copy from terminal)

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

4. Click "Add"

---

## 🔄 Auto-Deploy Updates

When you make changes:

```bash
git add .
git commit -m "Update features"
git push
```

Railway **automatically** redeploys! (Takes 1-2 minutes)

---

## 📊 Monitor Usage

Check your Railway dashboard:
- **Deployments** - See build logs
- **Metrics** - Check usage (500 hrs/month free)
- **Logs** - Debug any issues

---

## 💡 Tips

**Keep it running smoothly:**
- Railway auto-sleeps when not used (saves your hours)
- Wakes up instantly on first request
- Perfect for personal use or small groups

**Share with friends:**
- Give them your Railway URL
- They can use it instantly
- No installation needed

**Make it yours:**
- Add custom domain (Settings → Custom Domains)
- Choose any domain you own
- Free HTTPS included

---

## 🆘 Troubleshooting

### Build failed?
- Check logs in Railway → Deployments
- Ensure `requirements.txt` and `Procfile` exist
- Push again: `git push --force`

### App not loading?
- Wait 2-3 minutes after first deploy
- Check Railway → Logs for errors
- Ensure FFmpeg installed (auto-installed on Railway)

### Downloads not working?
- Check Railway → Logs
- Verify app has internet access
- Test with a short YouTube video first

---

## 🎯 What's Included

Railway automatically:
- ✅ Installs Python 3.11
- ✅ Installs all requirements
- ✅ Installs FFmpeg (for video processing)
- ✅ Enables WebSocket (for progress)
- ✅ Provides HTTPS
- ✅ Gives you a public URL

---

## 🔥 That's It!

You now have:
- 🌐 A live YouTube downloader
- 🆓 Hosted for free
- ⚡ Accessible worldwide
- 📱 Works on any device

**Total time:** ~2 minutes
**Cost:** $0
**Maintenance:** Auto-updates from GitHub

---

## 📸 Visual Guide

```
You:               GitHub:            Railway:           Users:
┌────────┐         ┌────────┐         ┌────────┐         ┌────────┐
│ Code   │──push──>│ Repo   │──auto──>│ Deploy │──url──>│ Browser│
│ Commit │         │ Store  │  sync   │ Live   │         │ Access │
└────────┘         └────────┘         └────────┘         └────────┘
```

---

## 🎉 Success!

Your YouTube downloader is now:
- ✅ Online and accessible
- ✅ Free forever (within limits)
- ✅ Auto-updating
- ✅ Mobile-friendly

Share your URL: `https://your-app.up.railway.app`

---

## 📚 Next Steps

**Want more?**
- [FREE-HOSTING.md](FREE-HOSTING.md) - Other free options
- [DEPLOYMENT.md](DEPLOYMENT.md) - Advanced deployment
- [README.md](README.md) - Full documentation

**Need help?**
- Check Railway logs
- View [Railway docs](https://docs.railway.app)
- Re-deploy: `git push`

---

**Enjoy your free YouTube downloader!** 🎬⬇️
