#!/bin/bash
# Cron Job Setup Script for Quant Dashboard
# This script sets up the daily report generation cron job

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PYTHON_PATH="/usr/bin/python3"
REPORT_SCRIPT="$SCRIPT_DIR/daily_report.py"
LOG_FILE="$PROJECT_DIR/logs/cron.log"

mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/reports"

echo "Setting up Quant Dashboard Cron Jobs"
echo "Project directory: $PROJECT_DIR"
echo "Report script: $REPORT_SCRIPT"

CRON_JOB="0 20 * * * cd $PROJECT_DIR && $PYTHON_PATH $REPORT_SCRIPT >> $LOG_FILE 2>&1"

(crontab -l 2>/dev/null | grep -v "daily_report.py") | crontab -

(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "Cron job installed successfully!"
echo "Schedule: Daily at 20:00 (8 PM)"
echo ""
echo "Current crontab entries:"
crontab -l

echo ""
echo "To verify the cron job:"
echo "  crontab -l"
echo ""
echo "To view logs:"
echo "  tail -f $LOG_FILE"
echo ""
echo "To manually run the report:"
echo "  python3 $REPORT_SCRIPT"
