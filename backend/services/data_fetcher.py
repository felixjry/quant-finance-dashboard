"""
Data fetching service for financial data using yfinance
Author: Lucas Soares (Quant A - Single Asset Analysis)
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFetcher:
    """
    Service to fetch financial data from Yahoo Finance with caching
    """

    PERIOD_MAP = {
        'daily': '1d',
        'weekly': '1wk',
        'monthly': '1mo'
    }

    def __init__(self):
        self._cache: Dict[str, Tuple[pd.DataFrame, datetime]] = {}
        self._cache_duration = timedelta(minutes=5)

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self._cache:
            return False
        _, timestamp = self._cache[cache_key]
        return datetime.now() - timestamp < self._cache_duration

    def get_asset_data(
        self,
        symbol: str,
        period: str = '1y',
        interval: str = 'daily'
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical asset data with caching

        Args:
            symbol: Asset ticker symbol
            period: Time period (e.g., '1y', '6mo', '5d')
            interval: Data interval (daily, weekly, monthly)

        Returns:
            DataFrame with OHLCV data or None on error
        """
        cache_key = f"{symbol}_{period}_{interval}"

        if self._is_cache_valid(cache_key):
            logger.info(f"Returning cached data for {symbol}")
            return self._cache[cache_key][0].copy()

        try:
            ticker = yf.Ticker(symbol)
            yf_interval = self.PERIOD_MAP.get(interval, '1d')

            df = ticker.history(period=period, interval=yf_interval)

            if df.empty:
                logger.warning(f"No data returned for {symbol}")
                return None

            # Clean column names
            df = df.reset_index()
            df.columns = [col.lower().replace(' ', '_') for col in df.columns]

            # Handle date column
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)
            elif 'datetime' in df.columns:
                df['date'] = pd.to_datetime(df['datetime']).dt.tz_localize(None)
                df = df.drop(columns=['datetime'])

            # Cache the result
            self._cache[cache_key] = (df.copy(), datetime.now())
            logger.info(f"Fetched {len(df)} rows for {symbol}")

            return df

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
