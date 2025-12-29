

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from scipy.optimize import minimize

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
    sortino_ratio: float
    max_drawdown: float
    var_95: float
    cvar_95: float
    diversification_ratio: float
    weights: Dict[str, float]
    correlation_matrix: pd.DataFrame
    cumulative_returns: pd.Series

class PortfolioAnalyzer:
    

    RISK_FREE_RATE = 0.04
    TRADING_DAYS = 252
    DEFAULT_TRANSACTION_COST = 0.001  # 0.1% per trade

    def __init__(self, prices: pd.DataFrame, transaction_cost: float = None):

        self.prices = prices.copy()
        self.returns = self.prices.pct_change().dropna()
        self.assets = list(self.prices.columns)
        self.n_assets = len(self.assets)
        self.transaction_cost = transaction_cost if transaction_cost is not None else self.DEFAULT_TRANSACTION_COST

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

    def get_min_variance_weights(self, min_weight: float = 0.0, max_weight: float = 1.0) -> Dict[str, float]:
        """
        Calculate minimum variance weights using scipy optimization
        More robust than matrix inversion, especially for ill-conditioned matrices
        """
        cov_matrix = self.calculate_covariance_matrix()

        # Objective: minimize portfolio variance
        def portfolio_variance(weights):
            return weights @ cov_matrix.values @ weights

        # Constraints: weights sum to 1
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}

        # Bounds: individual weights between min_weight and max_weight
        bounds = tuple((min_weight, max_weight) for _ in range(self.n_assets))

        # Initial guess: equal weights
        init_weights = np.array([1 / self.n_assets] * self.n_assets)

        # Optimize
        result = minimize(
            portfolio_variance,
            init_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'ftol': 1e-9, 'maxiter': 1000}
        )

        if result.success:
            weights = result.x
            weights = np.maximum(weights, 0)
            weights = weights / weights.sum()
        else:
            logger.warning("Min variance optimization failed, using equal weights")
            weights = init_weights

        return {asset: round(w, 4) for asset, w in zip(self.assets, weights)}

    def get_max_sharpe_weights(self, min_weight: float = 0.0, max_weight: float = 1.0) -> Dict[str, float]:
        """
        Calculate maximum Sharpe ratio weights using scipy optimization
        with optional weight constraints
        """
        mean_returns = self.returns.mean() * self.TRADING_DAYS
        cov_matrix = self.calculate_covariance_matrix()

        # Objective: minimize negative Sharpe ratio
        def neg_sharpe(weights):
            port_return = np.dot(weights, mean_returns)
            port_vol = np.sqrt(weights @ cov_matrix.values @ weights)
            sharpe = (port_return - self.RISK_FREE_RATE) / port_vol
            return -sharpe

        # Constraints: weights sum to 1
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}

        # Bounds: individual weights between min_weight and max_weight
        bounds = tuple((min_weight, max_weight) for _ in range(self.n_assets))

        # Initial guess: equal weights
        init_weights = np.array([1 / self.n_assets] * self.n_assets)

        # Optimize
        result = minimize(
            neg_sharpe,
            init_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'ftol': 1e-9, 'maxiter': 1000}
        )

        if result.success:
            weights = result.x
            # Ensure weights are non-negative and sum to 1
            weights = np.maximum(weights, 0)
            weights = weights / weights.sum()
        else:
            logger.warning("Optimization failed, using equal weights")
            weights = init_weights

        return {asset: round(w, 4) for asset, w in zip(self.assets, weights)}

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
        rebalance_freq: RebalanceFrequency = RebalanceFrequency.MONTHLY,
        apply_costs: bool = True
    ) -> pd.Series:
        """
        Calculate portfolio returns with optional transaction costs
        Costs are applied when portfolio is rebalanced
        """
        weight_array = np.array([weights[asset] for asset in self.assets])

        if rebalance_freq == RebalanceFrequency.DAILY:
            portfolio_returns = (self.returns * weight_array).sum(axis=1)
            # Daily rebalancing would be very expensive
            if apply_costs:
                logger.warning("Daily rebalancing with transaction costs is not recommended")

        else:
            freq_map = {
                RebalanceFrequency.WEEKLY: 'W',
                RebalanceFrequency.MONTHLY: 'ME',
                RebalanceFrequency.QUARTERLY: 'QE'
            }

            portfolio_returns = pd.Series(index=self.returns.index, dtype=float)
            current_weights = weight_array.copy()

            rebalance_dates = self.returns.resample(freq_map[rebalance_freq]).last().index

            for i, (date, row) in enumerate(self.returns.iterrows()):
                port_ret = (row * current_weights).sum()

                # Apply transaction costs on rebalance dates
                if date in rebalance_dates and apply_costs and i > 0:
                    # Calculate turnover (sum of absolute weight changes)
                    weight_diff = np.abs(weight_array - current_weights)
                    turnover = weight_diff.sum()

                    # Apply transaction costs as a drag on returns
                    transaction_cost = turnover * self.transaction_cost
                    port_ret -= transaction_cost

                portfolio_returns[date] = port_ret

                # Update weights based on returns (drift)
                current_weights = current_weights * (1 + row.values)
                current_weights = current_weights / current_weights.sum()

                # Rebalance to target weights
                if date in rebalance_dates:
                    current_weights = weight_array.copy()

        return portfolio_returns

    def calculate_turnover(
        self,
        weights: Dict[str, float],
        rebalance_freq: RebalanceFrequency = RebalanceFrequency.MONTHLY
    ) -> float:
        """Calculate average portfolio turnover per rebalance period"""
        weight_array = np.array([weights[asset] for asset in self.assets])

        freq_map = {
            RebalanceFrequency.WEEKLY: 'W',
            RebalanceFrequency.MONTHLY: 'ME',
            RebalanceFrequency.QUARTERLY: 'QE',
            RebalanceFrequency.DAILY: 'D'
        }

        rebalance_dates = self.returns.resample(freq_map[rebalance_freq]).last().index
        turnovers = []
        current_weights = weight_array.copy()

        for date, row in self.returns.iterrows():
            # Update weights based on returns (drift)
            current_weights = current_weights * (1 + row.values)
            current_weights = current_weights / current_weights.sum()

            # Calculate turnover on rebalance dates
            if date in rebalance_dates:
                weight_diff = np.abs(weight_array - current_weights)
                turnover = weight_diff.sum()
                turnovers.append(turnover)
                current_weights = weight_array.copy()

        return np.mean(turnovers) if turnovers else 0.0

    def analyze_portfolio(
        self,
        weighting_strategy: WeightingStrategy = WeightingStrategy.EQUAL_WEIGHT,
        custom_weights: Optional[Dict[str, float]] = None,
        rebalance_freq: RebalanceFrequency = RebalanceFrequency.MONTHLY,
        apply_transaction_costs: bool = True
    ) -> PortfolioMetrics:

        weights = self.get_weights(weighting_strategy, custom_weights)
        portfolio_returns = self.calculate_portfolio_returns(weights, rebalance_freq, apply_transaction_costs)

        cumulative = (1 + portfolio_returns).cumprod()
        total_return = (cumulative.iloc[-1] - 1) * 100

        years = len(portfolio_returns) / self.TRADING_DAYS
        annualized_return = ((1 + total_return / 100) ** (1 / years) - 1) * 100 if years > 0 else 0

        volatility = portfolio_returns.std() * np.sqrt(self.TRADING_DAYS) * 100

        excess_return = annualized_return / 100 - self.RISK_FREE_RATE
        sharpe_ratio = excess_return / (volatility / 100) if volatility > 0 else 0

        # Calculate Sortino Ratio (downside risk only)
        downside_returns = portfolio_returns[portfolio_returns < 0]
        downside_std = downside_returns.std() * np.sqrt(self.TRADING_DAYS)
        sortino_ratio = excess_return / downside_std if downside_std > 0 else 0

        # Calculate Value at Risk (VaR) and Conditional VaR (CVaR) at 95% confidence
        var_95 = np.percentile(portfolio_returns, 5) * 100
        cvar_95 = portfolio_returns[portfolio_returns <= np.percentile(portfolio_returns, 5)].mean() * 100

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
            sortino_ratio=round(sortino_ratio, 2),
            max_drawdown=round(max_drawdown, 2),
            var_95=round(var_95, 2),
            cvar_95=round(cvar_95, 2),
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

    def calculate_beta_alpha(
        self,
        portfolio_returns: pd.Series,
        benchmark_returns: pd.Series
    ) -> Tuple[float, float]:
        """Calculate portfolio beta and alpha vs benchmark using CAPM"""
        # Align indices
        aligned_port = portfolio_returns.reindex(benchmark_returns.index).dropna()
        aligned_bench = benchmark_returns.reindex(aligned_port.index)

        # Calculate beta (covariance / variance)
        cov = aligned_port.cov(aligned_bench)
        bench_var = aligned_bench.var()
        beta = cov / bench_var if bench_var > 0 else 1.0

        # Calculate alpha (excess return beyond what CAPM predicts)
        port_return = aligned_port.mean() * self.TRADING_DAYS
        bench_return = aligned_bench.mean() * self.TRADING_DAYS
        alpha = port_return - (self.RISK_FREE_RATE + beta * (bench_return - self.RISK_FREE_RATE))

        return beta, alpha

    def compare_with_benchmark(
        self,
        portfolio_metrics: PortfolioMetrics,
        benchmark_returns: pd.Series
    ) -> Dict:

        portfolio_returns = portfolio_metrics.cumulative_returns.pct_change().dropna()
        benchmark_returns = benchmark_returns.reindex(portfolio_returns.index).dropna()

        # Calculate beta and alpha
        beta, alpha = self.calculate_beta_alpha(portfolio_returns, benchmark_returns)

        # Tracking error (standard deviation of excess returns)
        excess_returns = portfolio_returns - benchmark_returns
        tracking_error = excess_returns.std() * np.sqrt(self.TRADING_DAYS)

        # Benchmark metrics
        bench_cum = (1 + benchmark_returns).cumprod()
        bench_total_return = (bench_cum.iloc[-1] - 1) * 100
        years = len(benchmark_returns) / self.TRADING_DAYS
        bench_annualized = ((1 + bench_total_return / 100) ** (1 / years) - 1) * 100 if years > 0 else 0

        # Information Ratio (excess return / tracking error)
        information_ratio = (portfolio_metrics.annualized_return - bench_annualized) / (tracking_error * 100) if tracking_error > 0 else 0

        return {
            'alpha': round(alpha * 100, 2),
            'beta': round(beta, 2),
            'tracking_error': round(tracking_error * 100, 2),
            'information_ratio': round(information_ratio, 2),
            'benchmark_return': round(bench_annualized, 2)
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
