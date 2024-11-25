# Makefile

# Variables
DOCKER_COMPOSE_FILE = docker-compose.yml

# Build all containers
build:
	docker-compose -f $(DOCKER_COMPOSE_FILE) build

# Run all containers in the background
up:
	docker-compose -f $(DOCKER_COMPOSE_FILE) up -d db web

# Run tests using the `test` service defined in docker-compose.yml
test: up 
	@echo "Waiting for PostgreSQL to be ready..."
	until docker exec postgres_container pg_isready -U myuser; do \
	    sleep 5; \
	done
	docker-compose -f $(DOCKER_COMPOSE_FILE) run --rm test

# Stop and remove all containers
down:
	docker-compose -f $(DOCKER_COMPOSE_FILE) down

# Run full test sequence
full-test: build up test down

.PHONY: lint
lint:
	flake8 .  
	black --check .  

.PHONY: lint-fix
lint-fix:
	black .  

