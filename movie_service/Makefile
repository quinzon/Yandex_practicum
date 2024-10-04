.PHONY: build_api run_tests clean

# Шаг 1: Build API Docker image
build_api:
	@echo "Building API Docker image..."
	docker build -t fastapi .

# Step 2: Run functional tests
run_tests: build_api
	@echo "Building and running functional tests..."
	cd tests/functional && docker compose -f docker-compose.test.yml up --build --exit-code-from tests --abort-on-container-exit

# Step 3: Clean test artifacts
clean:
	@echo "Stopping and cleaning up Docker resources for tests with label 'com.example.project=functional-tests'..."

	# Stop and clean containers
	docker ps -aq --filter "label=com.example.project=functional-tests" | xargs -r docker stop
	docker ps -aq --filter "label=com.example.project=functional-tests" | xargs -r docker rm

	# Clean images
	docker images -aq --filter "label=com.example.project=functional-tests" | xargs -r docker rmi

	# Clean volumes
	docker volume ls -q --filter "label=com.example.project=functional-tests" | xargs -r docker volume rm

	# Clean networks
	docker network ls -q --filter "label=com.example.project=functional-tests" | xargs -r docker network rm
