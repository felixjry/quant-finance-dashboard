# Systemd Service Configuration for 24/7 Operation

This document explains how to set up the Quant Dashboard API as a systemd service on a Linux VM for continuous operation.

## Service File

Create the service file at `/etc/systemd/system/quant-dashboard.service`:

```ini
[Unit]
Description=Quant Dashboard FastAPI Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/quant-dashboard-pro/backend
Environment=PYTHONPATH=/home/ubuntu/quant-dashboard-pro/backend
ExecStart=/home/ubuntu/quant-dashboard-pro/backend/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Installation Steps

1. Copy the service file:
```bash
sudo cp quant-dashboard.service /etc/systemd/system/
```

2. Reload systemd:
```bash
sudo systemctl daemon-reload
```

3. Enable the service (start on boot):
```bash
sudo systemctl enable quant-dashboard
```

4. Start the service:
```bash
sudo systemctl start quant-dashboard
```

## Management Commands

Check status:
```bash
sudo systemctl status quant-dashboard
```

View logs:
```bash
sudo journalctl -u quant-dashboard -f
```

Restart service:
```bash
sudo systemctl restart quant-dashboard
```

Stop service:
```bash
sudo systemctl stop quant-dashboard
```

## Cron Job for Daily Reports

The daily report cron job should be set up separately:

```bash
# Edit crontab
crontab -e

# Add this line for 8 PM daily report
0 20 * * * cd /home/ubuntu/quant-dashboard-pro/backend && /home/ubuntu/quant-dashboard-pro/backend/venv/bin/python scripts/daily_report.py >> /home/ubuntu/quant-dashboard-pro/backend/logs/cron.log 2>&1
```

## Directory Structure on VM

```
/home/ubuntu/quant-dashboard-pro/
├── backend/
│   ├── api/
│   ├── services/
│   ├── scripts/
│   ├── reports/       # Generated reports stored here
│   ├── logs/          # Log files
│   ├── venv/          # Python virtual environment
│   └── requirements.txt
└── frontend/
    └── dist/          # Built frontend files
```

## Nginx Configuration (Optional)

For serving the frontend and proxying API requests:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /home/ubuntu/quant-dashboard-pro/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API proxy
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
