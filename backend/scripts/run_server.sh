#!/bin/bash
# Server startup script for Quant Dashboard Backend
# Features:
# - Environment validation
# - Health checks
# - Graceful shutdown handling
# - Comprehensive logging
# - Process management

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
API_DIR="$PROJECT_DIR/api"
LOG_DIR="$PROJECT_DIR/logs"
PID_FILE="$PROJECT_DIR/.server.pid"

# Server configuration
HOST="${API_HOST:-0.0.0.0}"
PORT="${API_PORT:-8000}"
RELOAD="${API_RELOAD:-true}"

# Functions
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

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 is not installed"
        return 1
    fi
    log_success "$1 is installed"
    return 0
}

check_python_version() {
    local python_version=$(python3 --version 2>&1 | awk '{print $2}')
    local major=$(echo $python_version | cut -d. -f1)
    local minor=$(echo $python_version | cut -d. -f2)

    if [ "$major" -ge 3 ] && [ "$minor" -ge 8 ]; then
        log_success "Python version $python_version (OK)"
        return 0
    else
        log_error "Python 3.8+ required, found $python_version"
        return 1
    fi
}

check_port_available() {
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        log_error "Port $PORT is already in use"
        log_info "Process using port $PORT:"
        lsof -Pi :$PORT -sTCP:LISTEN
        return 1
    fi
    log_success "Port $PORT is available"
    return 0
}

validate_environment() {
    log_info "Validating environment..."

    # Check required commands
    check_command python3 || exit 1
    check_command pip3 || exit 1
    check_python_version || exit 1

    # Check if uvicorn is installed
    if ! python3 -c "import uvicorn" 2>/dev/null; then
        log_error "uvicorn is not installed"
        log_info "Run: pip install uvicorn[standard]"
        exit 1
    fi
    log_success "uvicorn is installed"

    # Check project structure
    if [ ! -d "$API_DIR" ]; then
        log_error "API directory not found: $API_DIR"
        exit 1
    fi
    log_success "Project structure verified"

    # Check port availability
    check_port_available || exit 1

    log_success "Environment validation complete"
    echo ""
}

setup_logging() {
    mkdir -p "$LOG_DIR"
    export LOG_FILE="$LOG_DIR/server_$(date +%Y%m%d_%H%M%S).log"
    log_info "Logging to: $LOG_FILE"
}

cleanup() {
    log_info "Shutting down gracefully..."
    if [ -f "$PID_FILE" ]; then
        rm -f "$PID_FILE"
    fi
    log_success "Server stopped"
}

# Trap SIGINT and SIGTERM
trap cleanup EXIT INT TERM

# Main execution
main() {
    echo "=========================================="
    echo "  Quant Dashboard API Server"
    echo "=========================================="
    echo ""

    # Validate environment
    validate_environment

    # Setup logging
    setup_logging

    # Change to project directory
    cd "$PROJECT_DIR"
    log_info "Working directory: $PROJECT_DIR"

    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate
        log_success "Virtual environment activated"
    else
        log_warning "No virtual environment found (venv directory missing)"
        log_info "Continuing with system Python..."
    fi

    # Set PYTHONPATH
    export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"
    log_info "PYTHONPATH configured"

    # Display server information
    echo ""
    echo "=========================================="
    echo "  Server Configuration"
    echo "=========================================="
    log_info "Host: $HOST"
    log_info "Port: $PORT"
    log_info "Reload: $RELOAD"
    log_info "API Docs: http://localhost:$PORT/docs"
    log_info "Redoc: http://localhost:$PORT/redoc"
    log_info "Health check: http://localhost:$PORT/health"
    echo "=========================================="
    echo ""

    # Save PID
    echo $$ > "$PID_FILE"

    # Start server
    log_info "Starting server..."
    echo ""

    if [ "$RELOAD" = "true" ]; then
        uvicorn api.main:app \
            --host "$HOST" \
            --port "$PORT" \
            --reload \
            --log-level info \
            2>&1 | tee -a "$LOG_FILE"
    else
        uvicorn api.main:app \
            --host "$HOST" \
            --port "$PORT" \
            --log-level info \
            --workers 4 \
            2>&1 | tee -a "$LOG_FILE"
    fi
}

# Run main function
main
