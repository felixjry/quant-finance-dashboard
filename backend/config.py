"""
Configuration file for the Quant Finance Dashboard
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import List

BASE_DIR = Path(__file__).parent

REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"


@dataclass
class APIConfig:
    """API Server Configuration"""
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
    """Data fetching and processing configuration"""
    cache_duration_minutes: int = 5
    default_period: str = "1y"
    default_interval: str = "daily"
    risk_free_rate: float = 0.04
    trading_days_per_year: int = 252


# Global configuration instances
api_config = APIConfig()
data_config = DataConfig()


def ensure_directories():
    """Create necessary directories if they don't exist"""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
