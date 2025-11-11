#!/bin/bash

# AI Newsletter Cron Setup Script
# This script sets up a cron job to run the newsletter on Monday and Thursday at 8 AM

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}AI Newsletter Cron Setup${NC}"
echo "================================"
echo ""

# Get the current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo -e "Newsletter directory: ${YELLOW}${SCRIPT_DIR}${NC}"
echo ""

# Find Python 3
PYTHON_PATH=$(which python3)
if [ -z "$PYTHON_PATH" ]; then
    echo -e "${RED}Error: python3 not found in PATH${NC}"
    echo "Please install Python 3 first"
    exit 1
fi
echo -e "Python path: ${YELLOW}${PYTHON_PATH}${NC}"
echo ""

# Create the cron job line
CRON_JOB="0 8 * * 1,4 cd ${SCRIPT_DIR} && ${PYTHON_PATH} ${SCRIPT_DIR}/newsletter.py >> ${SCRIPT_DIR}/cron.log 2>&1"

echo "Cron job to be added:"
echo -e "${YELLOW}${CRON_JOB}${NC}"
echo ""
echo "This will run the newsletter:"
echo "  - Every Monday at 8:00 AM"
echo "  - Every Thursday at 8:00 AM"
echo "  - Logs will be saved to: ${SCRIPT_DIR}/cron.log"
echo ""

# Ask for confirmation
read -p "Do you want to add this cron job? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Setup cancelled${NC}"
    exit 0
fi

# Check if cron job already exists
EXISTING_CRON=$(crontab -l 2>/dev/null | grep -F "${SCRIPT_DIR}/newsletter.py")

if [ ! -z "$EXISTING_CRON" ]; then
    echo -e "${YELLOW}Warning: A similar cron job already exists:${NC}"
    echo "$EXISTING_CRON"
    echo ""
    read -p "Do you want to replace it? (y/n) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove existing job
        (crontab -l 2>/dev/null | grep -v -F "${SCRIPT_DIR}/newsletter.py") | crontab -
        echo -e "${GREEN}Removed existing cron job${NC}"
    else
        echo -e "${YELLOW}Keeping existing cron job. No changes made.${NC}"
        exit 0
    fi
fi

# Add the cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Cron job added successfully!${NC}"
    echo ""
    echo "Your current cron jobs:"
    echo "---"
    crontab -l
    echo "---"
    echo ""
    echo -e "${GREEN}Setup complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Make sure you've configured config.yaml with your Gmail App Password"
    echo "2. Test the newsletter manually first:"
    echo -e "   ${YELLOW}cd ${SCRIPT_DIR} && python3 newsletter.py${NC}"
    echo "3. Check the cron log to verify it runs:"
    echo -e "   ${YELLOW}tail -f ${SCRIPT_DIR}/cron.log${NC}"
    echo ""
    echo "The newsletter will automatically run:"
    echo "  • Next Monday at 8:00 AM"
    echo "  • Next Thursday at 8:00 AM"
else
    echo -e "${RED}Error: Failed to add cron job${NC}"
    echo "Try adding it manually with: crontab -e"
    exit 1
fi
