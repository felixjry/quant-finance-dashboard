

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class WeightingStrategy(str, Enum):
    EQUAL_WEIGHT = "equal_weight"
    CUSTOM_WEIGHTS = "custom_weights"
    RISK_PARITY = "risk_parity"
    MIN_VARIANCE = "min_variance"
    MAX_SHARPE = "max_sharpe"

class RebalanceFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"

@dataclass
class PortfolioMetrics:
    
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    diversification_ratio: float
    weights: Dict[str, float]
    correlation_matrix: pd.DataFrame
    cumulative_returns: pd.Series

class PortfolioAnalyzer:
    

    RISK_FREE_RATE = 0.04
    TRADING_DAYS = 252

    def __init__(self, prices: pd.DataFrame):
        
        self.prices = prices.copy()
        self.returns = self.prices.pct_change().dropna()
        self.assets = list(self.prices.columns)
        self.n_assets = len(self.assets)

    def calculate_correlation_matrix(self) -> pd.DataFrame:
        
        return self.returns.corr()

    def calculate_covariance_matrix(self, annualized: bool = True) -> pd.DataFrame:
        
        cov = self.returns.cov()
        if annualized:
            cov = cov * self.TRADING_DAYS
        return cov

    def get_equal_weights(self) -> Dict[str, float]:
        
        weight = 1.0 / self.n_assets
        return {asset: round(weight, 4) for asset in self.assets}

    def get_risk_parity_weights(self) -> Dict[str, float]:
        
        volatilities = self.returns.std() * np.sqrt(self.TRADING_DAYS)
        inv_vol = 1 / volatilities
        weights = inv_vol / inv_vol.sum()

        return {asset: round(w, 4) for asset, w in zip(self.assets, weights)}

    def get_min_variance_weights(self) -> Dict[str, float]:
        
        cov_matrix = self.calculate_covariance_matrix()
        inv_cov = np.linalg.inv(cov_matrix.values)
        ones = np.ones(self.n_assets)

        weights = inv_cov @ ones / (ones @ inv_cov @ ones)
        weights = np.maximum(weights, 0)
        weights = weights / weights.sum()

        return {asset: round(w, 4) for asset, w in zip(self.assets, weights)}

    def get_max_sharpe_weights(self, iterations: int = 10000) -> Dict[str, float]:
        
        mean_returns = self.returns.mean() * self.TRADING_DAYS
        cov_matrix = self.calculate_covariance_matrix()

        best_sharpe = -np.inf
        best_weights = None

        for _ in range(iterations):
            weights = np.random.random(self.n_assets)
            weights = weights / weights.sum()

            port_return = np.dot(weights, mean_returns)
            port_vol = np.sqrt(weights @ cov_matrix.values @ weights)
            sharpe = (port_return - self.RISK_FREE_RATE) / port_vol

            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_weights = weights

        return {asset: round(w, 4) for asset, w in zip(self.assets, best_weights)}

    def get_weights(
        self,
        strategy: WeightingStrategy,
        custom_weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, float]:
        
        if strategy == WeightingStrategy.EQUAL_WEIGHT:
            return self.get_equal_weights()

        elif strategy == WeightingStrategy.RISK_PARITY:
            return self.get_risk_parity_weights()

        elif strategy == WeightingStrategy.MIN_VARIANCE:
            return self.get_min_variance_weights()

        elif strategy == WeightingStrategy.MAX_SHARPE:
            return self.get_max_sharpe_weights()

        elif strategy == WeightingStrategy.CUSTOM_WEIGHTS:
            if custom_weights is None:
                return self.get_equal_weights()
            total = sum(custom_weights.values())
            return {k: round(v / total, 4) for k, v in custom_weights.items()}

        return self.get_equal_weights()

    def calculate_portfolio_returns(
        self,
        weights: Dict[str, float],
        rebalance_freq: RebalanceFrequency = RebalanceFrequency.MONTHLY
    ) -> pd.Series:
        
        weight_array = np.array([weights[asset] for asset in self.assets])

        if rebalance_freq == RebalanceFrequency.DAILY:
            portfolio_returns = (self.returns * weight_array).sum(axis=1)

        else:
            freq_map = {
                RebalanceFrequency.WEEKLY: 'W',
                RebalanceFrequency.MONTHLY: 'M',
                RebalanceFrequency.QUARTERLY: 'Q'
            }

            portfolio_returns = pd.Series(index=self.returns.index, dtype=float)
            current_weights = weight_array.copy()

            rebalance_dates = self.returns.resample(freq_map[rebalance_freq]).last().index

            for i, (date, row) in enumerate(self.returns.iterrows()):
                port_ret = (row * current_weights).sum()
                portfolio_returns[date] = port_ret

                current_weights = current_weights * (1 + row.values)
                current_weights = current_weights / current_weights.sum()

                if date in rebalance_dates:
                    current_weights = weight_array.copy()

        return portfolio_returns

    def analyze_portfolio(
        self,
        weighting_strategy: WeightingStrategy = WeightingStrategy.EQUAL_WEIGHT,
        custom_weights: Optional[Dict[str, float]] = None,
        rebalance_freq: RebalanceFrequency = RebalanceFrequency.MONTHLY
    ) -> PortfolioMetrics:
        
        weights = self.get_weights(weighting_strategy, custom_weights)
        portfolio_returns = self.calculate_portfolio_returns(weights, rebalance_freq)

        cumulative = (1 + portfolio_returns).cumprod()
        total_return = (cumulative.iloc[-1] - 1) * 100

        years = len(portfolio_returns) / self.TRADING_DAYS
        annualized_return = ((1 + total_return / 100) ** (1 / years) - 1) * 100 if years > 0 else 0

        volatility = portfolio_returns.std() * np.sqrt(self.TRADING_DAYS) * 100

        excess_return = annualized_return / 100 - self.RISK_FREE_RATE
        sharpe_ratio = excess_return / (volatility / 100) if volatility > 0 else 0

        rolling_max = cumulative.expanding().max()
        drawdown = (cumulative - rolling_max) / rolling_max
        max_drawdown = abs(drawdown.min()) * 100

        weight_array = np.array([weights[asset] for asset in self.assets])
        asset_vols = self.returns.std() * np.sqrt(self.TRADING_DAYS)
        weighted_avg_vol = (weight_array * asset_vols).sum()
        portfolio_vol = volatility / 100
        diversification_ratio = weighted_avg_vol / portfolio_vol if portfolio_vol > 0 else 1

        correlation_matrix = self.calculate_correlation_matrix()

        return PortfolioMetrics(
            total_return=round(total_return, 2),
            annualized_return=round(annualized_return, 2),
            volatility=round(volatility, 2),
            sharpe_ratio=round(sharpe_ratio, 2),
            max_drawdown=round(max_drawdown, 2),
            diversification_ratio=round(diversification_ratio, 2),
            weights=weights,
            correlation_matrix=correlation_matrix,
            cumulative_returns=cumulative
        )

    def get_individual_metrics(self) -> Dict[str, Dict]:
        
        metrics = {}

        for asset in self.assets:
            asset_returns = self.returns[asset]
            cumulative = (1 + asset_returns).cumprod()

            total_return = (cumulative.iloc[-1] - 1) * 100
            years = len(asset_returns) / self.TRADING_DAYS
            annualized = ((1 + total_return / 100) ** (1 / years) - 1) * 100 if years > 0 else 0

            vol = asset_returns.std() * np.sqrt(self.TRADING_DAYS) * 100
            sharpe = (annualized / 100 - self.RISK_FREE_RATE) / (vol / 100) if vol > 0 else 0

            rolling_max = cumulative.expanding().max()
            drawdown = (cumulative - rolling_max) / rolling_max
            max_dd = abs(drawdown.min()) * 100

            metrics[asset] = {
                'total_return': round(total_return, 2),
                'annualized_return': round(annualized, 2),
                'volatility': round(vol, 2),
                'sharpe_ratio': round(sharpe, 2),
                'max_drawdown': round(max_dd, 2),
                'cumulative_returns': cumulative.tolist()
            }

        return metrics

    def compare_with_benchmark(
        self,
        portfolio_metrics: PortfolioMetrics,
        benchmark_returns: pd.Series
    ) -> Dict:
        
        portfolio_returns = portfolio_metrics.cumulative_returns.pct_change().dropna()
        benchmark_returns = benchmark_returns.reindex(portfolio_returns.index).dropna()

        tracking_error = (portfolio_returns - benchmark_returns).std() * np.sqrt(self.TRADING_DAYS)

        bench_cum = (1 + benchmark_returns).cumprod()
        bench_total_return = (bench_cum.iloc[-1] - 1) * 100

        alpha = portfolio_metrics.annualized_return - bench_total_return

        cov = portfolio_returns.cov(benchmark_returns)
        bench_var = benchmark_returns.var()
        beta = cov / bench_var if bench_var > 0 else 1

        return {
            'alpha': round(alpha, 2),
            'beta': round(beta, 2),
            'tracking_error': round(tracking_error * 100, 2),
            'information_ratio': round(alpha / (tracking_error * 100), 2) if tracking_error > 0 else 0
        }

def create_efficient_frontier(
    prices: pd.DataFrame,
    n_portfolios: int = 100
) -> List[Dict]:
    
    analyzer = PortfolioAnalyzer(prices)
    mean_returns = analyzer.returns.mean() * analyzer.TRADING_DAYS
    cov_matrix = analyzer.calculate_covariance_matrix()

    results = []

    for _ in range(n_portfolios):
        weights = np.random.random(analyzer.n_assets)
        weights = weights / weights.sum()

        port_return = np.dot(weights, mean_returns) * 100
        port_vol = np.sqrt(weights @ cov_matrix.values @ weights) * 100
        sharpe = (port_return / 100 - analyzer.RISK_FREE_RATE) / (port_vol / 100)

        results.append({
            'return': round(port_return, 2),
            'volatility': round(port_vol, 2),
            'sharpe': round(sharpe, 2),
            'weights': {asset: round(w, 4) for asset, w in zip(analyzer.assets, weights)}
        })

    return results
