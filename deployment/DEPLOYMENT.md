# Agent Zero Production Deployment Guide

This guide provides comprehensive instructions for deploying Agent Zero in a production environment with full monitoring and observability stack.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Quick Start](#quick-start)
5. [Deployment Methods](#deployment-methods)
6. [Configuration](#configuration)
7. [Monitoring & Observability](#monitoring--observability)
8. [Multi-User Setup](#multi-user-setup)
9. [Maintenance](#maintenance)
10. [Troubleshooting](#troubleshooting)

## Overview

The production deployment includes:

- **Agent Zero**: Main AI assistant application
- **LiteLLM Proxy**: Cost tracking, rate limiting, and model interchangeability
- **Langfuse**: LLM observability and tracing
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization and dashboards
- **Loki**: Log aggregation
- **Promtail**: Log shipping
- **Netdata**: Real-time system monitoring
- **RabbitMQ**: Message queue for async tasks
- **OpenSearch**: Search and analytics
- **PostgreSQL**: Database for LiteLLM and Langfuse
- **Redis**: Caching and session storage

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Load Balancer                        │
│                     (nginx/traefik)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐       ┌───────▼────────┐
│  Agent Zero    │       │  Monitoring    │
│  Application   │◄─────►│     Stack      │
└───────┬────────┘       └───────┬────────┘
        │                        │
        ├────────────────────────┤
        │                        │
┌───────▼────────┐       ┌───────▼────────┐
│   LiteLLM      │       │   Langfuse     │
│    Proxy       │       │  (Observability)│
└───────┬────────┘       └────────────────┘
        │
┌───────▼────────────────────────────────┐
│         PostgreSQL Database            │
└────────────────────────────────────────┘
```

## Prerequisites

### System Requirements

- **OS**: Ubuntu 20.04+, Debian 11+, or CentOS 8+
- **CPU**: 4+ cores (8+ recommended)
- **RAM**: 8GB minimum (16GB+ recommended)
- **Disk**: 50GB minimum (100GB+ recommended)
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### Software Dependencies

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Make (optional but recommended)
sudo apt-get install make -y  # Debian/Ubuntu
sudo yum install make -y      # CentOS/RHEL
```

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/agent0ai/agent-zero.git
cd agent-zero
```

### 2. Configure Environment

```bash
# Copy example environment file
cp example.env .env

# Edit .env and add your API keys
nano .env
```

Required environment variables:
```bash
# API Keys
API_KEY_OPENAI=your_openai_api_key
API_KEY_ANTHROPIC=your_anthropic_api_key
API_KEY_OPENROUTER=your_openrouter_api_key

# Passwords (change these!)
GRAFANA_ADMIN_PASSWORD=change_me_secure_password
POSTGRES_PASSWORD=change_me_secure_password
RABBITMQ_PASSWORD=change_me_secure_password
REDIS_PASSWORD=change_me_secure_password
LITELLM_MASTER_KEY=sk-your-secure-key
```

### 3. Deploy Using Make

```bash
# Initialize environment
make init-env

# Start all services
make start
```

### 4. Access Services

After deployment, services are available at:

- **Agent Zero UI**: http://localhost:50001
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Langfuse**: http://localhost:3000
- **LiteLLM**: http://localhost:4000
- **RabbitMQ Management**: http://localhost:15672 (admin/admin)
- **OpenSearch Dashboards**: http://localhost:5601
- **Netdata**: http://localhost:19999

## Deployment Methods

### Method 1: Using Make (Recommended)

```bash
# View all available commands
make help

# Deploy production stack
make deploy-production

# View logs
make logs-follow

# Check service status
make status

# Stop services
make stop

# Create backup
make backup
```

### Method 2: Using Docker Compose Directly

```bash
# Start services
docker-compose -f docker-compose.production.yml up -d

# View logs
docker-compose -f docker-compose.production.yml logs -f

# Stop services
docker-compose -f docker-compose.production.yml down
```

### Method 3: Using Ansible

For automated deployment to remote servers:

```bash
cd deployment/ansible

# Edit inventory file
cp inventory.ini.example inventory.ini
nano inventory.ini

# Run deployment
ansible-playbook -i inventory.ini deploy.yml
```

### Method 4: Using Systemd

For system service integration:

```bash
# Copy service file
sudo cp deployment/systemd/agent-zero.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable agent-zero
sudo systemctl start agent-zero

# Check status
sudo systemctl status agent-zero
```

## Configuration

### LiteLLM Configuration

Edit `config/litellm/litellm_config.yaml` to:
- Add/remove model providers
- Configure rate limits
- Set up fallback models
- Enable cost tracking

### Prometheus Alerts

Edit `config/prometheus/rules/agent_zero_alerts.yml` to customize alerting rules.

### Grafana Dashboards

Pre-configured dashboards are located in `config/grafana/dashboards/`. Import additional dashboards from [Grafana Dashboard Library](https://grafana.com/grafana/dashboards/).

## Monitoring & Observability

### Metrics (Prometheus + Grafana)

Access Grafana at http://localhost:3001 to view:
- System metrics (CPU, memory, disk)
- Container metrics
- Application metrics
- Custom Agent Zero metrics

### Logs (Loki + Promtail)

All logs are aggregated in Loki and queryable through Grafana:
1. Open Grafana
2. Go to Explore
3. Select Loki datasource
4. Query logs: `{job="agent-zero"}`

### Traces (Langfuse)

LLM traces are automatically sent to Langfuse:
1. Access http://localhost:3000
2. View request traces
3. Analyze costs
4. Debug prompts

### Cost Tracking (LiteLLM)

Monitor API costs:
1. Access LiteLLM UI at http://localhost:4000
2. View cost breakdown by model
3. Set budget limits
4. Configure alerts

## Multi-User Setup

### Enable Multi-User Mode

1. Configure Redis for session storage (already included)
2. Enable user authentication in `.env`:

```bash
# Add to .env
ENABLE_AUTH=true
AUTH_TYPE=basic  # or oauth, ldap
```

3. Configure user database:

```bash
# Use PostgreSQL for user management
USER_DB_URL=postgresql://postgres:password@postgres:5432/users
```

### User Isolation

Each user gets isolated:
- Memory space
- Knowledge base
- Chat history
- API rate limits

## Maintenance

### Backup

Create backups regularly:

```bash
# Using Make
make backup

# Using script directly
./deployment/scripts/backup.sh
```

Backups include:
- Docker volumes (memory, knowledge, logs)
- PostgreSQL databases
- Redis data
- Configuration files

### Restore

Restore from backup:

```bash
# Using Make
make restore

# Follow prompts to select backup
```

### Updates

Update Agent Zero:

```bash
# Pull latest changes
git pull origin main

# Update containers
make update

# Or using Docker Compose
docker-compose -f docker-compose.production.yml pull
docker-compose -f docker-compose.production.yml up -d
```

### Health Checks

Automated health checks run every 15 minutes:

```bash
# Run manual health check
./deployment/scripts/health-check.sh

# View health check logs
tail -f /var/log/agent-zero-health.log
```

## Troubleshooting

### Services Not Starting

```bash
# Check service status
make status

# View logs
make logs

# Restart services
make restart
```

### High Memory Usage

```bash
# Check container resource usage
docker stats

# Adjust resource limits in docker-compose.production.yml
```

### Database Connection Issues

```bash
# Check PostgreSQL logs
docker-compose -f docker-compose.production.yml logs postgres

# Restart database
docker-compose -f docker-compose.production.yml restart postgres
```

### Port Conflicts

If ports are already in use, edit `docker-compose.production.yml` to use different ports.

### Performance Issues

1. Check Grafana dashboards for bottlenecks
2. Review Netdata for real-time metrics
3. Analyze logs in Loki
4. Check LiteLLM rate limits

## Security Best Practices

1. **Change default passwords** in `.env`
2. **Enable HTTPS** using nginx/traefik reverse proxy
3. **Configure firewall** to restrict access
4. **Use secrets management** (e.g., HashiCorp Vault)
5. **Regular updates** of all components
6. **Enable authentication** for all services
7. **Monitor logs** for suspicious activity

## Scaling

### Horizontal Scaling

Scale Agent Zero instances:

```bash
# Scale to 3 instances
make scale-workers
# Enter: 3
```

### Load Balancing

Use nginx or traefik for load balancing:

```yaml
# Example nginx config
upstream agent_zero {
    server agent-zero-1:80;
    server agent-zero-2:80;
    server agent-zero-3:80;
}
```

## Support

- **Documentation**: [docs/](../docs/)
- **Issues**: [GitHub Issues](https://github.com/agent0ai/agent-zero/issues)
- **Discord**: [Join our Discord](https://discord.gg/B8KZKNsPpj)
- **Community**: [Skool Community](https://www.skool.com/agent-zero)

## License

Agent Zero is released under the MIT License. See [LICENSE](../LICENSE) for details.
