# Quant Finance Dashboard

> Professional quantitative finance dashboard for real-time asset analysis and portfolio management

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![React](https://img.shields.io/badge/React-18.3-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Live-success)

## Live Demo

**Production URL:** [http://34.163.147.93](http://34.163.147.93)

The application is deployed 24/7 on a Google Cloud VM and accessible worldwide.

---

## Team

| Role | Student | Email | Module |
|------|---------|-------|--------|
| **Quant A** | Lucas Soares | lucas.soares@edu.devinci.fr | Single Asset Analysis |
| **Quant B** | Felix Jouary | fjouary@gmail.com | Multi-Asset Portfolio |

---

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

## Key Features

### 🎯 Core Functionality

✅ **Live Market Ticker**
- Real-time price updates for major assets (AAPL, MSFT, GOOGL, BTC, etc.)
- Animated ticker banner with color-coded price changes
- Auto-refresh every 5 minutes

✅ **Dark Mode Support**
- System-preference aware theme switching
- Persistent theme selection
- Optimized for extended viewing sessions

✅ **Interactive Controls**
- Slider controls for strategy parameters (Lookback Period: 5-200 days)
- Forecast period adjustment (7-90 days)
- Real-time parameter updates with instant visualization

✅ **Strategy Backtesting** (Quant A)
- Buy-and-hold baseline
- Momentum strategy (configurable lookback)
- Mean reversion (Bollinger Bands)
- Moving average crossover
- Performance metrics: Sharpe ratio, max drawdown, volatility

✅ **Portfolio Analysis** (Quant B)
- Multi-asset portfolio construction (2-10 assets)
- Weighting strategies: Equal, Risk Parity, Min Variance, Max Sharpe
- Correlation matrix heatmap
- Diversification metrics
- Rebalancing simulation (daily/weekly/monthly/quarterly)

✅ **Paper Trading**
- Virtual $1,000,000 starting balance
- Real-time trade execution with live prices
- Portfolio P&L tracking
- Trade history with detailed records
- Active positions management

✅ **Price Prediction** (Bonus)
- Facebook Prophet forecasting model
- 7-365 day forecast horizons
- Confidence intervals visualization
- Model performance metrics (MAE, MAPE, RMSE, R²)

✅ **Automated Daily Reports**
- Cron job scheduled at 20:00 (8 PM) daily
- Comprehensive market summary with gainers/losers
- Individual asset reports with OHLC, volatility, max drawdown
- 30-day rolling archive with automatic cleanup

---

## Division of Work

### Quant A - Single Asset Analysis (Lucas Soares)

**Backend Services:**
- `data_fetcher.py` - Real-time market data fetching with 5-minute caching
- `strategies.py` - Trading strategies implementation
- `metrics.py` - Performance metrics calculation
- `prediction.py` - Price forecasting with Prophet (bonus)
- `signals.py` - Technical indicators (RSI, MACD, Bollinger Bands)
- `paper_trading.py` - Virtual trading simulator

**Frontend Components:**
- `SingleAsset.tsx` - Main single asset analysis page with interactive sliders
- `AssetChart.tsx` - Interactive price and strategy visualization
- `PredictionChart.tsx` - Forecast display with confidence intervals
- `MetricsCard.tsx` - Performance metrics cards
- `SignalIndicator.tsx` - Trading signal indicators
- `PaperTrading.tsx` - Paper trading interface
- `TradeHistory.tsx` - Trade history table with filtering

### Quant B - Multi-Asset Portfolio (Felix Jouary)

**Backend Services:**
- `portfolio.py` - Portfolio analysis and optimization
  - Equal weight allocation
  - Risk parity (inverse volatility weighting)
  - Minimum variance optimization
  - Maximum Sharpe ratio optimization
  - Custom user-defined weights
  - Rebalancing simulation
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
- `api.ts` - Frontend API client with TypeScript types
- `useFinancialData.ts` - React Query hooks for data fetching

**UI Infrastructure:**
- `Navigation.tsx` - Main navigation bar with dark mode toggle
- `MarketTicker.tsx` - Real-time market ticker banner
- shadcn/ui component library integration
- Recharts visualization setup
- React Router navigation
- Tailwind CSS styling

**Automation:**
- `daily_report.py` - Daily report generation script
- `cron_setup.sh` - Cron job configuration
- SystemD service setup for 24/7 operation

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
- **State Management:** React Query (TanStack Query)
- **Routing:** React Router v6
- **HTTP Client:** Axios

### DevOps
- **Platform:** Google Cloud Platform (Ubuntu 25.10 VM)
- **Process Manager:** SystemD
- **Web Server:** Nginx (reverse proxy)
- **Automation:** Cron jobs
- **Version Control:** Git + GitHub

---

## Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn
- Git

### Local Development

#### Backend Setup

```bash
# Clone repository
git clone https://github.com/felixjry/quant-finance-dashboard.git
cd quant-finance-dashboard

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
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Or use the startup script
chmod +x scripts/run_server.sh
./scripts/run_server.sh
```

**API Documentation:** http://localhost:8000/docs

#### Frontend Setup

```bash
# From project root directory
cd quant-finance-dashboard

# Install dependencies
npm install

# Configure API endpoint (if needed)
# Edit src/services/api.ts to point to your backend URL

# Run development server
npm run dev

# Build for production
npm run build
```

**Frontend URL:** http://localhost:8080

---

## Production Deployment

### Server Configuration

**Platform:** Google Cloud Platform
**Instance Type:** e2-micro (2 vCPUs, 1 GB RAM)
**OS:** Ubuntu 25.10
**Public IP:** 34.163.147.93

### Deployment Steps

#### 1. Backend Deployment

```bash
# SSH into VM
ssh user@34.163.147.93

# Clone repository
git clone https://github.com/felixjry/quant-finance-dashboard.git
cd quant-finance-dashboard/backend

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create SystemD service
sudo cp scripts/quant-dashboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable quant-dashboard
sudo systemctl start quant-dashboard

# Verify service is running
sudo systemctl status quant-dashboard
```

#### 2. Frontend Deployment

```bash
# Build frontend locally
npm run build

# Copy dist/ to VM (or build on VM)
cd ~/quant-finance-dashboard
npm install
npm run build

# Configure Nginx
sudo cp nginx.conf /etc/nginx/sites-available/quant-dashboard
sudo ln -s /etc/nginx/sites-available/quant-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 3. Cron Job Setup

```bash
# Setup daily report generation
cd backend/scripts
chmod +x cron_setup.sh
./cron_setup.sh

# Verify cron job
crontab -l

# Test report generation
python3 daily_report.py
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name 34.163.147.93;

    root /home/user/quant-finance-dashboard/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## API Endpoints

### Asset Data
- `GET /api/assets` - List available assets
- `GET /api/asset/{symbol}/price` - Get current price
- `GET /api/asset/{symbol}/history` - Get historical data
- `GET /api/asset/{symbol}/metrics` - Get performance metrics

### Strategies (Quant A)
- `GET /api/asset/{symbol}/strategy` - Run backtest strategy
- `POST /api/asset/{symbol}/strategy` - Run backtest with custom parameters

### Portfolio (Quant B)
- `POST /api/portfolio/analyze` - Analyze multi-asset portfolio
- `GET /api/portfolio/efficient-frontier` - Generate efficient frontier

### Prediction (Bonus)
- `GET /api/asset/{symbol}/predict` - Get price forecast

### Paper Trading (Bonus)
- `POST /api/paper-trading/user` - Create trading account
- `GET /api/paper-trading/user/{user_id}` - Get user details
- `POST /api/paper-trading/trade` - Execute virtual trade
- `GET /api/paper-trading/portfolio/{user_id}` - Get portfolio
- `GET /api/paper-trading/trades/{user_id}` - Get trade history

### Trading Signals
- `GET /api/signals` - Get active trading signals
- `GET /api/asset/{symbol}/signals` - Detect signals for specific asset

### System
- `GET /api/health` - Health check endpoint
- `DELETE /api/cache/clear` - Clear data cache

---

## Automation & Cron Jobs

### Daily Report Generation

The platform generates comprehensive daily reports at 20:00 (8 PM) via cron job.

**Report Contents:**
- Market summary with top gainers and losers
- Individual asset reports for watchlist (AAPL, MSFT, GOOGL, TSLA, SPY, BTC-USD, EURUSD=X, ENGI.PA)
- OHLC prices, volume, daily change
- Monthly metrics: volatility, max drawdown, total return
- Daily statistics: mean/std returns, positive/negative days

**Setup:**

```bash
# Install cron job
cd backend/scripts
chmod +x cron_setup.sh
./cron_setup.sh

# Verify installation
crontab -l
# Output: 0 20 * * * cd /path/to/backend && python3 scripts/daily_report.py >> logs/cron.log 2>&1

# View logs
tail -f backend/logs/cron.log

# View generated reports
ls -lh backend/reports/
cat backend/reports/daily_report_2026-01-05.json
```

**Features:**
- Automatic retry on API failures (3 attempts with exponential backoff)
- 30-day rolling archive with automatic cleanup
- Comprehensive logging and error handling
- Email notifications on critical errors (configurable)

---

## GitHub Workflow

### Repository Structure

```
quant-finance-dashboard/
├── backend/
│   ├── api/          # FastAPI application
│   ├── services/     # Business logic
│   ├── scripts/      # Automation scripts
│   ├── data/         # SQLite database
│   ├── reports/      # Generated reports
│   └── logs/         # Application logs
├── src/
│   ├── components/   # React components
│   ├── pages/        # Page components
│   ├── services/     # API client
│   └── hooks/        # Custom React hooks
├── public/           # Static assets
└── dist/             # Production build
```

### Branch Strategy

- `main` - Production-ready code (deployed)
- `master` - Development branch
- `feature/quant-a-single-asset` - Lucas's work (single asset analysis)
- `feature/quant-b-portfolio` - Felix's work (portfolio analysis)

### Commit History

All commits are properly attributed to respective team members:
- **Lucas Soares** - Data fetching, strategies, prediction, signals, paper trading
- **Felix Jouary** - Portfolio optimization, correlation analysis, frontend integration

### Collaboration Process

1. Each team member works on their dedicated branch
2. Regular commits with clear, descriptive messages
3. Pull requests for merging features into main
4. Code review and conflict resolution
5. Deployment from main branch to production

---

## Data Sources

**Primary:** [Yahoo Finance](https://finance.yahoo.com/) via yfinance library

**Supported Assets:**

- **US Stocks:** AAPL, MSFT, GOOGL, TSLA, AMZN, META, NVDA, JPM
- **French Stocks:** ENGI.PA, TTE.PA, BNP.PA, SAN.PA, AIR.PA, OR.PA
- **ETFs:** SPY, QQQ, IWM, VTI, EFA
- **Crypto:** BTC-USD, ETH-USD, SOL-USD
- **Forex:** EURUSD=X, GBPUSD=X, USDJPY=X, USDCHF=X

**Data Refresh:** Every 5 minutes with intelligent caching

---

## Performance & Optimization

### Backend Optimizations
- 5-minute data caching to minimize API calls
- Connection pooling for database operations
- Async/await for concurrent requests
- Efficient pandas operations for large datasets

### Frontend Optimizations
- React Query for intelligent data caching
- Code splitting with React.lazy()
- Optimized chart rendering with Recharts
- Debounced slider controls

### Infrastructure
- Nginx reverse proxy with gzip compression
- SystemD for automatic process recovery
- Log rotation to prevent disk space issues
- Daily cleanup of old reports (30-day retention)

---

## Error Handling

The platform includes robust error handling:

- **API Failures:** Automatic retry with exponential backoff
- **Invalid Symbols:** Clear error messages to users
- **Network Issues:** Cached data fallback
- **Process Crashes:** SystemD auto-restart
- **Cron Failures:** Detailed logging for debugging

---

## Testing

### Backend Testing

```bash
cd backend
pytest tests/ -v
```

### Frontend Testing

```bash
npm run test
```

### Manual Testing Checklist

- [ ] All pages load without errors
- [ ] Market ticker displays real-time prices
- [ ] Dark mode toggle works correctly
- [ ] Strategy sliders update charts in real-time
- [ ] Portfolio analysis accepts 2-10 assets
- [ ] Paper trading executes buy/sell orders
- [ ] Prediction charts display forecast with confidence intervals
- [ ] Daily reports generate successfully

---

## Troubleshooting

### Backend Issues

**Service not starting:**
```bash
sudo systemctl status quant-dashboard
sudo journalctl -u quant-dashboard -n 50
```

**API errors:**
```bash
tail -f backend/logs/uvicorn.log
```

### Frontend Issues

**Build failures:**
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

**API connection issues:**
- Check `src/services/api.ts` for correct backend URL
- Verify Nginx reverse proxy configuration
- Check backend is running: `curl http://localhost:8000/api/health`

### Cron Job Issues

**Report not generating:**
```bash
# Check cron is running
sudo systemctl status cron

# Test script manually
cd backend
python3 scripts/daily_report.py

# Check logs
tail -f backend/logs/cron.log
```

---

## Future Enhancements

- [ ] WebSocket support for real-time price updates
- [ ] User authentication and personalized portfolios
- [ ] Email/SMS alerts for trading signals
- [ ] Advanced ML models (LSTM, Transformer)
- [ ] Options and derivatives analysis
- [ ] Social trading features
- [ ] Mobile-responsive design improvements
- [ ] Docker containerization
- [ ] Kubernetes orchestration

---

## License

MIT License - See [LICENSE](LICENSE) for details

---

## Acknowledgments

- **Course:** Python, Git, Linux for Finance
- **Institution:** ESILV - École Supérieure d'Ingénieurs Léonard de Vinci
- **Data Provider:** Yahoo Finance
- **UI Library:** shadcn/ui
- **Forecasting:** Facebook Prophet

---

## Contact

- **Lucas Soares** - lucas.soares@edu.devinci.fr
- **Felix Jouary** - fjouary@gmail.com
- **Repository:** [https://github.com/felixjry/quant-finance-dashboard](https://github.com/felixjry/quant-finance-dashboard)
- **Live Demo:** [http://34.163.147.93](http://34.163.147.93)

---

**Last Updated:** January 2026
**Status:** ✅ Production - Live and Operational
