# Agent Zero Makefile
# Provides build, deployment, and management tasks

.PHONY: help install build start stop restart logs clean deploy-production deploy-dev test lint

# Variables
COMPOSE_FILE=docker-compose.production.yml
COMPOSE_PROJECT=agent-zero
PYTHON=python3
PIP=$(PYTHON) -m pip

# Default target
help:
	@echo "Agent Zero - Build and Deployment Automation"
	@echo ""
	@echo "Available targets:"
	@echo "  install              - Install Python dependencies"
	@echo "  build                - Build Docker images"
	@echo "  start                - Start all services"
	@echo "  stop                 - Stop all services"
	@echo "  restart              - Restart all services"
	@echo "  logs                 - Show logs from all services"
	@echo "  logs-follow          - Follow logs from all services"
	@echo "  logs-agent           - Show Agent Zero logs"
	@echo "  status               - Show status of all services"
	@echo "  clean                - Clean up containers and volumes"
	@echo "  clean-all            - Clean everything including volumes"
	@echo "  deploy-production    - Deploy production stack"
	@echo "  deploy-dev           - Deploy development stack"
	@echo "  test                 - Run tests"
	@echo "  lint                 - Run linters"
	@echo "  backup               - Create backup of data"
	@echo "  restore              - Restore from backup"
	@echo "  init-env             - Initialize environment file"

# Install Python dependencies
install:
	@echo "Installing Python dependencies..."
	$(PIP) install -r requirements.txt

# Build Docker images
build:
	@echo "Building Docker images..."
	docker-compose -f $(COMPOSE_FILE) -p $(COMPOSE_PROJECT) build

# Start services
start:
	@echo "Starting Agent Zero services..."
	docker-compose -f $(COMPOSE_FILE) -p $(COMPOSE_PROJECT) up -d
	@echo "Services started. Access points:"
	@echo "  Agent Zero UI:        http://localhost:50001"
	@echo "  Grafana:              http://localhost:3001 (admin/admin)"
	@echo "  Prometheus:           http://localhost:9090"
	@echo "  Langfuse:             http://localhost:3000"
	@echo "  LiteLLM:              http://localhost:4000"
	@echo "  RabbitMQ Management:  http://localhost:15672 (admin/admin)"
	@echo "  OpenSearch:           http://localhost:9200"
	@echo "  OpenSearch Dashboards: http://localhost:5601"
	@echo "  Netdata:              http://localhost:19999"

# Stop services
stop:
	@echo "Stopping Agent Zero services..."
	docker-compose -f $(COMPOSE_FILE) -p $(COMPOSE_PROJECT) stop

# Restart services
restart: stop start

# Show logs
logs:
	docker-compose -f $(COMPOSE_FILE) -p $(COMPOSE_PROJECT) logs --tail=100

# Follow logs
logs-follow:
	docker-compose -f $(COMPOSE_FILE) -p $(COMPOSE_PROJECT) logs -f

# Show Agent Zero logs
logs-agent:
	docker-compose -f $(COMPOSE_FILE) -p $(COMPOSE_PROJECT) logs -f agent-zero

# Show service status
status:
	@echo "Service Status:"
	@docker-compose -f $(COMPOSE_FILE) -p $(COMPOSE_PROJECT) ps

# Clean up containers
clean:
	@echo "Cleaning up containers..."
	docker-compose -f $(COMPOSE_FILE) -p $(COMPOSE_PROJECT) down

# Clean everything including volumes
clean-all:
	@echo "Warning: This will remove all data volumes!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose -f $(COMPOSE_FILE) -p $(COMPOSE_PROJECT) down -v; \
		echo "All containers and volumes removed."; \
	fi

# Deploy production stack
deploy-production:
	@echo "Deploying Agent Zero production stack..."
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Run 'make init-env' first."; \
		exit 1; \
	fi
	docker-compose -f $(COMPOSE_FILE) -p $(COMPOSE_PROJECT) pull
	docker-compose -f $(COMPOSE_FILE) -p $(COMPOSE_PROJECT) up -d
	@echo "Production deployment complete!"

# Deploy development stack
deploy-dev:
	@echo "Deploying Agent Zero development stack..."
	docker-compose -f docker/run/docker-compose.yml up -d
	@echo "Development deployment complete!"

# Run tests
test:
	@echo "Running tests..."
	$(PYTHON) -m pytest tests/ -v

# Run linters
lint:
	@echo "Running linters..."
	$(PYTHON) -m black --check .
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy .

# Create backup
backup:
	@echo "Creating backup..."
	@mkdir -p backups
	@BACKUP_FILE=backups/agent-zero-backup-$$(date +%Y%m%d-%H%M%S).tar.gz; \
	docker run --rm \
		-v agent-zero-memory:/data/memory \
		-v agent-zero-knowledge:/data/knowledge \
		-v agent-zero-logs:/data/logs \
		-v $$(pwd)/backups:/backup \
		alpine tar czf /backup/$$(basename $$BACKUP_FILE) -C /data .; \
	echo "Backup created: $$BACKUP_FILE"

# Restore from backup
restore:
	@echo "Available backups:"
	@ls -lh backups/*.tar.gz 2>/dev/null || echo "No backups found"
	@read -p "Enter backup filename: " BACKUP_FILE; \
	if [ -f "backups/$$BACKUP_FILE" ]; then \
		docker run --rm \
			-v agent-zero-memory:/data/memory \
			-v agent-zero-knowledge:/data/knowledge \
			-v agent-zero-logs:/data/logs \
			-v $$(pwd)/backups:/backup \
			alpine tar xzf /backup/$$BACKUP_FILE -C /data; \
		echo "Restore complete!"; \
	else \
		echo "Error: Backup file not found"; \
		exit 1; \
	fi

# Initialize environment file
init-env:
	@if [ -f .env ]; then \
		echo ".env file already exists. Backup created as .env.backup"; \
		cp .env .env.backup; \
	fi
	@cp example.env .env
	@echo "Created .env file from example.env"
	@echo "Please edit .env and add your API keys and configuration"

# Health check
health:
	@echo "Checking service health..."
	@docker-compose -f $(COMPOSE_FILE) -p $(COMPOSE_PROJECT) ps --filter "status=running" --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

# Scale specific services
scale-workers:
	@read -p "Number of worker instances: " WORKERS; \
	docker-compose -f $(COMPOSE_FILE) -p $(COMPOSE_PROJECT) up -d --scale agent-zero=$$WORKERS

# Update containers
update:
	@echo "Updating containers..."
	docker-compose -f $(COMPOSE_FILE) -p $(COMPOSE_PROJECT) pull
	docker-compose -f $(COMPOSE_FILE) -p $(COMPOSE_PROJECT) up -d

# Database migrations (if needed)
migrate:
	@echo "Running database migrations..."
	docker-compose -f $(COMPOSE_FILE) -p $(COMPOSE_PROJECT) exec postgres psql -U postgres -d litellm -f /migrations/migrate.sql

# Create systemd service (for Linux servers)
install-service:
	@echo "Creating systemd service..."
	@sudo cp deployment/systemd/agent-zero.service /etc/systemd/system/
	@sudo systemctl daemon-reload
	@echo "Service installed. Enable with: sudo systemctl enable agent-zero"
	@echo "Start with: sudo systemctl start agent-zero"
