# Quant Finance Dashboard

Quantitative finance platform for real-time asset analysis and portfolio management.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![React](https://img.shields.io/badge/React-18.3-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green)

## Live Demo

Production URL: http://34.163.147.93

The application runs 24/7 on a Google Cloud VM.

## Team

| Role | Student | Email | Module |
|------|---------|-------|--------|
| Quant A | Lucas Soares | lucas.soares@edu.devinci.fr | Single Asset Analysis |
| Quant B | Felix Jouary | fjouary@gmail.com | Multi-Asset Portfolio |

## Overview

This project was developed for the "Python, Git, Linux for Finance" course. The platform provides:

- Real-time financial data from Yahoo Finance
- Quantitative strategy backtesting (momentum, mean reversion, MA crossover)
- Portfolio optimization (risk parity, minimum variance, maximum Sharpe)
- Price prediction using Facebook Prophet
- Paper trading simulator
- Automated daily reports via cron jobs
- 24/7 deployment on Linux

## Features

### Core Requirements

**Live Market Ticker**
- Real-time price updates for major assets
- Animated ticker banner with color-coded changes
- Auto-refresh every 5 minutes

**Strategy Backtesting (Quant A)**
- Buy-and-hold baseline
- Momentum strategy
- Mean reversion (Bollinger Bands)
- Moving average crossover
- Performance metrics: Sharpe ratio, max drawdown, volatility

**Portfolio Analysis (Quant B)**
- Multi-asset portfolio construction (2-10 assets)
- Weighting strategies: Equal, Risk Parity, Min Variance, Max Sharpe
- Correlation matrix heatmap
- Rebalancing simulation (daily/weekly/monthly/quarterly)

**Automated Daily Reports**
- Cron job at 20:00 daily
- Market summary with gainers/losers
- Asset reports with OHLC, volatility, max drawdown
- 30-day rolling archive

### Bonus Features

**Price Prediction**
- Facebook Prophet model
- 7-365 day forecasts
- Confidence intervals
- Performance metrics (MAE, MAPE, RMSE, R²)

**Paper Trading**
- $1,000,000 virtual balance
- Real-time trade execution
- P&L tracking
- Trade history

**Additional UI Features**
- Dark mode toggle
- Interactive slider controls
- Trading signals (RSI, MACD, Bollinger Bands)

## Division of Work

### Quant A - Lucas Soares

Backend:
- `data_fetcher.py` - Real-time market data with caching
- `strategies.py` - Trading strategies
- `metrics.py` - Performance metrics
- `prediction.py` - Prophet forecasting
- `signals.py` - Technical indicators
- `paper_trading.py` - Trading simulator

Frontend:
- `SingleAsset.tsx` - Single asset page with sliders
- `AssetChart.tsx` - Price and strategy charts
- `PredictionChart.tsx` - Forecast visualization
- `MetricsCard.tsx` - Metrics display
- `SignalIndicator.tsx` - Signal indicators
- `PaperTrading.tsx` - Trading interface
- `TradeHistory.tsx` - Trade history table

### Quant B - Felix Jouary

Backend:
- `portfolio.py` - Portfolio optimization
  - Multiple weighting strategies
  - Rebalancing simulation
  - Efficient frontier

Frontend:
- `Portfolio.tsx` - Portfolio dashboard
- `PortfolioChart.tsx` - Multi-asset charts
- `CorrelationMatrix.tsx` - Correlation heatmap
- `RiskReturnProfile.tsx` - Risk-return chart

### Shared

- `main.py` - FastAPI API
- `api.ts` - Frontend API client
- `Navigation.tsx` - Navigation with dark mode
- `MarketTicker.tsx` - Market ticker
- `daily_report.py` - Report generator
- Deployment scripts and configuration

## Technical Stack

Backend: Python 3.10+, FastAPI, pandas, numpy, yfinance, Prophet, SQLite

Frontend: React 18, TypeScript, Vite, shadcn/ui, Recharts, React Query

DevOps: Google Cloud Platform, Nginx, SystemD, Cron

## Installation

### Backend

```bash
git clone https://github.com/felixjry/quant-finance-dashboard.git
cd quant-finance-dashboard/backend

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

uvicorn api.main:app --host 0.0.0.0 --port 8000
```

API documentation: http://localhost:8000/docs

### Frontend

```bash
cd quant-finance-dashboard

npm install
npm run dev      # Development
npm run build    # Production
```

Frontend runs on http://localhost:8080

## Deployment

Server: Google Cloud Platform (e2-micro, Ubuntu 25.10, IP: 34.163.147.93)

Backend managed by SystemD for automatic restart. Frontend served by Nginx reverse proxy.

### Backend Deployment

```bash
ssh user@34.163.147.93

git clone https://github.com/felixjry/quant-finance-dashboard.git
cd quant-finance-dashboard/backend

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

sudo cp scripts/quant-dashboard.service /etc/systemd/system/
sudo systemctl enable quant-dashboard
sudo systemctl start quant-dashboard
```

### Frontend Deployment

```bash
cd quant-finance-dashboard
npm install
npm run build

sudo cp nginx.conf /etc/nginx/sites-available/quant-dashboard
sudo ln -s /etc/nginx/sites-available/quant-dashboard /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### Cron Job

```bash
cd backend/scripts
chmod +x cron_setup.sh
./cron_setup.sh
crontab -l  # Verify
```

## API Endpoints

Asset Data:
- `GET /api/assets`
- `GET /api/asset/{symbol}/price`
- `GET /api/asset/{symbol}/history`

Strategies:
- `GET /api/asset/{symbol}/strategy`
- `POST /api/asset/{symbol}/strategy`

Portfolio:
- `POST /api/portfolio/analyze`
- `GET /api/portfolio/efficient-frontier`

Prediction:
- `GET /api/asset/{symbol}/predict`

Paper Trading:
- `POST /api/paper-trading/trade`
- `GET /api/paper-trading/portfolio/{user_id}`
- `GET /api/paper-trading/trades/{user_id}`

## Cron Job Details

Daily reports generated at 20:00 containing:
- Market summary (gainers/losers)
- Individual asset reports (AAPL, MSFT, GOOGL, TSLA, SPY, BTC-USD, EURUSD=X, ENGI.PA)
- OHLC prices, volume
- Volatility, max drawdown, returns

Reports stored in `backend/reports/` with 30-day retention.

## Data Sources

Yahoo Finance via yfinance library

Supported assets:
- US Stocks: AAPL, MSFT, GOOGL, TSLA, AMZN, META, NVDA, JPM
- French Stocks: ENGI.PA, TTE.PA, BNP.PA, SAN.PA, AIR.PA, OR.PA
- ETFs: SPY, QQQ, IWM, VTI, EFA
- Crypto: BTC-USD, ETH-USD, SOL-USD
- Forex: EURUSD=X, GBPUSD=X, USDJPY=X, USDCHF=X

Data refreshes every 5 minutes with caching.

## GitHub Workflow

Branches:
- `main` - Production deployment
- `master` - Development
- `feature/quant-a-single-asset` - Lucas's work
- `feature/quant-b-portfolio` - Felix's work

Commits attributed to respective team members. Pull requests used for merging.

## Testing

Backend:
```bash
cd backend
pytest tests/ -v
```

Frontend:
```bash
npm run test
```

## Troubleshooting

Backend issues:
```bash
sudo systemctl status quant-dashboard
sudo journalctl -u quant-dashboard -n 50
```

Frontend rebuild:
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

Cron job:
```bash
crontab -l
tail -f backend/logs/cron.log
```

## Contact

Lucas Soares - lucas.soares@edu.devinci.fr
Felix Jouary - fjouary@gmail.com

Repository: https://github.com/felixjry/quant-finance-dashboard
Live Demo: http://34.163.147.93

## License

MIT License

---

Last Updated: January 2026
