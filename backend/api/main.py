"""
FastAPI Main Application
RESTful API for the Quantitative Financial Dashboard
Updated: Added chart_data with portfolio cumulative returns
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict
from datetime import datetime
import pandas as pd
import numpy as np
import logging

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.data_fetcher import data_fetcher
from services.strategies import TradingStrategies, StrategyType, calculate_metrics_from_prices
from services.portfolio import PortfolioAnalyzer, WeightingStrategy, RebalanceFrequency, create_efficient_frontier
from services.prediction import predict_price
from services.paper_trading import PaperTradingDB, OrderType, Portfolio as PaperPortfolio
from services.signals import SignalDetector
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Paper Trading DB
paper_db = PaperTradingDB()

app = FastAPI(
    title="Quant Dashboard API",
    description="API for quantitative financial analysis and portfolio management",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "Quant Dashboard API",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
async def health_check():
    """API health check."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/assets")
async def get_available_assets():
    """Get list of all available assets by category."""
    return data_fetcher.get_available_symbols()

@app.get("/api/quote/{symbol}")
async def get_quote(symbol: str):
    
    price_info = data_fetcher.get_current_price(symbol)

    if price_info is None:
        raise HTTPException(status_code=404, detail=f"Asset {symbol} not found")

    return price_info

@app.get("/api/asset/{symbol}/price")
async def get_current_price(symbol: str):
    
    price_info = data_fetcher.get_current_price(symbol)

    if price_info is None:
        raise HTTPException(status_code=404, detail=f"Asset {symbol} not found")

    return price_info

@app.get("/api/asset/{symbol}/history")
async def get_asset_history(
    symbol: str,
    period: str = Query(default="1y"),
    interval: str = Query(default="daily")
):

    data = data_fetcher.get_asset_data_with_dates(
        symbol,
        start='2024-06-11',
        end=datetime.now().strftime('%Y-%m-%d'),
        interval=interval
    )

    if data is None:
        raise HTTPException(status_code=404, detail=f"No data available for {symbol}")

    return {
        "symbol": symbol,
        "period": period,
        "interval": interval,
        "data": data.to_dict(orient="records"),
        "count": len(data)
    }

@app.get("/api/asset/{symbol}/metrics")
async def get_asset_metrics(
    symbol: str,
    period: str = Query(default="1y")
):

    data = data_fetcher.get_asset_data_with_dates(
        symbol,
        start='2024-06-11',
        end=datetime.now().strftime('%Y-%m-%d'),
        interval='daily'
    )

    if data is None:
        raise HTTPException(status_code=404, detail=f"No data available for {symbol}")

    metrics = calculate_metrics_from_prices(data['close'])

    return {
        "symbol": symbol,
        "period": period,
        "metrics": metrics
    }

@app.get("/api/asset/{symbol}/strategy")
@app.post("/api/asset/{symbol}/strategy")
async def run_strategy(
    symbol: str,
    strategy: str = Query(default="buy_and_hold"),
    period: str = Query(default="1y"),
    interval: str = Query(default="daily"),
    lookback_period: int = Query(default=20, ge=5, le=200),
    short_window: int = Query(default=20, ge=5, le=100),
    long_window: int = Query(default=50, ge=20, le=200)
):

    data = data_fetcher.get_asset_data_with_dates(
        symbol,
        start='2024-06-11',
        end=datetime.now().strftime('%Y-%m-%d'),
        interval=interval
    )

    if data is None:
        raise HTTPException(status_code=404, detail=f"No data available for {symbol}")

    try:
        strategy_type = StrategyType(strategy)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid strategy: {strategy}")

    strategies = TradingStrategies(data)

    params = {
        'lookback_period': lookback_period,
        'short_window': short_window,
        'long_window': long_window
    }

    result = strategies.run_strategy(strategy_type, **params)

    if result is None:
        raise HTTPException(status_code=500, detail="Strategy execution failed")

    cumulative_list = result.cumulative_returns.fillna(0).tolist()
    dates = data['date'].dt.strftime('%Y-%m-%d').tolist()
    prices = data['close'].fillna(0).tolist()

    return {
        "symbol": symbol,
        "strategy": result.strategy_name,
        "metrics": {
            "total_return": result.total_return if not pd.isna(result.total_return) else 0.0,
            "annualized_return": result.annualized_return if not pd.isna(result.annualized_return) else 0.0,
            "volatility": result.volatility if not pd.isna(result.volatility) else 0.0,
            "sharpe_ratio": result.sharpe_ratio if not pd.isna(result.sharpe_ratio) else 0.0,
            "max_drawdown": result.max_drawdown if not pd.isna(result.max_drawdown) else 0.0,
            "win_rate": result.win_rate if not pd.isna(result.win_rate) else 0.0,
            "num_trades": result.num_trades
        },
        "chart_data": [
            {"date": d, "price": p, "strategy": s}
            for d, p, s in zip(dates, prices, cumulative_list)
        ]
    }

@app.get("/api/asset/{symbol}/predict")
async def predict_asset_price_v2(
    symbol: str,
    period: str = Query(default="1y"),
    forecast_days: int = Query(default=30, ge=7, le=365)  # Max 365 days
):
    """Price prediction."""
    data = data_fetcher.get_asset_data_with_dates(
        symbol,
        start='2024-06-11',
        end=datetime.now().strftime('%Y-%m-%d'),
        interval='daily'
    )

    if data is None:
        raise HTTPException(status_code=404, detail=f"No data available for {symbol}")

    if len(data) < 30:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient data for prediction: {len(data)} rows (minimum 30)"
        )

    result = predict_price(data, forecast_days)

    if result is None:
        raise HTTPException(status_code=500, detail="Price prediction failed")

    return {
        "symbol": symbol,
        "prediction": result
    }

@app.post("/api/portfolio/analyze")
async def analyze_portfolio(
    symbols: List[str],
    weighting: str = Query(default="equal_weight"),
    rebalance: str = Query(default="monthly"),
    period: str = Query(default="1y"),
    custom_weights: Optional[Dict[str, float]] = None
):

    if len(symbols) < 2:
        raise HTTPException(status_code=400, detail="Portfolio must have at least 2 assets")

    prices = data_fetcher.get_aligned_prices(
        symbols,
        start='2024-06-11',
        end=datetime.now().strftime('%Y-%m-%d')
    )

    if prices is None or prices.empty:
        raise HTTPException(status_code=404, detail="Could not fetch data for portfolio assets")

    try:
        weight_strategy = WeightingStrategy(weighting)
        rebalance_freq = RebalanceFrequency(rebalance)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    analyzer = PortfolioAnalyzer(prices)
    result = analyzer.analyze_portfolio(weight_strategy, custom_weights, rebalance_freq)

    dates = prices.index.strftime('%Y-%m-%d').tolist()

    # Pre-calculate normalized prices and cumulative returns to avoid index misalignment
    normalized_prices = {}
    for asset in symbols:
        normalized_prices[asset] = (prices[asset] / prices[asset].iloc[0]).tolist()

    cumulative_returns_list = result.cumulative_returns.tolist()

    # Build chart_data with proper length checking
    chart_data = []
    min_length = min(len(dates), len(cumulative_returns_list))
    for i in range(min_length):
        point = {"date": dates[i]}
        for asset in symbols:
            if i < len(normalized_prices[asset]):
                point[asset] = round(normalized_prices[asset][i], 4)
        if i < len(cumulative_returns_list):
            point["portfolio"] = round(cumulative_returns_list[i], 4)
        chart_data.append(point)

    correlation_data = []
    corr_matrix = result.correlation_matrix
    for asset1 in symbols:
        for asset2 in symbols:
            correlation_data.append({
                "asset1": asset1,
                "asset2": asset2,
                "correlation": round(corr_matrix.loc[asset1, asset2], 3)
            })

    return {
        "symbols": symbols,
        "weighting_strategy": weighting,
        "rebalance_frequency": rebalance,
        "metrics": {
            "total_return": result.total_return,
            "annualized_return": result.annualized_return,
            "volatility": result.volatility,
            "sharpe_ratio": result.sharpe_ratio,
            "max_drawdown": result.max_drawdown,
            "diversification_ratio": result.diversification_ratio
        },
        "weights": result.weights,
        "correlation_matrix": correlation_data,
        "chart_data": chart_data,
        "individual_metrics": analyzer.get_individual_metrics()
    }

@app.get("/api/portfolio/efficient-frontier")
async def get_efficient_frontier(
    symbols: List[str] = Query(...),
    period: str = Query(default="1y"),
    n_portfolios: int = Query(default=100, ge=50, le=500)
):

    if len(symbols) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 assets")

    prices = data_fetcher.get_aligned_prices(
        symbols,
        start='2024-06-11',
        end=datetime.now().strftime('%Y-%m-%d')
    )

    if prices is None:
        raise HTTPException(status_code=404, detail="Could not fetch price data")

    frontier = create_efficient_frontier(prices, n_portfolios)

    return {
        "symbols": symbols,
        "frontier": frontier
    }

@app.get("/api/calculate/portfolio-metrics")
async def get_portfolio_metrics(
    symbols: str = Query(...),
    days: int = Query(default=365),
    weighting: str = Query(default="equal_weight"),
    rebalance: str = Query(default="monthly")
):
    """Portfolio metrics."""
    symbol_list = symbols.split(',')

    if len(symbol_list) < 2:
        raise HTTPException(status_code=400, detail="Portfolio must have at least 2 assets")

    prices = data_fetcher.get_aligned_prices(symbol_list, start='2024-06-11', end=datetime.now().strftime('%Y-%m-%d'))

    if prices is None or prices.empty:
        raise HTTPException(status_code=404, detail="Could not fetch data for portfolio assets")

    try:
        weight_strategy = WeightingStrategy(weighting)
        rebalance_freq = RebalanceFrequency(rebalance)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    analyzer = PortfolioAnalyzer(prices)
    individual_metrics = analyzer.get_individual_metrics()

    result = analyzer.analyze_portfolio(
        weighting_strategy=weight_strategy,
        rebalance_freq=rebalance_freq
    )

    total_return = result.total_return
    annualized_return = result.annualized_return
    portfolio_volatility = result.volatility / 100
    sharpe_ratio = result.sharpe_ratio
    max_drawdown = result.max_drawdown
    diversification_ratio = result.diversification_ratio
    weights = result.weights

    corr_matrix = result.correlation_matrix
    correlation_dict = {}
    for asset1 in symbol_list:
        correlation_dict[asset1] = {}
        for asset2 in symbol_list:
            correlation_dict[asset1][asset2] = float(corr_matrix.loc[asset1, asset2]) if asset1 in corr_matrix.index and asset2 in corr_matrix.columns else (1.0 if asset1 == asset2 else 0.0)

    histories = {}
    for symbol in symbol_list:
        if symbol in prices.columns:
            histories[symbol] = [
                {
                    "date": date.strftime('%Y-%m-%d'),
                    "close": float(prices.loc[date, symbol])
                }
                for date in prices.index
            ]

    chart_data = []
    cumulative_aligned = result.cumulative_returns.reindex(prices.index, method='ffill').fillna(1.0)

    for i, date in enumerate(prices.index):
        point = {"date": date.strftime('%Y-%m-%d')}

        for symbol in symbol_list:
            if symbol in prices.columns:
                normalized = float(prices[symbol].iloc[i] / prices[symbol].iloc[0])
                point[symbol] = round(normalized, 4)

        point["portfolio"] = round(float(cumulative_aligned.iloc[i]), 4)
        chart_data.append(point)

    return {
        "correlation_matrix": correlation_dict,
        "portfolio_volatility": portfolio_volatility,
        "diversification_ratio": diversification_ratio,
        "individual_metrics": individual_metrics,
        "weights": weights,
        "portfolio_metrics": {
            "total_return": total_return,
            "annualized_return": annualized_return,
            "volatility": portfolio_volatility * 100,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown
        },
        "histories": histories,
        "chart_data": chart_data
    }

@app.get("/api/histories")
async def get_histories(
    symbols: str = Query(...),
    days: int = Query(default=365)
):
    """Historical prices."""
    symbol_list = symbols.split(',')

    prices = data_fetcher.get_aligned_prices(
        symbol_list,
        start='2024-06-11',
        end=datetime.now().strftime('%Y-%m-%d')
    )

    if prices is None or prices.empty:
        raise HTTPException(status_code=404, detail="Could not fetch historical data")

    result = {}
    for symbol in symbol_list:
        if symbol in prices.columns:
            result[symbol] = [
                {
                    "date": date.strftime('%Y-%m-%d'),
                    "close": float(prices.loc[date, symbol])
                }
                for date in prices.index
            ]

    return result

@app.get("/api/market/overview")
async def get_market_overview():
    """Market overview."""
    indices = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'BTC-USD', 'ETH-USD']

    overview = []
    for symbol in indices:
        price_info = data_fetcher.get_current_price(symbol)
        if price_info:
            overview.append(price_info)

    return {
        "timestamp": datetime.now().isoformat(),
        "assets": overview
    }

@app.get("/api/quotes")
async def get_bulk_quotes():
    """Bulk quotes."""
    symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'BTC-USD', 'ETH-USD']
    quotes = data_fetcher.get_bulk_quotes(symbols)
    return quotes

# ============================================
# PAPER TRADING ENDPOINTS
# ============================================

@app.post("/api/paper-trading/user/create")
async def create_paper_trading_user(
    user_id: str = Query(...),
    initial_balance: float = Query(default=1000000.0)
):
    """Create a new paper trading user"""
    success = paper_db.create_user(user_id, initial_balance)

    if success:
        return {
            "success": True,
            "user_id": user_id,
            "initial_balance": initial_balance,
            "message": f"User created with ${initial_balance:,.2f}"
        }
    else:
        return {
            "success": False,
            "message": "User already exists"
        }

@app.get("/api/paper-trading/user/{user_id}")
async def get_paper_trading_user(user_id: str):
    """Get user information"""
    user = paper_db.get_user(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@app.post("/api/paper-trading/trade")
async def execute_paper_trade(
    user_id: str = Query(...),
    symbol: str = Query(...),
    order_type: str = Query(...),
    quantity: float = Query(..., gt=0)
):
    """Execute a paper trading buy or sell order"""
    # Get current price
    price_info = data_fetcher.get_current_price(symbol)
    if not price_info:
        raise HTTPException(status_code=404, detail=f"Could not fetch price for {symbol}")

    price = price_info['price']

    # Validate order type
    try:
        order_type_enum = OrderType(order_type.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid order type. Must be 'buy' or 'sell'")

    # Execute trade
    success, message, trade_id = paper_db.execute_trade(
        user_id=user_id,
        symbol=symbol,
        order_type=order_type_enum,
        quantity=quantity,
        price=price
    )

    if success:
        return {
            "success": True,
            "trade_id": trade_id,
            "symbol": symbol,
            "order_type": order_type,
            "quantity": quantity,
            "price": price,
            "total_amount": quantity * price,
            "message": message
        }
    else:
        raise HTTPException(status_code=400, detail=message)

@app.get("/api/paper-trading/portfolio/{user_id}")
async def get_paper_portfolio(user_id: str):
    """Get complete paper trading portfolio"""
    if not paper_db.get_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")

    positions_raw = paper_db.get_positions(user_id, {})
    current_prices = {p.symbol: data_fetcher.get_current_price(p.symbol)['price']
                      for p in positions_raw if data_fetcher.get_current_price(p.symbol)}

    portfolio = paper_db.get_portfolio(user_id, current_prices)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    return {
        "user_id": portfolio.user_id,
        "cash_balance": portfolio.cash_balance,
        "total_invested": portfolio.total_invested,
        "total_value": portfolio.total_value,
        "total_pnl": portfolio.total_pnl,
        "total_pnl_pct": portfolio.total_pnl_pct,
        "trades_count": portfolio.trades_count,
        "positions": [{"symbol": p.symbol, "quantity": p.quantity, "avg_entry_price": p.avg_entry_price,
                       "current_price": p.current_price, "total_value": p.total_value,
                       "unrealized_pnl": p.unrealized_pnl, "unrealized_pnl_pct": p.unrealized_pnl_pct}
                      for p in portfolio.positions]
    }

@app.get("/api/paper-trading/trades/{user_id}")
async def get_paper_trades_history(user_id: str, limit: int = Query(default=50, ge=1, le=100), symbol: Optional[str] = None):
    """Get trade history"""
    trades = paper_db.get_trades_history(user_id, limit, symbol)
    return {
        "user_id": user_id,
        "trades_count": len(trades),
        "trades": [{"id": t.id, "symbol": t.symbol, "order_type": t.order_type, "quantity": t.quantity,
                    "price": t.price, "total_amount": t.total_amount, "timestamp": t.timestamp, "status": t.status}
                   for t in trades]
    }

@app.get("/api/signals/active")
async def get_active_signals(symbol: Optional[str] = None, limit: int = Query(default=20, ge=1, le=50)):
    """Get recent active trading signals"""
    signals = paper_db.get_active_signals(symbol, limit)
    return {"signals_count": len(signals), "signals": signals}

@app.get("/api/signals/{symbol}")
async def get_trading_signals(symbol: str):
    """Detect trading signals for a symbol"""
    data = data_fetcher.get_asset_data_with_dates(symbol, start='2024-06-11', end=datetime.now().strftime('%Y-%m-%d'), interval='daily')
    if data is None or len(data) < 50:
        raise HTTPException(status_code=404, detail=f"Insufficient data for {symbol}")

    signals = SignalDetector(data).detect_all_signals(symbol=symbol)
    for signal in signals:
        paper_db.record_signal(signal.symbol, signal.signal_type.value, signal.strategy, signal.price, json.dumps(signal.indicators))

    return {
        "symbol": symbol,
        "signals_count": len(signals),
        "signals": [{"signal_type": s.signal_type.value, "strength": s.strength.value, "strategy": s.strategy,
                     "price": s.price, "timestamp": s.timestamp, "indicators": s.indicators, "message": s.message}
                    for s in signals]
    }

@app.delete("/api/cache/clear")
async def clear_cache():
    """Clear the data cache."""
    data_fetcher.clear_cache()
    return {"status": "Cache cleared", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
