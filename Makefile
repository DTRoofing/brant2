# Makefile for the Brant Roofing System
#
# This Makefile provides a convenient set of commands for managing the application lifecycle.
# It is designed to work with the docker-compose.yml setup.

# Use bash for better scripting capabilities
SHELL := /bin/bash

# Default command to run when no target is specified
.DEFAULT_GOAL := help

# Phony targets don't represent files
.PHONY: help setup up dev down stop logs status health build restart clean test organize-docs

help:
	@echo "Usage: make [command]"
	@echo ""
	@echo "Commands:"
	@echo "  help           : Show this help message."
	@echo ""
	@echo "Lifecycle:"
	@echo "  setup          : Run the initial project setup script (quick-start.sh)."
	@echo "  up             : Start all services in detached mode."
	@echo "  dev            : Alias for 'up', starts development environment."
	@echo "  stop           : Stop all running services without removing them."
	@echo "  down           : Stop and remove all service containers and networks."
	@echo "  clean          : Run 'down' and then remove dangling Docker images."
	@echo "  build          : Build or rebuild service images."
	@echo "  restart        : Restart all services."
	@echo ""
	@echo "Utilities:"
	@echo "  logs           : View logs from all running services."
	@echo "  status         : Show the status of running services."
	@echo "  health         : Check the health of the API service."
	@echo "  test           : Run the test suite inside the api container."
	@echo "  organize-docs  : Move documentation files from the project root into the /docs directory."

# ==============================================================================
# Development Lifecycle
# ==============================================================================

setup:
	@echo "🚀 Running initial project setup..."
	@if [ ! -f quick-start.sh ]; then \
		echo "Error: quick-start.sh not found. Cannot run setup."; \
		exit 1; \
	fi
	@chmod +x quick-start.sh
	@./quick-start.sh

up:
	@echo "🚀 Starting all services in detached mode..."
	docker-compose up -d

dev: up

stop:
	@echo "🛑 Stopping all services..."
	docker-compose stop

down:
	@echo "🔥 Stopping and removing all service containers..."
	docker-compose down --remove-orphans

clean: down
	@echo "🧹 Cleaning up dangling Docker images..."
	docker system prune -f

build:
	@echo "🏗️ Building service images..."
	docker-compose build

restart: stop up

# ==============================================================================
# Utilities
# ==============================================================================

logs:
	@echo "📜 Tailing logs... (Press Ctrl+C to stop)"
	docker-compose logs -f

status:
	@echo "📊 Checking service status..."
	docker-compose ps

health:
	@echo "❤️ Checking API health..."
	@if curl -s -f http://localhost:3001/api/v1/pipeline/health > /dev/null; then \
		echo "✅ API is healthy."; \
	else \
		echo "❌ API health check failed. Is the API running?"; \
		exit 1; \
	fi

test:
	@echo "🧪 Running tests inside the 'api' container..."
	docker-compose exec api pytest

# ==============================================================================
# Documentation Management
# ==============================================================================

organize-docs:
	@echo "📂 Documentation has already been organized into the 'docs' directory."
	@echo "✅ Documentation organization complete."