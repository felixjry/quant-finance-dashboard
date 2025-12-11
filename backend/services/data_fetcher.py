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

    def __init__(self):
        self._cache: Dict[str, Tuple[pd.DataFrame, datetime]] = {}
        self._cache_duration = timedelta(minutes=5)

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self._cache:
            return False
        _, timestamp = self._cache[cache_key]
        return datetime.now() - timestamp < self._cache_duration
