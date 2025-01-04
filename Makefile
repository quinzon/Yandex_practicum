# Variables
COMPOSE_FILE_MONGO = mongo-cluster-compose.yml
COMPOSE_FILE_APP = docker-compose.yml
SETUP_SCRIPT = setup_mongo.sh

.PHONY: all up-mongo setup-mongo up-ugc up-stack down clean logs

# Full cycle: start MongoDB, configure it, and run core services
all: up-mongo setup-mongo up-ugc

# Start the full stack (all services from docker-compose.yml)
up-stack:
	@echo "Starting full stack (all services)..."
	docker-compose -f $(COMPOSE_FILE_APP) up -d

# Start the MongoDB cluster
up-mongo:
	@echo "Starting MongoDB cluster..."
	docker-compose -f $(COMPOSE_FILE_MONGO) up -d

# Configure the MongoDB cluster using setup_mongo.sh
setup-mongo:
	@echo "Setting up MongoDB cluster..."
	chmod +x $(SETUP_SCRIPT)
	./$(SETUP_SCRIPT)

# Start core services: Nginx, Redis, Postgres, Auth, UGC
up-ugc:
	@echo "Starting application services..."
	docker-compose -f $(COMPOSE_FILE_APP) up -d redis postgres auth_service ugc_service nginx

# Stop all services
down:
	@echo "Stopping all services..."
	docker-compose -f $(COMPOSE_FILE_MONGO) down
	docker-compose -f $(COMPOSE_FILE_APP) down

# Clean up data (remove all container data)
clean: down
	@echo "Removing volumes and clearing data..."
	docker volume prune -f
	rm -rf ./data

# Show logs of all services
logs:
	@echo "Displaying logs..."
	docker-compose -f $(COMPOSE_FILE_APP) logs -f
