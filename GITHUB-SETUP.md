# GitHub Setup Guide for Beginners

If you're new to GitHub, this guide will help you push your code online so you can use free hosting.

## Why GitHub?

GitHub stores your code online so platforms like Railway, Render, and Fly.io can:
- 📦 Access your code
- 🚀 Deploy automatically
- 🔄 Update when you make changes

**It's free and takes 5 minutes!**

---

## Step 1: Create GitHub Account

1. Go to **https://github.com**
2. Click **"Sign up"**
3. Enter email, password, username
4. Verify email
5. **Done!** You have a GitHub account

---

## Step 2: Install Git (If Not Installed)

### Check if Git is installed:
```bash
git --version
```

If you see a version number, Git is installed. **Skip to Step 3.**

### Install Git:

**macOS:**
```bash
brew install git
# Or download from https://git-scm.com/download/mac
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install git
```

**Windows:**
Download from https://git-scm.com/download/win

---

## Step 3: Configure Git

Tell Git who you are:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Use the **same email** as your GitHub account.

---

## Step 4: Create Repository on GitHub

### Option A: Using GitHub Website (Easier)

1. **Go to GitHub** → https://github.com
2. **Click** green "+" → "New repository"
3. **Repository name:** `yt-downloader`
4. **Description:** "YouTube downloader with web interface"
5. **Public** or **Private** (your choice)
6. **DON'T** check "Initialize with README"
7. **Click** "Create repository"

### Option B: Using GitHub CLI (Advanced)

```bash
# Install GitHub CLI first
brew install gh  # macOS
# or download from https://cli.github.com

# Login
gh auth login

# Create repo
gh repo create yt-downloader --public --source=. --remote=origin --push
```

---

## Step 5: Push Your Code

### First Time Setup:

```bash
# 1. Go to your project directory
cd yt-downloader

# 2. Initialize Git (if not done)
git init

# 3. Add all files
git add .

# 4. Commit files
git commit -m "Initial commit"

# 5. Rename branch to main
git branch -M main

# 6. Connect to GitHub
git remote add origin https://github.com/YOUR_USERNAME/yt-downloader.git
# Replace YOUR_USERNAME with your actual GitHub username

# 7. Push to GitHub
git push -u origin main
```

### Enter Credentials:

When prompted:
- **Username:** Your GitHub username
- **Password:** Use a **Personal Access Token** (not your password)

---

## Step 6: Create Personal Access Token (PAT)

GitHub requires tokens instead of passwords for command line.

1. **Go to** → https://github.com/settings/tokens
2. **Click** → "Generate new token" → "Generate new token (classic)"
3. **Note:** "Git operations"
4. **Expiration:** 90 days (or choose)
5. **Select scopes:**
   - ✅ `repo` (Full control of repositories)
6. **Click** "Generate token"
7. **Copy the token** (save it somewhere safe!)
8. **Use this token** as your password when pushing

---

## Step 7: Verify Upload

1. **Go to** → https://github.com/YOUR_USERNAME/yt-downloader
2. **You should see:**
   - All your files
   - `app.py`, `downloader.py`, etc.
   - README.md displayed below

**Success!** Your code is on GitHub! 🎉

---

## Common Issues & Fixes

### Error: "remote origin already exists"

```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/yt-downloader.git
```

### Error: "Permission denied"

You need a Personal Access Token (see Step 6 above).

### Error: "failed to push"

```bash
git pull origin main --rebase
git push -u origin main
```

### Forgot token?

Create a new one at https://github.com/settings/tokens

---

## Update Code Later

When you make changes:

```bash
# 1. Save your changes

# 2. Add changes
git add .

# 3. Commit with message
git commit -m "Added new feature"

# 4. Push to GitHub
git push
```

---

## Using SSH (Alternative to Token)

More convenient for frequent pushes:

### Setup SSH Key:

```bash
# 1. Generate key
ssh-keygen -t ed25519 -C "your.email@example.com"

# 2. Copy public key
cat ~/.ssh/id_ed25519.pub

# 3. Add to GitHub
# Go to: https://github.com/settings/keys
# Click "New SSH key"
# Paste the key
# Click "Add SSH key"

# 4. Change remote to SSH
git remote set-url origin git@github.com:YOUR_USERNAME/yt-downloader.git
```

Now you can push without entering credentials!

---

## Quick Reference

### Essential Git Commands:

```bash
# Check status
git status

# Add files
git add .                    # Add all files
git add filename             # Add specific file

# Commit
git commit -m "Your message"

# Push to GitHub
git push

# Pull from GitHub
git pull

# View remotes
git remote -v

# View commit history
git log --oneline
```

---

## Visual Flow

```
Your Computer          →          GitHub          →          Railway/Render
┌──────────────┐                ┌──────────┐              ┌──────────┐
│ yt-downloader│  git push      │  Repo    │  auto-deploy │  Live    │
│    files     │  ────────>     │  online  │  ──────────> │  app     │
└──────────────┘                └──────────┘              └──────────┘
```

---

## Next Steps

Now that your code is on GitHub:

1. **✅ Go to [RAILWAY-QUICKSTART.md](RAILWAY-QUICKSTART.md)**
2. **✅ Deploy in 2 minutes**
3. **✅ Get your free URL**

Your GitHub repo is ready for deployment!

---

## Need Help?

### GitHub Tutorials:
- https://docs.github.com/en/get-started/quickstart
- https://guides.github.com/activities/hello-world/

### Git Basics:
- https://git-scm.com/book/en/v2/Getting-Started-Git-Basics

### Common Questions:

**Q: Is GitHub free?**
A: Yes! Free for unlimited public and private repos.

**Q: Can others see my code?**
A: Only if you make it public. Private repos are hidden.

**Q: How much storage?**
A: GitHub gives you plenty of space (up to 1GB per file, unlimited repos).

**Q: Can I delete my repo later?**
A: Yes! Settings → Danger Zone → Delete Repository

---

## 🎉 You're Ready!

You now know how to:
- ✅ Create GitHub account
- ✅ Push code to GitHub
- ✅ Update code later
- ✅ Ready for free hosting

**Next:** [Deploy on Railway →](RAILWAY-QUICKSTART.md)
