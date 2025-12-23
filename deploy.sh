#!/bin/bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "=========================================="
echo "  Quant Dashboard Deployment Script"
echo "=========================================="
echo ""

if [ "$EUID" -eq 0 ]; then
    log_error "Do not run this script as root"
    exit 1
fi

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

log_info "Project directory: $PROJECT_DIR"
echo ""

log_info "Step 1/7: Checking system requirements..."
for cmd in python3 node npm nginx systemctl; do
    if ! command -v $cmd &> /dev/null; then
        log_error "$cmd is required but not installed"
        exit 1
    fi
    log_success "$cmd found"
done
echo ""

log_info "Step 2/7: Setting up Python virtual environment..."
cd "$BACKEND_DIR"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    log_success "Virtual environment created"
else
    log_info "Virtual environment already exists"
fi

source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
log_success "Python dependencies installed"
echo ""

log_info "Step 3/7: Installing frontend dependencies..."
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    npm install > /dev/null 2>&1
    log_success "Node modules installed"
else
    log_info "Node modules already installed"
fi
echo ""

log_info "Step 4/7: Building frontend..."
npm run build > /dev/null 2>&1
log_success "Frontend built successfully"
echo ""

log_info "Step 5/7: Setting up systemd service..."
sudo cp "$BACKEND_DIR/deploy/quant-backend.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable quant-backend.service
sudo systemctl restart quant-backend.service
log_success "Systemd service configured and started"
echo ""

log_info "Step 6/7: Configuring nginx..."
sudo cp "$BACKEND_DIR/deploy/nginx.conf" /etc/nginx/sites-available/quant-dashboard
sudo ln -sf /etc/nginx/sites-available/quant-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
log_success "Nginx configured and reloaded"
echo ""

log_info "Step 7/7: Setting up cron jobs..."
cd "$BACKEND_DIR/scripts"
bash setup_cron.sh
log_success "Cron jobs configured"
echo ""

echo "=========================================="
log_success "Deployment completed successfully!"
echo "=========================================="
echo ""
log_info "Backend API: http://localhost:8000"
log_info "API Docs: http://localhost:8000/docs"
log_info "Health check: http://localhost:8000/health"
echo ""
log_info "Service status: sudo systemctl status quant-backend"
log_info "Service logs: sudo journalctl -u quant-backend -f"
echo ""
