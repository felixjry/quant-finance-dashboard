

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class StrategyType(str, Enum):
    BUY_AND_HOLD = "buy_and_hold"
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    MOVING_AVERAGE_CROSSOVER = "ma_crossover"

@dataclass
class StrategyResult:
    
    strategy_name: str
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    num_trades: int
    cumulative_returns: pd.Series
    signals: pd.Series

class TradingStrategies:
    

    RISK_FREE_RATE = 0.04  # 4% annual risk-free rate

    def __init__(self, prices: pd.DataFrame):
        
        self.prices = prices.copy()
        self.prices = self.prices.sort_values('date').reset_index(drop=True)
        self.returns = self.prices['close'].pct_change().fillna(0)

    def _calculate_metrics(
        self,
        strategy_returns: pd.Series,
        signals: pd.Series,
        strategy_name: str
    ) -> StrategyResult:
        
        cumulative = (1 + strategy_returns).cumprod()
        total_return = (cumulative.iloc[-1] - 1) * 100

        trading_days = len(strategy_returns)
        years = trading_days / 252
        annualized_return = ((1 + total_return / 100) ** (1 / years) - 1) * 100 if years > 0 else 0

        volatility = strategy_returns.std() * np.sqrt(252) * 100

        excess_return = annualized_return / 100 - self.RISK_FREE_RATE
        sharpe_ratio = excess_return / (volatility / 100) if volatility > 0 else 0

        rolling_max = cumulative.expanding().max()
        drawdown = (cumulative - rolling_max) / rolling_max
        max_drawdown = abs(drawdown.min()) * 100

        signal_changes = signals.diff().fillna(0)
        num_trades = int((signal_changes != 0).sum() / 2)

        if num_trades > 0:
            trade_returns = []
            in_trade = False
            trade_start_value = 1

            for i, (ret, sig) in enumerate(zip(strategy_returns, signals)):
                if sig != 0 and not in_trade:
                    in_trade = True
                    trade_start_value = cumulative.iloc[i-1] if i > 0 else 1
                elif sig == 0 and in_trade:
                    in_trade = False
                    trade_end_value = cumulative.iloc[i]
                    trade_return = (trade_end_value - trade_start_value) / trade_start_value
                    trade_returns.append(trade_return)

            win_rate = (sum(1 for r in trade_returns if r > 0) / len(trade_returns) * 100) if trade_returns else 0
        else:
            win_rate = 0

        return StrategyResult(
            strategy_name=strategy_name,
            total_return=round(total_return, 2),
            annualized_return=round(annualized_return, 2),
            volatility=round(volatility, 2),
            sharpe_ratio=round(sharpe_ratio, 2),
            max_drawdown=round(max_drawdown, 2),
            win_rate=round(win_rate, 2),
            num_trades=num_trades,
            cumulative_returns=cumulative,
            signals=signals
        )

    def buy_and_hold(self) -> StrategyResult:
        
        signals = pd.Series(1, index=self.prices.index)
        strategy_returns = self.returns * signals

        return self._calculate_metrics(strategy_returns, signals, "Buy and Hold")

    def momentum(self, lookback_period: int = 20, holding_period: int = 5) -> StrategyResult:
        
        momentum = self.prices['close'].pct_change(lookback_period)

        signals = pd.Series(0, index=self.prices.index)
        signals[momentum > 0] = 1
        signals[momentum < 0] = -1

        signals = signals.shift(1).fillna(0)

        strategy_returns = self.returns * signals

        return self._calculate_metrics(strategy_returns, signals, f"Momentum ({lookback_period}d)")

    def mean_reversion(self, window: int = 20, num_std: float = 2.0) -> StrategyResult:
        
        rolling_mean = self.prices['close'].rolling(window=window).mean()
        rolling_std = self.prices['close'].rolling(window=window).std()

        upper_band = rolling_mean + (num_std * rolling_std)
        lower_band = rolling_mean - (num_std * rolling_std)

        signals = pd.Series(0, index=self.prices.index)

        current_position = 0
        for i in range(window, len(self.prices)):
            price = self.prices['close'].iloc[i]

            if price < lower_band.iloc[i]:
                current_position = 1
            elif price > upper_band.iloc[i]:
                current_position = -1
            elif lower_band.iloc[i] <= price <= upper_band.iloc[i]:
                if current_position == 1 and price > rolling_mean.iloc[i]:
                    current_position = 0
                elif current_position == -1 and price < rolling_mean.iloc[i]:
                    current_position = 0

            signals.iloc[i] = current_position

        signals = signals.shift(1).fillna(0)
        strategy_returns = self.returns * signals

        return self._calculate_metrics(strategy_returns, signals, f"Mean Reversion ({window}d)")

    def moving_average_crossover(
        self,
        short_window: int = 20,
        long_window: int = 50
    ) -> StrategyResult:
        
        short_ma = self.prices['close'].rolling(window=short_window).mean()
        long_ma = self.prices['close'].rolling(window=long_window).mean()

        signals = pd.Series(0, index=self.prices.index)
        signals[short_ma > long_ma] = 1
        signals[short_ma < long_ma] = -1

        signals = signals.shift(1).fillna(0)

        strategy_returns = self.returns * signals

        return self._calculate_metrics(
            strategy_returns,
            signals,
            f"MA Crossover ({short_window}/{long_window})"
        )

    def run_strategy(
        self,
        strategy_type: StrategyType,
        **params
    ) -> Optional[StrategyResult]:
        
        try:
            if strategy_type == StrategyType.BUY_AND_HOLD:
                return self.buy_and_hold()

            elif strategy_type == StrategyType.MOMENTUM:
                lookback = params.get('lookback_period', 20)
                holding = params.get('holding_period', 5)
                return self.momentum(lookback, holding)

            elif strategy_type == StrategyType.MEAN_REVERSION:
                window = params.get('window', 20)
                num_std = params.get('num_std', 2.0)
                return self.mean_reversion(window, num_std)

            elif strategy_type == StrategyType.MOVING_AVERAGE_CROSSOVER:
                short_window = params.get('short_window', 20)
                long_window = params.get('long_window', 50)
                return self.moving_average_crossover(short_window, long_window)

            else:
                logger.error(f"Unknown strategy type: {strategy_type}")
                return None

        except Exception as e:
            logger.error(f"Error running strategy {strategy_type}: {str(e)}")
            return None

    def compare_strategies(self, strategies_config: Dict) -> Dict[str, StrategyResult]:
        
        results = {}

        for strategy_type, params in strategies_config.items():
            result = self.run_strategy(StrategyType(strategy_type), **params)
            if result:
                results[result.strategy_name] = result

        return results

def calculate_metrics_from_prices(prices: pd.Series) -> Dict:
    
    returns = prices.pct_change().dropna()

    volatility = returns.std() * np.sqrt(252) * 100

    total_return = ((prices.iloc[-1] / prices.iloc[0]) - 1) * 100

    rolling_max = prices.expanding().max()
    drawdown = (prices - rolling_max) / rolling_max
    max_drawdown = abs(drawdown.min()) * 100

    years = len(returns) / 252
    annualized_return = ((1 + total_return / 100) ** (1 / years) - 1) * 100 if years > 0 else 0

    excess_return = annualized_return / 100 - 0.04
    sharpe_ratio = excess_return / (volatility / 100) if volatility > 0 else 0

    return {
        'total_return': round(total_return, 2),
        'annualized_return': round(annualized_return, 2),
        'volatility': round(volatility, 2),
        'sharpe_ratio': round(sharpe_ratio, 2),
        'max_drawdown': round(max_drawdown, 2)
    }
