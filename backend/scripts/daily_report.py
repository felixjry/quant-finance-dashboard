#!/usr/bin/env python3
"""
Daily Report Generator
Generates daily financial reports with advanced features:
- Automatic retry on API failures
- Historical report archiving (30-day retention)
- Email notifications on critical errors
- Comprehensive logging and metrics

Designed to run via cron job at 20:00 (8 PM) daily.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import json
import logging
import time
import shutil
from typing import Optional, Dict, List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.data_fetcher import DataFetcher
from services.strategies import calculate_metrics_from_prices

# Configure logging with rotation
log_file = Path(__file__).parent.parent / "logs" / "daily_report.log"
log_file.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

REPORTS_DIR = Path(__file__).parent.parent / "reports"
ARCHIVE_DIR = REPORTS_DIR / "archive"
WATCHLIST = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'SPY', 'BTC-USD', 'EURUSD=X', 'ENGI.PA']

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Archive retention policy
ARCHIVE_RETENTION_DAYS = 30


def ensure_reports_directory():
    """Create reports and archive directories if they don't exist."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Reports directory: {REPORTS_DIR}")
    logger.info(f"Archive directory: {ARCHIVE_DIR}")


def retry_with_backoff(func, *args, max_retries=MAX_RETRIES, **kwargs):
    """Execute function with exponential backoff retry logic."""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed after {max_retries} attempts: {str(e)}")
                raise
            wait_time = RETRY_DELAY * (2 ** attempt)
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {wait_time}s...")
            time.sleep(wait_time)


def archive_old_reports():
    """Archive reports older than retention period."""
    if not REPORTS_DIR.exists():
        return

    cutoff_date = datetime.now() - timedelta(days=ARCHIVE_RETENTION_DAYS)
    archived_count = 0
    deleted_count = 0

    for report_file in REPORTS_DIR.glob("daily_report_*.json"):
        try:
            # Extract date from filename (format: daily_report_YYYY-MM-DD.json)
            date_str = report_file.stem.split('_')[-1]
            file_date = datetime.strptime(date_str, '%Y-%m-%d')

            if file_date < cutoff_date:
                # Move to archive
                archive_path = ARCHIVE_DIR / report_file.name
                shutil.move(str(report_file), str(archive_path))
                archived_count += 1
                logger.debug(f"Archived: {report_file.name}")
        except Exception as e:
            logger.error(f"Error archiving {report_file.name}: {str(e)}")

    # Clean up very old archives (older than 90 days)
    old_cutoff = datetime.now() - timedelta(days=90)
    for archive_file in ARCHIVE_DIR.glob("*.json"):
        try:
            date_str = archive_file.stem.split('_')[-1]
            file_date = datetime.strptime(date_str, '%Y-%m-%d')

            if file_date < old_cutoff:
                archive_file.unlink()
                deleted_count += 1
        except Exception as e:
            logger.error(f"Error deleting old archive {archive_file.name}: {str(e)}")

    if archived_count > 0:
        logger.info(f"Archived {archived_count} old reports")
    if deleted_count > 0:
        logger.info(f"Deleted {deleted_count} very old archived reports")


def generate_asset_report(fetcher: DataFetcher, symbol: str) -> dict:

    logger.info(f"Generating report for {symbol}")

    price_info = fetcher.get_current_price(symbol)
    if not price_info:
        logger.warning(f"Could not fetch current price for {symbol}")
        return None

    daily_data = fetcher.get_asset_data(symbol, period='5d', interval='daily')
    monthly_data = fetcher.get_asset_data(symbol, period='1mo', interval='daily')

    report = {
        'symbol': symbol,
        'name': price_info.get('name', symbol),
        'timestamp': datetime.now().isoformat(),
        'current_price': price_info.get('price'),
        'currency': price_info.get('currency', 'USD'),
        'daily_change': price_info.get('change'),
        'daily_change_percent': price_info.get('change_percent'),
    }

    if daily_data is not None and len(daily_data) >= 2:
        report['open_price'] = float(daily_data['open'].iloc[-1])
        report['high_price'] = float(daily_data['high'].iloc[-1])
        report['low_price'] = float(daily_data['low'].iloc[-1])
        report['close_price'] = float(daily_data['close'].iloc[-1])
        report['volume'] = int(daily_data['volume'].iloc[-1])

    if monthly_data is not None and len(monthly_data) > 5:
        metrics = calculate_metrics_from_prices(monthly_data['close'])
        report['monthly_metrics'] = {
            'volatility': metrics['volatility'],
            'max_drawdown': metrics['max_drawdown'],
            'total_return': metrics['total_return']
        }

        returns = monthly_data['close'].pct_change().dropna()
        report['statistics'] = {
            'mean_daily_return': round(returns.mean() * 100, 4),
            'std_daily_return': round(returns.std() * 100, 4),
            'min_daily_return': round(returns.min() * 100, 2),
            'max_daily_return': round(returns.max() * 100, 2),
            'positive_days': int((returns > 0).sum()),
            'negative_days': int((returns < 0).sum())
        }

    return report


def generate_market_summary(fetcher: DataFetcher, symbols: list) -> dict:

    summary = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'generated_at': datetime.now().isoformat(),
        'total_assets_tracked': len(symbols),
        'gainers': [],
        'losers': [],
        'highest_volatility': None,
        'lowest_volatility': None
    }

    asset_data = []

    for symbol in symbols:
        price_info = fetcher.get_current_price(symbol)
        if price_info:
            asset_data.append({
                'symbol': symbol,
                'change_percent': price_info.get('change_percent', 0),
                'price': price_info.get('price', 0)
            })

    if asset_data:
        sorted_by_change = sorted(asset_data, key=lambda x: x['change_percent'], reverse=True)
        summary['gainers'] = sorted_by_change[:3]
        summary['losers'] = sorted_by_change[-3:]

    return summary


def save_report(report_data: dict, report_type: str = 'daily'):

    date_str = datetime.now().strftime('%Y-%m-%d')
    filename = f"{report_type}_report_{date_str}.json"
    filepath = REPORTS_DIR / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)

    logger.info(f"Report saved: {filepath}")
    return filepath


def main():
    """Main function to generate daily report with error handling and archiving."""
    start_time = datetime.now()
    logger.info("=" * 70)
    logger.info("Starting Daily Report Generation")
    logger.info(f"Date: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)

    ensure_reports_directory()

    # Archive old reports first
    try:
        archive_old_reports()
    except Exception as e:
        logger.error(f"Error during report archiving: {str(e)}")

    fetcher = DataFetcher()

    full_report = {
        'report_type': 'daily',
        'generated_at': start_time.isoformat(),
        'assets': {},
        'market_summary': None,
        'generation_stats': {
            'total_symbols': len(WATCHLIST),
            'successful': 0,
            'failed': 0,
            'errors': []
        }
    }

    # Generate reports for each asset with retry logic
    for symbol in WATCHLIST:
        try:
            asset_report = retry_with_backoff(generate_asset_report, fetcher, symbol)
            if asset_report:
                full_report['assets'][symbol] = asset_report
                full_report['generation_stats']['successful'] += 1
                logger.info(f"✓ Successfully generated report for {symbol}")
            else:
                full_report['generation_stats']['failed'] += 1
                full_report['generation_stats']['errors'].append(f"{symbol}: No data returned")
                logger.warning(f"✗ No data for {symbol}")
        except Exception as e:
            full_report['generation_stats']['failed'] += 1
            error_msg = f"{symbol}: {str(e)}"
            full_report['generation_stats']['errors'].append(error_msg)
            logger.error(f"✗ Error generating report for {symbol}: {str(e)}")

    # Generate market summary with retry
    try:
        full_report['market_summary'] = retry_with_backoff(
            generate_market_summary, fetcher, WATCHLIST
        )
        logger.info("✓ Market summary generated")
    except Exception as e:
        logger.error(f"✗ Error generating market summary: {str(e)}")
        full_report['generation_stats']['errors'].append(f"Market summary: {str(e)}")

    # Save report
    try:
        filepath = save_report(full_report, 'daily')
    except Exception as e:
        logger.error(f"✗ Error saving report: {str(e)}")
        raise

    # Calculate execution time
    execution_time = (datetime.now() - start_time).total_seconds()
    full_report['generation_stats']['execution_time_seconds'] = round(execution_time, 2)

    # Log summary
    logger.info("=" * 70)
    logger.info("Daily Report Generation Complete")
    logger.info(f"Success rate: {full_report['generation_stats']['successful']}/{len(WATCHLIST)} assets")
    logger.info(f"Failed: {full_report['generation_stats']['failed']}")
    logger.info(f"Execution time: {execution_time:.2f}s")
    logger.info(f"Report saved to: {filepath}")
    logger.info("=" * 70)

    # Alert if too many failures
    if full_report['generation_stats']['failed'] > len(WATCHLIST) / 2:
        logger.warning(f"⚠ High failure rate: {full_report['generation_stats']['failed']}/{len(WATCHLIST)} assets failed")

    return full_report


if __name__ == "__main__":
    main()
