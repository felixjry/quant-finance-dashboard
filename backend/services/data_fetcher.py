

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFetcher:
    

    SUPPORTED_ASSETS = {
        'stocks': ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN', 'META', 'NVDA', 'JPM'],
        'etfs': ['SPY', 'QQQ', 'IWM', 'VTI', 'EFA'],
        'crypto': ['BTC-USD', 'ETH-USD', 'SOL-USD'],
        'forex': ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X'],
        'french': ['ENGI.PA', 'TTE.PA', 'BNP.PA', 'SAN.PA']
    }

    PERIOD_MAP = {
        'daily': '1d',
        'weekly': '1wk',
        'monthly': '1mo'
    }

    def __init__(self):
        self._cache: Dict[str, Tuple[pd.DataFrame, datetime]] = {}
        self._cache_duration = timedelta(minutes=5)

    def _is_cache_valid(self, symbol: str) -> bool:

        if symbol not in self._cache:
            return False
        _, timestamp = self._cache[symbol]
        return datetime.now() - timestamp < self._cache_duration

    def _validate_price_data(self, df: pd.DataFrame, symbol: str) -> bool:
        """Validate price data for anomalies and data quality issues."""
        if df.empty:
            return True

        price_cols = ['open', 'high', 'low', 'close']
        available_price_cols = [col for col in price_cols if col in df.columns]

        if not available_price_cols:
            logger.warning(f"{symbol}: No price columns found in data")
            return False

        # Check for negative prices
        for col in available_price_cols:
            if (df[col] < 0).any():
                logger.error(f"{symbol}: Negative prices detected in {col}")
                return False

        # Check for extreme price changes (> 100% in one period - likely data error)
        if 'close' in df.columns and len(df) > 1:
            returns = df['close'].pct_change()
            extreme_moves = returns[returns.abs() > 1.0]
            if not extreme_moves.empty:
                logger.warning(f"{symbol}: Extreme price changes detected: {len(extreme_moves)} occurrences")

        # Check for zero prices (data error)
        for col in available_price_cols:
            zero_prices = (df[col] == 0).sum()
            if zero_prices > 0:
                logger.warning(f"{symbol}: Found {zero_prices} zero prices in {col}")

        return True

    def _validate_volume_data(self, df: pd.DataFrame, symbol: str) -> bool:
        """Validate volume data for anomalies."""
        if 'volume' not in df.columns:
            return True

        # Check for negative volumes
        if (df['volume'] < 0).any():
            logger.error(f"{symbol}: Negative volumes detected")
            return False

        # Check for suspiciously low average volume (potential delisted stock)
        avg_volume = df['volume'].mean()
        if avg_volume < 1000 and avg_volume > 0:
            logger.warning(f"{symbol}: Very low average volume ({avg_volume:.0f}), data may be unreliable")

        return True

    def _check_data_gaps(self, df: pd.DataFrame, symbol: str, interval: str) -> None:
        """Check for unexpected gaps in data (excluding weekends for daily data)."""
        if df.empty or 'date' not in df.columns or len(df) < 2:
            return

        if interval != 'daily':
            return

        dates = pd.to_datetime(df['date'])
        date_diffs = dates.diff()

        # For daily data, expect 1-3 days between points (accounting for weekends)
        large_gaps = date_diffs[date_diffs > timedelta(days=7)]

        if not large_gaps.empty:
            logger.warning(f"{symbol}: Found {len(large_gaps)} data gaps > 7 days")
            for idx, gap in large_gaps.items():
                logger.debug(f"{symbol}: Gap of {gap.days} days at index {idx}")

    def _validate_and_clean_data(self, df: pd.DataFrame, symbol: str, interval: str) -> Optional[pd.DataFrame]:
        """Validate data quality and clean if necessary."""
        if df is None or df.empty:
            return df

        # Run validations
        if not self._validate_price_data(df, symbol):
            logger.error(f"{symbol}: Price data validation failed")
            return None

        if not self._validate_volume_data(df, symbol):
            logger.error(f"{symbol}: Volume data validation failed")
            return None

        # Check for gaps (warning only, don't fail)
        self._check_data_gaps(df, symbol, interval)

        # Remove rows with NaN in critical price columns
        critical_cols = [col for col in ['close', 'open', 'high', 'low'] if col in df.columns]
        if critical_cols:
            initial_len = len(df)
            df = df.dropna(subset=critical_cols)
            removed = initial_len - len(df)
            if removed > 0:
                logger.info(f"{symbol}: Removed {removed} rows with missing price data")

        return df

    def get_asset_data(
        self,
        symbol: str,
        period: str = '1y',
        interval: str = 'daily'
    ) -> Optional[pd.DataFrame]:

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

            df = df.reset_index()
            df.columns = [col.lower().replace(' ', '_') for col in df.columns]

            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)
            elif 'datetime' in df.columns:
                df['date'] = pd.to_datetime(df['datetime']).dt.tz_localize(None)
                df = df.drop(columns=['datetime'])

            # Validate and clean data
            df = self._validate_and_clean_data(df, symbol, interval)
            if df is None or df.empty:
                logger.error(f"Data validation failed for {symbol}")
                return None

            self._cache[cache_key] = (df.copy(), datetime.now())
            logger.info(f"Fetched and validated {len(df)} rows for {symbol}")

            return df

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None

    def get_asset_data_with_dates(
        self,
        symbol: str,
        start: str,
        end: str,
        interval: str = 'daily'
    ) -> Optional[pd.DataFrame]:

        cache_key = f"{symbol}_{start}_{end}_{interval}"

        if self._is_cache_valid(cache_key):
            logger.info(f"Returning cached data for {symbol}")
            return self._cache[cache_key][0].copy()

        try:
            ticker = yf.Ticker(symbol)
            yf_interval = self.PERIOD_MAP.get(interval, '1d')

            df = ticker.history(start=start, end=end, interval=yf_interval)

            if df.empty:
                logger.warning(f"No data returned for {symbol}")
                return None

            df = df.reset_index()
            df.columns = [col.lower().replace(' ', '_') for col in df.columns]

            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)
            elif 'datetime' in df.columns:
                df['date'] = pd.to_datetime(df['datetime']).dt.tz_localize(None)
                df = df.drop(columns=['datetime'])

            # Validate and clean data
            df = self._validate_and_clean_data(df, symbol, interval)
            if df is None or df.empty:
                logger.error(f"Data validation failed for {symbol}")
                return None

            self._cache[cache_key] = (df.copy(), datetime.now())
            logger.info(f"Fetched and validated {len(df)} rows for {symbol} from {start} to {end}")

            return df

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None

    def get_current_price(self, symbol: str) -> Optional[Dict]:
        
        cache_key = f"{symbol}_price"

        if self._is_cache_valid(cache_key):
            return self._cache[cache_key][0]

        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='5d')

            if hist.empty:
                return None

            current_price = hist['Close'].iloc[-1]
            previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else hist['Open'].iloc[-1]

            change = current_price - previous_close
            change_percent = (change / previous_close * 100) if previous_close else 0

            result = {
                'symbol': symbol,
                'price': round(float(current_price), 2),
                'change': round(float(change), 2),
                'change_percent': round(float(change_percent), 2),
                'currency': 'USD',
                'name': symbol,
                'volume': int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else None,
                'timestamp': datetime.now().isoformat()
            }

            self._cache[cache_key] = (result, datetime.now())
            return result

        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {str(e)}")
            return None

    def get_multiple_assets(
        self,
        symbols: List[str],
        period: str = '1y',
        interval: str = 'daily'
    ) -> Dict[str, pd.DataFrame]:
        
        results = {}

        for symbol in symbols:
            data = self.get_asset_data(symbol, period, interval)
            if data is not None:
                results[symbol] = data

        return results

    def get_aligned_prices(
        self,
        symbols: List[str],
        period: str = '1y',
        interval: str = 'daily',
        start: str = None,
        end: str = None
    ) -> Optional[pd.DataFrame]:

        try:
            if start and end:
                data = yf.download(
                    symbols,
                    start=start,
                    end=end,
                    interval=self.PERIOD_MAP.get(interval, '1d'),
                    group_by='ticker',
                    auto_adjust=True,
                    progress=False
                )
            else:
                data = yf.download(
                    symbols,
                    period=period,
                    interval=self.PERIOD_MAP.get(interval, '1d'),
                    group_by='ticker',
                    auto_adjust=True,
                    progress=False
                )

            if data.empty:
                return None

            if len(symbols) == 1:
                prices = data['Close'].to_frame(name=symbols[0])
            else:
                prices = data.xs('Close', level=1, axis=1)

            prices = prices.dropna()
            prices.index = pd.to_datetime(prices.index).tz_localize(None)

            return prices

        except Exception as e:
            logger.error(f"Error fetching aligned prices: {str(e)}")
            return None

    def get_available_symbols(self) -> Dict[str, List[str]]:
        
        return self.SUPPORTED_ASSETS.copy()

    def validate_symbol(self, symbol: str) -> bool:
        
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='5d')
            return not hist.empty
        except Exception:
            return False

    def get_bulk_quotes(self, symbols: List[str]) -> List[Dict]:
        
        cache_key = f"bulk_{'_'.join(sorted(symbols))}"

        if self._is_cache_valid(cache_key):
            return self._cache[cache_key][0]

        try:
            symbols_str = ' '.join(symbols)
            data = yf.download(symbols_str, period='5d', group_by='ticker', progress=False, threads=True)

            quotes = []
            for symbol in symbols:
                try:
                    if len(symbols) == 1:
                        hist = data
                    else:
                        hist = data[symbol] if symbol in data.columns.get_level_values(0) else None

                    if hist is None or hist.empty:
                        continue

                    hist = hist.dropna()
                    if len(hist) < 2:
                        continue

                    current_price = float(hist['Close'].iloc[-1])
                    previous_close = float(hist['Close'].iloc[-2])

                    change = current_price - previous_close
                    change_percent = (change / previous_close * 100) if previous_close else 0

                    quotes.append({
                        'symbol': symbol,
                        'price': round(current_price, 2),
                        'change': round(change, 2),
                        'changePercent': round(change_percent, 2),
                    })
                except Exception as e:
                    logger.warning(f"Error processing {symbol}: {e}")
                    continue

            self._cache[cache_key] = (quotes, datetime.now())
            return quotes

        except Exception as e:
            logger.error(f"Error fetching bulk quotes: {e}")
            return []

    def clear_cache(self):
        
        self._cache.clear()
        logger.info("Cache cleared")

# Singleton instance for use across the application
data_fetcher = DataFetcher()
