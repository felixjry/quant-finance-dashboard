

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from scipy import stats
import logging

logger = logging.getLogger(__name__)

TRADING_DAYS = 252
RISK_FREE_RATE = 0.04

def calculate_returns(prices: pd.Series, log_returns: bool = False) -> pd.Series:
    
    if log_returns:
        return np.log(prices / prices.shift(1)).dropna()
    return prices.pct_change().dropna()

def calculate_volatility(
    returns: pd.Series,
    annualize: bool = True,
    window: Optional[int] = None
) -> float:
    
    if window:
        vol = returns.rolling(window=window).std().iloc[-1]
    else:
        vol = returns.std()

    if annualize:
        vol = vol * np.sqrt(TRADING_DAYS)

    return vol * 100

def calculate_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = RISK_FREE_RATE
) -> float:
    
    excess_returns = returns.mean() * TRADING_DAYS - risk_free_rate
    vol = returns.std() * np.sqrt(TRADING_DAYS)

    if vol == 0:
        return 0

    return excess_returns / vol

def calculate_sortino_ratio(
    returns: pd.Series,
    risk_free_rate: float = RISK_FREE_RATE
) -> float:
    
    excess_returns = returns.mean() * TRADING_DAYS - risk_free_rate
    downside_returns = returns[returns < 0]

    if len(downside_returns) == 0:
        return float('inf')

    downside_std = downside_returns.std() * np.sqrt(TRADING_DAYS)

    if downside_std == 0:
        return 0

    return excess_returns / downside_std

def calculate_max_drawdown(prices: pd.Series) -> Tuple[float, pd.Timestamp, pd.Timestamp]:
    
    rolling_max = prices.expanding().max()
    drawdown = (prices - rolling_max) / rolling_max

    max_dd = drawdown.min()
    trough_date = drawdown.idxmin()

    peak_date = prices[:trough_date].idxmax()

    return abs(max_dd) * 100, peak_date, trough_date

def calculate_calmar_ratio(
    returns: pd.Series,
    prices: pd.Series
) -> float:
    
    annualized_return = returns.mean() * TRADING_DAYS
    max_dd, _, _ = calculate_max_drawdown(prices)

    if max_dd == 0:
        return 0

    return (annualized_return * 100) / max_dd

def calculate_var(
    returns: pd.Series,
    confidence_level: float = 0.95,
    method: str = 'historical'
) -> float:
    
    if method == 'historical':
        var = np.percentile(returns, (1 - confidence_level) * 100)
    else:
        mean = returns.mean()
        std = returns.std()
        var = stats.norm.ppf(1 - confidence_level, mean, std)

    return abs(var) * 100

def calculate_cvar(
    returns: pd.Series,
    confidence_level: float = 0.95
) -> float:
    
    var_threshold = np.percentile(returns, (1 - confidence_level) * 100)
    cvar = returns[returns <= var_threshold].mean()

    return abs(cvar) * 100

def calculate_beta(
    asset_returns: pd.Series,
    market_returns: pd.Series
) -> float:
    
    aligned = pd.concat([asset_returns, market_returns], axis=1).dropna()

    if len(aligned) < 2:
        return 1.0

    covariance = aligned.iloc[:, 0].cov(aligned.iloc[:, 1])
    market_variance = aligned.iloc[:, 1].var()

    if market_variance == 0:
        return 1.0

    return covariance / market_variance

def calculate_alpha(
    asset_returns: pd.Series,
    market_returns: pd.Series,
    risk_free_rate: float = RISK_FREE_RATE
) -> float:
    
    beta = calculate_beta(asset_returns, market_returns)

    asset_ann_return = asset_returns.mean() * TRADING_DAYS
    market_ann_return = market_returns.mean() * TRADING_DAYS

    alpha = asset_ann_return - (risk_free_rate + beta * (market_ann_return - risk_free_rate))

    return alpha * 100

def calculate_information_ratio(
    asset_returns: pd.Series,
    benchmark_returns: pd.Series
) -> float:
    
    excess_returns = asset_returns - benchmark_returns
    tracking_error = excess_returns.std() * np.sqrt(TRADING_DAYS)

    if tracking_error == 0:
        return 0

    return (excess_returns.mean() * TRADING_DAYS) / tracking_error

def calculate_skewness(returns: pd.Series) -> float:
    
    return returns.skew()

def calculate_kurtosis(returns: pd.Series) -> float:
    
    return returns.kurtosis()

def calculate_all_metrics(
    prices: pd.Series,
    benchmark_prices: Optional[pd.Series] = None
) -> Dict:
    
    returns = calculate_returns(prices)

    total_return = ((prices.iloc[-1] / prices.iloc[0]) - 1) * 100
    years = len(returns) / TRADING_DAYS
    annualized_return = ((1 + total_return / 100) ** (1 / years) - 1) * 100 if years > 0 else 0

    max_dd, peak_date, trough_date = calculate_max_drawdown(prices)

    metrics = {
        'total_return': round(total_return, 2),
        'annualized_return': round(annualized_return, 2),
        'volatility': round(calculate_volatility(returns), 2),
        'sharpe_ratio': round(calculate_sharpe_ratio(returns), 2),
        'sortino_ratio': round(calculate_sortino_ratio(returns), 2),
        'max_drawdown': round(max_dd, 2),
        'calmar_ratio': round(calculate_calmar_ratio(returns, prices), 2),
        'var_95': round(calculate_var(returns, 0.95), 2),
        'cvar_95': round(calculate_cvar(returns, 0.95), 2),
        'skewness': round(calculate_skewness(returns), 2),
        'kurtosis': round(calculate_kurtosis(returns), 2),
        'positive_days': int((returns > 0).sum()),
        'negative_days': int((returns < 0).sum()),
        'best_day': round(returns.max() * 100, 2),
        'worst_day': round(returns.min() * 100, 2)
    }

    if benchmark_prices is not None:
        benchmark_returns = calculate_returns(benchmark_prices)
        metrics['beta'] = round(calculate_beta(returns, benchmark_returns), 2)
        metrics['alpha'] = round(calculate_alpha(returns, benchmark_returns), 2)
        metrics['information_ratio'] = round(calculate_information_ratio(returns, benchmark_returns), 2)

    return metrics
