#!/bin/bash

# AI Newsletter - GitHub Push Setup Script
# This script will help you push your code to GitHub

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}AI Newsletter - GitHub Setup${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Get the current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: git is not installed${NC}"
    echo "Please install git first: https://git-scm.com/downloads"
    exit 1
fi

echo -e "${BLUE}Step 1: GitHub Repository Setup${NC}"
echo "-----------------------------------"
echo ""
echo "First, you need to create a GitHub repository:"
echo "1. Go to: ${YELLOW}https://github.com/new${NC}"
echo "2. Repository name: ${YELLOW}ai-newsletter${NC}"
echo "3. Description: ${YELLOW}Automated AI news aggregator${NC}"
echo "4. Choose Public or Private"
echo "5. Do NOT check any boxes (no README, .gitignore, or license)"
echo "6. Click 'Create repository'"
echo ""
read -p "Press Enter once you've created the repository..."
echo ""

# Get GitHub username
echo -e "${BLUE}Step 2: GitHub Username${NC}"
echo "-----------------------------------"
read -p "Enter your GitHub username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo -e "${RED}Error: GitHub username is required${NC}"
    exit 1
fi

# Confirm repository name
echo ""
read -p "Repository name (default: ai-newsletter): " REPO_NAME
REPO_NAME=${REPO_NAME:-ai-newsletter}

REPO_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

echo ""
echo -e "Repository URL: ${YELLOW}${REPO_URL}${NC}"
echo ""
read -p "Is this correct? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Setup cancelled${NC}"
    exit 0
fi

# Check if already a git repository
if [ -d ".git" ]; then
    echo ""
    echo -e "${YELLOW}Warning: This directory is already a git repository${NC}"
    read -p "Do you want to reinitialize? This will remove existing git history. (y/n) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf .git
        echo -e "${GREEN}Removed existing git repository${NC}"
    else
        echo -e "${YELLOW}Keeping existing repository${NC}"
    fi
fi

# Initialize git if needed
if [ ! -d ".git" ]; then
    echo ""
    echo -e "${BLUE}Step 3: Initializing Git Repository${NC}"
    echo "-----------------------------------"
    git init
    echo -e "${GREEN}✓ Git repository initialized${NC}"
fi

# Check if config.yaml exists (should NOT be committed)
if [ -f "config.yaml" ]; then
    echo ""
    echo -e "${YELLOW}Note: config.yaml found (this is good!)${NC}"
    echo "It will NOT be pushed to GitHub (protected by .gitignore)"
fi

# Verify .gitignore exists
if [ ! -f ".gitignore" ]; then
    echo -e "${RED}Error: .gitignore not found${NC}"
    exit 1
fi

# Add all files
echo ""
echo -e "${BLUE}Step 4: Adding Files${NC}"
echo "-----------------------------------"
git add .

# Show what will be committed
echo ""
echo "Files to be committed:"
git status --short

# Verify config.yaml is NOT in the list
if git status --short | grep -q "config.yaml"; then
    echo ""
    echo -e "${RED}ERROR: config.yaml is being tracked!${NC}"
    echo "This should NOT happen. Please check .gitignore"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Files added (config.yaml is protected)${NC}"

# Create initial commit
echo ""
echo -e "${BLUE}Step 5: Creating Initial Commit${NC}"
echo "-----------------------------------"
git commit -m "Initial commit: AI Newsletter Generator with configurable sources and email delivery"
echo -e "${GREEN}✓ Initial commit created${NC}"

# Set branch name to main
echo ""
echo -e "${BLUE}Step 6: Setting Branch to Main${NC}"
echo "-----------------------------------"
git branch -M main
echo -e "${GREEN}✓ Branch set to main${NC}"

# Add remote
echo ""
echo -e "${BLUE}Step 7: Connecting to GitHub${NC}"
echo "-----------------------------------"

# Check if remote already exists
if git remote | grep -q "origin"; then
    echo "Removing existing remote 'origin'..."
    git remote remove origin
fi

git remote add origin "$REPO_URL"
echo -e "${GREEN}✓ Remote added: ${REPO_URL}${NC}"

# Push to GitHub
echo ""
echo -e "${BLUE}Step 8: Pushing to GitHub${NC}"
echo "-----------------------------------"
echo ""
echo -e "${YELLOW}You will be prompted for your GitHub credentials:${NC}"
echo "  Username: Your GitHub username"
echo "  Password: Your Personal Access Token (NOT your GitHub password)"
echo ""
echo "If you don't have a Personal Access Token:"
echo "  1. Go to: https://github.com/settings/tokens"
echo "  2. Click 'Generate new token (classic)'"
echo "  3. Select 'repo' scope"
echo "  4. Generate and copy the token"
echo "  5. Use it as your password below"
echo ""
read -p "Press Enter to continue with push..."
echo ""

git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}✓ SUCCESS!${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
    echo "Your AI Newsletter is now on GitHub!"
    echo ""
    echo "Repository: ${YELLOW}https://github.com/${GITHUB_USERNAME}/${REPO_NAME}${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Visit your repository to see the code"
    echo "2. Update the README.md clone URL if needed"
    echo "3. Star your own repo! ⭐"
    echo ""
    echo "To make future updates:"
    echo "  ${YELLOW}git add .${NC}"
    echo "  ${YELLOW}git commit -m \"Your commit message\"${NC}"
    echo "  ${YELLOW}git push${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}================================${NC}"
    echo -e "${RED}Push Failed${NC}"
    echo -e "${RED}================================${NC}"
    echo ""
    echo "Common issues:"
    echo "1. Wrong Personal Access Token"
    echo "2. Repository doesn't exist yet"
    echo "3. Network issues"
    echo ""
    echo "Try running this script again or push manually:"
    echo "  ${YELLOW}git push -u origin main${NC}"
    exit 1
fi
