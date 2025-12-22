#!/bin/bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  Quant Dashboard - Cron Job Setup${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DAILY_REPORT_SCRIPT="$SCRIPT_DIR/daily_report.py"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python3"

if [ ! -f "$DAILY_REPORT_SCRIPT" ]; then
    echo -e "${RED}Error: daily_report.py not found at $DAILY_REPORT_SCRIPT${NC}"
    exit 1
fi

if [ ! -f "$VENV_PYTHON" ]; then
    echo -e "${YELLOW}Warning: Virtual environment not found${NC}"
    echo -e "${YELLOW}Using system python3 instead${NC}"
    VENV_PYTHON="python3"
fi

CRON_JOB="0 20 * * * $VENV_PYTHON $DAILY_REPORT_SCRIPT >> $PROJECT_DIR/logs/cron.log 2>&1"

echo -e "${BLUE}Cron job to be added:${NC}"
echo "$CRON_JOB"
echo ""

if crontab -l 2>/dev/null | grep -F "$DAILY_REPORT_SCRIPT" >/dev/null 2>&1; then
    echo -e "${YELLOW}Cron job already exists!${NC}"
    echo ""
    read -p "Do you want to replace it? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Setup cancelled.${NC}"
        exit 0
    fi
    crontab -l 2>/dev/null | grep -v "$DAILY_REPORT_SCRIPT" | crontab -
    echo -e "${GREEN}Existing cron job removed${NC}"
fi

(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo ""
echo -e "${GREEN}✓ Cron job successfully added!${NC}"
echo ""
echo -e "${BLUE}Schedule:${NC} Daily at 20:00 (8 PM)"
echo -e "${BLUE}Script:${NC} $DAILY_REPORT_SCRIPT"
echo -e "${BLUE}Log file:${NC} $PROJECT_DIR/logs/cron.log"
echo ""

echo -e "${BLUE}Current crontab:${NC}"
crontab -l | grep -E "(daily_report|^\\* \\* \\* \\* \\*|^[0-9]+ [0-9]+)" || echo "No cron jobs found"

echo ""
echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}Setup complete!${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""
