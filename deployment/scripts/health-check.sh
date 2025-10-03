#!/bin/bash
# Agent Zero Health Check Script
# Checks if all critical services are running

set -e

AGENT_ZERO_PATH="${AGENT_ZERO_PATH:-/opt/agent-zero}"
COMPOSE_FILE="$AGENT_ZERO_PATH/docker-compose.production.yml"
LOG_FILE="/var/log/agent-zero-health.log"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_service() {
    local service=$1
    local port=$2
    
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "$service.*Up"; then
        if [ -n "$port" ]; then
            if nc -z localhost "$port" 2>/dev/null; then
                echo -e "${GREEN}✓${NC} $service is running and accessible on port $port"
                return 0
            else
                echo -e "${YELLOW}⚠${NC} $service is running but port $port is not accessible"
                return 1
            fi
        else
            echo -e "${GREEN}✓${NC} $service is running"
            return 0
        fi
    else
        echo -e "${RED}✗${NC} $service is not running"
        return 1
    fi
}

main() {
    log "Starting health check..."
    
    cd "$AGENT_ZERO_PATH" || exit 1
    
    local failures=0
    
    # Check critical services
    check_service "agent-zero" 50001 || ((failures++))
    check_service "postgres" 5432 || ((failures++))
    check_service "litellm" 4000 || ((failures++))
    check_service "langfuse" 3000 || ((failures++))
    check_service "prometheus" 9090 || ((failures++))
    check_service "grafana" 3001 || ((failures++))
    check_service "loki" 3100 || ((failures++))
    check_service "rabbitmq" 5672 || ((failures++))
    check_service "opensearch" 9200 || ((failures++))
    check_service "redis" 6379 || ((failures++))
    
    if [ $failures -eq 0 ]; then
        log "Health check passed: All services are running"
        exit 0
    else
        log "Health check failed: $failures service(s) are not healthy"
        
        # Try to restart failed services
        log "Attempting to restart services..."
        docker-compose -f "$COMPOSE_FILE" up -d
        
        exit 1
    fi
}

main "$@"
