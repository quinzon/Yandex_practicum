
# Movies Async API

An asynchronous API for an online movie theater platform, built with FastAPI. It supports various operations for handling movie data, genres, persons, and films. The API leverages Docker Compose for container orchestration and uses Redis, Elasticsearch, and PostgreSQL as its core technologies.

## Table of Contents

- [Technologies](#technologies)
- [Features](#features)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

## Technologies

- **FastAPI**: A modern, fast web framework for building APIs with Python 3.7+.
- **Redis**: Used as a caching layer.
- **Elasticsearch**: A search engine for managing movie data.
- **PostgreSQL**: The main relational database.
- **Docker Compose**: Container orchestration tool to manage multi-container Docker applications.

## Features

- **Asynchronous API**: High performance for handling multiple concurrent requests with FastAPI.
- **Redis Caching**: For fast access to frequently requested data.
- **Elasticsearch**: Powerful full-text search capabilities across movie data.
- **PostgreSQL**: Stores structured relational movie information.
- **Containerized**: Uses Docker and Docker Compose for consistent development and deployment environments.

## Installation

### Prerequisites

Make sure you have the following tools installed:
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Steps

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Quinzon/Async_API_sprint_1.git
   cd Async_API_sprint_1
   ```

2. **Set up environment variables**:  
   Create a `.env` file in the root of the project and add the following environment variables:

   ```bash
   # Project Settings
   PROJECT_NAME=movies
   DEBUG=False

   # Redis Settings
   REDIS_HOST=redis
   REDIS_PORT=6379

   # Elasticsearch Settings
   ES_HOST=http://elasticsearch
   ES_PORT=9200
   ES_JAVA_OPTS=-Xms256m -Xmx256m
   DISCOVERY_TYPE=single-node
   XPACK_SECURITY_ENABLED=false
   ELASTIC_CONTAINER=true

   # PostgreSQL Settings
   POSTGRES_USER=app
   POSTGRES_PASSWORD=123
   POSTGRES_HOST=postgres
   POSTGRES_PORT=5432
   POSTGRES_SCHEMA=content
   POSTGRES_SQL_DB=app
   ```

3. **Start the application**:

   Build and run the application stack using Docker Compose:

   ```bash
   docker-compose up --build
   ```

   This will:
   - Set up the FastAPI application.
   - Start Redis, Elasticsearch, and PostgreSQL containers.

4. **Access the API documentation**:

   - Swagger UI: [http://localhost:8000/api/openapi](http://localhost:8000/api/openapi)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Running the Application

Once the Docker containers are running, you can interact with the API at [http://localhost:8000](http://localhost:8000).

To shut down the application, run:

```bash
docker-compose down
```

## Environment Variables

The following environment variables are used to configure the project:

### Project Settings

- `PROJECT_NAME`: The name of the project.
- `DEBUG`: Debug mode for development.

### Redis Settings

- `REDIS_HOST`: Hostname for Redis.
- `REDIS_PORT`: Port for Redis.

### Elasticsearch Settings

- `ES_HOST`: URL for the Elasticsearch service.
- `ES_PORT`: Port for the Elasticsearch service.
- `ES_JAVA_OPTS`: Java memory options for Elasticsearch.
- `DISCOVERY_TYPE`: Type of Elasticsearch discovery (single-node for development).
- `XPACK_SECURITY_ENABLED`: Disable X-Pack security for development.
- `ELASTIC_CONTAINER`: Marks Elasticsearch as a container.

### PostgreSQL Settings

- `POSTGRES_USER`: PostgreSQL username.
- `POSTGRES_PASSWORD`: PostgreSQL password.
- `POSTGRES_HOST`: Hostname for PostgreSQL.
- `POSTGRES_PORT`: Port for PostgreSQL.
- `POSTGRES_SCHEMA`: PostgreSQL schema for the content.
- `POSTGRES_SQL_DB`: Name of the PostgreSQL database.

## API Endpoints

Here are some of the main API endpoints:

### Movies

- **GET** `/api/v1/films/`: List movies with pagination and filtering.
- **GET** `/api/v1/films/{movie_id}`: Retrieve detailed information for a specific movie.
- **POST** `/api/v1/films/`: Add a new movie (admin access).

### Genres

- **GET** `/api/v1/genres/`: List all genres with pagination and filtering.
- **GET** `/api/v1/genres/{genre_id}`: Retrieve detailed information for a specific genre.

### Persons

- **GET** `/api/v1/persons/`: List persons (actors, directors, etc.) involved in the movies.
- **GET** `/api/v1/persons/{person_id}`: Get detailed info about a specific person.

For a full list of available endpoints, visit the Swagger UI at [http://localhost:8000/api/openapi](http://localhost:8000/api/openapi).


## Tests

1. Build API image:
   `docker-compose build api`
2. Build Tests:
   `docker-compose -f tests/functional/docker-compose.test.yml up --build`

## Contributing

If you want to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make your changes.
4. Push the branch (`git push origin feature/your-feature`).
5. Open a pull request.
