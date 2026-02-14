# Makefile for Simple Dash Docker Operations

.PHONY: help build up down restart logs clean shell

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

build: ## Build the Docker image
	docker compose build

up: ## Start the container
	docker compose up -d

down: ## Stop the container
	docker compose down

restart: ## Restart the container
	docker compose restart

logs: ## View container logs
	docker compose logs -f

logs-tail: ## View last 100 lines of logs
	docker compose logs --tail=100

clean: ## Stop and remove container, images, and volumes
	docker compose down -v --rmi local

shell: ## Open a shell in the running container
	docker compose exec simpledash sh

ps: ## Show container status
	docker compose ps

rebuild: ## Rebuild and restart the container
	$(MAKE) down
	$(MAKE) build
	$(MAKE) up

health: ## Check container health
	docker compose ps
	@echo ""
	docker inspect --format='{{.State.Health.Status}}' simpledash 2>/dev/null || echo "Health check not available"
