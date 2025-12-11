

import os
from pathlib import Path
from dataclasses import dataclass
from typing import List

BASE_DIR = Path(__file__).parent

REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"


@dataclass
class APIConfig:
    
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    cors_origins: List[str] = None

    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = [
                "http://localhost:8080",
                "http://localhost:3000",
                "http://127.0.0.1:8080"
            ]


@dataclass
class DataConfig:
    
    cache_duration_minutes: int = 5
    default_period: str = "1y"
    default_interval: str = "daily"
    risk_free_rate: float = 0.04
    trading_days_per_year: int = 252


@dataclass
class ReportConfig:
    
    report_time: str = "20:00"
    watchlist: List[str] = None

    def __post_init__(self):
        if self.watchlist is None:
            self.watchlist = [
                'AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN',
                'SPY', 'QQQ',
                'BTC-USD', 'ETH-USD',
                'EURUSD=X',
                'ENGI.PA', 'TTE.PA'
            ]


api_config = APIConfig()
data_config = DataConfig()
report_config = ReportConfig()


def ensure_directories():
    
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


SUPPORTED_ASSETS = {
    'stocks_us': {
        'AAPL': 'Apple Inc.',
        'MSFT': 'Microsoft Corporation',
        'GOOGL': 'Alphabet Inc.',
        'TSLA': 'Tesla Inc.',
        'AMZN': 'Amazon.com Inc.',
        'META': 'Meta Platforms Inc.',
        'NVDA': 'NVIDIA Corporation',
        'JPM': 'JPMorgan Chase & Co.'
    },
    'stocks_fr': {
        'ENGI.PA': 'Engie SA',
        'TTE.PA': 'TotalEnergies SE',
        'BNP.PA': 'BNP Paribas SA',
        'SAN.PA': 'Sanofi SA',
        'AIR.PA': 'Airbus SE',
        'OR.PA': "L'Oréal SA"
    },
    'etfs': {
        'SPY': 'SPDR S&P 500 ETF',
        'QQQ': 'Invesco QQQ Trust',
        'IWM': 'iShares Russell 2000 ETF',
        'VTI': 'Vanguard Total Stock Market ETF',
        'EFA': 'iShares MSCI EAFE ETF'
    },
    'crypto': {
        'BTC-USD': 'Bitcoin',
        'ETH-USD': 'Ethereum',
        'SOL-USD': 'Solana'
    },
    'forex': {
        'EURUSD=X': 'EUR/USD',
        'GBPUSD=X': 'GBP/USD',
        'USDJPY=X': 'USD/JPY',
        'USDCHF=X': 'USD/CHF'
    }
}

STRATEGY_DESCRIPTIONS = {
    'buy_and_hold': {
        'name': 'Buy and Hold',
        'description': 'Simple strategy that buys at the beginning and holds until the end.',
        'parameters': []
    },
    'momentum': {
        'name': 'Momentum',
        'description': 'Goes long when past returns are positive, otherwise stays out or goes short.',
        'parameters': ['lookback_period', 'holding_period']
    },
    'mean_reversion': {
        'name': 'Mean Reversion',
        'description': 'Buys when price is below lower Bollinger Band, sells when above upper band.',
        'parameters': ['window', 'num_std']
    },
    'ma_crossover': {
        'name': 'Moving Average Crossover',
        'description': 'Buys when short MA crosses above long MA, sells when it crosses below.',
        'parameters': ['short_window', 'long_window']
    }
}

WEIGHTING_DESCRIPTIONS = {
    'equal_weight': {
        'name': 'Equal Weight',
        'description': 'All assets receive the same weight in the portfolio.'
    },
    'risk_parity': {
        'name': 'Risk Parity',
        'description': 'Weights assets so each contributes equally to portfolio risk.'
    },
    'min_variance': {
        'name': 'Minimum Variance',
        'description': 'Minimizes total portfolio variance.'
    },
    'max_sharpe': {
        'name': 'Maximum Sharpe Ratio',
        'description': 'Maximizes risk-adjusted returns.'
    },
    'custom_weights': {
        'name': 'Custom Weights',
        'description': 'User-defined weights for each asset.'
    }
}
