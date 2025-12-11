# Quant Finance Dashboard

> Professional quantitative finance dashboard for real-time asset analysis and portfolio management

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![React](https://img.shields.io/badge/React-18.3-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Team

| Role | Student | Email | Module |
|------|---------|-------|--------|
| **Quant A** | Lucas Soares | lucas.soares@edu.devinci.fr | Single Asset Analysis |
| **Quant B** | Felix Jouary | fjouary@gmail.com | Multi-Asset Portfolio |

## Project Overview

This project is a professional-grade quantitative finance platform developed as part of the "Python, Git, Linux for Finance" academic course. It provides tools for:

- **Real-time financial data retrieval** from Yahoo Finance
- **Quantitative strategy backtesting** (momentum, mean reversion, MA crossover)
- **Portfolio optimization** (risk parity, minimum variance, maximum Sharpe)
- **Price prediction** using Facebook Prophet (bonus feature)
- **Paper trading simulator** with virtual portfolio management
- **Automated daily reports** via cron jobs
- **24/7 deployment** on Linux servers

---

## Division of Work

### Quant A - Single Asset Analysis (Lucas Soares)

**Backend Services:**
- `data_fetcher.py` - Real-time market data fetching with 5-minute caching
- `strategies.py` - Trading strategies implementation:
  - Buy-and-hold baseline
  - Momentum strategy (configurable lookback period)
  - Mean reversion (Bollinger Bands)
  - Moving average crossover
- `metrics.py` - Performance metrics calculation:
  - Sharpe ratio
  - Maximum drawdown
  - Volatility
  - Total/annualized returns
- `prediction.py` - Price forecasting with Prophet (bonus)
- `signals.py` - Technical indicators (RSI, MACD, Bollinger Bands)
- `paper_trading.py` - Virtual trading simulator

**Frontend Components:**
- `SingleAsset.tsx` - Main single asset analysis page
- `AssetChart.tsx` - Interactive price and strategy visualization
- `PredictionChart.tsx` - Forecast display with confidence intervals
- `MetricsCard.tsx` - Performance metrics cards
- `SignalIndicator.tsx` - Trading signal indicators

### Quant B - Multi-Asset Portfolio (Felix Jouary)

**Backend Services:**
- `portfolio.py` - Portfolio analysis and optimization:
  - Equal weight allocation
  - Risk parity (inverse volatility weighting)
  - Minimum variance optimization
  - Maximum Sharpe ratio optimization
  - Custom user-defined weights
  - Rebalancing simulation (daily/weekly/monthly/quarterly)
  - Efficient frontier generation

**Frontend Components:**
- `Portfolio.tsx` - Portfolio analysis dashboard
- `PortfolioChart.tsx` - Multi-asset performance visualization
- `CorrelationMatrix.tsx` - Asset correlation heatmap
- `RiskReturnProfile.tsx` - Risk-return radar chart

### Shared Responsibilities

**Configuration & API:**
- `config.py` - Application configuration
- `main.py` - FastAPI REST API with 30+ endpoints
- `api.ts` - Frontend API client
- `useFinancialData.ts` - React Query hooks

**UI Infrastructure:**
- shadcn/ui component library integration
- Recharts visualization setup
- React Router navigation
- Tailwind CSS styling

**Automation:**
- Cron job configuration
- Daily report generation
- SystemD service setup

---

## Technical Stack

### Backend
- **Framework:** FastAPI (Python 3.10+)
- **Data Source:** Yahoo Finance (yfinance)
- **Data Processing:** pandas, numpy
- **Forecasting:** Facebook Prophet
- **Database:** SQLite (paper trading)
- **Server:** Uvicorn + Gunicorn

### Frontend
- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite
- **UI Library:** shadcn/ui (Radix UI + Tailwind CSS)
- **Charts:** Recharts
- **State Management:** React Query
- **Routing:** React Router v6

### DevOps
- **Deployment:** Linux VM (24/7 operation)
- **Process Manager:** SystemD
- **Web Server:** Nginx (reverse proxy)
- **Automation:** Cron jobs

---

## Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn
- Git

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Or use the startup script
chmod +x scripts/run_server.sh
./scripts/run_server.sh
```

**API Documentation:** http://localhost:8000/docs

### Frontend Setup

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

**Frontend URL:** http://localhost:8080

---

## Features

### Core Features (Required)

✅ **Data Retrieval**
- Real-time market data from Yahoo Finance
- 15+ supported assets (stocks, ETFs, crypto, forex)
- 5-minute caching for optimal performance

✅ **Strategy Backtesting** (Quant A)
- 4 trading strategies with interactive parameters
- Performance metrics visualization
- Historical backtest results

✅ **Portfolio Analysis** (Quant B)
- Multi-asset portfolio construction (2-10 assets)
- 4 weighting strategies with optimization
- Correlation analysis and diversification metrics
- Rebalancing simulation

✅ **Automated Refresh**
- Data updates every 5 minutes
- Real-time price display

✅ **Daily Reports**
- Automated report generation at 20:00 via cron
- Volatility, OHLC prices, max drawdown
- Stored locally in `backend/reports/`

✅ **24/7 Deployment**
- SystemD service configuration
- Process monitoring and auto-restart
- Nginx reverse proxy setup

### Bonus Features

🎁 **Price Prediction** (Quant A)
- Facebook Prophet forecasting model
- Confidence intervals visualization
- 7-365 day forecast horizons

🎁 **Paper Trading**
- Virtual trading simulator
- Real-time P&L tracking
- Trade history and position management

🎁 **Trading Signals**
- RSI, MACD, Bollinger Bands indicators
- Signal strength classification
- Automated signal detection

---

## API Endpoints

### Asset Data
- `GET /api/assets` - List available assets
- `GET /api/asset/{symbol}/price` - Get current price
- `GET /api/asset/{symbol}/history` - Get historical data
- `GET /api/asset/{symbol}/metrics` - Get performance metrics

### Strategies (Quant A)
- `GET /api/asset/{symbol}/strategy` - Run backtest strategy

### Portfolio (Quant B)
- `POST /api/portfolio/analyze` - Analyze multi-asset portfolio
- `GET /api/portfolio/efficient-frontier` - Generate efficient frontier

### Prediction (Bonus)
- `GET /api/asset/{symbol}/predict` - Get price forecast

### Paper Trading (Bonus)
- `POST /api/paper-trading/trade` - Execute virtual trade
- `GET /api/paper-trading/portfolio/{user_id}` - Get portfolio

---

## Automation & Cron Jobs

### Daily Report Setup

```bash
# Setup cron job (runs at 20:00 daily)
cd backend/scripts
chmod +x cron_setup.sh
./cron_setup.sh

# Verify installation
crontab -l

# View logs
tail -f backend/logs/cron.log
```

### SystemD Service (24/7 Deployment)

```bash
# Create service file
sudo cp backend/scripts/quant-dashboard.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start
sudo systemctl enable quant-dashboard
sudo systemctl start quant-dashboard

# Check status
sudo systemctl status quant-dashboard
```

See [backend/scripts/systemd_service.md](backend/scripts/systemd_service.md) for detailed instructions.

---

## GitHub Workflow

### Branch Structure
- `main` - Production-ready code
- `feature/quant-a-single-asset` - Lucas's work (single asset analysis)
- `feature/quant-b-portfolio` - Felix's work (portfolio analysis)

### Commit History
All commits are properly attributed to the respective team members:
- **Lucas Soares** - Data fetching, strategies, prediction, signals
- **Felix Jouary** - Portfolio optimization, correlation analysis, frontend integration

### Pull Requests
- Feature branches merged into `main` with proper review
- Clear separation of responsibilities maintained throughout

---

## Data Sources

**Primary:** [Yahoo Finance](https://finance.yahoo.com/) via yfinance library

**Supported Assets:**
- US Stocks: AAPL, MSFT, GOOGL, TSLA, AMZN, META, NVDA, JPM
- French Stocks: ENGI.PA, TTE.PA, BNP.PA, SAN.PA, AIR.PA, OR.PA
- ETFs: SPY, QQQ, IWM, VTI, EFA
- Crypto: BTC-USD, ETH-USD, SOL-USD
- Forex: EURUSD=X, GBPUSD=X, USDJPY=X, USDCHF=X

---

## License

MIT License - See [LICENSE](LICENSE) for details

---

## Acknowledgments

- **Course:** Python, Git, Linux for Finance
- **Institution:** ESILV - École Supérieure d'Ingénieurs Léonard de Vinci
- **Data Provider:** Yahoo Finance
- **UI Library:** shadcn/ui

---

## Contact

- **Lucas Soares** - lucas.soares@edu.devinci.fr
- **Felix Jouary** - fjouary@gmail.com

---

**Last Updated:** December 2024
