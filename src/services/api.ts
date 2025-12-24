/**
 * API Service Module
 * Handles communication with the Python FastAPI backend
 */

const API_BASE_URL = '/api';

interface PriceInfo {
  symbol: string;
  price: number;
  change: number;
  change_percent: number;
  currency: string;
  name: string;
  timestamp: string;
}

interface AssetHistory {
  symbol: string;
  period: string;
  interval: string;
  data: Array<{
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }>;
  count: number;
}

interface StrategyResult {
  symbol: string;
  strategy: string;
  metrics: {
    total_return: number;
    annualized_return: number;
    volatility: number;
    sharpe_ratio: number;
    max_drawdown: number;
    win_rate: number;
    num_trades: number;
  };
  chart_data: Array<{
    date: string;
    price: number;
    strategy: number;
  }>;
}

interface PortfolioResult {
  symbols: string[];
  weighting_strategy: string;
  rebalance_frequency: string;
  metrics: {
    total_return: number;
    annualized_return: number;
    volatility: number;
    sharpe_ratio: number;
    max_drawdown: number;
    diversification_ratio: number;
  };
  weights: Record<string, number>;
  correlation_matrix: Array<{
    asset1: string;
    asset2: string;
    correlation: number;
  }>;
  chart_data: Array<Record<string, string | number>>;
  individual_metrics: Record<string, {
    total_return: number;
    annualized_return: number;
    volatility: number;
    sharpe_ratio: number;
    max_drawdown: number;
    cumulative_returns: number[];
  }>;
}

interface PredictionResult {
  symbol: string;
  prediction: {
    forecast: Array<{
      date: string;
      predicted: number;
      lower_bound: number;
      upper_bound: number;
    }>;
    metrics: {
      mae: number;
      mape: number;
      rmse: number;
      mse: number;
      r2_score: number;
    };
    forecast_days: number;
    model: string;
    last_historical_date: string;
    last_price: number;
  };
}

interface ApiError {
  detail: string;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error: ApiError = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error ${response.status}`);
  }
  return response.json();
}

export const api = {
  /**
   * Get available assets by category
   */
  async getAvailableAssets(): Promise<Record<string, string[]>> {
    const response = await fetch(`${API_BASE_URL}/assets`);
    return handleResponse(response);
  },

  /**
   * Get current price for an asset
   */
  async getCurrentPrice(symbol: string): Promise<PriceInfo> {
    const response = await fetch(`${API_BASE_URL}/quote/${symbol}`);
    const data = await handleResponse<{
      symbol: string;
      price: number;
      change: number;
      change_percent: number;
    }>(response);

    return {
      symbol: data.symbol,
      price: data.price,
      change: data.change,
      change_percent: data.change_percent,
      currency: 'USD',
      name: data.symbol,
      timestamp: new Date().toISOString(),
    };
  },

  /**
   * Get historical data for an asset
   */
  async getAssetHistory(
    symbol: string,
    period: string = '1y',
    interval: string = 'daily'
  ): Promise<AssetHistory> {
    const response = await fetch(`${API_BASE_URL}/asset/${symbol}/history?period=${period}&interval=${interval}`);
    return handleResponse<AssetHistory>(response);
  },

  /**
   * Get performance metrics for an asset
   */
  async getAssetMetrics(symbol: string, period: string = '1y'): Promise<{
    symbol: string;
    period: string;
    metrics: {
      total_return: number;
      annualized_return: number;
      volatility: number;
      sharpe_ratio: number;
      max_drawdown: number;
    };
  }> {
    const days = period === '1y' ? 365 : period === '6mo' ? 180 : 730;
    const response = await fetch(`${API_BASE_URL}/calculate/metrics/${symbol}?days=${days}`);
    const data = await handleResponse<{
      sharpe_ratio: number;
      volatility: number;
      max_drawdown: number;
      total_return: number;
    }>(response);

    return {
      symbol,
      period,
      metrics: {
        total_return: data.total_return * 100,
        annualized_return: data.total_return * 100,
        volatility: data.volatility * 100,
        sharpe_ratio: data.sharpe_ratio,
        max_drawdown: data.max_drawdown * 100,
      },
    };
  },

  /**
   * Run a backtesting strategy
   */
  async runStrategy(
    symbol: string,
    strategy: string,
    period: string = '1y',
    options: {
      interval?: string;
      lookback_period?: number;
      short_window?: number;
      long_window?: number;
    } = {}
  ): Promise<StrategyResult> {
    const params: Record<string, string> = {
      strategy: strategy,
      period: period,
    };

    if (options.interval) {
      params.interval = options.interval;
    }
    if (options.lookback_period) {
      params.lookback_period = String(options.lookback_period);
    }
    if (options.short_window) {
      params.short_window = String(options.short_window);
    }
    if (options.long_window) {
      params.long_window = String(options.long_window);
    }

    const queryString = new URLSearchParams(params).toString();
    const response = await fetch(`${API_BASE_URL}/asset/${symbol}/strategy?${queryString}`);

    const data = await handleResponse<{
      symbol: string;
      strategy: string;
      metrics: {
        total_return: number;
        annualized_return: number;
        volatility: number;
        sharpe_ratio: number;
        max_drawdown: number;
        win_rate: number;
        num_trades: number;
      };
      chart_data: Array<{ date: string; price: number; strategy: number }>;
    }>(response);

    return {
      symbol: data.symbol,
      strategy: data.strategy,
      metrics: {
        total_return: data.metrics.total_return,
        annualized_return: data.metrics.annualized_return,
        volatility: data.metrics.volatility,
        sharpe_ratio: data.metrics.sharpe_ratio,
        max_drawdown: Math.abs(data.metrics.max_drawdown),
        win_rate: data.metrics.win_rate,
        num_trades: data.metrics.num_trades,
      },
      chart_data: data.chart_data,
    };
  },

  /**
   * Analyze a portfolio
   */
  async analyzePortfolio(
    symbols: string[],
    weighting: string = 'equal_weight',
    rebalance: string = 'monthly',
    period: string = '1y',
    customWeights?: Record<string, number>
  ): Promise<PortfolioResult> {
    const startDate = new Date('2024-06-11');
    const today = new Date();
    const daysSinceStart = Math.floor((today.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));
    const symbolsParam = symbols.join(',');

    const response = await fetch(
      `${API_BASE_URL}/calculate/portfolio-metrics?symbols=${symbolsParam}&days=${daysSinceStart}&weighting=${weighting}&rebalance=${rebalance}`
    );

    const data = await handleResponse<{
      correlation_matrix: Record<string, Record<string, number>>;
      portfolio_volatility: number;
      diversification_ratio: number;
      individual_metrics: Record<string, {
        total_return: number;
        annualized_return: number;
        volatility: number;
        sharpe_ratio: number;
        max_drawdown: number;
      }>;
      portfolio_metrics: {
        total_return: number;
        annualized_return: number;
        volatility: number;
        sharpe_ratio: number;
        max_drawdown: number;
      };
      weights: Record<string, number>;
      histories: Record<string, Array<{ date: string; close: number }>>;
    }>(response);

    const correlationArray: Array<{ asset1: string; asset2: string; correlation: number }> = [];
    for (const asset1 of symbols) {
      for (const asset2 of symbols) {
        correlationArray.push({
          asset1,
          asset2,
          correlation: data.correlation_matrix[asset1]?.[asset2] || (asset1 === asset2 ? 1 : 0),
        });
      }
    }

    // Use optimized weights from backend instead of equal weights
    const weights: Record<string, number> = data.weights || {};

    const individualMetrics: Record<string, {
      total_return: number;
      annualized_return: number;
      volatility: number;
      sharpe_ratio: number;
      max_drawdown: number;
      cumulative_returns: number[];
    }> = {};

    for (const symbol of symbols) {
      const metrics = data.individual_metrics[symbol];
      if (metrics) {
        individualMetrics[symbol] = {
          total_return: metrics.total_return,
          annualized_return: metrics.annualized_return,
          volatility: metrics.volatility,
          sharpe_ratio: metrics.sharpe_ratio,
          max_drawdown: metrics.max_drawdown,
          cumulative_returns: [],
        };
      }
    }

    // Use chart_data from backend if available (includes portfolio values with rebalancing)
    const chartData = (data as any).chart_data || (() => {
      // Fallback: calculate from histories (without rebalancing - less accurate)
      const firstSymbol = symbols[0];
      const dates = data.histories[firstSymbol]?.map(d => d.date) || [];
      return dates.map((date, i) => {
        const point: Record<string, string | number> = { date };
        let portfolioValue = 0;

        for (const symbol of symbols) {
          const history = data.histories[symbol];
          if (history && history[0] && history[i]) {
            const normalizedValue = history[i].close / history[0].close;
            point[symbol] = normalizedValue;
            portfolioValue += normalizedValue * weights[symbol];
          }
        }
        point.portfolio = portfolioValue;
        return point;
      });
    })();

    return {
      symbols,
      weighting_strategy: weighting,
      rebalance_frequency: rebalance,
      metrics: {
        total_return: data.portfolio_metrics.total_return,
        annualized_return: data.portfolio_metrics.annualized_return,
        volatility: data.portfolio_metrics.volatility,
        sharpe_ratio: data.portfolio_metrics.sharpe_ratio,
        max_drawdown: data.portfolio_metrics.max_drawdown,
        diversification_ratio: data.diversification_ratio,
      },
      weights,
      correlation_matrix: correlationArray,
      chart_data: chartData,
      individual_metrics: individualMetrics,
    };
  },

  /**
   * Get efficient frontier data
   */
  async getEfficientFrontier(
    symbols: string[],
    period: string = '1y',
    nPortfolios: number = 100
  ): Promise<{
    symbols: string[];
    frontier: Array<{
      return: number;
      volatility: number;
      sharpe: number;
      weights: Record<string, number>;
    }>;
  }> {
    return {
      symbols,
      frontier: [],
    };
  },

  /**
   * Get market overview
   */
  async getMarketOverview(): Promise<{
    timestamp: string;
    assets: PriceInfo[];
  }> {
    const response = await fetch(`${API_BASE_URL}/quotes`);
    const data = await handleResponse<Array<{
      symbol: string;
      price: number;
      change: number;
      changePercent: number;
    }>>(response);

    return {
      timestamp: new Date().toISOString(),
      assets: data.map(d => ({
        symbol: d.symbol,
        price: d.price,
        change: d.change,
        change_percent: d.changePercent,
        currency: 'USD',
        name: d.symbol,
        timestamp: new Date().toISOString(),
      })),
    };
  },

  /**
   * Predict future prices using Prophet
   */
  async predictPrice(
    symbol: string,
    period: string = '1y',
    forecast_days: number = 30
  ): Promise<PredictionResult> {
    const params = new URLSearchParams({
      period,
      forecast_days: forecast_days.toString()
    });
    const response = await fetch(`${API_BASE_URL}/asset/${symbol}/predict?${params}`);
    return handleResponse<PredictionResult>(response);
  },

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await fetch(`${API_BASE_URL}/`);
    return handleResponse(response);
  },

  // ============================================
  // PAPER TRADING API METHODS
  // ============================================

  /**
   * Create a new paper trading user
   */
  async createPaperTradingUser(
    userId: string,
    initialBalance: number = 1000000
  ): Promise<{ success: boolean; user_id: string; initial_balance: number; message: string }> {
    const params = new URLSearchParams({
      user_id: userId,
      initial_balance: initialBalance.toString()
    });
    const response = await fetch(`${API_BASE_URL}/paper-trading/user/create?${params}`, {
      method: 'POST'
    });
    return handleResponse(response);
  },

  /**
   * Get paper trading user info
   */
  async getPaperTradingUser(userId: string): Promise<PaperTradingUser> {
    const response = await fetch(`${API_BASE_URL}/paper-trading/user/${userId}`);
    return handleResponse(response);
  },

  /**
   * Execute a paper trade
   */
  async executePaperTrade(
    userId: string,
    symbol: string,
    orderType: 'buy' | 'sell',
    quantity: number
  ): Promise<PaperTradeResult> {
    const params = new URLSearchParams({
      user_id: userId,
      symbol: symbol,
      order_type: orderType,
      quantity: quantity.toString()
    });
    const response = await fetch(`${API_BASE_URL}/paper-trading/trade?${params}`, {
      method: 'POST'
    });
    return handleResponse(response);
  },

  /**
   * Get paper trading portfolio
   */
  async getPaperPortfolio(userId: string): Promise<PaperPortfolio> {
    const response = await fetch(`${API_BASE_URL}/paper-trading/portfolio/${userId}`);
    return handleResponse(response);
  },

  /**
   * Get trade history
   */
  async getPaperTrades(
    userId: string,
    limit: number = 50,
    symbol?: string
  ): Promise<{ user_id: string; trades_count: number; trades: PaperTrade[] }> {
    const params = new URLSearchParams({
      limit: limit.toString()
    });
    if (symbol) {
      params.append('symbol', symbol);
    }
    const response = await fetch(`${API_BASE_URL}/paper-trading/trades/${userId}?${params}`);
    return handleResponse(response);
  },

  /**
   * Get trading signals for a symbol
   */
  async getTradingSignals(symbol: string): Promise<SignalsResult> {
    const response = await fetch(`${API_BASE_URL}/signals/${symbol}`);
    return handleResponse(response);
  },

  /**
   * Get active signals
   */
  async getActiveSignals(
    symbol?: string,
    limit: number = 20
  ): Promise<{ signals_count: number; signals: TradingSignal[] }> {
    const params = new URLSearchParams({
      limit: limit.toString()
    });
    if (symbol) {
      params.append('symbol', symbol);
    }
    const response = await fetch(`${API_BASE_URL}/signals/active?${params}`);
    return handleResponse(response);
  },
};

// Paper Trading Types
interface PaperTradingUser {
  user_id: string;
  initial_balance: number;
  current_balance: number;
  created_at: string;
  updated_at: string;
}

interface PaperPosition {
  symbol: string;
  quantity: number;
  avg_entry_price: number;
  current_price: number;
  total_value: number;
  unrealized_pnl: number;
  unrealized_pnl_pct: number;
}

interface PaperPortfolio {
  user_id: string;
  cash_balance: number;
  total_invested: number;
  total_value: number;
  total_pnl: number;
  total_pnl_pct: number;
  trades_count: number;
  positions: PaperPosition[];
}

interface PaperTrade {
  id: number;
  symbol: string;
  order_type: string;
  quantity: number;
  price: number;
  total_amount: number;
  timestamp: string;
  status: string;
}

interface PaperTradeResult {
  success: boolean;
  trade_id: number;
  symbol: string;
  order_type: string;
  quantity: number;
  price: number;
  total_amount: number;
  message: string;
}

interface TradingSignal {
  id?: number;
  symbol: string;
  signal_type: string;
  strength: string;
  strategy: string;
  price: number;
  timestamp: string;
  indicators: Record<string, number>;
  message: string;
}

interface SignalsResult {
  symbol: string;
  signals_count: number;
  signals: TradingSignal[];
}

export type {
  PriceInfo,
  AssetHistory,
  StrategyResult,
  PortfolioResult,
  PredictionResult,
  PaperTradingUser,
  PaperPosition,
  PaperPortfolio,
  PaperTrade,
  PaperTradeResult,
  TradingSignal,
  SignalsResult
};
