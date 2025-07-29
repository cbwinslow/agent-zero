#!/bin/bash

set -euo pipefail

# Print info messages
log_info() {
    echo "[INFO] $1"
}

log_error() {
    echo "[ERROR] $1" >&2
}

# Catch errors and exit gracefully
trap 'log_error "Setup failed at line $LINENO while running: $BASH_COMMAND"' ERR

MCP_URL=""
INSTALL_ELK=false

# Parse custom arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --mcp-url)
            MCP_URL="$2"
            shift 2
            ;;
        --install-elk)
            INSTALL_ELK=true
            shift
            ;;
        *)
            break
            ;;
    esac
done

log_info "Installing dependencies"
if [[ -f requirements.txt ]]; then
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt
fi

# Optional ELK stack installation
if [[ "$INSTALL_ELK" == true ]]; then
    log_info "Installing ELK stack via scripts/install_elk.sh"
    bash scripts/install_elk.sh || log_error "ELK installation failed"
fi

# Download MCP server if URL provided
if [[ -n "$MCP_URL" ]]; then
    log_info "Downloading MCP server from $MCP_URL"
    bash scripts/download_mcp.sh "$MCP_URL"
fi

log_info "Preparing environment"
python3 prepare.py "$@"

log_info "Preloading models or data"
python3 preload.py "$@"

log_info "Starting the Agent Zero web UI"
exec python3 run_ui.py "$@"
