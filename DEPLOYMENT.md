# Deployment Guide

## Quick Start

```bash
chmod +x deploy.sh
./deploy.sh
```

## Manual Deployment

### 1. System Requirements

Ubuntu 20.04+ with:
- Python 3.8+
- Node.js 16+
- Nginx
- systemd

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nodejs npm nginx
```

### 2. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Environment configuration:
```bash
cp .env.example .env
nano .env
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run build
```

### 4. Systemd Service

```bash
sudo cp backend/deploy/quant-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable quant-backend
sudo systemctl start quant-backend
sudo systemctl status quant-backend
```

### 5. Nginx Configuration

```bash
sudo cp backend/deploy/nginx.conf /etc/nginx/sites-available/quant-dashboard
sudo ln -s /etc/nginx/sites-available/quant-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. SSL Certificate (Optional)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.quant-dashboard.com
```

### 7. Cron Jobs

```bash
cd backend/scripts
chmod +x setup_cron.sh
./setup_cron.sh
```

## Service Management

```bash
sudo systemctl start quant-backend
sudo systemctl stop quant-backend
sudo systemctl restart quant-backend
sudo systemctl status quant-backend
sudo journalctl -u quant-backend -f
```

## API Endpoints

- Health: http://localhost:8000/health
- Docs: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

## Directory Structure

```
/home/ubuntu/quant-finance-dashboard/
├── backend/
│   ├── api/
│   ├── services/
│   ├── logs/
│   ├── reports/
│   └── venv/
└── frontend/
    ├── src/
    └── dist/
```

## Troubleshooting

Check service status:
```bash
sudo systemctl status quant-backend
```

View logs:
```bash
sudo journalctl -u quant-backend -n 100
tail -f backend/logs/service.log
```

Test API:
```bash
curl http://localhost:8000/health
```

Check nginx:
```bash
sudo nginx -t
sudo systemctl status nginx
```

## Monitoring

Daily reports: `backend/reports/`
Service logs: `backend/logs/service.log`
Cron logs: `backend/logs/cron.log`
Nginx logs: `/var/log/nginx/`
