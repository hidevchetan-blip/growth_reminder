#!/bin/bash

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}    📈 Growth Reminder Installer${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}⚠️  Please don't run this script as root!${NC}"
   exit 1
fi

echo -e "${YELLOW}🔍 Checking Python installation...${NC}"

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 is not installed!${NC}"
    echo ""
    echo "Installing Python3..."
    
    # Detect package manager
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3 python3-pip
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y python3 python3-pip
    else
        echo -e "${RED}Could not install Python. Please install Python3 manually.${NC}"
        exit 1
    fi
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✅ $PYTHON_VERSION detected${NC}"

echo ""
echo -e "${YELLOW}📥 Creating directory...${NC}"
mkdir -p ~/GrowthReminder

echo -e "${YELLOW}📥 Downloading Growth Reminder script...${NC}"

# Download the Python script
if command -v wget &> /dev/null; then
    wget -q --show-progress -O ~/GrowthReminder/growth_reminder.py http://192.168.11.101:8000/script.py
elif command -v curl &> /dev/null; then
    curl -s -o ~/GrowthReminder/growth_reminder.py http://192.168.11.101:8000/script.py
else
    echo -e "${RED}Neither wget nor curl found. Please install one of them.${NC}"
    exit 1
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to download script. Is the server running at http://192.168.11.101:8000?${NC}"
    exit 1
fi

chmod +x ~/GrowthReminder/growth_reminder.py
echo -e "${GREEN}✅ Script downloaded successfully${NC}"

echo ""
echo -e "${YELLOW}📦 Installing required packages...${NC}"
pip3 install --user requests > /dev/null 2>&1
pip3 install --user python-xlib > /dev/null 2>&1
echo -e "${GREEN}✅ Dependencies installed${NC}"

echo ""
echo -e "${YELLOW}⏰ Setting up cron job (daily at 9:00 AM)...${NC}"

# Check if crontab exists
crontab -l > /tmp/current_cron 2>/dev/null || echo "" > /tmp/current_cron

# Check if job already exists
if grep -q "growth_reminder.py" /tmp/current_cron; then
    echo -e "${YELLOW}⚠️  Cron job already exists${NC}"
else
    # Add new cron job
    echo "0 9 * * * cd ~/GrowthReminder && /usr/bin/python3 ~/GrowthReminder/growth_reminder.py" >> /tmp/current_cron
    crontab /tmp/current_cron
    echo -e "${GREEN}✅ Cron job added successfully${NC}"
fi
rm /tmp/current_cron

echo ""
echo -e "${YELLOW}🎉 Testing notification...${NC}"
python3 ~/GrowthReminder/growth_reminder.py

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}    ✅ Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}📍 Script installed to:${NC} ~/GrowthReminder/"
echo -e "${BLUE}⏰ Daily reminder scheduled for:${NC} 9:00 AM"
echo ""
echo -e "${YELLOW}To uninstall:${NC}"
echo "  rm -rf ~/GrowthReminder"
echo "  crontab -e (remove the GrowthReminder line)"
echo ""
