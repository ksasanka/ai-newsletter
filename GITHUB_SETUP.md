# GitHub Setup Guide

Follow these steps to push your AI Newsletter to GitHub.

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `ai-newsletter` (or your preferred name)
3. Description: "Automated AI news aggregator that delivers curated newsletters"
4. Choose: **Public** or **Private**
5. Do NOT initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 2: Initialize Git Locally

```bash
cd /Users/sasankakatta/ai-newsletter

# Initialize git repository
git init

# Add all files (config.yaml is already in .gitignore)
git add .

# Create initial commit
git commit -m "Initial commit: AI Newsletter Generator with configurable sources and email delivery"
```

## Step 3: Connect to GitHub

Replace `yourusername` with your actual GitHub username:

```bash
# Add remote
git remote add origin https://github.com/yourusername/ai-newsletter.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

## Step 4: Verify

1. Go to your repository: `https://github.com/yourusername/ai-newsletter`
2. You should see:
   - All your code files
   - README.md displayed on the main page
   - **config.yaml should NOT be visible** (it's in .gitignore)
   - Cache and log files should NOT be visible

## Step 5: Update README (Optional)

In your GitHub repository, you may want to update the clone URL in README.md:

```bash
# Edit README.md and change this line:
git clone https://github.com/yourusername/ai-newsletter.git

# To your actual repository URL
git clone https://github.com/YOUR_ACTUAL_USERNAME/ai-newsletter.git

# Commit and push
git add README.md
git commit -m "Update clone URL in README"
git push
```

## Future Updates

Whenever you make changes:

```bash
# Check what changed
git status

# Add changed files
git add .

# Commit with a message
git commit -m "Description of your changes"

# Push to GitHub
git push
```

## Important Security Notes

✅ **config.yaml is NOT tracked by git** - Your email and password stay local
✅ **Logs and cache are NOT tracked** - Only code goes to GitHub
✅ **Anyone can clone your repo** - But they need their own config.yaml

## Cloning on Another Computer

To use this on another computer:

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-newsletter.git
cd ai-newsletter

# Install dependencies
pip3 install -r requirements.txt

# Create config from sample
cp config.sample.yaml config.yaml

# Edit config.yaml with your settings
nano config.yaml

# Test
python3 newsletter.py
```

## Common Git Commands

```bash
# See current status
git status

# See commit history
git log --oneline

# Pull latest changes (if you edit on GitHub)
git pull

# Create a new branch
git checkout -b feature-name

# Switch branches
git checkout main

# See all branches
git branch -a
```

## Troubleshooting

### "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/yourusername/ai-newsletter.git
```

### "config.yaml appears in git status"
Make sure `.gitignore` is properly created and run:
```bash
git rm --cached config.yaml
git commit -m "Remove config.yaml from tracking"
```

### Authentication issues
GitHub now requires Personal Access Tokens instead of passwords:
1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Generate new token (classic)
3. Select scopes: `repo` (all)
4. Use the token as your password when prompted

Or set up SSH keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

---

**You're all set! Your AI Newsletter is now on GitHub! 🎉**
