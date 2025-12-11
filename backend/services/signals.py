"""
Trading Signals Detection
Detect buy/sell signals using technical indicators
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class SignalType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    NEUTRAL = "neutral"

class SignalStrength(str, Enum):
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"

@dataclass
class TradingSignal:
    """Represents a trading signal"""
    symbol: str
    signal_type: SignalType
    strength: SignalStrength
    strategy: str
    price: float
    timestamp: str
    indicators: Dict[str, float]
    message: str

class SignalDetector:
    """Detect trading signals from price data"""

    def __init__(self, data: pd.DataFrame):
        """
        Initialize with price data
        data must have columns: date, open, high, low, close, volume
        """
        self.data = data.copy()
        self.data['date'] = pd.to_datetime(self.data['date'])
        self.data = self.data.sort_values('date').reset_index(drop=True)

    def calculate_sma(self, period: int, column: str = 'close') -> pd.Series:
        """Calculate Simple Moving Average"""
        return self.data[column].rolling(window=period).mean()

    def calculate_ema(self, period: int, column: str = 'close') -> pd.Series:
        """Calculate Exponential Moving Average"""
        return self.data[column].ewm(span=period, adjust=False).mean()

    def calculate_rsi(self, period: int = 14, column: str = 'close') -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = self.data[column].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_macd(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
        column: str = 'close'
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD, Signal line, and Histogram"""
        ema_fast = self.data[column].ewm(span=fast_period, adjust=False).mean()
        ema_slow = self.data[column].ewm(span=slow_period, adjust=False).mean()

        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

    def calculate_bollinger_bands(
        self,
        period: int = 20,
        std_dev: float = 2.0,
        column: str = 'close'
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        sma = self.data[column].rolling(window=period).mean()
        std = self.data[column].rolling(window=period).std()

        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)

        return upper_band, sma, lower_band

    def calculate_stochastic(
        self,
        k_period: int = 14,
        d_period: int = 3
    ) -> Tuple[pd.Series, pd.Series]:
        """Calculate Stochastic Oscillator"""
        low_min = self.data['low'].rolling(window=k_period).min()
        high_max = self.data['high'].rolling(window=k_period).max()

        k_line = 100 * ((self.data['close'] - low_min) / (high_max - low_min))
        d_line = k_line.rolling(window=d_period).mean()

        return k_line, d_line

    def detect_ma_crossover(
        self,
        short_period: int = 20,
        long_period: int = 50
    ) -> Optional[TradingSignal]:
        """Detect Moving Average Crossover signals"""
        if len(self.data) < long_period + 1:
            return None

        sma_short = self.calculate_sma(short_period)
        sma_long = self.calculate_sma(long_period)

        # Get last two points
        idx_current = len(self.data) - 1
        idx_previous = idx_current - 1

        short_current = sma_short.iloc[idx_current]
        short_previous = sma_short.iloc[idx_previous]
        long_current = sma_long.iloc[idx_current]
        long_previous = sma_long.iloc[idx_previous]

        if pd.isna(short_current) or pd.isna(long_current):
            return None

        current_price = self.data['close'].iloc[idx_current]
        timestamp = self.data['date'].iloc[idx_current].isoformat()
        symbol = "UNKNOWN"

        # Bullish crossover (Golden Cross)
        if short_previous < long_previous and short_current > long_current:
            distance_pct = ((short_current - long_current) / long_current) * 100

            if distance_pct > 2:
                strength = SignalStrength.STRONG
            elif distance_pct > 1:
                strength = SignalStrength.MODERATE
            else:
                strength = SignalStrength.WEAK

            return TradingSignal(
                symbol=symbol,
                signal_type=SignalType.BUY,
                strength=strength,
                strategy="MA Crossover",
                price=current_price,
                timestamp=timestamp,
                indicators={
                    f'sma_{short_period}': round(short_current, 2),
                    f'sma_{long_period}': round(long_current, 2),
                    'crossover_strength': round(distance_pct, 2)
                },
                message=f"Golden Cross: SMA{short_period} crossed above SMA{long_period}"
            )

        # Bearish crossover (Death Cross)
        elif short_previous > long_previous and short_current < long_current:
            distance_pct = ((long_current - short_current) / long_current) * 100

            if distance_pct > 2:
                strength = SignalStrength.STRONG
            elif distance_pct > 1:
                strength = SignalStrength.MODERATE
            else:
                strength = SignalStrength.WEAK

            return TradingSignal(
                symbol=symbol,
                signal_type=SignalType.SELL,
                strength=strength,
                strategy="MA Crossover",
                price=current_price,
                timestamp=timestamp,
                indicators={
                    f'sma_{short_period}': round(short_current, 2),
                    f'sma_{long_period}': round(long_current, 2),
                    'crossover_strength': round(distance_pct, 2)
                },
                message=f"Death Cross: SMA{short_period} crossed below SMA{long_period}"
            )

        return None

    def detect_rsi_signal(
        self,
        period: int = 14,
        oversold_threshold: float = 30.0,
        overbought_threshold: float = 70.0
    ) -> Optional[TradingSignal]:
        """Detect RSI-based signals"""
        if len(self.data) < period + 1:
            return None

        rsi = self.calculate_rsi(period)

        idx_current = len(self.data) - 1
        idx_previous = idx_current - 1

        rsi_current = rsi.iloc[idx_current]
        rsi_previous = rsi.iloc[idx_previous]

        if pd.isna(rsi_current):
            return None

        current_price = self.data['close'].iloc[idx_current]
        timestamp = self.data['date'].iloc[idx_current].isoformat()
        symbol = "UNKNOWN"

        # Oversold condition (potential buy)
        if rsi_current < oversold_threshold and rsi_previous >= oversold_threshold:
            if rsi_current < 20:
                strength = SignalStrength.STRONG
            elif rsi_current < 25:
                strength = SignalStrength.MODERATE
            else:
                strength = SignalStrength.WEAK

            return TradingSignal(
                symbol=symbol,
                signal_type=SignalType.BUY,
                strength=strength,
                strategy="RSI",
                price=current_price,
                timestamp=timestamp,
                indicators={
                    'rsi': round(rsi_current, 2),
                    'rsi_previous': round(rsi_previous, 2),
                    'threshold': oversold_threshold
                },
                message=f"RSI Oversold: {rsi_current:.1f} below {oversold_threshold}"
            )

        # Overbought condition (potential sell)
        elif rsi_current > overbought_threshold and rsi_previous <= overbought_threshold:
            if rsi_current > 80:
                strength = SignalStrength.STRONG
            elif rsi_current > 75:
                strength = SignalStrength.MODERATE
            else:
                strength = SignalStrength.WEAK

            return TradingSignal(
                symbol=symbol,
                signal_type=SignalType.SELL,
                strength=strength,
                strategy="RSI",
                price=current_price,
                timestamp=timestamp,
                indicators={
                    'rsi': round(rsi_current, 2),
                    'rsi_previous': round(rsi_previous, 2),
                    'threshold': overbought_threshold
                },
                message=f"RSI Overbought: {rsi_current:.1f} above {overbought_threshold}"
            )

        return None

    def detect_macd_signal(self) -> Optional[TradingSignal]:
        """Detect MACD crossover signals"""
        if len(self.data) < 50:
            return None

        macd_line, signal_line, histogram = self.calculate_macd()

        idx_current = len(self.data) - 1
        idx_previous = idx_current - 1

        macd_current = macd_line.iloc[idx_current]
        macd_previous = macd_line.iloc[idx_previous]
        signal_current = signal_line.iloc[idx_current]
        signal_previous = signal_line.iloc[idx_previous]
        hist_current = histogram.iloc[idx_current]

        if pd.isna(macd_current) or pd.isna(signal_current):
            return None

        current_price = self.data['close'].iloc[idx_current]
        timestamp = self.data['date'].iloc[idx_current].isoformat()
        symbol = "UNKNOWN"

        # Bullish MACD crossover
        if macd_previous < signal_previous and macd_current > signal_current:
            if abs(hist_current) > 1:
                strength = SignalStrength.STRONG
            elif abs(hist_current) > 0.5:
                strength = SignalStrength.MODERATE
            else:
                strength = SignalStrength.WEAK

            return TradingSignal(
                symbol=symbol,
                signal_type=SignalType.BUY,
                strength=strength,
                strategy="MACD",
                price=current_price,
                timestamp=timestamp,
                indicators={
                    'macd': round(macd_current, 2),
                    'signal': round(signal_current, 2),
                    'histogram': round(hist_current, 2)
                },
                message="MACD Bullish Crossover: MACD crossed above Signal line"
            )

        # Bearish MACD crossover
        elif macd_previous > signal_previous and macd_current < signal_current:
            if abs(hist_current) > 1:
                strength = SignalStrength.STRONG
            elif abs(hist_current) > 0.5:
                strength = SignalStrength.MODERATE
            else:
                strength = SignalStrength.WEAK

            return TradingSignal(
                symbol=symbol,
                signal_type=SignalType.SELL,
                strength=strength,
                strategy="MACD",
                price=current_price,
                timestamp=timestamp,
                indicators={
                    'macd': round(macd_current, 2),
                    'signal': round(signal_current, 2),
                    'histogram': round(hist_current, 2)
                },
                message="MACD Bearish Crossover: MACD crossed below Signal line"
            )

        return None

    def detect_bollinger_signal(self, period: int = 20, std_dev: float = 2.0) -> Optional[TradingSignal]:
        """Detect Bollinger Bands breakout signals"""
        if len(self.data) < period + 1:
            return None

        upper, middle, lower = self.calculate_bollinger_bands(period, std_dev)

        idx_current = len(self.data) - 1
        idx_previous = idx_current - 1

        price_current = self.data['close'].iloc[idx_current]
        price_previous = self.data['close'].iloc[idx_previous]
        upper_current = upper.iloc[idx_current]
        lower_current = lower.iloc[idx_current]
        middle_current = middle.iloc[idx_current]

        if pd.isna(upper_current) or pd.isna(lower_current):
            return None

        timestamp = self.data['date'].iloc[idx_current].isoformat()
        symbol = "UNKNOWN"

        band_width = ((upper_current - lower_current) / middle_current) * 100

        # Price bouncing off lower band (potential buy)
        if price_previous <= lower.iloc[idx_previous] and price_current > lower_current:
            distance_from_middle = ((middle_current - price_current) / middle_current) * 100

            if distance_from_middle > 5:
                strength = SignalStrength.STRONG
            elif distance_from_middle > 3:
                strength = SignalStrength.MODERATE
            else:
                strength = SignalStrength.WEAK

            return TradingSignal(
                symbol=symbol,
                signal_type=SignalType.BUY,
                strength=strength,
                strategy="Bollinger Bands",
                price=price_current,
                timestamp=timestamp,
                indicators={
                    'price': round(price_current, 2),
                    'lower_band': round(lower_current, 2),
                    'middle_band': round(middle_current, 2),
                    'band_width': round(band_width, 2)
                },
                message=f"Bollinger Bounce: Price bounced off lower band"
            )

        # Price bouncing off upper band (potential sell)
        elif price_previous >= upper.iloc[idx_previous] and price_current < upper_current:
            distance_from_middle = ((price_current - middle_current) / middle_current) * 100

            if distance_from_middle > 5:
                strength = SignalStrength.STRONG
            elif distance_from_middle > 3:
                strength = SignalStrength.MODERATE
            else:
                strength = SignalStrength.WEAK

            return TradingSignal(
                symbol=symbol,
                signal_type=SignalType.SELL,
                strength=strength,
                strategy="Bollinger Bands",
                price=price_current,
                timestamp=timestamp,
                indicators={
                    'price': round(price_current, 2),
                    'upper_band': round(upper_current, 2),
                    'middle_band': round(middle_current, 2),
                    'band_width': round(band_width, 2)
                },
                message=f"Bollinger Bounce: Price bounced off upper band"
            )

        return None

    def detect_all_signals(self, symbol: str = "UNKNOWN") -> List[TradingSignal]:
        """Run all signal detection strategies"""
        signals = []

        # MA Crossover
        ma_signal = self.detect_ma_crossover(short_period=20, long_period=50)
        if ma_signal:
            ma_signal.symbol = symbol
            signals.append(ma_signal)

        # RSI
        rsi_signal = self.detect_rsi_signal(period=14)
        if rsi_signal:
            rsi_signal.symbol = symbol
            signals.append(rsi_signal)

        # MACD
        macd_signal = self.detect_macd_signal()
        if macd_signal:
            macd_signal.symbol = symbol
            signals.append(macd_signal)

        # Bollinger Bands
        bb_signal = self.detect_bollinger_signal(period=20)
        if bb_signal:
            bb_signal.symbol = symbol
            signals.append(bb_signal)

        return signals
