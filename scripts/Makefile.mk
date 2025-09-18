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
	@echo "  test-e2e         : Run only the end-to-end tests."
	@echo "  test-integration : Run integration tests in an isolated environment."
	@echo "  organize-docs  : Move documentation files into the 'docs' directory."

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

test-e2e:
	@echo "🌐 Running end-to-end tests..."
	docker-compose exec api pytest -m e2e

test-integration:
	@echo "🔬 Running integration tests..."
	@echo "  -> Starting isolated test environment..."
	docker-compose -f docker-compose.test.yml up -d --build
	@echo "  -> Executing pytest against the test API..."
	docker-compose -f docker-compose.test.yml exec test-api pytest tests/integration/
	@echo "  -> Tearing down test environment..."
	docker-compose -f docker-compose.test.yml down
# ==============================================================================
# Documentation Management
# ==============================================================================

organize-docs:
	@echo "📂 Organizing all documentation into the 'docs' directory..."
	@mkdir -p docs/reports docs/setup docs/testing docs/development
	@echo "  -> Moving reports..."
	@if [ -f "COMPLETE_TEST_EXECUTION_REPORT.md" ]; then mv "COMPLETE_TEST_EXECUTION_REPORT.md" docs/reports/; echo "    - Moved COMPLETE_TEST_EXECUTION_REPORT.md"; fi
	@if [ -f "E2E_TEST_EXECUTION_LOG.md" ]; then mv "E2E_TEST_EXECUTION_LOG.md" docs/reports/; echo "    - Moved E2E_TEST_EXECUTION_LOG.md"; fi
	@echo "  -> Moving setup guides..."
	@if [ -f "PORT_FORWARDING_SETUP.md" ]; then mv "PORT_FORWARDING_SETUP.md" docs/setup/; echo "    - Moved PORT_FORWARDING_SETUP.md"; fi
	@if [ -d "build-documents" ]; then \
		echo "    - Moving content from 'build-documents'"; \
		mv build-documents/* docs/setup/ 2>/dev/null || true; \
		rmdir build-documents 2>/dev/null || true; \
	fi
	@echo "  -> Moving testing strategies..."
	@if [ -f "INTEGRATION_TESTING_STRATEGY.md" ]; then mv "INTEGRATION_TESTING_STRATEGY.md" docs/testing/; echo "    - Moved INTEGRATION_TESTING_STRATEGY.md"; fi
	@if [ -f "tests/depoyment_testing.md" ]; then mv "tests/depoyment_testing.md" docs/testing/; echo "    - Moved tests/depoyment_testing.md"; fi
	@echo "  -> Moving development guides..."
	@if [ -f "DEBUGGING_ROUTING.md" ]; then mv "DEBUGGING_ROUTING.md" docs/development/; echo "    - Moved DEBUGGING_ROUTING.md"; fi
	@if [ -f "debugger.md" ]; then mv "debugger.md" docs/development/; echo "    - Moved debugger.md"; fi
	@echo "  -> Moving general documentation..."
	@if [ -f "GCP_DEPLOYMENT.md" ]; then mv "GCP_DEPLOYMENT.md" docs/; echo "    - Moved GCP_DEPLOYMENT.md"; fi
	@if [ -f "SYSTEM_METRICS_TABLE.md" ]; then mv "SYSTEM_METRICS_TABLE.md" docs/; echo "    - Moved SYSTEM_METRICS_TABLE.md"; fi
	@if [ -f "WEEKLY_CHANGELOG.md" ]; then mv "WEEKLY_CHANGELOG.md" docs/; echo "    - Moved WEEKLY_CHANGELOG.md"; fi
	@if [ -f "CHANGELOG.md" ]; then mv "CHANGELOG.md" docs/; echo "    - Moved CHANGELOG.md"; fi
	@echo "✅ Documentation organization complete."